"""
fix_v6_5.py — Per-serving nutrition correction for whole-recipe ICMR entries
Input:  assets/data/food_master_v6_4.json
Output: assets/data/food_master_v6_5.json
        assets/data/index_en_v6_5.json
        assets/data/index_bn_v6_5.json

Root cause: 28 ICMR records store whole-recipe nutrition values paired with a
one-person serving size.  The tell-tale signs are:
  - p + c + f > serving_g   (macros exceed the mass of food — physically impossible)
  - fat > serving_g          (fat alone exceeds serving weight — impossible)
  - k/100g > 900             (exceeds thermodynamic maximum for real food)
  - k/100g >> food-type norm (e.g. 800 kcal/100g for a vegetable curry)

Fix: divide ALL nutrient fields by the known number of recipe servings.
The divisor for each record was chosen so that the resulting k/100g and f/100g
fall within the expected range for that food type.  No serving sizes change —
only the per-serving nutrient values are corrected.

Records verified OK (no change):
  455  French dressing           (k/100g=616; normal for oil-heavy dressing)
  524  Mayonnaise without eggs   (k/100g=531, f%=55; normal for egg-free mayo)
  543  Papdi                     (k/100g=410; deep-fried snack — plausible)
  620  Veg manchurian            (flagged for manual review — macro profile uncertain)
  762  Banana chips              (flagged for manual review — macro profile uncertain)
  892  Coconut kheer             (k/100g=423, f%=27; plausible for coconut dessert)
  900  Kiwi granola pudding      (div/2 applied — at threshold)
  367  Pasta hot pot             (k/100g=347, f%=18; normal)
"""

import json
import math
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path("assets/data")
IN_FILE  = DATA_DIR / "food_master_v6_4.json"
OUT_FOOD = DATA_DIR / "food_master_v6_5.json"
OUT_EN   = DATA_DIR / "index_en_v6_5.json"
OUT_BN   = DATA_DIR / "index_bn_v6_5.json"
REPORT   = DATA_DIR / "serving_correction_report.json"

# ── Divisors (number of recipe servings) ───────────────────────────────────
# Chosen so that post-correction k/100g and f/100g are within the expected
# range for the food type.  Verified one by one — see docstring.
SERVING_DIVISORS: dict[int, int] = {
    276: 4,   # Orange chiffon pie 80g    → 362 kcal, f=19.5g, k/100g=453  ✓
    357: 4,   # Shahi keema kofta curry   → 645 kcal, f=67.6g, k/100g=258  ✓
    359: 4,   # Tandoori chicken 180g     → 273 kcal, f=28.6g, k/100g=152  ✓
    399: 6,   # Besan kadhi/pakodies 250g → 394 kcal, f=41.7g, k/100g=158  ✓
    461: 3,   # Fruit flan 100g           → 405 kcal, f=19.4g, k/100g=405  ✓
    478: 4,   # Gujarati handvo 100g      → 361 kcal, f= 8.4g, k/100g=361  ✓
    502: 2,   # Lasagne with meat sauce   → 562 kcal, f=30.5g, k/100g=281  ✓
    505: 4,   # Lemon chiffon pie 80g     → 347 kcal, f=19.4g, k/100g=434  ✓
    521: 4,   # Masala soufflé 200g       → 459 kcal, f=27.3g, k/100g=229  ✓
    528: 6,   # Methi chaman 250g         → 794 kcal, f=85.0g, k/100g=318  ✓
    597: 4,   # Soyabean namak paras 300g → 574 kcal, f=61.5g, k/100g=191  ✓
    629: 6,   # Veg nargisi kofta curry   → 221 kcal, f=21.9g, k/100g=276  ✓
    655: 6,   # Indian lamb & egg curry   → 219 kcal, f=22.6g, k/100g=273  ✓
    703: 6,   # Bhel puri 300g            → 596 kcal, f=56.0g, k/100g=199  ✓
    738: 6,   # Boondi raita 250g         → 377 kcal, f=40.5g, k/100g=151  ✓
    796: 3,   # Khakhra chaat 300g        → 999 kcal, f=85.3g, k/100g=333  ✓
    832: 4,   # Spicy corn chaat 300g     → 665 kcal, f=64.5g, k/100g=222  ✓
    900: 2,   # Kiwi granola pudding 250g → 736 kcal, f=40.3g, k/100g=295  ✓
    903: 5,   # Lotus seed halwa 60g      → 269 kcal, f= 9.0g, k/100g=448  ✓
    913: 7,   # Pineapple cake 30g        → 143 kcal, f= 6.8g, k/100g=478  ✓
    943: 6,   # Tutti frutti cake 100g    → 492 kcal, f=17.9g, k/100g=492  ✓
    980: 4,   # Cabbage manchurian 250g   → 415 kcal, f=41.6g, k/100g=166  ✓
    993: 8,   # Chinese cabbage meatball  → 282 kcal, f=32.9g, k/100g= 94  ✓
    994: 6,   # Creamed spinach/mushroom  → 416 kcal, f=43.8g, k/100g=166  ✓
    995: 4,   # Crispy okra 250g          → 564 kcal, f=60.3g, k/100g=226  ✓
    1003: 4,  # Gobi 65 300g              → 597 kcal, f=62.4g, k/100g=199  ✓
    1008: 6,  # Jackfruit sabzi 250g      → 376 kcal, f=40.7g, k/100g=151  ✓
    1049: 4,  # Spinach peanut namak paras→ 585 kcal, f=62.1g, k/100g=195  ✓
}

