"""
add_fruits.py — Add exotic, wild/indigenous, and international fruits

ID mapping (user's original IDs → assigned IDs):
  Exotic/tropical 54001-54015 → 55001-55015  (54001-54015 taken by Amul)
  Indian Gooseberry 54101     → 54101         (free)
  Wild/indigenous  54201-54220 → 54201-54220  (free)
  54301-54320 block: deduplicated — 8 dups of exotic batch, 4 plural-of-existing-berry
  Unique from that block: Green Kiwi, Gold Kiwi, Cherimoya, Feijoa, Pomelo, Blood Orange

Skipped (name duplicates of existing singular-form entries):
  Blueberries → Blueberry (15006), Blackberries → Blackberry (15005),
  Raspberries → Raspberry (15004), Cranberries → Cranberry (15020),
  Nectarine (15017), Apricot (15015)
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

NEW_ITEMS = [
  # ── EXOTIC / TROPICAL FRUITS (55001-55015) ───────────────────────────────
  {'id':55001,'en':'Dragon Fruit','bn':'ড্রাগন ফল','cat':'fruit','s':'100g','k':60,'p':1.2,'c':13.0,'f':0.4,'fi':3.0,'ca':18,'fe':0.7,'src':'local'},
  {'id':55002,'en':'Kiwano (Horned Melon)','bn':'কিওয়ানো','cat':'fruit','s':'100g','k':44,'p':1.8,'c':7.6,'f':1.3,'fi':3.6,'ca':13,'fe':1.1,'src':'local'},
  {'id':55003,'en':'Mangosteen','bn':'ম্যাঙ্গোস্টিন','cat':'fruit','s':'100g','k':73,'p':0.6,'c':18.0,'f':0.6,'fi':1.8,'ca':12,'fe':0.3,'src':'local'},
  {'id':55004,'en':'Rambutan','bn':'রামবুটান','cat':'fruit','s':'100g','k':68,'p':0.9,'c':16.5,'f':0.2,'fi':0.9,'ca':22,'fe':0.4,'src':'local'},
  {'id':55005,'en':'Passion Fruit','bn':'প্যাশন ফল','cat':'fruit','s':'100g','k':97,'p':2.2,'c':23.4,'f':0.7,'fi':10.4,'ca':12,'fe':1.6,'src':'local'},
  {'id':55006,'en':'Star Fruit','bn':'কামরাঙা','cat':'fruit','s':'100g','k':31,'p':1.0,'c':6.7,'f':0.3,'fi':2.8,'ca':3,'fe':0.1,'src':'local'},
  {'id':55007,'en':'Avocado','bn':'অ্যাভোকাডো','cat':'fruit','s':'100g','k':160,'p':2.0,'c':8.5,'f':14.7,'fi':6.7,'ca':12,'fe':0.6,'src':'local'},
  {'id':55008,'en':'Persimmon','bn':'পার্সিমন','cat':'fruit','s':'100g','k':70,'p':0.6,'c':18.6,'f':0.2,'fi':3.6,'ca':8,'fe':0.2,'src':'local'},
  {'id':55009,'en':'Longan','bn':'লংগান','cat':'fruit','s':'100g','k':60,'p':1.3,'c':15.1,'f':0.1,'fi':1.1,'ca':1,'fe':0.1,'src':'local'},
  {'id':55010,'en':'Soursop','bn':'সাওয়ারসপ','cat':'fruit','s':'100g','k':66,'p':1.0,'c':16.8,'f':0.3,'fi':3.3,'ca':14,'fe':0.6,'src':'local'},
  {'id':55011,'en':'Breadfruit','bn':'ব্রেডফ্রুট','cat':'fruit','s':'100g','k':103,'p':1.1,'c':27.0,'f':0.2,'fi':4.9,'ca':17,'fe':0.5,'src':'local'},
  {'id':55012,'en':'Durian','bn':'ডুরিয়ান','cat':'fruit','s':'100g','k':147,'p':1.5,'c':27.1,'f':5.3,'fi':3.8,'ca':6,'fe':0.4,'src':'local'},
  {'id':55013,'en':'Jabuticaba','bn':'জাবুটিকাবা','cat':'fruit','s':'100g','k':58,'p':0.6,'c':15.0,'f':0.1,'fi':2.3,'ca':12,'fe':0.3,'src':'local'},
  {'id':55014,'en':'Bael Fruit','bn':'বেল','cat':'fruit','s':'100g','k':88,'p':1.8,'c':31.8,'f':0.3,'fi':2.9,'ca':85,'fe':0.7,'src':'local'},
  {'id':55015,'en':'Wood Apple','bn':'কয়েত বেল','cat':'fruit','s':'100g','k':134,'p':7.1,'c':18.0,'f':3.7,'fi':5.0,'ca':130,'fe':0.8,'src':'local'},
  # ── INDIAN GOOSEBERRY (54101) ─────────────────────────────────────────────
  {'id':54101,'en':'Indian Gooseberry (Amla)','bn':'আমলকি','cat':'fruit','s':'100g','k':44,'p':0.9,'c':10.2,'f':0.6,'fi':4.3,'ca':25,'fe':0.3,'src':'local'},
  # ── WILD / INDIGENOUS INDIAN FRUITS (54201-54220) ────────────────────────
  {'id':54201,'en':'Kaafal','bn':'কাফল','cat':'fruit','s':'100g','k':68,'p':1.2,'c':16.5,'f':0.5,'fi':4.8,'ca':24,'fe':0.9,'src':'local'},
  {'id':54202,'en':'Hisalu (Yellow Himalayan Raspberry)','bn':'হিসালু','cat':'fruit','s':'100g','k':55,'p':1.4,'c':11.9,'f':0.6,'fi':6.2,'ca':27,'fe':0.7,'src':'local'},
  {'id':54203,'en':'Bedu (Wild Fig)','bn':'বন ডুমুর','cat':'fruit','s':'100g','k':74,'p':0.9,'c':19.0,'f':0.3,'fi':2.9,'ca':35,'fe':0.4,'src':'local'},
  {'id':54204,'en':'Mahua Fruit','bn':'মহুয়া ফল','cat':'fruit','s':'100g','k':102,'p':1.5,'c':24.0,'f':0.5,'fi':3.5,'ca':42,'fe':0.8,'src':'local'},
  {'id':54205,'en':'Kendu Fruit','bn':'কেন্দু ফল','cat':'fruit','s':'100g','k':85,'p':1.0,'c':21.0,'f':0.4,'fi':3.6,'ca':20,'fe':0.5,'src':'local'},
  {'id':54206,'en':'Chironji Fruit','bn':'চিরৌঞ্জি ফল','cat':'fruit','s':'100g','k':96,'p':2.1,'c':22.4,'f':1.0,'fi':3.8,'ca':28,'fe':0.8,'src':'local'},
  {'id':54207,'en':'Elephant Apple','bn':'চালতা','cat':'fruit','s':'100g','k':52,'p':0.8,'c':13.0,'f':0.3,'fi':2.5,'ca':18,'fe':0.4,'src':'local'},
  {'id':54208,'en':'Monkey Jack','bn':'বন কাঠাল','cat':'fruit','s':'100g','k':90,'p':1.6,'c':22.0,'f':0.5,'fi':3.7,'ca':27,'fe':0.6,'src':'local'},
  {'id':54209,'en':'Wild Mango','bn':'বন আম','cat':'fruit','s':'100g','k':64,'p':0.9,'c':16.0,'f':0.4,'fi':2.0,'ca':12,'fe':0.2,'src':'local'},
  {'id':54210,'en':'Wild Ber','bn':'বন কুল','cat':'fruit','s':'100g','k':78,'p':1.3,'c':20.0,'f':0.2,'fi':2.9,'ca':25,'fe':0.8,'src':'local'},
  {'id':54211,'en':'Indian Olive','bn':'জলপাই','cat':'fruit','s':'100g','k':56,'p':1.0,'c':14.0,'f':0.4,'fi':3.2,'ca':31,'fe':0.6,'src':'local'},
  {'id':54212,'en':'Jungle Jalebi','bn':'জঙ্গল জিলাপি','cat':'fruit','s':'100g','k':83,'p':2.5,'c':18.5,'f':0.7,'fi':4.0,'ca':30,'fe':1.2,'src':'local'},
  {'id':54213,'en':'Wild Passion Fruit','bn':'বন্য প্যাশন ফল','cat':'fruit','s':'100g','k':90,'p':2.0,'c':21.5,'f':0.7,'fi':9.8,'ca':14,'fe':1.5,'src':'local'},
  {'id':54214,'en':'Sohiong','bn':'সোহিয়ং','cat':'fruit','s':'100g','k':63,'p':1.1,'c':15.5,'f':0.3,'fi':3.8,'ca':22,'fe':0.6,'src':'local'},
  {'id':54215,'en':'Sohshang','bn':'সোহশাং','cat':'fruit','s':'100g','k':58,'p':1.2,'c':13.8,'f':0.3,'fi':4.2,'ca':24,'fe':0.5,'src':'local'},
  {'id':54216,'en':'Wild Raspberry','bn':'বন্য রাস্পবেরি','cat':'fruit','s':'100g','k':52,'p':1.2,'c':11.8,'f':0.7,'fi':6.5,'ca':25,'fe':0.7,'src':'local'},
  {'id':54217,'en':'Wild Strawberry','bn':'বন্য স্ট্রবেরি','cat':'fruit','s':'100g','k':34,'p':0.8,'c':7.8,'f':0.3,'fi':2.2,'ca':16,'fe':0.4,'src':'local'},
  {'id':54218,'en':'Wild Peach','bn':'বন্য পীচ','cat':'fruit','s':'100g','k':41,'p':0.9,'c':10.1,'f':0.3,'fi':1.6,'ca':6,'fe':0.3,'src':'local'},
  {'id':54219,'en':'Wild Plum','bn':'বন্য বরই','cat':'fruit','s':'100g','k':46,'p':0.7,'c':11.4,'f':0.3,'fi':1.5,'ca':6,'fe':0.2,'src':'local'},
  {'id':54220,'en':'Wild Pear','bn':'বন্য নাশপাতি','cat':'fruit','s':'100g','k':57,'p':0.4,'c':15.2,'f':0.1,'fi':3.1,'ca':9,'fe':0.2,'src':'local'},
  # ── INTERNATIONAL FRUITS (unique from 54301-54320 block) ─────────────────
  # Skip: Dragon Fruit, Mangosteen, Rambutan, Longan, Persimmon, Passion Fruit,
  #        Durian, Avocado (all covered above); Blueberries/Blackberries/
  #        Raspberries/Cranberries (dup of singular forms 15006/15005/15004/15020);
  #        Nectarine (15017), Apricot (15015)
  {'id':54302,'en':'Green Kiwi','bn':'সবুজ কিউই','cat':'fruit','s':'100g','k':61,'p':1.1,'c':14.7,'f':0.5,'fi':3.0,'ca':34,'fe':0.3,'src':'local'},
  {'id':54303,'en':'Gold Kiwi','bn':'গোল্ড কিউই','cat':'fruit','s':'100g','k':63,'p':1.2,'c':15.8,'f':0.3,'fi':1.4,'ca':20,'fe':0.3,'src':'local'},
  {'id':54315,'en':'Cherimoya','bn':'চেরিমোয়া','cat':'fruit','s':'100g','k':75,'p':1.6,'c':17.7,'f':0.7,'fi':3.0,'ca':10,'fe':0.3,'src':'local'},
  {'id':54316,'en':'Feijoa','bn':'ফেইজোয়া','cat':'fruit','s':'100g','k':61,'p':1.0,'c':15.2,'f':0.8,'fi':6.4,'ca':17,'fe':0.1,'src':'local'},
  {'id':54317,'en':'Pomelo','bn':'পোমেলো','cat':'fruit','s':'100g','k':38,'p':0.8,'c':9.6,'f':0.0,'fi':1.0,'ca':4,'fe':0.1,'src':'local'},
  {'id':54318,'en':'Blood Orange','bn':'ব্লাড অরেঞ্জ','cat':'fruit','s':'100g','k':47,'p':0.9,'c':11.8,'f':0.1,'fi':2.4,'ca':40,'fe':0.1,'src':'local'},
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
