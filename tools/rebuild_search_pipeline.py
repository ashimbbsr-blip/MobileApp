"""
NutriCheck Food Search Pipeline v2
Phases 1-12: audit, family clustering, quality scoring, Bengali QA, search index
"""
import json, sys, re, collections, os
from difflib import SequenceMatcher
sys.stdout.reconfigure(encoding='utf-8')

import pathlib
_OUT_DIR = pathlib.Path('tools/output')
_OUT_DIR.mkdir(parents=True, exist_ok=True)

INPUT      = 'assets/data/food_master_v7_2.json'
OUT_MASTER = 'assets/data/food_master_v8_0.json'
OUT_AUDIT  = str(_OUT_DIR / 'food_audit_report.json')
OUT_FAM    = str(_OUT_DIR / 'food_families.json')
OUT_ALIAS  = str(_OUT_DIR / 'food_aliases.json')
OUT_USDA   = str(_OUT_DIR / 'usda_mapping.json')
OUT_BN_QA  = str(_OUT_DIR / 'bengali_qa_report.json')
OUT_INDEX  = 'assets/data/search_index_v2.json'

data = json.load(open(INPUT, encoding='utf-8'))
print(f'Loaded {len(data)} items')

# ── helpers ──────────────────────────────────────────────────────────────────
def nl(s): return (' ' + (s or '').lower() + ' ')

# ── FAMILY RULES (most-specific first, search in padded name) ────────────────
FAMILY_RULES = [
    ('biryani',      ['biryani','biriyani','biriani']),
    ('khichdi',      ['khichdi','khichuri','kitchdi']),
    ('pulao',        ['pulao','pilaf','pulav']),
    ('fried rice',   ['fried rice']),
    ('rice',         ['rice','bhaat']),
    ('paratha',      ['paratha','parantha','parotta']),
    ('puri',         ['puri ','poori','luchi']),
    ('naan',         ['naan']),
    ('dosa',         ['dosa ','dosai','uttapam']),
    ('idli',         ['idli','idly']),
    ('upma',         ['upma']),
    ('poha',         ['poha ','aval']),
    ('roti',         ['roti','chapati','chapatti','chappati','phulka']),
    ('bread',        ['bread','toast']),
    ('samosa',       ['samosa']),
    ('pakora',       ['pakora','pakoda','bajji','bhajia']),
    ('momo',         ['momo']),
    ('chaat',        ['chaat','bhelpuri','pani puri','golgappa']),
    ('dhokla',       ['dhokla']),
    ('dal',          ['dal ','daal',' lentil']),
    ('rajma',        ['rajma','kidney bean']),
    ('chana',        ['chana ','chickpea','chole']),
    ('moong',        ['moong','mung']),
    ('chicken',      ['chicken','murgi']),
    ('mutton',       ['mutton','lamb ','goat ','mangsho','keema','kheema']),
    ('beef',         ['beef']),
    ('pork',         ['pork']),
    ('hilsa',        ['hilsa','ilish']),
    ('rohu',         ['rohu','rui fish','rui mach']),
    ('catla',        ['catla','katla']),
    ('prawn',        ['prawn','shrimp','chingri']),
    ('crab',         ['crab']),
    ('fish',         [' fish ',' mach ']),
    ('omelette',     ['omelette','omelet']),
    ('egg',          [' egg ']),
    ('paneer',       ['paneer']),
    ('cheese',       ['cheese']),
    ('milk',         ['milk ','dudh']),
    ('yogurt',       ['yogurt','curd ','dahi ','raita']),
    ('ghee',         ['ghee']),
    ('butter',       ['butter']),
    ('pizza',        ['pizza']),
    ('burger',       ['burger']),
    ('wrap',         ['wrap']),
    ('kathi roll',   ['kathi roll','kati roll']),
    ('roll',         [' roll ']),
    ('pasta',        ['pasta','spaghetti','macaroni']),
    ('noodle',       ['noodle','chowmein','chow mein','hakka']),
    ('kheer',        ['kheer','payesh','payasam','firni']),
    ('halwa',        ['halwa','halva']),
    ('ladoo',        ['ladoo','laddoo','laddu']),
    ('rasgulla',     ['rasgulla','roshogolla']),
    ('gulab jamun',  ['gulab jamun']),
    ('barfi',        ['barfi','burfi']),
    ('jalebi',       ['jalebi']),
    ('ice cream',    ['ice cream','icecream','kulfi','gelato','soft serve',
                      'sundae','mcflurry','mcswirl','choco dip','chocodip','butterscotch dip']),
    ('cake',         ['cake ','muffin','brownie']),
    ('cookie',       ['cookie','biscuit']),
    ('chocolate',    ['chocolate']),
    ('tea',          [' tea ','chai ']),
    ('coffee',       ['coffee','cappuccino','latte ','mocha','espresso','frappe','americano','macchiato']),
    ('cola',         ['coca-cola','coke ','pepsi','sprite','fanta','7up']),
    ('juice',        ['juice','sharbat','nimbu pani']),
    ('lassi',        ['lassi']),
    ('shake',        ['shake ','milkshake','smoothie']),
    ('water',        ['water']),
    ('fries',        ['french fries','fries ']),
    ('wings',        ['wings']),
    ('nuggets',      ['nugget']),
    ('potato',       ['potato','aloo ']),
    ('tomato',       ['tomato']),
    ('onion',        ['onion']),
    ('spinach',      ['spinach','palak']),
    ('eggplant',     ['eggplant','brinjal','begun','baingan']),
    ('cauliflower',  ['cauliflower','gobi']),
    ('cabbage',      ['cabbage']),
    ('carrot',       ['carrot']),
    ('pumpkin',      ['pumpkin','kumro']),
    ('bitter gourd', ['bitter gourd','karela','ucche']),
    ('ridge gourd',  ['ridge gourd','jhinge']),
    ('mango',        ['mango','aam ']),
    ('banana',       ['banana','kela ']),
    ('apple',        ['apple']),
    ('orange',       ['orange','malta']),
    ('grapes',       ['grape']),
    ('watermelon',   ['watermelon']),
    ('papaya',       ['papaya']),
    ('guava',        ['guava']),
    ('almond',       ['almond','badam']),
    ('cashew',       ['cashew','kaju']),
    ('peanut',       ['peanut','groundnut']),
    ('oil',          [' oil ']),
    ('sugar',        ['sugar']),
    ('jaggery',      ['jaggery','gur ']),
    ('honey',        ['honey']),
    ('salt',         [' salt ']),
    ('mustard',      ['mustard']),
]

