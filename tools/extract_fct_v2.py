"""
Bangladesh FCT PDF extractor v2 - uses column-based word extraction for clean names.
Removes all previous bd_fct entries and re-adds correctly.
"""
import pdfplumber, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH   = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\FCT_10_2_14_final_version.pdf'
MASTER     = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v5_3.json'
INDEX_EN   = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_en_v5_3.json'
INDEX_BN   = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_bn_v5_3.json'

# ---------------------------------------------------------------------------
# Bengali Unicode name map  (keyed by clean English food name, lowercase)
# Based on Bangladesh FCT food items – proper Bengali script
# ---------------------------------------------------------------------------
BN_MAP = {
    # ---- Cereals ----
    "barley, whole-grain, raw": "যব, গোটা শস্য",
    "biscuit, sweet": "মিষ্টি বিস্কুট",
    "bread, bun/roll": "বনরুটি / বান / রোল",
    "bread, white, for toasting": "পাউরুটি",
    "maize/corn flour, whole, white": "ভুট্টার আটা",
    "maize/corn, yellow, dried, raw": "শুকনো ভুট্টা, হলুদ",
    "millet, foxtail, raw": "কাউন",
    "millet, proso, whole-grain, raw": "চিনা ধান, গোটা",
    "pearl millet, whole-grain, raw": "বাজরা, গোটা",
    "popcorn, maize (salt added)": "পপকর্ন (লবণ সহ)",
    "rice flakes, white grain, water-soaked": "চিড়া, ভেজানো",
    "rice flakes, white grain, raw": "চিড়া",
    "rice, br-28, parboiled, milled, raw": "চাল, BR-28, সিদ্ধ, কুঁড়া ছাড়া",
    "rice, br-11, parboiled, milled, raw": "চাল, BR-11, সিদ্ধ, কুঁড়া ছাড়া",
    "rice, br-16, parboiled, milled, raw": "চাল, BR-16, সিদ্ধ, কুঁড়া ছাড়া",
    "rice, br-26, parboiled, milled, raw": "চাল, BR-26, সিদ্ধ, কুঁড়া ছাড়া",
    "rice, br-3, parboiled, milled, raw": "চাল, BR-3, সিদ্ধ, কুঁড়া ছাড়া",
    "rice, brri dhan-30, parboiled, milled, raw": "চাল, BRRI ধান-30, সিদ্ধ",
    "rice, brri dhan-40, parboiled, milled, raw": "চাল, BRRI ধান-40, সিদ্ধ",
    "rice, bran, raw": "চালের কুঁড়া",
    "rice, parboiled, milled, raw": "চাল, সিদ্ধ, ঢেঁকিছাটা",
    "rice, red, parboiled, milled, raw": "চাল, লাল, সিদ্ধ, কুঁড়া ছাড়া",
    "rice, popped": "খই",
    "rice, puffed, salted": "মুড়ি",
    "rice, white, sunned, polished, milled, raw": "চাল, আতপ, HYV, কুঁড়া ছাড়া",
    "rice, white, sunned, polished, milled, boiled* (without salt)": "ভাত, আতপ, বাসি ভাত",
    "rice, br-28, boiled* (without salt)": "ভাত, BR-28",
    "rice, boiled* (without salt)": "ভাত, সিদ্ধ, ঢেঁকিছাটা",
    "rice, red, parboiled, milled, boiled* (without salt)": "ভাত, লাল, সিদ্ধ, কুঁড়া ছাড়া",
    "rice, sugandhi, boiled* (without salt)": "ভাত, সুগন্ধি",
    "semolina, wheat, raw": "সুজি",
    "sorghum, raw": "জোয়ার",
    "sweet corn, yellow, on the cob, raw": "কাঁচা ভুট্টা, হলুদ",
    "vermicelli, wheat, raw": "সেমাই",
    "vermicelli, boiled* (without salt)": "সেমাই সিদ্ধ",
    "wheat, flour, white": "আটা, সাদা",
    "wheat flour, white, refined": "ময়দা",
    "wheat, whole, raw": "গম, গোটা",
    "plain khichuri": "সাদা খিচুড়ি",
    "plain pulao": "সাদা পোলাও",
    "ruti": "রুটি",
    # ---- Legumes / Pulses ----
    "bengal gram, black, raw": "কালো ছোলা",
    "bengal gram, whole, dried, raw": "ছোলা, শুকনো",
    "black gram, dehulled, dried, raw": "মাষকলাই ডাল, আস্ত",
    "black gram, split, dried, raw": "মাষকলাই ডাল, ভাঙা",
    "green gram, split, dried, raw": "মুগ ডাল, ভাঙা",
    "green gram, whole, dried, raw": "মুগ ডাল, আস্ত",
    "grass pea, split, dried, raw": "খেসারি ডাল",
    "lentil, dried, raw": "মসুর ডাল",
    "pea, dried, raw": "মটর",
    "red gram, split, dried, raw": "অড়হর ডাল",
    "soybean, dried, raw": "সয়াবিন",
    "bengal gram, whole, boiled* (without salt)": "ছোলা সিদ্ধ",
    "green gram, split, boiled* (without salt)": "মুগ ডাল সিদ্ধ",
    "lentil, boiled* (without salt)": "মসুর ডাল সিদ্ধ",
    "pea, boiled* (without salt)": "মটর সিদ্ধ",
    "cholar dal, vanga": "ছোলার ডাল, ভাঙা",
    # ---- Vegetables ----
    "amaranth, stem, raw": "ডাঁটাশাক",
    "bean, scarlet runner, raw": "শিম",
    "bean, seeds and pods, raw": "শিম, বিচিসহ",
    "beet root, red, raw": "বিট",
    "brinjal, purple, long, raw": "বেগুন, কালো, লম্বা",
    "broad beans, raw": "মাখন শিম",
    "cabbage, raw": "বাঁধাকপি",
    "carrot, raw": "গাজর",
    "cauliflower, raw": "ফুলকপি",
    "chilli, green, with seeds, raw": "কাঁচা মরিচ",
    "cowpea, pods and seeds, raw": "বরবটি",
    "cucumber, peeled, raw": "শসা",
    "drumstick, pods, raw": "সজিনা ডাঁটা",
    "garlic, raw": "রসুন",
    "gourd, ash, raw": "চালকুমড়া",
    "gourd, bitter, raw": "করলা",
    "gourd, bottle, raw": "লাউ",
    "gourd, pointed, raw": "পটল",
    "gourd, ridge, raw": "ঝিঙা",
    "gourd, snake, raw": "চিচিঙ্গা",
    "gourd, sponge, raw": "ধুন্দুল",
    "gourd, teasle, raw": "কাঁকরোল",
    "okra/ladies finger, raw": "ঢ্যাঁড়শ",
    "onion, raw": "পেঁয়াজ",
    "papaya, unripe, raw": "কাঁচা পেঁপে",
    "peas, raw": "কাঁচা মটরশুঁটি",
    "plantain, raw": "কাঁচা কলা",
    "pumpkin, raw": "মিষ্টি কুমড়া",
    "radish, raw": "মূলা",
    "tomato, green, raw": "কাঁচা টমেটো",
    "tomato, red, ripe, raw": "পাকা টমেটো",
    "turnip, raw": "শালগম",
    "brinjal, boiled* (without salt)": "বেগুন সিদ্ধ",
    "cabbage, boiled* (without salt)": "বাঁধাকপি সিদ্ধ",
    "carrot, boiled* (without salt)": "গাজর সিদ্ধ",
    "cauliflower, boiled* (without salt)": "ফুলকপি সিদ্ধ",
    "cowpea, boiled* (without salt)": "বরবটি সিদ্ধ",
    "gourd, pointed, boiled* (without salt)": "পটল সিদ্ধ",
    "gourd, teasle, boiled* (without salt)": "কাঁকরোল সিদ্ধ",
    "okra/lady's finger, boiled* (without salt)": "ঢ্যাঁড়শ সিদ্ধ",
    "papaya, unripe, boiled* (without salt)": "কাঁচা পেঁপে সিদ্ধ",
    "plantain, boiled* (without salt)": "কাঁচা কলা সিদ্ধ",
    "pumpkin, boiled* (without salt)": "মিষ্টি কুমড়া সিদ্ধ",
    "radish, boiled* (without salt)": "মূলা সিদ্ধ",
    "lady's finger-tomato bhuna": "ঢ্যাঁড়শ-টমেটো ভুনা",
    "gourd, bitter, boiled* (without salt)": "করলা সিদ্ধ",
    "gourd, bitter, fry": "করলা ভাজা",
    # ---- Leafy Vegetables ----
    "agathi, raw": "বক ফুল শাক",
    "alligator weed, raw": "মালঞ্চ শাক",
    "amaranth, leaves, spiney, raw": "কাঁটা নটে শাক",
    "amaranth, leaves, red, raw": "লাল শাক",
    "amaranth, leaves, green, raw": "সবুজ ডাঁটা শাক",
    "dock leaves, raw": "চুকাই শাক",
    "beet greens leaves": "বিট শাক",
    "bengal dayflower, leaves, raw": "বাত বেগুন শাক",
    "bitter gourd leaves, green, raw": "করলা শাক",
    "bottle gourd leaves, raw": "লাউ শাক",
    "bugleweed, raw": "সাবারং",
    "cassava, leaves, raw": "সিমি আলু শাক",
    "colocasia leaves, black, raw": "কালো কচু শাক",
    "colocasia leaves, green, raw": "সবুজ কচু শাক",
    "cowpea, leaves, raw": "বরবটি পাতা",
    "dima leaves, raw": "দিমা শাক",
    "drumstick, leaves, raw": "সজিনা পাতা",
    "fern, leaves, raw": "ঢেঁকি শাক",
    "fenugreek, leaves, raw": "মেথি শাক",
    "indian spinach, raw": "পুঁই শাক",
    "jute leaves, raw": "পাট শাক",
    "pumpkin leaves, raw": "মিষ্টি কুমড়ার শাক",
    "radish leaves, raw": "মূলা শাক",
    "slender amaranth leaves, raw": "নটে শাক",
    "spinach, raw": "পালং শাক",
    "sweet potato leaves, raw": "মিষ্টি আলুর শাক",
    "sweet potato leaves, sp4, dark green, mature, raw": "মিষ্টি আলুর শাক (SP4)",
    "sweet potato leaves, sp7, dark green, mature, raw": "মিষ্টি আলুর শাক (SP7)",
    "sweet potato leaves, sp8, light green, mature, raw": "মিষ্টি আলুর শাক (SP8)",
    "water spinach, raw": "কলমি শাক",
    "watercress, raw": "হেলেঞ্চা শাক",
    "amaranth leaves, red, boiled* (without salt)": "লাল শাক সিদ্ধ",
    "slender amaranth leaves, boiled* (without salt)": "নটে শাক সিদ্ধ",
    "spinach, boiled* (without salt)": "পালং শাক সিদ্ধ",
    # ---- Roots & Tubers ----
    "colocasia/taro, corm, raw": "কচুর মুখী",
    "colocasia/taro/tannia, cormel, raw": "দুধকচু",
    "elephant foot, corm, raw": "ওল কচু",
    "giant taro, corm, raw": "মানকচু",
    "potato, diamond, raw": "গোল আলু, Diamond জাত",
    "sweet potato, orange flesh, raw": "মিষ্টি আলু, কমলা সুন্দরী",
    "sweet potato, pale-yellow flesh, raw": "মিষ্টি আলু, হলদে",
    "sweet potato, red skin, raw": "মিষ্টি আলু, লাল খোসা",
    "sweet potato, white flesh, raw": "মিষ্টি আলু, সাদা",
    "yam, tuber, raw": "বন আলু",
    "colocasia/taro, boiled* (without salt)": "কচুর মুখী সিদ্ধ",
    "potato, diamond, boiled* (without salt)": "গোল আলু সিদ্ধ",
    "colocasia/taro/tannia, cormel, boiled* (without salt)": "দুধকচু সিদ্ধ",
    "elephant foot, corm, boiled* (without salt)": "ওল কচু সিদ্ধ",
    "giant taro, corm, boiled* (without salt)": "মানকচু সিদ্ধ",
    "yam, tuber, boiled* (without salt)": "বন আলু সিদ্ধ",
    "potato mash": "আলু সিদ্ধ, লবণ সহ",
    # ---- Nuts & Seeds ----
    "sunflower seeds, dried": "সূর্যমুখীর বিচি",
    "cashew nuts, raw": "হিজলি বাদাম",
    "chilgoza pine, dried": "চিলগোজা",
    "coconut milk": "নারকেল দুধ",
    "coconut, desiccated": "শুকনো নারকেল",
    "coconut, mature kernel": "নারকেল",
    "groundnuts/peanut, raw": "চিনা বাদাম",
    "jackfruit seeds, raw": "কাঁঠালের বিচি",
    "linseed, raw": "তিসি",
    "lotus seeds, dried": "পদ্মের গোটা, শুকনো",
    "lotus seeds, green": "পদ্মের গোটা, কাঁচা",
    "mustard seeds, dried": "সরিষা",
    "pistachio nuts, dried": "পেস্তা বাদাম",
    "pumpkin seeds, dried": "মিষ্টি কুমড়ার বিচি",
    "sesame seeds, whole, dried": "তিল",
    "walnuts": "আখরোট",
    # ---- Spices & Herbs ----
    "bay leaf, dried": "তেজপাতা",
    "cardamom": "এলাচ",
    "chilli, red, dry": "শুকনো মরিচ",
    "cinnamon, ground": "দারচিনি গুঁড়া",
    "cloves, dried": "লবঙ্গ",
    "coriander leaves, raw": "ধনেপাতা",
    "coriander seed, dry": "ধনিয়া",
    "cumin seeds": "জিরা",
    "fennel seeds": "মৌরি",
    "fenugreek seeds": "মেথি",
    "ginger root, raw": "আদা",
    "indian pennywort, raw": "থানকুনি পাতা",
    "lemon grass, raw": "লেমন গ্রাস",
    "lemon peel, raw": "লেবুর খোসা",
    "mace, ground": "জয়িত্রী গুঁড়া",
    "nutmeg, dried": "জয়ফল",
    "pepper, black": "গোলমরিচ",
    "poppy seeds": "পোস্তদানা",
    "spearmint leaves, fresh": "পুদিনা পাতা",
    "turmeric, dried": "হলুদ",
    # ---- Fruits ----
    "apple, without skin, raw": "আপেল, খোসা ছাড়া",
    "apple, with skin, raw": "আপেল, খোসাসহ",
    "asian pears, raw": "নাশপাতি",
    "banana, sagar, ripe, raw": "কলা, সাগর, পাকা",
    "breadfruit, raw": "রুটি ফল",
    "bullocks heart, ripe, raw": "নোনা আতা",
    "carambola, raw": "কামরাঙা",
    "custard apple, raw": "আতাফল",
    "dates, dried": "খোরমা",
    "dates, raw": "খেজুর, পাকা, তাজা",
    "elephant apple, ripe, raw": "কদবেল",
    "emblic, raw": "আমলকি",
    "fig, ripe, raw": "ডুমুর, পাকা",
    "grapes, green, raw": "আঙুর, হালকা সবুজ",
    "guava, green, raw": "পেয়ারা",
    "hog plum, raw": "আমড়া",
    "jackfruit, ripe, raw": "কাঁঠাল, পাকা",
    "jambolan, raw": "কালোজাম",
    "jambos, raw": "জামরুল",
    "java apple, raw": "গোলাপজাম",
    "jujube, raw": "বরই",
    "lemon, kagoji, raw": "কাগজি লেবু",
    "lime, sweet, raw": "মুসাম্বি",
    "lychee, raw": "লিচু",
    "mango, fazli, orange flesh, ripe, raw": "আম, ফজলি, পাকা",
    "mango, langra, yellow flesh, ripe, raw": "আম, ল্যাংড়া, পাকা",
    "melon, futi, orange flesh, ripe, raw": "ফুটি, পাকা",
    "dewa": "দেওয়া ফল",
    "bangee, paka": "বাংগি, পাকা",
    "orange juice, raw (unsweetened)": "কমলার রস",
    "orange, raw": "কমলা",
    "orange, sweet, ripe, raw": "মাল্টা, পাকা",
    "taal, paka": "তাল, পাকা",
    "papaya, ripe, raw": "পেঁপে, পাকা",
    "persimmon, ripe, raw": "গাব",
    "pineapple, joldugee, ripe, raw": "আনারস, জলডুগি, পাকা",
    "pineapple, ripe, raw": "আনারস, পাকা",
    "pomegranate, ripe, with seed, raw": "বেদানা, পাকা",
    "pomelo, raw": "জম্বুরা",
    "tamarind, pulp, ripe, raw": "তেঁতুল, পাকা",
    "watermelon, ripe, raw": "তরমুজ, পাকা",
    "wood apple, ripe, raw": "বেল, পাকা",
    # ---- Fish & Seafood ----
    "anchovy, gangetic hairfin, dried": "ফেঁসো মাছ, শুঁটকি",
    "anchovy, gangetic hairfin, raw": "ফেঁসো মাছ",
    "anchovy, scaly hairfin, raw": "তেলি ফেঁসো মাছ",
    "barb, olive, without bones, raw": "সরপুঁটি মাছ, কাঁটা ছাড়া",
    "bata, raw": "বাটা মাছ",
    "boal, without bones, raw": "বোয়াল মাছ, কাঁটা ছাড়া",
    "bronze feather back, raw": "ফলি মাছ",
    "calbasu, without bones, raw": "কালবাউস মাছ",
    "catfish, bacha, raw": "বাচা মাছ",
    "catfish, pabda, raw": "পাবদা মাছ",
    "catla, raw": "কাতলা মাছ",
    "koi, deshi (eyes included)": "কই মাছ, দেশি, চোখসহ",
    "koi, thai (eyes included)": "কই মাছ, থাই, চোখসহ",
    "chital (without bones)": "চিতল মাছ, কাঁটা ছাড়া",
    "common carp, without bones, raw": "কমন কার্প মাছ, কাঁটা ছাড়া",
    "poa (without bones)": "পোয়া মাছ, কাঁটা ছাড়া",
    "kachki (mixed species)": "কাচকি মাছ",
    "gangetic ailia, raw": "কাজুলি মাছ",
    "gangetic mystus, raw": "গুলশা মাছ",
    "giant river-catfish, raw": "গুয়িজ্জা মাছ",
    "giant sea perch, without bones, raw": "ভেটকি মাছ, কাঁটা ছাড়া",
    "goby, tank goby, raw": "বেলে মাছ",
    "hilsha, without bones, raw": "ইলিশ মাছ, কাঁটা ছাড়া",
    "indian river shad, raw": "চাপিলা মাছ",
    "kuria labeo, without bones, raw": "গনিয়া মাছ, কাঁটা ছাড়া",
    "largescale/ayre (without bones)": "আইড় মাছ, কাঁটা ছাড়া",
    "minnow, finescale razorbelly, raw": "চেলা মাছ, ফুলচেলা",
    "minnow, large scale razorbelly, raw": "চেলা মাছ, নারকেলি",
    "mola (eyes included)": "মলা মাছ, চোখসহ",
    "mrigal carp, eyes included, raw": "মৃগেল মাছ, চোখসহ",
    "mussel/clam, mixed species, raw": "ঝিনুক",
    "pangas, without bones, raw": "পাঙ্গাস মাছ, কাঁটা ছাড়া",
    "pomfret, black, raw": "কালো পমফ্রেট মাছ",
    "pomfret, chinese silver, raw": "রুপচাঁদা মাছ, চিনা সাদা",
    "rohu, river, raw": "রুই মাছ, নদীর",
    "rohu, without bones, raw": "রুই মাছ, কাঁটা ছাড়া",
    "silver carp, without bones, raw": "সিলভার কার্প মাছ, কাঁটা ছাড়া",
    "stinging catfish, raw": "শিং মাছ, কাঁটা ছাড়া",
    "stone roller, raw": "তাটকিনি মাছ",
    "striped snake-head, raw": "শোল মাছ, কাঁটা ছাড়া",
    "tilapia, without bones, raw": "তেলাপিয়া মাছ, কাঁটা ছাড়া",
    "tuna, without bones, raw": "টুনা মাছ, কাঁটা ছাড়া",
    "walking catfish, without bones, raw": "মাগুর মাছ, কাঁটা ছাড়া",
    "small fish fry": "কাচকি মাছ ভাজা",
    "fish ball": "মাছের কোপ্তা",
    # ---- Meat & Poultry ----
    "beef liver, raw": "গরুর কলিজা",
    "beef, meat, lean, boneless, raw": "গরুর মাংস, চর্বিহীন, হাড় ছাড়া",
    "beef, meat, 15-20% fat, boneless, raw": "গরুর মাংস, ১৫-২০% চর্বি, হাড় ছাড়া",
    "beef, mince, lean, raw": "গরুর কিমা, চর্বিহীন",
    "buffalo meat, raw": "মহিষের মাংস",
    "chicken breast, without skin, raw": "মুরগির বুকের মাংস, চামড়া ছাড়া",
    "chicken leg, without skin, raw": "মুরগির ঠ্যাং, চামড়া ছাড়া",
    "chicken liver, raw": "মুরগির কলিজা",
    "duck, meat, raw": "হাঁসের মাংস",
    "goat meat, lean, raw": "খাসির মাংস, চর্বিহীন",
    "lamb/mutton, meat, moderately fat, raw": "ভেড়ার মাংস",
    "lamb/mutton, liver, raw": "ভেড়ার কলিজা",
    "pork, meat, <5 % fat, raw": "শূকরের মাংস",
    "beef handi kabab": "হাঁড়ি কাবাব (গরু)",
    "egg, chicken, farmed, raw": "মুরগির ডিম, ফার্মের",
    "egg, chicken, native, raw": "মুরগির ডিম, দেশি",
    "egg, chicken, native, yolk, raw": "মুরগির ডিমের কুসুম, দেশি",
    "egg, duck, whole, raw": "হাঁসের ডিম",
    "egg, duck, whole, boiled* (without salt)": "হাঁসের ডিম, সিদ্ধ",
    # ---- Dairy ----
    "buttermilk, fluid, low fat": "ঘোল",
    "cheese, cottage, 25% fat": "পনির",
    "curd, sweetened, whole milk": "মিষ্টি দই",
    "milk, buffalo, whole fat": "মহিষের দুধ",
    "milk, cow, powder, skimmed": "গুঁড়া দুধ, স্কিম",
    "milk, cow, powder, whole": "গুঁড়া দুধ, পূর্ণ ক্রিম",
    "milk, cow, skimmed": "গরুর দুধ, স্কিম",
    "milk, cow, whole fat (pasteurized, uth)": "গরুর দুধ, পূর্ণ চর্বি",
    "milk, goat, combined breeds": "ছাগলের দুধ",
    "milk, human, colostrum, raw": "শালদুধ (মায়ের প্রথম দুধ)",
    "milk, human, mature, raw": "মায়ের পরিপক্ব দুধ",
    "payesh": "পায়েস",
    "butter, salted": "মাখন, লবণযুক্ত",
    # ---- Oils & Fats ----
    "cottonseed oil": "তুলার বিচির তেল",
    "fish oil, cod liver": "কড লিভার তেল",
    "ghee, cow": "ঘি, গরু",
    "ghee, vegetable": "ডালডা / বনস্পতি",
    "margarine": "মার্জারিন",
    "mayonnaise, salted": "মেয়নেজ",
    "mustard oil": "সরিষার তেল",
    "palm oil": "পাম তেল",
    "peanut oil": "চিনা বাদামের তেল",
    "sesame oil": "তিলের তেল",
    "soybean oil": "সয়াবিন তেল",
    # ---- Beverages ----
    "coconut water": "ডাবের পানি",
    "coffee (with milk and sugar)": "কফি (দুধ ও চিনিসহ)",
    "coffee, powder": "কফি পাউডার",
    "soft drinks, carbonated": "কোমল পানীয়",
    "soya milk (not sweetened)": "সয়াবিনের দুধ",
    "sugar cane juice": "আখের রস",
    "tea, milk tea": "দুধ চা",
    "tea, infusion (with sugar)": "লিকার চা (চিনিসহ)",
    "tea, powder": "চা পাতা",
    # ---- Sugar & Sweets ----
    "baking powder": "বেকিং পাউডার",
    "betel leaves, raw": "পান পাতা",
    "honey": "মধু",
    "jaggery, sugarcane, solid": "গুড়, আখ",
    "jaggery/panela, date palm": "খেজুর গুড়",
    "jagggery liquid, date palm": "নলেন গুড়",
    "sugar, white": "চিনি, সাদা",
}

