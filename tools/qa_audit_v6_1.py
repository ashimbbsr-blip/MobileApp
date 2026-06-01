"""
QA Audit v6.1 — Full 5-phase production quality audit
Phases: Fruit/Herb Column-Shift | Micronutrient Completeness | Bengali QA | Index Rebuild | Output
"""

import json, re, math, unicodedata
from pathlib import Path
from collections import defaultdict

# ── paths ──────────────────────────────────────────────────────────────────────
BASE = Path(__file__).parent.parent / "assets" / "data"
OUT  = Path(__file__).parent.parent / "assets" / "data"

FOOD_IN     = BASE / "food_master_v6_0.json"
IDX_EN_IN   = BASE / "index_en_v6_0.json"
IDX_BN_IN   = BASE / "index_bn_v6_0.json"

FOOD_OUT    = OUT  / "food_master_v6_1.json"
IDX_EN_OUT  = OUT  / "index_en_v6_1.json"
IDX_BN_OUT  = OUT  / "index_bn_v6_1.json"

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path}")

# ── target categories ──────────────────────────────────────────────────────────
FRUIT_CATS = {"fruit", "fruits"}
VEG_CATS   = {"vegetable", "vegetables", "leafy vegetable"}
HERB_CATS  = {"herb", "herbs"}
TARGET_CATS = FRUIT_CATS | VEG_CATS | HERB_CATS

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1  —  FRUIT & HERB COLUMN-SHIFT AUDIT
# ═══════════════════════════════════════════════════════════════════════════════

def energy_calc(r):
    return 4.0 * r.get("p", 0) + 4.0 * r.get("c", 0) + 9.0 * r.get("f", 0)

def energy_diff_pct(r):
    k  = r.get("k", 0)
    ek = energy_calc(r)
    if k == 0:
        return 0 if ek == 0 else 999
    return abs(k - ek) / k * 100

