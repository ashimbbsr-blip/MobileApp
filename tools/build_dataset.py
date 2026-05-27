"""
Data Conversion Pipeline
Reads: datasetsource/bengalifood.txt + datasetsource/Anuvaad_INDB_2024.11.xlsx
Outputs:
  assets/data/food_master.json   – unified bilingual dataset
  assets/data/index_en.json      – English prefix search index
  assets/data/index_bn.json      – Bengali prefix search index
"""

import json, re, os, sys
from collections import defaultdict

try:
    import openpyxl
except ImportError:
    sys.exit("Run: py -m pip install openpyxl")

# ─── Paths ────────────────────────────────────────────────────────────────────

SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
ROOT         = os.path.dirname(SCRIPT_DIR)
BF_PATH      = os.path.join(ROOT, "datasetsource", "bengalifood.txt")
INDB_PATH    = os.path.join(ROOT, "datasetsource", "Anuvaad_INDB_2024.11.xlsx")
OUT_DIR      = os.path.join(ROOT, "assets", "data")
MASTER_PATH  = os.path.join(OUT_DIR, "food_master_v5_3.json")
IDX_EN_PATH  = os.path.join(OUT_DIR, "index_en_v5_3.json")
IDX_BN_PATH  = os.path.join(OUT_DIR, "index_bn_v5_3.json")

os.makedirs(OUT_DIR, exist_ok=True)

# ─── Bengali Translation Dictionary ──────────────────────────────────────────
# Full-phrase and word-level mappings (English → Bengali)

