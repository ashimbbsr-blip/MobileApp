"""
Add new fish (from ICMR seafoods PDF) and leafy vegetables (from IJCMAS 2020 PDF)
to the dataset. Reads food_master_v6_9.json, appends new items, saves as
food_master_v7_0.json and rebuilds indexes index_en_v7_0.json / index_bn_v7_0.json.

Sources:
  fish:       Gopalan et al. 2004, "Nutritive Value of Indian Foods", ICMR/NIN
  vegetables: IJCMAS 2020, "Nutritional contents of leafy vegetables" (Table 1, p.9)

VitA conversion for plant sources: IU × 0.3 = mcg RAE
"""

import json, re, os, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from collections import defaultdict

ROOT     = os.path.join(os.path.dirname(__file__), '..')
DATA_DIR = os.path.join(ROOT, 'assets', 'data')
SRC      = os.path.join(DATA_DIR, 'food_master_v6_9.json')
DST      = os.path.join(DATA_DIR, 'food_master_v7_0.json')
IDX_EN   = os.path.join(DATA_DIR, 'index_en_v7_0.json')
IDX_BN   = os.path.join(DATA_DIR, 'index_bn_v7_0.json')

# ---------------------------------------------------------------------------
# New entries — fish from ICMR (Gopalan 2004), per 100 g edible portion
# Columns used from PDF: Energy(kcal), Protein(g), Fat(g), Carbs(g),
#   Calcium(mg), Iron(mg).  B12/Zn/Mg/K filled from USDA typical values.
# ---------------------------------------------------------------------------
NEW_FISH = [
    {
        "id": 1449, "en": "Koi (Climbing perch), raw", "bn": "কই মাছ",
        "s": "100g", "cat": "fish",
        "k": 156.0, "p": 15.0, "f": 9.0, "c": 4.0, "fi": 0.0,
        "ca": 410.0, "fe": 1.0, "zn": 0.8, "mg": 25.0, "pot": 340.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 1.0,
        "kw": ["koi", "climbing perch", "anabas", "freshwater", "koi mach"],
        "src": "icmr_2004",
    },
    {
        "id": 1450, "en": "Chital, raw", "bn": "চিতল মাছ",
        "s": "100g", "cat": "fish",
        "k": 108.0, "p": 19.0, "f": 2.0, "c": 3.0, "fi": 0.0,
        "ca": 180.0, "fe": 3.0, "zn": 0.7, "mg": 26.0, "pot": 320.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 1.0,
        "kw": ["chital", "chitol", "featherback", "notopterus", "freshwater"],
        "src": "icmr_2004",
    },
    {
        "id": 1451, "en": "Puti, raw", "bn": "পুঁটি মাছ",
        "s": "100g", "cat": "fish",
        "k": 106.0, "p": 18.0, "f": 2.0, "c": 3.0, "fi": 0.0,
        "ca": 110.0, "fe": 1.0, "zn": 0.6, "mg": 22.0, "pot": 280.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 1.0,
        "kw": ["puti", "puthi", "small fish", "freshwater", "barb"],
        "src": "icmr_2004",
    },
    {
        "id": 1452, "en": "Tengra, fresh, raw", "bn": "টেংরা মাছ",
        "s": "100g", "cat": "fish",
        "k": 144.0, "p": 19.0, "f": 6.0, "c": 2.0, "fi": 0.0,
        "ca": 270.0, "fe": 2.0, "zn": 0.9, "mg": 27.0, "pot": 330.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 1.2,
        "kw": ["tengra", "tangra", "catfish", "mystus", "freshwater"],
        "src": "icmr_2004",
    },
    {
        "id": 1453, "en": "Mackerel, raw", "bn": "ম্যাকেরেল মাছ",
        "s": "100g", "cat": "fish",
        "k": 93.0, "p": 19.0, "f": 2.0, "c": 0.0, "fi": 0.0,
        "ca": 429.0, "fe": 4.0, "zn": 0.6, "mg": 30.0, "pot": 340.0,
        "va": 0.0, "vc": 0.0, "vd": 4.5, "b12": 9.0,
        "kw": ["mackerel", "bangda", "marine", "saltwater", "oily fish"],
        "src": "icmr_2004",
    },
    {
        "id": 1454, "en": "Seer fish (Surmai), raw", "bn": "সুরমাই মাছ",
        "s": "100g", "cat": "fish",
        "k": 126.0, "p": 22.0, "f": 4.0, "c": 0.0, "fi": 0.0,
        "ca": 71.0, "fe": 5.0, "zn": 0.5, "mg": 31.0, "pot": 380.0,
        "va": 0.0, "vc": 0.0, "vd": 2.0, "b12": 9.5,
        "kw": ["seer", "surmai", "king fish", "kingfish", "marine", "spanish mackerel"],
        "src": "icmr_2004",
    },
    {
        "id": 1455, "en": "Oil sardine, raw", "bn": "তেল সার্ডিন মাছ",
        "s": "100g", "cat": "fish",
        "k": 97.0, "p": 20.0, "f": 2.0, "c": 0.0, "fi": 0.0,
        "ca": 357.0, "fe": 6.0, "zn": 1.0, "mg": 28.0, "pot": 310.0,
        "va": 0.0, "vc": 0.0, "vd": 5.0, "b12": 8.0,
        "kw": ["sardine", "oil sardine", "mathi", "marine", "saltwater"],
        "src": "icmr_2004",
    },
    {
        "id": 1456, "en": "Sardine, raw", "bn": "সার্ডিন মাছ",
        "s": "100g", "cat": "fish",
        "k": 101.0, "p": 21.0, "f": 2.0, "c": 0.0, "fi": 0.0,
        "ca": 90.0, "fe": 2.0, "zn": 0.8, "mg": 26.0, "pot": 280.0,
        "va": 0.0, "vc": 0.0, "vd": 4.0, "b12": 7.0,
        "kw": ["sardine", "marine", "saltwater", "small fish"],
        "src": "icmr_2004",
    },
    {
        "id": 1457, "en": "Bombay duck, dried", "bn": "লইট্টা শুঁটকি",
        "s": "100g", "cat": "fish",
        "k": 293.0, "p": 62.0, "f": 4.0, "c": 2.0, "fi": 0.0,
        "ca": 1389.0, "fe": 19.0, "zn": 3.0, "mg": 95.0, "pot": 900.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 8.0,
        "kw": ["bombay duck", "loitta", "sutki", "dried fish", "bummalo"],
        "src": "icmr_2004",
    },
    {
        "id": 1458, "en": "Ribbon fish, raw", "bn": "চাঁদা মাছ",
        "s": "100g", "cat": "fish",
        "k": 104.0, "p": 18.0, "f": 3.0, "c": 1.0, "fi": 0.0,
        "ca": 214.0, "fe": 14.0, "zn": 0.5, "mg": 27.0, "pot": 295.0,
        "va": 0.0, "vc": 0.0, "vd": 1.0, "b12": 3.0,
        "kw": ["ribbon fish", "chanda", "beltfish", "hairtail", "marine"],
        "src": "icmr_2004",
    },
    {
        "id": 1459, "en": "Pomfret, white, raw", "bn": "সাদা পমফ্রেট",
        "s": "100g", "cat": "fish",
        "k": 87.0, "p": 17.0, "f": 1.0, "c": 2.0, "fi": 0.0,
        "ca": 200.0, "fe": 1.0, "zn": 0.6, "mg": 24.0, "pot": 300.0,
        "va": 0.0, "vc": 0.0, "vd": 2.0, "b12": 1.5,
        "kw": ["pomfret", "white pomfret", "marine", "saltwater", "pamplet"],
        "src": "icmr_2004",
    },
    {
        "id": 1460, "en": "Lobster, raw", "bn": "লবস্টার",
        "s": "100g", "cat": "fish",
        "k": 90.0, "p": 20.0, "f": 1.0, "c": 0.0, "fi": 0.0,
        "ca": 16.0, "fe": 0.0, "zn": 2.9, "mg": 26.0, "pot": 352.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 1.5,
        "kw": ["lobster", "seafood", "shellfish", "marine", "crustacean"],
        "src": "icmr_2004",
    },
    {
        "id": 1461, "en": "Crab, raw", "bn": "কাঁকড়া",
        "s": "100g", "cat": "fish",
        "k": 59.0, "p": 9.0, "f": 1.0, "c": 3.0, "fi": 0.0,
        "ca": 1370.0, "fe": 21.0, "zn": 3.8, "mg": 34.0, "pot": 265.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 9.8,
        "kw": ["crab", "seafood", "shellfish", "marine", "kankra"],
        "src": "icmr_2004",
    },
    {
        "id": 1462, "en": "Mullet, raw", "bn": "মুলেট মাছ",
        "s": "100g", "cat": "fish",
        "k": 155.0, "p": 19.0, "f": 8.0, "c": 2.0, "fi": 0.0,
        "ca": 357.0, "fe": 4.0, "zn": 0.5, "mg": 28.0, "pot": 335.0,
        "va": 0.0, "vc": 0.0, "vd": 2.0, "b12": 1.0,
        "kw": ["mullet", "boi", "grey mullet", "marine", "coastal"],
        "src": "icmr_2004",
    },
    {
        "id": 1463, "en": "Herring, Indian, raw", "bn": "ভারতীয় হেরিং মাছ",
        "s": "100g", "cat": "fish",
        "k": 119.0, "p": 20.0, "f": 3.0, "c": 2.0, "fi": 0.0,
        "ca": 429.0, "fe": 9.0, "zn": 0.9, "mg": 29.0, "pot": 285.0,
        "va": 0.0, "vc": 0.0, "vd": 4.0, "b12": 13.7,
        "kw": ["herring", "indian herring", "marine", "saltwater", "oily fish"],
        "src": "icmr_2004",
    },
    {
        "id": 1464, "en": "Shark, raw", "bn": "হাঙর মাছ",
        "s": "100g", "cat": "fish",
        "k": 93.0, "p": 22.0, "f": 0.0, "c": 1.0, "fi": 0.0,
        "ca": 357.0, "fe": 1.0, "zn": 0.4, "mg": 30.0, "pot": 360.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 3.2,
        "kw": ["shark", "hangor", "marine", "saltwater"],
        "src": "icmr_2004",
    },
    {
        "id": 1465, "en": "Sole, raw", "bn": "সোল মাছ",
        "s": "100g", "cat": "fish",
        "k": 94.0, "p": 16.0, "f": 2.0, "c": 2.0, "fi": 0.0,
        "ca": 140.0, "fe": 0.0, "zn": 0.3, "mg": 22.0, "pot": 280.0,
        "va": 0.0, "vc": 0.0, "vd": 1.0, "b12": 1.5,
        "kw": ["sole", "flatfish", "marine", "saltwater"],
        "src": "icmr_2004",
    },
    {
        "id": 1466, "en": "Bam (Eel), raw", "bn": "বাম মাছ",
        "s": "100g", "cat": "fish",
        "k": 100.0, "p": 16.0, "f": 1.0, "c": 7.0, "fi": 0.0,
        "ca": 330.0, "fe": 1.0, "zn": 0.9, "mg": 26.0, "pot": 300.0,
        "va": 0.0, "vc": 0.0, "vd": 2.0, "b12": 3.0,
        "kw": ["bam", "eel", "freshwater", "bam mach"],
        "src": "icmr_2004",
    },
    {
        "id": 1467, "en": "Lata, raw", "bn": "লাটা মাছ",
        "s": "100g", "cat": "fish",
        "k": 97.0, "p": 19.0, "f": 1.0, "c": 3.0, "fi": 0.0,
        "ca": 610.0, "fe": 3.0, "zn": 0.7, "mg": 24.0, "pot": 320.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 1.0,
        "kw": ["lata", "freshwater", "snakehead"],
        "src": "icmr_2004",
    },
    {
        "id": 1468, "en": "Ghol, raw", "bn": "ঘোল মাছ",
        "s": "100g", "cat": "fish",
        "k": 82.0, "p": 18.0, "f": 1.0, "c": 0.0, "fi": 0.0,
        "ca": 90.0, "fe": 2.0, "zn": 0.5, "mg": 25.0, "pot": 310.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 1.0,
        "kw": ["ghol", "croaker", "marine", "jeera mach"],
        "src": "icmr_2004",
    },
    {
        "id": 1469, "en": "Ray, raw", "bn": "রেই মাছ",
        "s": "100g", "cat": "fish",
        "k": 97.0, "p": 21.0, "f": 0.0, "c": 2.0, "fi": 0.0,
        "ca": 214.0, "fe": 5.0, "zn": 0.4, "mg": 28.0, "pot": 295.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 4.0,
        "kw": ["ray", "skate", "marine", "stingray"],
        "src": "icmr_2004",
    },
    {
        "id": 1470, "en": "Ravas (Indian salmon), raw", "bn": "রাভাস মাছ",
        "s": "100g", "cat": "fish",
        "k": 112.0, "p": 22.0, "f": 1.0, "c": 3.0, "fi": 0.0,
        "ca": 405.0, "fe": 2.0, "zn": 0.6, "mg": 30.0, "pot": 380.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 3.0,
        "kw": ["ravas", "indian salmon", "rawas", "marine", "saltwater"],
        "src": "icmr_2004",
    },
    {
        "id": 1471, "en": "Silver belly, raw", "bn": "সিলভার বেলি মাছ",
        "s": "100g", "cat": "fish",
        "k": 91.0, "p": 19.0, "f": 2.0, "c": 0.0, "fi": 0.0,
        "ca": 715.0, "fe": 2.0, "zn": 0.5, "mg": 24.0, "pot": 285.0,
        "va": 0.0, "vc": 0.0, "vd": 0.0, "b12": 2.0,
        "kw": ["silver belly", "marine", "saltwater"],
        "src": "icmr_2004",
    },
]