def detect_family(item):
    name = nl(item.get('en',''))
    for fam, kws in FAMILY_RULES:
        for kw in kws:
            if kw in name:
                return fam
    return item.get('cat','other')

# ── SOURCE MAPS ──────────────────────────────────────────────────────────────
BRAND_SRCS = {'pizzahut_india','kfc_india','mcdonalds_india','dominos_india',
               'maggi_in','deutsche_see_ciqual'}

SRC_MAP = {
    'indb':           ('ifct',           'very_high'),
    'icmr_2004':      ('ifct',           'very_high'),
    'ijcmas_2020':    ('ifct',           'very_high'),
    'bd_fct':         ('bd_fct',         'high'),
    'local':          ('ifct_recipe',    'high'),
    'odia':           ('ifct_recipe',    'medium'),
    'fatsecret_in':   ('usda',           'medium'),
    'fatsecret_usda': ('usda',           'medium'),
}
for s in BRAND_SRCS:
    SRC_MAP[s] = ('brand_official', 'very_high')

def src_base(src):
    if src in ('indb','icmr_2004','ijcmas_2020'): return 50
    if src == 'bd_fct': return 45
    if src in BRAND_SRCS: return 40
    if src in ('local',): return 35
    if src == 'odia': return 35
    if src in ('fatsecret_in','fatsecret_usda'): return 25
    return 20

