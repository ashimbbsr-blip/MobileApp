"""
audit_fix_v8_8.py  — Production audit + category remap + Bengali QA fixes
Maps all non-UI dataset categories to the 22 standard UI categories,
fixes obvious Bengali translation issues, and reports a summary.
"""
import json, sys, re
from pathlib import Path
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

DATASET = Path('assets/data/food_master_v8_2.json')

# ── Category remap: dataset cat → UI cat ─────────────────────────────────────
# UI cats: rice bread bakery vegetable shaak legume fish meat egg dairy
#          fruit juice snack sweet beverage soup breakfast grain salad
#          noodle pizza restaurant_food
CAT_REMAP = {
    # granular protein categories → meat
    'chicken':      'meat',
    'mutton':       'meat',
    # paneer = vegetarian Indian dishes → vegetable (user's explicit request)
    'paneer':       'vegetable',
    # dal = legume in UI
    'dal':          'legume',
    # shellfish / cephalopods / crustaceans → fish (seafood chip maps to fish)
    'seafood':      'fish',
    # generic vegetarian labels
    'vegetarian':   'vegetable',
    # international restaurant food
    'thai':         'restaurant_food',
    'japanese':     'restaurant_food',
    'fast_food':    'restaurant_food',
    'street_food':  'restaurant_food',
    # confectionery → sweet
    'chocolate':    'sweet',
}