BN_PHRASE = {
    # Beverages
    "hot tea": "গরম চা", "garam chai": "গরম চা", "milk tea": "দুধ চা",
    "black tea": "কালো চা", "green tea": "সবুজ চা", "herbal tea": "হারবাল চা",
    "ginger tea": "আদা চা", "iced tea": "ঠান্ডা চা", "masala tea": "মশলা চা",
    "instant coffee": "ইনস্ট্যান্ট কফি", "cold coffee": "ঠান্ডা কফি",
    "cold coffee with ice cream": "আইসক্রিম কফি",
    "espresso coffee": "এস্প্রেসো কফি", "black coffee": "কালো কফি",
    "milk coffee": "দুধ কফি", "hot cocoa": "গরম কোকো",
    "lemonade": "লেবুর শরবত", "iced lemon tea": "ঠান্ডা লেবু চা",
    "coconut water": "ডাবের জল", "tender coconut water": "ডাবের জল",
    "raw mango drink": "কাঁচা আমের পানীয়", "aam panna": "আম পান্না",
    "fruit punch": "ফ্রুট পাঞ্চ", "sugarcane juice": "আখের রস",
    "orange juice": "কমলার রস", "mango juice": "আমের রস",
    "tomato juice": "টমেটোর রস", "apple juice": "আপেলের রস",
    "lemon juice": "লেবুর রস", "grape juice": "আঙুরের রস",
    "watermelon juice": "তরমুজের রস", "pineapple juice": "আনারসের রস",
    "mixed fruit juice": "মিশ্র ফলের রস",
    "jeera water": "জিরা জল", "cumin infused water": "জিরা জল",
    "jeere ka pani": "জিরা জল", "zeere ka pani": "জিরা জল",
    "nimbu pani": "লেবুর শরবত", "nimboo pani": "লেবুর শরবত",
    "buttermilk": "ঘোল", "chaas": "ঘোল", "lassi": "লাচ্ছি",
    "sweet lassi": "মিষ্টি লাচ্ছি", "salted lassi": "নোনতা লাচ্ছি",
    "mango lassi": "আমের লাচ্ছি", "banana lassi": "কলার লাচ্ছি",
    "banana shake": "কলা শেক", "mango shake": "আম শেক",
    "strawberry shake": "স্ট্রবেরি শেক", "chocolate milk": "চকো মিল্ক",
    "milk shake": "মিল্কশেক", "protein shake": "প্রোটিন শেক",
    "detox water": "ডিটক্স জল", "lemon honey water": "লেবু মধু জল",
    "turmeric milk": "হলুদ দুধ", "golden milk": "সোনালি দুধ",
    "coco pine cooler": "নারকেল পাইনাপেল ড্রিংক",
    "summer cooler": "গ্রীষ্মের পানীয়",
    "apple cider drink": "আপেল সাইডার ড্রিংক",
    "sharbat": "শরবত", "rooh afza": "রুহ আফজা",
    "lem o gin": "লেমো জিন",

    # Rice Dishes
    "plain rice": "সাদা ভাত", "white rice": "সাদা ভাত",
    "brown rice": "লাল চালের ভাত", "steamed rice": "সেদ্ধ ভাত",
    "boiled rice": "সেদ্ধ ভাত", "fried rice": "ফ্রাইড রাইস",
    "egg fried rice": "ডিম ফ্রাইড রাইস",
    "chicken fried rice": "চিকেন ফ্রাইড রাইস",
    "veg fried rice": "ভেজ ফ্রাইড রাইস",
    "biryani": "বিরিয়ানি", "chicken biryani": "চিকেন বিরিয়ানি",
    "mutton biryani": "মাটন বিরিয়ানি", "veg biryani": "ভেজ বিরিয়ানি",
    "fish biryani": "মাছ বিরিয়ানি",
    "kolkata biryani": "কলকাতা বিরিয়ানি",
    "pulao": "পোলাও", "veg pulao": "সবজি পোলাও",
    "peas pulao": "মটর পোলাও", "mushroom pulao": "মাশরুম পোলাও",
    "vegetable pulao": "সবজি পোলাও",
    "khichdi": "খিচুড়ি", "khichri": "খিচুড়ি",
    "dal khichdi": "ডাল খিচুড়ি", "moong dal khichdi": "মুগ ডাল খিচুড়ি",
    "chicken khichdi": "চিকেন খিচুড়ি",
    "panta bhat": "পান্তা ভাত", "fermented rice": "পান্তা ভাত",
    "curd rice": "দই ভাত", "lemon rice": "লেবু ভাত",
    "coconut rice": "নারকেল ভাত", "spinach rice": "পালং ভাত",
    "tamarind rice": "তেঁতুল ভাত", "tomato rice": "টমেটো ভাত",
    "mishti pulao": "মিষ্টি পোলাও", "sweet pulao": "মিষ্টি পোলাও",
    "basanti pulao": "বসন্তী পোলাও",
    "fish pulao": "মাছ পোলাও", "prawn pulao": "চিংড়ি পোলাও",

    # Breads / Roti
    "roti": "রুটি", "chapati": "চাপাতি", "chapatti": "চাপাতি",
    "whole wheat chapati": "গমের রুটি", "whole wheat roti": "গমের রুটি",
    "phulka": "ফুলকা", "tandoori roti": "তন্দুরি রুটি",
    "naan": "নান", "garlic naan": "রসুন নান",
    "butter naan": "মাখন নান", "cheese naan": "চিজ নান",
    "paratha": "পরাঠা", "aloo paratha": "আলু পরাঠা",
    "gobi paratha": "ফুলকপি পরাঠা", "paneer paratha": "পনির পরাঠা",
    "methi paratha": "মেথি পরাঠা", "onion paratha": "পেঁয়াজ পরাঠা",
    "lachha paratha": "লাচ্ছা পরাঠা",
    "puri": "পুরি", "poori": "পুরি",
    "bhatura": "ভাটুরা", "luchi": "লুচি", "kochuri": "কচুরি",
    "missi roti": "মিশ্রি রুটি", "bajra roti": "বাজরার রুটি",
    "makki ki roti": "মাকইর রুটি", "corn roti": "ভুট্টার রুটি",
    "bread": "পাউরুটি", "white bread": "সাদা পাউরুটি",
    "brown bread": "ব্রাউন পাউরুটি",
    "whole wheat bread": "গমের পাউরুটি",
    "multigrain bread": "মাল্টিগ্রেন পাউরুটি",
    "toast": "টোস্ট", "rusk": "রাস্ক",

    # Dal / Legumes
    "dal": "ডাল", "lentil soup": "মসুর ডালের স্যুপ",
    "moong dal": "মুগ ডাল", "masoor dal": "মসুর ডাল",
    "toor dal": "তুর ডাল", "arhar dal": "অরহর ডাল",
    "chana dal": "ছোলার ডাল", "urad dal": "উড়দ ডাল",
    "mixed dal": "মিক্সড ডাল", "dal soup": "ডালের স্যুপ",
    "dal fry": "ডাল ফ্রাই", "dal tadka": "ডাল তড়কা",
    "dal makhani": "ডাল মাখানি", "dal palak": "ডাল পালং",
    "rajma": "রাজমা", "rajma chawal": "রাজমা ভাত",
    "chole": "ছোলা", "chana masala": "ছোলা মশলা",
    "cholar dal": "ছোলার ডাল",
    "sambhar": "সাম্বার", "sambar": "সাম্বার",
    "rasam": "রসম",
    "dhokla": "ঢোকলা", "dhokar dalna": "ঢোকার ডালনা",
    "ghugni": "ঘুগনি",

    # Vegetables
    "aloo gobi": "আলু ফুলকপি", "aloo matar": "আলু মটর",
    "aloo palak": "আলু পালং", "aloo posto": "আলু পোস্ত",
    "aloo bhaji": "আলু ভাজি", "aloo bhaja": "আলু ভাজা",
    "aloo sabzi": "আলু সবজি", "alur dom": "আলুর দম",
    "aloo dum": "আলুর দম",
    "palak paneer": "পালং পনির", "paneer butter masala": "পনির মাখনি",
    "matar paneer": "মটর পনির", "shahi paneer": "শাহি পনির",
    "paneer tikka": "পনির টিক্কা", "paneer bhurji": "পনির ভুরজি",
    "paneer curry": "পনির কারি", "grilled paneer": "গ্রিল পনির",
    "kadhi": "কাড়ি", "kadhi pakora": "কাড়ি পকোড়া",
    "bhindi fry": "ঢেঁড়স ভাজা", "bhindi masala": "ঢেঁড়স মশলা",
    "baingan bharta": "বেগুন ভর্তা", "baingan masala": "বেগুন মশলা",
    "begun bhaja": "বেগুন ভাজা",
    "lauki sabzi": "লাউ সবজি", "lauki ki sabzi": "লাউ সবজি",
    "lau ghonto": "লাউ ঘন্ট",
    "mocha ghonto": "মোচা ঘন্ট", "banana flower": "মোচা",
    "shukto": "শুক্তো", "mixed vegetable": "মিক্সড ভেজ",
    "mixed veg": "মিক্সড ভেজ", "sabzi": "সবজি",
    "veg curry": "সবজির তরকারি", "vegetable curry": "সবজির তরকারি",
    "cauliflower curry": "ফুলকপির তরকারি",
    "cabbage curry": "বাঁধাকপির তরকারি",
    "spinach curry": "পালং শাকের তরকারি",
    "labra": "লাবড়া", "dalna": "ডালনা",
    "potol posto": "পটল পোস্ত", "posto bata": "পোস্ত বাটা",
    "pumpkin curry": "কুমড়ার তরকারি",
    "bottle gourd curry": "লাউয়ের তরকারি",
    "bitter gourd": "করলা", "karela": "করলা",
    "drumstick curry": "সজনে ডাঁটার তরকারি",
    "jackfruit curry": "কাঁঠালের তরকারি",
    "raw banana curry": "কাঁচা কলার তরকারি",
    "steamed veg": "স্টিম সবজি", "boiled veg": "সেদ্ধ সবজি",
    "roasted veg": "রোস্টেড সবজি",
    "palong saag": "পালং শাক",

    # Chicken
    "chicken curry": "মুরগির ঝোল", "chicken masala": "চিকেন মশলা",
    "chicken tikka masala": "চিকেন টিক্কা মশলা",
    "chicken tikka": "চিকেন টিক্কা", "chicken roast": "চিকেন রোস্ট",
    "chicken do pyaza": "চিকেন দো পেঁয়াজ",
    "chicken korma": "চিকেন কোর্মা",
    "chicken rezala": "চিকেন রেজালা",
    "chicken stew": "চিকেন স্টু",
    "chicken soup": "চিকেন স্যুপ",
    "chicken roll": "চিকেন রোল",
    "chicken sandwich": "চিকেন স্যান্ডউইচ",
    "chicken burger": "চিকেন বার্গার",
    "chicken pizza": "চিকেন পিজা",
    "grilled chicken": "গ্রিল চিকেন",
    "boiled chicken": "সেদ্ধ চিকেন",
    "roasted chicken": "রোস্টেড চিকেন",
    "air fry chicken": "এয়ার ফ্রাই চিকেন",
    "chicken chowmein": "চিকেন চাওমিন",
    "chicken grill": "গ্রিল চিকেন",

    # Mutton / Beef / Pork
    "mutton curry": "মাটন কারি", "mutton masala": "মাটন মশলা",
    "mutton korma": "মাটন কোর্মা", "mutton biryani": "মাটন বিরিয়ানি",
    "mutton rogan josh": "রোগন জোশ",
    "mutton keema": "মাটন কিমা", "keema": "কিমা",
    "keema matar": "কিমা মটর",
    "beef curry": "গরুর মাংসের কারি",

    # Fish
    "fish curry": "মাছের ঝোল", "fish masala": "মাছের মশলা",
    "fish fry": "মাছ ভাজা", "fish kalia": "মাছ কালিয়া",
    "macher jhol": "মাছের ঝোল", "macher bhaja": "মাছ ভাজা",
    "rohu curry": "রুই মাছের ঝোল",
    "katla curry": "কাতলা মাছ", "katla fish": "কাতলা মাছ",
    "hilsa curry": "ইলিশ মাছের ঝোল",
    "shorshe ilish": "সরষে ইলিশ", "ilish bhapa": "ইলিশ ভাপা",
    "bhetki paturi": "ভেটকি পাতুরি",
    "pabda jhol": "পাবদা ঝোল",
    "tangra jhol": "ট্যাংরা ঝোল",
    "air fry fish": "এয়ার ফ্রাই মাছ",
    "fish steam": "স্টিম মাছ", "steamed fish": "স্টিম মাছ",
    "fish broth": "মাছের স্যুপ",
    "prawn curry": "চিংড়ি কারি",
    "chingri malai": "চিংড়ি মালাই",
    "daab chingri": "ডাব চিংড়ি",
    "chingri bhapa": "চিংড়ি ভাপা",
    "chingri bhorta": "চিংড়ি ভর্তা",
    "chingri cutlet": "চিংড়ি কাটলেট",

    # Eggs
    "egg curry": "ডিমের ঝোল", "egg masala": "ডিম মশলা",
    "boiled egg": "সেদ্ধ ডিম", "fried egg": "ডিম ভাজা",
    "scrambled egg": "ডিম ভুরজি", "egg bhurji": "ডিম ভুরজি",
    "omelette": "অমলেট", "egg omelette": "ডিম অমলেট",
    "egg white omelette": "এগ হোয়াইট অমলেট",
    "egg toast": "এগ টোস্ট", "egg sandwich": "ডিম স্যান্ডউইচ",
    "egg devil": "এগ ডেভিল", "egg chowmein": "এগ চাওমিন",
    "egg roll": "এগ রোল",

    # Dairy
    "milk": "দুধ", "full fat milk": "ফুল ফ্যাট দুধ",
    "skimmed milk": "স্কিমড দুধ", "toned milk": "টোনড দুধ",
    "curd": "দই", "yogurt": "দই", "plain yogurt": "সাদা দই",
    "mishti doi": "মিষ্টি দই", "strawberry yogurt": "স্ট্রবেরি দই",
    "paneer": "পনির", "cottage cheese": "পনির",
    "butter": "মাখন", "ghee": "ঘি",
    "cream": "ক্রিম", "ice cream": "আইসক্রিম",
    "cheese": "চিজ", "malai": "মালাই",
    "rabri": "রাবড়ি", "basundi": "বাসুন্দি",
    "khoa": "খোয়া", "khoya": "খোয়া",

    # Breakfast / South Indian
    "idli": "ইডলি", "plain idli": "সাদা ইডলি",
    "rava idli": "রাভা ইডলি", "set dosa": "সেট ডোসা",
    "dosa": "ডোসা", "plain dosa": "সাদা ডোসা",
    "masala dosa": "মশলা ডোসা", "rava dosa": "রাভা ডোসা",
    "uttapam": "উত্তাপম", "appam": "আপ্পম",
    "upma": "উপমা", "rava upma": "রাভা উপমা",
    "poha": "চিড়া", "kanda batata poha": "পেঁয়াজ আলু চিড়া",
    "sabudana khichdi": "সাবুদানা খিচুড়ি",
    "vermicelli upma": "সেমাই উপমা",
    "oats porridge": "ওটস পোরিজ", "oatmeal": "ওটস",
    "oats": "ওটস", "banana oats": "কলা ওটস",
    "granola": "গ্রানোলা", "muesli": "মুসলি",
    "cornflakes": "কর্নফ্লেক্স", "wheat flakes": "গমের ফ্লেক্স",
    "doi chire": "দই চিঁড়ে",

    # Snacks / Street Food
    "samosa": "সমোসা", "veg samosa": "ভেজ সমোসা",
    "singara": "সিঙ্গারা", "aloo singara": "আলু সিঙ্গারা",
    "pakora": "পকোড়া", "pakoda": "পকোড়া",
    "onion pakora": "পেঁয়াজ পকোড়া", "veg pakora": "ভেজ পকোড়া",
    "bread pakora": "পাউরুটি পকোড়া",
    "vada": "বড়া", "medu vada": "মেদু বড়া",
    "dahi vada": "দই বড়া",
    "bhajia": "ভাজিয়া", "beguni": "বেগুনি",
    "jhalmuri": "ঝালমুড়ি", "muri": "মুড়ি",
    "phuchka": "ফুচকা", "pani puri": "পানিপুরি",
    "golgappa": "গোলগাপ্পা",
    "chaat": "চাট", "bhel puri": "ভেলপুরি",
    "sev puri": "সেভপুরি", "papdi chaat": "পাপড়ি চাট",
    "dahi papdi chaat": "দই পাপড়ি চাট",
    "veg chop": "ভেজ চপ", "egg devil": "এগ ডেভিল",
    "chicken roll": "চিকেন রোল", "veg roll": "ভেজ রোল",
    "kathi roll": "কাঠি রোল",
    "chips": "চিপস", "potato chips": "আলু চিপস",
    "french fries": "ফ্রেঞ্চ ফ্রাই",
    "popcorn": "পপকর্ন", "peanuts": "চিনাবাদাম",
    "roasted peanuts": "ভাজা চিনাবাদাম",
    "roasted chana": "ছোলা ভাজা", "chana bhuna": "ছোলা ভুনা",
    "peanut chikki": "চিনাবাদাম চিক্কি",
    "chikki": "চিক্কি", "sesame chikki": "তিলের চিক্কি",
    "murir moa": "মুড়ির মোয়া",
    "energy bar": "এনার্জি বার", "protein bar": "প্রোটিন বার",
    "veg sandwich": "ভেজ স্যান্ডউইচ",
    "nut mix": "বাদাম মিক্স", "seed mix": "সিড মিক্স",
    "namkeen": "নামকিন", "mathri": "মাঠরি",
    "mathuri": "মাঠরি", "khakhra": "খাখরা",
    "chakli": "চক্লি", "murukku": "মুরুকু",
    "papad": "পাপড়", "pappad": "পাপড়",
    "masala vada": "মশলা বড়া",

    # Sweets / Desserts
    "gulab jamun": "গুলাব জামুন", "rasgulla": "রসগোল্লা",
    "sandesh": "সন্দেশ", "nolen gur sandesh": "নলেন গুড় সন্দেশ",
    "rasmalai": "রসমালাই", "kalakand": "কালাকান্দ",
    "halwa": "হালুয়া", "gajar halwa": "গাজর হালুয়া",
    "suji halwa": "সুজির হালুয়া", "sooji halwa": "সুজির হালুয়া",
    "mohan bhog": "মোহন ভোগ",
    "besan halwa": "বেসন হালুয়া",
    "kheer": "পায়েস", "payesh": "পায়েস",
    "rice kheer": "চালের পায়েস", "vermicelli kheer": "সেমাই পায়েস",
    "sewai kheer": "সেমাই পায়েস",
    "ladoo": "লাড্ডু", "besan ladoo": "বেসন লাড্ডু",
    "rava ladoo": "রাভা লাড্ডু",
    "barfi": "বরফি", "kaju barfi": "কাজু বরফি",
    "milk barfi": "দুধের বরফি",
    "peda": "পেড়া", "mathura peda": "মথুরার পেড়া",
    "jalebi": "জিলাপি", "imarti": "ইমার্তি",
    "shrikhand": "শ্রীখণ্ড", "basundi": "বাসুন্দি",
    "rabri": "রাবড়ি", "kulfi": "কুলফি",
    "ice cream": "আইসক্রিম",
    "gajar ka halwa": "গাজর হালুয়া",
    "payasam": "পায়েস",
    "patishapta": "পাটিসাপটা", "bhapa pitha": "ভাপা পিঠা",
    "chitoi pitha": "চিতই পিঠা", "pitha": "পিঠা",
    "gujia": "গুজিয়া", "ghujia": "গুজিয়া",
    "lavang latika": "লবঙ্গলতিকা",
    "modak": "মোদক", "puran poli": "পুরণ পোলি",
    "thepla": "থেপলা",

    # Soups
    "veg soup": "সবজির স্যুপ", "vegetable soup": "সবজির স্যুপ",
    "tomato soup": "টমেটো স্যুপ", "dal soup": "ডালের স্যুপ",
    "mixed veg soup": "মিক্সড ভেজ স্যুপ",
    "bone broth": "বোন ব্রথ", "chicken broth": "চিকেন ব্রথ",
    "bone broth chicken": "চিকেন বোন ব্রথ",
    "weight loss soup": "ওজন কমানোর স্যুপ",

    # Salads
    "fruit salad": "ফল সালাদ", "green salad": "সবুজ সালাদ",
    "sprouts salad": "স্প্রাউটস সালাদ",
    "moong sprouts": "মুগ স্প্রাউটস",
    "chickpea salad": "ছোলা সালাদ",
    "boiled chicken salad": "সেদ্ধ চিকেন সালাদ",
    "gym salad": "জিম সালাদ", "raita": "রায়তা",
    "boondi raita": "বুন্দি রায়তা",

    # Fruits
    "banana": "কলা", "apple": "আপেল", "mango": "আম",
    "orange": "কমলালেবু", "papaya": "পেঁপে", "guava": "পেয়ারা",
    "watermelon": "তরমুজ", "pineapple": "আনারস",
    "grapes": "আঙুর", "pomegranate": "ডালিম",
    "litchi": "লিচু", "kiwi": "কিউই",
    "strawberry": "স্ট্রবেরি", "blueberry": "ব্লুবেরি",
    "jackfruit": "কাঁঠাল", "coconut": "নারকেল",
    "raw mango": "কাঁচা আম", "ripe mango": "পাকা আম",
    "dates": "খেজুর", "figs": "ডুমুর", "raisins": "কিশমিশ",
    "mixed fruit": "মিশ্র ফল", "fruit bowl": "ফল বোল",
    "mixed fruit bowl": "ফল বোল",

    # Nuts / Seeds
    "almonds": "বাদাম", "almond": "বাদাম",
    "cashew": "কাজু", "cashews": "কাজু",
    "walnuts": "আখরোট", "walnut": "আখরোট",
    "pistachios": "পেস্তা", "pistachio": "পেস্তা",
    "peanuts": "চিনাবাদাম", "peanut": "চিনাবাদাম",
    "sunflower seeds": "সূর্যমুখীর বিচি",
    "chia seeds": "চিয়া বিজ",
    "flaxseeds": "তিসি", "pumpkin seeds": "কুমড়ার বিচি",
    "sesame seeds": "তিল",

    # Chutney / Condiments
    "tomato chutney": "টমেটো চাটনি",
    "aam chutney": "আমের চাটনি", "mango chutney": "আমের চাটনি",
    "green chutney": "সবুজ চাটনি",
    "tamarind chutney": "তেঁতুলের চাটনি",
    "tomato ketchup": "টমেটো কেচাপ",
    "mayonnaise": "মেয়োনিজ",
    "coconut chutney": "নারকেল চাটনি",
    "pickle": "আচার",

    # Noodles / Chinese
    "chowmein": "চাওমিন", "noodles": "নুডলস",
    "hakka noodles": "হক্কা নুডলস",
    "schezwan noodles": "সেজুয়ান নুডলস",
    "pasta": "পাস্তা",

    # Special / Diet
    "high protein bowl": "প্রোটিন বোল",
    "low carb bowl": "লো কার্ব বোল",
    "detox bowl": "ডিটক্স বোল",
    "fitness bowl": "ফিটনেস বোল",
    "wellness bowl": "ওয়েলনেস বোল",
    "lean chicken bowl": "লিন চিকেন বোল",
    "lean fish bowl": "লিন মাছ বোল",
    "protein khichdi": "প্রোটিন খিচুড়ি",
    "infinity wellness bowl": "ইনফিনিটি ওয়েলনেস বোল",
    "fat burn drink": "ফ্যাট বার্ন ড্রিংক",
    "weight loss soup": "ওজন কমানোর স্যুপ",
    "balanced diet bowl": "ব্যালান্সড ডায়েট বোল",
}

