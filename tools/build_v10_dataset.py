"""
build_v10_dataset.py — Merge foodmissing.txt into food_master_v9_0.json,
deduplicate, normalize, and produce food_master_v10.json with exactly 5000 items.

Usage:
    py tools/build_v10_dataset.py
"""
import json
import re
import sys
import io
import unicodedata
import collections
from difflib import SequenceMatcher

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAIN_FILE    = 'assets/data/food_master_v9_0.json'
MISSING_FILE = 'assets/data/foodmissing.txt'
OUTPUT_FILE  = 'assets/data/food_master_v10.json'
TARGET_COUNT = 5000

# ─── Category normalisation (mirrors Dart _normalizeCategory) ─────────────────
CATEGORY_MAP = {
    # foodmissing.txt specific
    'dessert':        'sweet',
    'protein_bar':    'snack',
    'dish':           'restaurant_food',
    'kebab':          'meat',
    'smoothie':       'beverage',
    'rum':            'beverage',
    'beer':           'beverage',
    'cookie':         'bakery',
    'coffee':         'beverage',
    'nutrition_drink':'beverage',
    'frappe':         'beverage',
    'whisky':         'beverage',
    'vodka':          'beverage',
    'cold_coffee':    'beverage',
    'gin':            'beverage',
    'combo':          'restaurant_food',
    'starter':        'snack',
    'spice':          'snack',
    'fast_food':      'restaurant_food',
    'naan':           'bread',
    'alcohol':        'beverage',
    'wine':           'beverage',
    'cocktail':       'beverage',
    'spirits':        'beverage',
    'supplement':     'snack',
    'whey':           'snack',
    'nuts':           'snack',
    'seeds':          'snack',
    'dry_fruit':      'snack',
    'oil':            'snack',
    'sauce':          'snack',
    'pickle':         'snack',
    'papad':          'snack',
    'wrap':           'bread',
    'sandwich':       'bread',
    'burger':         'restaurant_food',
    'pizza':          'pizza',
    'pasta':          'noodle',
    'noodle':         'noodle',
    'cake':           'sweet',
    'ice_cream':      'sweet',
    'pudding':        'sweet',
    'tart':           'sweet',
    # Dart mirrors
    'veg':            'vegetable',
    'leafy_vegetable':'shaak',
    'drink':          'beverage',
    'fitness':        'snack',
    'brand':          'snack',
    'condiment':      'snack',
    'diet':           'beverage',
    'meal':           'restaurant_food',
    'mutton':         'meat',
    'chicken':        'meat',
    'duck':           'meat',
    'beef':           'meat',
    'seafood':        'fish',
    'paneer':         'dairy',
    'curd':           'dairy',
    'cheese':         'dairy',
    'butter':         'dairy',
    'ghee':           'dairy',
    'milk':           'dairy',
    'milk_powder':    'dairy',
    'chocolate':      'sweet',
    'dark_chocolate': 'sweet',
    'candy':          'sweet',
    'biscuit':        'bakery',
    'rusk':           'bakery',
    'energy_drink':   'beverage',
    'sports_drink':   'beverage',
    'water':          'beverage',
    'prasad':         'sweet',
    'chutney':        'snack',
    'starch':         'grain',
    'food':           'snack',
    'curry':          'vegetable',
    'veg_curry':      'vegetable',
    'street_food':    'restaurant_food',
    'millet':         'grain',
    'tribal_food':    'restaurant_food',
    'restaurant':     'restaurant_food',
    'dal':            'legume',
    # Wine / spirit sub-types
    'red_wine':            'beverage',
    'white_wine':          'beverage',
    'sparkling_wine':      'beverage',
    'dessert_wine':        'beverage',
    'rose_wine':           'beverage',
    'vermouth':            'beverage',
    'whiskey':             'beverage',
    'traditional_drink':   'beverage',
    'millet_drink':        'beverage',
    'millet_sprouted_drink': 'beverage',
    'malted_cereal_drink': 'beverage',
    'multigrain_drink':    'beverage',
    'sprouted_cereal_drink': 'beverage',
    'malted_drink':        'beverage',
    'health_drink':        'beverage',
    'protein_drink':       'beverage',
    'ready_to_drink':      'beverage',
    'protein_shake':       'beverage',
    'hydration_drink':     'beverage',
    'recovery_drink':      'beverage',
    'electrolyte_drink':   'beverage',
    'nut_milk_mix':        'beverage',
    'beverage_base':       'beverage',
    'fruit_drink':         'beverage',
    'soft_drink':          'beverage',
    'traditional_food':    'restaurant_food',
    'temple_food':         'sweet',
    # Dairy sub-types
    'greek_yogurt':        'dairy',
    'yogurt':              'dairy',
    'fat_spread':          'dairy',
    'plant_dairy':         'dairy',
    'dairy_fat':           'dairy',
    'probiotic':           'dairy',
    'infant_growing_up_milk': 'dairy',
    # Nutrition / clinical
    'children_growth':     'snack',
    'children_nutrition':  'snack',
    'diabetes_nutrition':  'snack',
    'diabetic_nutrition':  'snack',
    'clinical_nutrition':  'snack',
    'oral_nutrition_supplement': 'snack',
    'kids_nutrition':      'snack',
    'medical_nutrition':   'snack',
    'pulmonary_nutrition': 'snack',
    'renal_nutrition':     'snack',
    'hepatic_nutrition':   'snack',
    'protein_supplement':  'snack',
    'plant_protein':       'snack',
    'kids_protein':        'snack',
    'clinical_protein':    'snack',
    'high_protein':        'snack',
    'millet_sprouted_mix': 'snack',
    'digestive_mix':       'snack',
    'fitness_energy':      'snack',
    # Snack sub-types
    'street_snack':        'snack',
    'fried_snack':         'snack',
    'light_snack':         'snack',
    'baked_snack':         'snack',
    'flatbread_snack':     'snack',
    'sweet_fried_snack':   'snack',
    'dry_snack':           'snack',
    'steamed_snack':       'snack',
    'fried_side':          'snack',
    'ekadashi_snack':      'snack',
    'fruit_nut':           'snack',
    'instant_food':        'snack',
    'sweetener':           'snack',
    'ayurveda':            'snack',
    'spread':              'snack',
    'herb':                'snack',
    'side':                'snack',
    'fried_food':          'snack',
    # Fruit sub-types
    'summer_fruit':        'fruit',
    'stone_fruit':         'fruit',
    'tropical_fruit':      'fruit',
    'berry':               'fruit',
    'mediterranean_fruit': 'fruit',
    'fresh_fruit':         'fruit',
    'semi_dry_fruit':      'fruit',
    'aquatic_fruit':       'fruit',
    'temperate_fruit':     'fruit',
    'fruit_preparation':   'fruit',
    'premium_dates':       'fruit',
    'fresh_dried_fruit':   'fruit',
    'tropical_dried_fruit':'fruit',
    'dried_fruit':         'fruit',
    'vegetable_fruit':     'fruit',
    # Vegetable sub-types
    'vegetable_curry':     'vegetable',
    'mixed_vegetable_curry': 'vegetable',
    'leafy_curry':         'vegetable',
    'vegetable_dish':      'vegetable',
    'smoked_vegetable':    'vegetable',
    'potato_curry':        'vegetable',
    'tomato_curry':        'vegetable',
    'veg_side':            'vegetable',
    'veg_main':            'vegetable',
    'winter_tuber':        'vegetable',
    'tuber':               'vegetable',
    'cooked_tuber':        'vegetable',
    'forest_food':         'vegetable',
    'mixed_tuber_dish':    'vegetable',
    # Grain sub-types
    'grain_food':          'grain',
    'flour':               'grain',
    'carb':                'grain',
    'base':                'grain',
    'cereal':              'breakfast',
    # Fish sub-types
    'fish_curry':          'fish',
    'fried_fish':          'fish',
    'grilled_fish':        'fish',
    'baked_fish':          'fish',
    'fish_fry':            'fish',
    'fish_dish':           'fish',
    'fish_stew':           'fish',
    'fish_meal':           'fish',
    'smoked_fish':         'fish',
    'pan_fried_fish':      'fish',
    'fried_seafood':       'fish',
    'seafood_pasta':       'fish',
    'fried_small_fish':    'fish',
    # Meat sub-types
    'tandoori_chicken':    'meat',
    'creamy_kebab':        'meat',
    'herb_kebab':          'meat',
    'spiced_kebab':        'meat',
    'soft_mince_kebab':    'meat',
    'non_veg_dish':        'meat',
    'tandoor':             'meat',
    # Dal sub-types
    'pulse':               'legume',
    'bean_curry':          'legume',
    'dal_vegetable_curry': 'legume',
    'thick_dal':           'legume',
    'rustic_dal':          'legume',
    'flavored_dal':        'legume',
    'dal_meal_combo':      'legume',
    'dal_combo':           'legume',
    'tempered_dal':        'legume',
    # Rice sub-types
    'biryani':             'rice',
    'rice_meal':           'rice',
    # Restaurant/food sub-types
    'main_course':         'restaurant_food',
    'ready_meal':          'restaurant_food',
    'comfort_food':        'restaurant_food',
    'rich_curry':          'restaurant_food',
    'combo':               'restaurant_food',
    # Sweet sub-types
    'confectionery':       'sweet',
    'ekadashi_dessert':    'sweet',
    'prasadam':            'sweet',
    'prasadam_main':       'sweet',
    # Egg
    'egg_curry':           'egg',
    # Ekadashi (festival fasting food)
    'ekadashi_potato':     'vegetable',
    'ekadashi_main':       'restaurant_food',
    'ekadashi_curry':      'vegetable',
    'ekadashi_paneer':     'dairy',
    # Bread sub-types
    'fried_bread':         'bread',
    'rice':           'rice',
    'grain':          'grain',
    'bread':          'bread',
    'fruit':          'fruit',
    'vegetable':      'vegetable',
    'meat':           'meat',
    'fish':           'fish',
    'egg':            'egg',
    'snack':          'snack',
    'beverage':       'beverage',
    'dairy':          'dairy',
    'sweet':          'sweet',
    'bakery':         'bakery',
    'soup':           'soup',
    'salad':          'salad',
    'juice':          'juice',
    'noodle':         'noodle',
    'shaak':          'shaak',
    'breakfast':      'breakfast',
    'legume':         'legume',
    'restaurant_food':'restaurant_food',
}

