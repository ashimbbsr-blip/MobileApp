"""
apply_bn_corrections_v8_1.py
Produces food_master_v8_1.json from food_master_v8_0.json by:
  1. Reading 4 xlsx correction files → en→bn lookup
  2. Applying hardcoded (id / en) corrections
  3. Applying xlsx corrections to matching items
  4. Fixing compound-letter / non-Bengali-script glitches in all bn fields
  5. Removing all bacon items
  6. Saving output and printing a summary
"""

import json, re, sys, io, unicodedata
import openpyxl

# ── UTF-8 stdout so Bengali prints cleanly ──────────────────────────────────
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ASSETS = r"C:\Users\ideapad\IdeaProjects\MobileApp\assets\data"
INPUT  = ASSETS + r"\food_master_v8_0.json"
OUTPUT = ASSETS + r"\food_master_v8_1.json"

XLSX_FILES = [
    ASSETS + r"\Bengalicorrect1.xlsx",
    ASSETS + r"\Bengalicorrect2.xlsx",
    ASSETS + r"\Bengalicorrect3.xlsx",
    ASSETS + r"\bengalicorrect4.xlsx",
]

# ── Hardcoded corrections (id primary key, en fallback) ─────────────────────
HARDCODED = [
    # beverages
    {"id": 1,  "en": "Coco pine cooler",                              "bn": "নারকেল আনারসের শরবত"},
    {"id": 3,  "en": "Coffee pear alaska",                            "bn": "কফি পেয়ার আলাস্কা"},
    {"id": 15, "en": "Woodapple juice",                               "bn": "কদবেলের রস"},
    # breakfast
    {"id": 19, "en": "Bacon and mushroom pancake",                    "bn": "বেকন ও মাশরুম প্যানকেক"},
    {"id": 22, "en": "Buckwheat pancake",                             "bn": "কুড়টুর প্যানকেক"},
    {"id": 24, "en": "Cereal pulse mix with amylase rice flour",      "bn": "অ্যামাইলেজ চালের গুঁড়ো মিশ্রিত খাদ্যশস্য ও ডাল মিক্স"},
    {"id": 32, "en": "Jowar dosa",                                    "bn": "জোয়ার দোসা"},
    {"id": 36, "en": "Moong bean dosa",                               "bn": "মুগ ডালের দোসা"},
    {"id": 40, "en": "Onion tomato uttapam",                          "bn": "পেঁয়াজ-টমেটো উত্তাপম"},
    {"id": 42, "en": "Plain dosa",                                    "bn": "প্লেন দোসা"},
    {"id": 52, "en": "Vegetable poha",                                "bn": "সবজি চিঁড়ে"},
    # dairy
    {"id": 64,  "en": "Cheese pudding",                               "bn": "চিজ পুডিং"},
    {"id": 72,  "en": "Chocolate cream shells",                       "bn": "চকলেট ক্রিম শেলস"},   # pure Bengali, fixes mixed-script bug
    {"id": 81,  "en": "Cream of tomato soup",                        "bn": "টমেটো ক্রিম স্যুপ"},
    {"id": 83,  "en": "Cucumber and yogurt salad",                   "bn": "শশা ও দইয়ের সালাদ"},
    {"id": 91,  "en": "Honey banana cream",                          "bn": "মধু ও কলার ক্রিম"},
    {"id": 93,  "en": "Kadhai Paneer",                               "bn": "কড়াই পনির"},
    {"id": 97,  "en": "Lemon curd filling",                          "bn": "লেমন কার্ড ফিলিং"},
    {"id": 100, "en": "Mashed banana with milk",                     "bn": "দুধ দিয়ে চটকানো কলা"},
    {"id": 106, "en": "Orange cream tart",                           "bn": "অরেঞ্জ ক্রিম টার্ট"},
    {"id": 107, "en": "Paneer and pea samosa",                       "bn": "পনির ও মটরশুঁটির সিঙাড়া"},
    {"id": 117, "en": "Paneer pea sandwich",                         "bn": "পনির ও মটরশুঁটির স্যান্ডউইচ"},
    {"id": 118, "en": "Paneer shaslik/tikka",                        "bn": "পনির শাশলিক / টিক্কা"},
    {"id": 120, "en": "Paneer stuffed cheela/chilla",                "bn": "পনির পুর ভরা চিলা"},
    {"id": 125, "en": "Peanut butter cucumber sandwich",             "bn": "পিনাট বাটার ও শশার স্যান্ডউইচ"},
    {"id": 132, "en": "Semolina milk drink",                         "bn": "সুজি ও দুধের পানীয়"},
    {"id": 135, "en": "Strawberry and vanilla cake with butter icing","bn": "স্ট্রবেরি ও ভ্যানিলা কেক (বাটার আইসিং সহ)"},
    {"id": 139, "en": "Veg paneer stew",                             "bn": "সবজি পনির স্টু"},
    # legumes_and_dal
    {"id": 140, "en": "Atta dal burfi",                              "bn": "আটা ডাল বারফি"},
    {"id": 147, "en": "Horsegram dal",                               "bn": "কুরথির ডাল"},
    {"id": 150, "en": "Maa chaane ki dal",                           "bn": "মা ছোলার ডাল"},
    {"id": 151, "en": "Masala urad dal vada",                        "bn": "মশলা মাষকলাই ডালের বড়া"},
    {"id": 157, "en": "Plain urad dal vada",                         "bn": "মাষকলাই ডালের বড়া"},
    {"id": 158, "en": "Rasam powder",                                "bn": "রসম মশলা"},
    {"id": 161, "en": "Rice moong dal cheela",                       "bn": "চাল ও মুগ ডালের চিলা"},
]

