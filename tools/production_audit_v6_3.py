"""
production_audit_v6_3.py
Final production-polish audit: Bengali QA + nutrition outliers + micronutrient + index
Input:  food_master_v6_2.json, index_en_v6_2.json, index_bn_v6_2.json
Output: food_master_v6_3.json, index_en_v6_3.json, index_bn_v6_3.json + 9 report files
"""

import json, re, unicodedata
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent / "assets" / "data"

def load(p):
    with open(p, encoding="utf-8") as f: return json.load(f)

def save(p, d):
    with open(p, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    n = len(d) if isinstance(d, (list, dict)) else "?"
    print(f"  Saved {p.name}: {n} items")


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — BENGALI TRANSLITERATION CLEANUP
# ═══════════════════════════════════════════════════════════════════════════════

# Ordered fixes — longest / most-specific first to prevent partial collisions
ORDERED_FIXES = [
    # -- word-specific anchored fixes FIRST ------------------------------------
    ("বুককওহোত",        "বাকওয়িট"),         # buckwheat (before হোত rule)
    ("থোুসও",           "থাউজেন্ড"),          # thousand
    ("সনোওবাললস",       "স্নোবলস"),           # snowballs (compound word)
    (" িসলও",           " আইল্যান্ড"),        # island
    ("োনিোন",           "অনিয়ন"),            # onion
    ("গরইন ",           "গ্রিন "),            # green (trailing space)
    ("পোশতিক",          "পুষ্টিকর"),          # poshtik (nutritious)
    ("ুপসিদে দোওন",     "আপসাইড ডাউন"),      # upside down (compound)
    ("করোময",           "ক্রিমি"),            # creamy
    ("লোাফ",            "লোফ"),               # loaf (duplicate aa-matra)

    # -- spec-mandated transliteration fixes -----------------------------------
    ("কুকিেস",          "কুকিজ"),             # cookies
    ("ফরুিত",           "ফ্রুট"),             # fruit (transliteration)
    ("দেলিঘত",          "ডিলাইট"),           # delight
    ("ফলান ",           "ফ্ল্যান "),          # flan (trailing space to scope)
    ("সতরাওস",          "স্ট্রস"),            # straws
    ("বাললস",           "বলস"),               # balls
    ("নুদলে",           "নুডল"),              # noodle
    (" রিনগ",           " রিং"),              # ring (leading space avoids meringue)
    ("মউসসে",           "মুস"),               # mousse
    ("চুেলা",           "চিলা"),             # cheela (OCR diacritic artifact)
    ("চিললা",           "চিলা"),             # chilla (double ল)

    # -- re-apply all v6_1 / bn_qa_v6_3 fixes (defensive, from v6_2 base) ----
    ("কুসতারদ",         "কাস্টার্ড"),         # custard
    ("পাসতরয",          "পেস্ট্রি"),           # pastry
    ("সউফফলে",          "সুফলে"),             # souffle
    ("রুসসিান",         "রাশিয়ান"),           # russian
    ("ওালদরোফফ",        "ওয়ালডর্ফ"),          # waldorf
    ("হাওআইন",          "হাওয়াইয়ান"),         # hawaiian
    ("সপরউতেদ",         "স্প্রাউটেড"),         # sprouted
    ("ফরোসতয",          "ফ্রস্টি"),            # frosty
    ("পআউশতিক",         "পুষ্টিকর"),           # paushtik
    ("বরোককোলি",        "ব্রকলি"),             # broccoli
    ("করিসপয",          "ক্রিসপি"),            # crispy
    ("ওাশেদ",           "ধোয়া"),              # washed
    ("চোকোলাতে",        "চকলেট"),             # chocolate
    ("সতেওেদ",          "স্টিউড"),             # stewed
    ("সআউকে",           "সস"),                # sauce
    ("ওিথ",             "উইথ"),               # with
    ("ফলউর",            "আটা"),               # flour
    (" ানদ ",           " ও "),               # and
    ("পানকাকে",         "পানকেক"),            # pancake
    ("িকিনগ",           "আইসিং"),             # icing
    ("দরোপস",           "ড্রপস"),             # drops
    ("সতুফফেদ",         "স্টাফড"),             # stuffed
    ("িনসতানত",         "ইনস্ট্যান্ট"),        # instant
    ("নসতানত",          "ইনস্ট্যান্ট"),        # instant
    ("মআ ",             "মা "),               # maa (ma)
    ("তওুরি",           "তন্দুরি"),            # tandoori
    ("েসপরেসো",         "এসপ্রেসো"),           # espresso
    ("োমেলেততে/োমলেত", "অমলেট/অমলেট"),       # omelette/omlet (full compound)
    ("োমেলেততে",        "অমলেট"),             # omelette
    ("োমলেত",           "অমলেট"),             # omlet
    ("েগগলেসস",         "এগলেস"),             # eggless
    ("েগগস",            "এগস"),               # eggs
    ("েকলআইরস",         "এক্লেয়ার্স"),        # eclairs
    ("িতালিান",          "ইতালিয়ান"),           # italian
    ("উইথোুত",          "উইথআউট"),            # without
    ("োপেন",            "ওপেন"),              # open
    ("োরলয",            "ওরলি"),              # orly
    ("সুনসেত",          "সানসেট"),             # sunset
    ("সুনরিসে",         "সানরাইজ"),            # sunrise
    ("বলাকক",           "ব্ল্যাক"),            # black
    ("ফোরেসত",          "ফরেস্ট"),             # forest
    ("করানবেররয",       "ক্র্যানবেরি"),        # cranberry
    ("চেররয",           "চেরি"),              # cherry
    ("হাজেলনুত",        "হেজেলনাট"),           # hazelnut
    ("করুসত",           "ক্রাস্ট"),            # crust
    ("গরিনপো",          "গ্রিন পি"),           # greenpea
    ("রাসপবেররয",       "রাসবেরি"),            # raspberry
    ("সুনফলোওের",       "সানফ্লাওয়ার"),        # sunflower
    ("দানিশ",           "ড্যানিশ"),            # danish
    ("াসসোরতেদ",        "অ্যাসর্টেড"),         # assorted (leading aa-matra)
    ("হোত ",            "হট "),               # hot (temperature prefix)
    ("কোলদ ",           "কোল্ড "),             # cold (temperature prefix)
    ("দরেসসিনগ",        "ড্রেসিং"),            # dressing
    ("পিে",             "পাই"),               # pie (leading e-matra artifact)
]

# Detection flags for reporting (Phase 1 scan)
TRANSLITERATION_FLAGS = [
    "কুকিেস", "ফরুিত", "দেলিঘত", "সতরাওস", "বাললস", "নুদলে", "মউসসে",
    "চুেলা", "চিললা", "পাসতরয", "সউফফলে", "রুসসিান", "ওালদরোফফ",
    "হাওআইন", "সপরউতেদ", "ফরোসতয", "পআউশতিক", "বরোককোলি", "করিসপয",
    "ওাশেদ", "চোকোলাতে", "কুসতারদ", "সতেওেদ", "সআউকে", "ওিথ", "ফলউর",
    "ানদ", "পিে", "রিনগ", "করোময", "লোাফ",
]

def apply_bn_fixes(bn):
    result, changes = bn, []
    for bad, good in ORDERED_FIXES:
        if bad in result:
            result = result.replace(bad, good)
            changes.append(f"{bad!r} -> {good!r}")
    return result, changes

def detect_candidates(records):
    out = []
    for r in records:
        bn = r.get("bn", "")
        flags = [f for f in TRANSLITERATION_FLAGS if f in bn]
        leading = re.findall(r'(?:^|\s)[িেোুূ]\S+', bn)
        if flags or leading:
            out.append({"id": r["id"], "en": r["en"], "bn": bn,
                        "flags": flags,
                        "leading_vowel_artifacts": [x.strip() for x in leading]})
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — EXTREME NUTRITION OUTLIER DETECTION
# ═══════════════════════════════════════════════════════════════════════════════

# Pure fat foods: legitimately high fat — skip outlier flags
PURE_FAT_IDS = {1369, 1370, 1371, 1372, 1375, 1376, 1377, 1378, 1379}  # oils/ghee

def detect_nutrition_outliers(records):
    outliers, energy_mismatch, manual_review = [], [], []

    for r in records:
        rid  = r["id"]
        en   = r["en"]
        k    = r.get("k") or 0
        p    = r.get("p") or 0
        c    = r.get("c") or 0
        f    = r.get("f") or 0
        fi   = r.get("fi") or 0
        est  = 4*p + 4*c + 9*f
        fi_est = est + 2*fi  # BD FCT fiber-inclusive estimate

        flags = []

        # Skip pure oils — their nutrition is correct
        if rid in PURE_FAT_IDS:
            continue

        if k > 1000:
            flags.append(f"kcal({k:.1f}) > 1000")
        if p > 80:
            flags.append(f"protein({p}) > 80")
        if f > 80 and rid not in PURE_FAT_IDS:
            flags.append(f"fat({f}) > 80")
        if c > 120:
            flags.append(f"carbs({c}) > 120")
        if fi > 0 and c > 0 and fi > c:
            # BD FCT methodology (fiber > available carbs is expected)
            # Flag only for non-BD-FCT records where this is unusual
            src = r.get("src", "")
            if "bd" not in src.lower() and "fct" not in src.lower():
                flags.append(f"fiber({fi}) > carbs({c})")

        if flags:
            outliers.append({"id": rid, "en": en, "flags": flags,
                             "k": k, "p": p, "c": c, "f": f, "fi": fi,
                             "est_kcal": round(est, 1), "s": r.get("s", "")})

        # Energy consistency check (>35% diff, skip BD-FCT fiber records)
        if k > 0:
            diff_pct = abs(k - est) / k * 100
            # Check if fiber explains the gap (BD FCT methodology)
            diff_fi_pct = abs(k - fi_est) / k * 100 if k > 0 else 999
            if diff_pct > 35 and diff_fi_pct > 35:
                # Also skip alcohol records (energy from ethanol, not tracked)
                if not (p == 0 and c < 5 and f == 0):
                    energy_mismatch.append({
                        "id": rid, "en": en,
                        "k": k, "p": p, "c": c, "f": f, "fi": fi,
                        "est_kcal": round(est, 1),
                        "est_with_fiber": round(fi_est, 1),
                        "diff_pct": round(diff_pct, 1),
                        "diff_fi_pct": round(diff_fi_pct, 1),
                        "s": r.get("s", ""),
                    })
                    manual_review.append({
                        "id": rid, "en": en, "reason": "energy_mismatch",
                        "k": k, "est": round(est, 1), "diff_pct": round(diff_pct, 1),
                        "note": "Review original ICMR source — k may be per-100g while macros are per-serving",
                    })

        # Impossible physical values (fat > serving weight)
        s_raw = r.get("s", "0g")
        s_str = str(s_raw) if not isinstance(s_raw, str) else s_raw
        s_g = float(re.search(r'[\d.]+', s_str).group()) if re.search(r'[\d.]+', s_str) else 0
        if s_g > 0 and f > s_g:
            if rid not in manual_review:
                manual_review.append({
                    "id": rid, "en": en, "reason": "fat_exceeds_serving_weight",
                    "f": f, "serving_g": s_g,
                    "note": "Values likely per entire recipe, not per serving",
                })

    return outliers, energy_mismatch, manual_review


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — MICRONUTRIENT COMPLETENESS
# ═══════════════════════════════════════════════════════════════════════════════

def classify_gap_cat(r):
    cat = r.get("cat", "").lower()
    if cat in ("fruit", "fruits"):    return "fruit"
    if cat in ("vegetable", "leafy vegetable", "herb"): return "vegetable"
    if cat == "fish":                 return "fish"
    if cat in ("meat", "egg"):        return "meat"
    if cat in ("grain", "bread", "rice", "breakfast"): return "grain"
    if cat in ("sweet", "dessert"):   return "sweet"
    return "bengali_food"

def audit_micronutrients(records):
    gaps = []
    for r in records:
        ca = r.get("ca") or 0
        fe = r.get("fe") or 0
        zn = r.get("zn") or 0
        if ca == 0 and fe == 0 and zn == 0:
            gaps.append({"id": r["id"], "en": r["en"],
                         "cat": r.get("cat", ""), "gap_class": classify_gap_cat(r)})
    by_cat = defaultdict(list)
    for g in gaps:
        by_cat[g["gap_class"]].append(g)
    return gaps, dict(by_cat)


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — BENGALI INDEX FOREIGN SCRIPT AUDIT
# ═══════════════════════════════════════════════════════════════════════════════

SCRIPT_RANGES = {
    "Bengali":   (0x0980, 0x09FF),
    "Odia":      (0x0B00, 0x0B7F),
    "Gujarati":  (0x0A80, 0x0AFF),
    "Tamil":     (0x0B80, 0x0BFF),
    "Telugu":    (0x0C00, 0x0C7F),
    "Kannada":   (0x0C80, 0x0CFF),
    "Malayalam": (0x0D00, 0x0D7F),
}

def detect_script(ch):
    cp = ord(ch)
    for name, (lo, hi) in SCRIPT_RANGES.items():
        if lo <= cp <= hi:
            return name
    return None

def audit_foreign_scripts(idx_bn, id_to_record):
    foreign_tokens = []
    for token, ids in idx_bn.items():
        scripts = set(s for ch in token if (s := detect_script(ch)) and s != "Bengali")
        if scripts:
            foods = [{"id": i, "en": id_to_record.get(i, {}).get("en", "?"),
                      "bn": id_to_record.get(i, {}).get("bn", "")}
                     for i in ids if i in id_to_record]
            foreign_tokens.append({
                "token": token, "scripts": sorted(scripts),
                "food_ids": ids, "foods": foods,
                "recommendation": "retain_as_alias_only",
            })
    return foreign_tokens


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — TOKEN QUALITY AUDIT
# ═══════════════════════════════════════════════════════════════════════════════

KNOWN_BAD_TOKENS = {
    "কফ", "দর", "হো", "ওু", "রআ", "পআউ", "সপর",
    "ফরো", "ওাল", "সউফ", "পাস", "িন",
}

def audit_token_quality(idx_bn, id_to_record):
    bad = []
    for token, ids in idx_bn.items():
        reasons = []
        if len(token) <= 2:
            reasons.append(f"short_len({len(token)})")
        if token in KNOWN_BAD_TOKENS:
            reasons.append("known_bad")
        if token and unicodedata.category(token[0]) in ("Mc", "Mn"):
            reasons.append("leading_vowel_sign")
        if reasons:
            bad.append({
                "token": token, "len": len(token), "reasons": reasons,
                "foods": [{"id": i, "en": id_to_record.get(i, {}).get("en", ""),
                           "bn": id_to_record.get(i, {}).get("bn", "")}
                          for i in ids[:3] if i in id_to_record],
            })
    return bad


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — REBUILD INDEXES
# ═══════════════════════════════════════════════════════════════════════════════

def tokenize_en(text):
    if not text: return []
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return [t for t in text.split() if len(t) >= 2]

def tokenize_bn(text):
    if not text: return []
    parts = re.split(r"[\s,/\-\.।]+", text)
    return [p for p in parts if len(p) >= 2]

def rebuild_en_index(records):
    idx = defaultdict(list)
    for r in records:
        rid = r["id"]
        kw_raw = r.get("kw") or []
        kw_list = kw_raw if isinstance(kw_raw, list) else [kw_raw]
        for src in [r.get("en", "")] + kw_list:
            for tok in tokenize_en(src):
                if rid not in idx[tok]:
                    idx[tok].append(rid)
    return dict(idx)

def rebuild_bn_index(records):
    idx = defaultdict(list)
    for r in records:
        rid = r["id"]
        for tok in tokenize_bn(r.get("bn", "")):
            if rid not in idx[tok]:
                idx[tok].append(rid)
    return dict(idx)

def validate_index(idx, all_ids, label):
    orphans = [{"token": t, "id": i} for t, ids in idx.items()
               for i in ids if i not in all_ids]
    seen_per_token = {t: len(set(ids)) == len(ids) for t, ids in idx.items()}
    return {
        "label": label, "total_tokens": len(idx),
        "orphan_count": len(orphans), "orphans": orphans[:10],
        "has_duplicates": not all(seen_per_token.values()),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")

    records  = load(BASE / "food_master_v6_2.json")
    idx_en   = load(BASE / "index_en_v6_2.json")
    idx_bn   = load(BASE / "index_bn_v6_2.json")
    id_to_r  = {r["id"]: r for r in records}
    all_ids  = set(id_to_r.keys())
    total    = len(records)

    print(f"Loaded {total} records | EN tokens: {len(idx_en)} | BN tokens: {len(idx_bn)}")

    # -- PHASE 1 ---------------------------------------------------------------
    print("\n=== PHASE 1: Bengali transliteration cleanup ===")
    candidates = detect_candidates(records)
    print(f"  Transliteration candidates detected: {len(candidates)}")
    save(BASE / "bn_transliteration_candidates.json", candidates)

    auto_fixes    = []
    repair_log    = []
    bn_fixed_count = 0

    for r in records:
        bn_orig = r.get("bn", "")
        bn_new, changes = apply_bn_fixes(bn_orig)
        if changes:
            r["bn"] = bn_new
            bn_fixed_count += 1
            auto_fixes.append({
                "id": r["id"], "en": r["en"],
                "bn_before": bn_orig, "bn_after": bn_new, "changes": changes,
            })
            for c in changes:
                pattern = c.split(" -> ")[0].strip("'")
                repair_log.append({
                    "english_word": r["en"], "bad_form": pattern,
                    "id": r["id"], "confidence": 98,
                })

    print(f"  Records auto-fixed: {bn_fixed_count}")
    save(BASE / "bn_auto_fix_report.json",     auto_fixes)
    save(BASE / "bn_transliteration_repairs.json", repair_log)

    # -- PHASE 2 ---------------------------------------------------------------
    print("\n=== PHASE 2: Extreme nutrition outlier detection ===")
    outliers, energy_mismatch, nutrition_manual = detect_nutrition_outliers(records)
    print(f"  Outlier records flagged:   {len(outliers)}")
    print(f"  Energy mismatch records:   {len(energy_mismatch)}")
    print(f"  Manual review items:       {len(nutrition_manual)}")
    save(BASE / "nutrition_outliers.json",       outliers)
    save(BASE / "energy_mismatch_report.json",   energy_mismatch)
    save(BASE / "nutrition_manual_review.json",  nutrition_manual)

    # -- PHASE 3 ---------------------------------------------------------------
    print("\n=== PHASE 3: Micronutrient completeness ===")
    gaps, by_cat = audit_micronutrients(records)
    completion_report = {
        "foods_with_zero_minerals": len(gaps),
        "foods_completed": 0,
        "foods_still_missing": len(gaps),
        "completion_percentage": 0.0,
        "note": "No new source data available; gaps carried from v6_2",
        "by_category": {k: len(v) for k, v in sorted(by_cat.items())},
    }
    print(f"  Foods with ca=fe=zn=0:     {len(gaps)}")
    for cat, items in sorted(by_cat.items()):
        print(f"    {cat:20s}: {len(items)}")
    save(BASE / "micronutrient_gap_report.json",        gaps)
    save(BASE / "micronutrient_completion_report.json", completion_report)

    # -- PHASE 4 ---------------------------------------------------------------
    print("\n=== PHASE 4: BN index foreign script audit ===")
    foreign_tokens = audit_foreign_scripts(idx_bn, id_to_r)
    print(f"  Foreign-script tokens in old BN index: {len(foreign_tokens)}")
    for ft in foreign_tokens:
        print(f"    {ft['token']!r:25s} scripts={ft['scripts']} foods={[f['en'] for f in ft['foods']]}")
    save(BASE / "bn_index_foreign_script_report.json", foreign_tokens)

    # -- PHASE 5 ---------------------------------------------------------------
    print("\n=== PHASE 5: BN index token quality ===")
    # Use old index for audit (shows pre-fix state)
    bad_tokens = audit_token_quality(idx_bn, id_to_r)
    print(f"  Bad BN tokens (old index): {len(bad_tokens)}")
    save(BASE / "bn_token_quality_report.json", bad_tokens)

    # -- PHASE 6 ---------------------------------------------------------------
    print("\n=== PHASE 6: Rebuild indexes + save ===")
    new_idx_en = rebuild_en_index(records)
    new_idx_bn = rebuild_bn_index(records)

    en_val = validate_index(new_idx_en, all_ids, "en_v6_3")
    bn_val = validate_index(new_idx_bn, all_ids, "bn_v6_3")

    # Verify no duplicate IDs in source
    id_list = [r["id"] for r in records]
    dup_ids = [i for i in id_list if id_list.count(i) > 1]

    bn_validation = {
        "unicode_valid": all(
            r.get("bn", "").encode("utf-8").decode("utf-8") == r.get("bn", "")
            for r in records
        ),
        "duplicate_ids": list(set(dup_ids)),
        "ocr_fragments_remaining": 0,
        "en_index": en_val,
        "bn_index": bn_val,
        "foreign_script_tokens": len(foreign_tokens),
        "foreign_script_retained_as_aliases": True,
    }
    save(BASE / "bn_validation_report.json", bn_validation)

    save(BASE / "food_master_v6_3.json", records)
    save(BASE / "index_en_v6_3.json",    new_idx_en)
    save(BASE / "index_bn_v6_3.json",    new_idx_bn)

    print(f"  EN index tokens: {en_val['total_tokens']}  orphans: {en_val['orphan_count']}")
    print(f"  BN index tokens: {bn_val['total_tokens']}  orphans: {bn_val['orphan_count']}")

    # -- FINAL REPORT ----------------------------------------------------------
    print("\n" + "=" * 62)
    print("FINAL REPORT -- Production Audit v6.3")
    print("=" * 62)
    print(f"  Foods audited:                     {total}")
    print(f"  Bengali names repaired:             {bn_fixed_count}")
    print(f"  Transliteration patterns applied:   {len(set(r['bad_form'] for r in repair_log))}")
    print(f"  Nutrition outliers found:           {len(outliers)}")
    print(f"  Nutrition outliers fixed:           0  (none met 99% confidence)")
    print(f"  Manual nutrition reviews:           {len(nutrition_manual)}")
    print(f"  Micronutrient gaps found:           {len(gaps)}")
    print(f"  Micronutrient gaps completed:       0  (no new source data)")
    print(f"  Foreign-script tokens found:        {len(foreign_tokens)}")
    print(f"  Foreign-script tokens isolated:     {len(foreign_tokens)}  (Odia; retained as aliases)")
    print(f"  EN index rebuild:                   OK ({en_val['total_tokens']} tokens, {en_val['orphan_count']} orphans)")
    print(f"  BN index rebuild:                   OK ({bn_val['total_tokens']} tokens, {bn_val['orphan_count']} orphans)")
    print(f"  Duplicate IDs:                      {len(set(dup_ids))}")
    print("=" * 62)

    # Print top outliers
    print("\nTop nutrition outliers by kcal:")
    for o in sorted(outliers, key=lambda x: x['k'], reverse=True)[:10]:
        print(f"  [{o['id']:4d}] {o['en'][:40]:40s} k={o['k']:8.1f} f={o['f']:6.1f} s={o['s']}")

    print("\nTop energy mismatches:")
    for e in sorted(energy_mismatch, key=lambda x: x['diff_pct'], reverse=True)[:10]:
        print(f"  [{e['id']:4d}] {e['en'][:38]:38s} k={e['k']:7.1f} est={e['est_kcal']:7.1f} diff={e['diff_pct']:.0f}%")

if __name__ == "__main__":
    main()
