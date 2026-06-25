import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

new_items = [
  {"id":10001,"en":"Mochar Ghonto","bn":"মোচার ঘন্ট","cat":"vegetable","s":"100g","k":115,"p":3.4,"c":14.8,"f":4.8,"fi":5.2,"ca":42,"fe":1.6,"src":"local","kw":["mochar ghonto","mocha","banana flower","ghonto","bengali","vegetable","tarkari"]},
  {"id":10002,"en":"Thor Ghonto","bn":"থোর ঘন্ট","cat":"vegetable","s":"100g","k":72,"p":2.1,"c":11.5,"f":2.2,"fi":4.8,"ca":58,"fe":1.3,"src":"local","kw":["thor","ghonto","banana stem","Bengali","vegetable","tarkari"]},
  {"id":10003,"en":"Enchorer Dalna","bn":"এঁচোড়ের ডালনা","cat":"vegetable","s":"100g","k":108,"p":2.8,"c":15.9,"f":3.9,"fi":4.1,"ca":35,"fe":1.1,"src":"local","kw":["enchor","enchore","jackfruit","raw jackfruit","dalna","bengali","vegetable","tarkari"]},
  {"id":10004,"en":"Shukto","bn":"শুক্তো","cat":"vegetable","s":"100g","k":68,"p":2.3,"c":8.9,"f":2.8,"fi":3.5,"ca":48,"fe":1.0,"src":"local","kw":["shukto","sukto","bitter","mixed vegetable","bengali","tarkari"]},
  {"id":10005,"en":"Labra","bn":"লাবড়া","cat":"vegetable","s":"100g","k":78,"p":2.0,"c":11.4,"f":2.9,"fi":3.8,"ca":45,"fe":1.1,"src":"local","kw":["labra","mixed vegetable","bengali","tarkari","five vegetable"]},
  {"id":10006,"en":"Chorchori","bn":"চচ্চড়ি","cat":"vegetable","s":"100g","k":82,"p":2.4,"c":10.8,"f":3.5,"fi":3.6,"ca":40,"fe":1.2,"src":"local","kw":["chorchori","charchori","mixed vegetable stir fry","bengali","tarkari"]},
  {"id":10007,"en":"Aloor Dom","bn":"আলুর দম","cat":"vegetable","s":"100g","k":125,"p":2.6,"c":18.9,"f":4.6,"fi":2.4,"ca":18,"fe":0.9,"src":"local","kw":["aloor dom","aloo dum","potato curry","dum aloo","bengali","tarkari"]},
  {"id":10008,"en":"Dhokar Dalna","bn":"ঢোকার ডালনা","cat":"vegetable","s":"100g","k":156,"p":7.2,"c":18.4,"f":5.8,"fi":3.1,"ca":36,"fe":2.0,"src":"local","kw":["dhokar dalna","dhoka","lentil cake curry","bengali","tarkari"]},
  {"id":10009,"en":"Potoler Dorma","bn":"পটলের দোরমা","cat":"vegetable","s":"100g","k":118,"p":3.5,"c":13.6,"f":5.0,"fi":3.2,"ca":28,"fe":1.0,"src":"local","kw":["potoler dorma","potol","pointed gourd","stuffed","bengali","tarkari"]},
  {"id":10010,"en":"Potol Bhaja","bn":"পটল ভাজা","cat":"vegetable","s":"100g","k":132,"p":2.1,"c":10.7,"f":8.9,"fi":2.7,"ca":24,"fe":0.8,"src":"local","kw":["potol","potol bhaja","pointed gourd","fry","bhaja","bengali","tarkari"]},
  {"id":10011,"en":"Begun Bhaja","bn":"বেগুন ভাজা","cat":"vegetable","s":"100g","k":145,"p":1.8,"c":9.6,"f":10.8,"fi":3.3,"ca":20,"fe":0.7,"src":"local","kw":["begun","brinjal","eggplant","bhaja","fry","bengali","tarkari"]},
  {"id":10012,"en":"Begun Pora","bn":"বেগুন পোড়া","cat":"vegetable","s":"100g","k":78,"p":2.2,"c":8.5,"f":3.5,"fi":3.7,"ca":26,"fe":1.1,"src":"local","kw":["begun pora","brinjal","eggplant","roasted","baingan bharta","bengali","tarkari"]},
  {"id":10013,"en":"Kumro Chhokka","bn":"কুমড়ো ছক্কা","cat":"vegetable","s":"100g","k":92,"p":2.1,"c":14.5,"f":2.8,"fi":2.9,"ca":30,"fe":0.9,"src":"local","kw":["kumro","chhokka","pumpkin","kumro chhokka","bengali","tarkari"]},
  {"id":10014,"en":"Bandhakopir Tarkari","bn":"বাঁধাকপির তরকারি","cat":"vegetable","s":"100g","k":64,"p":2.3,"c":8.4,"f":2.1,"fi":3.0,"ca":44,"fe":0.8,"src":"local","kw":["bandhakopi","cabbage","tarkari","bengali","vegetable"]},
  {"id":10015,"en":"Phulkopir Dalna","bn":"ফুলকপির ডালনা","cat":"vegetable","s":"100g","k":88,"p":3.0,"c":10.6,"f":3.4,"fi":3.5,"ca":38,"fe":1.0,"src":"local","kw":["phulkopi","cauliflower","dalna","bengali","tarkari"]},
  {"id":10016,"en":"Kochur Ghonto","bn":"কচুর ঘন্ট","cat":"vegetable","s":"100g","k":110,"p":2.4,"c":16.2,"f":3.8,"fi":4.0,"ca":54,"fe":1.5,"src":"local","kw":["kochu","kochur ghonto","taro","colocasia","ghonto","bengali","tarkari"]},
  {"id":10017,"en":"Pui Shaak Chorchori","bn":"পুঁই শাক চচ্চড়ি","cat":"vegetable","s":"100g","k":58,"p":2.6,"c":6.9,"f":2.1,"fi":3.9,"ca":82,"fe":2.2,"src":"local","kw":["pui shaak","malabar spinach","chorchori","bengali","shaak","greens","tarkari"]},
  {"id":10018,"en":"Lau Ghonto","bn":"লাউ ঘন্ট","cat":"vegetable","s":"100g","k":54,"p":1.9,"c":7.2,"f":1.8,"fi":2.7,"ca":30,"fe":0.7,"src":"local","kw":["lau","bottle gourd","ghonto","bengali","tarkari"]},
  {"id":10019,"en":"Lau Ghonto Veg","bn":"লাউ ঘন্ট","cat":"vegetable","s":"100g","k":65,"p":2.1,"c":8.1,"f":2.4,"fi":2.8,"ca":32,"fe":0.8,"src":"local","kw":["lau","bottle gourd","ghonto","veg","bengali","tarkari"]},
  {"id":10020,"en":"Jhinge Posto","bn":"ঝিঙে পোস্ত","cat":"vegetable","s":"100g","k":126,"p":3.4,"c":8.6,"f":8.8,"fi":3.0,"ca":115,"fe":1.4,"src":"local","kw":["jhinge","ridge gourd","posto","poppy seed","bengali","tarkari"]},
  {"id":10021,"en":"Aloo Posto","bn":"আলু পোস্ত","cat":"vegetable","s":"100g","k":152,"p":3.6,"c":16.4,"f":8.1,"fi":2.7,"ca":132,"fe":1.5,"src":"local","kw":["aloo","potato","posto","poppy seed","bengali","tarkari"]},
  {"id":10022,"en":"Potol Posto","bn":"পটল পোস্ত","cat":"vegetable","s":"100g","k":138,"p":3.2,"c":11.9,"f":8.6,"fi":3.1,"ca":126,"fe":1.3,"src":"local","kw":["potol","pointed gourd","posto","poppy seed","bengali","tarkari"]},
  {"id":10023,"en":"Uchhe Bhaja","bn":"উচ্ছে ভাজা","cat":"vegetable","s":"100g","k":92,"p":2.2,"c":9.1,"f":4.8,"fi":3.7,"ca":22,"fe":0.9,"src":"local","kw":["uchhe","bitter gourd","karela","bhaja","fry","bengali","tarkari"]},
  {"id":10024,"en":"Palong Shaak Bhaja","bn":"পালং শাক ভাজা","cat":"vegetable","s":"100g","k":66,"p":3.5,"c":5.8,"f":2.8,"fi":3.4,"ca":108,"fe":2.8,"src":"local","kw":["palong shaak","spinach","bhaja","stir fry","bengali","shaak","tarkari"]},
  {"id":10025,"en":"Data Chorchori","bn":"ডাটা চচ্চড়ি","cat":"vegetable","s":"100g","k":70,"p":2.4,"c":8.7,"f":2.5,"fi":3.6,"ca":62,"fe":1.4,"src":"local","kw":["data","stem vegetable","chorchori","bengali","tarkari"]},
]

with open('assets/data/food_master_v7_2.json', encoding='utf-8') as f:
    data = json.load(f)

existing_ids  = {item.get('id') for item in data}
existing_names = {item.get('en','').strip().lower() for item in data}

skipped = []
to_add  = []
for item in new_items:
    if item['id'] in existing_ids:
        skipped.append(f"  ID conflict: {item['id']} {item['en']}")
    elif item['en'].strip().lower() in existing_names:
        skipped.append(f"  Name exists: {item['en']}")
    else:
        to_add.append(item)

if skipped:
    print('Skipped (already exist):')
    for s in skipped:
        print(s)

data.extend(to_add)

with open('assets/data/food_master_v7_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

veg_total = sum(1 for item in data if item.get('cat') == 'vegetable')
print(f'Added {len(to_add)} items  |  Skipped {len(skipped)}  |  Total items {len(data)}  |  Vegetable total {veg_total}')