# ── Bengali Unicode range helpers ────────────────────────────────────────────
BENGALI_BLOCK = range(0x0980, 0x09FF + 1)

def is_allowed_char(ch):
    """Allow Bengali block, ASCII printable, space, common punctuation."""
    cp = ord(ch)
    if cp in BENGALI_BLOCK:
        return True
    if 0x20 <= cp <= 0x7E:          # ASCII printable (includes / ( ) . , etc.)
        return True
    if ch in ('‌', '‍'):  # ZWNJ, ZWJ (used in Bengali conjuncts)
        return True
    if ch in ('।', '॥', '়'):  # Bengali danda, double danda, nukta
        return True
    return False

def clean_bn(text):
    """Remove non-Bengali / non-ASCII characters from a Bengali string."""
    if not text:
        return text
    return "".join(ch for ch in text if is_allowed_char(ch)).strip()

def fix_doubled_letters(text):
    """
    Fix known machine-translation doubled-letter glitches:
      লল → ল   (when standing as a doubled error)
      তত → ত
    We only collapse runs of exactly 2 identical Bengali letters that are
    not part of a valid conjunct (i.e., not separated by hasanta U+09CD).
    Simple heuristic: replace লল with ল and তত with ত globally.
    """
    if not text:
        return text
    # Only collapse if NOT preceded or followed by hasanta (conjunct marker)
    # Use negative lookbehind/lookahead for hasanta U+09CD
    text = re.sub(r'(?<!্)লল(?!্)', 'ল', text)
    text = re.sub(r'(?<!্)তত(?!্)', 'ত', text)
    return text

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Load JSON
# ══════════════════════════════════════════════════════════════════════════════
print("=" * 60)
print("STEP 1 — Loading JSON dataset")
print("=" * 60)

with open(INPUT, "r", encoding="utf-8") as f:
    data = json.load(f)

if isinstance(data, dict):
    # Find the list key
    foods_key = next(k for k, v in data.items() if isinstance(v, list))
    foods = data[foods_key]
    is_wrapped = True
    print(f"  Top-level dict, foods at key '{foods_key}'")
else:
    foods = data
    is_wrapped = False
    print(f"  Top-level array")

