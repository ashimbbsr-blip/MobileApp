"""Final targeted patches for remaining issues in bd_fct entries."""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

MASTER   = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v5_3.json'
INDEX_EN = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_en_v5_3.json'
INDEX_BN = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_bn_v5_3.json'

# (current_en, new_en, new_bn)  — '' means keep existing
PATCHES = [
    # English name cleanup (transliterations still appended)
    ('Apple, without skin, raw Apel, khosa',    'Apple, without skin, raw',      'আপেল, খোসা ছাড়া'),
    ('Apple, with skin, raw Apel, khosa',        'Apple, with skin, raw',          'আপেল, খোসাসহ'),
    ('Cottonseed oil Tular bij',                 'Cottonseed oil',                 'তুলার বিচির তেল'),
    ('Fish oil, cod liver Kod liver',            'Fish oil, cod liver',            'কড লিভার তেল'),
    # Fix Latin in Bengali name
    ('Pear millet, whole-grain, raw',            '',                               'বাজরা, গোটা শস্য'),
    ('Indian spinach, boiled* (without salt)',   '',                               'পুঁই শাক সিদ্ধ'),
    ('Prawn, Monsoon river prawn, raw',          '',                               'চিংড়ি, বর্ষার নদীর'),
    ('Shrimp, Speckled, raw',                    '',                               'চিংড়ি, ছোট'),
    ('Spotted snakehead, raw',                   'Spotted snakehead, raw',         'টাকি মাছ'),
    # Remove garbled entry "Chira,"
    ('Chira,',                                   None,                             ''),
]

with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)

kept = []
patched = 0
removed = 0
existing_en = {item['en'].lower().strip() for item in master}

for item in master:
    if item.get('src') != 'bd_fct':
        kept.append(item)
        continue

    en = item['en']
    match = next((p for p in PATCHES if p[0] == en), None)
    if match:
        _, new_en, new_bn = match
        if new_en is None:
            # Remove
            removed += 1
            print(f"  REMOVE: '{en}'")
            continue
        if new_en and new_en != en:
            # Check for duplicate
            if new_en.lower().strip() in existing_en and new_en.lower().strip() != en.lower().strip():
                removed += 1
                print(f"  DUP REMOVE: '{en}' -> '{new_en}'")
                continue
            existing_en.discard(en.lower().strip())
            existing_en.add(new_en.lower().strip())
            item['en'] = new_en
        if new_bn:
            item['bn'] = new_bn
        patched += 1
        print(f"  PATCH: '{en}' -> '{item['en']}' / '{item['bn']}'")

    kept.append(item)

print(f"\nPatched: {patched}, Removed: {removed}, Total: {len(kept)}")
print(f"bd_fct: {sum(1 for i in kept if i.get('src')=='bd_fct')}")

new_index_en = sorted(
    [{'id': it['id'], 'en': it['en'], 'bn': it['bn'], 'k': it['k']} for it in kept],
    key=lambda x: x['en'].lower()
)
new_index_bn = sorted(
    [{'id': it['id'], 'en': it['en'], 'bn': it['bn'], 'k': it['k']} for it in kept],
    key=lambda x: x['bn']
)

with open(MASTER, 'w', encoding='utf-8') as f:
    json.dump(kept, f, ensure_ascii=False, separators=(',', ':'))
with open(INDEX_EN, 'w', encoding='utf-8') as f:
    json.dump(new_index_en, f, ensure_ascii=False, separators=(',', ':'))
with open(INDEX_BN, 'w', encoding='utf-8') as f:
    json.dump(new_index_bn, f, ensure_ascii=False, separators=(',', ':'))
print("Files updated.")
