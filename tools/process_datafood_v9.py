"""
process_datafood_v9.py
======================
Processes assets/data/datafood.txt and merges foods into food_master_v8_2.json
producing food_master_v9_0.json with exactly ~4000 items (WB + Odisha mandatory,
others optional up to 4000 cap). Rebuilds search_index_v2.json.

Rules:
  • Priority 1 (MANDATORY): West Bengal district foods (IDs 27001–27330 + 25101-25111)
  • Priority 2 (MANDATORY): Odisha/Puri foods (24001-24045, 26001-26060, 27600-27669)
  • Priority 3 (OPTIONAL):  North Indian restro breads/rice (25001-25016, 25101-25111)
  • SKIP: Sikkim/NE (27430-27445), Gujarat (27480-27500), Arunachal, etc.
  • Odia script (Unicode 0B00-0B7F) in bn field → extract Bengali after "/" or transliterate
  • No duplicate EN names against existing dataset (case-insensitive)
  • Target: exactly 4000 items (WB+Odisha may push it slightly over if needed)
"""
import json, re, sys, unicodedata
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

BASE   = Path('assets/data')
INPUT  = BASE / 'food_master_v8_2.json'
TXTIN  = BASE / 'datafood.txt'
OUTPUT = BASE / 'food_master_v9_0.json'
INDEX  = BASE / 'search_index_v2.json'

TARGET = 4000

# ── Odia → Bengali character map ──────────────────────────────────────────────
# Odia Unicode block: 0B00–0B7F
# Bengali Unicode block: 0980–09FF
# Many characters share the same relative offset within each block.
# Direct mapping table for core characters:
ODIA_TO_BN = {
    # Vowels
    'ଅ': 'অ', 'ଆ': 'আ', 'ଇ': 'ই', 'ଈ': 'ঈ', 'ଉ': 'উ', 'ଊ': 'ঊ',
    'ଋ': 'ঋ', 'ଌ': 'ঌ', 'ଏ': 'এ', 'ଐ': 'ঐ', 'ଓ': 'ও', 'ଔ': 'ঔ',
    # Consonants
    'କ': 'ক', 'ଖ': 'খ', 'ଗ': 'গ', 'ଘ': 'ঘ', 'ଙ': 'ঙ',
    'ଚ': 'চ', 'ଛ': 'ছ', 'ଜ': 'জ', 'ଝ': 'ঝ', 'ଞ': 'ঞ',
    'ଟ': 'ট', 'ଠ': 'ঠ', 'ଡ': 'ড', 'ଢ': 'ঢ', 'ଣ': 'ণ',
    'ତ': 'ত', 'ଥ': 'থ', 'ଦ': 'দ', 'ଧ': 'ধ', 'ନ': 'ন',
    'ପ': 'প', 'ଫ': 'ফ', 'ବ': 'ব', 'ଭ': 'ভ', 'ମ': 'ম',
    'ଯ': 'য', 'ର': 'র', 'ଲ': 'ল', 'ଳ': 'ল',  # ଳ (la with nukta) → ল
    'ଶ': 'শ', 'ଷ': 'ষ', 'ସ': 'স', 'ହ': 'হ',
    # Special consonants (with nukta/dot below in Odia)
    'ଡ଼': 'ড়', 'ଢ଼': 'ঢ়', 'ଯ଼': 'য়',
    # Vowel signs (matras)
    'ା': 'া', 'ି': 'ি', 'ୀ': 'ী', 'ୁ': 'ু', 'ୂ': 'ূ',
    'ୃ': 'ৃ', 'େ': 'ে', 'ୈ': 'ৈ', 'ୋ': 'ো', 'ୌ': 'ৌ',
    '୍': '্',  # virama/hasanta
    # Anusvara / visarga / candrabindu
    'ଁ': 'ঁ', 'ଂ': 'ং', 'ଃ': 'ঃ',
    # Nukta
    '଼': '়',
    # Digits (keep same numerals)
    '୦': '০', '୧': '১', '୨': '২', '୩': '৩', '୪': '৪',
    '୫': '৫', '୬': '৬', '୭': '৭', '୮': '৮', '୯': '৯',
}