BN_WORD = {
    # Core ingredients
    "rice": "ভাত", "dal": "ডাল", "lentil": "মসুর",
    "bread": "পাউরুটি", "roti": "রুটি", "chapati": "চাপাতি",
    "naan": "নান", "paratha": "পরাঠা", "puri": "পুরি",
    "chicken": "চিকেন", "mutton": "মাটন", "beef": "গরু",
    "pork": "শূকর", "fish": "মাছ", "prawn": "চিংড়ি",
    "shrimp": "চিংড়ি", "crab": "কাঁকড়া",
    "egg": "ডিম", "milk": "দুধ", "curd": "দই",
    "yogurt": "দই", "paneer": "পনির", "butter": "মাখন",
    "ghee": "ঘি", "oil": "তেল", "cream": "ক্রিম",
    "potato": "আলু", "onion": "পেঁয়াজ", "tomato": "টমেটো",
    "spinach": "পালং", "carrot": "গাজর", "cauliflower": "ফুলকপি",
    "cabbage": "বাঁধাকপি", "peas": "মটর", "beans": "শিম",
    "okra": "ঢেঁড়স", "eggplant": "বেগুন", "brinjal": "বেগুন",
    "pumpkin": "কুমড়া", "gourd": "লাউ",
    "banana": "কলা", "apple": "আপেল", "mango": "আম",
    "orange": "কমলা", "guava": "পেয়ারা", "watermelon": "তরমুজ",
    "coconut": "নারকেল", "dates": "খেজুর",
    "almond": "বাদাম", "cashew": "কাজু", "walnut": "আখরোট",
    "peanut": "চিনাবাদাম", "peanuts": "চিনাবাদাম",
    "oats": "ওটস", "wheat": "গম", "corn": "ভুট্টা",
    "millet": "বাজরা", "sugar": "চিনি", "salt": "লবণ",
    "spice": "মশলা", "ginger": "আদা", "garlic": "রসুন",
    "lemon": "লেবু", "tamarind": "তেঁতুল",
    # Cooking methods
    "fried": "ভাজা", "boiled": "সেদ্ধ", "grilled": "গ্রিল",
    "roasted": "রোস্টেড", "steamed": "স্টিম", "baked": "বেক",
    "curry": "তরকারি", "masala": "মশলা", "fry": "ভাজা",
    "bhaja": "ভাজা", "jhol": "ঝোল",
    # Beverages
    "tea": "চা", "coffee": "কফি", "water": "জল",
    "juice": "রস", "shake": "শেক", "lassi": "লাচ্ছি",
    "buttermilk": "ঘোল", "soup": "স্যুপ",
    # Meals
    "biryani": "বিরিয়ানি", "pulao": "পোলাও",
    "khichdi": "খিচুড়ি", "dosa": "ডোসা", "idli": "ইডলি",
    "upma": "উপমা", "poha": "চিড়া",
    "samosa": "সমোসা", "pakora": "পকোড়া",
    "halwa": "হালুয়া", "kheer": "পায়েস",
    "ladoo": "লাড্ডু", "barfi": "বরফি",
    "salad": "সালাদ", "chaat": "চাট",
    "sandwich": "স্যান্ডউইচ", "roll": "রোল",
    "chowmein": "চাওমিন", "noodles": "নুডলস",
    "raita": "রায়তা", "chutney": "চাটনি",
    "sweet": "মিষ্টি", "light": "হালকা",
    "plain": "সাদা", "white": "সাদা", "brown": "বাদামি",
    "mixed": "মিশ্র", "veg": "সবজি", "sprouts": "স্প্রাউটস",
    "protein": "প্রোটিন", "fitness": "ফিটনেস",
    "bowl": "বোল", "plate": "প্লেট",
    "healthy": "স্বাস্থ্যকর",
}

