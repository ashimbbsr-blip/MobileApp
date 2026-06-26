"""
add_breads.py — Add Indian/international bread variants; remove duplicate sugarcane juice.

IDs 57001-57012 taken by restaurant items → reassigned to 57013-57020.
Sugarcane juice: keep 1385 (BD FCT, src=bd_fct, k=33 — matches USDA ~30 kcal/100ml),
                 remove 56001 (local estimate, k=58, duplicate BN name).
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

NEW_ITEMS = [
  {'id':57013,'en':'White Bread (India - Bakery Style)','bn':'সাদা ব্রেড (ভারতীয় বেকারি)','cat':'bread','s':'100g','k':265,'p':8.5,'c':49.0,'f':3.2,'fi':2.5,'ca':140,'fe':3.1,'src':'local'},
  {'id':57014,'en':'White Bread (Germany - Toastbrot)','bn':'জার্মান সাদা টোস্ট ব্রেড','cat':'bread','s':'100g','k':255,'p':7.5,'c':50.0,'f':3.0,'fi':2.2,'ca':120,'fe':2.8,'src':'local'},
  {'id':57015,'en':'Brown Bread (India - Wheat Bread)','bn':'ব্রাউন ব্রেড (ভারতীয়)','cat':'bread','s':'100g','k':247,'p':10.5,'c':41.0,'f':4.0,'fi':6.0,'ca':180,'fe':3.5,'src':'local'},
  {'id':57016,'en':'Whole Wheat Bread (Germany - Vollkornbrot)','bn':'জার্মান হোলগ্রেইন ব্রেড','cat':'bread','s':'100g','k':240,'p':10.8,'c':42.0,'f':3.5,'fi':8.0,'ca':160,'fe':3.8,'src':'local'},
  {'id':57017,'en':'White Bread (Indian Packaged)','bn':'প্যাকেটজাত সাদা ব্রেড','cat':'bread','s':'100g','k':270,'p':7.8,'c':51.0,'f':3.5,'fi':2.0,'ca':130,'fe':3.0,'src':'local'},
  {'id':57018,'en':'Brown Bread (Indian Packaged)','bn':'প্যাকেটজাত ব্রাউন ব্রেড','cat':'bread','s':'100g','k':250,'p':9.5,'c':43.0,'f':4.5,'fi':5.5,'ca':150,'fe':3.2,'src':'local'},
  {'id':57019,'en':'White Bread (EU Industrial Standard)','bn':'ইউরোপীয় সাদা ব্রেড','cat':'bread','s':'100g','k':260,'p':8.0,'c':49.5,'f':3.1,'fi':2.3,'ca':125,'fe':3.0,'src':'local'},
  {'id':57020,'en':'Brown Bread (EU Wholegrain Standard)','bn':'ইউরোপীয় হোলগ্রেইন ব্রেড','cat':'bread','s':'100g','k':238,'p':11.0,'c':40.0,'f':3.8,'fi':8.5,'ca':165,'fe':3.7,'src':'local'},
]

data = json.load(open(DATASET, encoding='utf-8'))
print(f'Loaded {len(data)} items')

# ── Remove duplicate sugarcane juice (local estimate) ─────────────────────────
before = len(data)
data = [d for d in data if d['id'] != 56001]
if len(data) < before:
    print('Removed [56001] Sugarcane Juice (local) — keeping [1385] Sugar cane juice (BD FCT, k=33)')

# Update kept entry: promote to juice category for chip visibility
for d in data:
    if d['id'] == 1385:
        d['cat'] = 'juice'
        d['en']  = 'Sugarcane Juice'
        print(f'Updated [1385]: cat→juice, en→"Sugarcane Juice"')
        break

# ── Add bread items ───────────────────────────────────────────────────────────
existing_ids = {d['id'] for d in data}
existing_en  = {d['en'].strip().lower() for d in data}

added, skipped = 0, 0
for item in NEW_ITEMS:
    name_key = item['en'].strip().lower()
    if item['id'] in existing_ids:
        print(f'  SKIP id-conflict ({item["id"]}): {item["en"]}')
        skipped += 1
        continue
    if name_key in existing_en:
        print(f'  SKIP name-dup: {item["en"]}')
        skipped += 1
        continue
    data.append(item)
    existing_ids.add(item['id'])
    existing_en.add(name_key)
    added += 1
    print(f'  Added [{item["id"]}]: {item["en"]}')

print(f'\nAdded: {added}  |  Skipped: {skipped}')
print(f'Total items: {len(data)}')

with open(DATASET, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print('Saved.')