def is_odia(text: str) -> bool:
    """Returns True if text contains any Odia Unicode characters."""
    return any(0x0B00 <= ord(c) <= 0x0B7F for c in text)

def has_bengali(text: str) -> bool:
    """Returns True if text contains any Bengali Unicode characters."""
    return any(0x0980 <= ord(c) <= 0x09FF for c in text)

def odia_to_bengali(text: str) -> str:
    """Transliterate Odia script to Bengali script."""
    result = []
    i = 0
    while i < len(text):
        # Try 2-char sequence first (for nukta combinations like ଡ଼)
        two = text[i:i+2]
        if two in ODIA_TO_BN:
            result.append(ODIA_TO_BN[two])
            i += 2
        elif text[i] in ODIA_TO_BN:
            result.append(ODIA_TO_BN[text[i]])
            i += 1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)

def clean_bn(raw_bn: str) -> str:
    """
    Given a raw bn field value, return clean Bengali text:
      - If has '/' separator: take the part after '/' (Bengali part)
      - If pure Odia: transliterate to Bengali
      - If already Bengali: return as-is (strip trailing Odia if mixed without /)
    """
    if not raw_bn:
        return raw_bn
    # Pattern: "Odia text / Bengali text"
    if '/' in raw_bn:
        parts = raw_bn.split('/')
        # Take the last non-empty part (usually Bengali)
        for p in reversed(parts):
            p = p.strip()
            if p and has_bengali(p):
                return p
            if p and not is_odia(p):
                return p
        # fallback: take last part
        return parts[-1].strip()
    # Pure Odia → transliterate
    if is_odia(raw_bn) and not has_bengali(raw_bn):
        return odia_to_bengali(raw_bn)
    # Already Bengali or mixed without /
    if has_bengali(raw_bn):
        # strip any Odia characters
        cleaned = ''.join(c if not (0x0B00 <= ord(c) <= 0x0B7F) else '' for c in raw_bn).strip()
        return cleaned if cleaned else raw_bn
    return raw_bn

def normalize_cat(cat: str) -> str:
    """Map datafood.txt categories to standard UI categories."""
    mapping = {
        'seafood': 'fish', 'veg_curry': 'vegetable', 'paneer': 'dairy',
        'dal': 'legume', 'street_food': 'restaurant_food', 'dessert': 'sweet',
        'millet': 'grain', 'tribal_food': 'restaurant_food', 'condiment': 'snack',
        'drink': 'beverage', 'restaurant': 'restaurant_food', 'curry': 'vegetable',
        'veg': 'vegetable',
    }
    return mapping.get(cat, cat)

# ── Parse datafood.txt ────────────────────────────────────────────────────────
raw = TXTIN.read_text(encoding='utf-8')

# The file has multiple JSON arrays, sometimes glued together without proper
# whitespace. We use a robust approach: find all array starts and try to parse.
# Strategy: fix malformed JSON by inserting missing array close/open brackets.

# First, normalize: replace "][" and "]\n[" and "]\n\n[" with array separators
# Then split on array boundaries
fixed = re.sub(r'\]\s*\[', ']\n[', raw)

# Collect all individual JSON arrays
new_items_all = []
seen_parse_ids = set()

