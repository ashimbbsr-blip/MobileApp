import json
with open('assets/data/food_master_v7_2.json', encoding='utf-8') as f:
    data = json.load(f)
added = [item for item in data if item.get('id') in range(10001, 10026)]
print('New vegetable items added:')
for item in added:
    print(' ', item['id'], '-', item['en'])