total_before = len(foods)
print(f"  Total items: {total_before}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Read xlsx correction files
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("STEP 2 — Reading Excel correction files")
print("=" * 60)

# xlsx columns: ID | English Name (en) | Current Bengali (bn) | Issue | Corrected Bengali (bn)
# For file 3 the ID column header is None but data is still there in col 0
# We take: col[1] = EN name, col[4] = corrected BN

xlsx_lookup = {}   # en_lower → corrected_bn

for fpath in XLSX_FILES:
    fname = fpath.split("\\")[-1]
    wb = openpyxl.load_workbook(fpath)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    header = rows[0]
    print(f"\n  File: {fname}")
    print(f"    Header: {header}")
    added = 0
    for row in rows[1:]:
        if len(row) < 5:
            continue
        en_name = row[1]
        corrected_bn = row[4]
        if not en_name or not corrected_bn:
            continue
        en_name = str(en_name).strip()
        corrected_bn = str(corrected_bn).strip()
        if en_name and corrected_bn:
            # Some corrections have slash-alternatives like "X / Y" — use left side
            corrected_bn_clean = corrected_bn.split("/")[0].strip()
            xlsx_lookup[en_name.lower()] = corrected_bn_clean
            print(f"    + [{row[0]}] {en_name}  →  {corrected_bn_clean}")
            added += 1
    print(f"    {added} corrections loaded from {fname}")

print(f"\n  Total xlsx lookup entries: {len(xlsx_lookup)}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Build id→correction and en→correction from hardcoded list
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("STEP 3 — Applying hardcoded corrections")
print("=" * 60)

hardcoded_by_id  = {h["id"]: h for h in HARDCODED}
hardcoded_by_en  = {h["en"].lower(): h for h in HARDCODED}

hardcoded_applied = 0
hardcoded_log = []

for item in foods:
    item_id = item.get("id")
    item_en = item.get("en", "")

    match = None
    if item_id is not None and item_id in hardcoded_by_id:
        match = hardcoded_by_id[item_id]
    elif item_en.lower() in hardcoded_by_en:
        match = hardcoded_by_en[item_en.lower()]

    if match:
        old_bn = item.get("bn", "")
        new_bn = match["bn"]
        if old_bn != new_bn:
            item["bn"] = new_bn
            hardcoded_applied += 1
            hardcoded_log.append(
                f"  [id={item_id}] {item_en}\n"
                f"    OLD: {old_bn}\n"
                f"    NEW: {new_bn}"
            )

for line in hardcoded_log:
    print(line)
print(f"\n  Hardcoded corrections applied: {hardcoded_applied}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 4 — Apply xlsx corrections
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("STEP 4 — Applying xlsx corrections (by EN name)")
print("=" * 60)

xlsx_applied = 0
xlsx_log = []

for item in foods:
    en_lower = item.get("en", "").strip().lower()
    if en_lower in xlsx_lookup:
        new_bn = xlsx_lookup[en_lower]
        old_bn = item.get("bn", "")
        if old_bn != new_bn:
            item["bn"] = new_bn
            xlsx_applied += 1
            xlsx_log.append(
                f"  [id={item.get('id')}] {item.get('en')}\n"
                f"    OLD: {old_bn}\n"
                f"    NEW: {new_bn}"
            )

for line in xlsx_log:
    print(line)
print(f"\n  xlsx corrections applied: {xlsx_applied}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 5 — Fix Bengali glitches in ALL bn fields
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("STEP 5 — Fixing Bengali compound-letter glitches")
print("=" * 60)

glyph_fixed = 0
glyph_log   = []

for item in foods:
    old_bn = item.get("bn", "")
    if not old_bn:
        continue

    # Pass 1: remove non-Bengali / non-ASCII characters (catches katakana etc.)
    step1 = clean_bn(old_bn)

    # Pass 2: fix doubled-letter glitches
    step2 = fix_doubled_letters(step1)

    new_bn = step2.strip()

    if new_bn != old_bn:
        item["bn"] = new_bn
        glyph_fixed += 1
        glyph_log.append(
            f"  [id={item.get('id')}] {item.get('en')}\n"
            f"    OLD: {old_bn!r}\n"
            f"    NEW: {new_bn!r}"
        )

for line in glyph_log:
    print(line)
print(f"\n  Glyph / compound-letter fixes applied: {glyph_fixed}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 6 — Remove bacon items
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("STEP 6 — Removing bacon items")
print("=" * 60)

bacon_removed = []
cleaned_foods = []

for item in foods:
    en = item.get("en", "")
    if re.search(r"\bbacon\b", en, re.IGNORECASE):
        bacon_removed.append(item)
    else:
        cleaned_foods.append(item)

for item in bacon_removed:
    print(f"  REMOVED [id={item.get('id')}]: {item.get('en')}  |  bn={item.get('bn')}")

print(f"\n  Bacon items removed: {len(bacon_removed)}")

# ══════════════════════════════════════════════════════════════════════════════
# STEP 7 — Save output
# ══════════════════════════════════════════════════════════════════════════════
print()
print("=" * 60)
print("STEP 7 — Saving output")
print("=" * 60)

if is_wrapped:
    data[foods_key] = cleaned_foods
    out_obj = data
else:
    out_obj = cleaned_foods

with open(OUTPUT, "w", encoding="utf-8") as f:
    json.dump(out_obj, f, ensure_ascii=False, indent=2)

total_after = len(cleaned_foods)

print(f"  Saved → {OUTPUT}")
print()
print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"  Total items BEFORE      : {total_before}")
print(f"  Bacon items removed     : {len(bacon_removed)}")
print(f"  Hardcoded bn fixes      : {hardcoded_applied}")
print(f"  xlsx bn fixes           : {xlsx_applied}")
print(f"  Glyph / compound fixes  : {glyph_fixed}")
print(f"  Total bn updates        : {hardcoded_applied + xlsx_applied + glyph_fixed}")
print(f"  Total items AFTER       : {total_after}")
print("=" * 60)