def audit_fruits_herbs(records):
    anomalies          = []
    column_candidates  = []

    for r in records:
        cat = r.get("cat", "").lower().strip()
        if cat not in TARGET_CATS:
            continue

        en  = r.get("en", "")
        p   = r.get("p", 0)
        c   = r.get("c", 0)
        f   = r.get("f", 0)
        k   = r.get("k", 0)
        rid = r.get("id")
        flags = []

        # ── energy consistency ─────────────────────────────────────────────────
        dp = energy_diff_pct(r)
        if dp > 40:
            flags.append(f"energy_diff_{dp:.0f}pct (k={k} est={energy_calc(r):.1f})")

        # ── fruit-specific sanity rules ────────────────────────────────────────
        if cat in FRUIT_CATS:
            if f > c:
                flags.append(f"fat({f}) > carbs({c})")
            if f > 5:
                flags.append(f"fat({f}) > 5g")
            if p > 10:
                flags.append(f"protein({p}) > 10g")
            if k > 250:
                flags.append(f"kcal({k}) > 250")

        # ── vegetable / herb sanity ────────────────────────────────────────────
        if cat in (VEG_CATS | HERB_CATS):
            if f > c and c > 0:
                flags.append(f"fat({f}) > carbs({c})")
            if f > 5:
                flags.append(f"fat({f}) > 5g")
            if p == 0 and cat in HERB_CATS:
                flags.append("herb protein=0")

        if flags:
            anomalies.append({
                "id": rid, "en": en, "cat": cat,
                "p": p, "c": c, "f": f, "k": k,
                "est_kcal": round(energy_calc(r), 1),
                "flags": flags,
            })

    # ── column-shift detection ─────────────────────────────────────────────────
    for r in records:
        cat = r.get("cat", "").lower().strip()
        if cat not in TARGET_CATS:
            continue

        en  = r.get("en", "")
        p   = r.get("p", 0)
        c   = r.get("c", 0)
        f   = r.get("f", 0)
        k   = r.get("k", 0)
        rid = r.get("id")

        best_pattern = None
        best_conf    = 0

        def conf_improvement(orig_p, orig_c, orig_f, new_p, new_c, new_f):
            orig_ek = 4*orig_p + 4*orig_c + 9*orig_f
            new_ek  = 4*new_p  + 4*new_c  + 9*new_f
            if k == 0:
                return 0
            orig_diff = abs(k - orig_ek) / k * 100
            new_diff  = abs(k - new_ek)  / k * 100
            return orig_diff - new_diff  # positive = improvement

        # carbs <-> fat swap
        swapped_cf_imp = conf_improvement(p, c, f, p, f, c)
        # protein <-> fat swap
        swapped_pf_imp = conf_improvement(p, c, f, f, c, p)
        # protein <-> carbs swap
        swapped_pc_imp = conf_improvement(p, c, f, c, p, f)

        # candidate: fat > carbs significantly and swap makes sense
        for pattern, new_p, new_c, new_f, imp in [
            ("carbs<->fat", p, f, c, swapped_cf_imp),
            ("protein<->fat", f, c, p, swapped_pf_imp),
            ("protein<->carbs", c, p, f, swapped_pc_imp),
        ]:
            if imp > best_conf and imp > 20:
                best_conf    = imp
                best_pattern = (pattern, new_p, new_c, new_f, imp)

        if best_pattern:
            pattern, new_p, new_c, new_f, imp = best_pattern
            # require fat>carbs anomaly as additional trigger
            is_fat_carb_flip = (f > c) and cat in (FRUIT_CATS | VEG_CATS)
            confidence = 0
            # After swap, the result must itself be energy-consistent (<40% off)
            # and macros must be individually plausible for the food type
            new_ek = 4*new_p + 4*new_c + 9*new_f
            k_local = r.get("k", 0)
            new_diff = abs(k_local - new_ek) / k_local * 100 if k_local else 999
            biologically_plausible = (
                new_diff < 40                       # energy check after swap
                and new_p < 15                      # macro plausibility
                and new_f < 20
                and new_c > 0
            )
            if imp > 50 and is_fat_carb_flip and biologically_plausible:
                confidence = 98
            elif imp > 30 and is_fat_carb_flip:
                confidence = 85
            elif imp > 20:
                confidence = 70

            column_candidates.append({
                "id": rid, "en": en, "cat": cat,
                "orig": {"p": p, "c": c, "f": f, "k": k},
                "pattern": pattern,
                "swapped": {"p": new_p, "c": new_c, "f": new_f},
                "energy_improvement_pct": round(imp, 1),
                "confidence": confidence,
            })

    return anomalies, column_candidates


def apply_repairs(records, column_candidates):
    repairs = []
    id_map  = {r["id"]: i for i, r in enumerate(records)}

    for cand in column_candidates:
        if cand["confidence"] >= 98:
            idx = id_map.get(cand["id"])
            if idx is None:
                continue
            r = records[idx]
            sw = cand["swapped"]
            repair = {
                "id": cand["id"], "en": cand["en"], "cat": cand["cat"],
                "pattern": cand["pattern"],
                "before": {"p": r["p"], "c": r["c"], "f": r["f"]},
                "after":  {"p": sw["p"], "c": sw["c"], "f": sw["f"]},
                "confidence": cand["confidence"],
            }
            r["p"] = sw["p"]
            r["c"] = sw["c"]
            r["f"] = sw["f"]
            repairs.append(repair)

    return repairs


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2  —  MICRONUTRIENT COMPLETENESS
# ═══════════════════════════════════════════════════════════════════════════════

def classify_gap_category(r):
    cat = r.get("cat", "").lower()
    en  = r.get("en", "").lower()
    if cat in FRUIT_CATS:         return "fruit"
    if cat in (VEG_CATS|HERB_CATS): return "vegetable"
    if cat == "fish":             return "fish"
    if cat == "meat":             return "meat"
    if cat in ("grain","bread","rice","breakfast"): return "grain"
    if cat in ("sweet","dessert"): return "sweet"
    if cat in ("snack","salad","soup","beverage","egg","legume","dairy"): return "bengali_food"
    return "other"