# ─── Category Classification ──────────────────────────────────────────────────

CAT_RULES = [
    # (keyword_lower, category)
    ("biryani", "rice"), ("pulao", "rice"), ("khichdi", "rice"),
    ("fried rice", "rice"), ("panta bhat", "rice"), ("curd rice", "rice"),
    ("lemon rice", "rice"), ("coconut rice", "rice"),
    ("roti", "roti"), ("chapati", "roti"), ("paratha", "roti"),
    ("naan", "roti"), ("puri", "roti"), ("poori", "roti"),
    ("bhatura", "roti"), ("luchi", "roti"), ("kochuri", "roti"),
    ("bread", "roti"), ("phulka", "roti"),
    ("dal", "dal"), ("lentil", "dal"),
    ("sambhar", "dal"), ("sambar", "dal"), ("rasam", "dal"),
    ("rajma", "dal"), ("chole", "dal"), ("chana", "dal"),
    ("ghugni", "dal"), ("dhokla", "dal"),
    ("fish", "fish"), ("macher", "fish"), ("ilish", "fish"),
    ("hilsa", "fish"), ("rohu", "fish"), ("katla", "fish"),
    ("pabda", "fish"), ("tangra", "fish"), ("bhetki", "fish"),
    ("chingri", "fish"), ("prawn", "fish"), ("shrimp", "fish"),
    ("crab", "fish"),
    ("chicken", "meat"), ("mutton", "meat"), ("beef", "meat"),
    ("pork", "meat"), ("keema", "meat"),
    ("egg", "protein"),
    ("spinach", "vegetable"), ("palak", "vegetable"),
    ("aloo", "vegetable"), ("potato", "vegetable"),
    ("cauliflower", "vegetable"), ("gobi", "vegetable"),
    ("cabbage", "vegetable"), ("baingan", "vegetable"),
    ("eggplant", "vegetable"), ("brinjal", "vegetable"),
    ("bhindi", "vegetable"), ("okra", "vegetable"),
    ("lauki", "vegetable"), ("bottle gourd", "vegetable"),
    ("pumpkin", "vegetable"), ("bitter gourd", "vegetable"),
    ("karela", "vegetable"), ("drumstick", "vegetable"),
    ("jackfruit", "vegetable"), ("sabzi", "vegetable"),
    ("shukto", "vegetable"), ("labra", "vegetable"),
    ("paneer", "dairy"), ("milk", "dairy"), ("curd", "dairy"),
    ("yogurt", "dairy"), ("butter", "dairy"), ("ghee", "dairy"),
    ("cream", "dairy"), ("rabri", "dairy"), ("basundi", "dairy"),
    ("cheese", "dairy"), ("khoya", "dairy"), ("khoa", "dairy"),
    # Sweets / Desserts — BEFORE drink rules so "Coffee cake" → sweets, not beverage
    ("halwa", "sweets"), ("kheer", "sweets"), ("payesh", "sweets"),
    ("ladoo", "sweets"), ("barfi", "sweets"), ("sandesh", "sweets"),
    ("rasgulla", "sweets"), ("gulab jamun", "sweets"),
    ("jalebi", "sweets"), ("peda", "sweets"), ("modak", "sweets"),
    ("pitha", "sweets"), ("rasmalai", "sweets"),
    ("gujia", "sweets"), ("kalakand", "sweets"),
    ("mishti", "sweets"), ("sweet", "sweets"),
    ("cake", "sweets"), ("cookie", "sweets"), ("pudding", "sweets"),
    ("custard", "sweets"), ("mousse", "sweets"), ("sorbet", "sweets"),
    ("ice cream", "sweets"), ("icecream", "sweets"),
    ("brownie", "sweets"), ("donut", "sweets"), ("tart", "sweets"),
    # Snacks — BEFORE drink rules so "Coffee biscuit" → snack, not beverage
    ("samosa", "snack"), ("pakora", "snack"), ("pakoda", "snack"),
    ("vada", "snack"), ("bhajia", "snack"), ("bhaji", "snack"),
    ("chips", "snack"), ("fries", "snack"), ("popcorn", "snack"),
    ("namkeen", "snack"), ("mathri", "snack"), ("chakli", "snack"),
    ("chikki", "snack"), ("murir moa", "snack"),
    ("energy bar", "snack"), ("protein bar", "snack"),
    ("sandwich", "snack"), ("roll", "snack"), ("chaat", "snack"),
    ("phuchka", "snack"), ("jhalmuri", "snack"),
    ("singara", "snack"), ("chop", "snack"),
    ("pizza", "snack"), ("burger", "snack"), ("hotdog", "snack"),
    ("biscuit", "snack"), ("muffin", "snack"), ("cracker", "snack"),
    ("rusk", "snack"), ("crisp", "snack"), ("snack", "snack"),
    # Noodles
    ("noodles", "noodle"), ("chowmein", "noodle"), ("pasta", "noodle"),
    ("spaghetti", "noodle"), ("macaroni", "noodle"), ("vermicelli", "noodle"),
    # Breakfast items
    ("oats", "breakfast"), ("idli", "breakfast"),
    ("dosa", "breakfast"), ("upma", "breakfast"),
    ("poha", "breakfast"), ("uttapam", "breakfast"),
    ("appam", "breakfast"), ("granola", "breakfast"),
    ("cornflakes", "breakfast"), ("cornflake", "breakfast"),
    ("cereal", "breakfast"), ("waffle", "breakfast"), ("pancake", "breakfast"),
    ("toast", "breakfast"),
    # Beverages — AFTER food-type rules
    ("tea", "beverage"), ("coffee", "beverage"), ("juice", "beverage"),
    ("lassi", "beverage"), ("buttermilk", "beverage"),
    ("shake", "beverage"), ("sharbat", "beverage"),
    ("cooler", "beverage"), ("chaas", "beverage"),
    ("water", "beverage"), ("sherbet", "beverage"),
    # Fruits / Nuts / Grains
    ("banana", "fruit"), ("apple", "fruit"), ("mango", "fruit"),
    ("orange", "fruit"), ("papaya", "fruit"), ("guava", "fruit"),
    ("watermelon", "fruit"), ("pineapple", "fruit"),
    ("grape", "fruit"), ("pomegranate", "fruit"),
    ("litchi", "fruit"), ("kiwi", "fruit"),
    ("strawberry", "fruit"), ("dates", "fruit"),
    ("coconut", "fruit"),
    ("almond", "nut"), ("cashew", "nut"), ("walnut", "nut"),
    ("pistachio", "nut"), ("peanut", "nut"),
    ("seed mix", "nut"), ("nut mix", "nut"),
    ("soup", "soup"), ("broth", "soup"),
    ("salad", "salad"), ("raita", "salad"),
    ("rice", "grain"), ("wheat", "grain"),
]

