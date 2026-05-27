"""
Patch BD FCT fat/oil items: two systematic bugs
  Bug A: energy stored in kJ instead of kcal
  Bug B: protein (p) and fat (f) fields are swapped

All corrected values sourced from USDA FoodData Central.
"""
import json, sys, shutil, os
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

MASTER = os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'food_master_v5_3.json')

# USDA-sourced correct values per 100g
# k=kcal, p=protein(g), c=carbs(g), f=fat(g)
PATCHES = {
    1368: {"k": 717.0, "p": 0.9,  "c": 0.1, "f": 81.1},   # Butter, salted
    1369: {"k": 884.0, "p": 0.0,  "c": 0.0, "f": 100.0},  # Cottonseed oil
    1370: {"k": 902.0, "p": 0.0,  "c": 0.0, "f": 100.0},  # Fish oil, cod liver
    1371: {"k": 900.0, "p": 0.3,  "c": 0.0, "f": 99.5},   # Ghee, cow
    1372: {"k": 900.0, "p": 0.0,  "c": 0.0, "f": 100.0},  # Ghee, vegetable (vanaspati)
    1373: {"k": 718.0, "p": 0.2,  "c": 0.2, "f": 80.4},   # Margarine
    1374: {"k": 680.0, "p": 1.1,  "c": 0.6, "f": 74.9},   # Mayonnaise, salted
    1375: {"k": 884.0, "p": 0.0,  "c": 0.0, "f": 100.0},  # Mustard oil
    1376: {"k": 884.0, "p": 0.0,  "c": 0.0, "f": 100.0},  # Palm oil
    1377: {"k": 884.0, "p": 0.0,  "c": 0.0, "f": 100.0},  # Peanut oil
    1378: {"k": 884.0, "p": 0.0,  "c": 0.0, "f": 100.0},  # Sesame oil
    1379: {"k": 884.0, "p": 0.0,  "c": 0.0, "f": 100.0},  # Soybean oil
}

def main():
    # Backup
    backup = MASTER + f'.bak.{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    shutil.copy2(MASTER, backup)
    print(f'Backup → {backup}')

    with open(MASTER, encoding='utf-8') as f:
        data = json.load(f)

    by_id = {d['id']: d for d in data}
    patched = 0

    for food_id, fix in PATCHES.items():
        item = by_id.get(food_id)
        if item is None:
            print(f'  WARNING: id={food_id} not found — skipped')
            continue

        print(f'\n  [{food_id}] {item["en"]}')
        for field, new_val in fix.items():
            old_val = item.get(field, 'MISSING')
            item[field] = new_val
            print(f'    {field}: {old_val}  →  {new_val}')
        patched += 1

    with open(MASTER, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    print(f'\nPatched {patched}/{len(PATCHES)} items. Saved to {MASTER}')

    # Quick verification
    print('\n--- Verification ---')
    with open(MASTER, encoding='utf-8') as f:
        check = json.load(f)
    by_id2 = {d['id']: d for d in check}
    for food_id in PATCHES:
        d = by_id2.get(food_id, {})
        calc = d.get('p',0)*4 + d.get('c',0)*4 + d.get('f',0)*9
        diff = abs(calc - d.get('k',0))
        status = 'OK' if diff < 50 else 'MISMATCH'
        print(f'  [{status}] id={food_id} {d.get("en","")[:35]:<35} k={d.get("k")} calc={calc:.0f} diff={diff:.0f}')

if __name__ == '__main__':
    main()
