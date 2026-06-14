"""
Bengali Transliteration Normalization — v7.0 → v7.1
Phases 1–7: identify, fix, validate, rebuild index.
"""
import json, sys, io, re, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'data')
SRC_MASTER = os.path.join(BASE, 'food_master_v7_0.json')
SRC_IDX_BN = os.path.join(BASE, 'index_bn_v7_0.json')
OUT_MASTER = os.path.join(BASE, 'food_master_v7_1.json')
OUT_IDX_BN = os.path.join(BASE, 'index_bn_v7_1.json')
OUT_IDX_EN = os.path.join(BASE, 'index_en_v7_1.json')  # rebuilt too

data = json.load(open(SRC_MASTER, encoding='utf-8'))
idx_bn = json.load(open(SRC_IDX_BN, encoding='utf-8'))

# Also rebuild EN index — load source
SRC_IDX_EN = os.path.join(BASE, 'index_en_v7_0.json')
idx_en_src = json.load(open(SRC_IDX_EN, encoding='utf-8'))

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1+2: Known bad patterns + context-aware replacement map
# Key = (food_id, old_bn) → new_bn
# ─────────────────────────────────────────────────────────────────────────────

FIXES = {
    # id: (old_bn, new_bn)
    82:  ('ক্রিম পুফফস',             'ক্রিম পাফস'),
    88:  ('দই উইথ পোতাতোেস',         'দই ও আলু'),
    130: ('সাভউরয চিজ হোরনস',        'সেভরি চিজ হর্নস'),
    137: ('সওিতেনেদ দই',             'মিষ্টি দই'),
    138: ('থিককেনেদ সওিতেনেদ দুধ',   'ঘন মিষ্টি দুধ'),
    160: ('ভাত ডাল পোররিদগে',        'ভাত ডাল পোরিজ'),
    246: ('কলা গরউনদনুত পাসতে/পুরি', 'কলা চিনাবাদাম পেস্ট/পিউরি'),
    247: ('কলা মিলকশাকে',            'কলা মিল্কশেক'),
    270: ('আম মিলকশাকে',             'আম মিল্কশেক'),
    279: ('কমলা মিলকশাকে',           'কমলা মিল্কশেক'),
    284: ('আনারস মিলকশাকে',          'আনারস মিল্কশেক'),
    297: ('করাককেদ গম পোররিদগে',     'ভাঙা গম পোরিজ'),
    372: ('ভেরমিকেললি পোররিদগে',     'ভার্মিসেলি পোরিজ'),
    454: ('ফলাভউরেদ মিলকশাকে',      'ফ্লেভারড মিল্কশেক'),
    455: ('ফরেনচ ড্রেসিং',           'ফ্রেঞ্চ ড্রেসিং'),
    456: ('ফরেনচ অমলেট/অমলেট',      'ফ্রেঞ্চ অমলেট'),
    512: ('মসুর ও সেমোলিনা পোররিদগে','মসুর ও সুজি পোরিজ'),
    517: ('মআইজে পোররিদগে',          'ভুট্টার পোরিজ'),
    540: ('ওটস পোররিদগে',            'ওটমিল পোরিজ'),
    549: ('পোচ ব্লুবেরি পরেসেরভেস',  'পিচ ব্লুবেরি প্রিজার্ভস'),
    551: ('পোর পরেসেরভেস',           'নাশপাতি প্রিজার্ভস'),
    571: ('রোাসত পোতাতোেস',          'রোস্ট আলু'),
    581: ('সাভউরয পুফফস',            'সেভরি পাফস'),
    584: ('সেমোলিনা পোররিদগে',       'সুজি পোরিজ'),
    600: ('সতারফ্রুট পরেসেরভেস',     'স্টারফ্রুট প্রিজার্ভস'),
    602: ('স্টাফড বেকড পোতাতোেস',   'স্টাফড বেকড আলু'),
    603: ('স্টাফড বিততেরগউরদ',       'স্টাফড করলা'),
    605: ('স্টাফড রউনদ লাউ',         'স্টাফড গোল লাউ'),
    606: ('স্টাফড তোমাতোেস',         'স্টাফড টমেটো'),
    754: ('সপরিনগ বাসকেত সালাদ',     'স্প্রিং বাস্কেট সালাদ'),
    789: ('ফরেনচ স্যান্ডউইচ',        'ফ্রেঞ্চ স্যান্ডউইচ'),
    831: ('সপিকয চাটনি স্যান্ডউইচ',  'স্পাইসি চাটনি স্যান্ডউইচ'),
    832: ('সপিকয ভুট্টা চাট',         'স্পাইসি ভুট্টা চাট'),
    833: ('সপরিনগ রোল',              'স্প্রিং রোল'),
    857: ('ফরেনচ পেঁয়াজ স্যুপ',     'ফ্রেঞ্চ পেঁয়াজ স্যুপ'),
    941: ('মিষ্টি গম পোররিদগে',      'মিষ্টি গম পোরিজ'),

    # Phase 3 — additional discovered patterns
    80:  ('ক্রিম হোরনস',             'ক্রিম হর্নস'),
    984: ('ফুলকপি বাসকেত',           'ফুলকপি বাস্কেট'),

    # Additional artifacts found in spot-check
    15:  ('ওুদাপপলে রস',             'কাঠবেল রস'),          # woodapple = কাঠবেল
    110: ('পনির কআথি রোল',           'পনির কাঠি রোল'),
    415: ('ଛେନା ପୋଡ଼ା',              'ছেনা পোড়া'),          # Odia → Bengali
    517: ('মআইজে পোররিদগে',          'ভুট্টার পোরিজ'),       # duplicate — already listed above
    542: ('পআনের দো পযাজা',          'পনির দো পেঁয়াজা'),
    577: ('সারসোন কা সআগ',           'সর্ষে শাক'),
    605: ('স্টাফড রউনদ লাউ',         'স্টাফড গোল লাউ'),      # duplicate — already listed above
    648: ('ডিম ইন া পেপপের',         'ডিম পেপার বোলে'),
    848: ('ওাতেরকরেসস স্যান্ডউইচ',   'ওয়াটারক্রেস স্যান্ডউইচ'),
    992: ('কআউলিফলোওের, পো ও আলু ভুজিা', 'ফুলকপি, মটরশুটি ও আলু ভুজিয়া'),
    1434:('ପଖାଳ ଭାତ',               'পাখাল ভাত'),           # Odia → Bengali

    # Manual review fixes (Phase 6 items) — old values match v7_0 originals
    579: ('সআউনথ/সোনথ চাটনি উইথ তামারিনদ/িমলি', 'সোনঠ চাটনি সহ তেঁতুল/ইমলি'),
    580: ('সআউতিদ রাদিশেস উইথ গ্রিন শিম',       'ভাজা মূলা সহ সবুজ শিম'),
}

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4: Global pattern substitutions (applied after ID-specific fixes)
# Order matters — most specific first.
# ─────────────────────────────────────────────────────────────────────────────
GLOBAL_SUBS = [
    # Remaining known-bad transliterations not covered by ID-specific fixes
    ('পুফফস',      'পাফস'),
    ('পোতাতোেস',   'আলু'),
    ('সাভউরয',     'সেভরি'),
    ('সওিতেনেদ',   'সুইটেনড'),
    ('ভেরমিকেললি', 'ভার্মিসেলি'),
    ('পোররিদগে',   'পোরিজ'),
    ('পরেসেরভেস',  'প্রিজার্ভস'),
    ('সতারফ্রুট',  'স্টারফ্রুট'),
    ('বিততেরগউরদ', 'করলা'),
    ('রউনদ',       'গোল'),
    ('তোমাতোেস',   'টমেটো'),
    ('সপিকয',      'স্পাইসি'),
    ('সপরিনগ',     'স্প্রিং'),
    ('ফরেনচ',      'ফ্রেঞ্চ'),
    ('ফলাভউরেদ',   'ফ্লেভারড'),
    ('মিলকশাকে',   'মিল্কশেক'),
    # Phase 3 additional
    ('বাসকেত',     'বাস্কেট'),
    ('হোরনস',      'হর্নস'),
    ('পাসতে',      'পেস্ট'),
    ('গরউনদনুত',   'চিনাবাদাম'),
    ('করাককেদ',    'ভাঙা'),
    ('রোাসত',      'রোস্ট'),
    ('মআইজে',      'ভুট্টা'),
    ('থিককেনেদ',   'ঘন'),
    ('কআথি',       'কাঠি'),
    # "with" → সহ (global)
    (' উইথ ',     ' সহ '),
    # Cleanup: isolated Bengali transliterations of English prepositions
    (' ইন া ',    ' '),
    (' ইন ',      ' '),
    ('পোচ ',      'পিচ '),      # peach
    ('পোর ',      'নাশপাতি '), # pear — only when used as standalone word
    # bhujia — broken vowel sequence ভুজিা → correct ভুজিয়া
    ('ভুজিা',     'ভুজিয়া'),
    # tamarind
    ('তামারিনদ',  'তেঁতুল'),
]

