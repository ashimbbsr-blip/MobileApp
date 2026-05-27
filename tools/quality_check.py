"""Quality check on bd_fct entries."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

MASTER = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v5_3.json'

with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)

bd_fct = [i for i in master if i.get('src') == 'bd_fct']
print(f"Total bd_fct items: {len(bd_fct)}")

# Check for items where Bengali = English (fallback to English)
no_bn = [(i['en'], i['bn']) for i in bd_fct if i['bn'] == i['en'] or not i['bn'] or len(i['bn']) < 3]
if no_bn:
    print(f"\nItems with missing/bad Bengali ({len(no_bn)}):")
    for en, bn in no_bn[:20]:
        print(f"  '{en}' / '{bn}'")

# Check for transliteration fallbacks (Latin script in bn field)
import re
latin_bn = [(i['en'], i['bn']) for i in bd_fct if re.search(r'[a-zA-Z]{3,}', i['bn'])]
if latin_bn:
    print(f"\nItems with Latin in Bengali ({len(latin_bn)}):")
    for en, bn in latin_bn[:30]:
        print(f"  '{en}' / '{bn}'")

# Show sample of good items by category
print("\nSample good items by category:")
cats = {}
for i in bd_fct:
    cats.setdefault(i['cat'], []).append(i)

for cat, items in sorted(cats.items()):
    print(f"\n  {cat.upper()} ({len(items)} items):")
    for item in items[:3]:
        print(f"    [{item['id']}] {item['en']} / {item['bn']} — {item['k']} kcal, p={item['p']}g, c={item['c']}g, f={item['f']}g")

print(f"\nOverall stats: {len(master)} total items")
