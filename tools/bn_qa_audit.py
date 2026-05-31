"""
Bengali Language QA Audit — food_master_v6_0.json
Phases 1-6: detect, fix, validate, rebuild.
"""

import json, re, os, sys, unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA    = os.path.join(ROOT, "assets", "data")
REPORTS = os.path.join(ROOT, "tools", "reports")
os.makedirs(REPORTS, exist_ok=True)

def rp(name): return os.path.join(REPORTS, name)

V6_PATH     = os.path.join(DATA, "food_master_v6_0.json")
IDX_BN_PATH = os.path.join(DATA, "index_bn_v6_0.json")
V61_PATH    = os.path.join(DATA, "food_master_v6_1.json")
IDX61_PATH  = os.path.join(DATA, "index_bn_v6_1.json")

with open(V6_PATH, encoding="utf-8") as fh:
    items = json.load(fh)
with open(IDX_BN_PATH, encoding="utf-8") as fh:
    idx_bn_old = json.load(fh)

print(f"Loaded {len(items)} food items, {len(idx_bn_old)} BN index tokens")

# ── Known OCR/transliteration corruption patterns ──────────────────────────────
# Each entry: (pattern_regex, replacement_str_or_None, confidence, reason)
# replacement=None means manual review required.

PATTERN_FIXES = [
    # Exact token replacements (word-boundary aware)
    (r'ওিথ',       'উইথ',       99, 'OCR artifact for English "with"'),
    (r'সআউকে',     'সস',         99, 'OCR artifact for English "sauce"'),
    (r'ানদ',       'ও',          99, 'OCR artifact for English "and"'),
    (r'ফলউর',      'আটা',        98, 'OCR artifact for English "flour"'),
    (r'করিসপয',    'ক্রিসপি',   99, 'OCR artifact for English "crispy"'),
    (r'দরোপস',     'ড্রপস',     98, 'OCR artifact for English "drops"'),
    (r'কুসতারদ',   'কাস্টার্ড', 99, 'OCR artifact for English "custard"'),
    (r'সতেওেদ',    'স্টিউড',    99, 'OCR artifact for English "stewed"'),
    (r'বরোককোলি',  'ব্রকলি',    99, 'OCR artifact for English "broccoli"'),
    (r'কাকে',      'কেক',        98, 'OCR artifact for English "cake"'),
    (r'চোকোলাতে',  'চকলেট',     99, 'OCR artifact for English "chocolate"'),
    (r'ওাশেদ',     'ধোয়া',     99, 'OCR artifact for English "washed"'),
    # Additional corruption patterns found in data
    (r'বিতরুত',    'বিটরুট',    99, 'OCR misread of "beetroot" in Bengali'),
    (r'আফঘানি',    'আফগানি',    99, '"ঘ" should be "গ" — Afghani spelling'),
    (r'ালা কিনগ',  'আ লা কিং',  98, 'OCR artifact for French "à la King"'),
    (r' ালা ',     ' আ লা ',    98, 'Broken vowel sign — missing আ prefix'),
    (r'ালাসকা',    'আলাস্কা',   98, 'OCR artifact for "Alaska"'),
    (r'পোর ',      'পেয়ার ',   98, 'OCR artifact for "pear"'),
    # Dangling vowel signs at word start (common OCR artifact)
    (r'(?<!া-ৌািীুূৃেৈোৌ)^া',
     None, 0, 'Dangling আ-কার at string start — manual review'),
]

# Patterns that are ALWAYS suspicious (trigger flag regardless of fix)
SUSPICIOUS_EXACT = [
    'ওিথ', 'সআউকে', 'ানদ', 'ফলউর', 'করিসপয', 'দরোপস',
    'কুসতারদ', 'সতেওেদ', 'বরোককোলি', 'কাকে', 'চোকোলাতে', 'ওাশেদ',
    'বিতরুত', 'আফঘানি', 'ালাসকা', 'পোর ',
]

# Short bad tokens in index
BAD_SHORT_TOKENS = {'কফ', 'দর', 'হো', 'ওু', 'রআ', 'েস', 'াল', '(প', 'ালা'}

# ── Helpers ────────────────────────────────────────────────────────────────────

def is_valid_bengali_unicode(text):
    """Return True if all Bengali-range chars are valid Unicode codepoints."""
    for ch in text:
        cp = ord(ch)
        if 0x0980 <= cp <= 0x09FF:
            try:
                unicodedata.name(ch)
            except ValueError:
                return False
    return True