_CAT_PATTERNS = [(re.compile(r'\b' + re.escape(kw) + r'\b'), cat) for kw, cat in CAT_RULES]

def classify(name: str) -> str:
    n = name.lower()
    for pat, cat in _CAT_PATTERNS:
        if pat.search(n):
            return cat
    return "other"

# ─── Bengali Translation ──────────────────────────────────────────────────────

# Phonetic transliteration map (English clusters → Bengali)
PHON = [
    ("kha", "খা"), ("khi", "খি"), ("khu", "খু"), ("khe", "খে"), ("kho", "খো"), ("kh", "খ"),
    ("gha", "ঘা"), ("ghi", "ঘি"), ("ghu", "ঘু"), ("ghe", "ঘে"), ("gho", "ঘো"), ("gh", "ঘ"),
    ("cha", "চা"), ("chi", "চি"), ("chu", "চু"), ("che", "চে"), ("cho", "চো"), ("ch", "চ"),
    ("jha", "ঝা"), ("jhi", "ঝি"), ("jhu", "ঝু"), ("jhe", "ঝে"), ("jho", "ঝো"), ("jh", "ঝ"),
    ("sha", "শা"), ("shi", "শি"), ("shu", "শু"), ("she", "শে"), ("sho", "শো"), ("sh", "শ"),
    ("tha", "থা"), ("thi", "থি"), ("thu", "থু"), ("the", "থে"), ("tho", "থো"), ("th", "থ"),
    ("dha", "ধা"), ("dhi", "ধি"), ("dhu", "ধু"), ("dhe", "ধে"), ("dho", "ধো"), ("dh", "ধ"),
    ("bha", "ভা"), ("bhi", "ভি"), ("bhu", "ভু"), ("bhe", "ভে"), ("bho", "ভো"), ("bh", "ভ"),
    ("pha", "ফা"), ("phi", "ফি"), ("phu", "ফু"), ("phe", "ফে"), ("pho", "ফো"), ("ph", "ফ"),
    ("aa", "আ"), ("ai", "আই"), ("au", "আউ"), ("ou", "উ"),
    ("ee", "ি"), ("oo", "ু"),
    ("a", "া"), ("e", "ে"), ("i", "ি"), ("o", "ো"), ("u", "ু"),
    ("b", "ব"), ("c", "ক"), ("d", "দ"), ("f", "ফ"), ("g", "গ"),
    ("h", "হ"), ("j", "জ"), ("k", "ক"), ("l", "ল"), ("m", "ম"),
    ("n", "ন"), ("p", "প"), ("q", "ক"), ("r", "র"), ("s", "স"),
    ("t", "ত"), ("v", "ভ"), ("w", "ও"), ("x", "ক্স"), ("y", "য"), ("z", "জ"),
]