# ─── Bengali translation dictionary ───────────────────────────────────────────
# word → Bengali translation (for building translations from EN name parts)
BN_WORD_MAP = {
    # Alcoholic beverages
    'rum': 'রাম', 'beer': 'বিয়ার', 'whisky': 'হুইস্কি', 'whiskey': 'হুইস্কি',
    'vodka': 'ভদকা', 'gin': 'জিন', 'wine': 'ওয়াইন', 'brandy': 'ব্র্যান্ডি',
    'tequila': 'তেকিলা', 'champagne': 'শ্যাম্পেন', 'sake': 'সাকে',
    'scotch': 'স্কচ', 'bourbon': 'বার্বন', 'cocktail': 'ককটেল',
    'lager': 'লেগার', 'ale': 'এল বিয়ার', 'stout': 'স্টাউট',
    'mead': 'মিড', 'cider': 'সাইডার', 'sangria': 'সাংগ্রিয়া',
    'mojito': 'মোজিতো', 'margarita': 'মার্গারিটা', 'daiquiri': 'ডাইকিরি',
    'martini': 'মার্টিনি', 'shot': 'শট',

    # Coffee drinks
    'coffee': 'কফি', 'espresso': 'এসপ্রেসো', 'latte': 'ল্যাটে',
    'cappuccino': 'ক্যাপুচিনো', 'americano': 'আমেরিকানো',
    'mocha': 'মোকা কফি', 'frappe': 'ফ্র্যাপে', 'frappuccino': 'ফ্র্যাপুচিনো',
    'cold coffee': 'কোল্ড কফি', 'iced coffee': 'আইসড কফি',
    'macchiato': 'ম্যাকিয়াটো', 'affogato': 'আফোগাটো',
    'flat white': 'ফ্ল্যাট হোয়াইট', 'lungo': 'লুঙ্গো',
    'cold brew': 'কোল্ড ব্রু কফি',

    # Smoothies & shakes
    'smoothie': 'স্মুদি', 'shake': 'শেক', 'milkshake': 'মিল্কশেক',
    'protein shake': 'প্রোটিন শেক', 'green smoothie': 'সবুজ স্মুদি',

    # Protein / fitness
    'protein bar': 'প্রোটিন বার', 'protein': 'প্রোটিন', 'whey': 'হোয়ে',
    'creatine': 'ক্রিয়াটিন', 'bcaa': 'বিসিএএ', 'supplement': 'সাপ্লিমেন্ট',
    'energy bar': 'এনার্জি বার', 'granola bar': 'গ্রানোলা বার',
    'nutrition bar': 'নিউট্রিশন বার',

    # Desserts
    'cake': 'কেক', 'brownie': 'ব্রাউনি', 'tiramisu': 'তিরামিসু',
    'cheesecake': 'চিজকেক', 'mousse': 'মুস', 'pudding': 'পুডিং',
    'tart': 'টার্ট', 'pastry': 'পেস্ট্রি', 'eclair': 'এক্লেয়ার',
    'profiterole': 'প্রফিটারোল', 'macaron': 'ম্যাকারঁ',
    'waffle': 'ওয়াফেল', 'crepe': 'ক্রেপ', 'pancake': 'প্যানকেক',
    'muffin': 'মাফিন', 'cupcake': 'কাপকেক', 'donut': 'ডোনাট',
    'doughnut': 'ডোনাট', 'ice cream': 'আইসক্রিম', 'gelato': 'জেলাটো',
    'sorbet': 'সরবেট', 'panna cotta': 'পান্না কোট্টা',
    'creme brulee': 'ক্রেম ব্রুলে', 'parfait': 'পারফেট',
    'sundae': 'সানডে', 'fudge': 'ফাজ', 'toffee': 'টফি',
    'caramel': 'ক্যারামেল', 'truffle': 'ট্রাফেল',

    # Snacks
    'chips': 'চিপস', 'nachos': 'নাচোস', 'popcorn': 'পপকর্ন',
    'pretzel': 'প্রেটজেল', 'cracker': 'ক্র্যাকার', 'rice cake': 'রাইস কেক',
    'trail mix': 'ট্রেইল মিক্স', 'mixed nuts': 'মিক্সড নাট',

    # Fast food
    'burger': 'বার্গার', 'pizza': 'পিৎজা', 'hot dog': 'হট ডগ',
    'sandwich': 'স্যান্ডউইচ', 'wrap': 'র‍্যাপ', 'taco': 'ট্যাকো',
    'burrito': 'বুরিতো', 'quesadilla': 'কেসাডিলা', 'nachos': 'নাচোস',
    'french fries': 'ফ্রেঞ্চ ফ্রাই', 'fries': 'ফ্রাই', 'nuggets': 'নাগেট',

    # Dairy
    'milk': 'দুধ', 'full cream milk': 'ফুল ক্রিম দুধ',
    'toned milk': 'টোনড দুধ', 'skim milk': 'স্কিম দুধ',
    'almond milk': 'বাদাম দুধ', 'soy milk': 'সয়া দুধ',
    'oat milk': 'ওট দুধ', 'coconut milk': 'নারকেল দুধ',
    'curd': 'দই', 'yogurt': 'দই', 'greek yogurt': 'গ্রিক দই',
    'cheese': 'পনির', 'cream': 'ক্রিম', 'butter': 'মাখন',
    'ghee': 'ঘি', 'paneer': 'পনির',
    'whipped cream': 'হুইপড ক্রিম', 'cream cheese': 'ক্রিম চিজ',

    # Bread types
    'bread': 'রুটি', 'whole wheat bread': 'পুরো গমের রুটি',
    'white bread': 'সাদা রুটি', 'multigrain': 'মাল্টিগ্রেন',
    'sourdough': 'সাওয়ারডো', 'baguette': 'বাগেট',
    'ciabatta': 'চিয়াবাটা', 'focaccia': 'ফোকাচ্চা',
    'pita': 'পিতা', 'tortilla': 'টর্টিলা', 'bagel': 'বেগেল',
    'croissant': 'ক্রোয়াসাঁ',

    # International cuisine
    'sushi': 'সুশি', 'sashimi': 'সাশিমি', 'ramen': 'রামেন',
    'pad thai': 'প্যাড থাই', 'fried rice': 'ফ্রাইড রাইস',
    'dim sum': 'ডিম সাম', 'spring roll': 'স্প্রিং রোল',
    'tempura': 'টেম্পুরা', 'teriyaki': 'তেরিয়াকি',
    'steak': 'স্টেক', 'pasta': 'পাস্তা', 'risotto': 'রিসোটো',
    'lasagna': 'লাজানিয়া', 'gnocchi': 'নিওকি',
    'hummus': 'হুমুস', 'falafel': 'ফালাফেল', 'shawarma': 'শাওয়ারমা',
    'kebab': 'কাবাব', 'gyro': 'জাইরো', 'paella': 'পায়েলা',
    'tagine': 'তাজিন',

    # Grains
    'oats': 'ওটস', 'granola': 'গ্রানোলা', 'muesli': 'মুয়েসলি',
    'quinoa': 'কিনোয়া', 'barley': 'যব', 'rye': 'রাই',
    'bulgur': 'বুলগুর', 'couscous': 'কুসকুস',
    'cornflakes': 'কর্নফ্লেক্স', 'cereal': 'সিরিয়াল',

    # Fruits
    'apple': 'আপেল', 'banana': 'কলা', 'mango': 'আম',
    'orange': 'কমলা', 'grape': 'আঙুর', 'strawberry': 'স্ট্রবেরি',
    'blueberry': 'ব্লুবেরি', 'raspberry': 'রাসবেরি',
    'blackberry': 'ব্ল্যাকবেরি', 'cherry': 'চেরি',
    'peach': 'পিচ', 'pear': 'নাশপাতি', 'plum': 'বরই',
    'watermelon': 'তরমুজ', 'melon': 'খরবুজ',
    'pineapple': 'আনারস', 'papaya': 'পেঁপে',
    'guava': 'পেয়ারা', 'lychee': 'লিচু',
    'jackfruit': 'কাঁঠাল', 'coconut': 'নারকেল',
    'avocado': 'অ্যাভোকাডো', 'kiwi': 'কিউই',
    'pomegranate': 'ডালিম', 'passion fruit': 'প্যাশন ফল',
    'dragon fruit': 'ড্রাগন ফল', 'fig': 'ডুমুর',
    'date': 'খেজুর', 'apricot': 'আপ্রিকট',
    'mulberry': 'তুঁত', 'gooseberry': 'আমলকি',

    # Vegetables
    'potato': 'আলু', 'tomato': 'টমেটো', 'onion': 'পেঁয়াজ',
    'garlic': 'রসুন', 'ginger': 'আদা', 'carrot': 'গাজর',
    'spinach': 'পালং', 'broccoli': 'ব্রকলি',
    'cauliflower': 'ফুলকপি', 'cabbage': 'বাঁধাকপি',
    'capsicum': 'ক্যাপসিকাম', 'cucumber': 'শসা',
    'pumpkin': 'কুমড়ো', 'corn': 'ভুট্টা',
    'mushroom': 'মাশরুম', 'sweet potato': 'মিষ্টি আলু',
    'bitter gourd': 'করলা', 'bottle gourd': 'লাউ',
    'eggplant': 'বেগুন', 'peas': 'মটরশুটি',
    'beans': 'শিম', 'okra': 'ঢেঁড়স',
    'beetroot': 'বিট', 'radish': 'মুলা',
    'celery': 'সেলারি', 'zucchini': 'জুকিনি',
    'asparagus': 'অ্যাসপারাগাস', 'artichoke': 'আর্টিচোক',
    'leek': 'লিক', 'turnip': 'শালগম',

    # Proteins
    'chicken': 'মুরগি', 'mutton': 'মাটন', 'beef': 'গরু',
    'pork': 'শুকর', 'lamb': 'ভেড়া', 'duck': 'হাঁস',
    'turkey': 'টার্কি', 'fish': 'মাছ', 'prawn': 'চিংড়ি',
    'shrimp': 'চিংড়ি', 'crab': 'কাঁকড়া', 'lobster': 'লবস্টার',
    'salmon': 'স্যামন', 'tuna': 'টুনা', 'tilapia': 'তেলাপিয়া',
    'egg': 'ডিম', 'tofu': 'টোফু', 'tempeh': 'টেম্পে',

    # Pulses & legumes
    'lentil': 'ডাল', 'chickpea': 'ছোলা', 'kidney bean': 'কিডনি বিন',
    'black bean': 'কালো বিন', 'soybean': 'সয়াবিন',
    'peanut': 'চিনাবাদাম', 'almond': 'বাদাম',
    'cashew': 'কাজু', 'walnut': 'আখরোট', 'pistachio': 'পেস্তা',
    'hazelnut': 'হেজেলনাট', 'pecan': 'পিকান',
    'sunflower seed': 'সূর্যমুখী বীজ', 'pumpkin seed': 'কুমড়ো বীজ',
    'chia seed': 'চিয়া বীজ', 'flaxseed': 'তিসির বীজ',
    'sesame': 'তিল',

    # Common qualifiers
    'grilled': 'গ্রিলড', 'fried': 'ভাজা', 'baked': 'বেকড',
    'steamed': 'ভাপানো', 'boiled': 'সিদ্ধ', 'roasted': 'ভাজা',
    'raw': 'কাঁচা', 'fresh': 'তাজা', 'dried': 'শুকনো',
    'frozen': 'হিমায়িত', 'canned': 'টিনজাত', 'smoked': 'ধূমায়িত',
    'organic': 'জৈব', 'low fat': 'লো ফ্যাট', 'non fat': 'নন ফ্যাট',
    'sugar free': 'চিনিমুক্ত', 'diet': 'ডায়েট',
    'light': 'লাইট', 'extra': 'এক্সট্রা', 'double': 'ডাবল',
    'small': 'ছোট', 'medium': 'মাঝারি', 'large': 'বড়',
    'with': 'সহ', 'without': 'ছাড়া', 'and': 'ও',

    # Spices & condiments
    'salt': 'লবণ', 'pepper': 'মরিচ', 'cumin': 'জিরা',
    'coriander': 'ধনিয়া', 'turmeric': 'হলুদ', 'chilli': 'মরিচ',
    'cardamom': 'এলাচ', 'cinnamon': 'দারুচিনি',
    'clove': 'লবঙ্গ', 'nutmeg': 'জায়ফল',
    'saffron': 'জাফরান', 'bay leaf': 'তেজপাতা',
    'mustard': 'সরিষা', 'fennel': 'মৌরি',

    # Sauces & condiments
    'ketchup': 'কেচাপ', 'mayonnaise': 'মেওনেজ',
    'mustard sauce': 'সরিষার সস', 'hot sauce': 'হট সস',
    'soy sauce': 'সয়া সস', 'vinegar': 'ভিনেগার',
    'olive oil': 'অলিভ অয়েল', 'coconut oil': 'নারকেল তেল',
    'sunflower oil': 'সূর্যমুখী তেল',

    # Brands common words
    'classic': 'ক্লাসিক', 'original': 'অরিজিনাল',
    'premium': 'প্রিমিয়াম', 'special': 'স্পেশাল',
    'deluxe': 'ডিলাক্স', 'supreme': 'সুপ্রিম',
}

