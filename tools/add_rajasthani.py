import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'assets/data/food_master_v7_2.json'
data = json.load(open(path, encoding='utf-8'))

new_foods = [
  {'id':96001,'en':'Dal Baati','bn':'ডাল বাটি','cat':'grain','s':'100g','k':225,'p':8.5,'c':30.0,'f':7.5,'fi':4.5,'ca':32.0,'fe':2.4,'zn':1.2,'kw':['dal','baati','bati','rajasthani','ডাল','বাটি'],'src':'indb'},
  {'id':96002,'en':'Baati','bn':'বাটি','cat':'bread','s':'100g','k':265,'p':8.0,'c':42.0,'f':7.0,'fi':3.2,'ca':22.0,'fe':2.0,'zn':0.8,'kw':['baati','bati','wheat ball','rajasthani bread','বাটি'],'src':'indb'},
  {'id':96003,'en':'Churma','bn':'চুরমা','cat':'sweet','s':'100g','k':420,'p':7.0,'c':58.0,'f':18.0,'fi':4.0,'ca':28.0,'fe':1.8,'zn':0.9,'kw':['churma','rajasthani sweet','wheat sweet','চুরমা'],'src':'indb'},
  {'id':96004,'en':'Dal Baati Churma','bn':'ডাল বাটি চুরমা','cat':'grain','s':'100g','k':310,'p':8.0,'c':40.0,'f':12.0,'fi':4.0,'ca':30.0,'fe':2.1,'zn':1.0,'kw':['dal','baati','churma','rajasthani','thali','ডাল','বাটি','চুরমা'],'src':'indb'},
  {'id':96005,'en':'Gatte Ki Sabzi','bn':'গাট্টে কি সবজি','cat':'vegetable','s':'100g','k':165,'p':7.0,'c':12.0,'f':9.5,'fi':2.5,'ca':45.0,'fe':1.8,'zn':0.8,'kw':['gatte','sabzi','besan','gram flour dumpling','rajasthani','গাট্টে'],'src':'indb'},
  {'id':96006,'en':'Ker Sangri','bn':'কের সাংরি','cat':'vegetable','s':'100g','k':135,'p':4.5,'c':15.0,'f':6.0,'fi':6.0,'ca':75.0,'fe':2.2,'zn':0.7,'kw':['ker','sangri','desert beans','rajasthani','কের','সাংরি'],'src':'indb'},
  {'id':96007,'en':'Panchmel Dal','bn':'পঞ্চমেল ডাল','cat':'legume','s':'100g','k':130,'p':7.5,'c':18.0,'f':3.0,'fi':4.5,'ca':35.0,'fe':2.0,'zn':1.0,'kw':['panchmel','dal','five lentil','pancharangi','পঞ্চমেল','ডাল'],'src':'indb'},
  {'id':96008,'en':'Bajra Roti','bn':'বাজরা রুটি','cat':'bread','s':'100g','k':235,'p':8.0,'c':44.0,'f':2.5,'fi':8.0,'ca':27.0,'fe':3.5,'zn':1.8,'kw':['bajra','roti','pearl millet','flatbread','বাজরা','রুটি'],'src':'indb'},
  {'id':96009,'en':'Missi Roti','bn':'মিসি রুটি','cat':'bread','s':'100g','k':250,'p':9.0,'c':38.0,'f':5.0,'fi':5.0,'ca':35.0,'fe':2.8,'zn':1.2,'kw':['missi','roti','besan roti','gram flour flatbread','মিসি','রুটি'],'src':'indb'},
  {'id':96010,'en':'Rabdi','bn':'রাবড়ি','cat':'sweet','s':'100g','k':285,'p':6.5,'c':28.0,'f':16.0,'fi':0.0,'ca':220.0,'fe':0.2,'zn':0.8,'kw':['rabdi','rabri','condensed milk sweet','রাবড়ি'],'src':'indb'},
  {'id':96011,'en':'Laal Maas','bn':'লাল মাস','cat':'meat','s':'100g','k':255,'p':20.0,'c':3.0,'f':18.0,'fi':0.5,'ca':24.0,'fe':2.8,'zn':3.5,'kw':['laal','maas','red meat curry','rajasthani mutton','lamb','লাল','মাস'],'src':'indb'},
  {'id':96012,'en':'Safed Maas','bn':'সাফেদ মাস','cat':'meat','s':'100g','k':275,'p':19.0,'c':4.0,'f':20.0,'fi':0.4,'ca':28.0,'fe':2.6,'zn':3.2,'kw':['safed','maas','white mutton curry','rajasthani','সাফেদ','মাস'],'src':'indb'},
  {'id':96013,'en':'Jungli Maas','bn':'জংলি মাস','cat':'meat','s':'100g','k':235,'p':22.0,'c':1.5,'f':16.0,'fi':0.2,'ca':20.0,'fe':2.7,'zn':3.8,'kw':['jungli','maas','wild meat','rajasthani mutton','জংলি','মাস'],'src':'indb'},
  {'id':96014,'en':'Mohan Maas','bn':'মোহন মাস','cat':'meat','s':'100g','k':290,'p':18.0,'c':5.0,'f':22.0,'fi':0.4,'ca':35.0,'fe':2.5,'zn':3.0,'kw':['mohan','maas','rajasthani mutton','cream','মোহন','মাস'],'src':'indb'},
  {'id':96015,'en':'Rajasthani Kadhi','bn':'রাজস্থানি কড়ি','cat':'soup','s':'100g','k':105,'p':4.0,'c':10.0,'f':5.5,'fi':1.0,'ca':72.0,'fe':0.9,'zn':0.5,'kw':['rajasthani','kadhi','kadhi','yogurt curry','besan','কড়ি'],'src':'indb'},
  {'id':96016,'en':'Papad Ki Sabzi','bn':'পাপড় কি সবজি','cat':'vegetable','s':'100g','k':145,'p':6.5,'c':10.0,'f':8.5,'fi':2.0,'ca':55.0,'fe':1.6,'zn':0.7,'kw':['papad','sabzi','papadum curry','পাপড়','সবজি'],'src':'indb'},
  {'id':96017,'en':'Sev Tamatar','bn':'সেভ টমেটার','cat':'vegetable','s':'100g','k':165,'p':4.2,'c':14.0,'f':10.0,'fi':2.5,'ca':24.0,'fe':1.1,'zn':0.4,'kw':['sev','tamatar','tomato','crispy noodle','সেভ','টমেটার'],'src':'indb'},
  {'id':96018,'en':'Mirchi Vada','bn':'মির্চি বড়া','cat':'snack','s':'100g','k':275,'p':6.5,'c':30.0,'f':14.0,'fi':3.5,'ca':28.0,'fe':1.5,'zn':0.6,'kw':['mirchi','vada','chilli fritter','stuffed chilli','মির্চি','বড়া'],'src':'indb'},
  {'id':96019,'en':'Pyaz Kachori','bn':'পেঁয়াজ কচুরি','cat':'snack','s':'100g','k':360,'p':8.0,'c':40.0,'f':18.0,'fi':3.5,'ca':25.0,'fe':1.8,'zn':0.7,'kw':['pyaz','kachori','onion kachori','পেঁয়াজ','কচুরি'],'src':'indb'},
  {'id':96020,'en':'Dal Kachori','bn':'ডাল কচুরি','cat':'snack','s':'100g','k':340,'p':9.0,'c':38.0,'f':16.0,'fi':4.0,'ca':30.0,'fe':2.0,'zn':0.8,'kw':['dal','kachori','lentil kachori','ডাল','কচুরি'],'src':'indb'},
  {'id':96021,'en':'Ghevar','bn':'ঘেওয়ার','cat':'sweet','s':'100g','k':430,'p':5.0,'c':60.0,'f':18.0,'fi':0.5,'ca':85.0,'fe':0.8,'zn':0.4,'kw':['ghevar','ghewar','rajasthani sweet','festival sweet','ঘেওয়ার'],'src':'indb'},
  {'id':96022,'en':'Malpua','bn':'মালপুয়া','cat':'sweet','s':'100g','k':365,'p':5.5,'c':52.0,'f':15.0,'fi':0.8,'ca':95.0,'fe':0.7,'zn':0.5,'kw':['malpua','malpoa','pancake sweet','মালপুয়া'],'src':'indb'},
  {'id':96023,'en':'Mawa Kachori','bn':'মাওয়া কচুরি','cat':'sweet','s':'100g','k':445,'p':7.0,'c':52.0,'f':22.0,'fi':1.0,'ca':105.0,'fe':0.8,'zn':0.6,'kw':['mawa','khoya','kachori','sweet kachori','মাওয়া','কচুরি'],'src':'indb'},
  {'id':96024,'en':'Balushahi','bn':'বালুশাহি','cat':'sweet','s':'100g','k':425,'p':4.0,'c':65.0,'f':16.0,'fi':0.5,'ca':18.0,'fe':0.5,'zn':0.3,'kw':['balushahi','badusha','flaky sweet','বালুশাহি'],'src':'indb'},
  {'id':96025,'en':'Moong Dal Halwa','bn':'মুগ ডাল হালুয়া','cat':'sweet','s':'100g','k':410,'p':8.0,'c':42.0,'f':22.0,'fi':2.2,'ca':55.0,'fe':1.6,'zn':1.2,'kw':['moong','dal','halwa','mung bean sweet','মুগ','ডাল','হালুয়া'],'src':'indb'},
]

existing_ids = {d['id'] for d in data}
for nf in new_foods:
    if nf['id'] in existing_ids:
        print(f'CONFLICT: {nf["id"]} {nf["en"]}')

data.extend(new_foods)
print(f'New total: {len(data)} items')

with open(path, 'w', encoding='utf-8') as fp:
    json.dump(data, fp, ensure_ascii=False, separators=(',', ':'))
print('Done.')