# Split into candidate array chunks
chunks = re.split(r'\n(?=\[)', fixed)
for chunk in chunks:
    chunk = chunk.strip()
    if not chunk:
        continue
    # Find the start of array
    start = chunk.find('[')
    if start == -1:
        continue
    # Find the matching end of array (handle nested structures)
    # Use a simple bracket counter
    depth = 0
    end = -1
    for i, c in enumerate(chunk[start:], start):
        if c == '[':
            depth += 1
        elif c == ']':
            depth -= 1
            if depth == 0:
                end = i
                break
    if end == -1:
        # Malformed - try to find the last complete object
        # Add closing bracket and try
        chunk_fixed = chunk[:] + ']'
        try:
            arr = json.loads(chunk_fixed[start:])
            if isinstance(arr, list):
                for item in arr:
                    if isinstance(item, dict) and 'id' in item:
                        iid = item['id']
                        if iid not in seen_parse_ids:
                            seen_parse_ids.add(iid)
                            new_items_all.append(item)
        except Exception:
            pass
        continue
    try:
        arr = json.loads(chunk[start:end+1])
        if isinstance(arr, list):
            for item in arr:
                if isinstance(item, dict) and 'id' in item:
                    iid = item['id']
                    if iid not in seen_parse_ids:
                        seen_parse_ids.add(iid)
                        new_items_all.append(item)
    except json.JSONDecodeError as e:
        # Try to salvage valid objects from malformed array
        # Find all complete objects
        obj_pattern = re.compile(r'\{[^{}]*\}', re.DOTALL)
        for m in obj_pattern.finditer(chunk[start:end+1]):
            try:
                obj = json.loads(m.group())
                if isinstance(obj, dict) and 'id' in obj:
                    iid = obj['id']
                    if iid not in seen_parse_ids:
                        seen_parse_ids.add(iid)
                        new_items_all.append(obj)
            except Exception:
                pass

print(f'Parsed {len(new_items_all)} raw items from datafood.txt')

# ── Classify items by priority ────────────────────────────────────────────────
# WB = West Bengal district foods (mainly 27001-27330) + Kolkata biryani (25101-25111)
# Odisha = Mahaprasad/Puri (24001-24045) + Odisha regional (26001-26060) + Ganjam (27600-27669)
# NorthIndia = 25001-25099 (North Indian restaurant breads)
# Skip = Sikkim (27430-27445), Gujarat (27480-27500)
def classify(item_id: int) -> str:
    if 27001 <= item_id <= 27330:
        return 'WB'
    if 25101 <= item_id <= 25120:
        return 'WB'   # Kolkata biryani and rice dishes
    if 24001 <= item_id <= 24045:
        return 'Odisha'
    if 26001 <= item_id <= 26060:
        return 'Odisha'
    if 27600 <= item_id <= 27700:
        return 'Odisha'
    if 27331 <= item_id <= 27429:
        return 'Other'  # Could be NE or other states
    if 27430 <= item_id <= 27479:
        return 'Skip'   # Sikkim/NE
    if 27480 <= item_id <= 27530:
        return 'Skip'   # Gujarat
    if 25001 <= item_id <= 25100:
        return 'NorthIndia'
    return 'Other'

priority_order = {'WB': 1, 'Odisha': 2, 'NorthIndia': 3, 'Other': 4, 'Skip': 99}
new_items_all.sort(key=lambda x: (priority_order.get(classify(x.get('id', 0)), 99), x.get('id', 0)))

# ── Load existing dataset ─────────────────────────────────────────────────────
existing = json.loads(INPUT.read_text(encoding='utf-8'))
print(f'Existing dataset: {len(existing)} items')

# Build dedup set: EN names (lowercase, stripped)
existing_en_names = {item['en'].lower().strip() for item in existing if 'en' in item}
existing_ids = {item['id'] for item in existing}

# Find max existing ID in new-items namespace to avoid collisions
max_existing_local_id = max(
    (item['id'] for item in existing if isinstance(item.get('id'), int)),
    default=30000
)
next_id = max(30000, max_existing_local_id + 1)

# ── Convert and deduplicate new items ────────────────────────────────────────
to_add_mandatory = []  # WB + Odisha
to_add_optional  = []  # NorthIndia + Other

skipped_dup = 0
skipped_cat = 0

