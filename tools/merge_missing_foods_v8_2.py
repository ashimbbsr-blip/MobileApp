"""Merge missingfoodsneedtobeadded.txt into food_master_v8_1.json → food_master_v8_2.json."""
import json, re, difflib, collections, sys

sys.stdout.reconfigure(encoding='utf-8')

SRC_FILE  = 'assets/data/missingfoodsneedtobeadded.txt'
BASE_FILE = 'assets/data/food_master_v8_1.json'
OUT_FILE  = 'assets/data/food_master_v8_2.json'
IDX_FILE  = 'assets/data/search_index_v2.json'

# NE India BN name map (hand-assigned)
NE_BN_MAP = {
    'Cooked rice (Arunachal/Nagaland staple)': 'ভাত (অরুণাচল/নাগাল্যান্ড)',
    'Zan (finger millet porridge)':            'জান (রাগি পোরিজ)',
    'Bamboo shoot (fresh)':                    'বাঁশের কোঁড়া',
    'Axone (fermented soybean)':               'অ্যাক্সোনে (গাঁজানো সয়াবিন)',
    'Smoked pork':                             'ধোঁয়া শুয়োরের মাংস',
    'Wild leafy greens (boiled)':              'বন্য শাক সবজি (সিদ্ধ)',
    'King chilli (Bhut Jolokia)':              'ভূত জলকিয়া (রাজা মরিচ)',
}

# ── Category mapping ────────────────────────────────────────────────────────
CAT_MAP = {
    'dal':         'legume',
    'dessert':     'sweet',
    'street_food': 'snack',
    'chicken':     'meat',
    'mutton':      'meat',
    'porridge':    'breakfast',
    'condiment':   'snack',
    'seafood':     'fish',
}

VALID_CATS = {
    'bakery','beverage','bread','breakfast','dairy','egg','fish','fruit',
    'grain','juice','legume','meat','noodle','pizza','restaurant_food',
    'rice','salad','shaak','snack','soup','sweet','vegetable'
}

def map_cat(cat, en_name):
    cat = (cat or 'vegetable').strip().lower()
    if cat in VALID_CATS:
        return cat
    if cat == 'curry':
        el = en_name.lower()
        if any(w in el for w in ['chicken','mutton','meat','pork','beef','lamb','gosht','keema']):
            return 'meat'
        return 'vegetable'
    return CAT_MAP.get(cat, 'vegetable')

# ── Bengali validation ───────────────────────────────────────────────────────
BN_RE = re.compile(r'[ঀ-৿]')

def bn_fix(text):
    if not text:
        return text
    text = text.replace('লল','ল').replace('তত','ত').replace('দদ','দ')
    return text

def bn_ok(text):
    if not text:
        return False
    has_bn = bool(BN_RE.search(text))
    has_latin = bool(re.search(r'[A-Za-z]', text))
    return has_bn and not has_latin

# ── Keyword generation ───────────────────────────────────────────────────────
def make_kw(en, cat):
    tokens = re.findall(r'[a-zA-Z]+', en)
    words = [t.lower() for t in tokens]
    kw = list(dict.fromkeys(words))
    if cat and cat not in kw:
        kw.insert(0, cat.replace('_',' '))
    kw = [k for k in kw if len(k) >= 2]
    return kw[:6]

# ── Parse source file ────────────────────────────────────────────────────────
raw_text = open(SRC_FILE, encoding='utf-8').read().replace('\r\n', '\n')

# Strategy:
# 1. Find and extract the NE foods dict {"foods_per_100g":[...]} at the end
# 2. Split remaining text on ] ... [ boundaries to get standard array chunks

# Find the NE foods dict (starts with \n{ on its own line after a ])
ne_match = re.search(r'\n\s*\{\s*\n\s*"foods_per_100g"', raw_text)
if ne_match:
    ne_text = raw_text[ne_match.start():].strip()
    array_section = raw_text[:ne_match.start()]
    print(f'NE-foods dict found at char {ne_match.start()}')
