"""
add_seafood_duck_v8_6.py
Add: Snail curries (4), Squid/Octopus/Cuttlefish (9),
     Crab/Lobster/Mussels (14), Salmon/Tuna/Cod/Mackerel (12), Duck (8) = 47 items
"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

DATASET = Path('assets/data/food_master_v8_2.json')

SNAILS = [
    {"en": "Indian Spicy Snail Curry",            "bn": "ভারতীয় শামুক কারি",                 "s": "1 bowl (~250g)", "k": 240, "p": 18, "c": 12, "f": 14, "fi": 3, "so": 1.6, "kw": ["snail", "shamuk", "শামুক", "snail curry", "indian curry", "exotic seafood"]},
    {"en": "Bengali Mustard Snail Curry",          "bn": "শুঁটকি শামুক সর্ষে কারি",           "s": "1 bowl (~250g)", "k": 260, "p": 17, "c": 10, "f": 18, "fi": 2, "so": 2.0, "kw": ["snail", "bengali snail", "mustard snail", "shamuk", "শামুক", "sorse shamuk"]},
    {"en": "South Indian Pepper Snail Fry",        "bn": "সাউথ ইন্ডিয়ান পিপার শামুক ফ্রাই",  "s": "1 serving (~200g)", "k": 220, "p": 19, "c": 8, "f": 12, "fi": 2, "so": 1.4, "kw": ["snail fry", "pepper snail", "south indian snail", "shamuk", "exotic seafood"]},
    {"en": "Coconut Snail Curry",                  "bn": "নারকেল শামুক কারি",                  "s": "1 bowl (~250g)", "k": 310, "p": 16, "c": 14, "f": 22, "fi": 3, "so": 1.8, "kw": ["coconut snail", "snail curry", "shamuk", "শামুক", "coconut curry", "coastal"]},
]

CEPHALOPODS = [
    {"en": "Squid (Raw)",                          "bn": "স্কুইড (কাঁচা)",                     "s": "100g", "k": 92,  "p": 15.6,"c": 3.1, "f": 1.4, "fi": 0,  "so": 0.4, "kw": ["squid", "calamari", "seafood", "raw squid"]},
    {"en": "Squid Fry (Indian Style)",             "bn": "স্কুইড ফ্রাই",                       "s": "100g", "k": 210, "p": 16,  "c": 10,  "f": 12,  "fi": 1,  "so": 1.5, "kw": ["squid fry", "fried squid", "calamari", "indian squid", "seafood"]},
    {"en": "Squid Curry (Spicy)",                  "bn": "স্কুইড কারি",                         "s": "100g", "k": 180, "p": 14,  "c": 8,   "f": 10,  "fi": 1,  "so": 1.6, "kw": ["squid curry", "spicy squid", "calamari curry", "seafood", "indian curry"]},
    {"en": "Octopus (Raw)",                        "bn": "অক্টোপাস (কাঁচা)",                   "s": "100g", "k": 82,  "p": 14.9,"c": 2.2, "f": 1.0, "fi": 0,  "so": 0.4, "kw": ["octopus", "raw octopus", "seafood", "exotic seafood"]},
    {"en": "Grilled Octopus",                      "bn": "গ্রিলড অক্টোপাস",                    "s": "100g", "k": 160, "p": 25,  "c": 4,   "f": 5,   "fi": 0,  "so": 1.2, "kw": ["grilled octopus", "octopus", "seafood", "mediterranean", "high protein"]},
    {"en": "Octopus Curry (Indian Style)",         "bn": "অক্টোপাস কারি",                       "s": "100g", "k": 190, "p": 18,  "c": 6,   "f": 11,  "fi": 1,  "so": 1.7, "kw": ["octopus curry", "indian octopus", "seafood curry", "exotic seafood"]},
    {"en": "Cuttlefish (Raw)",                     "bn": "কাটলফিশ (কাঁচা)",                    "s": "100g", "k": 85,  "p": 16.2,"c": 2.0, "f": 0.7, "fi": 0,  "so": 0.3, "kw": ["cuttlefish", "raw cuttlefish", "seafood", "koika", "cephalopod"]},
    {"en": "Cuttlefish Curry (South Indian Style)","bn": "কাটলফিশ কারি",                        "s": "100g", "k": 200, "p": 17,  "c": 7,   "f": 12,  "fi": 1,  "so": 1.8, "kw": ["cuttlefish curry", "south indian cuttlefish", "seafood curry"]},
    {"en": "Cuttlefish Fry (Garlic Pepper)",       "bn": "কাটলফিশ ফ্রাই",                      "s": "100g", "k": 220, "p": 18,  "c": 9,   "f": 13,  "fi": 1,  "so": 1.6, "kw": ["cuttlefish fry", "garlic pepper cuttlefish", "seafood fry", "cuttlefish"]},
]

SHELLFISH = [
    {"en": "Crab (Raw Meat)",                      "bn": "কাঁকড়া (কাঁচা মাংস)",               "s": "100g", "k": 97,  "p": 19,  "c": 0,   "f": 1.5, "fi": 0,  "so": 0.8, "kw": ["crab", "kakra", "কাঁকড়া", "raw crab", "seafood", "shellfish"]},
    {"en": "Indian Crab Curry (Spicy Masala)",     "bn": "ভারতীয় কাঁকড়া কারি",               "s": "100g", "k": 180, "p": 17,  "c": 6,   "f": 11,  "fi": 1,  "so": 1.8, "kw": ["crab curry", "indian crab", "kakra curry", "কাঁকড়া কারি", "seafood curry"]},
    {"en": "Bengali Crab Curry (Mustard Style)",   "bn": "বাঙালি কাঁকড়া সর্ষে কারি",          "s": "100g", "k": 210, "p": 18,  "c": 5,   "f": 14,  "fi": 1,  "so": 2.0, "kw": ["bengali crab", "mustard crab", "sorse kakra", "কাঁকড়া সর্ষে", "bengali seafood"]},
    {"en": "European Garlic Butter Crab",          "bn": "ইউরোপিয়ান গার্লিক বাটার কাঁকড়া",   "s": "100g", "k": 230, "p": 18,  "c": 3,   "f": 16,  "fi": 0,  "so": 1.5, "kw": ["garlic butter crab", "european crab", "crab", "butter crab", "continental"]},
    {"en": "Steamed Crab (Plain)",                 "bn": "স্টিমড কাঁকড়া",                      "s": "100g", "k": 110, "p": 20,  "c": 0,   "f": 2,   "fi": 0,  "so": 0.9, "kw": ["steamed crab", "plain crab", "crab", "seafood", "low fat"]},
    {"en": "Lobster (Raw Meat)",                   "bn": "লবস্টার (কাঁচা মাংস)",               "s": "100g", "k": 89,  "p": 19,  "c": 0.5, "f": 0.9, "fi": 0,  "so": 0.8, "kw": ["lobster", "raw lobster", "seafood", "shellfish", "luxury seafood"]},
    {"en": "Butter Garlic Lobster (European Style)","bn": "বাটার গার্লিক লবস্টার",              "s": "100g", "k": 220, "p": 18,  "c": 4,   "f": 15,  "fi": 0,  "so": 1.4, "kw": ["butter garlic lobster", "lobster", "european lobster", "continental", "luxury"]},
    {"en": "Indian Lobster Curry (Masala)",        "bn": "ভারতীয় লবস্টার কারি",               "s": "100g", "k": 200, "p": 17,  "c": 7,   "f": 12,  "fi": 1,  "so": 1.9, "kw": ["lobster curry", "indian lobster", "masala lobster", "seafood curry"]},
    {"en": "Grilled Lobster (Olive Oil)",          "bn": "গ্রিলড লবস্টার",                     "s": "100g", "k": 160, "p": 20,  "c": 2,   "f": 8,   "fi": 0,  "so": 1.2, "kw": ["grilled lobster", "lobster", "healthy seafood", "olive oil lobster"]},
    {"en": "Mussels (Raw)",                        "bn": "ঝিনুক (কাঁচা)",                      "s": "100g", "k": 86,  "p": 12,  "c": 3,   "f": 2,   "fi": 0,  "so": 0.6, "kw": ["mussels", "jheenoek", "ঝিনুক", "raw mussels", "shellfish", "seafood"]},
    {"en": "Mussels White Wine Garlic (European)", "bn": "মাসেলস হোয়াইট ওয়াইন গার্লিক",      "s": "100g", "k": 160, "p": 14,  "c": 6,   "f": 9,   "fi": 1,  "so": 1.5, "kw": ["mussels white wine", "garlic mussels", "european mussels", "moules", "continental"]},
    {"en": "Indian Spicy Mussels Curry",           "bn": "ভারতীয় ঝিনুক কারি",                "s": "100g", "k": 170, "p": 13,  "c": 8,   "f": 10,  "fi": 1,  "so": 1.8, "kw": ["mussels curry", "indian mussels", "spicy mussels", "ঝিনুক কারি", "seafood curry"]},
    {"en": "Steamed Mussels (Plain)",              "bn": "স্টিমড ঝিনুক",                       "s": "100g", "k": 110, "p": 12,  "c": 2,   "f": 4,   "fi": 0,  "so": 1.0, "kw": ["steamed mussels", "mussels", "plain mussels", "shellfish"]},
    {"en": "Mussels Coconut Curry (Coastal India)","bn": "নারকেল ঝিনুক কারি",                  "s": "100g", "k": 210, "p": 13,  "c": 6,   "f": 14,  "fi": 1,  "so": 1.6, "kw": ["coconut mussels", "mussels coconut curry", "coastal curry", "ঝিনুক", "goa seafood"]},
]

EUROPEAN_FISH = [
    {"en": "Salmon (Raw)",                         "bn": "স্যালমন (কাঁচা)",                    "s": "100g", "k": 208, "p": 20,  "c": 0,   "f": 13,  "fi": 0,  "so": 0.4, "kw": ["salmon", "raw salmon", "atlantic salmon", "seafood", "omega 3", "fatty fish"]},
    {"en": "Grilled Salmon (European Style)",      "bn": "গ্রিলড স্যালমন",                     "s": "100g", "k": 230, "p": 22,  "c": 0,   "f": 15,  "fi": 0,  "so": 0.6, "kw": ["grilled salmon", "salmon", "european salmon", "healthy fish", "omega 3"]},
    {"en": "Salmon Curry (Indian Style)",          "bn": "স্যালমন কারি",                        "s": "100g", "k": 260, "p": 21,  "c": 6,   "f": 17,  "fi": 1,  "so": 1.8, "kw": ["salmon curry", "indian salmon", "salmon masala", "fish curry"]},
    {"en": "Tuna (Raw)",                           "bn": "টুনা (কাঁচা)",                       "s": "100g", "k": 132, "p": 29,  "c": 0,   "f": 1,   "fi": 0,  "so": 0.4, "kw": ["tuna", "raw tuna", "bluefin tuna", "seafood", "high protein fish"]},
    {"en": "Grilled Tuna Steak",                   "bn": "গ্রিলড টুনা স্টেক",                  "s": "100g", "k": 160, "p": 30,  "c": 0,   "f": 4,   "fi": 0,  "so": 0.6, "kw": ["tuna steak", "grilled tuna", "tuna", "high protein", "seafood"]},
    {"en": "Tuna Curry (Indian Style)",            "bn": "টুনা কারি",                           "s": "100g", "k": 190, "p": 28,  "c": 6,   "f": 8,   "fi": 1,  "so": 1.8, "kw": ["tuna curry", "indian tuna", "tuna masala", "fish curry"]},
    {"en": "Cod (Raw)",                            "bn": "কড মাছ (কাঁচা)",                     "s": "100g", "k": 82,  "p": 18,  "c": 0,   "f": 0.7, "fi": 0,  "so": 0.3, "kw": ["cod", "raw cod", "white fish", "atlantic cod", "seafood", "low fat fish"]},
    {"en": "Baked Cod (European Style)",           "bn": "বেকড কড",                             "s": "100g", "k": 120, "p": 20,  "c": 1,   "f": 4,   "fi": 0,  "so": 0.6, "kw": ["baked cod", "cod", "european fish", "healthy fish", "white fish"]},
    {"en": "Cod Curry (Indian Style)",             "bn": "কড কারি",                             "s": "100g", "k": 180, "p": 19,  "c": 6,   "f": 10,  "fi": 1,  "so": 1.7, "kw": ["cod curry", "indian cod", "fish curry", "cod masala"]},
    {"en": "Mackerel (Raw)",                       "bn": "ম্যাকারেল (কাঁচা)",                  "s": "100g", "k": 205, "p": 19,  "c": 0,   "f": 14,  "fi": 0,  "so": 0.5, "kw": ["mackerel", "raw mackerel", "fatty fish", "omega 3", "seafood"]},
    {"en": "Grilled Mackerel",                     "bn": "গ্রিলড ম্যাকারেল",                   "s": "100g", "k": 230, "p": 22,  "c": 0,   "f": 16,  "fi": 0,  "so": 0.7, "kw": ["grilled mackerel", "mackerel", "healthy fish", "omega 3", "seafood"]},
    {"en": "Mackerel Curry (Indian Style)",        "bn": "ম্যাকারেল কারি",                      "s": "100g", "k": 260, "p": 20,  "c": 6,   "f": 18,  "fi": 1,  "so": 1.9, "kw": ["mackerel curry", "indian mackerel", "bangda curry", "fish curry", "omega 3"]},
]

DUCK = [
    {"en": "Duck Meat (Raw, Skin On)",                        "bn": "হাঁসের মাংস (কাঁচা)",         "s": "100g", "k": 337, "p": 19, "c": 0,  "f": 28, "fi": 0, "so": 0.9, "kw": ["duck", "duck meat", "haanser mangsho", "হাঁস", "raw duck", "poultry"]},
    {"en": "Duck Curry (Bengali Style Kosha Haanser Mangsho)","bn": "কোশা হাঁসের মাংস",            "s": "100g", "k": 420, "p": 22, "c": 6,  "f": 34, "fi": 1, "so": 1.8, "kw": ["kosha hanser mangsho", "bengali duck", "duck curry", "কোশা হাঁস", "হাঁসের মাংস", "bengali meat"]},
    {"en": "Duck Curry (Assam Style – Khar/Spiced)",          "bn": "অসমীয়া হাঁস কারি",            "s": "100g", "k": 390, "p": 21, "c": 5,  "f": 32, "fi": 1, "so": 1.6, "kw": ["assam duck", "assamese duck", "khar duck", "হাঁস", "northeast india duck"]},
    {"en": "Duck Curry (Kerala Style Roast Curry)",           "bn": "কেরালা হাঁস রোস্ট কারি",       "s": "100g", "k": 410, "p": 20, "c": 8,  "f": 33, "fi": 1, "so": 1.7, "kw": ["kerala duck", "kerala duck roast", "duck curry", "south india duck", "হাঁস"]},
    {"en": "Duck Roast (Indian Dry Roast)",                   "bn": "হাঁস রোস্ট",                   "s": "100g", "k": 450, "p": 24, "c": 4,  "f": 38, "fi": 0, "so": 1.9, "kw": ["duck roast", "indian duck roast", "dry roast duck", "হাঁস রোস্ট", "duck"]},
    {"en": "Duck Fry (Shallow Fried Indian Style)",           "bn": "হাঁস ভাজা",                    "s": "100g", "k": 470, "p": 23, "c": 5,  "f": 40, "fi": 0, "so": 2.0, "kw": ["duck fry", "fried duck", "হাঁস ভাজা", "indian duck fry", "duck"]},
    {"en": "Duck Curry (Street Style North India)",           "bn": "স্ট্রিট স্টাইল হাঁস কারি",    "s": "100g", "k": 430, "p": 21, "c": 10, "f": 34, "fi": 1, "so": 2.1, "kw": ["street duck", "north india duck", "duck curry", "হাঁস", "street food"]},
    {"en": "Duck Soup (Clear Broth Style)",                   "bn": "হাঁস স্যুপ",                   "s": "100g", "k": 180, "p": 18, "c": 2,  "f": 12, "fi": 0, "so": 1.3, "kw": ["duck soup", "হাঁস স্যুপ", "duck broth", "clear soup", "light duck"]},
]

ALL_GROUPS = [
    ('Snail Curries',            SNAILS,         'seafood'),
    ('Squid / Octopus / Cuttlefish', CEPHALOPODS,'seafood'),
    ('Crab / Lobster / Mussels', SHELLFISH,      'seafood'),
    ('Salmon / Tuna / Cod / Mackerel', EUROPEAN_FISH, 'seafood'),
    ('Duck',                     DUCK,           'meat'),
]


def main():
    data = json.loads(DATASET.read_text(encoding='utf-8'))
    before   = len(data)
    max_id   = max(item['id'] for item in data)
    next_id  = max_id + 1
    existing = {item['en'].strip().lower() for item in data}

    added = skipped = 0
    for group_name, items, cat in ALL_GROUPS:
        print(f"\n── {group_name} ──")
        for raw in items:
            key = raw['en'].strip().lower()
            if key in existing:
                print(f"  SKIP (dup): {raw['en']}")
                skipped += 1
                continue
            item = {
                'id':            next_id,
                'en':            raw['en'],
                'bn':            raw['bn'],
                'cat':           cat,
                's':             raw['s'],
                'k':             raw['k'],
                'p':             raw['p'],
                'c':             raw['c'],
                'f':             raw['f'],
                'fi':            raw['fi'],
                'sod':           round(raw['so'] * 1000),
                'src':           'user_curated',
                'quality_score': 72,
                'kw':            raw.get('kw', []),
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
