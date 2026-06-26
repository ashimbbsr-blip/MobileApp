"""
audit_fix_v2.py — BN duplicate resolution + nutrition anomaly fixes

REMOVE (inferior entry, superseded or wrong data):
  358  Spinach mutton         → keep 3018 (k=390 too high)
  231  Rohu Curry             → keep 4001 (k=280 too high)
  949  Alur Dom               → keep 10007 (k=260 too high)
  952  Cabbage Curry          → keep 10014 (k=160 too high)
  958  Lau Ghonto             → keep 10019 (k=150 too high)
  1155 Gourd bitter fry       → keep 10023 (superseded by Uchhe Bhaja)
  11021 Neem Leaf Fry         → keep 11018 (identical nutrition, EN-name duplicate)
  11023 Neem Begun Tarkari    → keep 11017 (identical nutrition, same dish)
  1064 Rasgulla (Rosogolla)   → keep 12001 (near-identical nutrition)
  227  Macher Jhol            → keep 30012 (k=260 too high)
  1433 Mutton kosha           → keep 30017 (k=418 too high)
  60022 Rabri                 → keep 96010 (identical nutrition, better source=indb)
  1242 Carambola, raw         → keep 55006 Star Fruit (same fruit, USDA k=31 correct)
  1247 Emblic, raw            → keep 54101 Indian Gooseberry (same fruit)
  183  Coconut Water          → keep 56010 Tender Coconut Water (k=60 wrong; k=19 correct)
  1261 Orange juice, raw      → keep 56018 Orange Juice (k=9 wrong; k=45 correct per USDA)

RENAME BN (different dishes sharing same Bengali name):
  137  Sweetened yogurt          → "মিষ্টি দই (সাধারণ)"  (generic vs mishti doi)
  1403 Odia Badi Chura          → "বড়ি চুরা (ওড়িয়া)"    (Odia vs Bengali)
  30034 Baigana Poda             → "বেগুন পোড়া (ওড়িয়া)"  (Odia vs Bengali)
  1103 Grass pea, split, raw     → "খেসারি ডাল (কাঁচা)"   (raw vs cooked)
  1238 Asian pears, raw          → "এশিয়ান নাশপাতি"       (Asian vs European pear)
  15013 Plum                     → "আলুবোখারা"             (European plum ≠ jujube বরই)
  98211 7UP Zero Sugar PH        → "সেভেন আপ জিরো সুগার (পিজ্জা হাট)"
  56004 Lemon Juice (Sweetened)  → "লেবুর শরবত (মিষ্টি)"  (≠ 511 Lemonade)
  57004 Hilsa Paturi             → "ইলিশ পাতুরি (রেস্তোরাঁ)"
  57006 Chingri Malai Curry      → "চিংড়ি মালাইকারি (রেস্তোরাঁ)"
  57008 Shukto (Bengali Mixed Veg) → "শুক্তো (রেস্তোরাঁ)"
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

REMOVE_IDS = {
    358, 231, 949, 952, 958, 1155, 11021, 11023,
    1064, 227, 1433, 60022, 1242, 1247, 183, 1261,
}

BN_RENAMES = {
    137:   'মিষ্টি দই (সাধারণ)',
    1403:  'বড়ি চুরা (ওড়িয়া)',
    30034: 'বেগুন পোড়া (ওড়িয়া)',
    1103:  'খেসারি ডাল (কাঁচা)',
    1238:  'এশিয়ান নাশপাতি',
    15013: 'আলুবোখারা',
    98211: 'সেভেন আপ জিরো সুগার (পিজ্জা হাট)',
    56004: 'লেবুর শরবত (মিষ্টি)',
    57004: 'ইলিশ পাতুরি (রেস্তোরাঁ)',
    57006: 'চিংড়ি মালাইকারি (রেস্তোরাঁ)',
    57008: 'শুক্তো (রেস্তোরাঁ)',
}

data = json.load(open(DATASET, encoding='utf-8'))
print(f'Loaded {len(data)} items')

# ── Remove duplicates ─────────────────────────────────────────────────────────
before = len(data)
data = [d for d in data if d['id'] not in REMOVE_IDS]
print(f'Removed {before - len(data)} duplicate entries')

# ── Rename BN ─────────────────────────────────────────────────────────────────
id_map = {d['id']: d for d in data}
renamed = 0
for fid, new_bn in BN_RENAMES.items():
    if fid in id_map:
        old_bn = id_map[fid].get('bn', '')
        id_map[fid]['bn'] = new_bn
        print(f'  BN [{fid}] {id_map[fid]["en"]}: "{old_bn}" → "{new_bn}"')
        renamed += 1
    else:
        print(f'  BN [{fid}]: NOT FOUND (already removed)')
print(f'BN renames: {renamed}')

print(f'\nFinal item count: {len(data)}')
with open(DATASET, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print('Saved.')