# ─── Phonetic transliteration (romanised syllable → Bengali) ──────────────────
PHONETIC_MAP = [
    # Must be ordered longest → shortest to avoid partial-match problems
    ('tch', 'চ'), ('sh',  'শ'), ('ch',  'চ'), ('ph',  'ফ'),
    ('th',  'থ'), ('kh',  'খ'), ('gh',  'ঘ'), ('zh',  'জ'),
    ('wh',  'হু'), ('qu', 'কু'),
    ('a',   'অ'), ('e',   'এ'), ('i',   'ই'), ('o',   'ও'),
    ('u',   'উ'), ('b',   'ব'), ('c',   'ক'), ('d',   'ড'),
    ('f',   'ফ'), ('g',   'গ'), ('h',   'হ'), ('j',   'জ'),
    ('k',   'ক'), ('l',   'ল'), ('m',   'ম'), ('n',   'ন'),
    ('p',   'প'), ('q',   'ক'), ('r',   'র'), ('s',   'স'),
    ('t',   'ট'), ('v',   'ভ'), ('w',   'ওয়'), ('x',  'ক্স'),
    ('y',   'য'), ('z',   'জ'),
]

def phonetic_transliterate(text: str) -> str:
    """Very rough phonetic transliteration EN→BN for unknown words."""
    result = ''
    i = 0
    text = text.lower()
    while i < len(text):
        matched = False
        for (lat, ben) in PHONETIC_MAP:
            if text[i:i+len(lat)] == lat:
                result += ben
                i += len(lat)
                matched = True
                break
        if not matched:
            result += text[i]
            i += 1
    return result