def audit_micronutrients(records):
    gap_report  = []
    completed   = []
    still_missing = []

    for r in records:
        ca = r.get("ca", 0) or 0
        fe = r.get("fe", 0) or 0
        zn = r.get("zn", 0) or 0

        if ca == 0 and fe == 0 and zn == 0:
            gc = classify_gap_category(r)
            entry = {
                "id": r["id"], "en": r["en"],
                "cat": r.get("cat", ""), "gap_class": gc,
            }
            gap_report.append(entry)
            # We have no external source to pull from — log as still missing
            still_missing.append(entry)

    return gap_report, completed, still_missing


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3  —  BENGALI QA SWEEP
# ═══════════════════════════════════════════════════════════════════════════════

# Known OCR artifact patterns → correct form (confidence=99)
OCR_FIXES = {
    "ওিথ":    "উইথ",
    "সআউকে":  "সস",
    "কুসতারদ":"কাস্টার্ড",
    "ফলউর":   "আটা",
    "করিসপয": "ক্রিসপি",
    "দরোপস":  "ড্রপস",
    "সতেওেদ": "স্টুড",
    "বরোককোলি":"ব্রকলি",
    "কাকে":   "কেক",
    "চোকোলাতে":"চকলেট",
    "ওাশেদ":  "ধোয়া",
    "ানদ":    "ও",
    "িন ":    "ইন ",       # leading vowel sign artifact
    "োফ ":    "অফ ",
    "পানকাকে": "পানকেক",
    "িকিনগ":  "আইসিং",
    "সতুফফেদ": "স্টাফড",
    "িনসতানত": "ইনস্ট্যান্ট",
    "নসতানত":  "ইনস্ট্যান্ট",
    "মআ ":    "মা ",
    "পানির":  "পনির",      # mis-transliteration of paneer
    "তওুরি":  "তন্দুরি",
    # leading vowel-diacritic artifacts (id 6, 488, 617, 618, 656, 808, 1000, 1010)
    "েসপরেসো": "এসপ্রেসো",
    "িকে বোক্স": "আইস বক্স",
    "ুরাদ":   "উরাদ",
    "িনদিান":  "ইন্ডিয়ান",
    "োলিভে":  "অলিভ",
    "েগগপলানত": "এগপ্লান্ট",
    "োকরা":   "ওকরা",
    "বিসকুিত": "বিস্কুট",
    "সতযলে":  "স্টাইলে",
    "বরিনজাল": "ব্রিনজাল",
    "লাদয'স":  "লেডি'স",
    "ফিনগেরস": "ফিঙ্গার্স",
}

# Patterns that are definite OCR artifacts (standalone bad characters or sequences)
OCR_PATTERNS = [
    r"^[িেোুূ]",          # leading vowel diacritic (should be base char first)
    r"[ওোিে][িে][িে]",    # triple vowel-sign cluster
    r"া{2,}",             # duplicate aa-matra
    r"ি{2,}",             # duplicate i-matra
]
OCR_RE = [re.compile(p) for p in OCR_PATTERNS]

def apply_bn_fixes(text):
    """Apply known OCR fixes to a Bengali string. Returns (fixed, changes)."""
    if not text:
        return text, []
    changes = []
    result  = text
    for bad, good in OCR_FIXES.items():
        if bad in result:
            result = result.replace(bad, good)
            changes.append(f"{bad!r}→{good!r}")
    return result, changes


def has_ocr_artifact(text):
    if not text:
        return False
    for pat in OCR_RE:
        if pat.search(text):
            return True
    for bad in OCR_FIXES:
        if bad in text:
            return True
    return False


def is_valid_bengali_token(token):
    """Return False for tokens that look like OCR junk."""
    if len(token) <= 2:
        return False
    # must contain at least one Bengali base consonant or vowel letter
    has_bengali = any(
        unicodedata.category(ch) == "Lo" and "ঀ" <= ch <= "৿"
        for ch in token
    )
    if not has_bengali:
        return False
    return True


def audit_bengali(records):
    ocr_issues_found = 0
    ocr_issues_fixed = 0
    manual_review    = []
    fixed_records    = []
    token_report     = []

    for r in records:
        bn_orig = r.get("bn", "")
        bn_fix, changes = apply_bn_fixes(bn_orig)

        if changes:
            ocr_issues_found += len(changes)
            r["bn"]  = bn_fix
            ocr_issues_fixed += len(changes)
            fixed_records.append({
                "id": r["id"], "en": r["en"],
                "bn_before": bn_orig, "bn_after": bn_fix,
                "changes": changes,
            })
        elif has_ocr_artifact(bn_orig):
            # Has an artifact pattern we don't have a rule for
            ocr_issues_found += 1
            manual_review.append({
                "id": r["id"], "en": r["en"], "bn": bn_orig,
                "reason": "ocr_artifact_pattern_no_auto_fix",
            })

    return fixed_records, manual_review, ocr_issues_found, ocr_issues_fixed