def calc_quality(item, is_dup):
    s = src_base(item.get('src'))
    for k in ('fi','ca','fe','zn'):
        try:
            if float(item.get(k) or 0) > 0: s += 5
        except: pass
    has_vit = any(float(item.get(k) or 0) > 0 for k in ('va','vc','vd'))
    has_min = any(float(item.get(k) or 0) > 0 for k in ('mg','pot'))
    if has_vit: s += 5
    if has_min: s += 5
    if is_dup:  s -= 15
    return max(0, min(100, s))

# ── POPULARITY ────────────────────────────────────────────────────────────────
CAT_POP = {
    'rice':100,'grain':95,'bread':95,'legume':90,'meat':88,'fish':85,
    'vegetable':82,'dairy':80,'egg':80,'fruit':75,'breakfast':78,
    'soup':72,'salad':65,'snack':70,'sweet':68,'beverage':65,
    'noodle':65,'pizza':60,'shaak':72,'other':50
}
POP_BOOSTS = [
    (['biryani','biriyani'],8),(['dal ','daal'],10),(['roti','chapati'],10),
    (['hilsa','ilish'],10),(['rohu','rui fish'],8),(['prawn','chingri'],7),
    (['butter chicken'],8),(['palak paneer'],7),(['paneer'],5),
    (['samosa'],8),(['idli','dosa '],7),(['khichdi','khichuri'],5),
    (['chicken'],5),(['korma','kofta','rezala'],5),(['momo'],6),
    (['chaat','bhelpuri'],6),
]

def calc_pop(item):
    base = CAT_POP.get(item.get('cat','other'), 50)
    if item.get('src') in BRAND_SRCS:
        base = max(base - 10, 20)
    name = nl(item.get('en',''))
    boost = max((b for kws,b in POP_BOOSTS if any(k in name for k in kws)), default=0)
    return min(100, base + boost)

# ── GLOBAL ALIASES ────────────────────────────────────────────────────────────
GLOBAL_ALIASES = {
    'rice':       ['bhaat','bhat','cooked rice','boiled rice','steamed rice'],
    'dal':        ['daal','lentil','lentil soup','lentil curry'],
    'roti':       ['chapati','chapatti','chappati','flatbread','phulka'],
    'paratha':    ['parantha','laccha paratha','aloo paratha'],
    'puri':       ['poori','luchi','bhatura'],
    'naan':       ['nan','garlic naan','butter naan'],
    'dosa':       ['dosai','plain dosa','masala dosa'],
    'idli':       ['idly','soft idli','rice cake'],
    'chicken':    ['murgi','murgh','murghi'],
    'mutton':     ['lamb','goat meat','mangsho','gosht'],
    'hilsa':      ['ilish','ilish mach','hilsa fish','ilish maach'],
    'rohu':       ['rui','rui mach','rohu fish'],
    'prawn':      ['shrimp','chingri','jhinga','chingri mach'],
    'egg':        ['anda','deem','dim'],
    'paneer':     ['cottage cheese','chhena','chena'],
    'ghee':       ['clarified butter','desi ghee'],
    'yogurt':     ['dahi','curd','doi'],
    'biryani':    ['biriyani','biriani'],
    'momo':       ['dumpling','dimsum','dim sum','momos'],
    'samosa':     ['samoosa','singara','singada'],
    'pakora':     ['pakoda','bhajia','bajji'],
    'khichdi':    ['khichuri','kitchdi','kichri'],
    'kheer':      ['payesh','payasam','firni','phirni'],
    'halwa':      ['halva','sheera'],
    'ladoo':      ['laddoo','laddu','motichoor'],
    'rasgulla':   ['roshogolla','rossogolla'],
    'jalebi':     ['jilabi','imarti'],
    'barfi':      ['burfi','barfee'],
    'chana':      ['chickpea','chole','kabuli chana'],
    'rajma':      ['kidney bean','red kidney bean'],
    'moong':      ['mung','mung bean','green gram'],
    'coffee':     ['cafe','kapi'],
    'tea':        ['chai','cha'],
    'lassi':      ['buttermilk','chaas','mattha'],
    'chaat':      ['bhelpuri','pani puri','golgappa','papdi chaat'],
    'mango':      ['aam','keri','kairi'],
    'banana':     ['kela','kadali'],
    'guava':      ['amrood','peru'],
    'peanut':     ['groundnut','moongphali'],
    'cashew':     ['kaju','kaaju'],
    'almond':     ['badam'],
    'pizza':      ['peetza'],
    'noodle':     ['chowmein','hakka noodle','mein'],
    'biryani':    ['biriyani','biriani'],
    'kathi roll': ['kathi','kati roll','frankie'],
    'butter':     ['makhan'],
}