def build_bengali(en_name: str, existing_bn: str | None, cat: str) -> str:
    """Return a Bengali name for the item."""
    if existing_bn and existing_bn.strip():
        return existing_bn.strip()

    name_lower = en_name.lower().strip()

    # Try full-phrase lookup first
    if name_lower in BN_WORD_MAP:
        return BN_WORD_MAP[name_lower]

    # Try to build from parts (longest match first)
    words = name_lower.split()
    bn_parts = []
    i = 0
    while i < len(words):
        # try 3-gram, 2-gram, 1-gram phrase lookups
        found = False
        for span in (3, 2, 1):
            phrase = ' '.join(words[i:i+span])
            if phrase in BN_WORD_MAP:
                bn_parts.append(BN_WORD_MAP[phrase])
                i += span
                found = True
                break
        if not found:
            # Use phonetic for unknown single word
            bn_parts.append(phonetic_transliterate(words[i]))
            i += 1

    return ' '.join(bn_parts) if bn_parts else phonetic_transliterate(name_lower)

# ─── Name normalisation for deduplication ─────────────────────────────────────
_STRIP_TOKENS = re.compile(r"[^\w\s]")

def norm_key(name: str) -> str:
    """Normalise an EN food name into a dedup comparison key."""
    s = name.lower().strip()
    s = unicodedata.normalize('NFKD', s)
    s = _STRIP_TOKENS.sub('', s)
    s = re.sub(r'\s+', ' ', s).strip()
    # Remove common trailing plurals/descriptors
    s = re.sub(r'\braw\b', '', s)
    s = re.sub(r'\bfresh\b', '', s)
    s = re.sub(r'\bs\b', '', s)  # simple plural
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

