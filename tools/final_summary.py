"""Final summary of the dataset."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

MASTER = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v5_3.json'

with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)

bd = [i for i in master if i.get('src') == 'bd_fct']
orig = [i for i in master if i.get('src') != 'bd_fct']

print(f"=== Dataset Summary ===")
print(f"Original items:   {len(orig)}")
print(f"BD FCT items:     {len(bd)}")
print(f"Total:            {len(master)}")
print()

cats = {}
for i in bd:
    cats.setdefault(i['cat'], []).append(i)
print("BD FCT by category:")
for cat, items in sorted(cats.items()):
    print(f"  {cat:12} {len(items):3} items")

print()
print("Sample per category (first 2):")
for cat, items in sorted(cats.items()):
    print(f"\n  {cat.upper()}:")
    for item in items[:2]:
        print(f"    {item['en']}")
        print(f"    {item['bn']}")

# Check for remaining issues
import re
print("\n=== Remaining Issues ===")
issues = []
for i in bd:
    if re.search(r'[a-zA-Z]{3,}', i['bn']):
        if not re.search(r'SP\d|BR-|HYV|UTH|Diamond', i['bn']):
            issues.append(f"Latin in bn: '{i['en']}' / '{i['bn']}'")
    if len(i['bn']) < 2:
        issues.append(f"Short bn: '{i['en']}' / '{i['bn']}'")

if issues:
    for issue in issues:
        print(f"  {issue}")
else:
    print("  None!")
