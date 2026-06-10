"""
Add Maggi 2-Minute Noodles, Pani Puri, Sev Puri, Dahi Puri to dataset.
Reads food_master_v6_9.json, appends new items, rebuilds EN/BN indexes.
Output: food_master_v6_9.json updated in place + refreshed indexes.
"""

import json, re, os
from collections import defaultdict

ROOT      = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR  = os.path.join(ROOT, 'assets', 'data')
MASTER    = os.path.join(DATA_DIR, 'food_master_v6_9.json')
IDX_EN    = os.path.join(DATA_DIR, 'index_en_v6_9.json')
IDX_BN    = os.path.join(DATA_DIR, 'index_bn_v6_9.json')

NEW_FOODS = [
    {
        "id": 1445,
        "en": "Maggi 2 Minute Noodles",
        "bn": "ম্যাগি ২ মিনিট নুডলস",
        "s": "100g",
        "k": 384.0, "p": 8.2, "c": 59.6, "f": 12.5, "fi": 2.0,
        "ca": 15.0, "fe": 1.8, "zn": 0.5,
        "mg": 20.0, "pot": 120.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0,
        "cat": "noodle",
        "kw": ["maggi", "instant", "noodle", "masala", "packet"],
        "src": "maggi_in",
    },
    {
        "id": 1446,
        "en": "Pani Puri",
        "bn": "পানি পুরি",
        "s": "100g",
        "k": 307.0, "p": 5.3, "c": 46.2, "f": 11.2, "fi": 2.5,
        "ca": 25.0, "fe": 2.0, "zn": 0.4,
        "mg": 18.0, "pot": 130.0,
        "va": 0.0, "vc": 2.0, "vd": 0.0,
        "cat": "snack",
        "kw": ["pani", "puri", "golgappa", "snack", "street", "chaat"],
        "src": "fatsecret_in",
    },
    {
        "id": 1447,
        "en": "Sev Puri",
        "bn": "সেভ পুরি",
        "s": "100g",
        "k": 295.0, "p": 8.7, "c": 39.7, "f": 11.3, "fi": 2.5,
        "ca": 30.0, "fe": 1.5, "zn": 0.5,
        "mg": 22.0, "pot": 180.0,
        "va": 0.0, "vc": 3.0, "vd": 0.0,
        "cat": "snack",
        "kw": ["sev", "puri", "snack", "street", "chaat"],
        "src": "fatsecret_in",
    },
    {
        "id": 1448,
        "en": "Dahi Puri",
        "bn": "দহি পুরি",
        "s": "100g",
        "k": 204.0, "p": 3.4, "c": 18.0, "f": 13.3, "fi": 1.5,
        "ca": 80.0, "fe": 0.8, "zn": 0.4,
        "mg": 15.0, "pot": 150.0,
        "va": 30.0, "vc": 2.0, "vd": 0.1,
        "cat": "snack",
        "kw": ["dahi", "puri", "yogurt", "snack", "street", "chaat"],
        "src": "fatsecret_in",
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
    return {k: sorted(v) for k, v in index.items()}


def main():
    with open(MASTER, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_ids = {item['id'] for item in data}
    added = 0
    for food in NEW_FOODS:
        if food['id'] not in existing_ids:
            data.append(food)
            added += 1
            print(f"  + Added: {food['en']} (id={food['id']})")
        else:
            print(f"  ~ Skipped (already exists): {food['en']} (id={food['id']})")

    print(f"\nDataset: {len(data)} items total (+{added} new)")

    idx_en = build_index(data, 'en', is_bn=False)
    idx_bn = build_index(data, 'bn', is_bn=True)
    print(f"EN index: {len(idx_en)} buckets")
    print(f"BN index: {len(idx_bn)} buckets")

    with open(MASTER, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
    with open(IDX_EN, 'w', encoding='utf-8') as f:
        json.dump(idx_en, f, ensure_ascii=False, separators=(',', ':'))
    with open(IDX_BN, 'w', encoding='utf-8') as f:
        json.dump(idx_bn, f, ensure_ascii=False, separators=(',', ':'))

    print("\nFiles written:")
    for path in [MASTER, IDX_EN, IDX_BN]:
        print(f"  {os.path.basename(path)}: {os.path.getsize(path):,} bytes")


if __name__ == '__main__':
    main()