def _translit_word(word: str) -> str:
    """Phonetic transliteration: English word → Bengali script (approximate)."""
    s = word.lower()
    out = ""
    i = 0
    while i < len(s):
        matched = False
        for pat, rep in PHON:
            if s[i:i+len(pat)] == pat:
                out += rep
                i += len(pat)
                matched = True
                break
        if not matched:
            out += s[i]
            i += 1
    return out

def translate_to_bn(en_name: str) -> str:
    """Generate Bengali name for an English food name."""
    lower = en_name.lower().strip()

    # 1. Strip parenthetical alternate names and try exact match
    core = re.sub(r'\s*\(.*?\)\s*', ' ', lower).strip()
    for phrase in (lower, core):
        if phrase in BN_PHRASE:
            return BN_PHRASE[phrase]

    # 2. Try stripping common parenthetical suffixes
    for phrase in (lower, core):
        # remove trailing parenthetical
        stripped = re.sub(r'\s*\(.*', '', phrase).strip()
        if stripped in BN_PHRASE:
            return BN_PHRASE[stripped]

    # 3. Word-by-word translation
    words = core.split()
    translated = []
    skip_next = False
    for idx, w in enumerate(words):
        if skip_next:
            skip_next = False
            continue
        # try bigram first
        if idx + 1 < len(words):
            bigram = w + " " + words[idx + 1]
            if bigram in BN_PHRASE:
                translated.append(BN_PHRASE[bigram])
                skip_next = True
                continue
            if bigram in BN_WORD:
                translated.append(BN_WORD[bigram])
                skip_next = True
                continue
        if w in BN_WORD:
            translated.append(BN_WORD[w])
        elif w in BN_PHRASE:
            translated.append(BN_PHRASE[w])
        else:
            # Phonetic transliteration for unknown words
            translated.append(_translit_word(w))
    if translated:
        return " ".join(translated)

    # 4. Full phonetic transliteration
    return " ".join(_translit_word(w) for w in core.split())

# ─── Keyword Generation ───────────────────────────────────────────────────────

STOP_WORDS = {
    "the", "a", "an", "in", "on", "with", "and", "or", "of", "for",
    "to", "is", "it", "its", "at", "by", "as", "from", "that",
    "plain", "simple", "regular", "mixed", "light", "healthy",
}

def gen_keywords(en: str, bn: str, cat: str) -> list:
    kws = set()
    # English tokens
    for token in re.findall(r"[a-z]+", en.lower()):
        if len(token) >= 3 and token not in STOP_WORDS:
            kws.add(token)
    # Category
    if cat and cat != "other":
        kws.add(cat)
    # First word of bn (romanized hint)
    first_en = en.split()[0].lower()
    if first_en not in STOP_WORDS:
        kws.add(first_en)
    return sorted(kws)[:8]  # cap at 8 keywords

# ─── Serving Size Normalisation ───────────────────────────────────────────────

