"""
Rebuild search_index_v2.json with improved coverage for v9.0 dataset.

Improvements over previous version:
  - 120+ alias terms (was 94) — adds WB/Odisha food variants, common misspellings
  - 90+ family clusters (was 80) — adds chhanar, posto, nolen_gur, etc.
  - Extended romanization hints embedded in alias_lookup for Dart consumption
  - 4-char prefix indexing for EN (retained)
  - Bengali 2+3-char prefix indexing (retained)
  - Better top_foods list sorted by search_priority

Usage:
    py tools/rebuild_search_index_v3.py
"""
import json
import re
import sys
import io
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FOOD_MASTER = 'assets/data/food_master_v10.json'
OUTPUT_FILE = 'assets/data/search_index_v2.json'

# ─── Alias map ─────────────────────────────────────────────────────────────────
# Keys: search terms users type. Values: lists of EN name substrings to match.
# The script expands these into food IDs by scanning the dataset.
ALIAS_SEEDS = {
    # Fish — local names
    'rohu':         ['rohu', 'rui'],
    'rui':          ['rohu', 'rui'],
    'ilish':        ['hilsa', 'ilish'],
    'hilsa':        ['hilsa', 'ilish'],
    'katla':        ['katla', 'catla'],
    'catla':        ['katla', 'catla'],
    'bhetki':       ['bhetki', 'barramundi'],
    'pabda':        ['pabda'],
    'chitol':       ['chitol'],
    'tangra':       ['tangra'],
    'parshe':       ['parshe', 'mullet'],
    'mourala':      ['mourala', 'mola'],
    'koi':          ['koi fish', 'koi mach'],
    'magur':        ['magur', 'catfish'],
    'singi':        ['singi', 'stinging catfish'],
    'pomfret':      ['pomfret'],
    'chingri':      ['prawn', 'shrimp', 'chingri', 'chingudi'],
    'chingudi':     ['prawn', 'shrimp', 'chingri', 'chingudi'],
    'golda chingri':['golda chingri', 'giant prawn', 'freshwater prawn'],
    'dab chingri':  ['dab chingri', 'coconut prawn'],
    'crab':         ['crab', 'kakra', 'kankada'],
    'kakra':        ['crab', 'kakra'],
    'kankada':      ['crab', 'kankada'],
    'prawn':        ['prawn', 'shrimp', 'chingri', 'chingudi'],
    'shrimp':       ['prawn', 'shrimp', 'chingri'],

    # Fish cooking styles
    'macher jhol':  ['fish curry', 'macher jhol', 'fish jhol', 'macha'],
    'fish curry':   ['fish curry', 'macher jhol', 'macha'],
    'paturi':       ['paturi', 'patra', 'banana leaf fish'],
    'bhapa':        ['bhapa', 'steamed'],
    'steamed':      ['bhapa', 'steamed'],
    'besara':       ['besara', 'mustard paste', 'mustard sauce', 'sorshe'],
    'sorshe':       ['sorshe', 'shorshe', 'mustard', 'besara'],
    'shorshe':      ['sorshe', 'shorshe', 'mustard', 'besara'],
    'mustard':      ['sorshe', 'shorshe', 'mustard', 'besara'],
    'kalia':        ['kalia', 'rich gravy'],
    'jhal':         ['jhal', 'spicy curry', 'jhol spicy'],
    'roast':        ['roast', 'dry fry'],
    'cutlet':       ['cutlet', 'chop'],
    'kabiraji':     ['kabiraji'],
    'fry':          ['fry', 'bhaja', 'tawa'],
    'bhaja':        ['bhaja', 'fry', 'deep fried'],

    # Prawns/crab dishes
    'malai curry':  ['malai curry', 'malai chingri', 'coconut cream curry'],
    'chingri malai':['malai curry', 'chingri malai'],

    # Cottage cheese / chhena
    'paneer':       ['paneer', 'cottage cheese', 'chenna', 'chhana'],
    'chenna':       ['paneer', 'cottage cheese', 'chenna', 'chhana', 'chhanar', 'chhena'],
    'chhana':       ['paneer', 'cottage cheese', 'chenna', 'chhana', 'chhanar', 'chhena'],
    'chhena':       ['chhena', 'chhanar', 'cottage cheese', 'paneer'],
    'chhanar':      ['chhanar', 'chhena', 'paneer'],
    'cottage cheese':['paneer', 'cottage cheese', 'chenna', 'chhana'],

    # Sweets & Desserts
    'sandesh':      ['sandesh', 'sondesh'],
    'sondesh':      ['sandesh', 'sondesh'],
    'rasgulla':     ['rasgulla', 'rosogolla', 'roshogolla', 'rasagola'],
    'rosogolla':    ['rasgulla', 'rosogolla', 'roshogolla', 'rasagola'],
    'roshogolla':   ['rasgulla', 'rosogolla', 'roshogolla', 'rasagola'],
    'rasagola':     ['rasagola', 'rasgulla', 'rosogolla'],
    'rasmalai':     ['rasmalai', 'rosomalai', 'rasomalai'],
    'rosomalai':    ['rasmalai', 'rosomalai', 'rasomalai'],
    'mishti doi':   ['mishti doi', 'misti doi', 'sweet curd', 'sweet yogurt'],
    'misti doi':    ['mishti doi', 'misti doi', 'sweet curd'],
    'payesh':       ['payesh', 'kheer', 'rice pudding', 'payasam'],
    'kheer':        ['kheer', 'payesh', 'payasam', 'khiri', 'kheeri'],
    'khiri':        ['khiri', 'kheer', 'payesh'],
    'malpua':       ['malpua', 'malpoa'],
    'jalebi':       ['jalebi', 'jilapi', 'jilipi', 'jilebee'],
    'jilipi':       ['jalebi', 'jilapi', 'jilipi'],
    'ladoo':        ['ladoo', 'laddu', 'laddoo'],
    'laddu':        ['ladoo', 'laddu', 'laddoo'],
    'halwa':        ['halwa', 'halua', 'sheera'],
    'barfi':        ['barfi', 'burfi', 'barfee'],
    'gulab jamun':  ['gulab jamun', 'gulab jamon'],
    'langcha':      ['langcha'],
    'mihidana':     ['mihidana'],
    'sitabhog':     ['sitabhog'],
    'motichoor':    ['motichoor', 'motichur', 'boondhi'],
    'dorbesh':      ['dorbesh'],
    'nakuldana':    ['nakuldana'],
    'nolen gur':    ['nolen gur', 'nolen', 'date palm jaggery', 'khejur gur'],
    'khejur gur':   ['nolen gur', 'nolen', 'date palm jaggery', 'khejur gur'],
    'date palm jaggery': ['nolen gur', 'nolen', 'date palm jaggery', 'khejur gur'],
    'gur':          ['gur', 'jaggery', 'nolen'],
    'jaggery':      ['jaggery', 'gur', 'nolen', 'patali'],

    # Temple / Prasad
    'mahaprasad':   ['mahaprasad', 'prasad', 'jagannath', 'prasadam', 'bhog'],
    'prasad':       ['prasad', 'prasadam', 'bhog', 'temple', 'mahaprasad'],
    'prasadam':     ['prasadam', 'prasad', 'bhog', 'temple'],
    'bhog':         ['bhog', 'prasad', 'prasadam', 'khichuri bhog'],
    'jagannath':    ['jagannath', 'mahaprasad', 'puri temple'],
    'temple food':  ['prasad', 'prasadam', 'temple', 'bhog', 'jagannath'],
    'iskcon':       ['iskcon', 'mayapur'],
    'mayapur':      ['mayapur', 'iskcon'],

    # Rice dishes
    'khichuri':     ['khichuri', 'khichdi', 'khichdi', 'kedgeree'],
    'khichdi':      ['khichdi', 'khichuri', 'kedgeree'],
    'pakhala':      ['pakhala', 'panta bhat', 'fermented rice', 'water rice'],
    'panta bhat':   ['panta bhat', 'pakhala', 'fermented rice'],
    'fermented rice': ['panta bhat', 'pakhala', 'fermented rice'],
    'pulao':        ['pulao', 'pulav', 'pilaf', 'pilau'],
    'biryani':      ['biryani', 'biriyani', 'biriani', 'briyani'],
    'biriyani':     ['biryani', 'biriyani', 'biriani'],
    'biriani':      ['biryani', 'biriyani', 'biriani'],
    'fried rice':   ['fried rice'],

    # Breads
    'puri':         ['puri', 'poori', 'luchi'],
    'luchi':        ['luchi', 'puri'],
    'kochuri':      ['kochuri', 'kachori'],
    'kachori':      ['kachori', 'kochuri'],
    'paratha':      ['paratha', 'parotta', 'parotha'],
    'parotta':      ['parotta', 'paratha'],
    'naan':         ['naan', 'nan'],
    'roti':         ['roti', 'chapati', 'chapatti'],
    'chapati':      ['chapati', 'chapatti', 'roti'],
    'kulcha':       ['kulcha'],
    'rumali roti':  ['rumali roti'],
    'warqi':        ['warqi', 'layered'],
    'laccha paratha': ['laccha paratha'],
    'mughlai paratha': ['mughlai paratha', 'mughlai porota', 'moghlai porota'],
    'moghlai':      ['moghlai', 'mughlai', 'moghul', 'mughal'],
    'mughlai':      ['moghlai', 'mughlai', 'moghul', 'mughal'],

    # Snacks / Street food
    'singara':      ['singara', 'samosa'],
    'samosa':       ['samosa', 'singara'],
    'muri':         ['muri', 'puffed rice', 'murmura', 'muri'],
    'puffed rice':  ['puffed rice', 'muri', 'murmura', 'chura'],
    'chira':        ['chira', 'chira', 'poha', 'beaten rice', 'flattened rice'],
    'poha':         ['poha', 'chira', 'beaten rice', 'flattened rice'],
    'beaten rice':  ['beaten rice', 'chira', 'poha', 'flattened rice'],
    'ghugni':       ['ghugni', 'yellow peas', 'dried peas curry'],
    'dhuska':       ['dhuska'],
    'chop':         ['chop', 'cutlet'],
    'roll':         ['roll', 'kathi roll', 'kati roll', 'frankie'],
    'kathi roll':   ['kathi roll', 'kati roll', 'roll'],
    'kaati roll':   ['kathi roll', 'kati roll', 'roll'],
    'pakora':       ['pakora', 'pakoda', 'bhajiya', 'fritter'],
    'pakoda':       ['pakora', 'pakoda'],
    'bhajiya':      ['bhajiya', 'pakora', 'pakoda'],
    'chaat':        ['chaat', 'chat'],
    'sattu':        ['sattu', 'chatu', 'roasted chickpea flour'],
    'chatu':        ['chatu', 'sattu'],
    'tilkut':       ['tilkut', 'til', 'sesame sweet'],

    # Vegetables
    'aloo':         ['aloo', 'alu', 'potato'],
    'alu':          ['aloo', 'alu', 'potato'],
    'potato':       ['potato', 'aloo', 'alu'],
    'posto':        ['posto', 'poppy seed', 'khashkhash'],
    'poppy seed':   ['posto', 'poppy seed'],
    'dum aloo':     ['dum aloo', 'alur dom', 'dum potato'],
    'alur dom':     ['alur dom', 'dum aloo'],
    'begun':        ['begun', 'brinjal', 'baingan', 'eggplant', 'aubergine'],
    'brinjal':      ['brinjal', 'begun', 'baingan', 'eggplant'],
    'baingan':      ['baingan', 'begun', 'brinjal', 'eggplant'],
    'eggplant':     ['eggplant', 'begun', 'brinjal', 'baingan'],
    'kumro':        ['kumro', 'pumpkin', 'kaddu'],
    'pumpkin':      ['pumpkin', 'kumro', 'kaddu', 'kakharu'],
    'lau':          ['lau', 'bottle gourd', 'lauki'],
    'lauki':        ['lauki', 'lau', 'bottle gourd'],
    'bottle gourd': ['bottle gourd', 'lau', 'lauki'],
    'jhinge':       ['jhinge', 'ridge gourd', 'turai'],
    'ridge gourd':  ['ridge gourd', 'jhinge', 'turai'],
    'potol':        ['potol', 'parwal', 'pointed gourd'],
    'parwal':       ['parwal', 'potol', 'pointed gourd'],
    'pointed gourd':['pointed gourd', 'potol', 'parwal'],
    'uchhe':        ['uchhe', 'karela', 'bitter gourd', 'bitter melon'],
    'karela':       ['karela', 'uchhe', 'bitter gourd', 'bitter melon'],
    'bitter gourd': ['bitter gourd', 'karela', 'uchhe'],
    'fulkopi':      ['fulkopi', 'cauliflower', 'phulkopi'],
    'cauliflower':  ['cauliflower', 'fulkopi', 'phulkopi'],
    'mochar ghonto':['mochar ghonto', 'mocha ghonto', 'banana blossom', 'banana flower'],
    'mocha':        ['mocha', 'mochar', 'banana flower', 'banana blossom', 'banana stem'],
    'banana flower':['banana flower', 'banana blossom', 'mocha', 'mochar ghonto'],
    'banana blossom':['banana blossom', 'banana flower', 'mocha'],
    'echor':        ['echor', 'raw jackfruit', 'kancha kathal'],
    'raw jackfruit':['raw jackfruit', 'echor', 'kancha kathal'],
    'thor':         ['thor', 'banana stem', 'banana trunk'],
    'bamboo shoot': ['bamboo shoot', 'bans', 'shoots'],
    'kochu':        ['kochu', 'taro', 'arbi', 'kochur mukhi'],
    'taro':         ['taro', 'kochu', 'arbi'],
    'dhonepata':    ['dhonepata', 'coriander', 'cilantro'],
    'spinach':      ['spinach', 'palak', 'pui'],
    'palak':        ['palak', 'spinach'],
    'pui':          ['pui shaak', 'pui', 'malabar spinach'],
    'shaak':        ['shaak', 'sag', 'saag', 'greens'],
    'saag':         ['saag', 'sag', 'shaak', 'greens'],

    # Dal / Lentil
    'dal':          ['dal', 'daal', 'lentil', 'dhal'],
    'daal':         ['dal', 'daal', 'lentil', 'dhal'],
    'lentil':       ['lentil', 'dal', 'daal', 'dhal'],
    'chana':        ['chana', 'chickpea', 'cholar dal', 'channa', 'cholar'],
    'cholar dal':   ['cholar dal', 'chana dal'],
    'moong':        ['moong', 'mung', 'green gram'],
    'mung':         ['moong', 'mung', 'green gram'],
    'masoor':       ['masoor', 'red lentil'],
    'rajma':        ['rajma', 'kidney bean'],
    'dal makhani':  ['dal makhani'],
    'dalma':        ['dalma', 'dal with vegetables'],
    'santula':      ['santula', 'odia vegetable'],
    'ghugni':       ['ghugni', 'yellow peas'],
    'khesari':      ['khesari', 'grass pea'],
    'kurthi':       ['kurthi', 'horse gram'],

    # Meat
    'chicken':      ['chicken'],
    'mutton':       ['mutton', 'goat', 'lamb'],
    'kosha':        ['kosha', 'dry cooked', 'dark gravy'],
    'kosha mangsho':['kosha mangsho', 'kosha mutton'],
    'rezala':       ['rezala', 'white gravy mutton'],
    'korma':        ['korma', 'qorma', 'kurma'],
    'qorma':        ['korma', 'qorma', 'kurma'],

    # Pitha (rice cakes)
    'pitha':        ['pitha', 'pithe', 'patisapta', 'chitoi', 'chitau'],
    'pithe':        ['pithe', 'pitha', 'patisapta'],
    'patisapta':    ['patisapta'],
    'chitoi pitha': ['chitoi pitha', 'chitau pitha'],
    'chitau pitha': ['chitou pitha', 'chitai pitha', 'chitau'],

    # Drinks
    'lassi':        ['lassi'],
    'cha':          ['tea', 'chai', ' cha '],
    'chai':         ['chai', 'tea', 'masala chai'],
    'sharbat':      ['sharbat', 'shorbot', 'drink', 'juice', 'sherbet'],
    'shorbot':      ['shorbot', 'sharbat', 'drink'],
    'sattu sharbat':['sattu sharbat', 'chatu sharbat', 'sattu drink'],
    'chatu sharbat':['chatu sharbat', 'sattu sharbat'],
    'aam panna':    ['aam panna', 'kacha aamer', 'raw mango drink'],
    'dab':          ['dab', 'tender coconut', 'daab'],
    'tender coconut':['tender coconut', 'dab', 'daab', 'narikel jol'],
    'panchamrit':   ['panchamrit'],

    # Egg
    'egg':          ['egg', 'anda', 'dim'],
    'dim':          ['dim', 'egg'],
    'omelette':     ['omelette', 'omelet', 'omelete'],

    # Curry types
    'jhol':         ['jhol', 'light curry', 'thin gravy'],
    'dalna':        ['dalna', 'curry'],
    'ghonto':       ['ghonto', 'mash', 'mixed'],
    'chorchori':    ['chorchori', 'mixed vegetable stir fry'],
    'chachchari':   ['chachchari', 'chorchori'],
    'posto bora':   ['posto bora', 'poppy seed fritter'],
    'bora':         ['bora', 'fritter', 'pakora'],
    'chhenchra':    ['chhenchra', 'mixed organ meat curry'],

    # Fruits
    'aam':          ['aam', 'mango'],
    'mango':        ['mango', 'aam', 'amra', 'mangoo'],
    'kathal':       ['kathal', 'jackfruit', 'echor', 'kancha kathal'],
    'jackfruit':    ['jackfruit', 'kathal', 'echor'],
    'bel':          ['bel', 'bael', 'wood apple', 'stone apple'],
    'bael':         ['bael', 'bel', 'stone apple', 'wood apple'],
    'amra':         ['amra', 'hog plum'],
    'chalta':       ['chalta', 'elephant apple', 'wood apple'],
    'jamun':        ['jamun', 'java plum', 'jambul'],
    'java plum':    ['java plum', 'jamun', 'jambul'],
    'guava':        ['guava', 'peyara'],
    'peyara':       ['peyara', 'guava'],
    'narikel':      ['narikel', 'coconut'],
    'coconut':      ['coconut', 'narikel'],
    'khejur':       ['khejur', 'date', 'palm date'],
    'date palm':    ['date palm', 'nolen', 'khejur'],

    # District / Place specific
    'bardhaman':    ['bardhaman', 'burdwan'],
    'burdwan':      ['bardhaman', 'burdwan'],
    'kolkata':      ['kolkata', 'calcutta', 'kolkata'],
    'calcutta':     ['calcutta', 'kolkata'],
    'krishnanagar': ['krishnanagar'],
    'shaktigarh':   ['shaktigarh'],
    'nabadwip':     ['nabadwip'],
    'malda':        ['malda'],
    'murshidabad':  ['murshidabad'],
    'nadia':        ['nadia'],
    'hooghly':      ['hooghly', 'hugli'],
    'barasat':      ['barasat', 'basirhat', 'deganga'],
    'digha':        ['digha'],
    'darjeeling':   ['darjeeling'],
    'purulia':      ['purulia'],
    'bankura':      ['bankura'],
    'birbhum':      ['birbhum'],
    'serampore':    ['serampore'],
    'medinipur':    ['medinipur'],

    # Odia specifics
    'odia':         ['odia', 'odisha', 'orissa'],
    'odisha':       ['odisha', 'odia', 'orissa'],
    'orissa':       ['orissa', 'odisha', 'odia'],
    'dalama':       ['dalama', 'dalma'],
    'pakhala':      ['pakhala', 'panta bhat', 'fermented rice'],
    'mandia':       ['mandia', 'ragi', 'finger millet'],
    'santula':      ['santula'],
    'chhena gaja':  ['chhena gaja', 'chhena jhilli'],
    'chhena poda':  ['chhena poda'],
    'pahala':       ['pahala', 'rasagola'],
    'ganjam':       ['ganjam'],
    'chingudi besara': ['chingudi besara', 'prawn besara'],

    # South Indian (common searches)
    'idli':         ['idli', 'idly'],
    'dosa':         ['dosa', 'dosai', 'dosas'],
    'sambar':       ['sambar', 'sambhar'],
    'vada':         ['vada', 'wada', 'medu vada'],
    'upma':         ['upma'],
    'uttapam':      ['uttapam', 'uthappam'],
    'appam':        ['appam', 'hoppers'],
    'puttu':        ['puttu'],

    # Common misspellings / phonetic variants
    'biriyani':     ['biryani', 'biriyani', 'biriani'],
    'briyani':      ['biryani', 'biriyani'],
    'aloo dum':     ['dum aloo', 'aloo dum', 'alur dom'],
    'alur dom':     ['alur dom', 'dum aloo', 'aloo dum'],
    'dhokar dalna': ['dhokar dalna', 'dhoka dalna', 'lentil cake curry'],
    'dhoka':        ['dhoka', 'dhokar', 'lentil cake'],
    'lentil cake curry': ['dhokar dalna', 'lentil cake curry'],
    'fish in banana leaf': ['paturi', 'fish in banana leaf', 'patrapoda'],
    'momo':         ['momo', 'dumpling', 'momos'],
    'dumpling':     ['dumpling', 'momo', 'momos'],
    'modak':        ['modak', 'ladoo', 'sweet dumpling'],
    'churmuri':     ['churmuri', 'bhel puri'],
    'bhel puri':    ['bhel puri', 'churmuri'],
}

