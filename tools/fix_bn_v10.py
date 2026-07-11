"""
Bengali transliteration fix for food_master_v10.json.

Two-pass approach:
  Pass 1 — Word-level dictionary: exact replacements for known bad phrases/words.
  Pass 2 — Conservative matra fix: C + V_ind + C → C + V_matra + C
            Only fires when the preceding char is a consonant, virama, or nukta
            (NOT when preceded by a vowel matra — that would break বাইক, লাইট, etc.)

Usage:
    py tools/fix_bn_v10.py
"""

import json, re, sys, io, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE = os.path.join(os.path.dirname(__file__), '..', 'assets', 'data')
MASTER = os.path.join(BASE, 'food_master_v10.json')

# ── Bengali Unicode helpers ──────────────────────────────────────────────────

# Independent vowels we want to convert (excluding অ — too risky to auto-fix)
INDEP_VOWELS = frozenset('আইঈউঊএঐওঔ')

# Dependent vowel signs (matras): U+09BE – U+09CC
# These are the multi-char forms in NFC; U+09BE=া, U+09BF=ি, U+09C0=ী, etc.
MATRAS = frozenset('ািীুূৃেৈোৌ')

# Virama (hasanta), nukta, anusvara, visarga, chandrabindu
VIRAMA   = '্'   # ্
NUKTA    = '়'   # ়
ANUSV    = 'ং'   # ং
VISARG   = 'ঃ'   # ঃ
CHANDRA  = 'ঁ'   # ঁ

NON_MATRA_MODIFIERS = frozenset([VIRAMA, NUKTA, ANUSV, VISARG, CHANDRA])

VOWEL_TO_MATRA = {
    'আ': 'া',  # া
    'ই': 'ি',  # ি
    'ঈ': 'ী',  # ী
    'উ': 'ু',  # ু
    'ঊ': 'ূ',  # ূ
    'এ': 'ে',  # ে
    'ঐ': 'ৈ',  # ৈ
    'ও': 'ো',  # ো
    'ঔ': 'ৌ',  # ৌ
}


def is_consonant(c):
    """Basic Bengali consonants (U+0995–U+09B9) plus ৎ ড় ঢ় য়."""
    return 'ক' <= c <= 'হ' or c in 'ৎড়ঢ়য়'


def prev_is_consonant_context(c):
    """True if 'c' as the preceding character means we're in a consonant cluster.
    Excludes vowel matras so we don't break diphthongs like বাইক, লাইট, পাউরুটি."""
    return is_consonant(c) or c in NON_MATRA_MODIFIERS


def fix_matra_in_word(word):
    """Apply conservative matra fix to a single Bengali word token."""
    chars = list(word)
    n = len(chars)
    result = list(chars)
    for i in range(1, n - 1):          # never touch first or last char
        c = chars[i]
        if c not in INDEP_VOWELS:
            continue
        prev, nxt = chars[i - 1], chars[i + 1]
        if prev_is_consonant_context(prev) and is_consonant(nxt):
            result[i] = VOWEL_TO_MATRA[c]
    return ''.join(result)


def fix_matra_in_name(bn):
    """Split on non-Bengali chars, fix each token, rejoin."""
    # Split preserving delimiters so we can rejoin exactly
    tokens = re.split(r'([^ঀ-৿]+)', bn)
    fixed = []
    for tok in tokens:
        if tok and any('ঀ' <= c <= '৿' for c in tok):
            fixed.append(fix_matra_in_word(tok))
        else:
            fixed.append(tok)
    return ''.join(fixed)


# ── Pass-1 word/phrase dictionary ────────────────────────────────────────────
# Maps exact bad BN substrings → correct replacements.
# Ordered: longer / more specific phrases first.

