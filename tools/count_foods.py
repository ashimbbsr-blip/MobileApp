import json
from collections import Counter

with open('assets/data/food_master_v7_2.json', encoding='utf-8') as f:
    data = json.load(f)

cats = Counter(item.get('cat', 'unknown') for item in data)
print(f'Total items in database: {len(data)}')
print()
print('By category:')
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    print(f'  {cat:<18} {count}')