SERVING_MAP = {
    "tea cup": "1 cup", "cup": "1 cup", "small cup": "1 cup",
    "tall glass": "1 glass", "glass": "1 glass",
    "bowl": "1 bowl", "small bowl": "1 bowl",
    "plate": "1 plate", "thali": "1 plate",
    "piece": "1 pc", "pc": "1 pc", "pcs": "1 pc",
    "poori": "1 pc", "bhatura": "1 pc", "roti": "1 pc",
    "idli": "1 pc", "dosa": "1 pc", "puri": "1 pc",
    "paratha": "1 pc", "vada": "1 pc", "luchi": "1 pc",
    "cheela": "1 pc", "chilla": "1 pc",
    "muthia": "1 serving", "toast": "1 pc",
    "kachori": "1 pc", "gunjia": "1 pc",
    "": "100g",
}

def norm_serving(unit: str) -> str:
    if not unit:
        return "100g"
    u = str(unit).lower().strip()
    return SERVING_MAP.get(u, f"1 {u}")

# ─── Load bengalifood.txt ─────────────────────────────────────────────────────

def load_bengali_food(path: str) -> list:
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    # File has multiple JSON arrays separated by blank lines
    items = []
    for chunk in re.split(r'\]\s*\[', raw):
        chunk = chunk.strip().lstrip('[').rstrip(']').strip()
        if not chunk:
            continue
        try:
            arr = json.loads('[' + chunk + ']')
            items.extend(arr)
        except json.JSONDecodeError:
            # Try to parse each line separately
            for line in chunk.splitlines():
                line = line.strip().rstrip(',')
                if line.startswith('{') and line.endswith('}'):
                    try:
                        items.append(json.loads(line))
                    except Exception:
                        pass
    return items

# ─── Load INDB XLSX ───────────────────────────────────────────────────────────

def safe_float(v, default=0.0) -> float:
    if v is None:
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default

def nullable_float(v) -> float:
    """Returns the positive numeric value, or 0.0 if absent / zero / invalid.
    Used for vitamins — callers write the key only when result > 0,
    so 0.0 means "data not available" (key is omitted from JSON).
    """
    if v is None:
        return 0.0
    try:
        f = float(v)
        return f if f >= 0.01 else 0.0
    except (ValueError, TypeError):
        return 0.0

def load_indb(path: str) -> list:
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()

    header = [str(h).lower().strip() if h else '' for h in rows[0]]
    ci = {h: i for i, h in enumerate(header)}

    def gcv(row, name):
        """Safely fetch a column value by header name; None if column absent."""
        idx = ci.get(name)
        if idx is None:
            return None
        try:
            return row[idx]
        except (IndexError, TypeError):
            return None

    items = []
    for row in rows[1:]:
        code = str(row[ci.get('food_code', 0)] or '').strip()
        name = str(row[ci.get('food_name', 1)] or '').strip()
        if not name or name.lower() in ('nan', 'none', ''):
            continue

        # ── Per-100g macros ───────────────────────────────────────────────────
        kcal_100 = safe_float(row[ci.get('energy_kcal', 4)])
        carb_100  = safe_float(row[ci.get('carb_g', 5)])
        prot_100  = safe_float(row[ci.get('protein_g', 6)])
        fat_100   = safe_float(row[ci.get('fat_g', 7)])
        fibre_100 = safe_float(row[ci.get('fibre_g', 9)])
        ca_100    = safe_float(row[ci.get('calcium_mg', 14)])
        fe_100    = safe_float(row[ci.get('iron_mg', 19)])
        zn_100    = safe_float(row[ci.get('zinc_mg', 25)])

        # ── Per-100g vitamins & minerals (absent columns → 0.0 = omitted) ────
        va_100  = nullable_float(gcv(row, 'vita_ug'))
        vc_100  = nullable_float(gcv(row, 'vitc_mg'))
        vd_100  = (nullable_float(gcv(row, 'vitd2_ug'))
                   + nullable_float(gcv(row, 'vitd3_ug')))
        mg_100  = nullable_float(gcv(row, 'magnesium_mg'))
        pot_100 = nullable_float(gcv(row, 'potassium_mg'))

        # ── Per-serving macros ────────────────────────────────────────────────
        srv_unit  = str(row[ci.get('servings_unit', 42)] or '').strip()
        kcal_srv  = safe_float(row[ci.get('unit_serving_energy_kcal', 44)])
        carb_srv  = safe_float(row[ci.get('unit_serving_carb_g', 45)])
        prot_srv  = safe_float(row[ci.get('unit_serving_protein_g', 46)])
        fat_srv   = safe_float(row[ci.get('unit_serving_fat_g', 47)])
        fibre_srv = safe_float(row[ci.get('unit_serving_fibre_g', 49)])
        ca_srv    = safe_float(row[ci.get('unit_serving_calcium_mg', 54)])
        fe_srv    = safe_float(row[ci.get('unit_serving_iron_mg', 59)])
        zn_srv    = safe_float(row[ci.get('unit_serving_zinc_mg', 65)])

        # ── Per-serving vitamins & minerals ───────────────────────────────────
        va_srv  = nullable_float(gcv(row, 'unit_serving_vita_ug'))
        vc_srv  = nullable_float(gcv(row, 'unit_serving_vitc_mg'))
        vd_srv  = (nullable_float(gcv(row, 'unit_serving_vitd2_ug'))
                   + nullable_float(gcv(row, 'unit_serving_vitd3_ug')))
        mg_srv  = nullable_float(gcv(row, 'unit_serving_magnesium_mg'))
        pot_srv = nullable_float(gcv(row, 'unit_serving_potassium_mg'))

        # ── Choose per-serving or per-100g ────────────────────────────────────
        if srv_unit and kcal_srv > 0:
            k, p, c, fa, fi = kcal_srv, prot_srv, carb_srv, fat_srv, fibre_srv
            ca, fe, zn = ca_srv, fe_srv, zn_srv
            va, vc, vd, mg, pot = va_srv, vc_srv, vd_srv, mg_srv, pot_srv
            s = norm_serving(srv_unit)
        else:
            k, p, c, fa, fi = kcal_100, prot_100, carb_100, fat_100, fibre_100
            ca, fe, zn = ca_100, fe_100, zn_100
            va, vc, vd, mg, pot = va_100, vc_100, vd_100, mg_100, pot_100
            s = "100g"

        # Skip rows with no meaningful nutrition
        if k < 0.1 and p < 0.1 and c < 0.1:
            continue

        # Clean the English name
        clean_name = name
        if '(' in name:
            short = re.sub(r'\s*\(.*\)\s*$', '', name).strip()
            if len(short) >= 3:
                clean_name = short

        en  = clean_name
        bn  = translate_to_bn(name)
        cat = classify(clean_name)
        kw  = gen_keywords(clean_name, bn, cat)

        item = {
            '_code': code,
            'en': en,
            'bn': bn,
            's':  s,
            'k':  round(k,  1),
            'p':  round(p,  1),
            'c':  round(c,  1),
            'f':  round(fa, 1),
            'fi': round(fi, 1),
            'ca': round(ca, 1),
            'fe': round(fe, 2),
            'zn': round(zn, 2),
            'cat': cat,
            'kw':  kw,
            'src': 'indb',
        }
        # Only write vitamin/mineral keys when source data is actually present.
        # Absent key in JSON → null in Dart map → FoodItem field stays null →
        # dashboard excludes it from totals → UI never shows misleading zero.
        _va, _vc, _vd, _mg, _pot = round(va, 1), round(vc, 1), round(vd, 2), round(mg, 1), round(pot, 1)
        if _va  > 0: item['va']  = _va
        if _vc  > 0: item['vc']  = _vc
        if _vd  > 0: item['vd']  = _vd
        if _mg  > 0: item['mg']  = _mg
        if _pot > 0: item['pot'] = _pot
        items.append(item)

    return items

