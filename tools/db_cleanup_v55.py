"""
DB Quality Pipeline v5.5
Input:  food_master_v5_4.json
Output: food_master_v5_5.json + index_en/bn_v5_5.json + 7 reports

Phase 1 — Nutrition Validation & Repair
Phase 2 — Bengali Text Cleanup
Phase 3 — Duplicate Consolidation
Phase 4 — Index Rebuild
Phase 5 — Write Outputs & Summary
"""

import json, re, sys, os, unicodedata
from collections import defaultdict
from copy import deepcopy

sys.stdout.reconfigure(encoding="utf-8")

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA    = os.path.join(ROOT, "assets", "data")
REPORTS = os.path.join(ROOT, "tools", "reports")
os.makedirs(REPORTS, exist_ok=True)

MASTER_IN  = os.path.join(DATA, "food_master_v5_4.json")
MASTER_OUT = os.path.join(DATA, "food_master_v5_5.json")
IDX_EN_OUT = os.path.join(DATA, "index_en_v5_5.json")
IDX_BN_OUT = os.path.join(DATA, "index_bn_v5_5.json")

def rp(name):
    return os.path.join(REPORTS, name)

# ── Load ──────────────────────────────────────────────────────────────────────
with open(MASTER_IN, encoding="utf-8") as fh:
    RAW = json.load(fh)

FOODS_BEFORE = len(RAW)
items = deepcopy(RAW)
print(f"Loaded {FOODS_BEFORE} items from {MASTER_IN}")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def norm(s: str) -> str:
    """Lowercase, strip punctuation, collapse spaces."""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def denorm(s: str) -> str:
    """norm() then remove all spaces — detects 'Pati Shapta' == 'Patishapta'."""
    return re.sub(r"\s+", "", norm(s))

STOP = {
    "the","a","an","in","on","with","and","or","of","for",
    "to","is","it","its","at","by","as","from","boiled","raw",
    "fried","plain","cooked","without","salt"
}

def name_tokens(en: str) -> set:
    return set(re.findall(r"[a-z]+", en.lower())) - STOP

def jaccard(a: set, b: set) -> float:
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)

def serving_grams(s_field: str) -> float:
    m = re.search(r"(\d+(?:\.\d+)?)\s*g", str(s_field), re.IGNORECASE)
    if m:
        return float(m.group(1))
    m = re.search(r"(\d+(?:\.\d+)?)", str(s_field))
    return float(m.group(1)) if m else 100.0

def estimated_kcal(p: float, c: float, f: float) -> float:
    return round(4 * p + 4 * c + 9 * f, 1)

def diff_pct(stored: float, est: float) -> float:
    if est <= 0:
        return 0.0
    return abs(stored - est) / est

def richness(item: dict) -> int:
    """Count non-zero optional micronutrient fields — higher = richer profile."""
    fields = ["ca", "fe", "zn", "va", "vc", "vd", "mg", "pot"]
    return sum(1 for fld in fields if float(item.get(fld, 0)) > 0)


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — NUTRITION VALIDATION & REPAIR
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 1: NUTRITION VALIDATION & REPAIR ═══")

nutrition_outliers = []   # flagged items (all violations)
repair_log         = []   # every repair applied
manual_review      = []   # items that need human attention

INVISIBLE = re.compile(
    r"[​‌‍‎‏﻿­⁠᠎]"
)

# ── Repair helpers ────────────────────────────────────────────────────────────