# ── Known Bengali QA fixes ────────────────────────────────────────────────────
# Format: exact EN name → corrected BN name
BN_FIXES = {
    # Snails — generic transliterations → proper Bengali
    "Indian Spicy Snail Curry":            "ভারতীয় শামুক কারি",
    "Bengali Mustard Snail Curry":         "বাঙালি সর্ষে শামুক কারি",
    "South Indian Pepper Snail Fry":       "দক্ষিণ ভারতীয় গোলমরিচ শামুক ভাজা",
    "Coconut Snail Curry":                 "নারকেল শামুক কারি",
    # Cotton candy
    "Cotton Candy (Plain Sugar Floss)":    "তুলো মিষ্টি (বুড়ির চুল)",
    "Cotton Candy (Small Fair Portion)":   "তুলো মিষ্টি (ছোট পরিবেশন)",
    "Colored Cotton Candy (Artificial Flavour)": "রঙিন তুলো মিষ্টি",
    "Festival Cotton Candy Cone":          "মেলার তুলো মিষ্টি",
    # Flower dishes — already good but unify style
    "Sesbania Flower Curry (Agathi / Agastya Phool Curry)": "অগস্থি ফুলের তরকারি",
    "Sesbania Flower Stir Fry (South India Style)":         "অগস্থি ফুল ভাজি",
    # Nachos — "নাচোস" is standard
    "Plain Tortilla Chips (Nachos Base)":  "সাধারণ টর্টিলা চিপস (নাচোস)",
    # Popcorn - fix "পপকর্ন" (already correct, keep)
    # BK items
    "Veg Whopper":                         "ভেজ হোয়াপার",
    "Chicken Whopper":                     "চিকেন হোয়াপার",
    "Veg Crispy Burger":                   "ভেজ ক্রিসপি বার্গার",
    "BK Veggie Burger":                    "বিকে ভেজি বার্গার",
    "Veg Supreme Burger":                  "ভেজ সুপ্রিম বার্গার",
    "Paneer King Burger":                  "পনির কিং বার্গার",
    "Paneer Royale Burger":                "পনির রয়্যাল বার্গার",
    "Chicken Nuggets (6 pcs)":             "চিকেন নাগেটস (৬ পিস)",
    "French Fries (Medium)":               "ফ্রেঞ্চ ফ্রাই (মাঝারি)",
    "Veg Wrap":                            "ভেজ র‍্যাপ",
    "Chicken Wrap":                        "চিকেন র‍্যাপ",
    "Chocolate Shake (Medium)":            "চকলেট শেক (মাঝারি)",
    # Bakery
    "Croissant (Plain Butter)":            "ক্রোয়াসাঁ (বাটার)",
    "Chocolate Croissant (Pain au Chocolat)": "চকলেট ক্রোয়াসাঁ",
    "Danish Pastry (Fruit Filled)":        "ড্যানিশ পেস্ট্রি (ফল ভরা)",
    "Danish Pastry (Cheese)":              "ড্যানিশ পেস্ট্রি (চিজ)",
    "Muffin (Chocolate Chip)":             "মাফিন (চকলেট চিপ)",
    "Donut (Glazed)":                      "ডোনাট (গ্লেজড)",
    "Apple Turnover":                      "আপেল টার্নওভার",
    "Cheese Danish":                       "চিজ ড্যানিশ",
    "Strudel (Apple)":                     "স্ট্রুডেল (আপেল)",
    "Baklava":                             "বাকলাভা",
    "Cream Puff (Profiterole)":            "ক্রিম পাফ (প্রফিটরোল)",
    "Eclair (Chocolate)":                  "এক্লেয়ার (চকলেট)",
    # Turkish/Doner
    "Chicken Doner Kebab (Wrap)":          "চিকেন ডোনার কেবাব (র‍্যাপ)",
    "Chicken Doner Kebab (Box with Rice)": "চিকেন ডোনার কেবাব (বক্স রাইস)",
    "Chicken Doner Kebab (Pita)":          "চিকেন ডোনার কেবাব (পিটা)",
    "Chicken Shish Kebab":                 "চিকেন শিশ কেবাব",
    "Mixed Kebab Plate (Chicken + Rice + Salad)": "মিক্সড কেবাব প্লেট",
    "Lahmacun (Turkish Pizza)":            "লাহমাচুন (তুর্কি পিজা)",
    "Chicken Durum (Large Wrap)":          "চিকেন দুরুম (বড় র‍্যাপ)",
    "Adana Kebab (Chicken Variant)":       "আদানা কেবাব (চিকেন)",
    "Falafel Wrap":                        "ফালাফেল র‍্যাপ",
    "Turkish Fries (Street Style)":        "তুর্কি ফ্রাই (স্ট্রিট স্টাইল)",
    "Chicken Doner Salad Bowl":            "চিকেন ডোনার সালাদ বাউল",
    "Iskender Kebab (Chicken)":            "ইস্কেন্দার কেবাব (চিকেন)",
    # Generic chocolates
    "Milk Chocolate":                      "মিল্ক চকলেট",
    "Dark Chocolate 70%":                  "ডার্ক চকলেট ৭০%",
    "Dark Chocolate 85%":                  "ডার্ক চকলেট ৮৫%",
    "Dark Chocolate 90%+":                 "ডার্ক চকলেট ৯০%+",
    "White Chocolate":                     "হোয়াইট চকলেট",
    "Ruby Chocolate":                      "রুবি চকলেট",
    # Milkshakes
    "Vanilla Milkshake":                   "ভ্যানিলা মিল্কশেক",
    "Chocolate Milkshake":                 "চকলেট মিল্কশেক",
    "Strawberry Milkshake":                "স্ট্রবেরি মিল্কশেক",
    "Oreo Milkshake":                      "ওরিও মিল্কশেক",
    "KitKat Milkshake":                    "কিটক্যাট মিল্কশেক",
    "Butterscotch Milkshake":              "বাটারস্কচ মিল্কশেক",
    "Cold Coffee Milkshake":               "কোল্ড কফি মিল্কশেক",
    "Dry Fruit Milkshake":                 "ড্রাই ফ্রুট মিল্কশেক",
    "Badam Milkshake":                     "বাদাম মিল্কশেক",
    "Pista Milkshake":                     "পিস্তা মিল্কশেক",
    "Kesar Badam Milkshake":               "কেশর বাদাম মিল্কশেক",
    "Rose Milkshake":                      "গোলাপ মিল্কশেক",
    "Chikoo Milkshake":                    "চিকু মিল্কশেক",
    # Spring rolls
    "Spring Roll (Vegetable)":             "সবজি স্প্রিং রোল",
    "Chicken Spring Roll":                 "চিকেন স্প্রিং রোল",
    # Snacks
    "Air-Popped Popcorn (Plain)":          "এয়ার-পপড পপকর্ন (সাদা)",
    "Butter Popcorn (Cinema Style)":       "বাটার পপকর্ন (সিনেমা স্টাইল)",
    "Salted Popcorn":                      "লবণযুক্ত পপকর্ন",
    "Caramel Popcorn":                     "ক্যারামেল পপকর্ন",
    "Cheese Popcorn":                      "চিজ পপকর্ন",
    "Sweet Popcorn":                       "মিষ্টি পপকর্ন",
    "Spicy Masala Popcorn":                "মশলা পপকর্ন",
    "Movie Theatre Butter Popcorn (Large Serving)": "সিনেমা হলের বাটার পপকর্ন (বড়)",
    "Microwave Popcorn (Butter Flavored)": "মাইক্রোওয়েভ পপকর্ন (বাটার)",
    "Low Fat Popcorn":                     "লো-ফ্যাট পপকর্ন",
    # Roasted snacks
    "Roasted Chickpeas":                   "ভাজা ছোলা",
    "Roasted Makhana (Fox Nuts)":          "ভাজা মাখানা",
    "Roasted Almonds":                     "ভাজা বাদাম",
    # Duck
    "Duck Meat (Raw, Skin On)":            "হাঁসের মাংস (কাঁচা, চামড়াসহ)",
    "Duck Curry (Bengali Style Kosha Haanser Mangsho)": "কষা হাঁসের মাংস",
    "Duck Curry (Assam Style – Khar/Spiced)": "অসমীয়া হাঁসের কারি",
    "Duck Curry (Kerala Style Roast Curry)": "কেরালা স্টাইল হাঁস রোস্ট কারি",
    "Duck Roast (Indian Dry Roast)":       "হাঁস রোস্ট (ভারতীয় শুকনো রোস্ট)",
    "Duck Fry (Shallow Fried Indian Style)": "হাঁস ভাজা (ভারতীয় স্টাইল)",
    "Duck Curry (Street Style North India)": "স্ট্রিট স্টাইল হাঁসের কারি",
    "Duck Soup (Clear Broth Style)":       "হাঁসের স্যুপ",
}