for item in new_items_all:
    item_id = item.get('id', 0)
    prio    = classify(item_id)

    if prio == 'Skip':
        skipped_cat += 1
        continue

    en = (item.get('en') or '').strip()
    bn = (item.get('bn') or '').strip()

    # Deduplicate by EN name
    if en.lower() in existing_en_names:
        skipped_dup += 1
        continue

    # Clean Bengali text
    bn_clean = clean_bn(bn) if bn else en

    # Build output item matching food_master_v8_2.json schema
    out = {
        'id':   item_id,
        'en':   en,
        'bn':   bn_clean,
        'cat':  normalize_cat(item.get('cat', 'other')),
        's':    item.get('s', '100g'),
        'k':    item.get('k', 0),
        'p':    item.get('p', 0),
        'c':    item.get('c', 0),
        'f':    item.get('f', 0),
        'fi':   item.get('fi', 0),
        'ca':   item.get('ca', 0) if item.get('ca') else None,
        'fe':   item.get('fe', 0) if item.get('fe') else None,
        'src':  'local',
        'search_priority': 55 if prio in ('WB', 'Odisha') else 45,
        'quality_score':   70,
        'popularity_score': 50 if prio in ('WB', 'Odisha') else 40,
    }
    # Remove None values
    out = {k: v for k, v in out.items() if v is not None}

    # Mark as added to existing_en_names so we don't add duplicates from same file
    existing_en_names.add(en.lower())

    if prio in ('WB', 'Odisha'):
        to_add_mandatory.append(out)
    else:
        to_add_optional.append(out)

print(f'Mandatory (WB+Odisha): {len(to_add_mandatory)}')
print(f'Optional (NI+Other):   {len(to_add_optional)}')
print(f'Skipped (dups):        {skipped_dup}')
print(f'Skipped (Sikkim/GJ):   {skipped_cat}')

# ── Merge to reach TARGET ─────────────────────────────────────────────────────
# Always add all mandatory (WB + Odisha)
merged = existing + to_add_mandatory
print(f'After mandatory add:   {len(merged)} items')

slots_left = TARGET - len(merged)
if slots_left > 0:
    # Fill with optional items up to target
    merged += to_add_optional[:slots_left]
    print(f'Added {min(slots_left, len(to_add_optional))} optional items')

print(f'Final dataset size:    {len(merged)} items')

# ── Write output dataset ──────────────────────────────────────────────────────
OUTPUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Written {OUTPUT}')

# ── Rebuild search index ──────────────────────────────────────────────────────
print('\nRebuilding search index...')

# ── Category normalizer (mirror of Dart _normalizeCategory) ──────────────────
def dart_cat(cat):
    m = {
        'veg': 'vegetable', 'leafy_vegetable': 'shaak', 'drink': 'beverage',
        'fitness': 'snack', 'brand': 'snack', 'condiment': 'snack',
        'diet': 'beverage', 'meal': 'restaurant_food', 'dessert': 'sweet',
        'mutton': 'meat', 'chicken': 'meat', 'duck': 'meat', 'beef': 'meat',
        'seafood': 'fish', 'paneer': 'dairy', 'curd': 'dairy', 'cheese': 'dairy',
        'butter': 'dairy', 'ghee': 'dairy', 'milk_powder': 'dairy',
        'chocolate': 'sweet', 'dark_chocolate': 'sweet', 'candy': 'sweet',
        'biscuit': 'bakery', 'cookie': 'bakery', 'rusk': 'bakery',
        'energy_drink': 'beverage', 'sports_drink': 'beverage', 'water': 'beverage',
        'dal': 'legume', 'curry': 'vegetable', 'veg_curry': 'vegetable',
        'street_food': 'restaurant_food', 'millet': 'grain',
        'tribal_food': 'restaurant_food', 'restaurant': 'restaurant_food',
    }
    return m.get(cat, cat)

