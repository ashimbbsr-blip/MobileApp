"""Fix Bengali name collisions and add Odia traditional foods."""
import json, sys, uuid
sys.stdout.reconfigure(encoding='utf-8')

MASTER   = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v5_3.json'
INDEX_EN = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_en_v5_3.json'
INDEX_BN = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_bn_v5_3.json'

# ── 1. Remove true duplicates (EN name → reason) ─────────────────────────────
REMOVE_EN = {
    'Jeera Water',             # duplicate of Cumin infused water, less data
    'Potato fry (Alu bhaja)', # duplicate of Aloo Bhaja
    'Rasgulla',                # duplicate of Rasgulla (Rosogolla)
    'Walnuts Akhrot',          # bd_fct entry with corrupted data (k=2820)
    'Fish curry',              # duplicate of Macher Jhol (same dish, same BN)
}

# ── 2. Fix Bengali names on items that share BN with another item ─────────────
# (EN, new_bn)
BN_FIXES = [
    # Lassi pair
    ('Lassi',                                       'লাচ্ছি (প্লেইন)'),
    ('Sweet Lassi',                                 'মিষ্টি লাচ্ছি'),
    # Egg pair
    ('Egg Bhurji',                                  'ডিম ভুরজি'),
    ('Scrambled egg',                               'স্ক্র্যাম্বল্ড ডিম'),
    # Chicken salad pair
    ('Chicken salad',                               'চিকেন সালাদ (ক্রিমি)'),
    ('Boiled Chicken Salad',                        'সেদ্ধ চিকেন সালাদ'),
    # Veg pair
    ('Boiled Veg Mix',                              'সেদ্ধ মিক্সড সবজি'),
    ('Mixed Veg',                                   'মিক্সড সবজি তরকারি'),
    # Poha / raw flakes pair
    ('Poha',                                        'পোহা (রান্না)'),
    ('Rice flakes, white grain, raw',               'চিড়া, কাঁচা'),
    # Puffed rice pair
    ('Puffed rice (Muri / Mudi)',                   'মুড়ি'),
    ('Rice, puffed, salted',                        'মুড়ি, লবণযুক্ত'),
    # Lentil pair
    ('Masoor Dal',                                  'মসুর ডালের তরকারি'),
    ('Lentil, dried, raw',                          'মসুর ডাল, শুকনো'),
    # Cabbage pair
    ('Cabbage Curry',                               'বাঁধাকপির তরকারি'),
    ('Cabbage, raw',                                'বাঁধাকপি, কাঁচা'),
    # Bitter gourd pair
    ('Fried bitter gourd (Karla bhaja)',             'করলা ভাজা'),
    ('Gourd, bitter, fry',                          'উচ্ছে ভাজা'),
    # Spinach pair
    ('Palong Saag',                                 'পালং শাকের তরকারি'),
    ('Spinach, raw',                                'পালং শাক, কাঁচা'),
    # Guava pair
    ('Guava',                                       'পেয়ারা'),
    ('Guava, green, raw',                           'পেয়ারা, কাঁচা'),
    # Katla pair
    ('Katla Curry',                                 'কাতলা মাছের তরকারি'),
    ('Catla, raw',                                  'কাতলা মাছ, কাঁচা'),
    # Native egg pair (raw vs boiled)
    ('Egg, chicken, native, raw',                   'মুরগির ডিম, দেশি (কাঁচা)'),
    ('Egg, chicken, native, boiled* (without salt)','মুরগির ডিম, দেশি (সিদ্ধ)'),
    # Mishti Doi pair
    ('Mishti Doi',                                  'মিষ্টি দই'),
    ('Curd, sweetened, whole milk',                 'মিষ্টি দই (গরুর দুধ)'),
]

