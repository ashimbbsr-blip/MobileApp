"""
Fill missing vitamins (vc, va, vd, b12) in food_master_v10.json.

Strategy:
1. Keyword-based reference table (USDA FoodData Central standard values per 100g)
2. Items already having vc > 0 are skipped (don't overwrite good data)
3. Only fills where confident match exists
"""
import json, sys, io, re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ─────────────────────────────────────────────────────────────────────────────
# REFERENCE TABLE  (values per 100g, from USDA FoodData Central + ICMR IFCT)
# Keys are lowercase keyword patterns; longest/most-specific match wins.
# vc  = vitamin C (mg)
# va  = vitamin A (µg RAE)
# vd  = vitamin D (µg)
# b12 = vitamin B12 (µg)
# ─────────────────────────────────────────────────────────────────────────────
REFS = [
    # ─── Fruits ───
    {'kw': ['amla', 'gooseberry', 'amloki'],        'vc': 600, 'va': 2},
    {'kw': ['guava', 'peyara', 'peru'],              'vc': 228, 'va': 31},
    {'kw': ['kiwi'],                                 'vc': 92,  'va': 4},
    {'kw': ['papaya', 'pawpaw', 'pepe'],             'vc': 61,  'va': 47},
    {'kw': ['strawberry', 'strawberri'],             'vc': 59,  'va': 1},
    {'kw': ['orange, raw', 'orange,raw', 'santra', 'komla', 'narangi',
            'orange, sweet', 'orange (sweet)', 'sweet orange'],
                                                     'vc': 53,  'va': 11},
    {'kw': ['lemon', 'lebu', 'limon'],               'vc': 53,  'va': 1},
    {'kw': ['pineapple', 'ananas', 'anaras'],        'vc': 48,  'va': 3},
    {'kw': ['cantaloupe', 'kharbuj', 'kharbooj'],    'vc': 37,  'va': 169},
    {'kw': ['mango, raw', 'kacha aam', 'green mango', 'raw mango'],
                                                     'vc': 46,  'va': 17},
    {'kw': ['mango', 'aam', 'alphonso', 'langra', 'dussehri', 'himsagar'],
                                                     'vc': 36,  'va': 54},
    {'kw': ['lychee', 'litchi'],                     'vc': 72,  'va': 0},
    {'kw': ['raspberry'],                            'vc': 26,  'va': 2},
    {'kw': ['honeydew'],                             'vc': 18,  'va': 3},
    {'kw': ['pomegranate', 'anar', 'dalim'],         'vc': 10,  'va': 0},
    {'kw': ['banana', 'kela', 'kola'],               'vc': 9,   'va': 3},
    {'kw': ['blueberry'],                            'vc': 10,  'va': 3},
    {'kw': ['watermelon', 'tarbuj', 'tormuj'],       'vc': 8,   'va': 28},
    {'kw': ['peach', 'aadoo', 'adu'],                'vc': 7,   'va': 16},
    {'kw': ['cherry', 'cherri'],                     'vc': 7,   'va': 3},
    {'kw': ['avocado'],                              'vc': 10,  'va': 7},
    {'kw': ['pear', 'nashpati'],                     'vc': 4,   'va': 1},
    {'kw': ['apple', 'seb', 'aapel'],                'vc': 5,   'va': 3},
    {'kw': ['plum', 'aloobukhara'],                  'vc': 10,  'va': 17},
    {'kw': ['fig', 'anjeer', 'dumur', 'ডুমুর'],      'vc': 2,   'va': 7},
    {'kw': ['grape', 'angur', 'draksha'],            'vc': 3,   'va': 3},
    {'kw': ['coconut', 'narikel', 'narikela', 'narkel'],
                                                     'vc': 3,   'va': 0},
    {'kw': ['jackfruit', 'kathal', 'kanthal', 'kothol'],
                                                     'vc': 14,  'va': 5},
    {'kw': ['medjool date', 'ajwa date', 'khejur', 'khajoor', 'pind khajoor',
            'deglet', 'sukkari', 'mazafati', 'barhi date', 'zahidi'],
                                                     'vc': 0,   'va': 0},
    {'kw': ['date, dried', 'dried date', 'dry date'],
                                                     'vc': 0,   'va': 0},
    {'kw': ['tamarind', 'tetul', 'imli'],            'vc': 4,   'va': 2},
    {'kw': ['mulberry', 'shahtoot'],                 'vc': 36,  'va': 1},
    {'kw': ['passion fruit', 'krishnakeli'],         'vc': 30,  'va': 64},
    {'kw': ['longan'],                               'vc': 84,  'va': 0},
    {'kw': ['rambutan'],                             'vc': 40,  'va': 0},
    {'kw': ['persimmon', 'tendu'],                   'vc': 66,  'va': 81},
    {'kw': ['blood orange'],                         'vc': 53,  'va': 11},
    {'kw': ['clementine', 'mandarin'],               'vc': 49,  'va': 11},
    {'kw': ['kumquat'],                              'vc': 44,  'va': 15},
    {'kw': ['lime', 'gondhoraj', 'mosambi'],         'vc': 29,  'va': 2},
    {'kw': ['grapefruit'],                           'vc': 31,  'va': 11},
    {'kw': ['star fruit', 'kamranga'],               'vc': 35,  'va': 3},
    {'kw': ['wood apple', 'bel', 'bael'],            'vc': 9,   'va': 55},
    {'kw': ['raisin', 'kismis'],                     'vc': 3,   'va': 0},
    {'kw': ['apricot', 'khumani', 'zardalu'],        'vc': 10,  'va': 96},
    {'kw': ['prune', 'aloo bukhara'],                'vc': 1,   'va': 39},
    {'kw': ['dried mango', 'aam papad'],             'vc': 5,   'va': 30},
    {'kw': ['custard apple', 'sitaphal', 'ata fol'],'vc': 36,  'va': 3},

    # ─── Vegetables ───
    {'kw': ['capsicum, red', 'red capsicum', 'red bell pepper', 'red pepper'],
                                                     'vc': 128, 'va': 157},
    {'kw': ['capsicum, yellow', 'yellow capsicum', 'yellow bell pepper'],
                                                     'vc': 184, 'va': 10},
    {'kw': ['capsicum', 'bell pepper', 'shimla mirch'],
                                                     'vc': 80,  'va': 18},
    {'kw': ['broccoli'],                             'vc': 89,  'va': 31},
    {'kw': ['brussels sprout'],                      'vc': 85,  'va': 38},
    {'kw': ['bitter gourd', 'karela', 'ucche', 'kerala'],
                                                     'vc': 84,  'va': 24},
    {'kw': ['drumstick leaves', 'moringa leaves', 'sajina pata'],
                                                     'vc': 141, 'va': 378},
    {'kw': ['drumstick', 'moringa', 'sajina', 'sahjan'],
                                                     'vc': 141, 'va': 74},
    {'kw': ['fenugreek leaves', 'methi leaves', 'methi pata'],
                                                     'vc': 53,  'va': 395},
    {'kw': ['coriander leaves', 'dhania', 'dhaniya', 'cilantro', 'sorshe shak'],
                                                     'vc': 27,  'va': 337},
    {'kw': ['cauliflower', 'ful kopi', 'phulkopi'],  'vc': 48,  'va': 0},
    {'kw': ['peas', 'matar', 'mutter', 'motor dal', 'green pea'],
                                                     'vc': 40,  'va': 38},
    {'kw': ['spinach', 'palak', 'palong shak'],      'vc': 28,  'va': 469},
    {'kw': ['mint', 'pudina', 'poodina'],            'vc': 32,  'va': 212},
    {'kw': ['turnip', 'shalgam'],                    'vc': 21,  'va': 0},
    {'kw': ['garlic', 'lahsun', 'roshun', 'rasun'],  'vc': 31,  'va': 0},
    {'kw': ['lotus stem', 'kamal kakdi', 'padma shak'],
                                                     'vc': 44,  'va': 0},
    {'kw': ['snake gourd', 'chichinda', 'potol'],    'vc': 19,  'va': 15},
    {'kw': ['ridge gourd', 'torai', 'jhinga'],       'vc': 12,  'va': 41},
    {'kw': ['okra', 'bhindi', 'bhendi', 'ladies finger', 'dherosh'],
                                                     'vc': 23,  'va': 36},
    {'kw': ['cabbage', 'patta gobi', 'bandha kopi', 'banda kopi'],
                                                     'vc': 37,  'va': 5},
    {'kw': ['tomato', 'tamatar', 'tameta', 'tomate'], 'vc': 14,  'va': 42},
    {'kw': ['potato', 'aloo', 'batata', 'alu'],      'vc': 20,  'va': 0},
    {'kw': ['sweet potato', 'shakarkandi', 'mishti alu'],
                                                     'vc': 2,   'va': 961},
    {'kw': ['pumpkin', 'kaddu', 'kumra', 'kadu'],    'vc': 9,   'va': 369},
    {'kw': ['carrot', 'gajar', 'gajor'],             'vc': 6,   'va': 835},
    {'kw': ['radish', 'mooli', 'mula'],              'vc': 15,  'va': 0},
    {'kw': ['beetroot', 'beet', 'chukandar'],        'vc': 5,   'va': 2},
    {'kw': ['cucumber', 'kakdi', 'kakra', 'shasha'],  'vc': 3,   'va': 5},
    {'kw': ['eggplant', 'brinjal', 'baingan', 'begun', 'ringna'],
                                                     'vc': 2,   'va': 1},
    {'kw': ['bottle gourd', 'lauki', 'lau', 'dudhi'],
                                                     'vc': 12,  'va': 2},
    {'kw': ['onion', 'pyaz', 'piyaj', 'piaz'],       'vc': 7,   'va': 0},
    {'kw': ['spring onion', 'green onion', 'scallion'],
                                                     'vc': 19,  'va': 50},
    {'kw': ['green chilli', 'hari mirch', 'lonka', 'kancha lonka'],
                                                     'vc': 144, 'va': 18},
    {'kw': ['chilli', 'mirch', 'mirchi'],            'vc': 144, 'va': 18},
    {'kw': ['ginger', 'adrak', 'ada'],               'vc': 5,   'va': 0},
    {'kw': ['celery'],                               'vc': 3,   'va': 22},
    {'kw': ['mushroom', 'dhingri'],                  'vc': 3,   'va': 0,   'vd': 0.2},
    {'kw': ['colocasia', 'arbi', 'kochu', 'kochur mukhi'],
                                                     'vc': 8,   'va': 76},
    {'kw': ['yam', 'suran', 'ol'],                   'vc': 17,  'va': 7},
    {'kw': ['raw banana', 'kacha kola', 'kachkola'], 'vc': 10,  'va': 60},
    {'kw': ['raw jackfruit', 'kathal', 'echor'],     'vc': 7,   'va': 2},
    {'kw': ['cluster beans', 'guvar', 'guar phali'],  'vc': 49,  'va': 16},
    {'kw': ['french beans', 'green beans', 'beans'],  'vc': 12,  'va': 35},
    {'kw': ['ivy gourd', 'tindora', 'kundru'],       'vc': 25,  'va': 22},
    {'kw': ['raw papaya', 'kacha papaya'],           'vc': 62,  'va': 47},
    {'kw': ['malabar spinach', 'pui shak'],          'vc': 102, 'va': 400},
    {'kw': ['red amaranth', 'lal shak', 'laal saag'],'vc': 40,  'va': 367},
    {'kw': ['amaranth', 'chaulai', 'note shak'],     'vc': 34,  'va': 292},
    {'kw': ['fenugreek', 'methi'],                   'vc': 27,  'va': 83},
    {'kw': ['lotus', 'padma'],                       'vc': 44,  'va': 0},
    {'kw': ['zucchini', 'courgette'],                'vc': 18,  'va': 10},
    {'kw': ['ash gourd', 'petha', 'kumra'],          'vc': 13,  'va': 0},
    {'kw': ['pointed gourd', 'parwal'],              'vc': 29,  'va': 22},
    {'kw': ['knol khol', 'kohlrabi'],                'vc': 62,  'va': 2},
    {'kw': ['cactus pear', 'nagfani'],               'vc': 14,  'va': 3},
    {'kw': ['taro', 'arbi', 'kachalu'],              'vc': 8,   'va': 76},

    # ─── Legumes (low vc) ───
    {'kw': ['moong', 'mung', 'green gram'],          'vc': 5,   'va': 2},
    {'kw': ['sprouted', 'sprout'],                   'vc': 8,   'va': 0},
    {'kw': ['chickpea', 'chana', 'chole', 'chick pea'],
                                                     'vc': 1,   'va': 3},
    {'kw': ['lentil', 'masoor', 'dal', 'dhal'],      'vc': 0,   'va': 1},
    {'kw': ['kidney bean', 'rajma'],                 'vc': 0,   'va': 0},
    {'kw': ['soybean', 'soya'],                      'vc': 6,   'va': 1},
    {'kw': ['peanut', 'groundnut', 'badam'],         'vc': 0,   'va': 0},
    {'kw': ['cowpea', 'lobia', 'black-eyed'],        'vc': 1,   'va': 2},

    # ─── Grains ───
    {'kw': ['rice'],  'vc': 0, 'va': 0},
    {'kw': ['wheat', 'atta', 'maida'], 'vc': 0, 'va': 0},
    {'kw': ['oat'],   'vc': 0, 'va': 0},
    {'kw': ['millet', 'bajra', 'ragi', 'jowar'], 'vc': 0, 'va': 1},
    {'kw': ['corn', 'maize', 'bhutta'], 'vc': 7, 'va': 10},
    {'kw': ['barley', 'jau'],  'vc': 0, 'va': 0},

    # ─── Fish/Meat (low/no vc, some va) ───
    {'kw': ['hilsa', 'ilish', 'elish'],              'vc': 0, 'va': 60,  'b12': 5.0},
    {'kw': ['rohu', 'rui', 'rohita'],                'vc': 0, 'va': 15,  'b12': 2.0},
    {'kw': ['catla', 'katla', 'katol'],              'vc': 0, 'va': 15,  'b12': 2.0},
    {'kw': ['pabda', 'pabda fish'],                  'vc': 0, 'va': 20,  'b12': 2.0},
    {'kw': ['salmon'],                               'vc': 0, 'va': 50,  'vd': 11.0, 'b12': 3.2},
    {'kw': ['tuna'],                                 'vc': 0, 'va': 64,  'vd': 6.7,  'b12': 9.4},
    {'kw': ['mackerel', 'bangda'],                   'vc': 0, 'va': 40,  'vd': 16.1, 'b12': 8.7},
    {'kw': ['sardine', 'sardin'],                    'vc': 0, 'va': 25,  'vd': 4.8,  'b12': 8.9},
    {'kw': ['egg'],                                  'vc': 0, 'va': 149, 'vd': 2.0,  'b12': 1.1},
    {'kw': ['chicken', 'murgi', 'murgi'],            'vc': 0, 'va': 18,  'b12': 0.3},
    {'kw': ['mutton', 'goat', 'lamb'],               'vc': 0, 'va': 5,   'b12': 2.2},
    {'kw': ['beef', 'goru'],                         'vc': 0, 'va': 0,   'b12': 2.6},
    {'kw': ['pork'],                                 'vc': 0, 'va': 0,   'b12': 0.7},
    {'kw': ['prawn', 'shrimp', 'chingri'],           'vc': 0, 'va': 54,  'b12': 1.8},
    {'kw': ['crab', 'kakra', 'kakda'],               'vc': 0, 'va': 2,   'b12': 10},
    {'kw': ['liver'],                                'vc': 0, 'va': 4968,'b12': 59.3},

    # ─── Dairy ───
    {'kw': ['milk'],                                 'vc': 0, 'va': 46,  'vd': 0.1,  'b12': 0.4},
    {'kw': ['yogurt', 'curd', 'dahi', 'doi'],        'vc': 0, 'va': 27,  'vd': 0.1,  'b12': 0.6},
    {'kw': ['cheese', 'paneer', 'chhana', 'chana'],  'vc': 0, 'va': 98,  'vd': 0.2,  'b12': 0.8},
    {'kw': ['butter'],                               'vc': 0, 'va': 684, 'vd': 0.3,  'b12': 0.1},
    {'kw': ['ghee'],                                 'vc': 0, 'va': 840, 'vd': 0.3,  'b12': 0},

    # ─── Nuts & seeds ───
    {'kw': ['almond', 'badam'],                      'vc': 0, 'va': 1},
    {'kw': ['cashew', 'kaju'],                       'vc': 0, 'va': 0},
    {'kw': ['walnut', 'akhrot'],                     'vc': 1, 'va': 1},
    {'kw': ['pistachio', 'pista'],                   'vc': 5, 'va': 12},
    {'kw': ['sesame', 'til'],                        'vc': 0, 'va': 0},
    {'kw': ['flaxseed', 'alsi'],                     'vc': 1, 'va': 0},
    {'kw': ['sunflower seed'],                       'vc': 1, 'va': 1},
    {'kw': ['pumpkin seed', 'kaddu beej'],           'vc': 2, 'va': 0},

    # ─── Spices / condiments (minor vc) ───
    {'kw': ['lime juice', 'lemon juice', 'nimbu pani'],
                                                     'vc': 30, 'va': 1},
    {'kw': ['orange juice', 'santra juice'],         'vc': 50, 'va': 11},
    {'kw': ['amla juice', 'awla juice'],             'vc': 400,'va': 2},
    {'kw': ['tomato sauce', 'ketchup'],              'vc': 9,  'va': 42},
    {'kw': ['turmeric', 'haldi'],                    'vc': 26, 'va': 0},

    # ─── Fortified foods ───
    {'kw': ['cornflakes', 'corn flakes', 'breakfast cereal'],
                                                     'vc': 25, 'va': 150, 'vd': 2.5, 'b12': 1.5},
    {'kw': ['muesli'],                               'vc': 5,  'va': 100, 'vd': 2.0, 'b12': 1.0},
]