# ── Family rules ──────────────────────────────────────────────────────────────
FAMILY_RULES = [
    ('biryani',    ['biryani','biriyani','biriani']),
    ('khichdi',    ['khichdi','khichuri']),
    ('pulao',      ['pulao','pilaf','pulav']),
    ('fried rice', ['fried rice']),
    ('rice',       ['rice','bhaat']),
    ('paratha',    ['paratha','parantha','porota','porotta']),
    ('puri',       ['puri ','poori','luchi']),
    ('naan',       ['naan']),
    ('dosa',       ['dosa ','dosai','uttapam']),
    ('idli',       ['idli','idly']),
    ('poha',       ['poha ']),
    ('roti',       ['roti','chapati','chapatti','phulka']),
    ('bread',      ['bread','toast']),
    ('samosa',     ['samosa']),
    ('pakora',     ['pakora','pakoda','bajji']),
    ('momo',       ['momo']),
    ('chaat',      ['chaat','bhelpuri','pani puri','golgappa']),
    ('dal',        ['dal ','daal',' lentil']),
    ('rajma',      ['rajma','kidney bean']),
    ('chana',      ['chana ','chickpea','chole']),
    ('moong',      ['moong','mung']),
    ('chicken',    ['chicken','murgi']),
    ('mutton',     ['mutton','lamb ','goat ','mangsho','keema']),
    ('hilsa',      ['hilsa','ilish']),
    ('rohu',       ['rohu','rui ']),
    ('prawn',      ['prawn','shrimp','chingri','chingudi']),
    ('crab',       ['crab','kankada','kankra']),
    ('fish',       [' fish ',' mach ']),
    ('omelette',   ['omelette','omelet']),
    ('egg',        [' egg ']),
    ('paneer',     ['paneer']),
    ('cheese',     ['cheese']),
    ('milk',       ['milk ','dudh']),
    ('yogurt',     ['yogurt','curd ','dahi ','raita']),
    ('ghee',       ['ghee']),
    ('butter',     ['butter']),
    ('pizza',      ['pizza']),
    ('burger',     ['burger']),
    ('pasta',      ['pasta','spaghetti','macaroni']),
    ('noodle',     ['noodle','chowmein','chow mein','hakka']),
    ('kheer',      ['kheer','payesh','payasam','khir']),
    ('halwa',      ['halwa','halva']),
    ('ladoo',      ['ladoo','laddoo','laddu']),
    ('rasgulla',   ['rasgulla','roshogolla','rasagola']),
    ('gulab jamun',['gulab jamun']),
    ('barfi',      ['barfi','burfi']),
    ('jalebi',     ['jalebi','jilipi']),
    ('sandesh',    ['sandesh','sondesh']),
    ('mishti doi', ['mishti doi','misti doi']),
    ('rasmalai',   ['rasmalai','rosomalai']),
    ('pitha',      ['pitha ','pithe']),
    ('ice cream',  ['ice cream','icecream','kulfi']),
    ('cake',       ['cake ','muffin','brownie']),
    ('cookie',     ['cookie','biscuit']),
    ('chocolate',  ['chocolate']),
    ('tea',        [' tea ','chai ']),
    ('coffee',     ['coffee','cappuccino','latte ','mocha','espresso']),
    ('juice',      ['juice','sharbat']),
    ('lassi',      ['lassi']),
    ('shake',      ['shake ','milkshake','smoothie']),
    ('water',      ['water']),
    ('fries',      ['french fries','fries ']),
    ('potato',     ['potato','aloo ','alur ']),
    ('tomato',     ['tomato','tamatar']),
    ('spinach',    ['spinach','palak ']),
    ('banana',     ['banana','kela ','kola ']),
    ('mango',      ['mango','aam ']),
    ('apple',      ['apple']),
    ('orange',     ['orange']),
    ('bhindi',     ['bhindi','okra']),
    ('brinjal',    ['brinjal','eggplant','baingan','begun ']),
    ('capsicum',   ['capsicum','bell pepper']),
    ('cauliflower',['cauliflower','fulkopi','phulkopi']),
    ('cabbage',    ['cabbage','bandhakopi','badhakopi']),
    ('pumpkin',    ['pumpkin','kakharu','kumro ']),
    ('bitter gourd',['bitter gourd','karela','uchhe']),
    ('pointed gourd',['potol','pointed gourd','parwal']),
    ('hilsa',      ['ilish ']),
    ('katla',      ['katla','catla']),
    ('besara',     ['besara']),
    ('kalia',      ['kalia ']),
]