# ── 3. Odia traditional foods to add ─────────────────────────────────────────
# Fields: en, bn, k(kcal/100g), p, c, f, fi, ca, fe, cat, src, kw
# s=servingSize(g), servingUnit='g'
ODIA_FOODS = [
    # Staples / Rice dishes
    {'en':'Pakhala Bhaat',        'bn':'পাখালা ভাত',        'k':95,  'p':2.0, 'c':20.0,'f':0.3,'fi':0.4,'ca':10, 'fe':0.4,'cat':'grain',   'kw':'pakhala bhaat odia fermented rice water'},
    {'en':'Odia Khichdi',         'bn':'ওড়িয়া খিচুড়ি',     'k':140, 'p':5.0, 'c':26.0,'f':3.0,'fi':1.5,'ca':20, 'fe':1.0,'cat':'grain',   'kw':'khichdi khichuri odia rice lentil'},
    {'en':'Chakuli Pitha',        'bn':'চাকুলি পিঠা',       'k':145, 'p':3.2, 'c':30.0,'f':1.2,'fi':0.5,'ca':15, 'fe':0.5,'cat':'grain',   'kw':'chakuli pitha odia rice crepe pancake'},
    {'en':'Enduri Pitha',         'bn':'এন্দুরি পিঠা',      'k':130, 'p':4.0, 'c':27.0,'f':1.0,'fi':1.0,'ca':40, 'fe':0.8,'cat':'grain',   'kw':'enduri pitha odia steamed rice cake turmeric leaf'},
    {'en':'Arisa Pitha',          'bn':'আরিসা পিঠা',        'k':310, 'p':3.5, 'c':52.0,'f':9.0,'fi':0.8,'ca':12, 'fe':0.6,'cat':'snack',   'kw':'arisa pitha odia deep fried rice jaggery cake'},
    {'en':'Manda Pitha',          'bn':'মান্ডা পিঠা',       'k':165, 'p':4.5, 'c':32.0,'f':2.0,'fi':1.2,'ca':18, 'fe':0.7,'cat':'snack',   'kw':'manda pitha odia steamed dumpling coconut'},
    # Dals / Legume dishes
    {'en':'Dalma',                'bn':'ডালমা',             'k':112, 'p':5.0, 'c':17.0,'f':3.0,'fi':3.0,'ca':30, 'fe':1.5,'cat':'legume',  'kw':'dalma odia lentil vegetable dal'},
    {'en':'Ghuguni',              'bn':'ঘুগনি',             'k':152, 'p':7.5, 'c':22.0,'f':3.5,'fi':5.0,'ca':35, 'fe':2.0,'cat':'legume',  'kw':'ghuguni odia yellow peas curry'},
    {'en':'Odia Badi Chura',      'bn':'বড়ি চুরা',          'k':185, 'p':9.0, 'c':20.0,'f':7.5,'fi':2.5,'ca':40, 'fe':1.8,'cat':'legume',  'kw':'badi chura odia dried lentil dumplings'},
    # Vegetable dishes
    {'en':'Santula',              'bn':'সন্তুলা',            'k':80,  'p':2.5, 'c':10.0,'f':3.5,'fi':2.5,'ca':40, 'fe':1.2,'cat':'vegetable','kw':'santula odia mixed vegetable stir fry'},
    {'en':'Besara',               'bn':'বেসারা',             'k':95,  'p':2.0, 'c':8.0, 'f':6.0,'fi':2.0,'ca':30, 'fe':0.9,'cat':'vegetable','kw':'besara odia mustard vegetable curry'},
    {'en':'Dahi Baigana',         'bn':'দই বাইগনা',          'k':92,  'p':3.0, 'c':8.0, 'f':5.5,'fi':2.0,'ca':55, 'fe':0.6,'cat':'vegetable','kw':'dahi baigana odia brinjal eggplant curd yogurt'},
    {'en':'Alu Potala Rasa',      'bn':'আলু পোটল রসা',       'k':118, 'p':2.5, 'c':16.0,'f':5.0,'fi':2.2,'ca':28, 'fe':0.7,'cat':'vegetable','kw':'alu potala rasa odia potato pointed gourd curry'},
    {'en':'Saga Bhaja',           'bn':'সাগ ভাজা',           'k':70,  'p':3.5, 'c':5.0, 'f':4.5,'fi':3.0,'ca':120,'fe':3.0,'cat':'vegetable','kw':'saga bhaja odia fried greens spinach'},
    # Fish dishes
    {'en':'Machha Besara',        'bn':'মাছ বেসারা',         'k':180, 'p':18.0,'c':5.0, 'f':10.0,'fi':0.5,'ca':25, 'fe':1.0,'cat':'fish',    'kw':'machha besara odia fish mustard gravy'},
    {'en':'Maachha Jhola',        'bn':'মাছ ঝোলা',           'k':148, 'p':15.0,'c':5.0, 'f':8.0, 'fi':0.4,'ca':20, 'fe':0.9,'cat':'fish',    'kw':'maachha jhola odia light fish curry'},
    {'en':'Chungdi Malai',        'bn':'চিংড়ি মালাই',        'k':198, 'p':17.0,'c':6.0, 'f':12.0,'fi':0.3,'ca':80, 'fe':1.5,'cat':'fish',    'kw':'chungdi malai odia prawn coconut milk curry'},
    {'en':'Odia Machha Tarkari',  'bn':'ওড়িয়া মাছ তরকারি',  'k':155, 'p':16.0,'c':6.0, 'f':8.0, 'fi':0.5,'ca':22, 'fe':0.8,'cat':'fish',    'kw':'machha tarkari odia fish curry tomato'},
    # Meat dishes
    {'en':'Odia Mutton Curry',    'bn':'ওড়িয়া মটন কারি',   'k':260, 'p':22.0,'c':6.0, 'f':17.0,'fi':0.5,'ca':18, 'fe':2.5,'cat':'meat',    'kw':'odia mutton curry goat meat'},
    {'en':'Mudhi Mansa',          'bn':'মুড়ি মাংস',          'k':290, 'p':18.0,'c':28.0,'f':12.0,'fi':1.0,'ca':20, 'fe':2.0,'cat':'meat',    'kw':'mudhi mansa odia puffed rice mutton'},
    # Sweets / Desserts
    {'en':'Chhena Poda',          'bn':'ছেনা পোড়া',          'k':220, 'p':7.0, 'c':35.0,'f':7.0, 'fi':0.0,'ca':90, 'fe':0.3,'cat':'sweet',   'kw':'chhena poda odia baked cottage cheese dessert'},
    {'en':'Rasabali',             'bn':'রসাবলি',             'k':280, 'p':8.0, 'c':42.0,'f':9.0, 'fi':0.0,'ca':110,'fe':0.4,'cat':'sweet',   'kw':'rasabali odia cottage cheese sweet milk'},
    {'en':'Chhena Jhili',         'bn':'ছেনা ঝিলি',          'k':260, 'p':6.0, 'c':40.0,'f':9.0, 'fi':0.0,'ca':100,'fe':0.3,'cat':'sweet',   'kw':'chhena jhili odia deep fried cottage cheese syrup'},
    {'en':'Kheer Sagara',         'bn':'ক্ষীর সাগর',         'k':245, 'p':7.5, 'c':38.0,'f':8.0, 'fi':0.0,'ca':130,'fe':0.3,'cat':'sweet',   'kw':'kheer sagara odia cottage cheese balls sweet milk'},
    {'en':'Pahala Rasgulla',      'bn':'পাহালা রসগোল্লা',    'k':115, 'p':3.0, 'c':22.0,'f':2.0, 'fi':0.0,'ca':80, 'fe':0.2,'cat':'sweet',   'kw':'pahala rasgulla odia soft spongy cottage cheese balls'},
    {'en':'Odia Puri',            'bn':'ওড়িয়া পুরি',        'k':335, 'p':7.0, 'c':47.0,'f':14.0,'fi':1.5,'ca':15, 'fe':1.5,'cat':'grain',   'kw':'odia puri deep fried bread wheat'},
    {'en':'Kanika',               'bn':'কানিকা',             'k':195, 'p':3.5, 'c':36.0,'f':5.0, 'fi':0.5,'ca':15, 'fe':0.5,'cat':'grain',   'kw':'kanika odia sweet rice ghee raisin'},
    {'en':'Odia Khaja',           'bn':'ওড়িয়া খাজা',        'k':430, 'p':5.0, 'c':62.0,'f':18.0,'fi':0.8,'ca':12, 'fe':0.8,'cat':'snack',   'kw':'odia khaja layered crispy sweet'},
    {'en':'Odia Gaja',            'bn':'গজা',                'k':395, 'p':4.5, 'c':58.0,'f':16.0,'fi':0.6,'ca':10, 'fe':0.7,'cat':'snack',   'kw':'odia gaja deep fried sweet snack'},
]