# ─── Parse foodmissing.txt (multiple JSON arrays) ─────────────────────────────
def parse_missing(path: str) -> list[dict]:
    decoder = json.JSONDecoder()
    with open(path, encoding='utf-8') as f:
        content = f.read()

    items = []
    pos = 0
    errors = 0
    while pos < len(content):
        while pos < len(content) and content[pos] in ' \t\n\r':
            pos += 1
        if pos >= len(content):
            break
        try:
            obj, end = decoder.raw_decode(content, pos)
            if isinstance(obj, list):
                items.extend(obj)
            elif isinstance(obj, dict):
                items.append(obj)
            pos = end
        except json.JSONDecodeError:
            errors += 1
            pos += 1

    print(f'  Parsed {len(items)} items from {path} ({errors} JSON errors skipped)')
    return items

# ─── Convert foodmissing item to main-dataset schema ──────────────────────────
def normalise_cat(cat: str | None) -> str:
    if not cat:
        return 'snack'
    c = cat.lower().strip()
    return CATEGORY_MAP.get(c, c)

def to_float(v) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def missing_to_main(item: dict, new_id: int) -> dict:
    """Convert a foodmissing.txt item to the main-dataset schema."""
    en = (item.get('en') or item.get('name') or '').strip()
    if not en:
        return None

    # Category: try 'cat' then 'category'
    raw_cat = item.get('cat') or item.get('category') or ''
    cat = normalise_cat(raw_cat)

    # Bengali
    bn_raw = item.get('bn') or item.get('local_name') or ''
    bn = build_bengali(en, bn_raw, cat)

    # Serving
    s = (item.get('s') or '100g').strip()

    # Macros
    k  = to_float(item.get('k'))
    p  = to_float(item.get('p'))
    c  = to_float(item.get('c'))
    f  = to_float(item.get('f'))
    fi = to_float(item.get('fi'))
    ca = to_float(item.get('ca') or item.get('calcium'))
    fe = to_float(item.get('fe') or item.get('iron'))
    zn = to_float(item.get('zn') or item.get('magnesium'))
    mg = to_float(item.get('mg') or item.get('magnesium'))
    pot = to_float(item.get('pot') or item.get('potassium') or item.get('na'))
    va = to_float(item.get('va') or item.get('vit_a'))
    vc = to_float(item.get('vc') or item.get('vitc') or item.get('vit_c'))
    vd = to_float(item.get('vd'))
    na = to_float(item.get('na') or item.get('sodium'))
    sugar = to_float(item.get('sugar'))
    alc_g = to_float(item.get('alcohol') or item.get('alc_g'))

    # Defaults for missing macros
    if k is None: k = 0.0
    if p is None: p = 0.0
    if c is None: c = 0.0
    if f is None: f = 0.0
    if fi is None: fi = 0.0

    # Build quality score based on available data
    filled_count = sum(1 for v in [ca, fe, zn, mg, pot, va, vc, vd] if v is not None and v > 0)
    qs = 40 + filled_count * 5  # 40-80 range

    out = {
        'en': en,
        'bn': bn,
        's': s,
        'k': round(k, 1),
        'p': round(p, 1),
        'c': round(c, 1),
        'f': round(f, 1),
        'fi': round(fi, 1),
        'cat': cat,
        'kw': [],
        'src': 'brand' if item.get('brand') else 'local',
        'id': new_id,
        'quality_score': qs,
        'popularity_score': 40,
        'search_priority': 45,
        'aliases': [],
        'canonical': True,
    }
    if item.get('brand'):
        out['brand'] = item['brand']
    if ca is not None:
        out['ca'] = round(ca, 1)
    if fe is not None:
        out['fe'] = round(fe, 3)
    if zn is not None:
        out['zn'] = round(zn, 2)
    if mg is not None:
        out['mg'] = round(mg, 1)
    if pot is not None:
        out['pot'] = round(pot, 1)
    if va is not None:
        out['va'] = round(va, 1)
    if vc is not None:
        out['vc'] = round(vc, 2)
    if vd is not None:
        out['vd'] = round(vd, 2)
    if na is not None:
        out['na'] = round(na, 1)
    if sugar is not None:
        out['sugar'] = round(sugar, 1)
    if alc_g is not None:
        out['alc_g'] = round(alc_g, 2)
    return out

