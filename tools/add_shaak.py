import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

new_items = [
  {"id":11001,"en":"Palong Shaak Bhaja","bn":"পালং শাক ভাজা","cat":"shaak","s":"100g","k":66,"p":3.5,"c":5.8,"f":2.8,"fi":3.4,"ca":108,"fe":2.8,"src":"local","kw":["palong shaak","spinach","bhaja","stir fry","leafy","shaak","greens"]},
  {"id":11002,"en":"Lal Shaak Bhaja","bn":"লাল শাক ভাজা","cat":"shaak","s":"100g","k":58,"p":2.7,"c":6.2,"f":2.1,"fi":3.1,"ca":210,"fe":3.5,"src":"local","kw":["lal shaak","red amaranth","bhaja","leafy","shaak","greens"]},
  {"id":11003,"en":"Note Shaak Bhaja","bn":"নটে শাক ভাজা","cat":"shaak","s":"100g","k":61,"p":2.9,"c":6.8,"f":2.0,"fi":3.6,"ca":185,"fe":3.2,"src":"local","kw":["note shaak","note","amaranth","bhaja","leafy","shaak","greens"]},
  {"id":11004,"en":"Kolmi Shaak Bhaja","bn":"কলমি শাক ভাজা","cat":"shaak","s":"100g","k":52,"p":2.5,"c":5.4,"f":1.9,"fi":2.8,"ca":120,"fe":2.1,"src":"local","kw":["kolmi shaak","water spinach","morning glory","bhaja","leafy","shaak","greens"]},
  {"id":11005,"en":"Pui Shaak Chorchori","bn":"পুঁই শাক চচ্চড়ি","cat":"shaak","s":"100g","k":58,"p":2.6,"c":6.9,"f":2.1,"fi":3.9,"ca":82,"fe":2.2,"src":"local","kw":["pui shaak","malabar spinach","chorchori","leafy","shaak","greens"]},
  {"id":11006,"en":"Pui Shaak Ghonto","bn":"পুঁই শাক ঘন্ট","cat":"shaak","s":"100g","k":74,"p":2.8,"c":8.1,"f":3.1,"fi":4.1,"ca":88,"fe":2.3,"src":"local","kw":["pui shaak","malabar spinach","ghonto","leafy","shaak","greens"]},
  {"id":11007,"en":"Paat Shaak Bhaja","bn":"পাট শাক ভাজা","cat":"shaak","s":"100g","k":63,"p":3.1,"c":6.3,"f":2.2,"fi":3.7,"ca":145,"fe":3.0,"src":"local","kw":["paat shaak","jute leaves","bhaja","leafy","shaak","greens"]},
  {"id":11008,"en":"Methi Shaak Bhaja","bn":"মেথি শাক ভাজা","cat":"shaak","s":"100g","k":69,"p":4.1,"c":7.2,"f":2.3,"fi":4.2,"ca":175,"fe":3.8,"src":"local","kw":["methi","fenugreek leaves","bhaja","leafy","shaak","greens"]},
  {"id":11009,"en":"Sorshe Shaak Bhaja","bn":"সর্ষে শাক ভাজা","cat":"shaak","s":"100g","k":64,"p":3.7,"c":6.4,"f":2.1,"fi":3.8,"ca":118,"fe":2.5,"src":"local","kw":["sorshe shaak","mustard greens","bhaja","leafy","shaak","greens"]},
  {"id":11010,"en":"Lau Shaak Bhaja","bn":"লাউ শাক ভাজা","cat":"shaak","s":"100g","k":48,"p":2.1,"c":5.6,"f":1.7,"fi":2.9,"ca":96,"fe":1.8,"src":"local","kw":["lau shaak","bottle gourd leaves","bhaja","leafy","shaak","greens"]},
  {"id":11011,"en":"Kumro Shaak Bhaja","bn":"কুমড়ো শাক ভাজা","cat":"shaak","s":"100g","k":55,"p":2.4,"c":6.1,"f":1.9,"fi":3.2,"ca":104,"fe":2.0,"src":"local","kw":["kumro shaak","pumpkin leaves","bhaja","leafy","shaak","greens"]},
  {"id":11012,"en":"Data Shaak Chorchori","bn":"ডাটা শাক চচ্চড়ি","cat":"shaak","s":"100g","k":62,"p":2.8,"c":7.0,"f":2.1,"fi":3.4,"ca":132,"fe":2.2,"src":"local","kw":["data shaak","stem vegetable","chorchori","leafy","shaak","greens"]},
  {"id":11013,"en":"Kochu Shaak Chorchori","bn":"কচু শাক চচ্চড়ি","cat":"shaak","s":"100g","k":82,"p":2.6,"c":10.2,"f":3.0,"fi":4.8,"ca":138,"fe":2.5,"src":"local","kw":["kochu shaak","taro leaves","colocasia","chorchori","leafy","shaak","greens"]},
  {"id":11014,"en":"Kochu Shaak Ghonto","bn":"কচু শাক ঘন্ট","cat":"shaak","s":"100g","k":95,"p":2.9,"c":11.8,"f":3.6,"fi":5.0,"ca":145,"fe":2.7,"src":"local","kw":["kochu shaak","taro leaves","colocasia","ghonto","leafy","shaak","greens"]},
  {"id":11015,"en":"Ranga Alur Shaak Bhaja","bn":"রাঙা আলুর শাক ভাজা","cat":"shaak","s":"100g","k":57,"p":2.9,"c":6.1,"f":1.8,"fi":3.3,"ca":115,"fe":2.1,"src":"local","kw":["ranga alur shaak","sweet potato leaves","bhaja","leafy","shaak","greens"]},
  {"id":11016,"en":"Sojne Pata Bhaja","bn":"সজনে পাতা ভাজা","cat":"shaak","s":"100g","k":72,"p":5.2,"c":7.4,"f":2.3,"fi":4.5,"ca":240,"fe":4.2,"src":"local","kw":["sojne pata","moringa","drumstick leaves","bhaja","leafy","shaak","greens"]},
  {"id":11017,"en":"Neem Begun","bn":"নিম বেগুন","cat":"shaak","s":"100g","k":88,"p":2.2,"c":8.5,"f":5.2,"fi":3.1,"ca":34,"fe":1.0,"src":"local","kw":["neem","begun","brinjal","neem leaves","bengali","shaak"]},
  {"id":11018,"en":"Neem Pata Bhaja","bn":"নিম পাতা ভাজা","cat":"shaak","s":"100g","k":78,"p":3.1,"c":7.2,"f":4.0,"fi":3.8,"ca":85,"fe":1.7,"src":"local","kw":["neem pata","neem leaves","bhaja","bitter","leafy","shaak","greens"]},
  {"id":11019,"en":"Mixed Shaak Bhaja","bn":"মিশ্র শাক ভাজা","cat":"shaak","s":"100g","k":60,"p":3.0,"c":6.4,"f":2.0,"fi":3.6,"ca":140,"fe":2.8,"src":"local","kw":["mixed shaak","mixed greens","bhaja","leafy","shaak","greens"]},
  {"id":11020,"en":"Choddo Shaak","bn":"চোদ্দো শাক","cat":"shaak","s":"100g","k":68,"p":3.3,"c":7.0,"f":2.3,"fi":4.2,"ca":165,"fe":3.2,"src":"local","kw":["choddo shaak","fourteen greens","poila boisakh","bengali","shaak","greens","mixed"]},
  # 11021 — different English name from 11018 but same Bengali + same nutrition; include as alias
  {"id":11021,"en":"Neem Leaf Fry","bn":"নিম পাতা ভাজা","cat":"shaak","s":"100g","k":78,"p":3.1,"c":7.2,"f":4.0,"fi":3.8,"ca":85,"fe":1.7,"src":"local","kw":["neem","neem leaf","fry","bhaja","bitter","leafy","shaak","greens"]},
  # 11023 — Neem Begun under vegetable (user specified cat:vegetable)
  {"id":11023,"en":"Neem Begun Tarkari","bn":"নিম বেগুন","cat":"vegetable","s":"100g","k":88,"p":2.2,"c":8.5,"f":5.2,"fi":3.1,"ca":34,"fe":1.0,"src":"local","kw":["neem","begun","brinjal","eggplant","neem leaves","bengali","vegetable","tarkari"]},
]

with open('assets/data/food_master_v7_2.json', encoding='utf-8') as f:
    data = json.load(f)

existing_ids   = {item.get('id') for item in data}
existing_names = {item.get('en', '').strip().lower() for item in data}

skipped = []
to_add  = []
for item in new_items:
    en_lower = item['en'].strip().lower()
    if item['id'] in existing_ids:
        skipped.append(f"  ID conflict     : {item['id']}  {item['en']}")
    elif en_lower in existing_names:
        # Rename slightly to make it unique in English while keeping Bengali identical
        skipped.append(f"  Name exists     : {item['en']}")
    else:
        to_add.append(item)

if skipped:
    print('Skipped:')
    for s in skipped:
        print(s)

data.extend(to_add)

with open('assets/data/food_master_v7_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

shaak_total = sum(1 for item in data if item.get('cat') == 'shaak')
veg_total   = sum(1 for item in data if item.get('cat') == 'vegetable')
print(f'Added {len(to_add)}  |  Skipped {len(skipped)}  |  Total {len(data)}  |  shaak={shaak_total}  vegetable={veg_total}')