def main():
    data = json.loads(DATASET.read_text(encoding='utf-8'))
    before_cats = Counter(item.get('cat', 'MISSING') for item in data)

    cat_fixed = bn_fixed = 0

    for item in data:
        # Category remap
        old_cat = item.get('cat', '')
        if old_cat in CAT_REMAP:
            item['cat'] = CAT_REMAP[old_cat]
            cat_fixed += 1

        # Bengali QA fix
        en = item.get('en', '')
        if en in BN_FIXES:
            new_bn = BN_FIXES[en]
            if item.get('bn') != new_bn:
                item['bn'] = new_bn
                bn_fixed += 1

    after_cats = Counter(item.get('cat', 'MISSING') for item in data)

    print(f"Category remaps applied: {cat_fixed}")
    print(f"Bengali name fixes applied: {bn_fixed}")
    print(f"\nCategory distribution BEFORE:")
    for cat, count in sorted(before_cats.items(), key=lambda x: -x[1]):
        if cat not in after_cats or before_cats[cat] != after_cats[cat]:
            print(f"  {cat}: {count} → {after_cats.get(cat, 0)}")

    print(f"\nFinal category distribution:")
    for cat, count in sorted(after_cats.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count}")

    # Verify no unmapped categories remain
    ui_cats = {
        'rice','bread','bakery','vegetable','shaak','legume','fish','meat','egg','dairy',
        'fruit','juice','snack','sweet','beverage','soup','breakfast','grain','salad',
        'noodle','pizza','restaurant_food','other'
    }
    leftover = {c for c in after_cats if c not in ui_cats}
    if leftover:
        print(f"\nWARNING — still unmapped: {leftover}")
        for item in data:
            if item.get('cat') in leftover:
                print(f"  id={item['id']} cat={item['cat']}: {item['en']}")
    else:
        print(f"\nAll categories map cleanly to UI chips ✓")

    DATASET.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"\nSaved → {DATASET}  (total {len(data)} items)")

if __name__ == '__main__':
    main()
