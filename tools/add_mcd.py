import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'assets/data/food_master_v7_2.json'
data = json.load(open(path, encoding='utf-8'))

def mcd(id_, en, bn, w, k, c, p, f, cat, unit='g', fi=0.0):
    kws = list({t.lower() for t in en.split()} | {'mcdonalds','mcdonald','mcd'})
    return {'id':id_,'en':en,'bn':bn,'cat':cat,'s':f'{w}{unit}',
            'k':round(k,1),'p':round(p,1),'c':round(c,1),'f':round(f,1),'fi':fi,
            'ca':0.0,'fe':0.0,'zn':0.0,'kw':kws,'src':'mcdonalds_india'}

# Macro validation: carb*4+prot*4+fat*9 within ~10% of kcal for all items.
# Skipped: McFlurry Choco Crunch Regular (703 kcal/167g — internal macros consistent
#           but 4.5x scaling vs Small is impossible; PDF column-shift error)
#           Schweppes Packaged Water (0 kcal)

new_foods = [
    # ===== BURGERS & MAINS =====
    mcd(99057,'McVeggie Burger','ম্যাকভেজি বার্গার',168,402.1,56.5,10.2,13.8,'snack'),
    mcd(99058,'McDonalds Dosa Masala Burger','ম্যাকডোনাল্ডস ডোসা মাসালা বার্গার',138,340.2,51.5,5.7,12.4,'snack'),
    mcd(99059,'McAloo Tikki Burger','ম্যাক আলু টিক্কি বার্গার',146,339.5,50.3,8.5,11.3,'snack'),
    mcd(99060,'McSpicy Paneer Burger','ম্যাকস্পাইসি পনির বার্গার',199,652.8,52.3,20.3,39.5,'snack'),
    mcd(99061,'McSpicy Paneer Wrap','ম্যাকস্পাইসি পনির র‍্যাপ',250,674.7,59.3,21.0,39.1,'snack'),
    mcd(99062,'Schezwan Veg Burger','শেজওয়ান ভেজ বার্গার',121,286.1,46.3,6.1,8.5,'snack'),
    mcd(99063,'Butter Paneer Grilled Burger','বাটার পনির গ্রিলড বার্গার',142,382.3,44.1,12.9,17.2,'snack'),
    mcd(99064,'Veg Maharaja Mac','ভেজ মহারাজা ম্যাক',306,832.7,93.8,24.2,37.9,'snack'),
    mcd(99065,'McDonalds Pizza Puff','ম্যাকডোনাল্ডস পিৎজা পাফ',87,228.2,24.8,5.5,11.4,'snack'),
    mcd(99066,'Chicken McGrill Burger','চিকেন ম্যাকগ্রিল বার্গার',142,274.2,36.2,13.2,8.5,'snack'),
    mcd(99067,'Butter Chicken Grilled Burger','বাটার চিকেন গ্রিলড বার্গার',153,357.0,39.8,17.1,14.4,'snack'),
    mcd(99068,'McEgg Burger','ম্যাকএগ বার্গার',115,265.0,31.0,12.0,10.0,'snack'),
    mcd(99069,'McChicken Burger','ম্যাকচিকেন বার্গার',173,400.8,48.0,15.7,15.7,'snack'),
    mcd(99070,'Filet-O-Fish Burger','ফিলেট-ও-ফিশ বার্গার',136,348.1,38.9,15.4,14.2,'snack'),
    mcd(99071,'McSpicy Chicken Burger','ম্যাকস্পাইসি চিকেন বার্গার',186,451.9,46.1,21.5,19.4,'snack'),
    mcd(99072,'McSpicy Chicken Wrap','ম্যাকস্পাইসি চিকেন র‍্যাপ',257,567.2,57.1,23.7,26.9,'snack'),
    mcd(99073,'Chicken Maharaja Mac','চিকেন মহারাজা ম্যাক',296,689.1,55.4,34.0,36.7,'snack'),
    # ===== McNUGGETS =====
    mcd(99074,'McDonalds Chicken McNuggets 4pc','ম্যাকডোনাল্ডস চিকেন ম্যাকনাগেটস ৪ পিস',64,169.7,10.5,10.0,9.5,'meat'),
    mcd(99075,'McDonalds Chicken McNuggets 6pc','ম্যাকডোনাল্ডস চিকেন ম্যাকনাগেটস ৬ পিস',96,254.5,15.7,15.0,14.3,'meat'),
    mcd(99076,'McDonalds Chicken McNuggets 9pc','ম্যাকডোনাল্ডস চিকেন ম্যাকনাগেটস ৯ পিস',144,381.8,23.6,22.6,21.5,'meat'),
    mcd(99077,'McDonalds Chicken McNuggets 20pc','ম্যাকডোনাল্ডস চিকেন ম্যাকনাগেটস ২০ পিস',320,806.1,49.9,47.6,46.9,'meat'),
    # ===== FRIES =====
    mcd(99078,'McDonalds French Fries Regular','ম্যাকডোনাল্ডস ফ্রেঞ্চ ফ্রাইস রেগুলার',77,224.6,27.1,3.4,10.4,'snack'),
    mcd(99079,'McDonalds French Fries Medium','ম্যাকডোনাল্ডস ফ্রেঞ্চ ফ্রাইস মিডিয়াম',109,317.9,38.3,4.8,14.7,'snack'),
    mcd(99080,'McDonalds French Fries Large','ম্যাকডোনাল্ডস ফ্রেঞ্চ ফ্রাইস লার্জ',154,449.2,54.2,6.8,20.8,'snack'),
    # ===== DESSERTS =====
    mcd(99081,'McDonalds Soft Serve Cone','ম্যাকডোনাল্ডস সফট সার্ভ কোন',81,85.7,15.2,2.0,1.8,'sweet'),
    mcd(99082,'McSwirl Chocodip','ম্যাকসার্ল চকোডিপ',93,160.1,20.9,2.7,7.1,'sweet'),
    mcd(99083,'McSwirl ButterScotch','ম্যাকসার্ল বাটারস্কচ',95,181.2,22.2,2.8,8.1,'sweet'),
    mcd(99084,'McDonalds Sundae Chocolate Regular','ম্যাকডোনাল্ডস চকোলেট সানডেই রেগুলার',92,121.6,19.1,2.3,4.0,'sweet'),
    mcd(99085,'McDonalds Sundae Chocolate Medium','ম্যাকডোনাল্ডস চকোলেট সানডেই মিডিয়াম',132,197.5,30.4,3.5,6.9,'sweet'),
    mcd(99086,'McDonalds Sundae Strawberry Regular','ম্যাকডোনাল্ডস স্ট্রবেরি সানডেই রেগুলার',92,101.0,19.8,1.5,1.8,'sweet'),
    mcd(99087,'McDonalds Sundae Strawberry Medium','ম্যাকডোনাল্ডস স্ট্রবেরি সানডেই মিডিয়াম',132,156.1,31.8,2.1,2.4,'sweet'),
    mcd(99088,'McDonalds Sundae Chocolate Brownie Regular','ম্যাকডোনাল্ডস ব্রাউনি সানডেই রেগুলার',111,205.3,35.3,3.2,5.5,'sweet'),
    mcd(99089,'McDonalds Sundae Chocolate Brownie Medium','ম্যাকডোনাল্ডস ব্রাউনি সানডেই মিডিয়াম',155,311.4,55.2,4.7,7.5,'sweet'),
    mcd(99090,'McFlurry Oreo Small','ম্যাকফ্লারি ওরিও স্মল',87,116.4,18.7,2.1,3.7,'sweet'),
    mcd(99091,'McFlurry Oreo Regular','ম্যাকফ্লারি ওরিও রেগুলার',147,209.4,33.4,3.6,6.8,'sweet'),
    mcd(99092,'McFlurry Choco Crunch Small','ম্যাকফ্লারি চকো ক্রাঞ্চ স্মল',94,155.2,23.7,2.6,5.4,'sweet'),
    mcd(99093,'McDonalds Black Forest Regular','ম্যাকডোনাল্ডস ব্ল্যাক ফরেস্ট রেগুলার',115,268.3,47.9,4.4,6.4,'sweet'),
    mcd(99094,'McDonalds Black Forest Medium','ম্যাকডোনাল্ডস ব্ল্যাক ফরেস্ট মিডিয়াম',210,398.1,68.5,6.9,10.6,'sweet'),
    # ===== REGULAR MENU BEVERAGES =====
    mcd(99095,'McDonalds Black Coffee','ম্যাকডোনাল্ডস ব্ল্যাক কফি',200,6.8,1.7,0.0,0.0,'beverage','ml'),
    mcd(99096,'McDonalds Coca-Cola Small','ম্যাকডোনাল্ডস কোকা-কোলা স্মল',299,109.6,27.4,0.0,0.0,'beverage','ml'),
    mcd(99097,'McDonalds Coca-Cola Medium','ম্যাকডোনাল্ডস কোকা-কোলা মিডিয়াম',394,151.4,37.8,0.0,0.0,'beverage','ml'),
    mcd(99098,'McDonalds Coca-Cola Large','ম্যাকডোনাল্ডস কোকা-কোলা লার্জ',544,217.4,54.3,0.0,0.0,'beverage','ml'),
    mcd(99099,'McDonalds Fanta Small','ম্যাকডোনাল্ডস ফান্টা স্মল',299,129.5,32.4,0.0,0.0,'beverage','ml'),
    mcd(99100,'McDonalds Fanta Medium','ম্যাকডোনাল্ডস ফান্টা মিডিয়াম',394,178.9,44.7,0.0,0.0,'beverage','ml'),
    mcd(99101,'McDonalds Fanta Large','ম্যাকডোনাল্ডস ফান্টা লার্জ',544,256.9,64.2,0.0,0.0,'beverage','ml'),
    mcd(99102,'McDonalds Sprite Small','ম্যাকডোনাল্ডস স্প্রাইট স্মল',299,119.5,29.9,0.0,0.0,'beverage','ml'),
    mcd(99103,'McDonalds Sprite Medium','ম্যাকডোনাল্ডস স্প্রাইট মিডিয়াম',394,165.1,41.3,0.0,0.0,'beverage','ml'),
    mcd(99104,'McDonalds Sprite Large','ম্যাকডোনাল্ডস স্প্রাইট লার্জ',544,237.1,59.3,0.0,0.0,'beverage','ml'),
    mcd(99105,'McDonalds Coke Float','ম্যাকডোনাল্ডস কোক ফ্লোট',287,138.8,29.2,1.5,1.8,'beverage','ml'),
    mcd(99106,'McDonalds Fanta Float','ম্যাকডোনাল্ডস ফান্টা ফ্লোট',287,151.6,32.4,1.5,1.8,'beverage','ml'),
    mcd(99107,'McDonalds Sprite Float','ম্যাকডোনাল্ডস স্প্রাইট ফ্লোট',287,145.2,30.8,1.5,1.8,'beverage','ml'),
    mcd(99108,'McDonalds Cold Coffee','ম্যাকডোনাল্ডস কোল্ড কফি',250,301.1,40.2,9.8,11.2,'beverage','ml'),
    mcd(99109,'McDonalds Cold Coffee Float','ম্যাকডোনাল্ডস কোল্ড কফি ফ্লোট',270,270.1,45.4,5.9,7.2,'beverage','ml'),
    mcd(99110,'McDonalds Iced Tea','ম্যাকডোনাল্ডস আইসড টি',400,242.5,59.3,1.1,0.1,'beverage','ml'),
    mcd(99111,'McDonalds Masala Chai Regular','ম্যাকডোনাল্ডস মশলা চা রেগুলার',150,110.0,22.3,0.6,2.0,'beverage','ml'),
    mcd(99112,'McDonalds Masala Chai Cutting','ম্যাকডোনাল্ডস মশলা চা কাটিং',90,65.5,13.7,0.3,1.1,'beverage','ml'),
    mcd(99113,'McDonalds Minute Maid Pulpy Orange','ম্যাকডোনাল্ডস মিনিট মেইড পালপি অরেঞ্জ',300,156.0,39.0,0.0,0.0,'beverage','ml'),
    mcd(99114,'McDonalds Coke Zero','ম্যাকডোনাল্ডস কোক জিরো',330,0.1,0.0,0.0,0.0,'beverage','ml'),
    mcd(99115,'McDonalds Chocolate Milkshake','ম্যাকডোনাল্ডস চকোলেট মিল্কশেক',180,96.0,16.5,6.5,0.6,'beverage','ml'),
    # ===== CONDIMENTS =====
    mcd(99116,'McDonalds Mustard Dip Sauce','ম্যাকডোনাল্ডস মাস্টার্ড ডিপ সস',25,81.2,7.2,0.5,5.6,'snack'),
    mcd(99117,'McDonalds Barbeque Dip Sauce','ম্যাকডোনাল্ডস বারবিকিউ ডিপ সস',25,54.9,12.4,0.3,0.5,'snack'),
    mcd(99118,'McDonalds Chilli Sauce','ম্যাকডোনাল্ডস চিলি সস',10,7.0,1.7,0.0,0.0,'snack'),
    mcd(99119,'McDonalds Cheese Slice','ম্যাকডোনাল্ডস চিজ স্লাইস',14,51.0,0.7,3.1,4.0,'dairy'),
    mcd(99120,'McDonalds Tomato Ketchup','ম্যাকডোনাল্ডস টমেটো কেচাপ',8,10.0,2.5,0.0,0.0,'snack'),
    mcd(99121,'McDonalds Milk Tub Creamer','ম্যাকডোনাল্ডস মিল্ক ক্রিমার',10,14.0,0.8,0.5,1.0,'dairy'),
    mcd(99122,'McDonalds Peri-Peri Spice Mix','ম্যাকডোনাল্ডস পেরি-পেরি মশলা',5,12.0,2.2,0.3,0.2,'snack'),
    mcd(99123,'McDonalds Sugar Sachet','ম্যাকডোনাল্ডস চিনি সাশে',5,20.0,5.0,0.0,0.0,'snack'),
    mcd(99124,'McDonalds Pineapple Fruit Bowl','ম্যাকডোনাল্ডস আনারস ফ্রুট বোল',113,65.7,15.6,0.5,0.1,'fruit'),
    # ===== McCAFE =====
    mcd(99125,'McCafe Cappuccino Small','ম্যাককাফে ক্যাপুচিনো স্মল',240,136.4,10.0,8.0,7.2,'beverage','ml'),
    mcd(99126,'McCafe Cappuccino Regular','ম্যাককাফে ক্যাপুচিনো রেগুলার',360,206.5,15.5,11.8,10.8,'beverage','ml'),
    mcd(99127,'McCafe Latte Small','ম্যাককাফে লাতে স্মল',240,128.7,11.5,7.4,5.9,'beverage','ml'),
    mcd(99128,'McCafe Latte Regular','ম্যাককাফে লাতে রেগুলার',360,194.7,16.0,11.1,9.6,'beverage','ml'),
    mcd(99129,'McCafe Americano Small','ম্যাককাফে আমেরিকানো স্মল',240,6.3,0.2,1.2,0.1,'beverage','ml'),
    mcd(99130,'McCafe Americano Regular','ম্যাককাফে আমেরিকানো রেগুলার',360,10.7,0.4,1.8,0.2,'beverage','ml'),
    mcd(99131,'McCafe Mocha Small','ম্যাককাফে মোকা স্মল',240,221.6,30.9,8.6,7.0,'beverage','ml'),
    mcd(99132,'McCafe Mocha Regular','ম্যাককাফে মোকা রেগুলার',360,331.4,50.1,12.9,8.9,'beverage','ml'),
    mcd(99133,'McCafe Espresso Shot','ম্যাককাফে এসপ্রেসো শট',30,6.4,0.8,0.7,0.1,'beverage','ml'),
    mcd(99134,'McCafe Macchiato','ম্যাককাফে ম্যাচিয়াটো',120,44.9,5.1,1.9,1.9,'beverage','ml'),
    mcd(99135,'McCafe Hot Chocolate','ম্যাককাফে হট চকোলেট',240,267.2,44.4,8.5,6.2,'beverage','ml'),
    mcd(99136,'McCafe Cold Coffee Frappe','ম্যাককাফে কোল্ড কফি ফ্রাপে',320,364.0,55.9,5.5,13.2,'beverage','ml'),
    mcd(99137,'McCafe Caramel Frappe','ম্যাককাফে ক্যারামেল ফ্রাপে',320,445.4,77.1,4.1,13.4,'beverage','ml'),
    mcd(99138,'McCafe Choco Frappe','ম্যাককাফে চকো ফ্রাপে',320,428.9,74.2,5.3,12.3,'beverage','ml'),
    mcd(99139,'McCafe Chocolate Shake','ম্যাককাফে চকোলেট শেক',300,467.7,90.7,3.8,10.0,'beverage','ml'),
    mcd(99140,'McCafe Strawberry Shake','ম্যাককাফে স্ট্রবেরি শেক',300,452.3,94.5,3.6,6.7,'beverage','ml'),
    mcd(99141,'McCafe Vanilla Shake','ম্যাককাফে ভ্যানিলা শেক',300,402.2,73.9,4.0,10.1,'beverage','ml'),
    mcd(99142,'McCafe Vanilla Oreo Shake','ম্যাককাফে ভ্যানিলা ওরিও শেক',300,554.3,85.9,13.3,17.5,'beverage','ml'),
    mcd(99143,'McCafe Strawberry Banana Shake','ম্যাককাফে স্ট্রবেরি বানানা শেক',300,463.4,93.3,3.0,8.7,'beverage','ml'),
    mcd(99144,'McCafe Sweet Lime Cooler','ম্যাককাফে সুইট লাইম কুলার',320,150.8,37.0,0.4,0.1,'beverage','ml'),
    mcd(99145,'McCafe Peach Iced Tea','ম্যাককাফে পিচ আইসড টি',320,157.2,38.4,0.8,0.0,'beverage','ml'),
    mcd(99146,'McCafe Vanilla Muffin','ম্যাককাফে ভ্যানিলা মাফিন',80,325.5,42.7,2.8,16.0,'sweet'),
    mcd(99147,'McCafe Nutella Cookie','ম্যাককাফে নুটেলা কুকি',50,271.0,25.5,3.5,16.0,'sweet'),
]

existing_ids = {d['id'] for d in data}
conflicts = [nf for nf in new_foods if nf['id'] in existing_ids]
if conflicts:
    print(f'CONFLICTS: {[c["id"] for c in conflicts]}')
    sys.exit(1)

print(f'Adding {len(new_foods)} McDonald\'s items')
data.extend(new_foods)
print(f'New total: {len(data)} items')

with open(path, 'w', encoding='utf-8') as fp:
    json.dump(data, fp, ensure_ascii=False, separators=(',', ':'))
print('Done.')