# Correct category mapping by FCT code prefix (from Bangladesh FCT food group structure)
# 01=Cereals, 02=Legumes, 03=Vegetables, 04=Leafy veg, 05=Roots/Tubers,
# 06=Nuts/Seeds, 07=Spices, 08=Fruits, 09=Fish/Seafood, 10=Meat/Poultry,
# 11=Eggs, 12=Dairy, 13=Fats/Oils, 14=Beverages, 15=Sugar/Misc
CAT_MAP = {
    '01': 'grain',    '02': 'legume',   '03': 'vegetable',
    '04': 'vegetable','05': 'vegetable','06': 'snack',
    '07': 'spice',    '08': 'fruit',    '09': 'fish',
    '10': 'meat',     '11': 'meat',     '12': 'dairy',
    '13': 'fat',      '14': 'beverage', '15': 'sweet',
}

# X-coordinate boundaries for columns on proximate pages
X_EN_MAX   = 281   # English name column ends here
X_BN_MAX   = 413   # Bengali transliteration column ends here
X_CODE_MAX = 125   # Code column ends here


def classify_page(text):
    if 'Food name in Bengali' in text or ('Edible' in text and 'portion' in text):
        return 'proximate'
    if 'Ca (mg)' in text or 'Fe (mg)' in text:
        return 'mineral'
    if 'Thiamin' in text or ('Vitamin A' in text and 'Retinol' in text):
        return 'vitamin'
    return None