def get_family(en_lower):
    padded = ' ' + en_lower + ' '
    for family, keywords in FAMILY_RULES:
        if any(kw in padded for kw in keywords):
            return family
    return None

# ── Alias rules ───────────────────────────────────────────────────────────────
ALIAS_RULES = [
    # Bengali food specific
    ('roshogolla',   ['rasgulla','rosogolla','roshogolla']),
    ('sandesh',      ['sondesh','sandesh']),
    ('mishti doi',   ['misti doi','mishti doi','sweet curd']),
    ('rasmalai',     ['rosomalai','rasmalai']),
    ('jilipi',       ['jalebi']),
    ('luchi',        ['puri','luchi']),
    ('ilish',        ['hilsa','ilish']),
    ('chingri',      ['prawn','shrimp','chingri','chingudi']),
    ('rui',          ['rohu','rui']),
    ('katla',        ['catla','katla']),
    ('mocha',        ['banana blossom','mocha']),
    ('echor',        ['raw jackfruit','echor']),
    ('begun',        ['brinjal','eggplant','baingan','begun']),
    ('potol',        ['pointed gourd','parwal','potol']),
    ('kumro',        ['pumpkin','kumro']),
    ('uchhe',        ['bitter gourd','karela','uchhe']),
    ('lau',          ['bottle gourd','lauki','lau']),
    ('jhinge',       ['ridge gourd','jhinge']),
    ('patol',        ['potol','patol']),
    ('sorshe',       ['mustard','sorshe','mustard sauce']),
    ('paturi',       ['fish in banana leaf','paturi']),
    ('bhapa',        ['steamed','bhapa']),
    ('jhal',         ['spicy curry','jhal']),
    ('dhokar dalna', ['lentil cake curry','dhokar dalna']),
    ('alur dom',     ['dum aloo','alur dom','aloo dum']),
    ('korma',        ['qorma','korma']),
    ('kofta',        ['kofte','kofta']),
    ('malai curry',  ['malai curry','malaikari']),
    ('biryani',      ['biriyani','biriani','biryani']),
    ('khichuri',     ['khichdi','khichuri']),
    ('panta bhat',   ['panta bhat','fermented rice','pakhala']),
    ('chhena',       ['chenna','chhana','paneer','cottage cheese']),
    ('besara',       ['mustard paste curry','besara']),
    ('santula',      ['boiled mixed vegetable','santula']),
    ('dalma',        ['dalma','dal with vegetables']),
    ('mahaprasad',   ['temple food','mahaprasad','jagannath']),
    ('momo',         ['dumpling','momo','modak']),
    ('poha',         ['chira','poha','beaten rice']),
    ('muri',         ['puffed rice','muri','murmura']),
    ('sattu',        ['roasted chickpea flour','sattu']),
    ('maida',        ['refined flour','maida']),
    ('atta',         ['whole wheat flour','atta']),
    # Sikkim exclusion - none needed since we skip them
]

# Generate keyword list per item (for full-text search)
def get_keywords(item):
    en = item.get('en', '').lower()
    bn = item.get('bn', '')
    cat = dart_cat(item.get('cat', ''))
    words = set()
    # Split English name into words
    for w in re.split(r'[\s/\-\(\)]+', en):
        w = w.strip()
        if len(w) >= 3:
            words.add(w)
    # Add category
    if cat:
        words.add(cat)
    # Add family
    fam = get_family(en)
    if fam:
        words.add(fam)
    return list(words)

# ── Build search index ────────────────────────────────────────────────────────
en_prefix   = {}  # prefix → set of IDs
bn_prefix   = {}  # prefix → set of IDs
alias_lookup = {}  # alias → set of IDs
family_index = {}  # family → set of IDs