# Sort so longest keyword matches first (more specific)
REFS.sort(key=lambda r: -max(len(k) for k in r['kw']))


def match(name_lc: str, ref: dict) -> bool:
    return any(kw in name_lc for kw in ref['kw'])


def fill_item(food: dict) -> bool:
    name_lc = food['en'].lower()
    matched = False
    for ref in REFS:
        if not match(name_lc, ref):
            continue
        changed = False
        for field in ('vc', 'va', 'vd', 'b12'):
            if field in ref and food.get(field, 0) == 0:
                food[field] = ref[field]
                changed = True
        if changed:
            matched = True
        break  # use first (most-specific) match only
    return matched


# ─── Load & process ───────────────────────────────────────────────────────────
with open('assets/data/food_master_v10.json', encoding='utf-8') as f:
    foods = json.load(f)

filled = 0
vc_filled = 0
for food in foods:
    if fill_item(food):
        filled += 1
        if food.get('vc', 0) > 0:
            vc_filled += 1

print(f'Items updated: {filled}')
print(f'  of which got vc: {vc_filled}')

# Verify oranges
print('\nOrange items after fix:')
for f in foods:
    if 'orange' in f['en'].lower() and f.get('cat') == 'fruit':
        print(f"  ID:{f['id']:4} | {f['en'][:35]:35} | vc:{f.get('vc',0):.1f}mg | va:{f.get('va',0):.0f}mcg")

# Summary stats
has_vc = sum(1 for f in foods if f.get('vc', 0) > 0)
has_va = sum(1 for f in foods if f.get('va', 0) > 0)
print(f'\nAfter fix:')
print(f'  vc > 0: {has_vc} / 5000')
print(f'  va > 0: {has_va} / 5000')

with open('assets/data/food_master_v10.json', 'w', encoding='utf-8') as out:
    json.dump(foods, out, ensure_ascii=False, separators=(',', ':'))
print('Saved.')