def safe(v):
    if v is None:
        return None
    try:
        return float(str(v).strip('[]() '))
    except ValueError:
        return None


def extract_proximate(page):
    """Extract code, English name, Bengali transliteration, and nutrients using word positions."""
    words = page.extract_words(extra_attrs=['size'])
    # Group words by line (y within 3px tolerance)
    lines = {}
    for w in words:
        y = round(w['top'] / 3) * 3
        lines.setdefault(y, []).append(w)
    for y in lines:
        lines[y].sort(key=lambda w: w['x0'])

    entries = {}
    for y in sorted(lines):
        row = lines[y]
        # Find code (starts with \d\d_\d\d\d\d)
        code_w = next((w for w in row if re.match(r'^\d{2}_\d{4}$', w['text'])), None)
        if not code_w:
            continue
        code = code_w['text']

        # English name words: x0 > X_CODE_MAX and x0 < X_EN_MAX
        en_words = [w['text'] for w in row if w['x0'] > X_CODE_MAX and w['x0'] < X_EN_MAX]
        # Bengali transliteration words: x0 >= X_EN_MAX and x0 < X_BN_MAX
        bn_words = [w['text'] for w in row if w['x0'] >= X_EN_MAX and w['x0'] < X_BN_MAX]
        # Number words: x0 >= X_BN_MAX
        num_words = [w['text'] for w in row if w['x0'] >= X_BN_MAX]

        en = ' '.join(en_words).strip().rstrip('*').strip()
        bn_trans = ' '.join(bn_words).strip()

        # Parse numbers: edible_coeff, (kcal) kJ, water, protein, fat, carb, fiber, ash
        nums = []
        for nw in num_words:
            m = re.findall(r'[\[\(]?[\d.]+[\]\)]?', nw)
            nums.extend([x.strip('[]()') for x in m])

        # Multi-word English name may wrap; we handle continuations in a second pass
        if code not in entries:
            entries[code] = {'en': en, 'bn_trans': bn_trans, 'nums': nums}
        else:
            # Continuation line
            if en and not entries[code]['en'].endswith(en):
                entries[code]['en'] += ' ' + en
            if bn_trans and not entries[code]['bn_trans']:
                entries[code]['bn_trans'] = bn_trans
            entries[code]['nums'].extend(nums)

    results = {}
    for code, d in entries.items():
        nums = d['nums']
        if len(nums) < 6:
            continue
        try:
            i = 0
            _edible = float(nums[i]); i += 1
            kcal    = float(nums[i]); i += 1
            _kj     = float(nums[i]); i += 1
            _water  = float(nums[i]); i += 1
            prot    = float(nums[i]); i += 1
            fat     = float(nums[i]); i += 1
            carb    = float(nums[i]); i += 1
            fiber   = float(nums[i]) if i < len(nums) else None; i += 1
        except (ValueError, IndexError):
            continue
        results[code] = {
            'en': d['en'], 'bn_trans': d['bn_trans'],
            'kcal': kcal, 'protein': prot, 'fat': fat,
            'carb': carb, 'fiber': fiber,
        }
    return results


