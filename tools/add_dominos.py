import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'assets/data/food_master_v7_2.json'
data = json.load(open(path, encoding='utf-8'))

existing_ids = {d['id'] for d in data}
conflicts = [i for i in range(97001, 97088) if i in existing_ids]
if conflicts:
    print('ID CONFLICTS:', conflicts)
    sys.exit(1)

SIZE_EN = {'R': 'Regular', 'M': 'Medium', 'L': 'Large'}
SIZE_BN = {'R': 'রেগুলার', 'M': 'মিডিয়াম', 'L': 'লার্জ'}

def pizza(pid, en, bn, sz, gm, kcal, p, f, c, veg=True):
    kw = ['dominos', 'dominoz', 'pizza', 'fast food', SIZE_EN[sz].lower()] + en.lower().split()
    if not veg:
        kw.append('non veg')
    kw = list(dict.fromkeys(kw))
    return {
        'id': pid,
        'en': f"{en} ({SIZE_EN[sz]})",
        'bn': f"{bn} ({SIZE_BN[sz]})",
        'cat': 'pizza',
        's': f"{gm}g",
        'k': kcal, 'p': p, 'c': c, 'f': f,
        'fi': 1.5, 'ca': 80.0, 'fe': 0.8, 'zn': 0.5,
        'kw': kw, 'src': 'dominos_india'
    }

def side(pid, en, bn, gm, kcal, p, f, c, fi=1.5, cat='snack', extra=None):
    kw = ['dominos', 'dominoz', 'fast food'] + en.lower().split() + (extra or [])
    kw = list(dict.fromkeys(kw))
    return {
        'id': pid,
        'en': en, 'bn': bn, 'cat': cat,
        's': f"{gm}g",
        'k': kcal, 'p': p, 'c': c, 'f': f,
        'fi': fi, 'ca': 40.0, 'fe': 0.6, 'zn': 0.3,
        'kw': kw, 'src': 'dominos_india'
    }