def has_mixed_script(text):
    """True if Bengali text contains Latin/ASCII letters interspersed."""
    bn_chars = sum(1 for c in text if 0x0980 <= ord(c) <= 0x09FF)
    latin_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
    return bn_chars > 0 and latin_chars > 0

def has_duplicate_vowel_signs(text):
    """Detect back-to-back identical dependent vowel signs."""
    VOWEL_SIGNS = set('ািীুূৃেৈোৌ')
    for i in range(len(text) - 1):
        if text[i] in VOWEL_SIGNS and text[i] == text[i+1]:
            return True
    return False

def has_dangling_vowel(text):
    """Detect vowel signs at word boundaries without a base consonant."""
    # Flags a vowel sign immediately after a space/start
    VOWEL_SIGNS = 'ািীুূৃেৈোৌ'
    if text and text[0] in VOWEL_SIGNS:
        return True
    for i in range(1, len(text)):
        if text[i] in VOWEL_SIGNS and text[i-1] == ' ':
            return True
    return False

def is_suspicious(bn):
    """Return list of reasons a bn field is suspicious."""
    reasons = []
    if not bn:
        reasons.append("empty_bn")
        return reasons
    for pat in SUSPICIOUS_EXACT:
        if pat in bn:
            reasons.append(f"contains_ocr_artifact: {pat!r}")
    if not is_valid_bengali_unicode(bn):
        reasons.append("invalid_unicode_codepoint")
    if has_mixed_script(bn):
        reasons.append("mixed_latin_bengali_script")
    if has_duplicate_vowel_signs(bn):
        reasons.append("duplicate_vowel_signs")
    if has_dangling_vowel(bn):
        reasons.append("dangling_vowel_sign")
    return reasons


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — DETECT SUSPICIOUS RECORDS
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 1: DETECT SUSPICIOUS RECORDS ═══")

suspicious = []
for item in items:
    bn = item.get("bn", "")
    reasons = is_suspicious(bn)
    if reasons:
        suspicious.append({
            "id":      item["id"],
            "en":      item["en"],
            "bn":      bn,
            "reasons": reasons,
        })

with open(rp("bn_suspicious_records.json"), "w", encoding="utf-8") as fh:
    json.dump({"total_suspicious": len(suspicious), "records": suspicious},
              fh, ensure_ascii=False, indent=2)
print(f"  Suspicious records: {len(suspicious)}")
for r in suspicious[:10]:
    print(f"    id={r['id']:4d}  {r['en'][:35]:<35}  bn={r['bn']!r}")
    for reason in r['reasons']:
        print(f"           ↳ {reason}")
if len(suspicious) > 10:
    print(f"    ... and {len(suspicious)-10} more — see bn_suspicious_records.json")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — TOKEN AUDIT
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 2: TOKEN AUDIT ═══")

# Score each token: length <=2, known bad set, dangling vowel, mixed script
bad_tokens = []
for token, ids in idx_bn_old.items():
    issues = []
    if token in BAD_SHORT_TOKENS:
        issues.append("known_bad_token")
    if len(token) <= 2:
        issues.append(f"length={len(token)}")
    if has_dangling_vowel(token):
        issues.append("dangling_vowel")
    if has_mixed_script(token):
        issues.append("mixed_script")
    if not is_valid_bengali_unicode(token):
        issues.append("invalid_unicode")

    if issues:
        # Find source records
        source_bns = [
            {"id": iid, "en": next((x["en"] for x in items if x["id"]==iid), "?"),
             "bn": next((x["bn"] for x in items if x["id"]==iid), "?")}
            for iid in ids[:5]
        ]
        bad_tokens.append({
            "token":   token,
            "issues":  issues,
            "id_count": len(ids),
            "sample_ids": ids[:10],
            "source_records": source_bns,
        })

with open(rp("bn_token_audit.json"), "w", encoding="utf-8") as fh:
    json.dump({"total_bad_tokens": len(bad_tokens), "tokens": bad_tokens},
              fh, ensure_ascii=False, indent=2)
