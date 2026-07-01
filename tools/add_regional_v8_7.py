"""
add_regional_v8_7.py
Add: Flower Curries (9), Bengali Small Fish (10), Bengali Catfish/Predator Fish (14),
     Raw Banana Dishes (11), Jaggery/Gur Sweets (11), Cotton Candy (4) = 59 items
"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

DATASET = Path('assets/data/food_master_v8_2.json')

FLOWER_DISHES = [
    {"en": "Pumpkin Flower Curry (Bengal Bhaja / Torkari)", "bn": "কুমড়ো ফুল ভাজা",               "s": "100g",          "k": 75,  "p": 2.5, "c": 8,  "f": 4,  "fi": 2.5,"so": 0.6, "kw": ["pumpkin flower", "kumro phool", "কুমড়ো ফুল", "flower curry", "bengali vegetable", "vegetable"]},
    {"en": "Pumpkin Flower Pakora (Fritter)",                "bn": "কুমড়ো ফুলের পাকোড়া",          "s": "100g",          "k": 210, "p": 5,   "c": 22, "f": 12, "fi": 2,  "so": 0.8, "kw": ["pumpkin flower pakora", "kumro phool bora", "কুমড়ো ফুল", "flower fritter", "bengali snack"]},
    {"en": "Drumstick Flower Curry (Sojne Phool Torkari)",  "bn": "সজনে ফুলের তরকারি",             "s": "100g",          "k": 85,  "p": 4,   "c": 9,  "f": 4,  "fi": 3,  "so": 0.7, "kw": ["drumstick flower", "sojne phool", "সজনে ফুল", "moringa flower", "bengali vegetable"]},
    {"en": "Drumstick Flower Pakora",                        "bn": "সজনে ফুলের বড়া",               "s": "100g",          "k": 230, "p": 6,   "c": 25, "f": 14, "fi": 2,  "so": 1.0, "kw": ["drumstick flower pakora", "sojne phool bora", "সজনে ফুল", "moringa flower fritter"]},
    {"en": "Banana Flower Curry (Mocha Ghonto - Bengal)",   "bn": "মোচা ঘন্ট",                     "s": "100g",          "k": 140, "p": 5,   "c": 18, "f": 6,  "fi": 5,  "so": 0.9, "kw": ["mocha ghonto", "banana flower curry", "কলার মোচা", "mocha", "bengali vegetable", "মোচা"]},
    {"en": "Banana Flower Fry (Mocha Bhaja)",                "bn": "মোচা ভাজা",                     "s": "100g",          "k": 190, "p": 4,   "c": 20, "f": 10, "fi": 4,  "so": 1.2, "kw": ["mocha bhaja", "banana flower fry", "মোচা ভাজা", "bengali snack", "mocha"]},
    {"en": "Sesbania Flower Curry (Agathi / Agastya Phool Curry)", "bn": "অগস্তি ফুল কারি",       "s": "100g",          "k": 80,  "p": 5,   "c": 7,  "f": 3,  "fi": 3,  "so": 0.5, "kw": ["sesbania flower", "agastya phool", "agathi flower", "flower curry", "traditional vegetable"]},
    {"en": "Sesbania Flower Stir Fry (South India Style)",   "bn": "অগস্তি ফুল ভাজি",              "s": "100g",          "k": 120, "p": 6,   "c": 10, "f": 6,  "fi": 4,  "so": 0.8, "kw": ["sesbania stir fry", "agathi fry", "south indian flower", "flower stir fry"]},
    {"en": "Pumpkin Flower Curry (South Indian Coconut Style)", "bn": "কুমড়ো ফুল নারকেল কারি",   "s": "100g",          "k": 110, "p": 3,   "c": 10, "f": 7,  "fi": 2,  "so": 0.9, "kw": ["pumpkin flower coconut", "kumro phool", "coconut flower curry", "south indian vegetable"]},
]

SMALL_FISH = [
    {"en": "Tangra Fish (Mystus vittatus) Raw",              "bn": "তাঁগ্রা মাছ (কাঁচা)",           "s": "100g",          "k": 95,  "p": 17,  "c": 0,  "f": 2.5,"fi": 0,  "so": 0.8, "kw": ["tangra", "tangra fish", "তাঁগ্রা মাছ", "mystus", "bengali fish", "small fish"]},
    {"en": "Tangra Jhol (Bengali Light Curry)",              "bn": "তাঁগ্রা ঝোল",                   "s": "1 bowl (~250g)","k": 180, "p": 18,  "c": 6,  "f": 10, "fi": 1,  "so": 1.5, "kw": ["tangra jhol", "তাঁগ্রা ঝোল", "bengali fish curry", "tangra fish curry", "light curry"]},
    {"en": "Tangra Tel Jhol (Oil Curry Style)",              "bn": "তাঁগ্রা তেল ঝোল",               "s": "1 bowl (~250g)","k": 210, "p": 18,  "c": 5,  "f": 14, "fi": 1,  "so": 1.8, "kw": ["tangra tel jhol", "tangra oil curry", "তাঁগ্রা তেল", "bengali fish"]},
    {"en": "Koi Fish (Anabas testudineus) Raw",              "bn": "কৈ মাছ (কাঁচা)",                "s": "100g",          "k": 105, "p": 19,  "c": 0,  "f": 3,  "fi": 0,  "so": 0.9, "kw": ["koi fish", "koi mach", "কৈ মাছ", "anabas", "climbing perch", "bengali fish"]},
    {"en": "Tel Koi (Mustard Oil Curry)",                    "bn": "তেল কৈ",                         "s": "1 bowl (~250g)","k": 250, "p": 20,  "c": 6,  "f": 18, "fi": 1,  "so": 2.0, "kw": ["tel koi", "তেল কৈ", "koi fish curry", "mustard koi", "bengali fish"]},
    {"en": "Lata Fish (Ompok / Pabda-type small fish) Raw",  "bn": "লাটা মাছ (কাঁচা)",              "s": "100g",          "k": 88,  "p": 18,  "c": 0,  "f": 1.8,"fi": 0,  "so": 0.7, "kw": ["lata fish", "lata mach", "লাটা মাছ", "ompok", "bengali fish", "small fish"]},
    {"en": "Lata Fish Jhol (Light Bengali Curry)",           "bn": "লাটা মাছের ঝোল",                "s": "1 bowl (~250g)","k": 170, "p": 19,  "c": 5,  "f": 9,  "fi": 1,  "so": 1.4, "kw": ["lata fish curry", "লাটা মাছ ঝোল", "bengali fish curry", "light fish curry"]},
    {"en": "Mixed Small Fish Fry (Tangra + Koi + Puti)",     "bn": "ছোট মাছ ভাজা",                  "s": "100g",          "k": 230, "p": 20,  "c": 6,  "f": 15, "fi": 1,  "so": 1.6, "kw": ["small fish fry", "choto mach bhaja", "ছোট মাছ", "bengali fish fry", "mixed fish"]},
    {"en": "Tangra Bhaja (Deep Fried)",                      "bn": "তাঁগ্রা ভাজা",                  "s": "100g",          "k": 260, "p": 18,  "c": 8,  "f": 18, "fi": 0,  "so": 2.1, "kw": ["tangra bhaja", "তাঁগ্রা ভাজা", "fried tangra", "bengali fried fish", "tangra"]},
    {"en": "Koi Macher Jhol (Simple Curry)",                 "bn": "কৈ মাছের ঝোল",                  "s": "1 bowl (~250g)","k": 190, "p": 19,  "c": 6,  "f": 11, "fi": 1,  "so": 1.5, "kw": ["koi macher jhol", "কৈ মাছ ঝোল", "koi fish curry", "bengali fish curry"]},
]

PREDATOR_FISH = [
    {"en": "Magur Fish (Clarias batrachus) Raw",             "bn": "মাগুর মাছ (কাঁচা)",             "s": "100g",          "k": 105, "p": 18,  "c": 0,  "f": 3.5,"fi": 0,  "so": 0.9, "kw": ["magur", "magur fish", "মাগুর মাছ", "catfish", "clarias", "bengali fish"]},
    {"en": "Magur Curry (Bengali Style Jhol)",               "bn": "মাগুর মাছের ঝোল",               "s": "1 bowl (~250g)","k": 220, "p": 20,  "c": 6,  "f": 14, "fi": 1,  "so": 1.7, "kw": ["magur jhol", "মাগুর ঝোল", "catfish curry", "bengali fish curry", "magur"]},
    {"en": "Singhi Fish (Heteropneustes fossilis) Raw",       "bn": "সিঙ্গি মাছ (কাঁচা)",            "s": "100g",          "k": 95,  "p": 17,  "c": 0,  "f": 2.8,"fi": 0,  "so": 0.8, "kw": ["singhi", "singhi fish", "সিঙ্গি মাছ", "stinging catfish", "bengali fish", "medicinal fish"]},
    {"en": "Singhi Jhol (Light Bengali Curry)",              "bn": "সিঙ্গি মাছের ঝোল",              "s": "1 bowl (~250g)","k": 200, "p": 18,  "c": 5,  "f": 12, "fi": 1,  "so": 1.5, "kw": ["singhi jhol", "সিঙ্গি ঝোল", "singhi curry", "bengali fish curry"]},
    {"en": "Shol Fish (Snakehead) Raw",                      "bn": "শোল মাছ (কাঁচা)",               "s": "100g",          "k": 110, "p": 20,  "c": 0,  "f": 3,  "fi": 0,  "so": 0.9, "kw": ["shol fish", "শোল মাছ", "snakehead fish", "channa", "bengali fish"]},
    {"en": "Shol Macher Jhol (Traditional Curry)",           "bn": "শোল মাছের ঝোল",                 "s": "1 bowl (~250g)","k": 210, "p": 21,  "c": 6,  "f": 12, "fi": 1,  "so": 1.6, "kw": ["shol jhol", "শোল ঝোল", "snakehead curry", "bengali fish curry", "shol mach"]},
    {"en": "Shol Bhaja (Fried Snakehead)",                   "bn": "শোল মাছ ভাজা",                  "s": "100g",          "k": 260, "p": 20,  "c": 6,  "f": 18, "fi": 0,  "so": 2.0, "kw": ["shol bhaja", "শোল ভাজা", "fried snakehead", "bengali fried fish", "shol mach"]},
    {"en": "Pabda Fish (Ompok pabda) Raw",                   "bn": "পাবদা মাছ (কাঁচা)",             "s": "100g",          "k": 92,  "p": 18,  "c": 0,  "f": 2.2,"fi": 0,  "so": 0.7, "kw": ["pabda", "pabda fish", "পাবদা মাছ", "butter catfish", "bengali fish"]},
    {"en": "Pabda Macher Jhol (Light Curry)",                "bn": "পাবদা মাছের ঝোল",               "s": "1 bowl (~250g)","k": 190, "p": 19,  "c": 5,  "f": 10, "fi": 1,  "so": 1.4, "kw": ["pabda jhol", "পাবদা ঝোল", "pabda fish curry", "bengali fish curry", "pabda"]},
    {"en": "Pabda Bhapa (Steamed Mustard Curry)",            "bn": "পাবদা ভাপা",                    "s": "100g",          "k": 210, "p": 20,  "c": 4,  "f": 14, "fi": 1,  "so": 1.8, "kw": ["pabda bhapa", "পাবদা ভাপা", "steamed pabda", "mustard pabda", "bengali fish"]},
    {"en": "Chital Fish (Wallago attu) Raw",                 "bn": "চিতল মাছ (কাঁচা)",              "s": "100g",          "k": 120, "p": 19,  "c": 0,  "f": 4,  "fi": 0,  "so": 0.9, "kw": ["chital fish", "চিতল মাছ", "chitala", "clown knifefish", "bengali fish"]},
    {"en": "Chital Macher Muitha (Bengali Dum Curry)",       "bn": "চিতল মাছের মুইঠা",              "s": "1 bowl (~250g)","k": 280, "p": 20,  "c": 12, "f": 16, "fi": 2,  "so": 1.8, "kw": ["chital muitha", "চিতল মুইঠা", "fish dumpling curry", "bengali fish", "chital mach"]},
    {"en": "Boal Fish (Wallago attu large) Raw",             "bn": "বোয়াল মাছ (কাঁচা)",            "s": "100g",          "k": 135, "p": 20,  "c": 0,  "f": 5,  "fi": 0,  "so": 1.0, "kw": ["boal fish", "বোয়াল মাছ", "wallago", "large catfish", "bengali fish"]},
    {"en": "Boal Fish Curry (Spicy Bengali Style)",          "bn": "বোয়াল মাছের ঝোল",              "s": "1 bowl (~250g)","k": 240, "p": 21,  "c": 6,  "f": 16, "fi": 1,  "so": 1.9, "kw": ["boal jhol", "বোয়াল ঝোল", "boal curry", "bengali fish curry", "boal mach"]},
]

RAW_BANANA = [
    {"en": "Raw Banana (Kaancha Kola - Raw)",                "bn": "কাঁচা কলা (কাঁচা)",             "s": "100g",          "k": 122, "p": 1.5, "c": 31, "f": 0.4,"fi": 3.1,"so": 0.01,"kw": ["raw banana", "kaancha kola", "কাঁচা কলা", "green banana", "cooking banana", "kola"]},
    {"en": "Kaancha Kolar Torkari (Bengali Curry)",          "bn": "কাঁচা কলার তরকারি",             "s": "1 bowl (~250g)","k": 180, "p": 3,   "c": 35, "f": 6,  "fi": 5,  "so": 1.2, "kw": ["kaancha kolar torkari", "কাঁচা কলার তরকারি", "raw banana curry", "bengali vegetable"]},
    {"en": "Bengali Kaancha Kolar Dalna",                    "bn": "কাঁচা কলার ডালনা",              "s": "1 bowl (~250g)","k": 210, "p": 4,   "c": 38, "f": 8,  "fi": 5,  "so": 1.4, "kw": ["kolar dalna", "কাঁচা কলার ডালনা", "raw banana dalna", "bengali curry"]},
    {"en": "Kaancha Kolar Kofta Curry (Bengali)",            "bn": "কাঁচা কলার কোফতা কারি",        "s": "1 bowl (~300g)","k": 320, "p": 7,   "c": 42, "f": 18, "fi": 6,  "so": 1.8, "kw": ["kolar kofta", "কাঁচা কলার কোফতা", "banana kofta", "vegetarian kofta", "bengali"]},
    {"en": "Raw Banana Kofta (Fried Balls)",                 "bn": "কাঁচা কলার কোফতা ভাজা",        "s": "100g",          "k": 260, "p": 5,   "c": 28, "f": 16, "fi": 4,  "so": 1.5, "kw": ["banana kofta", "কলার কোফতা", "fried banana balls", "bengali snack"]},
    {"en": "Kaancha Kola Bhaja (Dry Fry)",                   "bn": "কাঁচা কলা ভাজা",                "s": "100g",          "k": 180, "p": 2,   "c": 25, "f": 8,  "fi": 3,  "so": 0.9, "kw": ["kaancha kola bhaja", "কাঁচা কলা ভাজা", "raw banana fry", "bengali snack"]},
    {"en": "Kaancha Kola Chips (Crispy Fry)",                "bn": "কাঁচা কলার চিপস",               "s": "100g",          "k": 280, "p": 2,   "c": 30, "f": 18, "fi": 2,  "so": 1.2, "kw": ["banana chips", "কাঁচা কলার চিপস", "green banana chips", "crispy chips", "kola chips"]},
    {"en": "Raw Banana Bharta (Mashed Style)",               "bn": "কাঁচা কলার ভর্তা",              "s": "100g",          "k": 150, "p": 2,   "c": 22, "f": 6,  "fi": 4,  "so": 0.8, "kw": ["kolar bharta", "কাঁচা কলার ভর্তা", "mashed banana", "banana bharta", "bengali"]},
    {"en": "Raw Banana Pakora (Besan Fry)",                  "bn": "কাঁচা কলার পাকোড়া",            "s": "100g",          "k": 300, "p": 6,   "c": 35, "f": 18, "fi": 3,  "so": 1.4, "kw": ["banana pakora", "কাঁচা কলার পাকোড়া", "raw banana fritter", "besan fry", "snack"]},
    {"en": "Kerala Style Raw Banana Fry (Chips Style)",      "bn": "কাঁচা কলা ফ্রাই (কেরালা স্টাইল)", "s": "100g",       "k": 260, "p": 2,   "c": 32, "f": 16, "fi": 3,  "so": 1.1, "kw": ["kerala banana fry", "raw banana chips", "ethakka", "nendran chips", "kerala snack"]},
    {"en": "Orissa Style Raw Banana Curry",                  "bn": "ওড়িশা স্টাইল কাঁচা কলার তরকারি","s": "1 bowl (~250g)","k": 200, "p": 4,   "c": 36, "f": 7,  "fi": 5,  "so": 1.3, "kw": ["orissa banana curry", "odia raw banana", "কাঁচা কলা", "odisha vegetable", "cooking banana"]},
]

JAGGERY = [
    {"en": "Akher Gur (Sugarcane Jaggery)",                  "bn": "আখের গুড়",                      "s": "100g",          "k": 383, "p": 0.4, "c": 97, "f": 0.1,"fi": 0.5,"so": 0.01,"kw": ["akher gur", "sugarcane jaggery", "আখের গুড়", "gur", "jaggery", "unrefined sugar"]},
    {"en": "Nolen Gur (Date Palm Liquid Jaggery)",           "bn": "নলেন গুড়",                      "s": "100g",          "k": 370, "p": 0.3, "c": 94, "f": 0.2,"fi": 0.4,"so": 0.02,"kw": ["nolen gur", "নলেন গুড়", "date palm jaggery", "khejur gur", "liquid jaggery", "bengali"]},
    {"en": "Patali Gur (Solid Date Palm Jaggery Block)",     "bn": "পাটালি গুড়",                    "s": "100g",          "k": 375, "p": 0.4, "c": 95, "f": 0.2,"fi": 0.5,"so": 0.02,"kw": ["patali gur", "পাটালি গুড়", "solid jaggery", "date palm block", "gur block", "bengali"]},
    {"en": "Khejur Gur Payesh (Bengali Rice Kheer)",         "bn": "খেজুর গুড়ের পায়েস",             "s": "1 bowl (~200g)","k": 220, "p": 5,   "c": 35, "f": 7,  "fi": 0.6,"so": 0.2, "kw": ["khejur gur payesh", "খেজুর গুড় পায়েস", "date palm kheer", "rice kheer", "bengali sweet"]},
    {"en": "Nolen Gur Sandesh (Bengali Sweet)",              "bn": "নলেন গুড় সন্দেশ",               "s": "100g",          "k": 280, "p": 6,   "c": 38, "f": 12, "fi": 0.5,"so": 0.2, "kw": ["nolen gur sandesh", "নলেন গুড় সন্দেশ", "date palm sandesh", "bengali sweet", "mishti"]},
    {"en": "Gurer Rosogolla (Jaggery Rasgulla)",             "bn": "গুড়ের রসগোল্লা",                "s": "2 pieces (~100g)","k": 240, "p": 5,  "c": 45, "f": 6,  "fi": 0.2,"so": 0.3, "kw": ["gurer rosogolla", "গুড়ের রসগোল্লা", "jaggery rasgulla", "bengali sweet", "mishti"]},
    {"en": "Gurer Sandesh (Sugarcane Gur Version)",          "bn": "গুড়ের সন্দেশ",                  "s": "100g",          "k": 260, "p": 6,   "c": 40, "f": 10, "fi": 0.5,"so": 0.2, "kw": ["gurer sandesh", "গুড়ের সন্দেশ", "jaggery sandesh", "bengali sweet", "mishti"]},
    {"en": "Gurer Payesh (Date Palm Kheer - Nolen Gur)",     "bn": "নলেন গুড়ের পায়েস",             "s": "1 bowl (~200g)","k": 260, "p": 6,   "c": 38, "f": 10, "fi": 0.6,"so": 0.2, "kw": ["nolen gur payesh", "নলেন গুড়ের পায়েস", "date palm rice pudding", "bengali sweet", "mishti"]},
    {"en": "Gur Chikki (Gur + Peanut Brittle)",              "bn": "গুড় চিঁকি",                     "s": "100g",          "k": 480, "p": 10,  "c": 55, "f": 22, "fi": 4,  "so": 0.3, "kw": ["gur chikki", "গুড় চিঁকি", "peanut brittle", "jaggery chikki", "indian sweet", "chikki"]},
    {"en": "Til Gur Ladoo (Sesame Jaggery Balls)",           "bn": "তিল গুড়ের লাড্ডু",              "s": "100g",          "k": 520, "p": 12,  "c": 50, "f": 28, "fi": 6,  "so": 0.4, "kw": ["til gur ladoo", "তিল গুড় লাড্ডু", "sesame jaggery ball", "til ladoo", "makar sankranti"]},
    {"en": "Moa (Joynagar Moa with Nolen Gur)",              "bn": "জয়নগরের মোয়া",                 "s": "100g",          "k": 450, "p": 8,   "c": 60, "f": 18, "fi": 3,  "so": 0.3, "kw": ["joynagar moa", "মোয়া", "nolen gur moa", "bengali sweet", "winter sweet", "rice crispy ball"]},
]

COTTON_CANDY = [
    {"en": "Cotton Candy (Plain Sugar Floss)",               "bn": "কটন ক্যান্ডি",                  "s": "100g",          "k": 400, "p": 0,   "c": 100,"f": 0,  "fi": 0,  "so": 0,   "kw": ["cotton candy", "candy floss", "sugar floss", "কটন ক্যান্ডি", "fair food", "carnival snack"]},
    {"en": "Cotton Candy (Small Fair Portion)",              "bn": "কটন ক্যান্ডি (ছোট পরিবেশন)",   "s": "1 cup (~30g)", "k": 120, "p": 0,   "c": 30, "f": 0,  "fi": 0,  "so": 0,   "kw": ["cotton candy", "small cotton candy", "fair snack", "mela candy", "বুড়ির চুল"]},
    {"en": "Colored Cotton Candy (Artificial Flavour)",      "bn": "রঙিন কটন ক্যান্ডি",             "s": "100g",          "k": 410, "p": 0,   "c": 100,"f": 0,  "fi": 0,  "so": 0.1, "kw": ["colored cotton candy", "flavored cotton candy", "food coloring candy", "carnival sweet"]},
    {"en": "Festival Cotton Candy Cone",                     "bn": "মেলা কটন ক্যান্ডি কন",          "s": "1 cone (~25g)","k": 100, "p": 0,   "c": 25, "f": 0,  "fi": 0,  "so": 0,   "kw": ["cotton candy cone", "mela candy", "মেলার মিষ্টি", "festival sweet", "বুড়ির চুল"]},
]

ALL_GROUPS = [
    ('Flower Curries',                    FLOWER_DISHES,  'vegetable'),
    ('Small Bengali Fish (Tangra/Koi)',   SMALL_FISH,     'fish'),
    ('Bengali Catfish & Predator Fish',   PREDATOR_FISH,  'fish'),
    ('Raw Banana Dishes',                 RAW_BANANA,     'vegetable'),
    ('Jaggery / Gur Sweets',              JAGGERY,        'sweet'),
    ('Cotton Candy',                      COTTON_CANDY,   'sweet'),
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
