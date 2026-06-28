import json, sys, re
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

with open('assets/data/food_master_v8_2.json', encoding='utf-8') as f:
    data = json.load(f)

cats = Counter(i.get('cat', '') for i in data)
new_items = [i for i in data if i['id'] >= 100039]

print(f'Total items     : {len(data)}')
print(f'New items added : {len(new_items)}')
print(f'Max ID          : {max(i["id"] for i in data)}')
print()
print('Categories breakdown:')
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f'  {cat:<25} {count}')

bad_bn = []
for i in new_items:
    bn = i.get('bn', '')
    non_bn = re.sub(r'[ঀ-৿\s\(\)\/\-\.,\'\"]', '', bn)
    if non_bn:
        bad_bn.append((i['id'], i['en'], bn, non_bn))
print(f'\nNew items with non-Bengali chars in bn: {len(bad_bn)}')
for id_, en, bn, bad in bad_bn[:15]:
    print(f'  id={id_} {en} | bn={bn} | bad={bad}')

with open('assets/data/search_index_v2.json', encoding='utf-8') as f:
    idx = json.load(f)
print(f'\nSearch index total_foods : {idx["total_foods"]}')
print(f'EN prefix tokens         : {len(idx["en_prefix"])}')
print(f'BN prefix tokens         : {len(idx["bn_prefix"])}')
print(f'Families                 : {len(idx["family_index"])}')
