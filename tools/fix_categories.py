"""
fix_categories.py — Normalize all micro/legacy categories in food_master_v7_2.json
to the 22 official UI categories.
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

CAT_MAP = {
    # Micro-meat categories → meat
    'mutton':       'meat',
    'chicken':      'meat',
    'duck':         'meat',
    'beef':         'meat',
    'seafood':      'fish',       # prawn/seafood grouped with fish
    # Dairy sub-types → dairy
    'paneer':       'dairy',
    'curd':         'dairy',
    'cheese':       'dairy',
    'butter':       'dairy',
    'ghee':         'dairy',
    'milk_powder':  'dairy',
    # Confectionery → sweet
    'chocolate':    'sweet',
    'dark_chocolate':'sweet',
    'candy':        'sweet',
    'dessert':      'sweet',
    # Baked goods → bakery
    'biscuit':      'bakery',
    'cookie':       'bakery',
    'rusk':         'bakery',
    # Pulses → legume
    'dal':          'legume',
    # Drinks → beverage
    'energy_drink': 'beverage',
    'sports_drink': 'beverage',
    'water':        'beverage',
    # Catch-all curry → vegetable (only item is Kadhi Pakora, a vegetarian dish)
    'curry':        'vegetable',
}

data = json.load(open(DATASET, encoding='utf-8'))
print(f'Loaded {len(data)} items')

changed = 0
for d in data:
    old = d.get('cat', '')
    new = CAT_MAP.get(old)
    if new:
        d['cat'] = new
        changed += 1

print(f'Category fixes applied: {changed}')

with open(DATASET, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print('Saved.')