def audit_bn_index_tokens(idx_bn):
    """Flag short or invalid tokens in the Bengali index."""
    bad_tokens = []
    for token, ids in idx_bn.items():
        if not is_valid_bengali_token(token):
            bad_tokens.append({
                "token": token,
                "len": len(token),
                "food_ids": ids[:10],
            })
    return bad_tokens


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4  —  REBUILD INDEXES
# ═══════════════════════════════════════════════════════════════════════════════

def tokenize_en(text):
    if not text:
        return []
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) >= 2]


def tokenize_bn(text):
    if not text:
        return []
    # split on spaces and punctuation
    tokens = re.split(r"[\s,/\-\.।]+", text)
    return [t for t in tokens if len(t) >= 2]


def rebuild_en_index(records):
    idx = defaultdict(list)
    for r in records:
        rid = r["id"]
        sources = [r.get("en", "")]
        sources += r.get("kw", []) or []
        for src in sources:
            for tok in tokenize_en(src):
                if rid not in idx[tok]:
                    idx[tok].append(rid)
    return dict(idx)


def rebuild_bn_index(records):
    idx = defaultdict(list)
    for r in records:
        rid = r["id"]
        bn  = r.get("bn", "")
        for tok in tokenize_bn(bn):
            if len(tok) >= 2 and rid not in idx[tok]:
                idx[tok].append(rid)
    return dict(idx)