def try_repair_kcal(stored_k: float, est_k: float) -> tuple:
    """
    Detect obvious decimal-shift or leading-digit errors in kcal.
    Returns (fixed_value, reason) or (None, None).
    Only fires when the corrected value lands within 20% of est_k.
    Confidence threshold: 95%.
    """
    if est_k <= 0 or stored_k <= 0:
        return None, None

    candidates = []

    # /10 and /100
    for factor in [10, 100]:
        candidate = round(stored_k / factor, 1)
        if candidate > 0:
            d = diff_pct(candidate, est_k)
            if d < 0.20:
                candidates.append((candidate, f"kcal÷{factor}", d))

    # Subtract 1000 (leading-1 artifact: 1138 → 138, 1215 → 215)
    if stored_k > 1000:
        candidate = round(stored_k - 1000, 1)
        if candidate > 0:
            d = diff_pct(candidate, est_k)
            if d < 0.20:
                candidates.append((candidate, "kcal−1000", d))

    # Drop leading digit(s) from the integer string
    s = str(int(stored_k))
    for i in range(1, min(3, len(s) - 1)):
        try:
            candidate = float(s[i:])
            if candidate > 0:
                d = diff_pct(candidate, est_k)
                if d < 0.20:
                    candidates.append((candidate, f"drop_{i}_leading_digit", d))
        except ValueError:
            pass

    if not candidates:
        return None, None

    best_val, best_reason, _ = min(candidates, key=lambda x: x[2])

    # Safety: result must be plausible food kcal
    if not (5 < best_val <= 1200):
        return None, None

    return best_val, best_reason


def try_repair_macro(val: float, s_g: float, field: str) -> tuple:
    """
    Fix a macro that exceeds serving weight via decimal shift.
    Returns (fixed_value, reason) or (None, None).
    Examples: 502 fat → 50.2, 498 fat → 49.8.
    """
    if val <= s_g:
        return None, None

    for factor in [10, 100]:
        candidate = round(val / factor, 1)
        if 0 < candidate <= s_g:
            return candidate, f"{field}÷{factor}"

    return None, None


# ── Validate and repair each item ─────────────────────────────────────────────

for item in items:
    iid = item["id"]
    en  = item.get("en", "")
    s_g = serving_grams(item.get("s", "100g"))

    p  = float(item.get("p",  0))
    c  = float(item.get("c",  0))
    f  = float(item.get("f",  0))
    fi = float(item.get("fi", 0))
    k  = float(item.get("k",  0))
    ca = float(item.get("ca", 0))
    fe = float(item.get("fe", 0))
    zn = float(item.get("zn", 0))

    ek   = estimated_kcal(p, c, f)
    dp   = diff_pct(k, ek)

    # ── Collect violations ────────────────────────────────────────────────────
    violations   = []
    is_critical  = False

    if k <= 0:
        violations.append("kcal<=0"); is_critical = True
    if k > 1500:
        violations.append(f"kcal={k}>1500"); is_critical = True
    if p > s_g:
        violations.append(f"protein={p}>serving={s_g}g"); is_critical = True
    if c > s_g:
        violations.append(f"carbs={c}>serving={s_g}g"); is_critical = True
    if f > s_g:
        violations.append(f"fat={f}>serving={s_g}g"); is_critical = True
    if fi > c and fi > 1:
        violations.append(f"fiber={fi}>carbs={c}")
    if ca < 0: violations.append(f"ca<0")
    if fe < 0: violations.append(f"fe<0")
    if zn < 0: violations.append(f"zn<0")
    if ek > 0 and dp > 0.40:
        violations.append(
            f"energy_mismatch stored={k} est={ek} diff={round(dp*100)}%"
        )
    if ek > 0 and dp > 1.00:
        is_critical = True

    if not violations:
        continue

    # ── Attempt auto-repair ───────────────────────────────────────────────────
    local_repairs = []

    # Step A: fix macros that exceed serving (decimal shift)
    for field, val in [("p", p), ("c", c), ("f", f)]:
        if val > s_g:
            fixed, reason = try_repair_macro(val, s_g, field)
            if fixed is not None:
                local_repairs.append(
                    {"id": iid, "en": en, "field": field,
                     "old": val, "new": fixed, "reason": reason}
                )
                item[field] = fixed
                if field == "p": p = fixed
                elif field == "c": c = fixed
                elif field == "f": f = fixed

    # Recalculate after macro repairs
    ek = estimated_kcal(p, c, f)
    dp = diff_pct(k, ek)

    # Step B: fix kcal if still mismatched (decimal shift / leading digit)
    if ek > 0 and dp > 0.40 and k > 0:
        fixed_k, reason = try_repair_kcal(k, ek)
        if fixed_k is not None:
            local_repairs.append(
                {"id": iid, "en": en, "field": "k",
                 "old": k, "new": fixed_k, "reason": reason}
            )
            item["k"] = fixed_k
            k = fixed_k
            dp = diff_pct(k, ek)

    repair_log.extend(local_repairs)

    # ── Re-evaluate after repairs ─────────────────────────────────────────────
    still_critical = (
        k <= 0 or k > 1500 or
        p > s_g or c > s_g or f > s_g or
        (ek > 0 and dp > 1.00)
    )
    still_flagged = (
        still_critical or
        (ek > 0 and dp > 0.40) or
        (fi > c and fi > 1)
    )

    rec = {
        "id": iid, "en": en, "s": item.get("s"), "s_g": s_g,
        "k": k, "p": p, "c": c, "f": f, "fi": fi,
        "est_kcal": ek, "diff_pct": round(dp * 100, 1),
        "violations": violations,
        "auto_repaired": len(local_repairs) > 0,
        "is_critical": is_critical,
    }

    nutrition_outliers.append(rec)

    if still_flagged and not local_repairs:
        manual_review.append({
            **rec,
            "note": (
                "Critical — needs manual correction"
                if is_critical else
                "Energy mismatch >40% — verify macros or kcal"
            ),
        })