# ─────────────────────────────────────────────────────────────────────────────
# High-confidence manual review candidates (confidence < 95%)
# ─────────────────────────────────────────────────────────────────────────────
MANUAL_REVIEW = []

# ─────────────────────────────────────────────────────────────────────────────
# Apply fixes
# ─────────────────────────────────────────────────────────────────────────────
fixed_ids = []
manual_ids = []
auto_fixed = 0

for item in data:
    original_bn = item['bn']
    new_bn = original_bn

    # Apply ID-specific fix first (highest accuracy)
    if item['id'] in FIXES:
        old, replacement = FIXES[item['id']]
        if old == new_bn:
            new_bn = replacement
        else:
            # BN has already changed (duplicate ID listed) — apply global pass
            pass

    # Apply global substitutions on whatever we have now
    for old_pat, new_pat in GLOBAL_SUBS:
        new_bn = new_bn.replace(old_pat, new_pat)

    # Trailing/leading space cleanup
    new_bn = re.sub(r'  +', ' ', new_bn).strip()

    if new_bn != original_bn:
        fixed_ids.append(item['id'])
        auto_fixed += 1
        print(f'  FIX ID {item["id"]:4d}: [{item["en"]}]')
        print(f'         OLD: {original_bn}')
        print(f'         NEW: {new_bn}')
        item['bn'] = new_bn