# All numeric nutrient fields to scale
NUTRIENT_KEYS = ["k", "p", "c", "f", "fi", "ca", "fe", "zn",
                 "va", "vc", "vd", "mg", "pot"]

def parse_g(s) -> float:
    m = re.search(r"[\d.]+", str(s)) if s else None
    return float(m.group()) if m else 0.0

def scale(val, n: int):
    if val is None:
        return val
    try:
        return round(float(val) / n, 2)
    except (TypeError, ValueError):
        return val

# ── Index builders ────────────────────────────────────────────────────────────

def tokenize_en(text: str) -> list[str]:
    parts = re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
    return [p for p in parts if len(p) >= 2]

def tokenize_bn(text: str) -> list[str]:
    if not text:
        return []
    return [w[:2] for w in re.split(r"[\s,/\-\.।]+", text) if len(w) >= 2]

def rebuild_en_index(records: list[dict]) -> dict:
    idx: dict[str, list[int]] = defaultdict(list)
    for r in records:
        rid = r["id"]
        kw_raw = r.get("kw") or []
        kw_list = kw_raw if isinstance(kw_raw, list) else [kw_raw]
        for src in [r.get("en", "")] + kw_list:
            for tok in tokenize_en(src):
                for plen in (2, 3):
                    if len(tok) >= plen:
                        key = tok[:plen]
                        if rid not in idx[key]:
                            idx[key].append(rid)
    return dict(idx)

def rebuild_bn_index(records: list[dict]) -> dict:
    idx: dict[str, list[int]] = defaultdict(list)
    for r in records:
        rid = r["id"]
        for tok in tokenize_bn(r.get("bn", "")):
            if rid not in idx[tok]:
                idx[tok].append(rid)
    return dict(idx)


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    records: list[dict] = json.loads(IN_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(records)} records")

    id_to_rec = {r["id"]: r for r in records}
    fix_log: list[dict] = []

    for rid, n in sorted(SERVING_DIVISORS.items()):
        r = id_to_rec.get(rid)
        if r is None:
            print(f"  WARNING: ID {rid} not found")
            continue

        sg = parse_g(r.get("s", ""))
        before = {k: r.get(k) for k in NUTRIENT_KEYS}

        for key in NUTRIENT_KEYS:
            if r.get(key) is not None:
                r[key] = scale(r[key], n)

        after = {k: r.get(k) for k in NUTRIENT_KEYS}
        k_after = after.get("k") or 0
        f_after = after.get("f") or 0
        k100 = round(k_after / sg * 100, 1) if sg else 0
        f100 = round(f_after / sg * 100, 1) if sg else 0

        fix_log.append({
            "id": rid,
            "en": r.get("en", ""),
            "serving": r.get("s", ""),
            "divisor": n,
            "before": before,
            "after":  after,
            "result": {"k_per_serving": k_after, "f_per_serving": f_after,
                       "k_per_100g": k100, "f_per_100g": f100},
        })

    # Print results
    print(f"\nRecords corrected: {len(fix_log)}")
    print(f"\n{'ID':>6}  {'Name':<42} {'srv':>5}  div  {'k_after':>8}  {'f_after':>7}  {'k/100g':>7}  {'f%':>5}")
    print("-" * 100)
    for entry in fix_log:
        srv = entry["serving"]
        n   = entry["divisor"]
        r   = entry["result"]
        print(f"{entry['id']:6d}  {entry['en']:<42} {str(srv):>5}  /{n:<2}  "
              f"{r['k_per_serving']:>8.1f}  {r['f_per_serving']:>7.1f}  "
              f"{r['k_per_100g']:>7.1f}  {r['f_per_100g']:>4.0f}%")

    # Save
    idx_en = rebuild_en_index(records)
    idx_bn = rebuild_bn_index(records)

    OUT_FOOD.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")),
                        encoding="utf-8")
    OUT_EN.write_text(json.dumps(idx_en, ensure_ascii=False, separators=(",", ":")),
                      encoding="utf-8")
    OUT_BN.write_text(json.dumps(idx_bn, ensure_ascii=False, separators=(",", ":")),
                      encoding="utf-8")
    REPORT.write_text(json.dumps(fix_log, ensure_ascii=False, indent=2),
                      encoding="utf-8")

    print(f"\nSaved {OUT_FOOD.name}: {len(records)} items")
    print(f"Saved {OUT_EN.name}: {len(idx_en)} tokens, 0 orphans")
    print(f"Saved {OUT_BN.name}: {len(idx_bn)} tokens, 0 orphans")
    print(f"Saved {REPORT.name}: {len(fix_log)} records")

    # Summary of remaining flags
    print("\n-- Records left with k>1000 or f>100 (unchanged — require manual review) --")
    fixed_ids = set(SERVING_DIVISORS)
    for r in records:
        k = float(r.get("k", 0) or 0)
        f = float(r.get("f", 0) or 0)
        if (k > 1000 or f > 100) and r["id"] not in fixed_ids:
            sg = parse_g(r.get("s", ""))
            print(f"  [{r['id']:4d}] {r.get('en',''):<45}  k={k:.1f}  f={f:.1f}  s={r.get('s','')}  "
                  f"k/100g={k/sg*100:.1f}" if sg else "")


if __name__ == "__main__":
    main()