WORD_DICT = [
    # ── Porridge (পোররিদগে → পোরিজ) — already fixed in v7.1 but may recur ──
    ('পোররিদগে',   'পোরিজ'),
    ('মিলকশাকে',   'মিল্কশেক'),
    ('মিলকশেক',    'মিল্কশেক'),   # partial fix artifact
    ('পুফফস',      'পাফস'),
    ('পরেসেরভেস',  'প্রিজার্ভস'),
    ('ভেরমিকেললি', 'ভার্মিসেলি'),
    ('সাভউরয',     'সেভরি'),
    ('সওিতেনেদ',   'সুইটেনড'),
    ('বাসকেত',     'বাস্কেট'),
    ('হোরনস',      'হর্নস'),
    ('করাককেদ',    'ভাঙা'),
    ('গরউনদনুত',   'চিনাবাদাম'),
    ('থিককেনেদ',   'ঘন'),
    ('ফলাভউরেদ',   'ফ্লেভারড'),
    ('ফরেনচ',      'ফ্রেঞ্চ'),
    ('সপরিনগ',     'স্প্রিং'),
    ('সপিকয',      'স্পাইসি'),
    ('সতারফ্রুট',  'স্টারফ্রুট'),
    ('বিততেরগউরদ', 'করলা'),
    ('তোমাতোেস',   'টমেটো'),
    ('পোতাতোেস',   'আলু'),
    ('রউনদ',       'গোল'),
    ('তামারিনদ',   'তেঁতুল'),
    ('পাসতে',      'পেস্ট'),
    (' উইথ ',      ' সহ '),
    (' ইন া ',     ' '),
    (' ইন ',       ' '),
    ('ভুজিা',      'ভুজিয়া'),
    ('পোচ ',       'পিচ '),         # peach
    ('পোর ',       'নাশপাতি '),    # pear

    # ── Brand/product words commonly transliterated badly ────────────────────
    # OZiva-style
    ('ওজইভঅ',      'ওজিভা'),
    ('ওজিভঅ',      'ওজিভা'),
    # Kids
    ('কইডস',       'কিডস'),
    # Plant, Protein, Powder
    ('পলঅনট',      'প্ল্যান্ট'),
    ('পরোটিন',     'প্রোটিন'),     # common wrong form
    ('পরটিন',      'প্রোটিন'),
    ('পাউডার',     'পাউডার'),      # already correct — keep
    # Drink
    ('ডরইনক',      'ড্রিংক'),
    ('ডরিনক',      'ড্রিংক'),
    # Junior
    ('জউনিওর',     'জুনিয়র'),
    ('জউনিয়র',    'জুনিয়র'),
    # Ensure / Horlicks / Bournvita style artifacts
    ('এনসউর',      'এনশিওর'),
    # Whey
    ('ওহেয',       'হোয়ে'),
    # Vanilla
    ('ভানিললা',    'ভ্যানিলা'),
    ('ভেনিলা',     'ভ্যানিলা'),
    # Chocolate
    ('চোকোলেট',    'চকোলেট'),
    # Strawberry
    ('সতরাওবেররয', 'স্ট্রবেরি'),
    ('সতরাবেরি',   'স্ট্রবেরি'),
    # Blueberry
    ('বলউবেররি',   'ব্লুবেরি'),
    ('বলুবেরি',    'ব্লুবেরি'),
    # Mango
    ('মআনগো',      'আম'),
    # Apple
    ('আপপলে',      'আপেল'),
    ('আপলে',       'আপেল'),
    # Banana
    ('বানানা',     'কলা'),         # "Banana" in Bengali = কলা
    # Cranberry
    ('করানবেররি',  'ক্র্যানবেরি'),
    # Raspberry
    ('রাসপবেররি',  'রাস্পবেরি'),
    # Ginger
    ('গিনগের',     'আদা'),
    # Turmeric
    ('তউরমেরিক',   'হলুদ'),
    # Cinnamon
    ('সিননামন',    'দারুচিনি'),
    # Cardamom
    ('কারদামোম',   'এলাচ'),
    # Clove
    ('ক্লোভে',     'লবঙ্গ'),
    # Pepper (standalone word only; পেপারোনি = pepperoni sausage must NOT be changed)
    ('পেপপের',     'মরিচ'),
    (' পেপার ',    ' মরিচ '),   # standalone "pepper" as vegetable
    # Cumin
    ('কউমিন',      'জিরা'),
    # Coriander
    ('কোরিআনডের',  'ধনে'),
    # Fenugreek
    ('ফেনউগরিক',   'মেথি'),
    # Mustard
    ('মউসতারদ',    'সরিষা'),
    # Spinach
    ('সপিনাচ',     'পালংশাক'),
    # Broccoli
    ('বরোককোলি',   'ব্রকলি'),
    ('বরককোলি',    'ব্রকলি'),
    # Zucchini
    ('জউককিনি',    'জুকিনি'),
    # Avocado
    ('আভোকাডো',    'অ্যাভোকাডো'),
    # Kiwi
    ('কিওই',       'কিউই'),
    # Pomegranate
    ('পোমেগরানাতে', 'ডালিম'),
    # Watermelon
    ('ওাতেরমেলোন',  'তরমুজ'),
    ('ওয়াটারমেলন', 'তরমুজ'),
    # Pineapple
    ('পিনেআপপলে',   'আনারস'),
    # Papaya
    ('পাপায়া',     'পেঁপে'),       # already correct form preserved

    # ── Fix common "with" artifacts ──
    ('সাহ ',       'সহ '),   # সাহ is wrong form of সহ

    # ── Fix common Odia remnants ──
    ('ଛେ', 'ছে'),  # Odia cha → Bengali
]


def apply_word_dict(bn):
    for old, new in WORD_DICT:
        if old in bn:
            bn = bn.replace(old, new)
    return bn


# ── Main ─────────────────────────────────────────────────────────────────────

def fix_bn(bn):
    if not bn:
        return bn
    s = apply_word_dict(bn)
    s = fix_matra_in_name(s)
    # Normalize multiple spaces
    s = re.sub(r'  +', ' ', s).strip()
    return s


def main():
    print(f'Loading {MASTER}...')
    with open(MASTER, encoding='utf-8') as f:
        data = json.load(f)
    print(f'  {len(data)} items')

    fixed_count = 0
    samples = []

    for item in data:
        orig = item.get('bn', '')
        if not orig:
            continue
        fixed = fix_bn(orig)
        if fixed != orig:
            item['bn'] = fixed
            fixed_count += 1
            if len(samples) < 40:
                en = item.get('en', '')
                # Safe ASCII representation for Windows console
                orig_safe  = orig.encode('ascii', 'backslashreplace').decode('ascii')
                fixed_safe = fixed.encode('ascii', 'backslashreplace').decode('ascii')
                samples.append(f'  [{en}]\n    OLD: {orig_safe}\n    NEW: {fixed_safe}')

    print(f'\nFixed: {fixed_count} items')
    for s in samples:
        print(s)

    # Save in-place
    with open(MASTER, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    print(f'\nSaved {MASTER}')


if __name__ == '__main__':
    main()