print(f'\nTotal auto-fixed: {auto_fixed}')

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 5: Validate BN index tokens — find bad tokens
# ─────────────────────────────────────────────────────────────────────────────
def bn_bigrams(text):
    """Generate 2-char word-prefix tokens from Bengali words.
    Splits on any non-Bengali character so that punctuation like / ( ) doesn't
    bleed into index tokens. Matches how LocalSearchService queries the index."""
    tokens = set()
    # Split by any char outside Bengali Unicode block (U+0980–U+09FF)
    words = re.split(r'[^ঀ-৿]+', text)
    for word in words:
        if len(word) >= 2:
            tokens.add(word[:2])  # first 2 chars = the prefix the app will look up
    return tokens

BAD_TOKEN_PATTERNS = [
    lambda t: len(t) == 1,                                        # single char
    lambda t: any(c in t for c in '0123456789()[]/' ),           # ASCII symbols/digits
    lambda t: any('଀' <= c <= '୿' for c in t),         # Odia script
    lambda t: t[0] in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', # Latin
]

bad_tokens_before = {}
for tok, ids in idx_bn.items():
    if any(p(tok) for p in BAD_TOKEN_PATTERNS):
        bad_tokens_before[tok] = ids

print(f'\nPhase 5: Bad index tokens BEFORE fix: {len(bad_tokens_before)}')
for tok, ids in sorted(bad_tokens_before.items()):
    print(f'  [{tok}] -> IDs {ids[:4]}{"..." if len(ids)>4 else ""}')

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 6: Manual review — items with remaining artifacts
# ─────────────────────────────────────────────────────────────────────────────
SUSPECT_PATTERNS = [
    'উিথ', 'ওেস', 'ওুদ', 'পপলে', 'পযাজ', 'সআগ', 'কআ', 'পআ',
    'সআ', 'ভুজিা', 'কআউলি',
]
for item in data:
    bn = item['bn']
    suspects = [p for p in SUSPECT_PATTERNS if p in bn]
    if suspects:
        MANUAL_REVIEW.append({
            'id': item['id'],
            'en': item['en'],
            'bn': bn,
            'reason': f'Remaining artifact patterns: {suspects}',
            'confidence': 70,
        })

