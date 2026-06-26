"""
add_restaurant_juices.py — Add restaurant foods and fresh Indian juices

Groups:
  Saravana Bhavan items: 55101-55112 (free)
  Oh! Calcutta / Bhojohori Manna / Kamat items: 57001-57012
    (reassigned from 55001-55012 — those IDs taken by exotic fruits)
  Fresh Indian juices: 56001-56020 (free)
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

NEW_ITEMS = [
  # ── SARAVANA BHAVAN (55101-55112) ────────────────────────────────────────
  {'id':55101,'en':'Saravana Bhavan Idli','bn':'ইডলি (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':135,'p':4.2,'c':27.0,'f':1.5,'fi':1.8,'ca':22,'fe':1.0,'src':'brand'},
  {'id':55102,'en':'Saravana Bhavan Ghee Idli','bn':'ঘি ইডলি (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':210,'p':4.2,'c':27.0,'f':9.5,'fi':1.8,'ca':25,'fe':1.0,'src':'brand'},
  {'id':55103,'en':'Saravana Bhavan Vada','bn':'বড়া (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':290,'p':8.5,'c':24.0,'f':18.0,'fi':2.5,'ca':40,'fe':2.2,'src':'brand'},
  {'id':55104,'en':'Saravana Bhavan Masala Dosa','bn':'মসালা ডোসা (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':165,'p':4.5,'c':28.0,'f':5.5,'fi':2.2,'ca':18,'fe':1.1,'src':'brand'},
  {'id':55105,'en':'Saravana Bhavan Plain Dosa','bn':'প্লেইন ডোসা (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':140,'p':3.8,'c':26.0,'f':4.5,'fi':2.0,'ca':15,'fe':1.0,'src':'brand'},
  {'id':55106,'en':'Saravana Bhavan Ghee Roast Dosa','bn':'ঘি রোস্ট ডোসা (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':210,'p':4.2,'c':26.0,'f':10.5,'fi':2.0,'ca':15,'fe':1.0,'src':'brand'},
  {'id':55107,'en':'Saravana Bhavan Onion Dosa','bn':'অনিয়ন ডোসা (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':150,'p':4.0,'c':27.0,'f':5.0,'fi':2.3,'ca':18,'fe':1.0,'src':'brand'},
  {'id':55108,'en':'Saravana Bhavan Rava Dosa','bn':'রাভা ডোসা (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':180,'p':3.5,'c':28.0,'f':7.0,'fi':1.8,'ca':14,'fe':0.9,'src':'brand'},
  {'id':55109,'en':'Saravana Bhavan Sambar','bn':'সাম্বার (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':85,'p':3.2,'c':12.0,'f':2.8,'fi':3.5,'ca':45,'fe':1.6,'src':'brand'},
  {'id':55110,'en':'Saravana Bhavan Coconut Chutney','bn':'নারকেল চাটনি (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':230,'p':2.5,'c':6.0,'f':22.0,'fi':4.0,'ca':20,'fe':1.1,'src':'brand'},
  {'id':55111,'en':'Saravana Bhavan Upma','bn':'উপমা (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':160,'p':4.0,'c':28.0,'f':4.5,'fi':2.0,'ca':12,'fe':0.8,'src':'brand'},
  {'id':55112,'en':'Saravana Bhavan Pongal','bn':'পোঙ্গাল (সারাভানা ভবন)','cat':'restaurant_food','s':'100g','k':180,'p':5.0,'c':28.0,'f':6.0,'fi':2.2,'ca':18,'fe':1.1,'src':'brand'},
  # ── OH! CALCUTTA / BHOJOHORI MANNA / KAMAT (57001-57012) ─────────────────
  # (reassigned from 55001-55012 — those IDs are taken by exotic fruits)
  {'id':57001,'en':'Oh! Calcutta Chicken Biryani','bn':'ও কলকাতা চিকেন বিরিয়ানি','cat':'restaurant_food','s':'100g','k':155,'p':6.8,'c':18.5,'f':6.2,'fi':0.6,'ca':18,'fe':0.7,'src':'brand'},
  {'id':57002,'en':'Oh! Calcutta Mutton Biryani','bn':'ও কলকাতা মাটন বিরিয়ানি','cat':'restaurant_food','s':'100g','k':165,'p':7.2,'c':17.8,'f':7.0,'fi':0.6,'ca':18,'fe':0.8,'src':'brand'},
  {'id':57003,'en':'Hilsa Bhaja (Restaurant Style)','bn':'ইলিশ ভাজা (রেস্তোরাঁ স্টাইল)','cat':'restaurant_food','s':'100g','k':290,'p':18.0,'c':2.0,'f':23.0,'fi':0.0,'ca':35,'fe':1.5,'src':'brand'},
  {'id':57004,'en':'Hilsa Paturi','bn':'ইলিশ পাতুরি','cat':'restaurant_food','s':'100g','k':260,'p':17.5,'c':3.0,'f':20.0,'fi':0.2,'ca':40,'fe':1.4,'src':'brand'},
  {'id':57005,'en':'Bhetki Paturi','bn':'ভেটকি পাতুরি','cat':'restaurant_food','s':'100g','k':240,'p':18.5,'c':3.5,'f':18.0,'fi':0.3,'ca':45,'fe':1.2,'src':'brand'},
  {'id':57006,'en':'Chingri Malai Curry','bn':'চিংড়ি মালাইকারি','cat':'restaurant_food','s':'100g','k':215,'p':14.0,'c':6.0,'f':16.0,'fi':0.5,'ca':60,'fe':1.1,'src':'brand'},
  {'id':57007,'en':'Bhojohori Manna Aloo Bhaja','bn':'আলু ভাজা (ভোজোহরি মান্না)','cat':'restaurant_food','s':'100g','k':310,'p':2.5,'c':28.0,'f':20.0,'fi':3.0,'ca':15,'fe':0.8,'src':'brand'},
  {'id':57008,'en':'Shukto (Bengali Mixed Veg)','bn':'শুক্তো','cat':'restaurant_food','s':'100g','k':95,'p':3.2,'c':10.5,'f':4.0,'fi':3.5,'ca':55,'fe':1.0,'src':'brand'},
  {'id':57009,'en':'Kamat Masala Dosa','bn':'মসালা ডোসা (কামত)','cat':'restaurant_food','s':'100g','k':210,'p':4.5,'c':28.0,'f':8.0,'fi':2.2,'ca':25,'fe':1.2,'src':'brand'},
  {'id':57010,'en':'Kamat Idli','bn':'ইডলি (কামত)','cat':'restaurant_food','s':'100g','k':130,'p':4.0,'c':24.0,'f':2.0,'fi':1.5,'ca':20,'fe':0.9,'src':'brand'},
  {'id':57011,'en':'Bhojohori Manna Mochar Ghonto','bn':'মোচার ঘন্ট (ভোজোহরি মান্না)','cat':'restaurant_food','s':'100g','k':145,'p':3.5,'c':18.0,'f':6.0,'fi':4.5,'ca':60,'fe':1.3,'src':'brand'},
  {'id':57012,'en':'Kamat Veg Curry (South Indian Style)','bn':'সবজি কারি (কামত)','cat':'restaurant_food','s':'100g','k':120,'p':2.8,'c':12.0,'f':7.0,'fi':3.0,'ca':40,'fe':1.0,'src':'brand'},
  # ── FRESH INDIAN JUICES (56001-56020) ────────────────────────────────────
  {'id':56001,'en':'Sugarcane Juice','bn':'আখের রস','cat':'juice','s':'100ml','k':58,'p':0.2,'c':13.1,'f':0.4,'fi':0.6,'ca':11,'fe':0.2,'src':'local'},
  {'id':56002,'en':'Fresh Mango Juice','bn':'আমের রস','cat':'juice','s':'100ml','k':65,'p':0.5,'c':15.5,'f':0.3,'fi':1.2,'ca':11,'fe':0.2,'src':'local'},
  {'id':56003,'en':'Aam Panna','bn':'আম পান্না','cat':'juice','s':'100ml','k':45,'p':0.4,'c':11.0,'f':0.1,'fi':0.8,'ca':9,'fe':0.3,'src':'local'},
  {'id':56004,'en':'Lemon Juice (Sweetened)','bn':'লেবুর শরবত','cat':'juice','s':'100ml','k':40,'p':0.2,'c':10.0,'f':0.1,'fi':0.3,'ca':6,'fe':0.1,'src':'local'},
  {'id':56005,'en':'Sweet Lime Juice (Mosambi)','bn':'মোসাম্বি জুস','cat':'juice','s':'100ml','k':43,'p':0.6,'c':10.5,'f':0.2,'fi':0.5,'ca':12,'fe':0.2,'src':'local'},
  {'id':56006,'en':'Pomegranate Juice','bn':'ডালিমের রস','cat':'juice','s':'100ml','k':60,'p':0.8,'c':14.0,'f':0.3,'fi':0.7,'ca':10,'fe':0.3,'src':'local'},
  {'id':56007,'en':'Watermelon Juice','bn':'তরমুজের রস','cat':'juice','s':'100ml','k':30,'p':0.4,'c':7.5,'f':0.1,'fi':0.4,'ca':7,'fe':0.2,'src':'local'},
  {'id':56008,'en':'Papaya Juice','bn':'পেঁপের রস','cat':'juice','s':'100ml','k':43,'p':0.5,'c':10.8,'f':0.2,'fi':1.3,'ca':9,'fe':0.3,'src':'local'},
  {'id':56009,'en':'Guava Juice','bn':'পেয়ারার রস','cat':'juice','s':'100ml','k':57,'p':0.8,'c':13.5,'f':0.1,'fi':3.5,'ca':9,'fe':0.4,'src':'local'},
  {'id':56010,'en':'Tender Coconut Water','bn':'ডাবের জল','cat':'juice','s':'100ml','k':19,'p':0.7,'c':3.7,'f':0.2,'fi':0.2,'ca':24,'fe':0.3,'src':'local'},
  {'id':56011,'en':'Lychee Juice','bn':'লিচুর রস','cat':'juice','s':'100ml','k':66,'p':0.7,'c':16.0,'f':0.2,'fi':0.9,'ca':5,'fe':0.2,'src':'local'},
  {'id':56012,'en':'Jamun Juice','bn':'জামুনের রস','cat':'juice','s':'100ml','k':50,'p':0.5,'c':12.0,'f':0.3,'fi':1.5,'ca':15,'fe':0.5,'src':'local'},
  {'id':56013,'en':'Bael Juice','bn':'বেল শরবত','cat':'juice','s':'100ml','k':60,'p':0.6,'c':14.0,'f':0.2,'fi':1.8,'ca':20,'fe':0.6,'src':'local'},
  {'id':56014,'en':'Carrot Juice','bn':'গাজরের রস','cat':'juice','s':'100ml','k':41,'p':0.9,'c':9.6,'f':0.2,'fi':2.8,'ca':33,'fe':0.3,'src':'local'},
  {'id':56015,'en':'Beetroot Juice','bn':'বিটরুটের রস','cat':'juice','s':'100ml','k':43,'p':1.0,'c':10.0,'f':0.2,'fi':2.0,'ca':16,'fe':0.8,'src':'local'},
  {'id':56016,'en':'Cucumber Juice','bn':'শসার রস','cat':'juice','s':'100ml','k':15,'p':0.6,'c':3.6,'f':0.1,'fi':0.5,'ca':16,'fe':0.2,'src':'local'},
  {'id':56017,'en':'Pineapple Juice','bn':'আনারসের রস','cat':'juice','s':'100ml','k':50,'p':0.5,'c':13.0,'f':0.1,'fi':0.9,'ca':13,'fe':0.3,'src':'local'},
  {'id':56018,'en':'Orange Juice','bn':'কমলার রস','cat':'juice','s':'100ml','k':45,'p':0.7,'c':10.4,'f':0.2,'fi':0.6,'ca':11,'fe':0.2,'src':'local'},
  {'id':56019,'en':'Mixed Fruit Juice','bn':'মিক্সড ফলের রস','cat':'juice','s':'100ml','k':55,'p':0.6,'c':13.0,'f':0.2,'fi':1.0,'ca':10,'fe':0.3,'src':'local'},
  {'id':56020,'en':'Aloe Vera Juice','bn':'অ্যালোভেরা জুস','cat':'juice','s':'100ml','k':8,'p':0.0,'c':2.0,'f':0.0,'fi':0.0,'ca':8,'fe':0.1,'src':'local'},
]

data = json.load(open(DATASET, encoding='utf-8'))
print(f'Loaded {len(data)} items')

existing_ids = {d['id'] for d in data}
existing_en  = {d['en'].strip().lower() for d in data}

added, skipped = 0, 0
for item in NEW_ITEMS:
    name_key = item['en'].strip().lower()
    if item['id'] in existing_ids:
        print(f'  SKIP id-conflict ({item["id"]}): {item["en"]}')
        skipped += 1
        continue
    if name_key in existing_en:
        print(f'  SKIP name-dup: {item["en"]}')
        skipped += 1
        continue
    data.append(item)
    existing_ids.add(item['id'])
    existing_en.add(name_key)
    added += 1

print(f'\nAdded: {added}  |  Skipped: {skipped}')
print(f'Total items: {len(data)}')

with open(DATASET, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))
print('Saved.')
