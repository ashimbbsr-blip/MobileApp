"""add_drinks_v8_4b.py — add 10 packaged mango/fruit drinks (Maaza, Slice)"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

DATASET = Path('assets/data/food_master_v8_2.json')

NEW_DRINKS = [
    {"en": "Maaza Mango",                       "bn": "মাজা ম্যাঙ্গো",                  "s": "100ml",  "k": 60,  "p": 0.3, "c": 15, "f": 0.1, "fi": 0.2, "so": 0.02},
    {"en": "Maaza Mango (Bottle)",               "bn": "মাজা ম্যাঙ্গো (বোতল)",           "s": "250ml",  "k": 150, "p": 0.8, "c": 37, "f": 0.3, "fi": 0.5, "so": 0.05},
    {"en": "Maaza Mango (Large Bottle)",         "bn": "মাজা ম্যাঙ্গো (বড় বোতল)",       "s": "600ml",  "k": 360, "p": 1.8, "c": 90, "f": 0.7, "fi": 1.0, "so": 0.12},
    {"en": "Slice Mango Drink",                  "bn": "স্লাইস ম্যাঙ্গো ড্রিংক",        "s": "100ml",  "k": 65,  "p": 0.2, "c": 16, "f": 0.1, "fi": 0.1, "so": 0.02},
    {"en": "Slice Mango (Bottle)",               "bn": "স্লাইস ম্যাঙ্গো (বোতল)",        "s": "250ml",  "k": 162, "p": 0.5, "c": 40, "f": 0.2, "fi": 0.3, "so": 0.05},
    {"en": "Slice Mango (Large Bottle)",         "bn": "স্লাইস ম্যাঙ্গো (বড় বোতল)",    "s": "600ml",  "k": 390, "p": 1.2, "c": 96, "f": 0.5, "fi": 0.8, "so": 0.12},
    {"en": "Maaza Guava",                        "bn": "মাজা গুয়াভা",                    "s": "100ml",  "k": 55,  "p": 0.2, "c": 13, "f": 0.1, "fi": 0.3, "so": 0.02},
    {"en": "Maaza Pineapple",                    "bn": "মাজা পাইনঅ্যাপল",                "s": "100ml",  "k": 58,  "p": 0.2, "c": 14, "f": 0.1, "fi": 0.2, "so": 0.02},
    {"en": "Maaza Mango No Sugar Added",         "bn": "মাজা ম্যাঙ্গো (নো সুগার)",      "s": "100ml",  "k": 35,  "p": 0.3, "c": 9,  "f": 0.1, "fi": 0.3, "so": 0.02},
    {"en": "Slice Mango Light (Low Sugar Variant)", "bn": "স্লাইস ম্যাঙ্গো লাইট",     "s": "100ml",  "k": 40,  "p": 0.2, "c": 10, "f": 0.1, "fi": 0.2, "so": 0.02},
]

KW_MAP = {
    'maaza':       ['maaza', 'coca cola brand', 'mango drink', 'fruit drink', 'packaged juice'],
    'slice':       ['slice', 'pepsico', 'mango drink', 'fruit drink', 'packaged juice'],
    'mango':       ['mango', 'aam', 'आम', 'আম'],
    'guava':       ['guava', 'peyara', 'আমরুদ'],
    'pineapple':   ['pineapple', 'ananas', 'আনারস'],
    'no sugar':    ['no sugar added', 'low sugar', 'diet'],
    'light':       ['light', 'low sugar', 'diet'],
    'bottle':      ['bottle', 'ready to drink', 'rtd'],
    'large bottle':['large bottle', '600ml', 'family pack'],
}

def make_kw(en: str) -> list:
    el = en.lower()
    kw = set()
    kw.update(['beverage', 'fruit drink', 'cold drink', 'soft drink'])
    for k, tags in KW_MAP.items():
        if k in el:
            kw.update(tags)
    return sorted(kw)


def main():
    data = json.loads(DATASET.read_text(encoding='utf-8'))
    before   = len(data)
    max_id   = max(item['id'] for item in data)
    next_id  = max_id + 1
    existing = {item['en'].strip().lower() for item in data}

    added = skipped = 0
    for raw in NEW_DRINKS:
        key = raw['en'].strip().lower()
        if key in existing:
            print(f"  SKIP (dup): {raw['en']}")
            skipped += 1
            continue
        item = {
            'id':            next_id,
            'en':            raw['en'],
            'bn':            raw['bn'],
            'cat':           'beverage',
            's':             raw['s'],
            'k':             raw['k'],
            'p':             raw['p'],
            'c':             raw['c'],
            'f':             raw['f'],
            'fi':            raw['fi'],
            'sod':           round(raw['so'] * 1000),
            'src':           'user_curated',
            'quality_score': 72,
            'kw':            make_kw(raw['en']),
        }
        data.append(item)
        existing.add(key)
        print(f"  ADD id={next_id}: {raw['en']}")
        next_id += 1
        added += 1

    print(f"\nBefore: {before}  Added: {added}  Skipped: {skipped}  After: {len(data)}")
    DATASET.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Saved → {DATASET}")


if __name__ == '__main__':
    main()