else:
    ne_text = None
    array_section = raw_text
    print('WARNING: NE-foods dict not found')

# Parse NE foods
ne_raw_items = []
if ne_text:
    try:
        ne_obj = json.loads(ne_text)
        for f in ne_obj.get('foods_per_100g', []):
            en_name = f.get('food', '')
            el = en_name.lower()
            if 'pork' in el:
                cat_ne = 'meat'
            elif 'axone' in el or 'soybean' in el:
                cat_ne = 'legume'
            elif 'millet' in el or 'zan' in el or 'porridge' in el:
                cat_ne = 'breakfast'
            elif 'rice' in el:
                cat_ne = 'rice'
            else:
                cat_ne = 'vegetable'

            item = {
                'id': 99000,
                'en': en_name,
                'bn': NE_BN_MAP.get(en_name, ''),
                'cat': cat_ne,
                's': '100g',
                'k': f.get('calories_kcal', 0),
                'p': f.get('protein_g', 0),
                'c': f.get('carbohydrates_g', 0),
                'f': f.get('fat_g', 0),
                'fi': f.get('fiber_g', 0),
                'ca': f.get('calcium_mg', 0),
                'fe': f.get('iron_mg', 0),
                'vc': f.get('vitamin_c_mg', 0),
                'kp': f.get('potassium_mg', 0),
                'na': 0,
                '_needs_bn': en_name not in NE_BN_MAP,
            }
            ne_raw_items.append(item)
        print(f'  NE-foods dict: {len(ne_raw_items)} items parsed')
    except Exception as e:
        print(f'  NE-foods dict PARSE ERROR: {e}')

# Split the array section into chunks on ] ... [ boundaries
chunks_raw = re.split(r'\]\s*\n+\s*\[', array_section)

all_raw_items = []
num_chunks = 0

for i, piece in enumerate(chunks_raw):
    piece = piece.strip()
    # Re-add brackets removed by split
    if not piece.startswith('['):
        piece = '[' + piece
    if not piece.endswith(']'):
        piece = piece + ']'
    num_chunks += 1
    try:
        items = json.loads(piece)
        all_raw_items.extend(items)
        print(f'  Chunk {i+1}: {len(items)} items')
    except json.JSONDecodeError as e:
        print(f'  Chunk {i+1}: PARSE ERROR: {e.msg} at line {e.lineno}')
        # Try fixing trailing commas
        fixed = re.sub(r',(\s*[\]\}])', r'\1', piece)
        try:
            items = json.loads(fixed)
            all_raw_items.extend(items)
            print(f'    → Fixed! {len(items)} items')
        except Exception as e2:
            print(f'    → Still failed: {e2}')
            print(f'    → Preview: {piece[:400]}')

# Append NE foods
all_raw_items.extend(ne_raw_items)
print(f'\nFound {num_chunks} array chunks + 1 NE-dict chunk')
total_raw = len(all_raw_items)
print(f'Total raw items (before any dedup): {total_raw}')

# ── Load existing dataset ────────────────────────────────────────────────────
existing = json.load(open(BASE_FILE, encoding='utf-8'))
print(f'Existing dataset: {len(existing)} items')
max_id = max(item['id'] for item in existing)
print(f'Max existing ID: {max_id}')

# Build lookup sets
ex_en_set = {}
ex_bn_set = {}

for item in existing:
    en_norm = item.get('en','').strip().lower()
    bn_norm  = item.get('bn','').strip()
    if en_norm:
        ex_en_set[en_norm] = item['id']
    if bn_norm:
        ex_bn_set[bn_norm] = item['id']

ex_en_list = list(ex_en_set.keys())

