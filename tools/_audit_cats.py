import json, collections, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('assets/data/food_master_v9_0.json', encoding='utf-8'))
cats = collections.Counter(d.get('cat','') for d in data)
ui_cats = {'rice','bread','bakery','vegetable','shaak','legume','fish','meat','egg',
           'dairy','fruit','juice','snack','sweet','beverage','soup','breakfast',
           'grain','salad','noodle','pizza','restaurant_food','other'}
print("All cats in dataset:")
for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
    flag = '' if cat in ui_cats else '  <<< NOT IN UI'
    print(f"  {cat}: {count}{flag}")
# Also check for zero-calorie foods
zero = [d for d in data if d.get('k', 0) == 0]
print(f"\nZero-calorie items: {len(zero)}")
for d in zero[:5]:
    print(f"  {d['id']}: {d['en']}")
# Check blank bn
blank_bn = [d for d in data if not d.get('bn','').strip()]
print(f"Blank BN fields: {len(blank_bn)}")
for d in blank_bn[:5]:
    print(f"  {d['id']}: {d['en']}")
