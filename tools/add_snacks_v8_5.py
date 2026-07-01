"""
add_snacks_v8_5.py
Add snack items: Popcorn (10), Nachos (12), Mixture/Chanachur (14),
Roasted Snacks (3), Spring Rolls (2) = 41 items total.
"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

DATASET = Path('assets/data/food_master_v8_2.json')

# so = sodium in grams → sod in mg (× 1000)
# sf, su, id dropped

POPCORN = [
    {"en": "Air-Popped Popcorn (Plain)",                 "bn": "এয়ার পপড পপকর্ন (সাধারণ)",         "s": "100g", "k": 387, "p": 12,  "c": 78, "f": 4.5, "fi": 15, "so": 0.02, "kw": ["popcorn", "air popped", "plain popcorn", "low fat snack", "whole grain"]},
    {"en": "Butter Popcorn (Cinema Style)",               "bn": "বাটার পপকর্ন (সিনেমা স্টাইল)",     "s": "100g", "k": 530, "p": 8,   "c": 50, "f": 35,  "fi": 8,  "so": 1.2,  "kw": ["butter popcorn", "cinema popcorn", "movie popcorn", "popcorn", "theatre snack"]},
    {"en": "Salted Popcorn",                             "bn": "সল্টেড পপকর্ন",                      "s": "100g", "k": 480, "p": 9,   "c": 65, "f": 22,  "fi": 10, "so": 1.8,  "kw": ["salted popcorn", "salty popcorn", "popcorn", "snack"]},
    {"en": "Caramel Popcorn",                            "bn": "কারামেল পপকর্ন",                     "s": "100g", "k": 460, "p": 4,   "c": 80, "f": 14,  "fi": 4,  "so": 0.6,  "kw": ["caramel popcorn", "sweet popcorn", "popcorn", "caramel snack"]},
    {"en": "Cheese Popcorn",                             "bn": "চিজ পপকর্ন",                         "s": "100g", "k": 510, "p": 10,  "c": 52, "f": 30,  "fi": 6,  "so": 1.5,  "kw": ["cheese popcorn", "cheesy popcorn", "popcorn", "cheddar popcorn"]},
    {"en": "Sweet Popcorn",                              "bn": "মিষ্টি পপকর্ন",                      "s": "100g", "k": 430, "p": 5,   "c": 75, "f": 12,  "fi": 7,  "so": 0.4,  "kw": ["sweet popcorn", "popcorn", "sugary popcorn", "snack"]},
    {"en": "Spicy Masala Popcorn",                       "bn": "মসলা পপকর্ন",                        "s": "100g", "k": 470, "p": 8,   "c": 60, "f": 20,  "fi": 9,  "so": 2.0,  "kw": ["masala popcorn", "spicy popcorn", "popcorn", "indian snack", "chatpata"]},
    {"en": "Movie Theatre Butter Popcorn (Large Serving)","bn": "সিনেমা বাটার পপকর্ন (লার্জ)",       "s": "150g", "k": 795, "p": 12,  "c": 75, "f": 52,  "fi": 12, "so": 1.8,  "kw": ["movie popcorn", "cinema popcorn", "large popcorn", "butter popcorn", "theatre"]},
    {"en": "Microwave Popcorn (Butter Flavored)",        "bn": "মাইক্রোওয়েভ পপকর্ন (বাটার)",       "s": "100g", "k": 500, "p": 7,   "c": 55, "f": 28,  "fi": 6,  "so": 1.6,  "kw": ["microwave popcorn", "instant popcorn", "butter popcorn", "popcorn"]},
    {"en": "Low Fat Popcorn",                            "bn": "লো ফ্যাট পপকর্ন",                   "s": "100g", "k": 320, "p": 9,   "c": 70, "f": 6,   "fi": 14, "so": 0.2,  "kw": ["low fat popcorn", "healthy popcorn", "diet popcorn", "popcorn", "light snack"]},
]

NACHOS = [
    {"en": "Plain Tortilla Chips (Nachos Base)",         "bn": "সাধারণ টর্টিলা চিপস",              "s": "100g", "k": 480, "p": 7,  "c": 63, "f": 22, "fi": 5, "so": 0.9, "kw": ["tortilla chips", "nachos", "plain chips", "corn chips", "crispy"]},
    {"en": "Cheese Nachos (Basic)",                      "bn": "চিজ নাচোস (সাধারণ)",               "s": "100g", "k": 540, "p": 10, "c": 50, "f": 32, "fi": 4, "so": 1.5, "kw": ["cheese nachos", "nachos", "cheesy", "snack", "cinema snack"]},
    {"en": "Loaded Cheese Nachos (Cinema Style)",        "bn": "লোডেড চিজ নাচোস (সিনেমা স্টাইল)", "s": "100g", "k": 620, "p": 12, "c": 52, "f": 40, "fi": 4, "so": 1.8, "kw": ["loaded nachos", "cinema nachos", "cheese nachos", "nachos", "movie snack"]},
    {"en": "Chicken Nachos",                             "bn": "চিকেন নাচোস",                       "s": "100g", "k": 580, "p": 20, "c": 45, "f": 30, "fi": 4, "so": 1.9, "kw": ["chicken nachos", "nachos", "loaded nachos", "protein snack"]},
    {"en": "Beef Nachos",                                "bn": "বিফ নাচোস",                          "s": "100g", "k": 610, "p": 22, "c": 44, "f": 34, "fi": 4, "so": 2.1, "kw": ["beef nachos", "nachos", "loaded nachos", "snack"]},
    {"en": "Veggie Nachos (Beans + Corn + Cheese)",      "bn": "ভেজ নাচোস (বিনস + কর্ন)",          "s": "100g", "k": 520, "p": 14, "c": 58, "f": 26, "fi": 8, "so": 1.4, "kw": ["veggie nachos", "vegetarian nachos", "bean nachos", "nachos", "veg snack"]},
    {"en": "Spicy Jalapeno Nachos",                      "bn": "স্পাইসি জলাপেনো নাচোস",             "s": "100g", "k": 510, "p": 9,  "c": 55, "f": 28, "fi": 5, "so": 1.7, "kw": ["jalapeno nachos", "spicy nachos", "nachos", "hot snack"]},
    {"en": "BBQ Chicken Nachos",                         "bn": "BBQ চিকেন নাচোস",                   "s": "100g", "k": 600, "p": 21, "c": 53, "f": 32, "fi": 4, "so": 2.0, "kw": ["bbq nachos", "barbecue nachos", "chicken nachos", "nachos", "smoky"]},
    {"en": "Sour Cream & Cheese Nachos",                 "bn": "সাওয়ার ক্রিম ও চিজ নাচোস",         "s": "100g", "k": 560, "p": 10, "c": 48, "f": 35, "fi": 3, "so": 1.6, "kw": ["sour cream nachos", "nachos", "creamy nachos", "snack"]},
    {"en": "Cinema Nachos Combo (Large Serving)",        "bn": "সিনেমা নাচোস কম্বো (লার্জ)",        "s": "150g", "k": 850, "p": 15, "c": 75, "f": 52, "fi": 6, "so": 2.4, "kw": ["cinema nachos", "large nachos", "nachos combo", "movie snack", "nachos"]},
    {"en": "Cheese Dip Nachos",                          "bn": "চিজ ডিপ নাচোস",                     "s": "100g", "k": 580, "p": 11, "c": 49, "f": 38, "fi": 3, "so": 1.9, "kw": ["cheese dip nachos", "nachos", "dip snack", "cheesy nachos"]},
    {"en": "Low Fat Nachos (Baked Chips)",               "bn": "লো ফ্যাট নাচোস (বেকড)",             "s": "100g", "k": 380, "p": 8,  "c": 60, "f": 12, "fi": 6, "so": 0.7, "kw": ["baked nachos", "low fat nachos", "healthy nachos", "nachos", "diet chips"]},
]

MIXTURE = [
    {"en": "Classic Mixture (North Indian)",             "bn": "ক্লাসিক মিক্সচার",                  "s": "100g", "k": 520, "p": 10, "c": 55, "f": 30, "fi": 6, "so": 1.8, "kw": ["mixture", "namkeen", "indian snack", "north indian", "savory mix"]},
    {"en": "Bombay Mix (Chanachur)",                     "bn": "বম্বে মিক্স / চানাচুর",             "s": "100g", "k": 500, "p": 11, "c": 58, "f": 28, "fi": 7, "so": 2.0, "kw": ["bombay mix", "chanachur", "namkeen", "indian snack", "mixture", "farsan"]},
    {"en": "Bengali Chanachur (Spicy Jhal Mix)",         "bn": "বাঙালি চানাচুর (ঝাল মিক্স)",        "s": "100g", "k": 510, "p": 12, "c": 52, "f": 30, "fi": 6, "so": 2.1, "kw": ["chanachur", "bengali chanachur", "jhal mix", "spicy mixture", "bangladeshi snack", "নামকীন"]},
    {"en": "Khatta Meetha Mixture",                      "bn": "খাট্টা মিঠা মিক্সচার",              "s": "100g", "k": 490, "p": 9,  "c": 65, "f": 24, "fi": 5, "so": 1.6, "kw": ["khatta meetha", "sweet sour mix", "mixture", "namkeen", "indian snack"]},
    {"en": "South Indian Mixture (Madras Mix)",          "bn": "সাউথ ইন্ডিয়ান মিক্সচার",           "s": "100g", "k": 530, "p": 10, "c": 60, "f": 29, "fi": 6, "so": 2.2, "kw": ["south indian mixture", "madras mix", "namkeen", "mixture", "farsan"]},
    {"en": "Rajasthani Mixture",                         "bn": "রাজস্থানী মিক্সচার",                "s": "100g", "k": 540, "p": 9,  "c": 57, "f": 33, "fi": 6, "so": 2.3, "kw": ["rajasthani mixture", "rajasthani snack", "namkeen", "mixture"]},
    {"en": "Bikaneri Mixture (Sev Heavy)",               "bn": "বিকানেরি মিক্সচার",                 "s": "100g", "k": 550, "p": 11, "c": 54, "f": 35, "fi": 6, "so": 2.4, "kw": ["bikaneri mixture", "sev mixture", "namkeen", "rajasthan snack", "mixture"]},
    {"en": "Cornflakes Mixture",                         "bn": "কর্নফ্লেক্স মিক্সচার",             "s": "100g", "k": 480, "p": 7,  "c": 70, "f": 20, "fi": 4, "so": 1.5, "kw": ["cornflakes mixture", "cornflake mix", "namkeen", "mixture", "crispy snack"]},
    {"en": "Peanut Sev Mixture",                         "bn": "চিনাবাদাম সেভ মিক্স",               "s": "100g", "k": 560, "p": 15, "c": 45, "f": 38, "fi": 8, "so": 2.1, "kw": ["peanut sev", "sev mixture", "namkeen", "mixture", "peanut snack"]},
    {"en": "Dry Fruit Mixture",                          "bn": "ড্রাই ফ্রুট মিক্সচার",             "s": "100g", "k": 600, "p": 12, "c": 50, "f": 40, "fi": 7, "so": 0.8, "kw": ["dry fruit mixture", "trail mix", "dry fruit", "healthy snack", "namkeen"]},
    {"en": "Balaji Style Mixture",                       "bn": "বালাজি স্টাইল মিক্সচার",            "s": "100g", "k": 530, "p": 10, "c": 60, "f": 30, "fi": 6, "so": 1.9, "kw": ["balaji mixture", "balaji namkeen", "mixture", "indian snack"]},
    {"en": "Local Street Mixture (Unbranded)",           "bn": "লোকাল স্ট্রিট মিক্সচার",            "s": "100g", "k": 510, "p": 9,  "c": 62, "f": 28, "fi": 5, "so": 2.5, "kw": ["street mixture", "unbranded mix", "namkeen", "mixture", "local snack"]},
    {"en": "Spicy Chanachur (Extra Hot Kolkata Style)",  "bn": "এক্সট্রা হট চানাচুর",               "s": "100g", "k": 515, "p": 12, "c": 50, "f": 32, "fi": 6, "so": 2.3, "kw": ["chanachur", "extra hot chanachur", "kolkata chanachur", "spicy snack", "bengali snack"]},
    {"en": "Healthy Roasted Mixture (Low Oil)",          "bn": "হেলদি রোস্টেড মিক্সচার",            "s": "100g", "k": 380, "p": 14, "c": 55, "f": 10, "fi": 10, "so": 0.7, "kw": ["roasted mixture", "healthy mix", "low oil mixture", "diet snack", "namkeen"]},
]

ROASTED = [
    {"en": "Roasted Chickpeas",                          "bn": "ভাজা ছোলা",                          "s": "100g", "k": 380, "p": 20, "c": 60, "f": 6,  "fi": 12, "so": 0.5, "kw": ["roasted chickpeas", "chana", "chhola", "ভাজা ছোলা", "protein snack", "healthy snack"]},
    {"en": "Roasted Makhana (Fox Nuts)",                 "bn": "মখানা",                              "s": "100g", "k": 350, "p": 9,  "c": 70, "f": 2,  "fi": 10, "so": 0.2, "kw": ["makhana", "fox nuts", "lotus seeds", "roasted makhana", "healthy snack", "makhna"]},
    {"en": "Roasted Almonds",                            "bn": "বাদাম",                              "s": "100g", "k": 580, "p": 21, "c": 22, "f": 50, "fi": 12, "so": 0.01,"kw": ["roasted almonds", "badam", "almonds", "বাদাম", "nut", "healthy snack"]},
]

SPRING_ROLLS = [
    {"en": "Spring Roll (Vegetable)",                    "bn": "স্প্রিং রোল",                       "s": "100g", "k": 250, "p": 5,  "c": 28, "f": 12, "fi": 3, "so": 1.0, "kw": ["spring roll", "veg spring roll", "vegetable roll", "chinese snack", "fried roll"]},
    {"en": "Chicken Spring Roll",                        "bn": "চিকেন স্প্রিং রোল",                "s": "100g", "k": 290, "p": 10, "c": 25, "f": 15, "fi": 2, "so": 1.3, "kw": ["chicken spring roll", "spring roll", "chicken roll", "chinese snack", "fried roll"]},
]

CAT_MAP = {
    'popcorn':      'snack',
    'nachos':       'snack',
    'mixture':      'snack',
    'roasted':      'snack',
    'spring_roll':  'snack',
}

ALL_GROUPS = [
    ('Popcorn',      POPCORN,      'snack'),
    ('Nachos',       NACHOS,       'snack'),
    ('Mixture',      MIXTURE,      'snack'),
    ('Roasted',      ROASTED,      'snack'),
    ('Spring Rolls', SPRING_ROLLS, 'snack'),
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
