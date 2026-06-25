import json
with open('assets/data/food_master_v7_2.json', encoding='utf-8') as f:
    data = json.load(f)
mutton = [item for item in data if item.get('id') in range(3001, 3051)]
print('Mutton items found:', len(mutton))
meat_count = sum(1 for item in data if item.get('cat') == 'meat')
print('Total meat category items:', meat_count)
for item in mutton[:5]:
    print(' ', item['id'], item['cat'], item['en'])
print('  ...')
print(' ', mutton[-1]['id'], mutton[-1]['cat'], mutton[-1]['en'])
