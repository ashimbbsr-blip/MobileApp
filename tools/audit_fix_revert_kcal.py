"""
audit_fix_revert_kcal.py — Revert kcal changes where audit_fix.py INCREASED the value.

For soups and pulaos, the stored kcal was in a plausible range (~70-870)
but the macros were inflated per-serving, causing calc > stored.
Recalculating in that direction was wrong. Restore originals.
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

# Items where audit_fix.py INCREASED kcal (bad) — restore original stored values
REVERT_KCAL = {
    149:  121.3,   # Lentil soup (calc 621.5 was wrong — macros inflated)
    325:  108.3,   # Chicken consomme
    334:   68.5,   # Chicken sweet corn soup
    369:  364.7,   # Spaghetti bolognese (calc 610.8 too high)
    374:  375.2,   # Almond soup (calc 855.8 implausible)
    646:   84.6,   # Egg drop soup
    669:  723.2,   # Chicken pulao (both too high but revert to original)
    685:  866.5,   # Mutton pulao (same)
    996:  129.8,   # Curried Cauliflower soup
    1052: 163.9,   # Spinach soup
}

data = json.load(open(DATASET, encoding='utf-8'))
print(f'Loaded {len(data)} items')

reverted = 0
for item in data:
    if item['id'] in REVERT_KCAL:
        orig = REVERT_KCAL[item['id']]
        print(f'  REVERT [{item["id"]}] {item["en"]}: {item["k"]} → {orig}')
        item['k'] = orig
        reverted += 1

print(f'\nReverted: {reverted}')
with open(DATASET, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
print('Saved.')