def is_dup_of_existing(en, bn):
    en_n = en.strip().lower()
    bn_n = bn.strip()
    if en_n in ex_en_set:
        return ex_en_set[en_n], en_n
    if bn_n and bn_n in ex_bn_set:
        return ex_bn_set[bn_n], bn_n
    matches = difflib.get_close_matches(en_n, ex_en_list, n=1, cutoff=0.90)
    if matches:
        return ex_en_set[matches[0]], matches[0]
    return None, None

# ── Deduplicate within new items ─────────────────────────────────────────────
seen_en = {}
seen_bn = {}
new_items_unique = []
internal_skip = 0

for item in all_raw_items:
    en_n = item.get('en','').strip().lower()
    bn_n = item.get('bn','').strip()
    if en_n in seen_en:
        internal_skip += 1
        print(f'SKIP_INTERNAL [{item.get("id","")}] "{item.get("en","")}" — dup of internal #{seen_en[en_n]}')
        continue
    if bn_n and bn_n in seen_bn:
        internal_skip += 1
        print(f'SKIP_INTERNAL [{item.get("id","")}] "{item.get("en","")}" — dup bn of internal #{seen_bn[bn_n]}')
        continue
    seen_en[en_n] = len(new_items_unique)
    if bn_n:
        seen_bn[bn_n] = len(new_items_unique)
    new_items_unique.append(item)

print(f'\nAfter internal dedup: {len(new_items_unique)} items ({internal_skip} skipped)')

# ── Dedup against existing ───────────────────────────────────────────────────
accepted = []
existing_skip = 0

for item in new_items_unique:
    en_name = item.get('en','')
    bn_name = item.get('bn','')
    dup_id, matched = is_dup_of_existing(en_name, bn_name)
    if dup_id is not None:
        existing_skip += 1
        print(f'SKIP [{item.get("id","")}] "{en_name}" — duplicate of existing "{matched}" (id {dup_id})')
        continue
    accepted.append(item)

print(f'\nAfter existing dedup: {len(accepted)} accepted, {existing_skip} skipped as duplicates of existing')

# ── Assign new IDs ────────────────────────────────────────────────────────────
next_id = max_id + 1
for item in accepted:
    item['_new_id'] = next_id
    next_id += 1

# ── Build enriched items ──────────────────────────────────────────────────────
def make_item(src):
    new_id = src['_new_id']
    en     = src.get('en', '')
    bn_raw = src.get('bn', '')
    bn     = bn_fix(bn_raw)
    cat_src = src.get('cat', 'vegetable')
    cat    = map_cat(cat_src, en)

    needs_review = src.get('_needs_bn', False)
    if bn and not bn_ok(bn):
        needs_review = True

    item = {
        'en':  en,
        'bn':  bn,
        's':   src.get('s', '100g'),
        'k':   src.get('k', 0),
        'p':   src.get('p', 0),
        'c':   src.get('c', 0),
        'f':   src.get('f', 0),
        'fi':  src.get('fi', 0),
        'ca':  src.get('ca', 0),
        'fe':  src.get('fe', 0),
        'vc':  src.get('vc', 0),
        'kp':  src.get('kp', 0),
        'na':  src.get('na', 0),
        'cat': cat,
        'kw':  make_kw(en, cat),
        'src': 'curated_estimate',
        'id':  new_id,
        'family': '',
        'nutrition_source': 'user_estimate',
        'nutrition_confidence': 'low',
        'quality_score': 40,
        'popularity_score': 50,
        'search_priority': 45,
        'aliases': [],
        'canonical': False,
    }
    return item, needs_review

enriched = []
bn_reviews = []

for src in accepted:
    item, needs_review = make_item(src)
    enriched.append(item)
    if needs_review:
        bn_reviews.append(item['en'])

# ── Merge and save ────────────────────────────────────────────────────────────
final_data = existing + enriched

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(final_data, f, ensure_ascii=False, separators=(',',':'))

print(f'\nSaved {len(final_data)} items → {OUT_FILE}')

