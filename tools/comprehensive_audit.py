"""
comprehensive_audit.py — In-place audit and fix of food_master_v7_2.json

Phase 1: Category normalization
Phase 2: Duplicate removal (keep item with more nutrition fields filled)
Phase 3: Nutrition validation (warn only, no auto-fix)
Phase 4: Summary

Usage:
  py tools/comprehensive_audit.py
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATASET = Path(__file__).parent.parent / "assets" / "data" / "food_master_v7_2.json"

# ---------------------------------------------------------------------------
# Phase 1 — Category normalization
# ---------------------------------------------------------------------------

KNOWN_CATEGORIES = {
    "vegetable", "sweet", "snack", "pizza", "meat", "fish", "beverage",
    "dairy", "bread", "legume", "fruit", "grain", "breakfast", "rice",
    "soup", "salad", "egg", "noodle", "shaak", "bakery", "other",
}

CAT_MAP = {
    "namkeen": "snack",
    "packaged_snack": "snack",
    "berry": "fruit",
    "curry": "soup",
    "main": "legume",
    "dessert": "sweet",
    "drink": "beverage",
    "veg": "vegetable",
    "leafy_vegetable": "shaak",
    "condiment": "snack",
    "brand": "snack",
}

FALLBACK_CAT = "snack"


def normalize_category(cat: str) -> tuple[str, bool]:
    """Return (new_cat, changed). Unknown valid cats pass through unchanged."""
    if cat in KNOWN_CATEGORIES:
        return cat, False
    mapped = CAT_MAP.get(cat)
    if mapped:
        return mapped, True
    # Unknown category → fallback
    return FALLBACK_CAT, True


# ---------------------------------------------------------------------------
# Phase 2 — Duplicate detection helpers
# ---------------------------------------------------------------------------

NUTRITION_FIELDS = ["ca", "fe", "va", "vc", "vd", "mg", "pot", "b12", "zn"]


def nutrition_score(item: dict) -> int:
    """Count how many nutrition fields are non-null and non-zero."""
    score = 0
    for field in NUTRITION_FIELDS:
        val = item.get(field)
        if val is not None and val != 0:
            score += 1
    return score


# ---------------------------------------------------------------------------
# Phase 3 — Nutrition validation
# ---------------------------------------------------------------------------

def calc_kcal(item: dict) -> float | None:
    p = item.get("p")
    c = item.get("c")
    f = item.get("f")
    if any(v is None for v in [p, c, f]):
        return None
    return p * 4 + c * 4 + f * 9


def check_kcal(item: dict) -> str | None:
    """Return warning string if kcal is anomalous, else None."""
    if item.get("alc_g") is not None:
        return None  # Skip alcohol items
    k = item.get("k")
    if k is None or k == 0:
        return None
    calc = calc_kcal(item)
    if calc is None:
        return None
    deviation = abs(calc - k) / max(k, 1)
    if deviation > 0.35:
        return (
            f"  KCAL ANOMALY id={item.get('id')} '{item.get('en')}': "
            f"stored={k}, calc={calc:.1f}, diff={deviation*100:.0f}%"
        )
    return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Loading dataset from {DATASET}")
    data: list[dict] = json.loads(DATASET.read_text(encoding="utf-8"))
    total_before = len(data)
    print(f"Loaded {total_before} items\n")

    # -----------------------------------------------------------------------
    # Phase 1 — Category normalization
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("PHASE 1 — Category Normalization")
    print("=" * 60)

    cat_changes = 0
    cat_change_log: dict[str, int] = {}  # old_cat → count

    for item in data:
        old_cat = item.get("cat", "")
        new_cat, changed = normalize_category(old_cat)
        if changed:
            key = f"{old_cat} → {new_cat}"
            cat_change_log[key] = cat_change_log.get(key, 0) + 1
            item["cat"] = new_cat
            cat_changes += 1

    if cat_changes:
        for change, count in sorted(cat_change_log.items()):
            print(f"  {change}: {count} items")
    else:
        print("  No category changes needed.")

    print(f"\nCategory changes: {cat_changes}\n")

    # -----------------------------------------------------------------------
    # Phase 2 — Duplicate removal
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("PHASE 2 — Duplicate Removal")
    print("=" * 60)

    # Group items by lower-cased, stripped English name
    name_groups: dict[str, list[dict]] = {}
    for item in data:
        key = item.get("en", "").strip().lower()
        name_groups.setdefault(key, []).append(item)

    ids_to_remove: set = set()

    for name_key, group in name_groups.items():
        if len(group) <= 1:
            continue
        # Sort descending by nutrition score; among ties keep lower ID (original)
        group_sorted = sorted(group, key=lambda x: (nutrition_score(x), -x.get("id", 0)), reverse=True)
        winner = group_sorted[0]
        losers = group_sorted[1:]
        for loser in losers:
            print(
                f"  REMOVE dup: id={loser.get('id')} '{loser.get('en')}' "
                f"(score={nutrition_score(loser)}) — kept id={winner.get('id')} "
                f"(score={nutrition_score(winner)})"
            )
            ids_to_remove.add(loser.get("id"))

    data_deduped = [item for item in data if item.get("id") not in ids_to_remove]
    dups_removed = total_before - len(data_deduped)
    data = data_deduped

    print(f"\nDuplicates removed: {dups_removed}\n")

    # -----------------------------------------------------------------------
    # Phase 3 — Nutrition validation
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("PHASE 3 — Nutrition Validation (warnings only)")
    print("=" * 60)

    anomalies = 0
    for item in data:
        warning = check_kcal(item)
        if warning:
            print(warning)
            anomalies += 1

    if anomalies == 0:
        print("  No anomalies found.")

    print(f"\nAnomalies flagged: {anomalies}\n")

    # -----------------------------------------------------------------------
    # Write back
    # -----------------------------------------------------------------------
    DATASET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    total_after = len(data)

    # -----------------------------------------------------------------------
    # Phase 4 — Summary
    # -----------------------------------------------------------------------
    print("=" * 60)
    print("PHASE 4 — Summary")
    print("=" * 60)
    print(f"  Items before:        {total_before}")
    print(f"  Items after:         {total_after}")
    print(f"  Duplicates removed:  {dups_removed}")
    print(f"  Category changes:    {cat_changes}")
    print(f"  Nutrition anomalies: {anomalies}")
    print(f"\nSaved to {DATASET}")


if __name__ == "__main__":
    main()
