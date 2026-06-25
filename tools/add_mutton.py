import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

new_items = [
  {"id":3001,"en":"Mutton Kosha","bn":"মাটন কষা","cat":"meat","s":"100g","k":285,"p":18.5,"c":4.2,"f":21.0,"fi":0.8,"ca":18,"fe":2.3,"src":"local","kw":["mutton","kosha","gosht","bengali","khasi"]},
  {"id":3002,"en":"Bengali Mutton Curry","bn":"বাংলা মাটন ঝোল","cat":"meat","s":"100g","k":220,"p":17.0,"c":5.0,"f":14.5,"fi":0.9,"ca":16,"fe":2.1,"src":"local","kw":["mutton","curry","jhol","bengali","gosht","khasi"]},
  {"id":3003,"en":"Mutton Rezala","bn":"মাটন রেজালা","cat":"meat","s":"100g","k":250,"p":18.0,"c":3.8,"f":18.0,"fi":0.5,"ca":22,"fe":2.0,"src":"local","kw":["mutton","rezala","white curry","bengali","gosht"]},
  {"id":3004,"en":"Mutton Dak Bungalow","bn":"মাটন ডাকবাংলো","cat":"meat","s":"100g","k":240,"p":18.2,"c":4.0,"f":17.2,"fi":0.7,"ca":19,"fe":2.2,"src":"local","kw":["mutton","dak bungalow","colonial","bengali","gosht"]},
  {"id":3005,"en":"Mutton Chaap","bn":"মাটন চাপ","cat":"meat","s":"100g","k":310,"p":20.0,"c":4.0,"f":24.0,"fi":0.4,"ca":21,"fe":2.5,"src":"local","kw":["mutton","chaap","chap","street food","kolkata"]},
  {"id":3006,"en":"Mutton Kalia","bn":"মাটন কালিয়া","cat":"meat","s":"100g","k":265,"p":18.5,"c":5.0,"f":19.5,"fi":0.8,"ca":17,"fe":2.3,"src":"local","kw":["mutton","kalia","kalia curry","bengali","gosht","khasi"]},
  {"id":3007,"en":"Mutton Stew Bengali Style","bn":"বাংলা মাটন স্ট্যু","cat":"meat","s":"100g","k":180,"p":16.0,"c":6.0,"f":10.0,"fi":1.0,"ca":18,"fe":2.0,"src":"local","kw":["mutton","stew","bengali","light curry","gosht"]},
  {"id":3008,"en":"Mutton Pulao","bn":"মাটন পোলাও","cat":"meat","s":"100g","k":235,"p":10.0,"c":24.0,"f":11.0,"fi":1.1,"ca":14,"fe":1.6,"src":"local","kw":["mutton","pulao","polao","rice","bengali"]},
  {"id":3009,"en":"Kolkata Mutton Biryani","bn":"কলকাতা মাটন বিরিয়ানি","cat":"meat","s":"100g","k":250,"p":11.5,"c":27.0,"f":10.5,"fi":1.2,"ca":15,"fe":1.8,"src":"local","kw":["mutton","biryani","biriyani","kolkata","kolkata biryani","bengali"]},
  {"id":3010,"en":"Mutton Tehari","bn":"মাটন তেহারি","cat":"meat","s":"100g","k":245,"p":11.0,"c":25.0,"f":11.0,"fi":1.1,"ca":15,"fe":1.7,"src":"local","kw":["mutton","tehari","tehri","rice","bengali"]},
  {"id":3011,"en":"Mutton Liver Curry","bn":"মেটে কষা","cat":"meat","s":"100g","k":190,"p":20.0,"c":3.0,"f":10.0,"fi":0.4,"ca":8,"fe":6.0,"src":"local","kw":["mutton","liver","mete","offal","bengali","kosa"]},
  {"id":3012,"en":"Mutton Brain Curry","bn":"মগজ কারি","cat":"meat","s":"100g","k":170,"p":12.0,"c":2.0,"f":12.0,"fi":0.2,"ca":12,"fe":2.5,"src":"local","kw":["mutton","brain","mogoj","offal","bengali"]},
  {"id":3013,"en":"Mutton Heart Curry","bn":"মাটন হার্ট কারি","cat":"meat","s":"100g","k":180,"p":18.0,"c":3.0,"f":10.0,"fi":0.3,"ca":10,"fe":4.2,"src":"local","kw":["mutton","heart","offal","bengali","gosht"]},
  {"id":3014,"en":"Mutton Kidney Curry","bn":"কিডনি কারি","cat":"meat","s":"100g","k":175,"p":17.0,"c":3.0,"f":9.5,"fi":0.3,"ca":9,"fe":4.0,"src":"local","kw":["mutton","kidney","offal","bengali","gosht"]},
  {"id":3015,"en":"Mutton Bone Broth","bn":"মাটন স্যুপ","cat":"meat","s":"100g","k":55,"p":7.0,"c":0.5,"f":2.0,"fi":0.0,"ca":25,"fe":0.6,"src":"local","kw":["mutton","soup","broth","bone broth","bengali","gosht"]},
  {"id":3016,"en":"Aloo Diye Mutton","bn":"আলু দিয়ে মাটন","cat":"meat","s":"100g","k":210,"p":15.0,"c":9.0,"f":12.0,"fi":1.2,"ca":15,"fe":1.9,"src":"local","kw":["mutton","aloo","potato","bengali","gosht","khasi"]},
  {"id":3017,"en":"Mutton with Green Peas","bn":"মটর দিয়ে মাটন","cat":"meat","s":"100g","k":225,"p":16.0,"c":8.0,"f":14.0,"fi":1.8,"ca":20,"fe":2.1,"src":"local","kw":["mutton","matar","peas","green peas","bengali","gosht"]},
  {"id":3018,"en":"Mutton with Spinach","bn":"পালং মাটন","cat":"meat","s":"100g","k":200,"p":17.0,"c":4.0,"f":12.0,"fi":1.5,"ca":55,"fe":3.2,"src":"local","kw":["mutton","spinach","palak","paalang","bengali","gosht"]},
  {"id":3019,"en":"Saag Gosht","bn":"শাগ গোশত","cat":"meat","s":"100g","k":195,"p":17.0,"c":4.0,"f":11.5,"fi":1.6,"ca":58,"fe":3.3,"src":"local","kw":["mutton","saag","gosht","spinach","greens","bengali"]},
  {"id":3020,"en":"Mutton Cabbage Curry","bn":"বাঁধাকপি মাটন","cat":"meat","s":"100g","k":190,"p":15.0,"c":5.0,"f":11.0,"fi":1.4,"ca":30,"fe":2.0,"src":"local","kw":["mutton","cabbage","badhakobi","bengali","gosht"]},
  {"id":3021,"en":"Mutton Do Pyaza","bn":"মাটন দোপেয়াজা","cat":"meat","s":"100g","k":230,"p":17.0,"c":6.0,"f":15.0,"fi":1.0,"ca":18,"fe":2.1,"src":"local","kw":["mutton","do pyaza","dopiaza","onion","bengali","gosht"]},
  {"id":3022,"en":"Mutton Bhuna","bn":"মাটন ভুনা","cat":"meat","s":"100g","k":275,"p":19.0,"c":4.0,"f":20.0,"fi":0.5,"ca":16,"fe":2.3,"src":"local","kw":["mutton","bhuna","bhona","dry curry","gosht"]},
  {"id":3023,"en":"Mutton Rogan Josh","bn":"মাটন রগন জোশ","cat":"meat","s":"100g","k":240,"p":18.0,"c":4.0,"f":17.0,"fi":0.5,"ca":18,"fe":2.2,"src":"local","kw":["mutton","rogan josh","kashmiri","gosht"]},
  {"id":3024,"en":"Mutton Handi","bn":"মাটন হান্ডি","cat":"meat","s":"100g","k":235,"p":18.0,"c":4.0,"f":16.0,"fi":0.6,"ca":18,"fe":2.1,"src":"local","kw":["mutton","handi","handhi","pot curry","gosht"]},
  {"id":3025,"en":"Mutton Korma","bn":"মাটন কোরমা","cat":"meat","s":"100g","k":260,"p":17.0,"c":5.0,"f":19.0,"fi":0.6,"ca":20,"fe":2.0,"src":"local","kw":["mutton","korma","korma curry","mughal","gosht"]},
  {"id":3026,"en":"Mutton Nihari","bn":"মাটন নিহারি","cat":"meat","s":"100g","k":200,"p":16.0,"c":3.0,"f":13.0,"fi":0.4,"ca":16,"fe":2.2,"src":"local","kw":["mutton","nihari","nihari curry","slow cooked","gosht"]},
  {"id":3027,"en":"Mutton Haleem","bn":"মাটন হালিম","cat":"meat","s":"100g","k":180,"p":10.0,"c":18.0,"f":8.0,"fi":2.5,"ca":22,"fe":2.4,"src":"local","kw":["mutton","haleem","lentil","wheat","gosht"]},
  {"id":3028,"en":"Mutton Khichuri","bn":"মাটন খিচুড়ি","cat":"meat","s":"100g","k":185,"p":9.0,"c":20.0,"f":7.0,"fi":2.0,"ca":18,"fe":1.8,"src":"local","kw":["mutton","khichuri","khichdi","rice lentil","bengali","gosht"]},
  {"id":3029,"en":"Mutton Paya","bn":"মাটন পায়া","cat":"meat","s":"100g","k":110,"p":11.0,"c":1.0,"f":6.0,"fi":0.0,"ca":28,"fe":1.2,"src":"local","kw":["mutton","paya","trotters","feet","gosht","bone"]},
  {"id":3030,"en":"Mutton Keema","bn":"মাটন কিমা","cat":"meat","s":"100g","k":250,"p":18.0,"c":5.0,"f":18.0,"fi":0.8,"ca":16,"fe":2.3,"src":"local","kw":["mutton","keema","kima","minced","mince","gosht"]},
  {"id":3031,"en":"Keema Aloo","bn":"কিমা আলু","cat":"meat","s":"100g","k":220,"p":14.0,"c":10.0,"f":13.0,"fi":1.4,"ca":16,"fe":2.0,"src":"local","kw":["mutton","keema","kima","aloo","potato","minced","gosht"]},
  {"id":3032,"en":"Keema Matar","bn":"কিমা মটর","cat":"meat","s":"100g","k":215,"p":15.0,"c":9.0,"f":12.0,"fi":1.8,"ca":18,"fe":2.1,"src":"local","kw":["mutton","keema","kima","matar","peas","minced","gosht"]},
  {"id":3033,"en":"Mutton Stuffed Paratha","bn":"মাটন পরোটা","cat":"meat","s":"100g","k":290,"p":11.0,"c":24.0,"f":16.0,"fi":1.5,"ca":20,"fe":2.1,"src":"local","kw":["mutton","paratha","porota","stuffed","keema","gosht"]},
  {"id":3034,"en":"Mutton Roll","bn":"মাটন রোল","cat":"meat","s":"100g","k":280,"p":12.0,"c":23.0,"f":15.0,"fi":1.2,"ca":18,"fe":1.9,"src":"local","kw":["mutton","roll","kati roll","street food","kolkata","gosht"]},
  {"id":3035,"en":"Mutton Cutlet","bn":"মাটন কাটলেট","cat":"meat","s":"100g","k":275,"p":15.0,"c":14.0,"f":18.0,"fi":1.0,"ca":16,"fe":2.0,"src":"local","kw":["mutton","cutlet","fried","bengali","gosht"]},
  {"id":3036,"en":"Kobiraji Mutton Cutlet","bn":"কবিরাজি মাটন কাটলেট","cat":"meat","s":"100g","k":310,"p":15.0,"c":16.0,"f":22.0,"fi":0.8,"ca":18,"fe":2.1,"src":"local","kw":["mutton","kobiraji","kabiraji","cutlet","egg net","bengali","kolkata"]},
  {"id":3037,"en":"Mutton Chop","bn":"মাটন চপ","cat":"meat","s":"100g","k":290,"p":16.0,"c":15.0,"f":19.0,"fi":1.0,"ca":17,"fe":2.2,"src":"local","kw":["mutton","chop","fried","bengali","street food"]},
  {"id":3038,"en":"Mutton Shami Kebab","bn":"মাটন শামি কাবাব","cat":"meat","s":"100g","k":260,"p":17.0,"c":8.0,"f":17.0,"fi":1.1,"ca":16,"fe":2.3,"src":"local","kw":["mutton","shami","kebab","kabab","gosht"]},
  {"id":3039,"en":"Mutton Seekh Kebab","bn":"মাটন সিক কাবাব","cat":"meat","s":"100g","k":270,"p":19.0,"c":4.0,"f":20.0,"fi":0.4,"ca":16,"fe":2.4,"src":"local","kw":["mutton","seekh","sikh","kebab","kabab","grilled","gosht"]},
  {"id":3040,"en":"Mutton Tikka","bn":"মাটন টিক্কা","cat":"meat","s":"100g","k":240,"p":22.0,"c":3.0,"f":15.0,"fi":0.3,"ca":15,"fe":2.2,"src":"local","kw":["mutton","tikka","grilled","tandoor","gosht"]},
  {"id":3041,"en":"Mutton Bharta","bn":"মাটন ভর্তা","cat":"meat","s":"100g","k":230,"p":17.0,"c":4.0,"f":16.0,"fi":0.6,"ca":15,"fe":2.1,"src":"local","kw":["mutton","bharta","bhurji","mashed","gosht","bengali"]},
  {"id":3042,"en":"Mutton Posto","bn":"মাটন পোস্ত","cat":"meat","s":"100g","k":290,"p":18.0,"c":5.0,"f":22.0,"fi":1.2,"ca":45,"fe":2.5,"src":"local","kw":["mutton","posto","poppy seed","khus khus","bengali","gosht"]},
  {"id":3043,"en":"Mutton with Bottle Gourd","bn":"লাউ মাটন","cat":"meat","s":"100g","k":185,"p":15.0,"c":4.0,"f":11.0,"fi":1.0,"ca":18,"fe":1.9,"src":"local","kw":["mutton","lau","bottle gourd","lauki","bengali","gosht"]},
  {"id":3044,"en":"Mutton with Radish","bn":"মুলো মাটন","cat":"meat","s":"100g","k":190,"p":15.0,"c":5.0,"f":11.0,"fi":1.2,"ca":22,"fe":2.0,"src":"local","kw":["mutton","mulo","mooli","radish","bengali","gosht"]},
  {"id":3045,"en":"Mutton with Green Papaya","bn":"কাঁচা পেঁপে মাটন","cat":"meat","s":"100g","k":195,"p":16.0,"c":5.0,"f":11.0,"fi":1.3,"ca":20,"fe":2.0,"src":"local","kw":["mutton","green papaya","kacha pepe","raw papaya","bengali","gosht"]},
  {"id":3046,"en":"Mutton Jhal","bn":"মাটন ঝাল","cat":"meat","s":"100g","k":235,"p":18.0,"c":4.0,"f":16.0,"fi":0.5,"ca":15,"fe":2.2,"src":"local","kw":["mutton","jhal","spicy","bengali","gosht","khasi"]},
  {"id":3047,"en":"Mutton Tok","bn":"মাটন টক","cat":"meat","s":"100g","k":205,"p":16.0,"c":5.0,"f":12.0,"fi":0.7,"ca":17,"fe":2.0,"src":"local","kw":["mutton","tok","sour","tamarind","bengali","gosht"]},
  {"id":3048,"en":"Mutton with Black Gram","bn":"কালাই ডাল মাটন","cat":"meat","s":"100g","k":210,"p":15.0,"c":9.0,"f":11.0,"fi":2.0,"ca":22,"fe":2.4,"src":"local","kw":["mutton","kalai dal","black gram","urad","bengali","gosht"]},
  {"id":3049,"en":"Mutton with Lentils","bn":"ডাল মাটন","cat":"meat","s":"100g","k":205,"p":15.0,"c":10.0,"f":10.0,"fi":2.2,"ca":24,"fe":2.5,"src":"local","kw":["mutton","dal","lentil","bengali","gosht"]},
  {"id":3050,"en":"Traditional Bengali Goat Curry","bn":"ঐতিহ্যবাহী খাসির ঝোল","cat":"meat","s":"100g","k":225,"p":17.0,"c":4.0,"f":15.0,"fi":0.8,"ca":18,"fe":2.2,"src":"local","kw":["mutton","goat","khashi","khasi","jhol","traditional","bengali","gosht"]},
]

with open('assets/data/food_master_v7_2.json', encoding='utf-8') as f:
    data = json.load(f)

existing_ids = {item.get('id') for item in data}
to_add = [item for item in new_items if item['id'] not in existing_ids]
data.extend(to_add)

with open('assets/data/food_master_v7_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

print(f'Added {len(to_add)} items. Total: {len(data)}')