def extract_mineral(page):
    words = page.extract_words()
    lines = {}
    for w in words:
        y = round(w['top'] / 3) * 3
        lines.setdefault(y, []).append(w)
    for y in lines:
        lines[y].sort(key=lambda w: w['x0'])

    results = {}
    for y in sorted(lines):
        row = lines[y]
        code_w = next((w for w in row if re.match(r'^\d{2}_\d{4}$', w['text'])), None)
        if not code_w:
            continue
        code = code_w['text']
        # Numbers come after English name (x > ~310)
        num_words = [w['text'] for w in row if w['x0'] > 310]
        nums = []
        for nw in num_words:
            m = re.findall(r'[\[\(]?-?[\d.]+[\]\)]?', nw)
            nums.extend([x.strip('[]()') for x in m])
        if len(nums) < 4:
            continue
        try:
            results[code] = {
                'ca': safe(nums[0]), 'fe': safe(nums[1]),
                'mg': safe(nums[2]), 'p':  safe(nums[3]),
                'pot': safe(nums[4]) if len(nums) > 4 else None,
                'zn':  safe(nums[6]) if len(nums) > 6 else None,
            }
        except IndexError:
            pass
    return results


def extract_vitamin(page):
    words = page.extract_words()
    lines = {}
    for w in words:
        y = round(w['top'] / 3) * 3
        lines.setdefault(y, []).append(w)
    for y in lines:
        lines[y].sort(key=lambda w: w['x0'])

    results = {}
    for y in sorted(lines):
        row = lines[y]
        code_w = next((w for w in row if re.match(r'^\d{2}_\d{4}$', w['text'])), None)
        if not code_w:
            continue
        code = code_w['text']
        num_words = [w['text'] for w in row if w['x0'] > 310]
        nums = []
        for nw in num_words:
            m = re.findall(r'[\[\(]?-?[\d.]+[\]\)]?', nw)
            nums.extend([x.strip('[]()') for x in m])
        if len(nums) < 3:
            continue
        try:
            results[code] = {
                'va': safe(nums[0]),
                'vd': safe(nums[3]) if len(nums) > 3 else None,
                'vc': safe(nums[10]) if len(nums) > 10 else None,
            }
        except IndexError:
            pass
    return results


