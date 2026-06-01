"""
bn_qa_v6_3.py — Bengali language QA: 6-phase OCR + transliteration cleanup
Input:  food_master_v6_2.json, index_bn_v6_2.json
Output: food_master_v6_3.json, index_bn_v6_3.json + 5 report files
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
    n = len(d) if isinstance(d, list) else (len(d) if isinstance(d, dict) else "?")
    print(f"  Saved {p.name}: {n} items")

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — DETECT BAD BENGALI
# ═══════════════════════════════════════════════════════════════════════════════

SPEC_FLAGS = [
    "ওিথ", "সআউকে", "কুসতারদ", "ফলউর", "করিসপয", "দরোপস", "সতেওেদ",
    "বরোককোলি", "কাকে", "চোকোলাতে", "ওাশেদ", "কুকিেস", "পাসতরয",
    "সউফফলে", "রুসসিান", "ওালদরোফফ", "হাওআইন", "সপরউতেদ", "ফরোসতয",
    "পআউশতিক", "ানদ",
]

# Additional leading-vowel and other OCR patterns found in the data
EXTRA_FLAGS = [
    "োপেন", "েগগস", "েগগলেসস", "িতালিান", "োমেলেততে", "োমলেত",
    "উইথোুত", "োরলয", "েকলআইরস", "িসলও", "দরেসসিনগ",
    "সুনসেত", "সুনরিসে", "ুপসিদে", "বলাকক", "ফোরেসত",
    "করানবেররয", "চেররয", "হাজেলনুত", "করুসত", "গরিনপো",
    "রাসপবেররয", "সুনফলোওের", "দানিশ", "াসসোরতেদ",
    "হোত", "কোলদ", "ফলাকয", "ফলান ",
]

ALL_FLAGS = SPEC_FLAGS + EXTRA_FLAGS

def detect_suspicious(records):
    results = []
    for r in records:
        bn = r.get("bn", "")
        found = [f for f in ALL_FLAGS if f in bn]
        # Also detect standalone leading-vowel-sign words
        extra = re.findall(r'\s[িেোুূ]\S+|^[িেোুূ]\S+', bn)
        extra = [e.strip() for e in extra]
        if found or extra:
            results.append({
                "id": r["id"], "en": r["en"], "bn": bn,
                "spec_flags": [f for f in found if f in SPEC_FLAGS],
                "extra_flags": [f for f in found if f in EXTRA_FLAGS],
                "leading_vowel_fragments": extra,
            })
    return results

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — AUTO FIXES  (confidence >= 98%)
# Applied as ordered string replacements — order matters for overlapping patterns.
# ═══════════════════════════════════════════════════════════════════════════════

# Each entry: (bad_pattern, good_replacement)
# Ordered from longest/most-specific to shortest to avoid partial collisions.
ORDERED_FIXES = [
    # ── spec-mandated fixes ────────────────────────────────────────────────────
    ("কুকিেস",        "কুকিজ"),         # cookies
    ("পাসতরয",        "পেস্ট্রি"),       # pastry
    ("সউফফলে",        "সুফলে"),          # souffle
    ("রুসসিান",       "রাশিয়ান"),       # russian
    ("ওালদরোফফ",     "ওয়ালডর্ফ"),      # waldorf
    ("হাওআইন",       "হাওয়াইয়ান"),     # hawaiian
    ("সপরউতেদ",      "স্প্রাউটেড"),     # sprouted
    ("ফরোসতয",       "ফ্রস্টি"),        # frosty
    ("পআউশতিক",      "পুষ্টিকর"),       # paushtik (nutritious)
    ("বরোককোলি",     "ব্রকলি"),         # broccoli
    ("করিসপয",       "ক্রিসপি"),        # crispy
    ("ওাশেদ",        "ধোয়া"),           # washed
    ("চোকোলাতে",     "চকলেট"),          # chocolate
    ("কুসতারদ",      "কাস্টার্ড"),      # custard
    ("সতেওেদ",       "স্টিউড"),         # stewed
    ("সআউকে",        "সস"),             # sauce
    ("ওিথ",          "উইথ"),            # with
    ("ফলউর",         "আটা"),            # flour
    (" ানদ ",        " ও "),            # and

    # ── word-specific fixes BEFORE generic temperature / word rules ──────────────
    ("বুককওহোত",       "বাকওয়িট"),       # buckwheat (before হোত rule)
    ("থোুসও",          "থাউজেন্ড"),        # thousand
    (" িসলও",          " আইল্যান্ড"),      # island (leading vowel artifact)
    ("োনিোন",          "অনিয়ন"),          # onion
    ("গরইন ",          "গ্রিন "),          # green (trailing space to avoid partial)

    # ── additional high-confidence OCR corrections ─────────────────────────────
    ("োমেলেততে/োমলেত", "অমলেট/অমলেট"),  # omelette/omlet (full form first)
    ("োমেলেততে",     "অমলেট"),          # omelette standalone
    ("োমলেত",        "অমলেট"),          # omlet
    ("েগগলেসস",      "এগলেস"),          # eggless
    ("েগগস",         "এগস"),            # eggs
    ("েকলআইরস",      "এক্লেয়ার্স"),    # eclairs
    ("িতালিান",       "ইতালিয়ান"),      # italian
    ("উইথোুত",       "উইথআউট"),        # without
    ("োপেন",         "ওপেন"),           # open
    ("োরলয",         "ওরলি"),           # orly
    ("সুনসেত",       "সানসেট"),         # sunset
    ("সুনরিসে",      "সানরাইজ"),        # sunrise
    ("ুপসিদে দোওন",  "আপসাইড ডাউন"),   # upside down
    ("বলাকক",        "ব্ল্যাক"),        # black
    ("ফোরেসত",       "ফরেস্ট"),         # forest
    ("করানবেররয",    "ক্র্যানবেরি"),   # cranberry
    ("চেররয",        "চেরি"),           # cherry
    ("হাজেলনুত",     "হেজেলনাট"),       # hazelnut
    ("করুসত",        "ক্রাস্ট"),        # crust
    ("গরিনপো",       "গ্রিন পি"),       # greenpea
    ("রাসপবেররয",    "রাসবেরি"),        # raspberry
    ("সুনফলোওের",    "সানফ্লাওয়ার"),   # sunflower
    ("দানিশ",        "ড্যানিশ"),        # danish
    ("াসসোরতেদ",     "অ্যাসর্টেড"),    # assorted (leading aa-matra artifact)
    ("হোত ",         "হট "),            # hot (temperature prefix)
    ("কোলদ ",        "কোল্ড "),         # cold (temperature prefix)
    ("ফলাকয",        "ফ্লেকি"),         # flaky
    ("দরেসসিনগ",     "ড্রেসিং"),        # dressing
]

def apply_fixes(bn):
    """Apply all ordered fixes. Return (fixed_text, list_of_changes)."""
    result = bn
    changes = []
    for bad, good in ORDERED_FIXES:
        if bad in result:
            result = result.replace(bad, good)
            changes.append(f"{bad!r} -> {good!r}")
    return result, changes

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — TOKEN QUALITY AUDIT
# ═══════════════════════════════════════════════════════════════════════════════

SHORT_TOKEN_THRESHOLD = 3

KNOWN_BAD_TOKENS = {
    "কফ", "দর", "হো", "ওু", "রআ", "পআউ", "সপর",
    "ফরো", "ওাল", "সউফ", "পাস",
}

def audit_tokens(idx_bn, id_to_record):
    bad = []
    for token, ids in idx_bn.items():
        reasons = []
        if len(token) <= SHORT_TOKEN_THRESHOLD:
            reasons.append(f"short({len(token)})")
        if token in KNOWN_BAD_TOKENS:
            reasons.append("known_bad")
        # leading vowel sign (OCR artifact)
        if token and unicodedata.category(token[0]) in ("Mc", "Mn"):
            reasons.append("leading_vowel_sign")
        if reasons:
            foods = [
                {"id": i, "en": id_to_record[i]["en"],
                 "bn": id_to_record[i].get("bn", "")}
                for i in ids if i in id_to_record
            ]
            bad.append({"token": token, "len": len(token),
                        "reasons": reasons, "foods": foods[:5]})
    return bad

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — TRANSLITERATION IMPROVEMENT
# (covered by ORDERED_FIXES above; this phase collects what was repaired)
# ═══════════════════════════════════════════════════════════════════════════════

TRANSLITERATION_TARGETS = {
    "cookies":   ("কুকিেস",    "কুকিজ"),
    "pastry":    ("পাসতরয",    "পেস্ট্রি"),
    "souffle":   ("সউফফলে",    "সুফলে"),
    "russian":   ("রুসসিান",   "রাশিয়ান"),
    "waldorf":   ("ওালদরোফফ", "ওয়ালডর্ফ"),
    "hawaiian":  ("হাওআইন",   "হাওয়াইয়ান"),
    "sprouted":  ("সপরউতেদ",  "স্প্রাউটেড"),
    "custard":   ("কুসতারদ",  "কাস্টার্ড"),
    "chocolate": ("চোকোলাতে", "চকলেট"),
    "broccoli":  ("বরোককোলি", "ব্রকলি"),
    "omelette":  ("োমেলেততে", "অমলেট"),
    "eggless":   ("েগগলেসস",  "এগলেস"),
    "eclairs":   ("েকলআইরস",  "এক্লেয়ার্স"),
    "italian":   ("িতালিান",   "ইতালিয়ান"),
    "cranberry": ("করানবেররয", "ক্র্যানবেরি"),
    "cherry":    ("চেররয",     "চেরি"),
    "hazelnut":  ("হাজেলনুত",  "হেজেলনাট"),
    "raspberry": ("রাসপবেররয", "রাসবেরি"),
    "sunflower": ("সুনফলোওের", "সানফ্লাওয়ার"),
    "danish":    ("দানিশ",     "ড্যানিশ"),
}

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_unicode(text):
    try:
        text.encode("utf-8").decode("utf-8")
        return True
    except Exception:
        return False

def has_remaining_ocr(text):
    for bad, _ in ORDERED_FIXES:
        if bad in text:
            return True
    for flag in SPEC_FLAGS:
        if flag in text:
            return True
    return False

def validate_dataset(records, idx_bn):
    all_ids = {r["id"] for r in records}
    issues = []
    # Unicode validity
    for r in records:
        bn = r.get("bn", "")
        if not validate_unicode(bn):
            issues.append({"id": r["id"], "issue": "invalid_unicode", "bn": bn})
        if has_remaining_ocr(bn):
            issues.append({"id": r["id"], "issue": "ocr_fragment_remains",
                           "en": r["en"], "bn": bn})
    # Orphan IDs in index
    orphans = []
    for tok, ids in idx_bn.items():
        for i in ids:
            if i not in all_ids:
                orphans.append({"token": tok, "orphan_id": i})
    # Duplicate BN names
    bn_seen = {}
    duplicates = []
    for r in records:
        bn = r.get("bn", "")
        if bn and bn in bn_seen:
            duplicates.append({"id": r["id"], "en": r["en"], "bn": bn,
                               "duplicate_of_id": bn_seen[bn]})
        else:
            bn_seen[bn] = r["id"]
    return {
        "total_records": len(records),
        "unicode_valid": all(validate_unicode(r.get("bn","")) for r in records),
        "ocr_fragments_remain": [i for i in issues if i["issue"] == "ocr_fragment_remains"],
        "orphan_ids_in_index": orphans[:20],
        "duplicate_bn_names": duplicates[:20],
        "total_issues": len(issues),
    }

# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — REBUILD BN INDEX
# ═══════════════════════════════════════════════════════════════════════════════

def tokenize_bn(text):
    if not text: return []
    tokens = re.split(r"[\s,/\-\.।]+", text)
    return [t for t in tokens if len(t) >= 2]

def rebuild_bn_index(records):
    idx = defaultdict(list)
    for r in records:
        rid = r["id"]
        for tok in tokenize_bn(r.get("bn", "")):
            if rid not in idx[tok]:
                idx[tok].append(rid)
    return dict(idx)

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    records = load(BASE / "food_master_v6_2.json")
    idx_bn  = load(BASE / "index_bn_v6_2.json")
    id_to_record = {r["id"]: r for r in records}
    total = len(records)

    print(f"Loaded {total} records  |  BN index tokens: {len(idx_bn)}")

    # ── PHASE 1 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 1: Detect suspicious Bengali ===")
    suspicious = detect_suspicious(records)
    print(f"  Suspicious records found: {len(suspicious)}")
    save(BASE / "bn_suspicious_records.json", suspicious)

    # ── PHASE 2 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 2: Apply high-confidence fixes ===")
    auto_fix_report = []
    manual_review   = []
    ocr_fixed       = 0
    trans_fixed     = 0

    for r in records:
        bn_orig = r.get("bn", "")
        bn_new, changes = apply_fixes(bn_orig)
        if changes:
            r["bn"] = bn_new
            auto_fix_report.append({
                "id": r["id"], "en": r["en"],
                "bn_before": bn_orig, "bn_after": bn_new,
                "changes": changes,
            })
            ocr_fixed   += sum(1 for c in changes if "->" in c
                               and any(b in c for b, _ in ORDERED_FIXES[:19]))
            trans_fixed += sum(1 for c in changes
                               if any(b in c for b, _ in list(ORDERED_FIXES)[19:]))

        # Flag records that still have leading vowel-sign artifacts
        remaining_arts = re.findall(r'\s[িেোুূ]\S+|^[িেোুূ]\S+', bn_new)
        if remaining_arts:
            manual_review.append({
                "id": r["id"], "en": r["en"], "bn": bn_new,
                "remaining_artifacts": remaining_arts,
                "reason": "leading_vowel_sign_no_auto_rule",
            })

    print(f"  Records auto-fixed: {len(auto_fix_report)}")
    print(f"  Still needs manual: {len(manual_review)}")
    save(BASE / "bn_auto_fix_report.json",  auto_fix_report)

    # ── PHASE 3 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 3: Token quality audit ===")
    bad_tokens = audit_tokens(idx_bn, id_to_record)
    print(f"  Bad BN index tokens (old index): {len(bad_tokens)}")
    save(BASE / "bn_token_quality_report.json", bad_tokens)

    # ── PHASE 4 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 4: Transliteration repairs ===")
    trans_repairs = []
    for word, (bad, good) in TRANSLITERATION_TARGETS.items():
        affected = [e for e in auto_fix_report if any(bad in c for c in e["changes"])]
        if affected:
            trans_repairs.append({
                "english_word": word,
                "bad_form": bad,
                "corrected_form": good,
                "records_fixed": len(affected),
                "confidence": 98,
            })
    save(BASE / "bn_transliteration_repairs.json", trans_repairs)
    print(f"  Transliteration patterns repaired: {len(trans_repairs)}")

    # ── PHASE 5 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 5: Validation ===")
    # Rebuild index first, then validate
    new_idx_bn = rebuild_bn_index(records)
    validation = validate_dataset(records, new_idx_bn)
    validation["manual_review_count"] = len(manual_review)
    validation["auto_fixed_count"]    = len(auto_fix_report)
    validation["index_tokens_new"]    = len(new_idx_bn)
    ocr_frags = validation["ocr_fragments_remain"]
    print(f"  Unicode valid:            {validation['unicode_valid']}")
    print(f"  OCR fragments remaining:  {len(ocr_frags)}")
    print(f"  Orphan IDs in new index:  {len(validation['orphan_ids_in_index'])}")
    print(f"  Duplicate BN names:       {len(validation['duplicate_bn_names'])}")
    save(BASE / "bn_validation_report.json",    validation)
    save(BASE / "bn_manual_review.json",        manual_review)

    # ── PHASE 6 ────────────────────────────────────────────────────────────────
    print("\n=== PHASE 6: Rebuild ===")
    save(BASE / "food_master_v6_3.json", records)
    save(BASE / "index_bn_v6_3.json",   new_idx_bn)

    # ── FINAL SUMMARY ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("FINAL SUMMARY -- Bengali QA v6.3")
    print("=" * 60)
    print(f"  Total Bengali records audited:   {total}")
    print(f"  Suspicious records detected:     {len(suspicious)}")
    print(f"  Records auto-fixed:              {len(auto_fix_report)}")
    print(f"  Transliteration patterns fixed:  {len(trans_repairs)}")
    print(f"  Bad tokens (old index):          {len(bad_tokens)}")
    print(f"  OCR fragments still remaining:   {len(ocr_frags)}")
    print(f"  Manual review needed:            {len(manual_review)}")
    print(f"  BN index tokens (new):           {len(new_idx_bn)}")
    print(f"  Orphan IDs in new index:         {len(validation['orphan_ids_in_index'])}")
    print(f"  Index rebuild:                   OK")
    print("=" * 60)

    if ocr_frags:
        print("\nOCR fragments still remaining (manual fix needed):")
        for item in ocr_frags[:10]:
            print(f"  [{item['id']}] {item.get('en','')[:35]:35s} | {item['bn']}")

    if manual_review:
        print("\nManual review items:")
        for item in manual_review[:10]:
            print(f"  [{item['id']}] {item['en'][:35]:35s} | {item['bn']}")
            print(f"    artifacts: {item['remaining_artifacts']}")

if __name__ == "__main__":
    main()