# ─── Priority scoring for trimming ────────────────────────────────────────────
def item_priority(item: dict, is_main: bool) -> int:
    """Higher is better. Main items always beat missing items."""
    base = 10000 if is_main else 0
    qs = item.get('quality_score', 40)
    ps = item.get('popularity_score', 40)
    sp = item.get('search_priority', 45)
    # Bonus for having real nutrition data
    k = item.get('k', 0) or 0
    nutrition_bonus = 20 if k > 0 else 0
    # Bonus for having micronutrients
    micro = sum(1 for field in ['ca', 'fe', 'zn', 'mg', 'pot', 'va', 'vc', 'vd']
                if item.get(field, 0) or 0 > 0)
    micro_bonus = micro * 3
    # Bonus for having bn
    bn_bonus = 10 if item.get('bn') else 0
    return base + qs + ps + sp + nutrition_bonus + micro_bonus + bn_bonus

# ─── Main merge logic ─────────────────────────────────────────────────────────
def main():
    print(f'Loading main dataset: {MAIN_FILE}')
    with open(MAIN_FILE, encoding='utf-8') as f:
        main_items = json.load(f)
    print(f'  {len(main_items)} items')

    print(f'Parsing foodmissing: {MISSING_FILE}')
    raw_missing = parse_missing(MISSING_FILE)

    # ── Remove duplicates within main dataset ─────────────────────────────────
    print('Deduplicating main dataset...')
    seen_main = {}
    clean_main = []
    for item in main_items:
        key = norm_key(item.get('en', ''))
        if not key:
            continue
        if key not in seen_main:
            seen_main[key] = True
            clean_main.append(item)
    print(f'  {len(main_items) - len(clean_main)} duplicates removed from main')
    print(f'  {len(clean_main)} unique main items')

    # ── Validate basic structure for missing items ────────────────────────────
    print('Filtering missing items...')
    valid_missing = []
    for item in raw_missing:
        en = (item.get('en') or item.get('name') or '').strip()
        if not en:
            continue
        if not isinstance(item.get('k'), (int, float)) and not isinstance(item.get('k'), str):
            pass  # allow, will default to 0
        valid_missing.append(item)
    print(f'  {len(valid_missing)} valid missing items')

    # ── Find next available ID ────────────────────────────────────────────────
    main_id_set = set(item['id'] for item in clean_main if isinstance(item.get('id'), int))
    next_id = max(main_id_set) + 1 if main_id_set else 200000
    # Make sure we start well above the main dataset max
    next_id = max(next_id, 200001)

    # ── Convert missing items to main schema ─────────────────────────────────
    print('Converting missing items to main schema...')
    converted = []
    for item in valid_missing:
        result = missing_to_main(item, next_id)
        if result:
            converted.append(result)
            next_id += 1
    print(f'  {len(converted)} items converted')

    # ── Deduplicate missing against main ─────────────────────────────────────
    print('Deduplicating missing items against main dataset...')
    new_items = []
    skipped_dups = 0
    for item in converted:
        key = norm_key(item.get('en', ''))
        if key in seen_main:
            skipped_dups += 1
            continue
        # Also check high similarity to existing keys
        is_dup = False
        for existing_key in seen_main:
            if len(key) > 4 and len(existing_key) > 4:
                sim = similarity(key, existing_key)
                if sim > 0.92:
                    is_dup = True
                    break
        if is_dup:
            skipped_dups += 1
            continue
        seen_main[key] = True
        new_items.append(item)
    print(f'  {skipped_dups} duplicates skipped')
    print(f'  {len(new_items)} unique new items from missing file')

    # ── Also remove duplicates within new_items ───────────────────────────────
    seen_new = {}
    deduped_new = []
    for item in new_items:
        key = norm_key(item.get('en', ''))
        if key not in seen_new:
            seen_new[key] = True
            deduped_new.append(item)
    print(f'  {len(new_items) - len(deduped_new)} intra-missing dups removed')
    new_items = deduped_new

    # ── Merge & target 5000 ───────────────────────────────────────────────────
    total_available = len(clean_main) + len(new_items)
    print(f'\nTotal available: {total_available} ({len(clean_main)} main + {len(new_items)} new)')

    if total_available <= TARGET_COUNT:
        # Use everything
        merged = clean_main + new_items
        print(f'Using all {len(merged)} items (under target {TARGET_COUNT})')
        if len(merged) < TARGET_COUNT:
            print(f'  WARNING: only {len(merged)} unique items, target was {TARGET_COUNT}')
    else:
        # Keep all main items, select best from new_items
        new_needed = TARGET_COUNT - len(clean_main)
        if new_needed < 0:
            # Main itself is over 5000 — trim main by lowest priority
            print(f'Main dataset alone has {len(clean_main)} items, trimming to {TARGET_COUNT}')
            clean_main.sort(key=lambda x: item_priority(x, True), reverse=True)
            merged = clean_main[:TARGET_COUNT]
        else:
            # Select best new_items
            new_items.sort(key=lambda x: item_priority(x, False), reverse=True)
            selected_new = new_items[:new_needed]
            merged = clean_main + selected_new
            print(f'Selected {len(selected_new)} new items (needed {new_needed} to reach {TARGET_COUNT})')

    print(f'\nFinal dataset: {len(merged)} items')

    # ── Validate & fix all items ───────────────────────────────────────────────
    print('Validating all items...')
    main_id_set = set(item['id'] for item in clean_main if isinstance(item.get('id'), int))
    next_id = max(main_id_set | {200000}) + 1
    no_bn = 0
    fixed_cat = 0
    reassigned_ids = 0

    for item in merged:
        # Ensure bn
        if not item.get('bn'):
            item['bn'] = build_bengali(item.get('en', ''), None, item.get('cat', ''))
            no_bn += 1

        # Ensure category is in known set
        cat = item.get('cat', '')
        normalised = normalise_cat(cat)
        if normalised != cat:
            item['cat'] = normalised
            fixed_cat += 1

        # Ensure numeric fields are floats
        for fld in ['k', 'p', 'c', 'f', 'fi']:
            v = item.get(fld)
            if v is None:
                item[fld] = 0.0
            elif not isinstance(v, float):
                try:
                    item[fld] = float(v)
                except (TypeError, ValueError):
                    item[fld] = 0.0

        # Ensure serving string
        if not item.get('s'):
            item['s'] = '100g'

        # Ensure kw is list
        if not isinstance(item.get('kw'), list):
            item['kw'] = []

    print(f'  {no_bn} items got Bengali auto-generated')
    print(f'  {fixed_cat} items had category fixed')

    # ── Category stats ────────────────────────────────────────────────────────
    cats = collections.Counter(item.get('cat', '?') for item in merged)
    print('\nCategory distribution:')
    for cat, count in cats.most_common():
        print(f'  {cat}: {count}')

    # ── Write output ──────────────────────────────────────────────────────────
    print(f'\nWriting {OUTPUT_FILE}...')
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(merged, f, ensure_ascii=False, separators=(',', ':'), indent=None)

    import os
    size_mb = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f'Done. {len(merged)} items, {size_mb:.1f} MB')

    # ── Quick audit ───────────────────────────────────────────────────────────
    print('\n── Audit ─────────────────────────────────')
    no_bn_final = sum(1 for item in merged if not item.get('bn'))
    no_k_final  = sum(1 for item in merged if not item.get('k'))
    id_set = [item.get('id') for item in merged if isinstance(item.get('id'), int)]
    dup_ids = len(id_set) - len(set(id_set))
    print(f'  Items without bn: {no_bn_final}')
    print(f'  Items with k=0:   {no_k_final}')
    print(f'  Duplicate IDs:    {dup_ids}')
    print('──────────────────────────────────────────')

if __name__ == '__main__':
    main()