# Top foods by search_priority
all_ids_with_priority = []

def add_prefix(index, prefix, fid):
    if prefix not in index:
        index[prefix] = set()
    index[prefix].add(fid)

for item in merged:
    fid = item.get('id')
    if fid is None:
        continue
    en = (item.get('en') or '').lower().strip()
    bn = (item.get('bn') or '').strip()
    cat = dart_cat(item.get('cat', ''))
    kws = item.get('kw', []) or []
    sp  = item.get('search_priority', 50)

    all_ids_with_priority.append((sp, fid))

    # EN prefixes: 2-char and 3-char for each word
    for word in re.split(r'[\s/\-\(\)&]+', en):
        word = word.strip()
        if not word:
            continue
        if len(word) >= 2:
            add_prefix(en_prefix, word[:2], fid)
        if len(word) >= 3:
            add_prefix(en_prefix, word[:3], fid)
        if len(word) >= 4:
            add_prefix(en_prefix, word[:4], fid)

    # BN prefixes: 2-char Bengali prefix
    if bn and has_bengali(bn):
        # Split on space
        for word in bn.split():
            word = word.strip()
            if len(word) >= 2:
                prefix_2 = word[:2]
                add_prefix(bn_prefix, prefix_2, fid)
            if len(word) >= 3:
                prefix_3 = word[:3]
                add_prefix(bn_prefix, prefix_3, fid)

    # Alias lookup
    en_lower = en
    for alias_key, alias_list in ALIAS_RULES:
        if any(a in en_lower for a in alias_list):
            for a in alias_list:
                if a not in alias_lookup:
                    alias_lookup[a] = set()
                alias_lookup[a].add(fid)
            break

    # Family index
    fam = get_family(en_lower)
    if fam:
        if fam not in family_index:
            family_index[fam] = set()
        family_index[fam].add(fid)

    # Also index keywords
    for kw in kws:
        kw_l = kw.lower().strip()
        if len(kw_l) >= 2:
            add_prefix(en_prefix, kw_l[:2], fid)
        if len(kw_l) >= 3:
            add_prefix(en_prefix, kw_l[:3], fid)

# Top 200 foods by search priority
all_ids_with_priority.sort(key=lambda x: -x[0])
top_foods = [fid for _, fid in all_ids_with_priority[:200]]

# Convert sets to sorted lists
def sets_to_lists(d):
    return {k: sorted(v) for k, v in d.items()}

index_obj = {
    'en_prefix':    sets_to_lists(en_prefix),
    'bn_prefix':    sets_to_lists(bn_prefix),
    'alias_lookup': sets_to_lists(alias_lookup),
    'family_index': sets_to_lists(family_index),
    'top_foods':    top_foods,
}

INDEX.write_text(json.dumps(index_obj, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
print(f'Written {INDEX}')
print(f'EN prefix tokens:    {len(en_prefix)}')
print(f'BN prefix tokens:    {len(bn_prefix)}')
print(f'Alias terms:         {len(alias_lookup)}')
print(f'Family clusters:     {len(family_index)}')
print(f'Top foods:           {len(top_foods)}')
print('\nDone!')

# ── Summary ───────────────────────────────────────────────────────────────────
wb_count     = sum(1 for i in to_add_mandatory if classify(i['id']) == 'WB')
odisha_count = sum(1 for i in to_add_mandatory if classify(i['id']) == 'Odisha')
ni_count     = sum(1 for i in to_add_optional[:max(0, TARGET - len(existing) - len(to_add_mandatory))] if classify(i['id']) == 'NorthIndia')
print(f'\nAdded WB foods:     {wb_count}')
print(f'Added Odisha foods: {odisha_count}')
print(f'Added NI/Other:     {len(merged) - len(existing) - len(to_add_mandatory)}')
print(f'Total: {len(merged)}')