# ── PHASE 1: DUPLICATE DETECTION ─────────────────────────────────────────────
print('Phase 1: Duplicate detection...')
dup_ids  = set()
dup_pairs, near_pairs, var_pairs = [], [], []

cat_groups = collections.defaultdict(list)
for item in data:
    cat_groups[item.get('cat','other')].append(item)

for cat, items in cat_groups.items():
    n = len(items)
    for i in range(n):
        for j in range(i+1, n):
            a, b = items[i], items[j]
            ratio = SequenceMatcher(None, (a['en'] or '').lower(),
                                         (b['en'] or '').lower()).ratio()
            pair = {'id_a':a['id'],'en_a':a['en'],'id_b':b['id'],'en_b':b['en'],
                    'similarity':round(ratio,3),'category':cat}
            if ratio >= 0.90:
                dup_pairs.append(pair)
                dup_ids.add(b['id'])
            elif ratio >= 0.75:
                near_pairs.append(pair)
            elif ratio >= 0.62:
                var_pairs.append(pair)

print(f'  Dups={len(dup_pairs)}, Near={len(near_pairs)}, Variants={len(var_pairs)}')

# ── PHASE 10: BENGALI QA ─────────────────────────────────────────────────────
print('Phase 10: Bengali QA...')
LATIN_RE = re.compile(r'[a-zA-Z]')
bn_issues = []
for item in data:
    bn = item.get('bn','')
    issues = []
    if LATIN_RE.search(bn): issues.append('latin_chars')
    bn_chars = [c for c in bn if 'ঀ' <= c <= '৿']
    if len(bn_chars) < 2 and len(bn.strip()) > 0: issues.append('too_short')
    if not bn.strip(): issues.append('empty')
    if issues:
        bn_issues.append({'id':item['id'],'en':item['en'],'bn':bn,'issues':issues})
print(f'  Bengali issues: {len(bn_issues)}')

# ── ENRICH ALL ITEMS ──────────────────────────────────────────────────────────
print('Enriching items...')
for item in data:
    fam = detect_family(item)
    item['family']               = fam
    ns, nc                       = SRC_MAP.get(item.get('src'), ('user_estimate','low'))
    item['nutrition_source']     = ns
    item['nutrition_confidence'] = nc
    item['quality_score']        = calc_quality(item, item['id'] in dup_ids)
    item['popularity_score']     = calc_pop(item)
    item['search_priority']      = round(item['quality_score']*0.4 + item['popularity_score']*0.6)
    item['aliases']              = list(GLOBAL_ALIASES.get(fam, []))
    item['canonical']            = False

# Canonical: highest quality_score per family (prefer lower id on tie)
fam_groups = collections.defaultdict(list)
for item in data:
    fam_groups[item['family']].append(item)
for fam, items in fam_groups.items():
    best = max(items, key=lambda x: (x['quality_score'], -x['id']))
    best['canonical'] = True

avg_q = sum(d['quality_score'] for d in data)/len(data)
avg_p = sum(d['popularity_score'] for d in data)/len(data)
print(f'  avg_quality={avg_q:.1f}, avg_popularity={avg_p:.1f}')

# ── SAVE MASTER v8 ────────────────────────────────────────────────────────────
print('Saving food_master_v8_0.json...')
with open(OUT_MASTER,'w',encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',',':'))

