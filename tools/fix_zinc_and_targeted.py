"""
Targeted fixes:
  1. ID 40  (Onion Tomato Uttapam) — fat was 63.2g in 120g (ICMR-corrected)
  2. ID 105 (Orange and Pineapple Cream) — family 'apple' → 'cream_dessert'
  3. Zinc (zn) fill for all local/indb items that have zn=0.0 or missing
     Uses category-based ICMR averages scaled to each item's serving size.
"""

import json, sys, re

sys.stdout.reconfigure(encoding='utf-8')

IN_FILE  = 'assets/data/food_master_v10.json'
OUT_FILE = 'assets/data/food_master_v10.json'

# ── ICMR zinc reference per 100g (conservative midpoint values) ───────────────
CATEGORY_ZN_PER_100G = {
    'legume':          2.2,   # lentils, chickpeas, dal
    'meat':            3.2,   # chicken, mutton, beef
    'fish':            0.7,   # typical fish
    'egg':             1.1,
    'dairy':           0.5,   # milk, paneer, curd
    'grain':           1.2,   # wheat, oats, barley
    'bread':           0.8,   # roti, chapati, paratha
    'rice':            0.7,   # cooked rice preparations
    'breakfast':       0.5,   # dosa, idli, poha
    'vegetable':       0.3,
    'shaak':           0.4,   # leafy greens
    'fruit':           0.15,
    'juice':           0.05,
    'snack':           0.5,
    'sweet':           0.3,
    'bakery':          0.5,
    'restaurant_food': 0.6,
    'soup':            0.4,
    'salad':           0.3,
    'pizza':           0.9,
    'noodle':          0.5,
    'beverage':        0.05,
}

def parse_serving_g(s):
    """Extract gram weight from serving string."""
    s = str(s).lower()
    # parenthetical: (Xg) or (~Xg)
    m = re.search(r'[~]?(\d+(?:\.\d+)?)\s*g', s)
    if m:
        return float(m.group(1))
    m = re.search(r'[~]?(\d+(?:\.\d+)?)\s*ml', s)
    if m:
        return float(m.group(1))
    # leading number + known unit
    unit_map = {'bowl': 250, 'plate': 300, 'cup': 240, 'piece': 60,
                'pcs': 60, 'pc': 60, 'slice': 40, 'wrap': 250}
    m = re.match(r'^(\d+(?:\.\d+)?)\s+(.+)', s)
    if m:
        n, unit = float(m.group(1)), m.group(2).strip()
        for k, v in unit_map.items():
            if k in unit:
                return n * v
    return 100.0


with open(IN_FILE, encoding='utf-8') as f:
    data = json.load(f)

fixes = {'uttapam': 0, 'family': 0, 'zinc': 0}

for item in data:
    iid = item.get('id')

    # ── Fix 1: Onion Tomato Uttapam (ID 40) ──────────────────────────────────
    if iid == 40:
        # ICMR reference for vegetable uttapam per 120g:
        # The plain (ID 50) is 174.2 kcal with f=6.1g. With onion/tomato
        # and slightly more oil the realistic range is 200-220 kcal.
        item['k']  = 210.0
        item['p']  = 4.0
        item['c']  = 26.0
        item['f']  = 8.5
        item['fi'] = 2.2
        item['ca'] = 25.0
        item['fe'] = 0.70
        item['zn'] = 0.45
        item['mg'] = 24.0
        item['pot']= 182.0
        item['vc'] = 5.5
        item['va'] = 28.0
        item['vd'] = 2.50
        print(f'  [UTTAPAM]  ID 40: fat corrected 63.2g → 8.5g; k 644.3 → 210.0 kcal')
        fixes['uttapam'] += 1

    # ── Fix 2: Orange and Pineapple Cream (ID 105) ───────────────────────────
    if iid == 105:
        item['family'] = 'cream_dessert'
        print(f"  [FAMILY]   ID 105 '{item.get('en')}': family 'apple' → 'cream_dessert'")
        fixes['family'] += 1

    # ── Fix 3: Zinc fill for local/indb items with zn=0 or missing ───────────
    src = item.get('src', '')
    if src in ('local', 'indb', 'ifct_recipe') and not item.get('zn'):
        cat = item.get('cat')
        zn_per_100g = CATEGORY_ZN_PER_100G.get(cat)
        if zn_per_100g:
            serving_g = parse_serving_g(item.get('s', '100g'))
            zn_value  = round(zn_per_100g * serving_g / 100.0, 2)
            item['zn'] = max(zn_value, 0.01)
            fixes['zinc'] += 1

print(f'\nFix summary:')
for k, v in fixes.items():
    print(f'  {k}: {v}')

# Quick sanity check on the fixes
id_map = {i['id']: i for i in data}

print('\n--- Verification ---')
for iid, label in [(40, 'Onion Tomato Uttapam'), (50, 'Plain Uttapam'),
                   (105, 'Orange Pineapple Cream'), (141, 'Chana Bhuna'), (142, 'Cholar Dal'), (34, 'Luchi')]:
    item = id_map.get(iid, {})
    p, c, f, k = item.get('p',0), item.get('c',0), item.get('f',0), item.get('k',0)
    calc = round(p*4+c*4+f*9, 1)
    print(f"  ID {iid} {label}: k={k} f={f} zn={item.get('zn','—')} family={item.get('family')} calc_k={calc}")

# Count remaining zn=0 items in local data
still_zero = sum(1 for i in data if i.get('src') in ('local','indb') and not i.get('zn'))
print(f'\nLocal/indb items still with zn=0: {still_zero}')

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print(f'Saved {len(data)} items to {OUT_FILE}')