print(f"  Bad/suspicious tokens: {len(bad_tokens)}")
for t in bad_tokens[:15]:
    print(f"    {t['token']!r:12}  issues={t['issues']}  ids({t['id_count']}): {t['sample_ids'][:4]}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — AUTO FIXES (confidence >= 98%)
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 3: AUTO FIXES ═══")

auto_fix_report = []
manual_candidates = []

# Work on a mutable copy keyed by id
fixed_items = {item["id"]: dict(item) for item in items}

for item in items:
    iid = item["id"]
    bn_orig = item.get("bn", "")
    if not bn_orig:
        continue

    bn_current = bn_orig
    applied_fixes = []

    for pattern, replacement, confidence, reason in PATTERN_FIXES:
        if replacement is None or confidence < 98:
            continue
        if re.search(pattern, bn_current):
            bn_new = re.sub(pattern, replacement, bn_current)
            if bn_new != bn_current:
                applied_fixes.append({
                    "pattern":     pattern,
                    "replacement": replacement,
                    "confidence":  confidence,
                    "reason":      reason,
                    "before":      bn_current,
                    "after":       bn_new,
                })
                bn_current = bn_new

    # Additional: strip leading dangling vowel signs
    if bn_current and bn_current[0] in 'ািীুূৃেৈোৌ':
        bn_new = bn_current.lstrip('ািীুূৃেৈোৌ').strip()
        if bn_new != bn_current:
            applied_fixes.append({
                "pattern":     "leading_vowel_sign",
                "replacement": "(stripped)",
                "confidence":  98,
                "reason":      "OCR artifact — vowel sign at string start",
                "before":      bn_current,
                "after":       bn_new,
            })
            bn_current = bn_new

    if applied_fixes:
        fixed_items[iid]["bn"] = bn_current
        auto_fix_report.append({
            "id":        iid,
            "en":        item["en"],
            "bn_before": bn_orig,
            "bn_after":  bn_current,
            "fixes":     applied_fixes,
        })
    elif is_suspicious(bn_orig):
        # Suspicious but no auto-fix available → manual review
        reasons = is_suspicious(bn_orig)
        manual_candidates.append({
            "id":           iid,
            "en":           item["en"],
            "current_bn":   bn_orig,
            "suggested_bn": None,
            "confidence":   0,
            "reason":       "; ".join(reasons),
        })

with open(rp("bn_auto_fix_report.json"), "w", encoding="utf-8") as fh:
    json.dump({"total_auto_fixed": len(auto_fix_report), "records": auto_fix_report},
              fh, ensure_ascii=False, indent=2)
print(f"  Auto-fixed records: {len(auto_fix_report)}")
for r in auto_fix_report[:10]:
    print(f"    id={r['id']:4d}  {r['en'][:30]:<30}  {r['bn_before']!r}  →  {r['bn_after']!r}")
if len(auto_fix_report) > 10:
    print(f"    ... and {len(auto_fix_report)-10} more — see bn_auto_fix_report.json")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — MANUAL REVIEW CANDIDATES
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 4: MANUAL REVIEW CANDIDATES ═══")

# Also catch any remaining suspicous items not yet in manual_candidates
already_fixed_ids = {r["id"] for r in auto_fix_report}
for item in items:
    if item["id"] in already_fixed_ids:
        continue
    if item["id"] in {r["id"] for r in manual_candidates}:
        continue
    bn = item.get("bn", "")
    reasons = is_suspicious(bn)
    if reasons:
        manual_candidates.append({
            "id":           item["id"],
            "en":           item["en"],
            "current_bn":   bn,
            "suggested_bn": None,
            "confidence":   0,
            "reason":       "; ".join(reasons),
        })

with open(rp("bn_manual_review.json"), "w", encoding="utf-8") as fh:
    json.dump({"total_manual": len(manual_candidates), "records": manual_candidates},
              fh, ensure_ascii=False, indent=2)
print(f"  Manual review candidates: {len(manual_candidates)}")
for r in manual_candidates[:10]:
    print(f"    id={r['id']:4d}  {r['en'][:30]:<30}  bn={r['current_bn']!r}")
    print(f"           reason: {r['reason'][:80]}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 5: VALIDATION ═══")

validation_errors = []
validation_warnings = []

for iid, item in fixed_items.items():
    bn = item.get("bn", "")
    if not bn:
        validation_warnings.append({"id": iid, "en": item["en"], "issue": "empty_bn"})
        continue
    if not is_valid_bengali_unicode(bn):
        validation_errors.append({"id": iid, "en": item["en"], "bn": bn, "issue": "invalid_unicode"})
    # Check no OCR artifacts remain
    for pat in SUSPICIOUS_EXACT:
        if pat in bn:
            validation_errors.append({
                "id": iid, "en": item["en"], "bn": bn,
                "issue": f"OCR artifact remains: {pat!r}"
            })
    if has_dangling_vowel(bn):
        validation_warnings.append({
            "id": iid, "en": item["en"], "bn": bn,
            "issue": "dangling_vowel_sign_remains"
        })

# Check index will resolve — rebuild preview
new_idx = defaultdict(list)
for iid, item in fixed_items.items():
    bn = item.get("bn", "")
    if not bn:
        continue
    for word in bn.split():
        if len(word) >= 2:
            prefix = word[:2]
            if iid not in new_idx[prefix]:
                new_idx[prefix].append(iid)

# Check all items with Bengali names appear in the index
not_indexed = []
for iid, item in fixed_items.items():
    bn = item.get("bn", "")
    if not bn:
        continue
    first_word = bn.split()[0] if bn.split() else ""
    if len(first_word) >= 2:
        prefix = first_word[:2]
        if iid not in new_idx.get(prefix, []):
            not_indexed.append(iid)

validation_status = "PASS" if not validation_errors else "FAIL"

with open(rp("bn_validation_report.json"), "w", encoding="utf-8") as fh:
    json.dump({
        "status":               validation_status,
        "errors":               len(validation_errors),
        "warnings":             len(validation_warnings),
        "not_indexed_count":    len(not_indexed),
        "error_records":        validation_errors,
        "warning_records":      validation_warnings[:20],
        "not_indexed_sample":   not_indexed[:10],
    }, fh, ensure_ascii=False, indent=2)

print(f"  Status: {validation_status}")
print(f"  Errors: {len(validation_errors)}  Warnings: {len(validation_warnings)}  Not-indexed: {len(not_indexed)}")
if validation_errors:
    for e in validation_errors[:5]:
        print(f"    ERROR id={e['id']}: {e['issue']}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — REBUILD
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 6: REBUILD ═══")

# Build food_master_v6_1.json (list preserving original order)
v61_list = [fixed_items[item["id"]] for item in items]
with open(V61_PATH, "w", encoding="utf-8") as fh:
    json.dump(v61_list, fh, ensure_ascii=False, indent=2)
print(f"  Written: {V61_PATH}")

# Build index_bn_v6_1.json
# Algorithm: 2-char prefix from each Bengali word in bn field
idx_bn_new = defaultdict(list)
for item in v61_list:
    bn = item.get("bn", "")
    iid = item["id"]
    if not bn:
        continue
    seen_prefixes = set()
    for word in bn.split():
        if len(word) >= 2:
            prefix = word[:2]
            if prefix not in seen_prefixes and iid not in idx_bn_new[prefix]:
                idx_bn_new[prefix].append(iid)
                seen_prefixes.add(prefix)

# Convert to regular dict for JSON serialisation
idx_bn_new = dict(idx_bn_new)
with open(IDX61_PATH, "w", encoding="utf-8") as fh:
    json.dump(idx_bn_new, fh, ensure_ascii=False, indent=2)
print(f"  Written: {IDX61_PATH}")
print(f"  BN index tokens (v6_0): {len(idx_bn_old)}  →  (v6_1): {len(idx_bn_new)}")

# Count removed bad tokens
old_tokens = set(idx_bn_old.keys())
new_tokens = set(idx_bn_new.keys())
removed = old_tokens - new_tokens
added   = new_tokens - old_tokens
print(f"  Tokens removed: {len(removed)}  ({sorted(removed)[:10]})")
print(f"  Tokens added:   {len(added)}")


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═"*65)
print("  BENGALI QA AUDIT — FINAL SUMMARY")
print("═"*65)
print(f"  Total Bengali records audited:   {len(items)}")
print(f"  OCR/corruption issues found:     {len(suspicious)}")
print(f"  Records auto-fixed:              {len(auto_fix_report)}")
print(f"  Records requiring manual review: {len(manual_candidates)}")
print(f"  Suspicious tokens removed:       {len(removed)}")
print(f"  New index tokens:                {len(idx_bn_new)}")
print(f"  Validation status:               {validation_status}")
print(f"  Output: food_master_v6_1.json    ({len(v61_list)} records)")
print(f"  Output: index_bn_v6_1.json       ({len(idx_bn_new)} tokens)")
print("═"*65)