# ── AUDIT REPORT ──────────────────────────────────────────────────────────────
no_src   = [{'id':d['id'],'en':d['en'],'cat':d.get('cat')} for d in data if not d.get('src')]
low_q    = sorted([{'id':d['id'],'en':d['en'],'quality_score':d['quality_score']}
                    for d in data if d['quality_score']<30],key=lambda x:x['quality_score'])
audit    = {
    'total':data.__len__(),
    'summary':{'duplicates':len(dup_pairs),'near_duplicates':len(near_pairs),
                'variants':len(var_pairs),'no_src':len(no_src),'low_quality':len(low_q),'bn_qa':len(bn_issues)},
    'duplicates':   dup_pairs[:300],
    'near_duplicates':near_pairs[:300],
    'variants':     var_pairs[:200],
    'no_src':       no_src,
    'low_quality':  low_q[:100],
}
with open(OUT_AUDIT,'w',encoding='utf-8') as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

# ── FOOD FAMILIES ─────────────────────────────────────────────────────────────
fam_out = {}
for fam, items in sorted(fam_groups.items(),key=lambda x:-len(x[1])):
    canonical = next((it for it in items if it['canonical']), items[0])
    fam_out[fam] = {'count':len(items),'canonical_id':canonical['id'],
                    'canonical_en':canonical['en'],
                    'member_ids':sorted(it['id'] for it in items)}
with open(OUT_FAM,'w',encoding='utf-8') as f:
    json.dump({'version':1,'families':fam_out}, f, ensure_ascii=False, indent=2)

# ── ALIASES FILE ──────────────────────────────────────────────────────────────
with open(OUT_ALIAS,'w',encoding='utf-8') as f:
    json.dump({'version':1,'aliases':GLOBAL_ALIASES}, f, ensure_ascii=False, indent=2)

# ── USDA MAPPING ─────────────────────────────────────────────────────────────
best_rice = max((d for d in data if 'rice' in (d['en'] or '').lower() and d['cat']=='grain'),
                key=lambda x:x['quality_score'], default=data[0])
best_chk  = max((d for d in data if 'chicken' in (d['en'] or '').lower()),
                key=lambda x:x['quality_score'], default=data[0])
usda_doc  = {
    'description':'USDA normalization pipeline — maps raw USDA food names to NutriCheck canonical foods',
    'version':1,
    'pipeline_steps':[
        '1. Normalize: lowercase, strip commas/parens, collapse spaces',
        '2. Detect family using FAMILY_RULES keyword list',
        '3. Find local canonical food for that family (canonical=true)',
        '4. If SequenceMatcher ratio >= 0.85, link to canonical; else create new local item',
        '5. Tag: src=usda, nutrition_source=usda, nutrition_confidence=medium',
        '6. Store usda_cache={fdc_id, cached:true, cached_at, local_id}',
    ],
    'cache_schema':{'source':'usda','fdc_id':0,'cached':True,'cached_at':'ISO8601','local_id':'int'},
    'example_mappings':{
        'Rice, white, long-grain, cooked':f'→ id:{best_rice["id"]} ({best_rice["en"]})',
        'Rice, white, enriched, cooked':  f'→ id:{best_rice["id"]} ({best_rice["en"]})',
        'Chicken, broilers, meat only, roasted':f'→ id:{best_chk["id"]} ({best_chk["en"]})',
        'Chicken breast, cooked':         f'→ id:{best_chk["id"]} ({best_chk["en"]})',
    },
    'dedup_rule':'If similarity >= 0.85 to existing canonical, reuse canonical id. Do not create duplicate.',
}
with open(OUT_USDA,'w',encoding='utf-8') as f:
    json.dump(usda_doc, f, ensure_ascii=False, indent=2)

# ── BENGALI QA REPORT ─────────────────────────────────────────────────────────
by_type = collections.defaultdict(list)
for issue in bn_issues:
    for t in issue['issues']:
        by_type[t].append({'id':issue['id'],'en':issue['en'],'bn':issue['bn']})