# ---------------------------------------------------------------------------
# New entries — leafy vegetables from IJCMAS 2020 (Table 1, p.9), per 100 g
# VitA (IU → mcg RAE): plant source × 0.3
# ---------------------------------------------------------------------------
NEW_VEGETABLES = [
    {
        "id": 1472,
        "en": "Curry leaf, raw",
        "bn": "কারি পাতা",
        "s": "100g", "cat": "vegetable",
        # E=108, P=6.1, F=1.0, C=18.7, VitA=600IU→180mcg, VitC=4, Ca=830, Fe=0.93
        "k": 108.0, "p": 6.1, "f": 1.0, "c": 18.7, "fi": 6.4,
        "ca": 830.0, "fe": 0.93, "zn": 0.1, "mg": 44.0, "pot": 500.0,
        "va": 180.0, "vc": 4.0, "vd": 0.0, "b12": 0.0,
        "kw": ["curry leaf", "kari pata", "meetha neem", "murraya", "herb"],
        "src": "ijcmas_2020",
    },
    {
        "id": 1473,
        "en": "Purslane, raw",
        "bn": "নুনিয়া শাক",
        "s": "100g", "cat": "vegetable",
        # E=16, P=1.3, F=0.1, C=3.4, VitA=1320IU→396mcg, VitC=21, Ca=65, Fe=2.0, K=494
        "k": 16.0, "p": 1.3, "f": 0.1, "c": 3.4, "fi": 0.5,
        "ca": 65.0, "fe": 2.0, "zn": 0.2, "mg": 68.0, "pot": 494.0,
        "va": 396.0, "vc": 21.0, "vd": 0.0, "b12": 0.0,
        "kw": ["purslane", "nunia", "portulaca", "nuniya shak", "succulent"],
        "src": "ijcmas_2020",
    },
    {
        "id": 1474,
        "en": "Sweet leaf bush (Chekkurmanis), raw",
        "bn": "মধু শাক",
        "s": "100g", "cat": "vegetable",
        # E=103, P=6.8, F=3.2, C=11.6, VitA=5706IU→1712mcg, VitC=247, Ca=570, Fe=28
        "k": 103.0, "p": 6.8, "f": 3.2, "c": 11.6, "fi": 3.8,
        "ca": 570.0, "fe": 28.0, "zn": 0.5, "mg": 45.0, "pot": 420.0,
        "va": 1712.0, "vc": 247.0, "vd": 0.0, "b12": 0.0,
        "kw": ["chekkurmanis", "sweet leaf", "sauropus", "madhu shak", "leafy"],
        "src": "ijcmas_2020",
    },
    {
        "id": 1475,
        "en": "Ceylon spinach, raw",
        "bn": "বিলাতি পালং শাক",
        "s": "100g", "cat": "vegetable",
        # E=44, P=2.6, F=4.8, C=2.1, VitA=265IU→80mcg, VitC=49
        "k": 44.0, "p": 2.6, "f": 4.8, "c": 2.1, "fi": 1.5,
        "ca": 85.0, "fe": 1.5, "zn": 0.2, "mg": 36.0, "pot": 280.0,
        "va": 80.0, "vc": 49.0, "vd": 0.0, "b12": 0.0,
        "kw": ["ceylon spinach", "bilati palang", "spinach", "leafy green"],
        "src": "ijcmas_2020",
    },
    {
        "id": 1476,
        "en": "Ponnankanni (Alternanthera), raw",
        "bn": "পোন্নাকান্নি শাক",
        "s": "100g", "cat": "vegetable",
        # E=251, P=4.7, F=0.8, C=11.8, VitA=192IU→58mcg, VitC=17, Ca=146, Fe=60
        "k": 251.0, "p": 4.7, "f": 0.8, "c": 11.8, "fi": 2.5,
        "ca": 146.0, "fe": 60.0, "zn": 0.3, "mg": 40.0, "pot": 350.0,
        "va": 58.0, "vc": 17.0, "vd": 0.0, "b12": 0.0,
        "kw": ["ponnankanni", "alternanthera", "water amaranth", "sessilis", "leafy"],
        "src": "ijcmas_2020",
    },
]

NEW_FOODS = NEW_FISH + NEW_VEGETABLES


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
            # also index keywords
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

    existing_ids  = {item['id'] for item in data}
    existing_en   = {item['en'].lower() for item in data}

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