print(f"  Nutrition violations found: {len(nutrition_outliers)}")
print(f"  Auto-repairs applied:       {len(repair_log)}")
print(f"  Manual review needed:       {len(manual_review)}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — BENGALI TEXT CLEANUP
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 2: BENGALI TEXT CLEANUP ═══")

BN_RANGE      = re.compile(r"[ঀ-৿]")
LATIN_RANGE   = re.compile(r"[a-zA-Z]")
ODIA_RANGE    = re.compile(r"[ଓ-ୟ଀-୿]")
CONSEC_VOWELS = re.compile(r"[া-ৌ]{2,}")   # consecutive dependent vowel marks

bn_cleaned_count  = 0
bn_auto_fixes     = []
bn_manual_review  = []
bn_quality_report = []

for item in items:
    iid = item["id"]
    en  = item.get("en", "")
    bn_orig = item.get("bn", "")

    # ── Safe auto-fixes ───────────────────────────────────────────────────────
    bn = bn_orig

    # 1. Normalize to NFC (fixes decomposed Unicode)
    bn = unicodedata.normalize("NFC", bn)

    # 2. Remove invisible / control characters
    bn = INVISIBLE.sub("", bn)

    # 3. Collapse duplicate spaces
    bn = re.sub(r" {2,}", " ", bn)

    # 4. Strip leading/trailing whitespace and punctuation
    bn = bn.strip().strip("।,;:!?।")

    if bn != bn_orig:
        bn_auto_fixes.append({
            "id": iid, "en": en,
            "old_bn": bn_orig, "new_bn": bn
        })
        item["bn"] = bn
        bn_cleaned_count += 1

    # ── Flag issues for manual review ────────────────────────────────────────
    issues = []

    has_bengali = bool(BN_RANGE.search(bn))
    has_latin   = bool(LATIN_RANGE.search(bn))

    # Mixed English + Bengali script in BN field
    if has_bengali and has_latin:
        issues.append("mixed_script")

    # Odia script in BN field
    if ODIA_RANGE.search(bn):
        issues.append("odia_script_in_bn_field")

    # Consecutive dependent vowel marks (OCR artifact)
    if CONSEC_VOWELS.search(bn):
        issues.append("consecutive_vowel_marks_ocr")

    # BN field is pure ASCII (not a Bengali name)
    if bn and not has_bengali:
        issues.append("no_bengali_characters")

    # Suspiciously short
    if len(bn.strip()) < 2:
        issues.append("too_short")

    # Unexpected ASCII punctuation embedded mid-name
    if re.search(r"[<>{}\\|@#$%^&*]", bn):
        issues.append("unexpected_ascii_in_bn")

    if issues:
        bn_quality_report.append({"id": iid, "en": en, "bn": bn, "issues": issues})
        # Only send to manual review if not just too_short
        if any(i in issues for i in [
            "mixed_script", "odia_script_in_bn_field",
            "consecutive_vowel_marks_ocr", "no_bengali_characters"
        ]):
            bn_manual_review.append({
                "id": iid, "en": en, "bn": bn, "issues": issues,
                "note": "DO NOT AUTO-FIX — verify Bengali name manually"
            })

print(f"  Bengali records auto-cleaned: {bn_cleaned_count}")
print(f"  Bengali quality issues:       {len(bn_quality_report)}")
print(f"  Bengali records for manual review: {len(bn_manual_review)}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — DUPLICATE CONSOLIDATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 3: DUPLICATE CONSOLIDATION ═══")

id_to = {it["id"]: it for it in items}

dup_report        = {"merged": [], "skipped": []}
dup_manual_review = []
merged_away       = set()
aliases_added     = 0


def dup_confidence(a: dict, b: dict) -> float:
    """
    Multi-signal confidence that two records are the same food.
    Returns 0–100.
    """
    # 1. Normalized name equality (de-spaced) → certain duplicate
    if denorm(a.get("en", "")) == denorm(b.get("en", "")) and denorm(a.get("en", "")):
        return 100.0

    ta = name_tokens(a.get("en", ""))
    tb = name_tokens(b.get("en", ""))

    # 2. Name token Jaccard (most important signal)
    j_name = jaccard(ta, tb) if ta and tb else 0.0

    # 3. Same category
    cat_match = 1.0 if a.get("cat") == b.get("cat") else 0.0

    # 4. Keyword overlap
    kw_a = {norm(str(k)) for k in a.get("kw", [])}
    kw_b = {norm(str(k)) for k in b.get("kw", [])}
    j_kw = jaccard(kw_a, kw_b) if kw_a and kw_b else 0.0

    # 5. Bengali name similarity (token Jaccard on BN words)
    bn_a_words = set(a.get("bn", "").split())
    bn_b_words = set(b.get("bn", "").split())
    j_bn = jaccard(bn_a_words, bn_b_words) if bn_a_words and bn_b_words else 0.0

    # 6. Kcal proximity (within 15% = full score, otherwise scales)
    k_a = float(a.get("k", 0))
    k_b = float(b.get("k", 0))
    kcal_sim = 0.0
    if k_a > 0 and k_b > 0:
        kd = abs(k_a - k_b) / max(k_a, k_b)
        kcal_sim = max(0.0, 1.0 - kd / 0.15) if kd < 0.15 else 0.0

    # Weighted sum → 0–100
    score = (
        j_name  * 55 +    # name similarity most important
        cat_match * 20 +  # same category
        j_kw    * 8  +    # keyword overlap
        j_bn    * 12 +    # Bengali name overlap
        kcal_sim * 5      # nutrition similarity
    )

    return min(score, 100.0)


def select_canonical(a: dict, b: dict) -> tuple:
    """
    Given two records to merge, return (keep, drop).
    Prefer: oldest ID (smallest), then richest nutrition.
    """
    if richness(b) > richness(a) + 2:
        # Drop record is significantly richer in micronutrients — swap
        keep, drop = b, a
    else:
        keep = a if a["id"] < b["id"] else b
        drop = b if a["id"] < b["id"] else a
    return keep, drop


def best_bn(a: dict, b: dict) -> str:
    """Return whichever BN name has more Bengali characters."""
    bn_a = a.get("bn", "")
    bn_b = b.get("bn", "")
    score_a = sum(1 for ch in bn_a if "ঀ" <= ch <= "৿")
    score_b = sum(1 for ch in bn_b if "ঀ" <= ch <= "৿")
    return bn_a if score_a >= score_b else bn_b


def absorb_aliases(keep: dict, drop: dict):
    """Absorb all searchable names from drop into keep's kw list."""
    global aliases_added
    kw_set = {k.lower() for k in keep.get("kw", [])}
    kw_set.add(norm(keep.get("en", "")))

    new_kw = list(keep.get("kw", []))

    for alias in [
        drop.get("en", ""),
        norm(drop.get("en", "")),
        denorm(drop.get("en", "")),
        *drop.get("kw", []),
    ]:
        alias_lc = str(alias).lower().strip()
        if alias_lc and alias_lc not in kw_set and len(alias_lc) > 1:
            new_kw.append(alias_lc)
            kw_set.add(alias_lc)
            aliases_added += 1

    keep["kw"] = new_kw[:16]   # cap at 16 to stay lean


# ── Candidate generation ──────────────────────────────────────────────────────
merge_pairs  = []   # (conf, a_id, b_id)
seen_pairs   = set()

for i, a in enumerate(items):
    ta = name_tokens(a.get("en", ""))
    if not ta:
        continue
    for b in items[i + 1:]:
        pair_key = (min(a["id"], b["id"]), max(a["id"], b["id"]))
        if pair_key in seen_pairs:
            continue

        tb = name_tokens(b.get("en", ""))
        if not tb:
            continue

        # Quick pre-filter: must share at least one non-stop token
        # OR have de-spaced name match
        if not (ta & tb) and denorm(a.get("en","")) != denorm(b.get("en","")):
            continue

        conf = dup_confidence(a, b)
        if conf >= 70:   # collect everything ≥70 for review/merge
            merge_pairs.append((conf, a["id"], b["id"]))
            seen_pairs.add(pair_key)

merge_pairs.sort(key=lambda x: -x[0])
print(f"  Candidate pairs (conf≥70):  {len(merge_pairs)}")

# ── Execute merges ────────────────────────────────────────────────────────────
for conf, id_a, id_b in merge_pairs:
    a = id_to.get(id_a)
    b = id_to.get(id_b)
    if not a or not b:
        continue
    if id_a in merged_away or id_b in merged_away:
        continue

    keep, drop = select_canonical(a, b)
    keep_id, drop_id = keep["id"], drop["id"]

    if conf >= 90:
        # Merge: absorb BN name and all aliases, then remove drop
        keep["bn"] = best_bn(keep, drop)
        absorb_aliases(keep, drop)

        dup_report["merged"].append({
            "kept_id": keep_id, "kept_en": keep.get("en"),
            "dropped_id": drop_id, "dropped_en": drop.get("en"),
            "confidence": round(conf, 1),
            "reason": "auto_merge_conf>=90",
        })
        merged_away.add(drop_id)
    else:
        # 70–89%: flag for human decision
        dup_manual_review.append({
            "id_a": id_a, "en_a": a.get("en"), "cat_a": a.get("cat"),
            "id_b": id_b, "en_b": b.get("en"), "cat_b": b.get("cat"),
            "confidence": round(conf, 1),
            "note": "Possible duplicate — verify before merging",
        })

# Remove merged-away items
items = [it for it in items if it["id"] not in merged_away]
id_to = {it["id"]: it for it in items}

print(f"  Merged (conf≥90):           {len(dup_report['merged'])}")
print(f"  Manual review (70–89%):     {len(dup_manual_review)}")
print(f"  Items after merge:          {len(items)}")
print(f"  Search aliases added:       {aliases_added}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — INDEX REBUILD
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 4: INDEX REBUILD ═══")

items.sort(key=lambda x: x["id"])

def build_en_index(food_items):
    idx = defaultdict(set)
    for item in food_items:
        fid = item["id"]
        for word in re.findall(r"[a-z]+", item.get("en", "").lower()):
            if len(word) >= 2: idx[word[:2]].add(fid)
            if len(word) >= 3: idx[word[:3]].add(fid)
        for kw in item.get("kw", []):
            for word in re.findall(r"[a-z]+", str(kw).lower()):
                if len(word) >= 2: idx[word[:2]].add(fid)
                if len(word) >= 3: idx[word[:3]].add(fid)
    return {k: sorted(v) for k, v in idx.items()}

def build_bn_index(food_items):
    idx = defaultdict(set)
    for item in food_items:
        fid = item["id"]
        for word in item.get("bn", "").split():
            w = word.strip()
            if len(w) >= 1:
                prefix = w[:2]
                if any(0x0980 <= ord(ch) <= 0x09FF for ch in prefix):
                    idx[prefix].add(fid)
    return {k: sorted(v) for k, v in idx.items()}

idx_en = build_en_index(items)
idx_bn = build_bn_index(items)

all_ids    = {it["id"] for it in items}
en_indexed = {fid for ids in idx_en.values() for fid in ids}
bn_indexed = {fid for ids in idx_bn.values() for fid in ids}
orphan_en  = sorted(all_ids - en_indexed)
orphan_bn  = sorted(all_ids - bn_indexed)

print(f"  EN tokens: {len(idx_en)},  orphan IDs: {len(orphan_en)}")
print(f"  BN tokens: {len(idx_bn)},  orphan IDs: {len(orphan_bn)}")
if orphan_en:
    print(f"    EN orphans: {orphan_en[:10]}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — WRITE OUTPUTS & REPORTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 5: WRITE OUTPUTS ═══")

FOODS_AFTER = len(items)

# ── Food database ─────────────────────────────────────────────────────────────
with open(MASTER_OUT, "w", encoding="utf-8") as fh:
    json.dump(items, fh, ensure_ascii=False, separators=(",", ":"))
print(f"  Written: {MASTER_OUT}")

# ── Indexes ───────────────────────────────────────────────────────────────────
with open(IDX_EN_OUT, "w", encoding="utf-8") as fh:
    json.dump(idx_en, fh, ensure_ascii=False, separators=(",", ":"))
print(f"  Written: {IDX_EN_OUT}")

with open(IDX_BN_OUT, "w", encoding="utf-8") as fh:
    json.dump(idx_bn, fh, ensure_ascii=False, separators=(",", ":"))
print(f"  Written: {IDX_BN_OUT}")

# ── Reports ───────────────────────────────────────────────────────────────────
with open(rp("nutrition_outliers.json"), "w", encoding="utf-8") as fh:
    json.dump(nutrition_outliers, fh, ensure_ascii=False, indent=2)

with open(rp("nutrition_repair_report.json"), "w", encoding="utf-8") as fh:
    json.dump(repair_log, fh, ensure_ascii=False, indent=2)

with open(rp("manual_review.json"), "w", encoding="utf-8") as fh:
    json.dump(manual_review, fh, ensure_ascii=False, indent=2)

with open(rp("bn_quality_report.json"), "w", encoding="utf-8") as fh:
    json.dump(bn_quality_report, fh, ensure_ascii=False, indent=2)

with open(rp("bn_manual_review.json"), "w", encoding="utf-8") as fh:
    json.dump(bn_manual_review, fh, ensure_ascii=False, indent=2)

with open(rp("duplicate_report.json"), "w", encoding="utf-8") as fh:
    json.dump(dup_report, fh, ensure_ascii=False, indent=2)

with open(rp("duplicate_manual_review.json"), "w", encoding="utf-8") as fh:
    json.dump(dup_manual_review, fh, ensure_ascii=False, indent=2)

print(f"  Reports written to: {REPORTS}")


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═" * 58)
print("  DATABASE v5.5 — FINAL SUMMARY")
print("═" * 58)
print(f"  Foods before:                    {FOODS_BEFORE}")
print(f"  Foods after:                     {FOODS_AFTER}")
print()
print(f"  Nutrition outliers found:        {len(nutrition_outliers)}")
print(f"  Nutrition repairs applied:       {len(repair_log)}")
print(f"  Records needing manual review:   {len(manual_review)}")
print()
print(f"  Bengali records auto-cleaned:    {bn_cleaned_count}")
print(f"  Bengali records for manual review:{len(bn_manual_review)}")
print()
print(f"  Duplicates detected (≥70%):      {len(merge_pairs)}")
print(f"  Duplicates merged (≥90%):        {len(dup_report['merged'])}")
print(f"  Duplicate candidates for review: {len(dup_manual_review)}")
print()
print(f"  Search aliases added:            {aliases_added}")
print(f"  EN index tokens rebuilt:         {len(idx_en)}")
print(f"  BN index tokens rebuilt:         {len(idx_bn)}")
print(f"  Orphan IDs removed:              {len(merged_away)}")
print("═" * 58)
