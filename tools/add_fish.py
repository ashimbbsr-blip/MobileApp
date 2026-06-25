import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# All prawn/chingri items mapped to "fish" (no separate seafood chip in the UI)
new_items = [
  # ── Rohu ─────────────────────────────────────────────────────────────────────
  {"id":4001,"en":"Rohu Fish Curry","bn":"রুই মাছের ঝোল","cat":"fish","s":"100g","k":145,"p":18.5,"c":2.0,"f":7.0,"fi":0.2,"ca":28,"fe":1.1,"src":"local","kw":["rohu","rui","rui macher jhol","fish curry","bengali","mach"]},
  {"id":4002,"en":"Rohu Kalia","bn":"রুই কালিয়া","cat":"fish","s":"100g","k":180,"p":19.0,"c":4.0,"f":10.0,"fi":0.4,"ca":30,"fe":1.2,"src":"local","kw":["rohu","rui","kalia","kalia curry","bengali","mach"]},
  {"id":4003,"en":"Rohu Fry","bn":"রুই ভাজা","cat":"fish","s":"100g","k":210,"p":21.0,"c":1.0,"f":13.0,"fi":0.1,"ca":29,"fe":1.1,"src":"local","kw":["rohu","rui","fry","bhaja","fried fish","bengali","mach"]},
  {"id":4004,"en":"Rohu Tok","bn":"রুই টক","cat":"fish","s":"100g","k":155,"p":18.0,"c":5.0,"f":6.5,"fi":0.5,"ca":28,"fe":1.0,"src":"local","kw":["rohu","rui","tok","sour","tamarind","bengali","mach"]},
  {"id":4005,"en":"Muri Ghonto","bn":"মুড়ি ঘন্ট","cat":"fish","s":"100g","k":190,"p":10.0,"c":20.0,"f":7.0,"fi":1.2,"ca":20,"fe":1.5,"src":"local","kw":["muri ghonto","fish head","rohu","rui","bengali","mach"]},
  # ── Catla ────────────────────────────────────────────────────────────────────
  {"id":4006,"en":"Catla Fish Curry","bn":"কাতলা মাছের ঝোল","cat":"fish","s":"100g","k":155,"p":19.0,"c":2.0,"f":8.0,"fi":0.2,"ca":30,"fe":1.2,"src":"local","kw":["catla","katla","katla macher jhol","fish curry","bengali","mach"]},
  {"id":4007,"en":"Catla Kalia","bn":"কাতলা কালিয়া","cat":"fish","s":"100g","k":190,"p":19.0,"c":4.0,"f":11.0,"fi":0.3,"ca":30,"fe":1.3,"src":"local","kw":["catla","katla","kalia","bengali","mach"]},
  {"id":4008,"en":"Catla Fry","bn":"কাতলা ভাজা","cat":"fish","s":"100g","k":215,"p":21.0,"c":1.0,"f":13.0,"fi":0.1,"ca":30,"fe":1.2,"src":"local","kw":["catla","katla","fry","bhaja","fried fish","bengali","mach"]},
  {"id":4009,"en":"Catla Korma","bn":"কাতলা কোরমা","cat":"fish","s":"100g","k":200,"p":18.0,"c":4.0,"f":12.0,"fi":0.3,"ca":32,"fe":1.2,"src":"local","kw":["catla","katla","korma","bengali","mach"]},
  {"id":4010,"en":"Catla Macher Matha Dal","bn":"কাতলা মাছের মাথা ডাল","cat":"fish","s":"100g","k":175,"p":10.0,"c":15.0,"f":8.0,"fi":2.0,"ca":35,"fe":1.8,"src":"local","kw":["catla","katla","macher matha","fish head dal","bengali","mach"]},
  # ── Hilsa / Ilish ────────────────────────────────────────────────────────────
  {"id":4011,"en":"Hilsa Curry","bn":"ইলিশ মাছের ঝোল","cat":"fish","s":"100g","k":240,"p":20.0,"c":1.0,"f":17.0,"fi":0.0,"ca":32,"fe":1.5,"src":"local","kw":["hilsa","ilish","hilsa curry","bengali","mach","jhol"]},
  {"id":4012,"en":"Sorshe Ilish","bn":"সর্ষে ইলিশ","cat":"fish","s":"100g","k":255,"p":20.0,"c":2.0,"f":18.0,"fi":0.3,"ca":34,"fe":1.6,"src":"local","kw":["hilsa","ilish","sorshe","mustard hilsa","bengali","mach"]},
  {"id":4013,"en":"Doi Ilish","bn":"দই ইলিশ","cat":"fish","s":"100g","k":250,"p":19.0,"c":3.0,"f":18.0,"fi":0.2,"ca":38,"fe":1.5,"src":"local","kw":["hilsa","ilish","doi","yoghurt","bengali","mach"]},
  {"id":4014,"en":"Ilish Bhapa","bn":"ইলিশ ভাপা","cat":"fish","s":"100g","k":260,"p":20.0,"c":2.0,"f":19.0,"fi":0.2,"ca":34,"fe":1.6,"src":"local","kw":["hilsa","ilish","bhapa","steamed","mustard","bengali","mach"]},
  {"id":4015,"en":"Ilish Paturi","bn":"ইলিশ পাতুরি","cat":"fish","s":"100g","k":265,"p":20.0,"c":2.0,"f":19.5,"fi":0.2,"ca":34,"fe":1.7,"src":"local","kw":["hilsa","ilish","paturi","banana leaf","bengali","mach"]},
  # ── Pabda / Tangra / Small Fish ──────────────────────────────────────────────
  {"id":4016,"en":"Pabda Jhal","bn":"পাবদা ঝাল","cat":"fish","s":"100g","k":135,"p":18.0,"c":2.0,"f":6.0,"fi":0.2,"ca":25,"fe":1.0,"src":"local","kw":["pabda","jhal","spicy fish","bengali","mach"]},
  {"id":4017,"en":"Pabda Curry","bn":"পাবদা মাছের ঝোল","cat":"fish","s":"100g","k":130,"p":18.0,"c":2.0,"f":6.0,"fi":0.2,"ca":25,"fe":1.0,"src":"local","kw":["pabda","fish curry","bengali","mach","jhol"]},
  {"id":4018,"en":"Tangra Jhal","bn":"ট্যাংরা ঝাল","cat":"fish","s":"100g","k":140,"p":18.0,"c":2.0,"f":6.5,"fi":0.2,"ca":25,"fe":1.0,"src":"local","kw":["tangra","jhal","spicy fish","bengali","mach"]},
  {"id":4019,"en":"Tangra Curry","bn":"ট্যাংরা মাছের ঝোল","cat":"fish","s":"100g","k":135,"p":18.0,"c":2.0,"f":6.0,"fi":0.2,"ca":25,"fe":1.0,"src":"local","kw":["tangra","fish curry","bengali","mach","jhol"]},
  {"id":4020,"en":"Punti Fish Curry","bn":"পুঁটি মাছের ঝোল","cat":"fish","s":"100g","k":125,"p":17.0,"c":2.0,"f":5.5,"fi":0.2,"ca":40,"fe":1.5,"src":"local","kw":["punti","small fish","fish curry","bengali","mach","jhol"]},
  # ── Other Bengali freshwater fish ─────────────────────────────────────────────
  {"id":4021,"en":"Mourala Bhaja","bn":"মৌরলা ভাজা","cat":"fish","s":"100g","k":185,"p":20.0,"c":1.0,"f":10.0,"fi":0.1,"ca":55,"fe":2.0,"src":"local","kw":["mourala","mola","small fish","bhaja","fried fish","bengali","mach"]},
  {"id":4022,"en":"Koi Fish Curry","bn":"কই মাছের ঝোল","cat":"fish","s":"100g","k":145,"p":18.0,"c":2.0,"f":7.0,"fi":0.2,"ca":28,"fe":1.2,"src":"local","kw":["koi","climbing perch","fish curry","bengali","mach","jhol"]},
  {"id":4023,"en":"Magur Curry","bn":"মাগুর মাছের ঝোল","cat":"fish","s":"100g","k":140,"p":18.0,"c":2.0,"f":6.5,"fi":0.2,"ca":28,"fe":1.2,"src":"local","kw":["magur","catfish","fish curry","bengali","mach","jhol"]},
  {"id":4024,"en":"Shing Fish Curry","bn":"শিং মাছের ঝোল","cat":"fish","s":"100g","k":145,"p":18.0,"c":2.0,"f":7.0,"fi":0.2,"ca":30,"fe":1.3,"src":"local","kw":["shing","stinging catfish","fish curry","bengali","mach","jhol"]},
  {"id":4025,"en":"Shol Fish Curry","bn":"শোল মাছের ঝোল","cat":"fish","s":"100g","k":150,"p":19.0,"c":2.0,"f":7.0,"fi":0.2,"ca":28,"fe":1.2,"src":"local","kw":["shol","snakehead","fish curry","bengali","mach","jhol"]},
  # ── Chital / Boal / Other ─────────────────────────────────────────────────────
  {"id":4026,"en":"Chital Muitha","bn":"চিতল মুইঠ্যা","cat":"fish","s":"100g","k":190,"p":18.0,"c":6.0,"f":10.0,"fi":0.6,"ca":28,"fe":1.4,"src":"local","kw":["chital","chitol","muitha","fish dumpling","bengali","mach"]},
  {"id":4027,"en":"Chital Kalia","bn":"চিতল কালিয়া","cat":"fish","s":"100g","k":195,"p":18.0,"c":4.0,"f":11.0,"fi":0.4,"ca":28,"fe":1.4,"src":"local","kw":["chital","chitol","kalia","bengali","mach"]},
  {"id":4028,"en":"Boal Curry","bn":"বোয়াল মাছের ঝোল","cat":"fish","s":"100g","k":150,"p":18.0,"c":2.0,"f":8.0,"fi":0.2,"ca":25,"fe":1.1,"src":"local","kw":["boal","wallago attu","fish curry","bengali","mach","jhol"]},
  {"id":4029,"en":"Parshe Jhal","bn":"পার্শে ঝাল","cat":"fish","s":"100g","k":140,"p":18.0,"c":2.0,"f":6.0,"fi":0.2,"ca":24,"fe":1.0,"src":"local","kw":["parshe","mullet","jhal","spicy fish","bengali","mach"]},
  {"id":4030,"en":"Topse Fry","bn":"টপসে ভাজা","cat":"fish","s":"100g","k":220,"p":20.0,"c":6.0,"f":12.0,"fi":0.4,"ca":26,"fe":1.2,"src":"local","kw":["topse","mango fish","bhaja","fried fish","bengali","mach"]},
  # ── Bhetki / Pomfret ─────────────────────────────────────────────────────────
  {"id":4031,"en":"Bhetki Fry","bn":"ভেটকি ফ্রাই","cat":"fish","s":"100g","k":180,"p":22.0,"c":4.0,"f":8.0,"fi":0.3,"ca":22,"fe":0.8,"src":"local","kw":["bhetki","barramundi","fry","bhaja","fried fish","bengali","mach"]},
  {"id":4032,"en":"Bhetki Paturi","bn":"ভেটকি পাতুরি","cat":"fish","s":"100g","k":190,"p":22.0,"c":2.0,"f":10.0,"fi":0.2,"ca":22,"fe":0.8,"src":"local","kw":["bhetki","barramundi","paturi","banana leaf","bengali","mach"]},
  {"id":4033,"en":"Bhetki Curry","bn":"ভেটকি ঝোল","cat":"fish","s":"100g","k":135,"p":22.0,"c":2.0,"f":4.0,"fi":0.2,"ca":22,"fe":0.8,"src":"local","kw":["bhetki","barramundi","fish curry","bengali","mach","jhol"]},
  {"id":4034,"en":"Pomfret Curry","bn":"পমফ্রেট কারি","cat":"fish","s":"100g","k":145,"p":21.0,"c":2.0,"f":6.0,"fi":0.2,"ca":24,"fe":0.9,"src":"local","kw":["pomfret","pamplet","fish curry","bengali","mach"]},
  {"id":4035,"en":"Pomfret Fry","bn":"পমফ্রেট ভাজা","cat":"fish","s":"100g","k":205,"p":22.0,"c":2.0,"f":12.0,"fi":0.2,"ca":24,"fe":0.9,"src":"local","kw":["pomfret","pamplet","fry","bhaja","fried fish","bengali","mach"]},
  # ── Prawns / Shrimp (Chingri) — mapped to fish chip ──────────────────────────
  {"id":4036,"en":"Chingri Malaikari","bn":"চিংড়ি মালাইকারি","cat":"fish","s":"100g","k":190,"p":18.0,"c":4.0,"f":11.0,"fi":0.2,"ca":45,"fe":1.1,"src":"local","kw":["chingri","prawn","shrimp","malai","coconut milk","bengali","mach"]},
  {"id":4037,"en":"Golda Chingri Malaikari","bn":"গলদা চিংড়ি মালাইকারি","cat":"fish","s":"100g","k":200,"p":19.0,"c":4.0,"f":12.0,"fi":0.2,"ca":46,"fe":1.2,"src":"local","kw":["golda chingri","lobster prawn","malai","coconut milk","bengali","mach"]},
  {"id":4038,"en":"Chingri Bhapa","bn":"চিংড়ি ভাপা","cat":"fish","s":"100g","k":125,"p":21.0,"c":2.0,"f":3.0,"fi":0.1,"ca":42,"fe":1.0,"src":"local","kw":["chingri","prawn","shrimp","bhapa","steamed","mustard","bengali","mach"]},
  {"id":4039,"en":"Chingri Posto","bn":"চিংড়ি পোস্ত","cat":"fish","s":"100g","k":210,"p":18.0,"c":4.0,"f":14.0,"fi":1.0,"ca":60,"fe":1.3,"src":"local","kw":["chingri","prawn","shrimp","posto","poppy seed","bengali","mach"]},
  {"id":4040,"en":"Chingri Paturi","bn":"চিংড়ি পাতুরি","cat":"fish","s":"100g","k":140,"p":21.0,"c":2.0,"f":5.0,"fi":0.2,"ca":45,"fe":1.1,"src":"local","kw":["chingri","prawn","shrimp","paturi","banana leaf","bengali","mach"]},
  {"id":4041,"en":"Lau Chingri","bn":"লাউ চিংড়ি","cat":"fish","s":"100g","k":110,"p":10.0,"c":5.0,"f":6.0,"fi":1.0,"ca":35,"fe":0.8,"src":"local","kw":["chingri","prawn","shrimp","lau","bottle gourd","bengali","mach"]},
  {"id":4042,"en":"Mocha Chingri","bn":"মোচা চিংড়ি","cat":"fish","s":"100g","k":145,"p":12.0,"c":8.0,"f":8.0,"fi":2.0,"ca":38,"fe":1.0,"src":"local","kw":["chingri","prawn","shrimp","mocha","banana flower","bengali","mach"]},
  {"id":4043,"en":"Prawn Curry","bn":"চিংড়ি কারি","cat":"fish","s":"100g","k":130,"p":21.0,"c":2.0,"f":4.0,"fi":0.2,"ca":42,"fe":1.0,"src":"local","kw":["chingri","prawn","shrimp","curry","bengali","mach"]},
  {"id":4044,"en":"Tiger Prawn Curry","bn":"টাইগার প্রন কারি","cat":"fish","s":"100g","k":135,"p":22.0,"c":2.0,"f":4.0,"fi":0.2,"ca":44,"fe":1.0,"src":"local","kw":["tiger prawn","tiger shrimp","chingri","curry","bengali","mach"]},
  {"id":4045,"en":"Prawn Fry","bn":"চিংড়ি ভাজা","cat":"fish","s":"100g","k":180,"p":22.0,"c":2.0,"f":8.0,"fi":0.1,"ca":42,"fe":1.0,"src":"local","kw":["chingri","prawn","shrimp","fry","bhaja","bengali","mach"]},
  # ── Marine / Other fish ───────────────────────────────────────────────────────
  {"id":4046,"en":"Mackerel Curry","bn":"ম্যাকারেল কারি","cat":"fish","s":"100g","k":205,"p":20.0,"c":2.0,"f":12.0,"fi":0.2,"ca":25,"fe":1.1,"src":"local","kw":["mackerel","bangda","fish curry","mach"]},
  {"id":4047,"en":"Sardine Curry","bn":"সার্ডিন কারি","cat":"fish","s":"100g","k":210,"p":21.0,"c":2.0,"f":13.0,"fi":0.2,"ca":40,"fe":1.8,"src":"local","kw":["sardine","sardines","fish curry","mach"]},
  {"id":4048,"en":"Seer Fish Curry","bn":"সুরমাই কারি","cat":"fish","s":"100g","k":170,"p":22.0,"c":2.0,"f":8.0,"fi":0.2,"ca":25,"fe":1.0,"src":"local","kw":["seer fish","surmai","king fish","fish curry","mach"]},
  {"id":4049,"en":"Tuna Curry","bn":"টুনা কারি","cat":"fish","s":"100g","k":165,"p":24.0,"c":2.0,"f":6.0,"fi":0.2,"ca":20,"fe":1.0,"src":"local","kw":["tuna","fish curry","mach"]},
  {"id":4050,"en":"Salmon Curry","bn":"স্যালমন কারি","cat":"fish","s":"100g","k":220,"p":22.0,"c":2.0,"f":14.0,"fi":0.2,"ca":22,"fe":0.9,"src":"local","kw":["salmon","fish curry","mach"]},
]

with open('assets/data/food_master_v7_2.json', encoding='utf-8') as f:
    data = json.load(f)

existing_ids = {item.get('id') for item in data}
to_add = [item for item in new_items if item['id'] not in existing_ids]
data.extend(to_add)

with open('assets/data/food_master_v7_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

print('Added', len(to_add), 'items. Total:', len(data))
fish_total = sum(1 for item in data if item.get('cat') == 'fish')
print('Fish category total:', fish_total)
