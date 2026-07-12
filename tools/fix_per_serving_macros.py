"""
Fix items where macro/calorie data was stored per SERVING instead of per 100g.
These items have c > 100g (physically impossible per 100g) and serving sizes > 100g.
"""
import json, re

MACRO_FIELDS = ['k', 'p', 'c', 'f', 'fi', 'alc_g']

def parse_serving_g(s_val):
    """Extract numeric grams from a serving field like '250g', '1 plate' etc."""
    if s_val is None:
        return None
    m = re.search(r'[\d.]+', str(s_val))
    if m:
        return float(m.group())
    return None

with open('assets/data/food_master_v10.json', encoding='utf-8') as f:
    foods = json.load(f)

changes = []

for food in foods:
    c_val = food.get('c', 0) or 0
    if c_val <= 100:
        continue

    bid = food['id']
    s_raw = food.get('s', None)
    sg = parse_serving_g(s_raw)

    # Special manual corrections
    if bid == 534:  # Pear preserves — USDA correct values per 100g
        food['k'] = 268.0; food['p'] = 0.3; food['c'] = 65.0; food['f'] = 0.2
        food['fi'] = 1.3
        changes.append('ID:534 manual fix (Pear preserves -> 268kcal, 65g carbs per 100g)')
        continue

    if bid == 4849:  # Full Belur Math Bhog Plate — plate ~500g entered as 100g
        factor = 5.0
        for fld in MACRO_FIELDS:
            if fld in food:
                food[fld] = round(food[fld] / factor, 1)
        food['s'] = '500g'
        changes.append('ID:4849 plate normalization /5 (assumed 500g serving)')
        continue

    if bid == 4488:  # Full Darshini Combo Meal — "1 plate" ~500g
        factor = 5.0
        for fld in MACRO_FIELDS:
            if fld in food:
                food[fld] = round(food[fld] / factor, 1)
        food['s'] = '500g'
        changes.append('ID:4488 plate normalization /5 (assumed 500g serving, s was "1 plate")')
        continue

    # General case: s > 100g means values are per serving
    if sg and sg > 100:
        factor = sg / 100.0
        old_c = food.get('c', 0)
        old_k = food.get('k', 0)
        for fld in MACRO_FIELDS:
            if fld in food:
                food[fld] = round(food[fld] / factor, 1)
        changes.append('ID:' + str(bid) + ' per-serving norm /' + str(round(factor,2)) + ' | k:' + str(old_k) + '->' + str(food.get('k')) + ' c:' + str(old_c) + '->' + str(food.get('c')) + ' | ' + food.get('en','').encode('ascii','replace').decode())
    else:
        print('WARNING: ID:' + str(bid) + ' c=' + str(c_val) + ' but s=' + str(s_raw) + ' (cannot auto-normalize)')

print('\n' + str(len(changes)) + ' items fixed:')
for ch in changes:
    print('  ' + ch)

with open('assets/data/food_master_v10.json', 'w', encoding='utf-8') as f:
    json.dump(foods, f, ensure_ascii=False, separators=(',', ':'))

print('\nDone. food_master_v10.json updated.')
