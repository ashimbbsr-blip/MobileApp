import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

new_items = [
  {"id":12001,"en":"Rosogolla","bn":"রসগোল্লা","cat":"sweet","s":"100g","k":119,"p":1.4,"c":25.8,"f":1.7,"fi":0.0,"ca":57,"fe":0.1,"src":"local","kw":["rosogolla","rasgulla","chhena","chenna","bengali sweet","mishti","doi"]},
  {"id":12002,"en":"Rajbhog","bn":"রাজভোগ","cat":"sweet","s":"100g","k":250,"p":6.0,"c":42.0,"f":6.0,"fi":0.0,"ca":180,"fe":0.3,"src":"local","kw":["rajbhog","rajbhog sweet","chhena","bengali sweet","mishti"]},
  {"id":12003,"en":"Pantua","bn":"পান্তুয়া","cat":"sweet","s":"100g","k":385,"p":6.2,"c":55.0,"f":15.8,"fi":0.1,"ca":148,"fe":0.8,"src":"local","kw":["pantua","gulab jamun","chhena","bengali sweet","mishti","fried"]},
  {"id":12004,"en":"Langcha","bn":"ল্যাংচা","cat":"sweet","s":"100g","k":355,"p":6.1,"c":50.2,"f":13.6,"fi":0.2,"ca":145,"fe":0.7,"src":"local","kw":["langcha","chhena","bengali sweet","mishti","shaktigarh"]},
  {"id":12005,"en":"Chomchom","bn":"চমচম","cat":"sweet","s":"100g","k":310,"p":6.4,"c":48.5,"f":9.5,"fi":0.0,"ca":165,"fe":0.5,"src":"local","kw":["chomchom","chamcham","chhena","bengali sweet","mishti","porabari"]},
  {"id":12006,"en":"Ledikeni","bn":"লেডিকেনি","cat":"sweet","s":"100g","k":340,"p":5.8,"c":52.0,"f":11.5,"fi":0.1,"ca":140,"fe":0.6,"src":"local","kw":["ledikeni","chhena","bengali sweet","mishti","kolkata"]},
  {"id":12007,"en":"Mihidana","bn":"মিহিদানা","cat":"sweet","s":"100g","k":415,"p":6.2,"c":74.0,"f":10.4,"fi":0.6,"ca":32,"fe":1.0,"src":"local","kw":["mihidana","burdwan","bengali sweet","mishti","besan"]},
  {"id":12008,"en":"Sitabhog","bn":"সীতাভোগ","cat":"sweet","s":"100g","k":430,"p":5.5,"c":78.5,"f":10.2,"fi":0.5,"ca":28,"fe":0.8,"src":"local","kw":["sitabhog","burdwan","bengali sweet","mishti","rice flour"]},
  {"id":12009,"en":"Kheer Kadam","bn":"ক্ষীর কদম","cat":"sweet","s":"100g","k":365,"p":7.5,"c":52.0,"f":14.0,"fi":0.0,"ca":210,"fe":0.4,"src":"local","kw":["kheer kadam","khir kadam","chhena","bengali sweet","mishti","khoya"]},
  {"id":12010,"en":"Chhanar Jilipi","bn":"ছানার জিলিপি","cat":"sweet","s":"100g","k":375,"p":7.0,"c":52.0,"f":15.0,"fi":0.0,"ca":155,"fe":0.7,"src":"local","kw":["chhanar jilipi","chhana jilipi","jalebi","chhena","bengali sweet","mishti"]},
  {"id":12011,"en":"Sandesh","bn":"সন্দেশ","cat":"sweet","s":"100g","k":285,"p":9.0,"c":35.0,"f":12.0,"fi":0.0,"ca":220,"fe":0.3,"src":"local","kw":["sandesh","chhena","bengali sweet","mishti","kolkata"]},
  {"id":12012,"en":"Nolen Gur Sandesh","bn":"নলেন গুড়ের সন্দেশ","cat":"sweet","s":"100g","k":295,"p":8.8,"c":38.0,"f":11.0,"fi":0.0,"ca":215,"fe":0.5,"src":"local","kw":["nolen gur sandesh","nolen gur","date jaggery","chhena","bengali sweet","mishti","winter"]},
  {"id":12013,"en":"Rasmalai","bn":"রসমালাই","cat":"sweet","s":"100g","k":185,"p":6.0,"c":24.0,"f":7.0,"fi":0.0,"ca":180,"fe":0.2,"src":"local","kw":["rasmalai","rosmalai","chhena","bengali sweet","mishti","milk"]},
  {"id":12014,"en":"Mishti Doi","bn":"মিষ্টি দই","cat":"sweet","s":"100g","k":168,"p":4.1,"c":26.0,"f":5.2,"fi":0.0,"ca":149,"fe":0.1,"src":"local","kw":["mishti doi","sweet yogurt","doi","bengali sweet","mishti"]},
  {"id":12015,"en":"Payesh","bn":"পায়েস","cat":"sweet","s":"100g","k":146,"p":3.4,"c":24.0,"f":4.2,"fi":0.0,"ca":110,"fe":0.2,"src":"local","kw":["payesh","kheer","rice pudding","bengali sweet","mishti"]},
  {"id":12016,"en":"Patishapta","bn":"পাটিসাপটা","cat":"sweet","s":"100g","k":255,"p":5.0,"c":38.0,"f":9.0,"fi":0.8,"ca":75,"fe":0.7,"src":"local","kw":["patishapta","pitha","crepe","bengali sweet","mishti","winter"]},
  {"id":12017,"en":"Patishapta Nolen Gur","bn":"নলেন গুড় পাটিসাপটা","cat":"sweet","s":"100g","k":268,"p":4.8,"c":42.0,"f":8.5,"fi":0.8,"ca":74,"fe":0.7,"src":"local","kw":["patishapta","nolen gur","date jaggery","pitha","bengali sweet","mishti","winter"]},
  {"id":12018,"en":"Chhena Poda","bn":"ছেনা পোড়া","cat":"sweet","s":"100g","k":315,"p":10.5,"c":32.0,"f":15.0,"fi":0.0,"ca":260,"fe":0.5,"src":"local","kw":["chhena poda","chenna poda","baked chhena","odia sweet","mishti"]},
  {"id":12019,"en":"Rasabali","bn":"রসবালি","cat":"sweet","s":"100g","k":295,"p":8.0,"c":36.0,"f":13.0,"fi":0.0,"ca":230,"fe":0.4,"src":"local","kw":["rasabali","chhena","odia sweet","mishti","khoya"]},
  {"id":12020,"en":"Chhena Jhili","bn":"ছেনা ঝিলি","cat":"sweet","s":"100g","k":350,"p":8.0,"c":46.0,"f":15.0,"fi":0.0,"ca":220,"fe":0.5,"src":"local","kw":["chhena jhili","chhena","odia sweet","mishti"]},
  {"id":12021,"en":"Chhena Gaja","bn":"ছেনা গজা","cat":"sweet","s":"100g","k":390,"p":8.5,"c":52.0,"f":16.0,"fi":0.0,"ca":210,"fe":0.5,"src":"local","kw":["chhena gaja","chhena","odia sweet","mishti","kendrapara"]},
  {"id":12022,"en":"Khaja","bn":"খাজা","cat":"sweet","s":"100g","k":475,"p":5.0,"c":62.0,"f":23.0,"fi":0.8,"ca":18,"fe":1.2,"src":"local","kw":["khaja","flaky sweet","odia sweet","mishti","puri"]},
  {"id":12023,"en":"Khira Gaja","bn":"খিরা গজা","cat":"sweet","s":"100g","k":410,"p":7.0,"c":58.0,"f":16.0,"fi":0.2,"ca":160,"fe":0.5,"src":"local","kw":["khira gaja","kheer","chhena","sweet","mishti"]},
  {"id":12024,"en":"Arisa Pitha","bn":"আরিসা পিঠা","cat":"sweet","s":"100g","k":390,"p":4.0,"c":64.0,"f":13.0,"fi":1.0,"ca":25,"fe":0.8,"src":"local","kw":["arisa pitha","rice cake","odia pitha","sweet","mishti"]},
  {"id":12025,"en":"Manda Pitha","bn":"মান্দা পিঠা","cat":"sweet","s":"100g","k":260,"p":4.5,"c":46.0,"f":6.0,"fi":1.2,"ca":45,"fe":0.6,"src":"local","kw":["manda pitha","steamed dumpling","pitha","sweet","mishti","bengali"]},
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
        skipped.append(f"  ID conflict  : {item['id']}  {item['en']}")
    elif en_lower in existing_names:
        skipped.append(f"  Name exists  : {item['en']}")
    else:
        to_add.append(item)

data.extend(to_add)

with open('assets/data/food_master_v7_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

sweet_total = sum(1 for item in data if item.get('cat') == 'sweet')
print(f'Added {len(to_add)}  |  Skipped {len(skipped)}  |  Total items {len(data)}  |  Sweet total {sweet_total}')
if skipped:
    print('Skipped:')
    for s in skipped:
        print(s)