print(f'\nPhase 6: Manual review items: {len(MANUAL_REVIEW)}')
for m in MANUAL_REVIEW:
    print(f'  ID {m["id"]}: [{m["en"]}] => {m["bn"]} ({m["reason"]})')

# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7: Rebuild BN index
# ─────────────────────────────────────────────────────────────────────────────
new_idx_bn = defaultdict(list)
for item in data:
    for prefix in bn_bigrams(item['bn']):
        new_idx_bn[prefix].append(item['id'])

# Sort IDs within each entry, sort keys
new_idx_bn = {k: sorted(v) for k, v in sorted(new_idx_bn.items())}

# Bad tokens AFTER fix
bad_tokens_after = {}
for tok in new_idx_bn:
    if any(p(tok) for p in BAD_TOKEN_PATTERNS):
        bad_tokens_after[tok] = new_idx_bn[tok]

print(f'\nPhase 7: Bad index tokens AFTER fix: {len(bad_tokens_after)}')
for tok, ids in sorted(bad_tokens_after.items()):
    print(f'  [{tok}] -> IDs {ids[:4]}{"..." if len(ids)>4 else ""}')

bad_removed = len(bad_tokens_before) - len(bad_tokens_after)
print(f'Bad tokens removed: {bad_removed}')
print(f'Total BN index tokens: {len(new_idx_bn)}')

# ─────────────────────────────────────────────────────────────────────────────
# Rebuild EN index (unchanged content, just resaved at v7_1)
# ─────────────────────────────────────────────────────────────────────────────
new_idx_en = idx_en_src  # EN names unchanged