# ── Summary ───────────────────────────────────────────────────────────────────
print('\n' + '='*60)
print('MERGE SUMMARY')
print('='*60)
print(f'Total in source file (before dedup): {total_raw}')
print(f'Skipped as internal duplicates:      {internal_skip}')
print(f'Skipped as duplicates of existing:   {existing_skip}')
print(f'Added:                               {len(enriched)}')
print(f'Final total in v8_2:                 {len(final_data)}')
print()
if bn_reviews:
    print(f'Items needing Bengali review ({len(bn_reviews)}):')
    for name in bn_reviews:
        print(f'  # NEEDS_BN_REVIEW: {name}')
print()
print('ADDED ITEMS:')
for item in enriched:
    print(f'  ADD [{item["id"]}] "{item["en"]}" cat={item["cat"]} k={item["k"]}')

# ── Rebuild search index ───────────────────────────────────────────────────────
print('\n' + '='*60)
print('REBUILDING SEARCH INDEX')
print('='*60)

data = json.load(open(OUT_FILE, encoding='utf-8'))
print(f'Loaded {len(data)} items for index rebuild')

STOPWORDS = {'and','the','with','of','in','a','an','or','for','to','at','by'}

def en_tokens(text):
    return [t for t in re.findall(r'[a-z0-9]+', (text or '').lower())
            if len(t) >= 2 and t not in STOPWORDS]

def bn_tokens(text):
    return [t for t in re.findall(r'[ঀ-৿]+', text or '') if len(t) >= 2]

def add_pfx(bucket, token, fid, pri):
    for l in range(2, len(token) + 1):
        bucket[token[:l]].append((pri, fid))

en_pfx = collections.defaultdict(list)
bn_pfx = collections.defaultdict(list)
al_idx = collections.defaultdict(list)
fm_idx = collections.defaultdict(list)

for item in data:
    fid = item['id']
    pri = item.get('search_priority', 50)
    fam = item.get('family', 'other') or 'other'
    toks = set()
    for src in [item.get('en', ''), *item.get('kw', []), *item.get('aliases', [])]:
        toks.update(en_tokens(src))
    for tok in toks:
        add_pfx(en_pfx, tok, fid, pri)
    for tok in bn_tokens(item.get('bn', '')):
        add_pfx(bn_pfx, tok, fid, pri)
    for al in item.get('aliases', []):
        for tok in en_tokens(al):
            al_idx[tok].append((pri, fid))
    fm_idx[fam].append((pri, fid))

def sort_bkt(lst, cap=200):
    seen, out = set(), []
    for pri, fid in sorted(lst, key=lambda x: -x[0]):
        if fid not in seen:
            seen.add(fid); out.append(fid)
            if len(out) >= cap:
                break
    return out

top100 = [d['id'] for d in sorted(data, key=lambda x: -x.get('search_priority', 0))[:100]]

idx_v2 = {
    'version': 2, 'created': '2026-06-28', 'total_foods': len(data),
    'en_prefix':    {k: sort_bkt(v)      for k, v in en_pfx.items()},
    'bn_prefix':    {k: sort_bkt(v)      for k, v in bn_pfx.items()},
    'alias_lookup': {k: sort_bkt(v, 50)  for k, v in al_idx.items()},
    'family_index': {k: sort_bkt(v)      for k, v in fm_idx.items()},
    'top_foods':    top100,
}

with open(IDX_FILE, 'w', encoding='utf-8') as f:
    json.dump(idx_v2, f, ensure_ascii=False, separators=(',', ':'))

en_count = sum(len(v) for v in idx_v2['en_prefix'].values())
bn_count = sum(len(v) for v in idx_v2['bn_prefix'].values())
print(f'EN prefix tokens : {len(idx_v2["en_prefix"])}')
print(f'BN prefix tokens : {len(idx_v2["bn_prefix"])}')
print(f'EN index entries : {en_count}')
print(f'BN index entries : {bn_count}')
print(f'Families         : {len(idx_v2["family_index"])}')
print(f'Saved → {IDX_FILE}')
print('\nDone!')