# ── Load ──────────────────────────────────────────────────────────────────────
with open(MASTER, 'r', encoding='utf-8') as f:
    master = json.load(f)

existing_en = {i['en'].lower().strip() for i in master}

# ── Apply removes ─────────────────────────────────────────────────────────────
before = len(master)
master = [i for i in master if i['en'] not in REMOVE_EN]
print(f"Removed {before - len(master)} duplicate items")

# Rebuild existing_en after removals
existing_en = {i['en'].lower().strip() for i in master}

# ── Apply BN fixes ────────────────────────────────────────────────────────────
bn_lookup = {i['en']: i for i in master}
fixed = 0
for en, new_bn in BN_FIXES:
    if en in bn_lookup:
        bn_lookup[en]['bn'] = new_bn
        fixed += 1
print(f"Fixed {fixed} Bengali names")

# ── Add Odia foods ────────────────────────────────────────────────────────────
# Determine next ID
max_id = max(i['id'] for i in master if isinstance(i.get('id'), int))
added = 0
for food in ODIA_FOODS:
    en_norm = food['en'].lower().strip()
    if en_norm in existing_en:
        print(f"  SKIP (exists): {food['en']}")
        continue
    max_id += 1
    item = {
        'id': max_id,
        'en': food['en'],
        'bn': food['bn'],
        'k':  food['k'],
        'p':  food['p'],
        'c':  food['c'],
        'f':  food['f'],
        'fi': food.get('fi', 0.0),
        'ca': food.get('ca', 0),
        'fe': food.get('fe', 0.0),
        'zn': food.get('zn', 0.0),
        'mg': food.get('mg', 0),
        'pot':food.get('pot', 0),
        'va': food.get('va', 0),
        'vc': food.get('vc', 0),
        'vd': food.get('vd', 0),
        's':  100,
        'servingUnit': 'g',
        'cat': food['cat'],
        'kw':  food['kw'],
        'src': 'odia',
    }
    master.append(item)
    existing_en.add(en_norm)
    added += 1

print(f"Added {added} Odia food items")
print(f"Total: {len(master)}")

# ── Rebuild indexes ───────────────────────────────────────────────────────────
new_index_en = sorted(
    [{'id':i['id'],'en':i['en'],'bn':i['bn'],'k':i['k']} for i in master],
    key=lambda x: x['en'].lower()
)
new_index_bn = sorted(
    [{'id':i['id'],'en':i['en'],'bn':i['bn'],'k':i['k']} for i in master],
    key=lambda x: x['bn']
)

with open(MASTER,    'w', encoding='utf-8') as f:
    json.dump(master, f, ensure_ascii=False, separators=(',',':'))
with open(INDEX_EN,  'w', encoding='utf-8') as f:
    json.dump(new_index_en, f, ensure_ascii=False, separators=(',',':'))
with open(INDEX_BN,  'w', encoding='utf-8') as f:
    json.dump(new_index_bn, f, ensure_ascii=False, separators=(',',':'))

print("Files saved.")
