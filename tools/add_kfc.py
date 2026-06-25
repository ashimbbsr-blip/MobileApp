import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'assets/data/food_master_v7_2.json'
data = json.load(open(path, encoding='utf-8'))

def kfc(id_, en, bn, w, k, c, p, f, cat, fi=0.0):
    kws = list({t.lower() for t in en.split()} | {'kfc','kfc india'})
    return {'id':id_,'en':en,'bn':bn,'cat':cat,'s':f'{w}g',
            'k':k,'p':p,'c':c,'f':f,'fi':fi,
            'ca':0.0,'fe':0.0,'zn':0.0,'kw':kws,'src':'kfc_india'}

# Macro validation (carb*4 + protein*4 + fat*9 should be within 10% of kcal):
# All items below have been verified against PDF macros. Items with >10% mismatch skipped.
# Skipped: Tandoori Zinger Burger (902 kcal vs 618 from macros — PDF typo)
#           Korean/Thai/Tandoori Chicken Roll (kcal mismatch — PDF column shift)
#           Nashville Sauce Bottle (macros inconsistent)

new_foods = [
    # ===== CHICKEN PIECES — per 1 piece =====
    kfc(99001,'KFC Hot & Crispy Chicken','কেএফসি হট অ্যান্ড ক্রিসপি চিকেন',110,320,16,19,20,'meat'),
    kfc(99002,'KFC Hot & Crispy Leg Piece','কেএফসি হট অ্যান্ড ক্রিসপি লেগ পিস',100,288,17,18,17,'meat'),
    kfc(99003,'KFC Piripiri Hot & Crispy Leg','কেএফসি পিরিপিরি লেগ পিস',100,299,19,18,17,'meat'),
    kfc(99004,'KFC Hot Wings','কেএফসি হট উইংস',35,125,8,6,8,'meat'),
    kfc(99005,'KFC Boneless Strips','কেএফসি বোনলেস স্ট্রিপস',45,117,7,9,6,'meat'),
    kfc(99006,'KFC Piripiri Boneless Strips','কেএফসি পিরিপিরি বোনলেস স্ট্রিপস',45,135,9,8,8,'meat'),
    kfc(99007,'KFC Zinger Fillet','কেএফসি জিঞ্জার ফিলেট',135,359,34,18,18,'meat'),
    kfc(99008,'KFC Smoky Chicken','কেএফসি স্মোকি চিকেন',90,171,8,21,6,'meat'),
    kfc(99009,'KFC Grilled Leg Piece','কেএফসি গ্রিলড লেগ পিস',170,338,15,34,17,'meat'),
    # ===== POPCORN CHICKEN =====
    kfc(99010,'KFC Popcorn Chicken Regular','কেএফসি পপকর্ন চিকেন রেগুলার',90,306,21,17,18,'meat'),
    kfc(99011,'KFC Popcorn Chicken Medium','কেএফসি পপকর্ন চিকেন মিডিয়াম',140,476,32,27,28,'meat'),
    kfc(99012,'KFC Popcorn Chicken Large','কেএফসি পপকর্ন চিকেন লার্জ',190,646,44,36,38,'meat'),
    # ===== BURGERS =====
    kfc(99013,'KFC Classic Zinger Burger','কেএফসি ক্লাসিক জিঞ্জার বার্গার',225,612,63,27,29,'snack'),
    kfc(99014,'KFC Spicy Zinger Burger','কেএফসি স্পাইসি জিঞ্জার বার্গার',215,439,47,28,16,'snack'),
    kfc(99015,'KFC Pro Zinger Burger','কেএফসি প্রো জিঞ্জার বার্গার',225,529,41,29,29,'snack'),
    kfc(99016,'KFC Veg Zinger Burger','কেএফসি ভেজ জিঞ্জার বার্গার',230,619,83,14,25,'snack'),
    kfc(99017,'KFC Paneer Zinger Burger','কেএফসি পনির জিঞ্জার বার্গার',215,643,56,24,37,'snack'),
    kfc(99018,'KFC Egg Burger','কেএফসি এগ বার্গার',130,281,31,13,12,'snack'),
    kfc(99019,'KFC Loaded Egg Burger','কেএফসি লোডেড এগ বার্গার',230,497,46,32,23,'snack'),
    kfc(99020,'KFC Chatpata Channa Burger','কেএফসি চাটপাটা ছানা বার্গার',130,366,51,9,14,'snack'),
    kfc(99021,'KFC Dunked Burger','কেএফসি ডাংকড বার্গার',210,559,53,29,27,'snack'),
    # ===== KRISPERS =====
    kfc(99022,'KFC Classic Chicken Krisper','কেএফসি ক্লাসিক চিকেন ক্রিসপার',150,405,47,17,17,'snack'),
    kfc(99023,'KFC Spicy Chicken Krisper','কেএফসি স্পাইসি চিকেন ক্রিসপার',145,342,49,17,8,'snack'),
    kfc(99024,'KFC Classic Veg Krisper','কেএফসি ক্লাসিক ভেজ ক্রিসপার',145,496,54,9,28,'snack'),
    kfc(99025,'KFC Spicy Veg Krisper','কেএফসি স্পাইসি ভেজ ক্রিসপার',145,436,58,9,19,'snack'),
    # ===== LONGER / ROLLS =====
    kfc(99026,'KFC Chicken Longer','কেএফসি চিকেন লঙ্গার',120,356,37,12,18,'snack'),
    kfc(99027,'KFC Chicken Roll','কেএফসি চিকেন রোল',150,461,57,14,20,'snack'),
    kfc(99028,'KFC Double Chicken Roll','কেএফসি ডাবল চিকেন রোল',190,526,51,23,27,'snack'),
    kfc(99029,'KFC Veg Roll','কেএফসি ভেজ রোল',145,447,55,8,22,'snack'),
    kfc(99030,'KFC Veg Patty','কেএফসি ভেজ পাটি',55,133,17,4,6,'snack'),
    kfc(99031,'KFC Double Veg Patty','কেএফসি ডাবল ভেজ পাটি',110,266,34,7,11,'snack'),
    # ===== RICE BOWLS =====
    kfc(99032,'KFC Plain Rice Bowl','কেএফসি প্লেইন রাইস বোল',250,418,65,10,13,'rice'),
    kfc(99033,'KFC Veg Rice Bowl','কেএফসি ভেজ রাইস বোল',305,418,76,9,9,'rice'),
    kfc(99034,'KFC Classic Chicken Rice Bowl','কেএফসি ক্লাসিক চিকেন রাইস বোল',360,547,61,36,18,'rice'),
    kfc(99035,'KFC Popcorn Chicken Rice Bowl','কেএফসি পপকর্ন চিকেন রাইস বোল',340,615,88,24,19,'rice'),
    kfc(99036,'KFC Smoky Chicken Rice Bowl','কেএফসি স্মোকি চিকেন রাইস বোল',340,418,65,24,8,'rice'),
    # ===== LIMITED TIME OFFER / SPECIAL =====
    kfc(99037,'KFC Double Down','কেএফসি ডাবল ডাউন',225,590,34,38,34,'snack'),
    kfc(99038,'KFC Chizza','কেএফসি চিজা',225,473,29,36,23,'snack'),
    kfc(99039,'KFC Shawarma','কেএফসি শাওয়ার্মা',165,452,51,17,25,'snack'),
    kfc(99040,'KFC DDX','কেএফসি ডিডিএক্স',250,720,63,33,40,'snack'),
    kfc(99041,'KFC Dunked Wings','কেএফসি ডাংকড উইংস',135,402,28,19,24,'snack'),
    kfc(99042,'KFC Dunked Boneless Wings','কেএফসি ডাংকড বোনলেস উইংস',135,339,27,18,18,'snack'),
    kfc(99043,'KFC Dunked Strips','কেএফসি ডাংকড স্ট্রিপস',135,325,24,22,16,'snack'),
    kfc(99044,'KFC Dunked Drums','কেএফসি ডাংকড ড্রামস',200,550,40,34,28,'snack'),
    # ===== FRIES =====
    kfc(99045,'KFC French Fries Regular','কেএফসি ফ্রেঞ্চ ফ্রাইস রেগুলার',75,224,28,5,11,'snack'),
    kfc(99046,'KFC French Fries Medium','কেএফসি ফ্রেঞ্চ ফ্রাইস মিডিয়াম',100,299,37,7,14,'snack'),
    kfc(99047,'KFC French Fries Large','কেএফসি ফ্রেঞ্চ ফ্রাইস লার্জ',135,404,50,9,19,'snack'),
    # ===== DIPS & SAUCES (20g per dip) =====
    kfc(99048,'KFC Dynamite Spicy Mayo','কেএফসি ডায়নামাইট স্পাইসি মেয়ো',20,77,3,0,7,'snack'),
    kfc(99049,'KFC Creamy Veg Mayo','কেএফসি ক্রিমি ভেজ মেয়ো',20,74,2,0,7,'snack'),
    kfc(99050,'KFC Tandoori Masala Mayo','কেএফসি তান্দুরি মাসালা মেয়ো',20,74,3,0,7,'snack'),
    kfc(99051,'KFC Zesty Thousand Island Dip','কেএফসি জেস্টি থাউজেন্ড আইল্যান্ড ডিপ',20,72,4,0,6,'snack'),
    kfc(99052,'KFC Nashville Dip','কেএফসি ন্যাশভিল ডিপ',20,30,7,0,0,'snack'),
    # ===== DESSERTS =====
    kfc(99053,'KFC Choco Lava Cake','কেএফসি চকো লাভা কেক',60,343,34,6,21,'sweet'),
    kfc(99054,'KFC Choco Mud Pie','কেএফসি চকো মাড পাই',93,241,37,3,9,'sweet'),
    kfc(99055,'KFC Mousse Cake Coffee','কেএফসি কফি মুস কেক',70,135,17,2,7,'sweet'),
    kfc(99056,'KFC Mini Dessert Bucket','কেএফসি মিনি ডেজার্ট বাকেট',85,250,34,4,11,'sweet'),
]

# Conflict check
existing_ids = {d['id'] for d in data}
conflicts = [nf for nf in new_foods if nf['id'] in existing_ids]
if conflicts:
    print(f'CONFLICTS: {[c["id"] for c in conflicts]}')
    sys.exit(1)

print(f'Adding {len(new_foods)} KFC items')
data.extend(new_foods)
print(f'New total: {len(data)} items')

with open(path, 'w', encoding='utf-8') as fp:
    json.dump(data, fp, ensure_ascii=False, separators=(',', ':'))
print('Done.')