# ─── Merge & Deduplicate ──────────────────────────────────────────────────────

def normalize_key(name: str) -> str:
    """Lowercase, remove punctuation, collapse spaces — used for dedup."""
    n = name.lower().strip()
    n = re.sub(r'[^a-z0-9 ]', ' ', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def merge_datasets(bf_items: list, indb_items: list) -> list:
    seen = {}  # normalized_key → item

    # Priority 1: bengalifood items (already have verified Bengali names)
    for item in bf_items:
        en = item.get('en', '')
        if not en:
            continue
        key = normalize_key(en)
        merged = {
            'en': en,
            'bn': item.get('bn', translate_to_bn(en)),
            's':  item.get('s', '100g'),
            'k':  float(item.get('k', 0)),
            'p':  float(item.get('p', 0)),
            'c':  float(item.get('c', 0)),
            'f':  float(item.get('f', 0)),
            'fi': float(item.get('fi', 0)),
            'ca': float(item.get('ca', 0)),
            'fe': float(item.get('fe', 0)),
            'zn': float(item.get('zn', 0)),
            'cat': item.get('cat', classify(en)),
            'kw': item.get('kw', gen_keywords(en, item.get('bn', ''), item.get('cat', ''))),
            'src': 'local',
        }
        for vkey in ('va', 'vc', 'vd', 'mg', 'pot'):
            if vkey in item:
                merged[vkey] = item[vkey]
        seen[key] = merged

    # Priority 2: INDB items — skip if name already covered
    for item in indb_items:
        en = item.get('en', '')
        if not en:
            continue
        key = normalize_key(en)

        # Also try matching against existing keys with fuzzy-ish match
        if key in seen:
            continue

        # Check partial overlaps (e.g., "Hot tea (Garam Chai)" vs "Milk Tea")
        found = False
        for existing_key in seen:
            # If first two significant words match, consider duplicate
            ek_words = existing_key.split()[:2]
            nk_words = key.split()[:2]
            if ek_words and nk_words and ek_words == nk_words:
                found = True
                break
        if found:
            continue

        indb_merged = {
            'en': item['en'],
            'bn': item['bn'],
            's':  item['s'],
            'k':  item['k'],
            'p':  item['p'],
            'c':  item['c'],
            'f':  item['f'],
            'fi': item['fi'],
            'ca': item['ca'],
            'fe': item['fe'],
            'zn': item['zn'],
            'cat': item['cat'],
            'kw': item['kw'],
            'src': item['src'],
        }
        for vkey in ('va', 'vc', 'vd', 'mg', 'pot'):
            if vkey in item:
                indb_merged[vkey] = item[vkey]
        seen[key] = indb_merged

    # Sort by category then English name
    all_items = list(seen.values())
    all_items.sort(key=lambda x: (x.get('cat', 'zzz'), x.get('en', '')))

    # Assign sequential IDs
    for i, item in enumerate(all_items, start=1):
        item['id'] = i

    return all_items

# ─── Build Search Indexes ─────────────────────────────────────────────────────

def build_index(items: list, key: str, is_bn: bool = False) -> dict:
    """Build prefix index: 2-char prefix → sorted list of IDs."""
    index = defaultdict(list)
    for item in items:
        name = item.get(key, '')
        if not name:
            continue
        # Index each word in the name
        if is_bn:
            # Bengali: split on spaces, use first 2 Unicode chars as prefix
            for word in name.split():
                w = word.strip()
                if len(w) >= 1:
                    prefix = w[:2]  # 2 Unicode codepoints
                    index[prefix].append(item['id'])
        else:
            # English: 2-char and 3-char prefixes of each word
            for word in re.findall(r'[a-z]+', name.lower()):
                if len(word) >= 2:
                    index[word[:2]].append(item['id'])
                if len(word) >= 3:
                    index[word[:3]].append(item['id'])

    # Deduplicate and sort each list
    return {k: sorted(set(v)) for k, v in index.items()}

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Step 1/4  Loading bengalifood.txt …")
    bf = load_bengali_food(BF_PATH)
    print(f"          Loaded {len(bf)} Bengali-food items")

    print("Step 2/4  Loading Anuvaad INDB xlsx …")
    indb = load_indb(INDB_PATH)
    print(f"          Loaded {len(indb)} INDB items")

    print("Step 3/4  Merging & deduplicating …")
    master = merge_datasets(bf, indb)
    print(f"          Unified dataset: {len(master)} unique items")

    # Strip internal '_code'/'src' fields before writing (keep src for info)
    for item in master:
        item.pop('_code', None)

    print("Step 4/4  Building search indexes …")
    idx_en = build_index(master, 'en', is_bn=False)
    idx_bn = build_index(master, 'bn', is_bn=True)
    print(f"          English index: {len(idx_en)} prefix buckets")
    print(f"          Bengali index:  {len(idx_bn)} prefix buckets")

    # ── Write outputs ──────────────────────────────────────────────────────
    with open(MASTER_PATH, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, separators=(',', ':'))
    print(f"\n[OK] {MASTER_PATH}")

    with open(IDX_EN_PATH, 'w', encoding='utf-8') as f:
        json.dump(idx_en, f, ensure_ascii=False, separators=(',', ':'))
    print(f"[OK] {IDX_EN_PATH}")

    with open(IDX_BN_PATH, 'w', encoding='utf-8') as f:
        json.dump(idx_bn, f, ensure_ascii=False, separators=(',', ':'))
    print(f"[OK] {IDX_BN_PATH}")

    # ── Stats ──────────────────────────────────────────────────────────────
    cats = defaultdict(int)
    for item in master:
        cats[item.get('cat', 'other')] += 1
    print("\nCategory breakdown:")
    for cat, count in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"  {cat:15s} {count:4d}")

    sizes = {
        'food_master_v5_3.json': os.path.getsize(MASTER_PATH),
        'index_en_v5_3.json':    os.path.getsize(IDX_EN_PATH),
        'index_bn_v5_3.json':    os.path.getsize(IDX_BN_PATH),
    }
    print("\nFile sizes:")
    for fname, size in sizes.items():
        print(f"  {fname}: {size/1024:.1f} KB")

if __name__ == '__main__':
    main()