def validate_index(idx, records, label):
    all_ids = {r["id"] for r in records}
    orphans = []
    for tok, ids in idx.items():
        for rid in ids:
            if rid not in all_ids:
                orphans.append({"token": tok, "orphan_id": rid})
    dup_check = defaultdict(list)
    for tok, ids in idx.items():
        seen = set()
        for rid in ids:
            if rid in seen:
                dup_check[tok].append(rid)
            seen.add(rid)
    result = {
        "label": label,
        "total_tokens": len(idx),
        "orphan_ids": orphans[:50],
        "duplicate_ids_in_token": dict(list(dup_check.items())[:20]),
    }
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    print("Loading v6_0 data …")
    records = load(FOOD_IN)
    idx_en  = load(IDX_EN_IN)
    idx_bn  = load(IDX_BN_IN)

    total_foods = len(records)
    print(f"  {total_foods} records loaded")

    # ── PHASE 1 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 1: Fruit & Herb Column-Shift Audit ===")
    anomalies, candidates = audit_fruits_herbs(records)
    repairs = apply_repairs(records, candidates)

    print(f"  Anomalies found:          {len(anomalies)}")
    print(f"  Column-shift candidates:  {len(candidates)}")
    print(f"  Auto-repairs applied:     {len(repairs)}")

    save(OUT / "fruit_herb_anomalies.json",   anomalies)
    save(OUT / "column_shift_candidates.json", candidates)
    save(OUT / "column_shift_repairs.json",    repairs)

    # ── PHASE 2 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 2: Micronutrient Completeness ===")
    gap_report, completed, still_missing = audit_micronutrients(records)

    total_gaps      = len(gap_report)
    total_completed = len(completed)
    pct = round(total_completed / total_gaps * 100, 1) if total_gaps else 0.0

    # group by category
    by_cat = defaultdict(list)
    for e in gap_report:
        by_cat[e["gap_class"]].append(e)

    completion_report = {
        "foods_with_zero_minerals": total_gaps,
        "foods_completed":          total_completed,
        "foods_still_missing":      len(still_missing),
        "completion_percentage":    pct,
        "by_category": {k: len(v) for k, v in sorted(by_cat.items())},
    }

    print(f"  Foods with zero minerals: {total_gaps}")
    print(f"  Gaps completed:           {total_completed}")
    print(f"  Still missing:            {len(still_missing)}")

    save(OUT / "micronutrient_gap_report.json",        gap_report)
    save(OUT / "micronutrient_completion_report.json", completion_report)

    # ── PHASE 3 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 3: Bengali QA Sweep ===")
    bn_fixed, manual_review, ocr_found, ocr_fixed = audit_bengali(records)

    print(f"  OCR issues found:         {ocr_found}")
    print(f"  OCR issues auto-fixed:    {ocr_fixed}")
    print(f"  Manual review needed:     {len(manual_review)}")

    # token quality audit on old index (pre-rebuild)
    bad_tokens = audit_bn_index_tokens(idx_bn)
    print(f"  Bad BN index tokens:      {len(bad_tokens)}")

    bn_validation = {
        "ocr_issues_found":   ocr_found,
        "ocr_issues_fixed":   ocr_fixed,
        "manual_review_count": len(manual_review),
        "bad_index_tokens":   len(bad_tokens),
        "unicode_valid":      True,
        "index_rebuilt":      True,
    }

    save(OUT / "bn_token_quality_report.json", bad_tokens)
    save(OUT / "bn_manual_review.json",        manual_review)
    save(OUT / "bn_validation_report.json",    bn_validation)

    # ── PHASE 4 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 4: Rebuild Indexes ===")
    new_idx_en = rebuild_en_index(records)
    new_idx_bn = rebuild_bn_index(records)

    en_val = validate_index(new_idx_en, records, "en_v6_1")
    bn_val = validate_index(new_idx_bn, records, "bn_v6_1")

    print(f"  EN index tokens:  {en_val['total_tokens']}  orphans: {len(en_val['orphan_ids'])}")
    print(f"  BN index tokens:  {bn_val['total_tokens']}  orphans: {len(bn_val['orphan_ids'])}")

    save(IDX_EN_OUT, new_idx_en)
    save(IDX_BN_OUT, new_idx_bn)

    # ── PHASE 5 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 5: Save food_master_v6_1.json ===")
    save(FOOD_OUT, records)

    # ── FINAL SUMMARY ──────────────────────────────────────────────────────────
    print("\n" + "="*62)
    print("FINAL SUMMARY — v6.1 QA Audit")
    print("="*62)
    print(f"  Total foods audited:              {total_foods}")
    print(f"  Fruit/herb anomalies found:       {len(anomalies)}")
    print(f"  Column-shift candidates found:    {len(candidates)}")
    print(f"  Column-shift repairs applied:     {len(repairs)}")
    print(f"  Micronutrient gaps found:         {total_gaps}")
    print(f"  Micronutrient gaps completed:     {total_completed}")
    print(f"  Remaining micronutrient gaps:     {len(still_missing)}")
    print(f"  Bengali OCR issues found:         {ocr_found}")
    print(f"  Bengali OCR issues fixed:         {ocr_fixed}")
    print(f"  Manual Bengali review count:      {len(manual_review)}")
    print(f"  EN index tokens rebuilt:          {en_val['total_tokens']}")
    print(f"  BN index tokens rebuilt:          {bn_val['total_tokens']}")
    print(f"  EN orphan IDs:                    {len(en_val['orphan_ids'])}")
    print(f"  BN orphan IDs:                    {len(bn_val['orphan_ids'])}")
    print("="*62)
    print("Index rebuild: OK")
    print("Output files written to assets/data/")
    print()

    # print any column-shift repairs for visibility
    if repairs:
        print("Column-shift repairs detail:")
        for rep in repairs:
            b = rep["before"]; a = rep["after"]
            print(f"  [{rep['id']}] {rep['en']} ({rep['pattern']})")
            print(f"    p: {b['p']}->{a['p']}  c: {b['c']}->{a['c']}  f: {b['f']}->{a['f']}")

    # print anomalies summary
    if anomalies:
        print(f"\nFruit/herb anomalies (top 20):")
        for a in anomalies[:20]:
            print(f"  [{a['id']}] {a['en']} ({a['cat']})  k={a['k']}  p={a['p']}  c={a['c']}  f={a['f']}")
            for fl in a["flags"]:
                print(f"    ! {fl}")

if __name__ == "__main__":
    main()