new_foods = [
    # ── VEG PIZZAS (HT Crust) ─────────────────────────────────────────────────
    pizza(97001,'Dominos Margherita','ডমিনোজ মার্গেরিটা','R',52,138.5,6.8,3.2,20.5),
    pizza(97002,'Dominos Margherita','ডমিনোজ মার্গেরিটা','M',69,184.3,9.1,4.3,27.3),
    pizza(97003,'Dominos Margherita','ডমিনোজ মার্গেরিটা','L',96,256.4,12.7,6.0,38.0),

    pizza(97004,'Dominos Double Cheese Margherita','ডমিনোজ ডবল চিজ মার্গেরিটা','R',56,145.5,6.5,3.2,22.6),
    pizza(97005,'Dominos Double Cheese Margherita','ডমিনোজ ডবল চিজ মার্গেরিটা','M',64,166.7,7.5,3.7,25.9),
    pizza(97006,'Dominos Double Cheese Margherita','ডমিনোজ ডবল চিজ মার্গেরিটা','L',108,279.3,12.5,6.2,43.4),

    pizza(97007,'Dominos Country Special','ডমিনোজ কান্ট্রি স্পেশাল','R',70,153.2,6.8,3.3,24.0),
    pizza(97008,'Dominos Country Special','ডমিনোজ কান্ট্রি স্পেশাল','M',80,175.5,7.8,3.8,27.5),
    pizza(97009,'Dominos Country Special','ডমিনোজ কান্ট্রি স্পেশাল','L',123,268.1,11.9,5.8,42.1),

    pizza(97010,'Dominos Farm House','ডমিনোজ ফার্ম হাউস','R',70,156.5,6.7,3.4,24.9),
    pizza(97011,'Dominos Farm House','ডমিনোজ ফার্ম হাউস','M',83,184.6,7.9,4.0,29.3),
    pizza(97012,'Dominos Farm House','ডমিনোজ ফার্ম হাউস','L',114,253.5,10.8,5.5,40.3),

    pizza(97013,'Dominos Mexican Green Wave','ডমিনোজ মেক্সিকান গ্রিন ওয়েভ','R',65,144.5,6.1,3.0,23.1),
    pizza(97014,'Dominos Mexican Green Wave','ডমিনোজ মেক্সিকান গ্রিন ওয়েভ','M',82,181.9,7.7,3.8,29.1),
    pizza(97015,'Dominos Mexican Green Wave','ডমিনোজ মেক্সিকান গ্রিন ওয়েভ','L',114,253.4,10.8,5.3,40.6),

    pizza(97016,'Dominos Spicy Triple Tango','ডমিনোজ স্পাইসি ট্রিপল ট্যাঙ্গো','R',69,160.1,7.4,3.3,25.2),
    pizza(97017,'Dominos Spicy Triple Tango','ডমিনোজ স্পাইসি ট্রিপল ট্যাঙ্গো','M',75,175.1,8.1,3.6,27.6),
    pizza(97018,'Dominos Spicy Triple Tango','ডমিনোজ স্পাইসি ট্রিপল ট্যাঙ্গো','L',109,254.8,11.8,5.3,40.1),

    pizza(97019,'Dominos Peppy Paneer','ডমিনোজ পেপি পনির','R',68,168.8,7.2,4.5,24.8),
    pizza(97020,'Dominos Peppy Paneer','ডমিনোজ পেপি পনির','M',79,198.4,8.5,5.3,29.1),
    pizza(97021,'Dominos Peppy Paneer','ডমিনোজ পেপি পনির','L',109,271.9,11.6,7.3,40.0),

    pizza(97022,'Dominos 5 Pepper','ডমিনোজ ৫ পেপার','R',90,190.0,8.5,3.3,31.6),
    pizza(97023,'Dominos 5 Pepper','ডমিনোজ ৫ পেপার','M',79,167.5,7.5,2.9,27.9),
    pizza(97024,'Dominos 5 Pepper','ডমিনোজ ৫ পেপার','L',107,225.4,10.1,3.9,37.5),

    pizza(97025,'Dominos Veggie Paradise','ডমিনোজ ভেজি প্যারাডাইস','R',72,156.7,7.2,3.3,24.5),
    pizza(97026,'Dominos Veggie Paradise','ডমিনোজ ভেজি প্যারাডাইস','M',77,167.7,7.7,3.5,26.2),
    pizza(97027,'Dominos Veggie Paradise','ডমিনোজ ভেজি প্যারাডাইস','L',97,210.9,9.7,4.5,33.0),

    pizza(97028,'Dominos Veggie Deluxe','ডমিনোজ ভেজি ডিলাক্স','R',76,169.7,7.5,4.0,26.0),
    pizza(97029,'Dominos Veggie Deluxe','ডমিনোজ ভেজি ডিলাক্স','M',79,175.6,7.8,4.1,26.9),
    pizza(97030,'Dominos Veggie Deluxe','ডমিনোজ ভেজি ডিলাক্স','L',99,220.5,9.8,5.2,33.7),

    pizza(97031,'Dominos Veg Extravaganza','ডমিনোজ ভেজ এক্সট্রাভাগানজা','R',91,173.3,8.8,2.4,29.2),
    pizza(97032,'Dominos Veg Extravaganza','ডমিনোজ ভেজ এক্সট্রাভাগানজা','M',97,184.2,9.3,2.5,31.1),
    pizza(97033,'Dominos Veg Extravaganza','ডমিনোজ ভেজ এক্সট্রাভাগানজা','L',128,242.6,12.3,3.3,40.9),

    pizza(97034,'Dominos Cloud 9','ডমিনোজ ক্লাউড ৯','R',78,170.1,7.7,5.2,23.3),
    pizza(97035,'Dominos Cloud 9','ডমিনোজ ক্লাউড ৯','M',106,231.2,10.4,7.0,31.6),
    pizza(97036,'Dominos Cloud 9','ডমিনোজ ক্লাউড ৯','L',126,274.2,12.4,8.3,37.5),

    pizza(97037,'Dominos Chefs Veg Wonder','ডমিনোজ শেফস ভেজ ওয়ান্ডার','R',74,167.6,8.1,3.4,26.0),
    pizza(97038,'Dominos Chefs Veg Wonder','ডমিনোজ শেফস ভেজ ওয়ান্ডার','M',79,178.9,8.7,3.7,27.8),
    pizza(97039,'Dominos Chefs Veg Wonder','ডমিনোজ শেফস ভেজ ওয়ান্ডার','L',112,253.4,12.3,5.2,39.3),

    # ── NON-VEG PIZZAS ────────────────────────────────────────────────────────
    pizza(97040,'Dominos Cheese BBQ Chicken','ডমিনোজ চিজ বিবিকিউ চিকেন','R',61,141.8,7.6,2.9,21.4,False),
    pizza(97041,'Dominos Cheese BBQ Chicken','ডমিনোজ চিজ বিবিকিউ চিকেন','M',77,180.5,9.7,3.6,27.3,False),
    pizza(97042,'Dominos Cheese BBQ Chicken','ডমিনোজ চিজ বিবিকিউ চিকেন','L',96,224.6,12.0,4.5,34.0,False),

    pizza(97043,'Dominos Chicken Salami Special','ডমিনোজ চিকেন সালামি স্পেশাল','R',60,176.7,7.1,8.3,18.3,False),
    pizza(97044,'Dominos Chicken Salami Special','ডমিনোজ চিকেন সালামি স্পেশাল','M',71,209.2,8.4,9.9,21.7,False),
    pizza(97045,'Dominos Chicken Salami Special','ডমিনোজ চিকেন সালামি স্পেশাল','L',97,283.7,11.4,13.4,29.4,False),

    pizza(97046,'Dominos BBQ Chicken','ডমিনোজ বিবিকিউ চিকেন','R',65,152.1,7.2,3.3,23.3,False),
    pizza(97047,'Dominos BBQ Chicken','ডমিনোজ বিবিকিউ চিকেন','M',79,185.5,8.7,4.1,28.5,False),
    pizza(97048,'Dominos BBQ Chicken','ডমিনোজ বিবিকিউ চিকেন','L',109,255.4,12.0,5.6,39.2,False),

    pizza(97049,'Dominos Chicken Fiesta','ডমিনোজ চিকেন ফিয়েস্তা','R',65,150.1,6.9,4.3,21.0,False),
    pizza(97050,'Dominos Chicken Fiesta','ডমিনোজ চিকেন ফিয়েস্তা','M',94,217.4,10.0,6.2,30.4,False),
    pizza(97051,'Dominos Chicken Fiesta','ডমিনোজ চিকেন ফিয়েস্তা','L',99,227.7,10.5,6.5,31.9,False),

    pizza(97052,'Dominos Chicken Lovers','ডমিনোজ চিকেন লাভার্স','R',66,145.0,7.7,2.4,23.1,False),
    pizza(97053,'Dominos Chicken Lovers','ডমিনোজ চিকেন লাভার্স','M',78,172.7,9.1,2.9,27.5,False),
    pizza(97054,'Dominos Chicken Lovers','ডমিনোজ চিকেন লাভার্স','L',108,238.0,12.6,4.0,37.9,False),

    pizza(97055,'Dominos Chicken Mexicana','ডমিনোজ চিকেন মেক্সিকানা','R',69,156.6,8.0,3.8,22.7,False),
    pizza(97056,'Dominos Chicken Mexicana','ডমিনোজ চিকেন মেক্সিকানা','M',87,197.5,10.1,4.8,28.6,False),
    pizza(97057,'Dominos Chicken Mexicana','ডমিনোজ চিকেন মেক্সিকানা','L',107,241.4,12.3,5.8,35.0,False),

    pizza(97058,'Dominos Chicken Golden Delight','ডমিনোজ চিকেন গোল্ডেন ডিলাইট','R',73,170.0,7.5,1.4,31.8,False),
    pizza(97059,'Dominos Chicken Golden Delight','ডমিনোজ চিকেন গোল্ডেন ডিলাইট','M',79,185.2,8.2,1.5,34.7,False),
    pizza(97060,'Dominos Chicken Golden Delight','ডমিনোজ চিকেন গোল্ডেন ডিলাইট','L',96,225.1,9.9,1.9,42.1,False),

    pizza(97061,'Dominos Chefs Chicken Choice','ডমিনোজ শেফস চিকেন চয়েস','R',72,163.9,8.6,3.7,23.9,False),
    pizza(97062,'Dominos Chefs Chicken Choice','ডমিনোজ শেফস চিকেন চয়েস','M',85,194.3,10.2,4.4,28.3,False),
    pizza(97063,'Dominos Chefs Chicken Choice','ডমিনোজ শেফস চিকেন চয়েস','L',112,254.7,13.4,5.8,37.1,False),

    pizza(97064,'Dominos Chicken Dominator','ডমিনোজ চিকেন ডমিনেটর','R',70,172.5,9.1,5.5,21.7,False),
    pizza(97065,'Dominos Chicken Dominator','ডমিনোজ চিকেন ডমিনেটর','M',92,226.7,12.0,7.2,28.5,False),
    pizza(97066,'Dominos Chicken Dominator','ডমিনোজ চিকেন ডমিনেটর','L',155,399.0,18.3,14.9,48.0,False),

    pizza(97067,'Dominos Seventh Heaven','ডমিনোজ সেভেন্থ হেভেন','R',76,158.4,9.4,4.7,19.6,False),
    pizza(97068,'Dominos Seventh Heaven','ডমিনোজ সেভেন্থ হেভেন','M',108,224.4,13.3,6.7,27.8,False),
    pizza(97069,'Dominos Seventh Heaven','ডমিনোজ সেভেন্থ হেভেন','L',115,237.9,14.1,7.1,29.4,False),

    pizza(97070,'Dominos Non-Veg Supreme','ডমিনোজ নন-ভেজ সুপ্রিম','R',80,174.5,7.3,3.8,27.8,False),
    pizza(97071,'Dominos Non-Veg Supreme','ডমিনোজ নন-ভেজ সুপ্রিম','M',91,199.2,8.3,4.3,31.7,False),
    pizza(97072,'Dominos Non-Veg Supreme','ডমিনোজ নন-ভেজ সুপ্রিম','L',132,287.9,12.0,6.3,45.9,False),

    pizza(97073,'Dominos Cheese Pepperoni','ডমিনোজ চিজ পেপারোনি','R',68,169.0,9.2,6.7,23.1,False),
    pizza(97074,'Dominos Cheese Pepperoni','ডমিনোজ চিজ পেপারোনি','M',75,210.0,10.2,7.4,25.6,False),
    pizza(97075,'Dominos Cheese Pepperoni','ডমিনোজ চিজ পেপারোনি','L',99,272.3,13.2,9.6,33.2,False),

    # ── SIDES ─────────────────────────────────────────────────────────────────
    side(97076,'Dominos Garlic Breadsticks','ডমিনোজ গার্লিক ব্রেডস্টিক',122,340.3,11.9,6.9,57.6,2.0,'snack',['garlic','breadstick','bread']),
    side(97077,'Dominos Stuffed Garlic Breadsticks','ডমিনোজ স্টাফড গার্লিক ব্রেডস্টিক',190,540.2,20.2,14.4,82.4,2.5,'snack',['stuffed','garlic','breadstick']),
    side(97078,'Dominos Pasta Veg White','ডমিনোজ পাস্তা ভেজ হোয়াইট',198,593.2,19.6,21.4,80.4,3.0,'noodle',['pasta','veg','white sauce']),
    side(97079,'Dominos Taco Mexicana Veg','ডমিনোজ ট্যাকো মেক্সিকানা ভেজ',91,327.2,6.8,15.4,40.3,2.0,'snack',['taco','mexicana','veg']),
    side(97080,'Dominos Calzone Pockets Veg','ডমিনোজ ক্যালজোন পকেটস ভেজ',238,593.3,20.6,16.3,91.1,4.0,'snack',['calzone','pocket','veg']),
    side(97081,'Dominos Zingy Parcel Veg','ডমিনোজ জিঞ্জি পার্সেল ভেজ',180,620.4,16.9,30.5,69.5,3.0,'snack',['zingy','parcel','veg']),
    side(97082,'Dominos Lava Cake','ডমিনোজ লাভা কেক',85,323.2,5.1,12.1,46.4,1.0,'sweet',['lava','cake','chocolate','dessert']),
    side(97083,'Dominos Chicken Wings','ডমিনোজ চিকেন উইংস',174,352.9,35.3,12.6,24.5,0.5,'meat',['chicken','wings']),
    side(97084,'Dominos Crispy Chicken Strips','ডমিনোজ ক্রিসপি চিকেন স্ট্রিপস',156,461.2,26.7,13.9,57.3,1.5,'snack',['crispy','chicken','strips']),
    side(97085,'Dominos Zingy Parcel Chicken','ডমিনোজ জিঞ্জি পার্সেল চিকেন',210,667.5,19.2,31.3,77.3,3.0,'snack',['zingy','parcel','chicken']),
    side(97086,'Dominos Taco Mexicana Chicken','ডমিনোজ ট্যাকো মেক্সিকানা চিকেন',97,322.6,9.3,16.5,34.2,1.5,'snack',['taco','mexicana','chicken']),
    side(97087,'Dominos Calzone Pockets Chicken','ডমিনোজ ক্যালজোন পকেটস চিকেন',240,582.9,18.6,11.6,101.0,4.0,'snack',['calzone','pocket','chicken']),
]

data.extend(new_foods)
print(f'Added: {len(new_foods)} items  |  Total: {len(data)}')

with open(path, 'w', encoding='utf-8') as fp:
    json.dump(data, fp, ensure_ascii=False, separators=(',', ':'))
print('Done.')
