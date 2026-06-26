"""
add_state_foods.py — Add regional state foods (Kashmir, UP, Assam, Punjab, Haryana, Kerala)
to food_master_v8_0.json

Duplicates skipped automatically (checked by both ID and English name):
  - Seekh Kebab, Shami Kebab, Chole, Dal Makhani, Paneer Butter Masala, Butter Chicken
  - Assam batch 20001-20010 are identical to 18101-18110 (skipped by name)
  - IDs 20013/20014 reassigned to 21001/21002 (conflict with Pongal/Ven Pongal)
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

NEW_ITEMS = [
  # ── KASHMIR (17001-17015) ────────────────────────────────────────────────
  {'id':17001,'en':'Rogan Josh','bn':'রোগান জোশ','cat':'mutton','s':'100g','k':248,'p':18.8,'c':3.8,'f':17.2,'fi':0.6,'ca':22,'fe':2.2,'src':'local'},
  {'id':17002,'en':'Yakhni','bn':'ইয়াখনি','cat':'mutton','s':'100g','k':182,'p':17.5,'c':2.8,'f':11.0,'fi':0.2,'ca':65,'fe':1.8,'src':'local'},
  {'id':17003,'en':'Gushtaba','bn':'গুস্তাবা','cat':'mutton','s':'100g','k':232,'p':17.0,'c':4.0,'f':16.2,'fi':0.3,'ca':52,'fe':2.1,'src':'local'},
  {'id':17004,'en':'Rista','bn':'রিস্তা','cat':'mutton','s':'100g','k':238,'p':18.0,'c':3.5,'f':17.0,'fi':0.4,'ca':28,'fe':2.3,'src':'local'},
  {'id':17005,'en':'Tabak Maaz','bn':'তাবাক মাজ','cat':'mutton','s':'100g','k':335,'p':21.0,'c':2.0,'f':27.0,'fi':0.0,'ca':24,'fe':2.1,'src':'local'},
  {'id':17006,'en':'Dhaniwal Korma','bn':'ধানিওয়াল কোরমা','cat':'mutton','s':'100g','k':220,'p':18.5,'c':4.0,'f':14.5,'fi':0.7,'ca':30,'fe':2.0,'src':'local'},
  {'id':17007,'en':'Aab Gosht','bn':'আব গোশ্ত','cat':'mutton','s':'100g','k':205,'p':17.2,'c':3.2,'f':13.0,'fi':0.3,'ca':72,'fe':1.8,'src':'local'},
  {'id':17008,'en':'Kashmiri Dum Aloo','bn':'কাশ্মীরি দম আলু','cat':'vegetable','s':'100g','k':146,'p':2.6,'c':18.5,'f':6.8,'fi':2.8,'ca':26,'fe':0.9,'src':'local'},
  {'id':17009,'en':'Nadru Yakhni','bn':'নাদরু ইয়াখনি','cat':'vegetable','s':'100g','k':108,'p':3.8,'c':11.5,'f':5.5,'fi':2.6,'ca':42,'fe':1.2,'src':'local'},
  {'id':17010,'en':'Nadru Monje','bn':'নাদরু মঞ্জে','cat':'snack','s':'100g','k':235,'p':4.0,'c':28.5,'f':11.8,'fi':3.2,'ca':38,'fe':1.5,'src':'local'},
  {'id':17011,'en':'Haak Saag','bn':'হাক শাক','cat':'vegetable','s':'100g','k':56,'p':3.5,'c':7.2,'f':1.8,'fi':3.8,'ca':158,'fe':2.4,'src':'local'},
  {'id':17012,'en':'Methi Chaman','bn':'মেথি চামান','cat':'paneer','s':'100g','k':196,'p':10.8,'c':5.8,'f':14.2,'fi':1.8,'ca':236,'fe':1.0,'src':'local'},
  {'id':17013,'en':'Chaman Kaliya','bn':'চামান কালিয়া','cat':'paneer','s':'100g','k':208,'p':11.5,'c':5.2,'f':15.6,'fi':1.0,'ca':242,'fe':1.0,'src':'local'},
  {'id':17014,'en':'Modur Pulao','bn':'মোদুর পুলাও','cat':'rice','s':'100g','k':198,'p':3.5,'c':34.0,'f':5.2,'fi':1.4,'ca':22,'fe':0.8,'src':'local'},
  {'id':17015,'en':'Kashmiri Kahwa','bn':'কাশ্মীরি কাহওয়া','cat':'beverage','s':'100g','k':24,'p':0.2,'c':5.8,'f':0.1,'fi':0.3,'ca':8,'fe':0.2,'src':'local'},
  # ── UTTAR PRADESH / LUCKNOW (18001-18010, skip Seekh Kebab & Shami Kebab dups) ──
  {'id':18001,'en':'Lucknowi Chicken Biryani','bn':'লখনউই চিকেন বিরিয়ানি','cat':'rice','s':'100g','k':186,'p':9.5,'c':20.8,'f':7.0,'fi':1.1,'ca':18,'fe':1.2,'src':'local'},
  {'id':18002,'en':'Lucknowi Mutton Biryani','bn':'লখনউই মাটন বিরিয়ানি','cat':'rice','s':'100g','k':215,'p':10.8,'c':20.2,'f':10.5,'fi':1.0,'ca':16,'fe':1.7,'src':'local'},
  {'id':18003,'en':'Galouti Kebab','bn':'গালৌটি কাবাব','cat':'mutton','s':'100g','k':284,'p':17.8,'c':5.4,'f':20.6,'fi':0.6,'ca':18,'fe':2.7,'src':'local'},
  # 18004 Seekh Kebab — skip (exists as 60016)
  {'id':18005,'en':'Kakori Kebab','bn':'কাকোরি কাবাব','cat':'mutton','s':'100g','k':276,'p':18.2,'c':4.6,'f':19.5,'fi':0.4,'ca':20,'fe':2.5,'src':'local'},
  {'id':18006,'en':'Nihari','bn':'নিহারি','cat':'mutton','s':'100g','k':192,'p':16.5,'c':3.2,'f':12.2,'fi':0.4,'ca':24,'fe':2.0,'src':'local'},
  # 18007 Shami Kebab — skip (exists as 60017)
  {'id':18008,'en':'Bedmi Puri','bn':'বেদমি পুরি','cat':'bread','s':'100g','k':318,'p':8.4,'c':41.5,'f':13.5,'fi':4.0,'ca':32,'fe':2.3,'src':'local'},
  {'id':18009,'en':'Aloo Sabzi','bn':'আলুর সবজি','cat':'vegetable','s':'100g','k':92,'p':2.0,'c':13.5,'f':3.4,'fi':2.1,'ca':16,'fe':0.8,'src':'local'},
  {'id':18010,'en':'Tehri','bn':'তেহরি','cat':'rice','s':'100g','k':152,'p':3.8,'c':24.0,'f':4.5,'fi':2.3,'ca':20,'fe':0.9,'src':'local'},
  # ── ASSAM (18101-18110) ──────────────────────────────────────────────────
  {'id':18101,'en':'Masor Tenga','bn':'মাসোর টেঙ্গা','cat':'fish','s':'100g','k':112,'p':17.8,'c':2.5,'f':3.2,'fi':0.6,'ca':28,'fe':1.0,'src':'local'},
  {'id':18102,'en':'Khar','bn':'খার','cat':'vegetable','s':'100g','k':74,'p':2.6,'c':10.8,'f':2.1,'fi':2.6,'ca':34,'fe':1.2,'src':'local'},
  {'id':18103,'en':'Duck Curry','bn':'হাঁসের ঝোল','cat':'duck','s':'100g','k':238,'p':18.5,'c':3.5,'f':16.2,'fi':0.5,'ca':18,'fe':2.5,'src':'local'},
  {'id':18104,'en':'Chicken with Bamboo Shoot','bn':'বাঁশকোঁড়া দিয়ে মুরগি','cat':'chicken','s':'100g','k':168,'p':19.2,'c':3.2,'f':8.4,'fi':1.2,'ca':22,'fe':1.1,'src':'local'},
  {'id':18105,'en':'Pitika','bn':'পিটিকা','cat':'vegetable','s':'100g','k':82,'p':2.1,'c':14.5,'f':2.0,'fi':2.8,'ca':18,'fe':0.8,'src':'local'},
  {'id':18106,'en':'Ou Khatta','bn':'ওউ খাট্টা','cat':'vegetable','s':'100g','k':98,'p':0.8,'c':23.2,'f':0.4,'fi':3.4,'ca':20,'fe':0.6,'src':'local'},
  {'id':18107,'en':'Pura Maas','bn':'পুরা মাছ','cat':'fish','s':'100g','k':158,'p':22.5,'c':1.0,'f':7.0,'fi':0.3,'ca':32,'fe':1.2,'src':'local'},
  {'id':18108,'en':'Bora Saul with Curd','bn':'বোরা চাল দই','cat':'rice','s':'100g','k':128,'p':3.5,'c':25.2,'f':1.6,'fi':0.8,'ca':58,'fe':0.5,'src':'local'},
  {'id':18109,'en':'Poita Bhat','bn':'পইতা ভাত','cat':'rice','s':'100g','k':112,'p':2.8,'c':24.5,'f':0.4,'fi':0.6,'ca':8,'fe':0.4,'src':'local'},
  {'id':18110,'en':'Assamese Mixed Vegetable','bn':'অসমীয়া মিশ্র সবজি','cat':'vegetable','s':'100g','k':78,'p':2.5,'c':11.8,'f':2.4,'fi':3.1,'ca':36,'fe':1.2,'src':'local'},
  # ── PUNJAB (19001-19010, skip Dal Makhani/Chole/Paneer Butter Masala/Butter Chicken dups) ──
  {'id':19001,'en':'Sarson Ka Saag','bn':'সর্ষে শাক','cat':'vegetable','s':'100g','k':92,'p':4.2,'c':8.8,'f':4.8,'fi':4.2,'ca':178,'fe':2.6,'src':'local'},
  {'id':19002,'en':'Makki Ki Roti','bn':'মক্কির রুটি','cat':'bread','s':'100g','k':268,'p':6.4,'c':53.2,'f':3.8,'fi':6.4,'ca':12,'fe':2.1,'src':'local'},
  # 19003 Dal Makhani — skip (exists as id=144)
  {'id':19004,'en':'Rajma Masala','bn':'রাজমা মসালা','cat':'dal','s':'100g','k':136,'p':7.8,'c':18.5,'f':3.2,'fi':6.2,'ca':38,'fe':2.5,'src':'local'},
  # 19005 Chole — skip (exists as id=60002)
  # 19006 Paneer Butter Masala — skip (exists as id=40015)
  {'id':19007,'en':'Amritsari Fish','bn':'অমৃতসরি মাছ ভাজা','cat':'fish','s':'100g','k':228,'p':20.8,'c':9.4,'f':12.1,'fi':0.8,'ca':28,'fe':1.4,'src':'local'},
  {'id':19008,'en':'Amritsari Kulcha','bn':'অমৃতসরি কুলচা','cat':'bread','s':'100g','k':286,'p':8.2,'c':46.8,'f':7.6,'fi':2.8,'ca':48,'fe':2.5,'src':'local'},
  {'id':19009,'en':'Lassi Sweet','bn':'মিষ্টি লস্যি','cat':'beverage','s':'100g','k':92,'p':3.3,'c':11.8,'f':3.6,'fi':0.0,'ca':126,'fe':0.1,'src':'local'},
  # 19010 Butter Chicken — skip (exists as id=319)
  # ── HARYANA (19101-19108) ────────────────────────────────────────────────
  {'id':19101,'en':'Bajra Khichdi','bn':'বাজরা খিচুড়ি','cat':'rice','s':'100g','k':134,'p':4.2,'c':24.2,'f':2.3,'fi':3.8,'ca':18,'fe':2.0,'src':'local'},
  {'id':19102,'en':'Bajra Roti','bn':'বাজরার রুটি','cat':'bread','s':'100g','k':271,'p':8.1,'c':51.6,'f':4.3,'fi':8.0,'ca':27,'fe':3.1,'src':'local'},
  {'id':19103,'en':'Kadhi Pakora','bn':'কড়ি পাকোড়া','cat':'curry','s':'100g','k':124,'p':4.8,'c':8.8,'f':7.2,'fi':1.2,'ca':92,'fe':0.8,'src':'local'},
  {'id':19104,'en':'Bathua Raita','bn':'বাথুয়া রায়তা','cat':'curd','s':'100g','k':74,'p':3.6,'c':5.2,'f':4.2,'fi':1.6,'ca':138,'fe':1.2,'src':'local'},
  {'id':19105,'en':'Besan Masala Roti','bn':'বেসন মসালা রুটি','cat':'bread','s':'100g','k':296,'p':11.0,'c':44.8,'f':8.2,'fi':6.1,'ca':34,'fe':2.8,'src':'local'},
  {'id':19106,'en':'Mixed Saag','bn':'মিশ্র শাক','cat':'vegetable','s':'100g','k':68,'p':3.5,'c':8.2,'f':2.4,'fi':3.9,'ca':146,'fe':2.3,'src':'local'},
  {'id':19107,'en':'Haryanvi Kheer','bn':'হরিয়ানভি ক্ষীর','cat':'sweet','s':'100g','k':162,'p':4.2,'c':25.6,'f':5.0,'fi':0.2,'ca':128,'fe':0.2,'src':'local'},
  {'id':19108,'en':'Bajra Aloo Paratha','bn':'বাজরা আলু পরোটা','cat':'bread','s':'100g','k':248,'p':6.8,'c':37.2,'f':8.4,'fi':5.0,'ca':22,'fe':2.3,'src':'local'},
  # ── KERALA (19201-19215) ─────────────────────────────────────────────────
  {'id':19201,'en':'Appam','bn':'আপ্পাম','cat':'breakfast','s':'100g','k':151,'p':3.6,'c':31.2,'f':1.6,'fi':1.2,'ca':18,'fe':0.6,'src':'local'},
  {'id':19202,'en':'Idiyappam','bn':'ইডিয়াপ্পাম','cat':'breakfast','s':'100g','k':147,'p':2.8,'c':33.8,'f':0.4,'fi':1.0,'ca':10,'fe':0.5,'src':'local'},
  {'id':19203,'en':'Puttu','bn':'পুট্টু','cat':'breakfast','s':'100g','k':171,'p':3.8,'c':34.5,'f':2.8,'fi':2.8,'ca':14,'fe':1.2,'src':'local'},
  {'id':19204,'en':'Kadala Curry','bn':'কাডালা কারি','cat':'dal','s':'100g','k':152,'p':7.4,'c':18.4,'f':5.0,'fi':6.2,'ca':42,'fe':2.4,'src':'local'},
  {'id':19205,'en':'Avial','bn':'আভিয়াল','cat':'vegetable','s':'100g','k':112,'p':2.6,'c':10.6,'f':7.2,'fi':3.5,'ca':46,'fe':1.0,'src':'local'},
  {'id':19206,'en':'Erissery','bn':'এরিশেরি','cat':'vegetable','s':'100g','k':118,'p':4.2,'c':14.4,'f':5.2,'fi':4.0,'ca':52,'fe':1.5,'src':'local'},
  {'id':19207,'en':'Thoran','bn':'থোরান','cat':'vegetable','s':'100g','k':104,'p':2.8,'c':9.6,'f':6.4,'fi':3.8,'ca':48,'fe':1.2,'src':'local'},
  {'id':19208,'en':'Fish Molee','bn':'ফিশ মোলি','cat':'fish','s':'100g','k':168,'p':18.2,'c':3.8,'f':8.6,'fi':0.6,'ca':36,'fe':1.1,'src':'local'},
  {'id':19209,'en':'Kerala Fish Curry','bn':'কেরালা মাছের কারি','cat':'fish','s':'100g','k':154,'p':18.4,'c':2.8,'f':7.2,'fi':0.5,'ca':34,'fe':1.0,'src':'local'},
  {'id':19210,'en':'Chicken Stew','bn':'চিকেন স্ট্যু','cat':'chicken','s':'100g','k':148,'p':15.8,'c':3.6,'f':8.0,'fi':0.5,'ca':28,'fe':1.0,'src':'local'},
  {'id':19211,'en':'Malabar Parotta','bn':'মালাবার পরোটা','cat':'bread','s':'100g','k':324,'p':7.6,'c':44.2,'f':13.8,'fi':2.1,'ca':26,'fe':2.2,'src':'local'},
  {'id':19212,'en':'Prawn Roast','bn':'চিংড়ি রোস্ট','cat':'seafood','s':'100g','k':182,'p':21.0,'c':4.2,'f':8.4,'fi':0.5,'ca':58,'fe':1.8,'src':'local'},
  {'id':19213,'en':'Beef Fry (Kerala Style)','bn':'কেরালা স্টাইল বিফ ফ্রাই','cat':'beef','s':'100g','k':242,'p':21.4,'c':3.4,'f':16.2,'fi':0.6,'ca':18,'fe':2.8,'src':'local'},
  {'id':19214,'en':'Payasam','bn':'পায়াসম','cat':'sweet','s':'100g','k':176,'p':3.8,'c':28.6,'f':5.8,'fi':0.4,'ca':86,'fe':0.5,'src':'local'},
  {'id':19215,'en':'Ada Pradhaman','bn':'আদা প্রদামান','cat':'sweet','s':'100g','k':214,'p':2.8,'c':34.8,'f':7.8,'fi':0.8,'ca':42,'fe':0.6,'src':'local'},
  # ── ASSAM EXTRA (20011-20015; 20013/20014 reassigned to 21001/21002 to avoid ID conflicts) ──
  {'id':20011,'en':'Lai Xaak Bhaji','bn':'লাই শাক ভাজি','cat':'vegetable','s':'100g','k':52,'p':3.2,'c':6.4,'f':1.4,'fi':3.6,'ca':162,'fe':2.4,'src':'local'},
  {'id':20012,'en':'Bilahi Maas','bn':'টমেটো মাছের ঝোল','cat':'fish','s':'100g','k':126,'p':18.6,'c':3.4,'f':4.2,'fi':0.8,'ca':26,'fe':1.0,'src':'local'},
  {'id':21001,'en':'Boror Tenga','bn':'বড়ার টেঙ্গা','cat':'vegetable','s':'100g','k':148,'p':5.8,'c':16.8,'f':6.4,'fi':3.6,'ca':42,'fe':1.8,'src':'local'},
  {'id':21002,'en':'Koldil Chicken','bn':'কলা ফুল দিয়ে মুরগি','cat':'chicken','s':'100g','k':172,'p':18.5,'c':5.0,'f':8.0,'fi':2.6,'ca':36,'fe':1.3,'src':'local'},
  {'id':20015,'en':'Black Sesame Chicken','bn':'কালো তিল দিয়ে মুরগি','cat':'chicken','s':'100g','k':196,'p':19.0,'c':3.4,'f':11.4,'fi':1.5,'ca':82,'fe':2.1,'src':'local'},
]

data = json.load(open(DATASET, encoding='utf-8'))
print(f'Loaded {len(data)} items')

existing_ids  = {d['id'] for d in data}
existing_en   = {d['en'].strip().lower() for d in data}

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