# ─── Family clusters ───────────────────────────────────────────────────────────
# Maps cluster name → list of EN name substrings to match for family membership.
FAMILY_SEEDS = {
    # Fish families
    'hilsa':        ['hilsa', 'ilish', 'shorshe ilish', 'ilish kalia'],
    'rohu':         ['rohu', ' rui '],
    'katla':        ['katla', 'catla', 'doi katla'],
    'bhetki':       ['bhetki'],
    'pabda':        ['pabda'],
    'chitol':       ['chitol'],
    'tangra':       ['tangra'],
    'pomfret':      ['pomfret'],
    'prawn':        ['chingri', 'chingudi', 'prawn', 'shrimp'],
    'crab':         ['crab', 'kakra', 'kankada'],
    'fish':         ['fish', 'macher', 'macha', 'paturi', 'besara'],

    # Meat
    'chicken':      ['chicken'],
    'mutton':       ['mutton', 'kosha mangsho'],
    'egg':          ['egg', 'omelette', 'dim'],

    # Sweets
    'rasgulla':     ['rasgulla', 'rosogolla', 'roshogolla', 'rasagola'],
    'sandesh':      ['sandesh', 'sondesh'],
    'mishti doi':   ['mishti doi', 'misti doi', 'sweet curd'],
    'rasmalai':     ['rasmalai', 'rosomalai'],
    'kheer':        ['kheer', 'payesh', 'payasam', 'khiri', 'kheeri'],
    'barfi':        ['barfi', 'burfi'],
    'ladoo':        ['ladoo', 'laddu', 'laddoo'],
    'halwa':        ['halwa', 'halua'],
    'gulab jamun':  ['gulab jamun'],
    'jalebi':       ['jalebi', 'jilipi', 'jilapi'],
    'malpua':       ['malpua', 'malpoa'],
    'ice cream':    ['ice cream'],
    'cake':         ['cake'],
    'cookie':       ['cookie', 'biscuit'],
    'langcha':      ['langcha'],
    'mihidana':     ['mihidana'],
    'sitabhog':     ['sitabhog'],
    'sandesh':      ['sandesh', 'sondesh'],
    'nolen gur':    ['nolen gur', 'nolen', 'date palm jaggery'],
    'pitha':        ['pitha', 'pithe', 'patisapta'],
    'motichoor':    ['motichoor', 'motichur'],
    'chhanar':      ['chhanar', 'chhena', 'chhana', 'paneer', 'chenna', 'cottage cheese'],

    # Pitha / cakes
    'pitha':        ['pitha', 'pithe', 'patisapta', 'chitoi', 'chitau'],

    # Rice
    'biryani':      ['biryani', 'biriyani', 'biriani'],
    'pulao':        ['pulao', 'pulav'],
    'khichdi':      ['khichdi', 'khichuri'],
    'fried rice':   ['fried rice'],
    'rice':         ['rice', ' bhat', 'anna', 'pakhala'],
    'pakhala':      ['pakhala', 'panta bhat'],

    # Breads
    'bread':        ['bread', 'naan', 'pao', 'bun'],
    'roti':         ['roti', 'chapati', 'rumali', 'warqi'],
    'paratha':      ['paratha', 'parotta', 'laccha', 'mughlai', 'moghlai'],
    'puri':         ['puri', 'luchi', 'poori'],
    'naan':         ['naan', 'kulcha'],
    'dosa':         ['dosa', 'uttapam', 'appam'],
    'idli':         ['idli', 'idly'],

    # Curry / Sabji
    'dal':          ['dal', 'daal', 'dhal', 'lentil curry', 'dalma', 'dalama', 'khesari', 'kurthi', 'kandul'],
    'chana':        ['chana', 'chickpea', 'cholar', 'chole'],
    'rajma':        ['rajma', 'kidney bean'],
    'moong':        ['moong', 'mung'],
    'posto':        ['posto', 'poppy seed', 'khashkhash'],
    'potato':       ['potato', 'aloo', 'alur'],
    'brinjal':      ['brinjal', 'begun', 'baingan', 'eggplant'],
    'cauliflower':  ['cauliflower', 'fulkopi', 'phulkopi'],
    'pumpkin':      ['pumpkin', 'kumro', 'kakharu'],
    'spinach':      ['spinach', 'palak', 'pui shaak'],
    'pointed gourd':['pointed gourd', 'potol', 'parwal'],
    'bitter gourd': ['bitter gourd', 'karela', 'uchhe'],
    'bottle gourd': ['bottle gourd', 'lau', 'lauki'],
    'ridge gourd':  ['ridge gourd', 'jhinge', 'turai'],
    'mochar ghonto':['mochar ghonto', 'mocha ghonto', 'banana flower'],
    'besara':       ['besara', 'mustard paste', 'mustard sauce'],
    'santula':      ['santula'],
    'dalma':        ['dalma', 'dalama'],
    'kalia':        ['kalia'],
    'korma':        ['korma', 'qorma', 'navratan'],
    'ghugni':       ['ghugni', 'dried peas'],
    'samosa':       ['samosa', 'singara'],
    'pakora':       ['pakora', 'pakoda', 'bhajiya'],

    # Snacks / Street
    'muri':         ['muri', 'puffed rice', 'murmura'],
    'poha':         ['poha', 'chira', 'beaten rice'],
    'chaat':        ['chaat', 'chat'],
    'momo':         ['momo', 'dumpling'],
    'fries':        ['fries', 'french fries', 'chips'],
    'burger':       ['burger', 'veggie burger'],
    'pizza':        ['pizza'],

    # Beverages
    'tea':          ['tea', 'chai', ' cha '],
    'coffee':       ['coffee', 'kappi'],
    'juice':        ['juice', 'sharbat', 'shorbot'],
    'water':        ['water', 'jol', 'paani'],
    'lassi':        ['lassi'],
    'shake':        ['shake', 'milkshake', 'smoothie'],
    'milk':         ['milk', 'doodh', 'dudh'],
    'coconut water':['coconut water', 'tender coconut', 'dab'],

    # Fruits
    'mango':        ['mango', 'aam', 'amra'],
    'banana':       ['banana', 'kela', 'kola'],
    'jackfruit':    ['jackfruit', 'kathal', 'echor'],
    'apple':        ['apple'],
    'orange':       ['orange'],
    'guava':        ['guava', 'peyara'],
    'coconut':      ['coconut', 'narikel'],

    # Dairy
    'yogurt':       ['yogurt', 'curd', 'doi', 'dahi'],
    'cheese':       ['cheese', 'bandel'],
    'butter':       ['butter'],
    'ghee':         ['ghee'],
    'paneer':       ['paneer', 'cottage cheese'],

    # Prasad / Temple
    'mahaprasad':   ['mahaprasad', 'prasadam', 'bhog', 'temple', 'jagannath'],
    'panchamrit':   ['panchamrit'],
}

