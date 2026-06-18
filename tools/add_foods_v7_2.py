"""
Add Dorade Royal (Gilt-head sea bream) and Carp to the dataset.

Sources:
  Dorade Royal:  Deutsche See GmbH label (macros); Ciqual/EUROFIR (minerals/vitamins)
  Carp:          FatSecret (macros); USDA FDC #174191 (minerals/vitamins)

Reads food_master_v7_1.json, saves food_master_v7_2.json and rebuilt indexes.
"""

import json, re, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from collections import defaultdict

ROOT     = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(ROOT, 'assets', 'data')
SRC      = os.path.join(DATA_DIR, 'food_master_v7_1.json')
DST      = os.path.join(DATA_DIR, 'food_master_v7_2.json')
IDX_EN   = os.path.join(DATA_DIR, 'index_en_v7_2.json')
IDX_BN   = os.path.join(DATA_DIR, 'index_bn_v7_2.json')

NEW_FOODS = [
    {
        # Macros: Deutsche See GmbH label (per 100g raw)
        # Minerals/vitamins: Ciqual French food database — sea bream (daurade)
        "id": 1477, "en": "Dorade Royal (Sea bream), raw", "bn": "ডোরাডে রয়্যাল মাছ",
        "s": "100g", "cat": "fish",
        "k": 121.0, "p": 18.3, "f": 5.3, "c": 0.0, "fi": 0.0,
        "ca": 14.0, "fe": 0.4, "zn": 0.5, "mg": 30.0, "pot": 370.0,
        "va": 10.0, "vc": 0.0, "vd": 5.0, "b12": 3.0,
        "kw": ["dorade", "dorade royal", "sea bream", "gilt-head", "gilt head bream",
               "sparus aurata", "marine", "saltwater", "oily fish", "european sea bream"],
        "src": "deutsche_see_ciqual",
    },
    {
        # Macros: FatSecret (per 100g raw, matches USDA FDC #174191)
        # Minerals/vitamins: USDA FDC #174191 Fish, carp, raw
        "id": 1478, "en": "Carp, raw", "bn": "কার্প মাছ",
        "s": "100g", "cat": "fish",
        "k": 127.0, "p": 17.8, "f": 5.6, "c": 0.0, "fi": 0.0,
        "ca": 41.0, "fe": 1.2, "zn": 1.5, "mg": 28.0, "pot": 333.0,
        "va": 12.0, "vc": 1.5, "vd": 0.4, "b12": 1.5,
        "kw": ["carp", "common carp", "freshwater", "cyprinidae", "river fish",
               "karper", "karpfen"],
        "src": "fatsecret_usda",
    },
]


def build_index(items, key, is_bn=False):
    index = defaultdict(set)
    for item in items:
        name = item.get(key, '')
        if not name:
            continue
        if is_bn:
            for word in name.split():
                w = word.strip()
                if len(w) >= 1:
                    index[w[:2]].add(item['id'])
        else:
            for word in re.findall(r'[a-z]+', name.lower()):
                if len(word) >= 2:
                    index[word[:2]].add(item['id'])
                if len(word) >= 3:
                    index[word[:3]].add(item['id'])
            for kw in item.get('kw', []):
                for word in re.findall(r'[a-z]+', kw.lower()):
                    if len(word) >= 2:
                        index[word[:2]].add(item['id'])
                    if len(word) >= 3:
                        index[word[:3]].add(item['id'])
    return {k: sorted(v) for k, v in index.items()}


def main():
    with open(SRC, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_ids = {item['id'] for item in data}
    existing_en  = {item['en'].lower() for item in data}

    added = 0
    skipped = 0
    for food in NEW_FOODS:
        if food['id'] in existing_ids:
            print(f"  ~ Skip (id exists):  {food['en']}")
            skipped += 1
        elif food['en'].lower() in existing_en:
            print(f"  ~ Skip (name exists): {food['en']}")
            skipped += 1
        else:
            data.append(food)
            existing_ids.add(food['id'])
            existing_en.add(food['en'].lower())
            added += 1
            print(f"  + Added: {food['en']}  (id={food['id']}, bn={food['bn']})")

    print(f"\nDataset: {len(data)} items total  (+{added} new, {skipped} skipped)")

    idx_en = build_index(data, 'en', is_bn=False)
    idx_bn = build_index(data, 'bn', is_bn=True)
    print(f"EN index: {len(idx_en)} buckets")
    print(f"BN index: {len(idx_bn)} buckets")

    with open(DST, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    with open(IDX_EN, 'w', encoding='utf-8') as f:
        json.dump(idx_en, f, ensure_ascii=False, separators=(',', ':'))
    with open(IDX_BN, 'w', encoding='utf-8') as f:
        json.dump(idx_bn, f, ensure_ascii=False, separators=(',', ':'))

    print("\nFiles written:")
    for path in [DST, IDX_EN, IDX_BN]:
        print(f"  {os.path.basename(path)}: {os.path.getsize(path):,} bytes")


if __name__ == '__main__':
    main()