with open(OUT_BN_QA,'w',encoding='utf-8') as f:
    json.dump({'total_issues':len(bn_issues),'by_type':dict(by_type),'all_issues':bn_issues},
              f, ensure_ascii=False, indent=2)

# ── SEARCH INDEX V2 ───────────────────────────────────────────────────────────
print('Building search_index_v2...')
STOPWORDS = {'and','the','with','of','in','a','an','or','for','to','at','by'}

def en_tokens(text):
    return [t for t in re.findall(r'[a-z0-9]+', (text or '').lower())
            if len(t)>=2 and t not in STOPWORDS]

def bn_tokens(text):
    return [t for t in re.findall(r'[ঀ-৿]+', text or '') if len(t)>=2]

def add_pfx(bucket, token, fid, pri):
    for l in range(2, min(len(token)+1, len(token)+1)):
        bucket[token[:l]].append((pri, fid))

en_pfx = collections.defaultdict(list)
bn_pfx = collections.defaultdict(list)
al_idx = collections.defaultdict(list)
fm_idx = collections.defaultdict(list)

for item in data:
    fid, pri, fam = item['id'], item['search_priority'], item['family']
    toks = set()
    for src in [item.get('en',''), *item.get('kw',[]), *item.get('aliases',[])]:
        toks.update(en_tokens(src))
    for tok in toks:
        add_pfx(en_pfx, tok, fid, pri)
    for tok in bn_tokens(item.get('bn','')):
        add_pfx(bn_pfx, tok, fid, pri)
    for al in item.get('aliases',[]):
        for tok in en_tokens(al):
            al_idx[tok].append((pri, fid))
    fm_idx[fam].append((pri, fid))

def sort_bkt(lst, cap=200):
    seen, out = set(), []
    for pri, fid in sorted(lst, key=lambda x:-x[0]):
        if fid not in seen:
            seen.add(fid); out.append(fid)
            if len(out) >= cap: break
    return out

top100 = [d['id'] for d in sorted(data, key=lambda x:-x['search_priority'])[:100]]

idx_v2 = {
    'version':2,'created':'2026-06-25','total_foods':len(data),
    'en_prefix':  {k:sort_bkt(v)     for k,v in en_pfx.items()},
    'bn_prefix':  {k:sort_bkt(v)     for k,v in bn_pfx.items()},
    'alias_lookup':{k:sort_bkt(v,50) for k,v in al_idx.items()},
    'family_index':{k:sort_bkt(v)    for k,v in fm_idx.items()},
    'top_foods':  top100,
}
with open(OUT_INDEX,'w',encoding='utf-8') as f:
    json.dump(idx_v2, f, ensure_ascii=False, separators=(',',':'))

# ── SUMMARY ──────────────────────────────────────────────────────────────────
print()
print('='*62)
print('PIPELINE COMPLETE')
print('='*62)
print(f'Total items:          {len(data)}')
print(f'Families:             {len(fam_out)}')
print(f'Avg quality_score:    {avg_q:.1f}')
print(f'Avg popularity_score: {avg_p:.1f}')
print(f'Duplicates:           {len(dup_pairs)}')
print(f'Near-duplicates:      {len(near_pairs)}')
print(f'Variants:             {len(var_pairs)}')
print(f'Bengali QA issues:    {len(bn_issues)}')
print(f'EN prefix tokens:     {len(idx_v2["en_prefix"])}')
print(f'BN prefix tokens:     {len(idx_v2["bn_prefix"])}')
print()
print('Top 15 families by size:')
for fam,(info) in list(fam_out.items())[:15]:
    print(f'  {fam:<22} {info["count"]:>4}')
print()
for path in [OUT_MASTER,OUT_AUDIT,OUT_FAM,OUT_ALIAS,OUT_USDA,OUT_BN_QA,OUT_INDEX]:
    kb = os.path.getsize(path)//1024
    print(f'  {path}  ({kb}KB)')