def load_foods(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def en_name_lower(food):
    return food.get('en', '').lower()

def bn_name_lower(food):
    return food.get('bn', '').lower()

def keywords_lower(food):
    # 'kw' is keywords; 'k' is calories — use 'kw'
    kws = food.get('kw', [])
    if isinstance(kws, list):
        return [k.lower() for k in kws]
    return []

def contains_bengali(text):
    return any(0x0980 <= ord(c) <= 0x09FF for c in text)

def build_prefix_index(foods, min_len=2, max_len=4):
    """Build EN prefix index: prefix -> list of food IDs."""
    index = defaultdict(set)
    for food in foods:
        fid = food['id']
        name = en_name_lower(food)
        kws = keywords_lower(food)
        all_terms = [name] + kws
        for term in all_terms:
            words = re.split(r'[\s/\-\(\)]+', term)
            for w in words:
                w = w.strip()
                if not w:
                    continue
                for length in range(min_len, min(max_len + 1, len(w) + 1)):
                    index[w[:length]].add(fid)
    return {k: sorted(v) for k, v in sorted(index.items())}

def build_bn_prefix_index(foods, min_len=2, max_len=3):
    """Build Bengali prefix index: prefix -> list of food IDs."""
    index = defaultdict(set)
    for food in foods:
        fid = food['id']
        bn = bn_name_lower(food)
        if not bn:
            continue
        words = re.split(r'[\s/\-\(\)]+', bn)
        for w in words:
            w = w.strip()
            if not w:
                continue
            for length in range(min_len, min(max_len + 1, len(w) + 1)):
                prefix = w[:length]
                if any(contains_bengali(c) for c in prefix):
                    index[prefix].add(fid)
    return {k: sorted(v) for k, v in sorted(index.items())}

def build_alias_lookup(foods, alias_seeds):
    """Map alias term -> list of food IDs where EN name contains any seed."""
    index = defaultdict(set)
    for alias_term, seeds in alias_seeds.items():
        for food in foods:
            en = en_name_lower(food)
            kws = keywords_lower(food)
            all_searchable = en + ' ' + ' '.join(kws)
            if any(seed.lower() in all_searchable for seed in seeds):
                index[alias_term].add(food['id'])
    # Deduplicate and sort
    return {k: sorted(v) for k, v in sorted(index.items()) if v}

def build_family_index(foods, family_seeds):
    """Map family name -> list of food IDs."""
    index = defaultdict(set)
    for family, seeds in family_seeds.items():
        for food in foods:
            en = en_name_lower(food)
            kws = keywords_lower(food)
            all_searchable = en + ' ' + ' '.join(kws)
            if any(seed.lower() in all_searchable for seed in seeds):
                index[family].add(food['id'])
    return {k: sorted(v) for k, v in sorted(index.items()) if v}

def build_top_foods(foods, n=200):
    """Top N foods by search_priority field, then alphabetical."""
    def priority(f):
        sp = f.get('search_priority', 50)
        try:
            return -int(sp)
        except (TypeError, ValueError):
            return -50
    sorted_foods = sorted(foods, key=lambda f: (priority(f), f.get('en', '')))
    return [f['id'] for f in sorted_foods[:n]]

def main():
    print(f'Loading {FOOD_MASTER}...')
    foods = load_foods(FOOD_MASTER)
    print(f'  {len(foods)} foods loaded')

    print('Building EN prefix index (2–4 char)...')
    en_prefix = build_prefix_index(foods, min_len=2, max_len=4)
    print(f'  {len(en_prefix)} tokens')

    print('Building BN prefix index (2–3 char)...')
    bn_prefix = build_bn_prefix_index(foods, min_len=2, max_len=3)
    print(f'  {len(bn_prefix)} tokens')

    print('Building alias lookup...')
    alias_lookup = build_alias_lookup(foods, ALIAS_SEEDS)
    print(f'  {len(alias_lookup)} alias terms')

    print('Building family index...')
    family_index = build_family_index(foods, FAMILY_SEEDS)
    print(f'  {len(family_index)} family clusters')

    print('Building top_foods list...')
    top_foods = build_top_foods(foods, n=200)
    print(f'  {len(top_foods)} top foods')

    # Print stats per alias
    empty_aliases = [k for k, v in alias_lookup.items() if not v]
    if empty_aliases:
        print(f'  WARNING: {len(empty_aliases)} aliases matched 0 foods: {empty_aliases}')

    index = {
        'en_prefix':    en_prefix,
        'bn_prefix':    bn_prefix,
        'alias_lookup': alias_lookup,
        'family_index': family_index,
        'top_foods':    top_foods,
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, separators=(',', ':'))

    import os
    size_kb = os.path.getsize(OUTPUT_FILE) / 1024
    print(f'\nWrote {OUTPUT_FILE} ({size_kb:.1f} KB)')
    print('Done.')

if __name__ == '__main__':
    main()
