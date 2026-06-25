import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

reclassify = {"palong shaak bhaja", "pui shaak chorchori"}

with open('assets/data/food_master_v7_2.json', encoding='utf-8') as f:
    data = json.load(f)

changed = []
for item in data:
    if item.get('en', '').strip().lower() in reclassify and item.get('cat') != 'shaak':
        old = item['cat']
        item['cat'] = 'shaak'
        # add shaak keywords if not present
        kw = item.get('kw', [])
        for k in ['shaak', 'leafy', 'greens']:
            if k not in kw:
                kw.append(k)
        item['kw'] = kw
        changed.append(f"  {item['id']}  {item['en']}  [{old} -> shaak]")

with open('assets/data/food_master_v7_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

shaak_total = sum(1 for item in data if item.get('cat') == 'shaak')
print('Reclassified:')
for c in changed:
    print(c)
print(f'shaak total now: {shaak_total}')