def get_bn_name(en_name, bn_trans):
    """Get proper Bengali Unicode name from map, or construct from transliteration."""
    key = en_name.lower().strip().rstrip('*').strip()
    if key in BN_MAP:
        return BN_MAP[key]
    # Try partial match (strip trailing *)
    for map_key, bn in BN_MAP.items():
        if key.startswith(map_key) or map_key.startswith(key[:20]):
            return bn
    # Fallback: return transliteration as-is (Latin)
    return bn_trans if bn_trans else en_name


def main():
    # Step 1: Load existing master and remove previous bd_fct entries
    print("Loading existing dataset...")
    with open(MASTER, 'r', encoding='utf-8') as f:
        master = json.load(f)
    orig_count = len(master)
    master = [item for item in master if item.get('src') != 'bd_fct']
    print(f"Removed {orig_count - len(master)} previous bd_fct entries. Remaining: {len(master)}")

    # Step 2: Extract from PDF
    print("\nExtracting from PDF...")
    prox_data = {}
    min_data  = {}
    vit_data  = {}

    with pdfplumber.open(PDF_PATH) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            ptype = classify_page(text)
            if not ptype:
                continue
            if ptype == 'proximate':
                prox_data.update(extract_proximate(page))
            elif ptype == 'mineral':
                min_data.update(extract_mineral(page))
            elif ptype == 'vitamin':
                vit_data.update(extract_vitamin(page))

    print(f"Proximate: {len(prox_data)}, Mineral: {len(min_data)}, Vitamin: {len(vit_data)}")

    # Step 3: Build food items
    existing_en = {item['en'].lower().strip() for item in master}
    max_id = max(item['id'] for item in master)
    added = 0
    skipped = 0

    for code in sorted(prox_data.keys()):
        p = prox_data[code]
        en = p['en'].strip()
        if not en or not p.get('kcal'):
            skipped += 1
            continue

        # Skip duplicate (case-insensitive)
        if en.lower().strip() in existing_en:
            skipped += 1
            continue

        bn = get_bn_name(en, p.get('bn_trans', ''))
        mn = min_data.get(code, {})
        vt = vit_data.get(code, {})
        cat_prefix = code[:2]
        cat = CAT_MAP.get(cat_prefix, 'dish')

        kw = sorted(set(w.lower() for w in re.findall(r'[A-Za-z]+', en) if len(w) > 2))

        max_id += 1
        item = {
            'en':  en,
            'bn':  bn,
            's':   '100g',
            'k':   round(p['kcal'],   1),
            'p':   round(p['protein'],1),
            'c':   round(p['carb'],   1),
            'f':   round(p['fat'],    1),
            'fi':  round(p['fiber'] or 0, 1),
            'ca':  round(mn.get('ca')  or 0, 1),
            'fe':  round(mn.get('fe')  or 0, 2),
            'zn':  round(mn.get('zn')  or 0, 2),
            'cat': cat,
            'kw':  kw,
            'src': 'bd_fct',
            'va':  round(vt.get('va')  or 0, 1),
            'vc':  round(vt.get('vc')  or 0, 1),
            'vd':  round(vt.get('vd')  or 0, 2),
            'mg':  round(mn.get('mg')  or 0, 1),
            'pot': round(mn.get('pot') or 0, 1),
            'id':  max_id,
        }
        master.append(item)
        existing_en.add(en.lower().strip())
        added += 1
        print(f"  +[{max_id}] {en}  /  {bn}")

    print(f"\nAdded: {added}, Skipped: {skipped}")

    # Step 4: Write updated files
    new_index_en = sorted(
        [{'id': it['id'], 'en': it['en'], 'bn': it['bn'], 'k': it['k']} for it in master],
        key=lambda x: x['en'].lower()
    )
    new_index_bn = sorted(
        [{'id': it['id'], 'en': it['en'], 'bn': it['bn'], 'k': it['k']} for it in master],
        key=lambda x: x['bn']
    )
    with open(MASTER, 'w', encoding='utf-8') as f:
        json.dump(master, f, ensure_ascii=False, separators=(',', ':'))
    with open(INDEX_EN, 'w', encoding='utf-8') as f:
        json.dump(new_index_en, f, ensure_ascii=False, separators=(',', ':'))
    with open(INDEX_BN, 'w', encoding='utf-8') as f:
        json.dump(new_index_bn, f, ensure_ascii=False, separators=(',', ':'))

    print(f"\nDataset updated. Total items: {len(master)}")


if __name__ == '__main__':
    main()