# ─────────────────────────────────────────────────────────────────────────────
# Save outputs
# ─────────────────────────────────────────────────────────────────────────────
with open(OUT_MASTER, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print(f'\nSaved: {OUT_MASTER}')

with open(OUT_IDX_BN, 'w', encoding='utf-8') as f:
    json.dump(new_idx_bn, f, ensure_ascii=False, separators=(',', ':'))
print(f'Saved: {OUT_IDX_BN}')

with open(OUT_IDX_EN, 'w', encoding='utf-8') as f:
    json.dump(new_idx_en, f, ensure_ascii=False, separators=(',', ':'))
print(f'Saved: {OUT_IDX_EN}')

# ─────────────────────────────────────────────────────────────────────────────
# Save report files
# ─────────────────────────────────────────────────────────────────────────────
REPORT_DIR = os.path.join(os.path.dirname(__file__), '..', 'tools')

# bn_transliteration_candidates.json
candidates = []
KNOWN_BAD = ['সপিকয','সপরিনগ','সতারফ্রুট','পরেসেরভেস','পোতাতোেস','বিততেরগউরদ',
             'রউনদ','তোমাতোেস','সওিতেনেদ','ভেরমিকেললি','পোররিদগে','সাভউরয',
             'পুফফস','ফরেনচ','ফলাভউরেদ','মিলকশাকে']
# Re-scan original (v7_0) for Phase 1 report
orig = json.load(open(SRC_MASTER, encoding='utf-8'))
# We already fixed data, so use orig data loaded at top — we have item['bn'] already fixed
# so rebuild candidates from fixed data for transparency
for item in data:
    found = [p for p in KNOWN_BAD if p in item['bn']]
    if found:
        candidates.append({'id':item['id'],'en':item['en'],'bn':item['bn'],'remaining_bad':found})

with open(os.path.join(REPORT_DIR, 'bn_transliteration_candidates.json'), 'w', encoding='utf-8') as f:
    json.dump(candidates, f, ensure_ascii=False, indent=2)
print(f'\nReport: bn_transliteration_candidates.json ({len(candidates)} remaining)')

# bn_pattern_discovery_report.json
discovery = {}
DISCOVERY_PATTERNS = [
    ('উরয','savoury suffix'),('ফফস','puffs'),('রিদগে','porridge'),
    ('গউরদ','gourd'),('মিলক','milkshake'),('তোমাত','tomatoes'),
    ('পোতাত','potatoes'),('পরেস','preserves'),('করাক','cracked'),
    ('রোাস','roast'),('মআইজ','maize'),('থিকক','thickened'),
    ('বাসকেত','basket'),('পাসতে','paste'),('হোরনস','horns'),
    ('গরউনদ','groundnut'),('কেললি','vermicelli'),('উইথ','with'),
]
for pat, desc in DISCOVERY_PATTERNS:
    found = [{'id':i['id'],'en':i['en'],'bn':i['bn']} for i in data if pat in i['bn']]
    discovery[pat] = {'description':desc,'remaining_count':len(found),'items':found}

with open(os.path.join(REPORT_DIR, 'bn_pattern_discovery_report.json'), 'w', encoding='utf-8') as f:
    json.dump(discovery, f, ensure_ascii=False, indent=2)
print(f'Report: bn_pattern_discovery_report.json')

# bn_bad_tokens.json
bad_tok_report = {
    'before_fix': {k: v for k,v in sorted(bad_tokens_before.items())},
    'after_fix': {k: v for k,v in sorted(bad_tokens_after.items())},
    'removed_count': bad_removed,
}
with open(os.path.join(REPORT_DIR, 'bn_bad_tokens.json'), 'w', encoding='utf-8') as f:
    json.dump(bad_tok_report, f, ensure_ascii=False, indent=2)
print(f'Report: bn_bad_tokens.json')

# bn_manual_review.json
with open(os.path.join(REPORT_DIR, 'bn_manual_review.json'), 'w', encoding='utf-8') as f:
    json.dump(MANUAL_REVIEW, f, ensure_ascii=False, indent=2)
print(f'Report: bn_manual_review.json ({len(MANUAL_REVIEW)} items)')

# ─────────────────────────────────────────────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────────────────────────────────────────────
print(f"""
╔══════════════════════════════════════════════════════════════╗
║           FINAL REPORT — Bengali Transliteration Fix         ║
╠══════════════════════════════════════════════════════════════╣
║  Foods audited             : {len(data):>4}                          ║
║  Transliteration issues    : {auto_fixed + len(MANUAL_REVIEW):>4}  (found)               ║
║  Issues auto-fixed         : {auto_fixed:>4}                          ║
║  Issues for manual review  : {len(MANUAL_REVIEW):>4}                          ║
║  Bad index tokens before   : {len(bad_tokens_before):>4}                          ║
║  Bad index tokens after    : {len(bad_tokens_after):>4}                          ║
║  Bad tokens removed        : {bad_removed:>4}                          ║
║  BN index total tokens     : {len(new_idx_bn):>4}                          ║
║  Index rebuild status      : ✓ Complete                      ║
╚══════════════════════════════════════════════════════════════╝
""")
