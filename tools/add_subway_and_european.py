"""
add_subway_and_european.py
  - Adds 2 European Indian restaurant items (59001-59002)
  - Adds all Subway US menu items from us-nutrition-en.pdf (Jan 2026)
    IDs 59003-59200

All Subway nutrition stored per-100g (converted from per-serving using
the serving weight column from the PDF).

Bengali names use standard transliteration.
Source: subway_us (Jan 2026 PDF)
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

# ── Helper: convert per-serving → per-100g ──────────────────────────────────
def p100(val, sv):
    return round(val * 100 / sv, 1)

# ── Raw data: (id, en, bn, cat, sv_g, k, fat, carb, fib, pro, ca_pct, fe_pct) ──
# sv_g = serving grams; k/fat/carb/fib/pro = per-serving values
# ca_pct / fe_pct = %DV per serving (Ca DV=1300mg, Fe DV=18mg)
RAW = [
  # ── EUROPEAN INDIAN RESTAURANT (user-provided, per 100g already) ──────────
  # Stored directly — no conversion needed
  # ── SUBWAY 6" SANDWICHES ──────────────────────────────────────────────────
  # Cheesesteaks
  (59003,'Subway 6" Steak Philly','সাবওয়ে স্টেক ফিলি (৬ ইঞ্চি)','restaurant_food',192,510,25,43,2,28,90,100),
  (59004,'Subway 6" Chipotle Philly','সাবওয়ে চিপোটলে ফিলি (৬ ইঞ্চি)','restaurant_food',198,490,22,44,2,30,100,100),
  (59005,'Subway 6" Cheesy Garlic Steak','সাবওয়ে চিজি গার্লিক স্টেক (৬ ইঞ্চি)','restaurant_food',199,510,23,49,3,26,30,90),
  # Chicken
  (59006,'Subway 6" Grilled Chicken','সাবওয়ে গ্রিলড চিকেন (৬ ইঞ্চি)','restaurant_food',247,510,24,43,3,31,100,90),
  (59007,'Subway 6" Chicken & Bacon Ranch','সাবওয়ে চিকেন ব্যাকন র‌্যাঞ্চ (৬ ইঞ্চি)','restaurant_food',262,580,29,44,3,35,8,100),
  (59008,'Subway 6" Spicy Nacho Chicken','সাবওয়ে স্পাইসি নাচো চিকেন (৬ ইঞ্চি)','restaurant_food',203,440,17,49,3,24,35,90),
  (59009,'Subway 6" Honey Mustard BBQ Chicken','সাবওয়ে হানি মাস্টার্ড বিবিকিউ চিকেন (৬ ইঞ্চি)','restaurant_food',273,510,20,53,3,30,8,100),
  (59010,'Subway 6" Sweet Onion Teriyaki Chicken','সাবওয়ে সুইট অনিয়ন তেরিয়াকি চিকেন (৬ ইঞ্চি)','restaurant_food',256,430,11,55,4,29,10,15),
  # Italians
  (59011,'Subway 6" B.M.T.','সাবওয়ে বিএমটি (৬ ইঞ্চি)','restaurant_food',240,610,36,44,2,27,100,100),
  (59012,'Subway 6" Spicy Italian','সাবওয়ে স্পাইসি ইতালিয়ান (৬ ইঞ্চি)','restaurant_food',239,680,44,44,3,27,100,100),
  (59013,'Subway 6" 5 Meat Italian','সাবওয়ে ফাইভ মিট ইতালিয়ান (৬ ইঞ্চি)','restaurant_food',303,680,37,46,3,40,100,100),
  (59014,'Subway 6" Meatball Marinara','সাবওয়ে মিটবল মারিনারা (৬ ইঞ্চি)','restaurant_food',239,570,28,53,4,27,110,100),
  (59015,'Subway 6" Meatball Pepperoni','সাবওয়ে মিটবল পেপারোনি (৬ ইঞ্চি)','restaurant_food',268,690,38,56,4,33,110,100),
  # Deli Classics
  (59016,'Subway 6" Oven-Roasted Turkey','সাবওয়ে ওভেন রোস্টেড টার্কি (৬ ইঞ্চি)','restaurant_food',233,480,23,42,3,26,100,100),
  (59017,'Subway 6" Black Forest Ham','সাবওয়ে ব্ল্যাক ফরেস্ট হ্যাম (৬ ইঞ্চি)','restaurant_food',233,490,23,44,2,25,100,90),
  (59018,'Subway 6" Roast Beef','সাবওয়ে রোস্ট বিফ (৬ ইঞ্চি)','restaurant_food',247,500,23,44,2,31,100,90),
  (59019,'Subway 6" Cold Cut Combo','সাবওয়ে কোল্ড কাট কম্বো (৬ ইঞ্চি)','restaurant_food',240,530,29,43,2,25,100,100),
  (59020,'Subway 6" Tuna','সাবওয়ে টুনা (৬ ইঞ্চি)','restaurant_food',236,570,33,42,2,27,100,90),
  (59021,'Subway 6" Veggie Delite','সাবওয়ে ভেজি ডিলাইট (৬ ইঞ্চি)','restaurant_food',191,320,10,41,4,17,20,15),
  # Clubs
  (59022,'Subway 6" All American Club','সাবওয়ে অল আমেরিকান ক্লাব (৬ ইঞ্চি)','restaurant_food',242,540,28,45,3,27,90,100),
  (59023,'Subway 6" Subway Club','সাবওয়ে ক্লাব (৬ ইঞ্চি)','restaurant_food',263,500,24,43,4,31,10,25),
  # Local Favorites
  (59024,'Subway 6" Big Hot Pastrami','সাবওয়ে বিগ হট পাস্ত্রামি (৬ ইঞ্চি)','restaurant_food',232,550,30,44,2,30,90,110),
  (59025,'Subway 6" B.L.T.','সাবওয়ে বিএলটি (৬ ইঞ্চি)','restaurant_food',171,480,26,42,2,18,80,90),
  (59026,'Subway 6" Buffalo Chicken','সাবওয়ে বাফেলো চিকেন (৬ ইঞ্চি)','restaurant_food',288,510,19,55,3,31,25,35),
  (59027,'Subway 6" Oven-Roasted Turkey & Ham','সাবওয়ে টার্কি অ্যান্ড হ্যাম (৬ ইঞ্চি)','restaurant_food',233,480,23,41,4,27,20,20),
  (59028,'Subway 6" Pizza Sub','সাবওয়ে পিজ্জা সাব (৬ ইঞ্চি)','restaurant_food',177,490,25,45,2,22,100,100),
  (59029,'Subway 6" Veggie Patty','সাবওয়ে ভেজি প্যাটি (৬ ইঞ্চি)','restaurant_food',263,470,19,58,12,19,10,15),
  # Fresh Fit
  (59030,'Subway 6" Grilled Chicken & Smashed Avocado','সাবওয়ে গ্রিলড চিকেন অ্যাভোকাডো (ফ্রেশ ফিট)','restaurant_food',311,470,19,44,6,35,4,20),
  (59031,'Subway 6" Grilled Chicken & Fresh Avocado','সাবওয়ে গ্রিলড চিকেন ফ্রেশ অ্যাভোকাডো (ফ্রেশ ফিট)','restaurant_food',304,450,16,44,6,35,4,20),
  (59032,'Subway 6" Ham & Turkey Stacker','সাবওয়ে হ্যাম টার্কি স্ট্যাকার (ফ্রেশ ফিট)','restaurant_food',226,290,5,42,4,20,4,20),
  (59033,'Subway 6" Turkey & Ranch Delite','সাবওয়ে টার্কি র‌্যাঞ্চ ডিলাইট (ফ্রেশ ফিট)','restaurant_food',254,380,13,41,5,26,4,30),
  (59034,'Subway 6" Seasoned Steak & Smashed Avocado','সাবওয়ে সিজন্ড স্টেক অ্যাভোকাডো (ফ্রেশ ফিট)','restaurant_food',297,460,16,45,6,35,4,25),
  (59035,'Subway 6" Seasoned Steak & Fresh Avocado','সাবওয়ে সিজন্ড স্টেক ফ্রেশ অ্যাভোকাডো (ফ্রেশ ফিট)','restaurant_food',290,430,14,45,6,35,4,25),
  # Kids Mini
  (59036,"Subway Kids' Mini Veggie Delite",'সাবওয়ে মিনি ভেজি ডিলাইট (কিডস)','restaurant_food',108,140,2,27,3,6,2,10),
  (59037,"Subway Kids' Mini Black Forest Ham",'সাবওয়ে মিনি হ্যাম (কিডস)','restaurant_food',137,180,3,28,3,11,2,10),
  (59038,"Subway Kids' Mini Oven Roasted Turkey",'সাবওয়ে মিনি টার্কি (কিডস)','restaurant_food',137,170,3,27,3,12,2,15),

  # ── WRAPS ──────────────────────────────────────────────────────────────────
  # Cheesesteaks wraps
  (59039,'Subway Steak Philly Wrap','সাবওয়ে স্টেক ফিলি র‍্যাপ','restaurant_food',295,710,35,56,3,46,15,30),
  (59040,'Subway Chipotle Philly Wrap','সাবওয়ে চিপোটলে ফিলি র‍্যাপ','restaurant_food',300,700,32,56,3,47,20,30),
  (59041,'Subway Cheesy Garlic Steak Wrap','সাবওয়ে চিজি গার্লিক স্টেক র‍্যাপ','restaurant_food',302,710,33,62,3,43,8,30),
  # Chicken wraps
  (59042,'Subway Grilled Chicken Wrap','সাবওয়ে গ্রিলড চিকেন র‍্যাপ','restaurant_food',349,680,31,55,3,48,25,20),
  (59043,'Subway Chicken & Bacon Ranch Wrap','সাবওয়ে চিকেন ব্যাকন র‌্যাঞ্চ র‍্যাপ','restaurant_food',367,830,42,56,3,56,20,25),
  (59044,'Subway Spicy Nacho Chicken Wrap','সাবওয়ে স্পাইসি নাচো চিকেন র‍্যাপ','restaurant_food',294,610,24,59,3,40,6,25),
  (59045,'Subway Honey Mustard BBQ Chicken Wrap','সাবওয়ে বিবিকিউ চিকেন র‍্যাপ','restaurant_food',363,680,27,63,4,46,20,25),
  (59046,'Subway Sweet Onion Teriyaki Chicken Wrap','সাবওয়ে তেরিয়াকি চিকেন র‍্যাপ','restaurant_food',360,620,16,76,3,45,15,25),
  # Italian wraps
  (59047,'Subway Spicy Italian Wrap','সাবওয়ে স্পাইসি ইতালিয়ান র‍্যাপ','restaurant_food',318,1010,69,57,3,39,25,30),
  (59048,'Subway 5 Meat Italian Wrap','সাবওয়ে ফাইভ মিট ইতালিয়ান র‍্যাপ','restaurant_food',450,1000,56,60,3,66,25,40),
  (59049,'Subway Meatball Marinara Wrap','সাবওয়ে মিটবল মারিনারা র‍্যাপ','restaurant_food',397,890,49,76,7,40,30,30),
  (59050,'Subway Meatball Pepperoni Wrap','সাবওয়ে মিটবল পেপারোনি র‍্যাপ','restaurant_food',433,1050,63,77,7,47,30,35),
  # Deli wraps
  (59051,'Subway Oven-Roasted Turkey Wrap','সাবওয়ে ওভেন রোস্টেড টার্কি র‍্যাপ','restaurant_food',309,610,27,53,3,38,20,40),
  (59052,'Subway Black Forest Ham Wrap','সাবওয়ে হ্যাম র‍্যাপ','restaurant_food',309,630,28,57,3,36,20,25),
  (59053,'Subway Roast Beef Wrap','সাবওয়ে রোস্ট বিফ র‍্যাপ','restaurant_food',337,660,27,57,3,48,20,25),
  (59054,'Subway Tuna Wrap','সাবওয়ে টুনা র‍্যাপ','restaurant_food',330,900,59,52,3,41,20,25),
  (59055,'Subway Veggie Delite Wrap','সাবওয়ে ভেজি ডিলাইট র‍্যাপ','restaurant_food',210,400,13,53,3,17,20,20),
  # Club wraps
  (59056,'Subway All American Club Wrap','সাবওয়ে অল আমেরিকান ক্লাব র‍্যাপ','restaurant_food',333,760,39,57,3,44,15,35),
  (59057,'Subway Club Wrap','সাবওয়ে ক্লাব র‍্যাপ','restaurant_food',374,690,30,58,3,48,15,40),
  # Local Favorites wraps
  (59058,'Subway Big Hot Pastrami Wrap','সাবওয়ে পাস্ত্রামি র‍্যাপ','restaurant_food',365,890,54,56,3,49,15,50),
  (59059,'Subway B.L.T. Wrap','সাবওয়ে বিএলটি র‍্যাপ','restaurant_food',220,710,42,53,3,30,6,25),
  (59060,'Subway Turkey & Ham Wrap','সাবওয়ে টার্কি হ্যাম র‍্যাপ','restaurant_food',309,620,28,55,3,37,20,30),
  (59061,'Subway Pizza Sub Wrap','সাবওয়ে পিজ্জা সাব র‍্যাপ','restaurant_food',232,730,42,56,3,30,25,25),
  (59062,'Subway Veggie Patty Wrap','সাবওয়ে ভেজি প্যাটি র‍্যাপ','restaurant_food',367,720,30,87,19,25,10,20),
  # Protein Pockets
  (59063,'Subway Baja Chicken Pocket','সাবওয়ে বাজা চিকেন পকেট','restaurant_food',184,330,13,30,2,24,15,15),
  (59064,'Subway Italian Trio Pocket','সাবওয়ে ইতালিয়ান ট্রিও পকেট','restaurant_food',192,480,29,32,2,22,15,15),
  (59065,'Subway Peppercorn Ranch Chicken Pocket','সাবওয়ে পেপারকর্ন র‌্যাঞ্চ চিকেন পকেট','restaurant_food',190,330,13,30,2,24,15,15),
  (59066,'Subway Turkey & Ham Pocket','সাবওয়ে টার্কি হ্যাম পকেট','restaurant_food',193,320,11,32,2,21,15,20),

  # ── SALADS ─────────────────────────────────────────────────────────────────
  # Cheesesteak salads
  (59067,'Subway Steak Philly Salad','সাবওয়ে স্টেক ফিলি স্যালাড','salad',409,450,35,13,4,24,15,15),
  (59068,'Subway Chipotle Philly Salad','সাবওয়ে চিপোটলে ফিলি স্যালাড','salad',415,400,28,15,5,25,15,15),
  (59069,'Subway Cheesy Garlic Steak Salad','সাবওয়ে চিজি গার্লিক স্টেক স্যালাড','salad',434,460,32,21,5,23,80,8),
  # Chicken salads
  (59070,'Subway Grilled Chicken Salad','সাবওয়ে গ্রিলড চিকেন স্যালাড','salad',415,440,34,12,4,26,20,10),
  (59071,'Subway Chicken & Bacon Ranch Salad','সাবওয়ে চিকেন ব্যাকন র‌্যাঞ্চ স্যালাড','salad',430,490,36,14,5,30,20,15),
  (59072,'Subway Spicy Nacho Chicken Salad','সাবওয়ে স্পাইসি নাচো চিকেন স্যালাড','salad',420,320,19,20,5,20,6,10),
  (59073,'Subway Honey Mustard BBQ Chicken Salad','সাবওয়ে বিবিকিউ চিকেন স্যালাড','salad',454,420,24,31,5,25,20,15),
  (59074,'Subway Sweet Onion Teriyaki Chicken Salad','সাবওয়ে তেরিয়াকি চিকেন স্যালাড','salad',423,300,10,33,4,23,15,15),
  # Italian salads
  (59075,'Subway B.M.T. Salad','সাবওয়ে বিএমটি স্যালাড','salad',407,540,46,13,4,22,25,15),
  (59076,'Subway Spicy Italian Salad','সাবওয়ে স্পাইসি ইতালিয়ান স্যালাড','salad',407,610,54,13,4,22,25,15),
  (59077,'Subway 5 Meat Italian Salad','সাবওয়ে ফাইভ মিট ইতালিয়ান স্যালাড','salad',471,610,47,14,4,35,25,20),
  (59078,'Subway Meatball Marinara Salad','সাবওয়ে মিটবল মারিনারা স্যালাড','salad',484,530,39,25,7,23,30,20),
  (59079,'Subway Meatball Pepperoni Salad','সাবওয়ে মিটবল পেপারোনি স্যালাড','salad',502,610,47,26,7,26,30,25),
  # Deli salads
  (59080,'Subway Oven-Roasted Turkey Salad','সাবওয়ে টার্কি স্যালাড','salad',400,410,33,11,4,21,20,20),
  (59081,'Subway Black Forest Ham Salad','সাবওয়ে হ্যাম স্যালাড','salad',400,420,33,13,4,20,20,10),
  (59082,'Subway Roast Beef Salad','সাবওয়ে রোস্ট বিফ স্যালাড','salad',415,440,33,13,4,26,20,10),
  (59083,'Subway Cold Cut Combo Salad','সাবওয়ে কোল্ড কাট কম্বো স্যালাড','salad',408,470,39,11,4,20,25,15),
  (59084,'Subway Tuna Salad','সাবওয়ে টুনা স্যালাড','salad',390,410,32,10,4,22,20,10),
  (59085,'Subway Veggie Delite Salad','সাবওয়ে ভেজি ডিলাইট স্যালাড','salad',316,150,9,10,4,10,20,10),
  # Club salads
  (59086,'Subway All American Club Salad','সাবওয়ে অল আমেরিকান ক্লাব স্যালাড','salad',410,480,39,13,4,22,15,15),
  (59087,'Subway Club Salad','সাবওয়ে ক্লাব স্যালাড','salad',430,440,34,14,4,24,15,20),
  # Local favorites salads
  (59088,'Subway Big Hot Pastrami Salad','সাবওয়ে পাস্ত্রামি স্যালাড','salad',463,410,30,15,5,26,15,25),
  (59089,'Subway B.L.T. Salad','সাবওয়ে বিএলটি স্যালাড','salad',345,420,36,11,4,13,6,10),
  (59090,'Subway Turkey & Ham Salad','সাবওয়ে টার্কি হ্যাম স্যালাড','salad',400,420,33,12,4,21,20,15),
  (59091,'Subway Pizza Sub Salad','সাবওয়ে পিজ্জা সাব স্যালাড','salad',380,330,24,15,5,17,25,15),
  (59092,'Subway Veggie Patty Salad','সাবওয়ে ভেজি প্যাটি স্যালাড','salad',395,300,17,28,12,13,15,10),

  # ── PROTEIN BOWLS ──────────────────────────────────────────────────────────
  (59093,'Subway Steak Philly Protein Bowl','সাবওয়ে স্টেক ফিলি প্রোটিন বোল','restaurant_food',403,630,46,14,3,43,20,20),
  (59094,'Subway Chipotle Philly Protein Bowl','সাবওয়ে চিপোটলে ফিলি প্রোটিন বোল','restaurant_food',415,600,41,16,4,46,25,20),
  (59095,'Subway Cheesy Garlic Steak Protein Bowl','সাবওয়ে চিজি গার্লিক স্টেক প্রোটিন বোল','restaurant_food',417,630,42,27,4,39,8,20),
  (59096,'Subway Grilled Chicken Protein Bowl','সাবওয়ে গ্রিলড চিকেন প্রোটিন বোল','restaurant_food',415,620,44,12,3,48,35,10),
  (59097,'Subway Chicken & Bacon Ranch Protein Bowl','সাবওয়ে চিকেন ব্যাকন র‌্যাঞ্চ প্রোটিন বোল','restaurant_food',445,760,55,14,4,55,35,15),
  (59098,'Subway Spicy Nacho Chicken Protein Bowl','সাবওয়ে স্পাইসি নাচো চিকেন প্রোটিন বোল','restaurant_food',425,510,30,26,5,35,8,15),
  (59099,'Subway Honey Mustard BBQ Chicken Protein Bowl','সাবওয়ে বিবিকিউ চিকেন প্রোটিন বোল','restaurant_food',466,620,36,31,4,45,35,15),
  (59100,'Subway Sweet Onion Teriyaki Chicken Protein Bowl','সাবওয়ে তেরিয়াকি চিকেন প্রোটিন বোল','restaurant_food',432,470,18,41,3,42,20,15),
  (59101,'Subway B.M.T. Protein Bowl','সাবওয়ে বিএমটি প্রোটিন বোল','restaurant_food',401,820,68,14,3,40,40,15),
  (59102,'Subway Spicy Italian Protein Bowl','সাবওয়ে স্পাইসি ইতালিয়ান প্রোটিন বোল','restaurant_food',396,960,84,14,3,39,40,20),
  (59103,'Subway 5 Meat Italian Protein Bowl','সাবওয়ে ফাইভ মিট ইতালিয়ান প্রোটিন বোল','restaurant_food',528,960,70,17,3,66,40,30),
  (59104,'Subway Meatball Marinara Protein Bowl','সাবওয়ে মিটবল মারিনারা প্রোটিন বোল','restaurant_food',553,880,65,37,8,42,50,25),
  (59105,'Subway Meatball Pepperoni Protein Bowl','সাবওয়ে মিটবল পেপারোনি প্রোটিন বোল','restaurant_food',589,1040,79,38,8,48,50,25),
  (59106,'Subway Oven-Roasted Turkey Protein Bowl','সাবওয়ে টার্কি প্রোটিন বোল','restaurant_food',386,560,42,10,3,38,35,25),
  (59107,'Subway Black Forest Ham Protein Bowl','সাবওয়ে হ্যাম প্রোটিন বোল','restaurant_food',386,580,43,14,3,36,35,15),
  (59108,'Subway Roast Beef Protein Bowl','সাবওয়ে রোস্ট বিফ প্রোটিন বোল','restaurant_food',415,610,42,14,3,48,35,15),
  (59109,'Subway Tuna Protein Bowl','সাবওয়ে টুনা প্রোটিন বোল','restaurant_food',394,750,62,9,3,41,35,15),
  (59110,'Subway All American Club Protein Bowl','সাবওয়ে অল আমেরিকান ক্লাব প্রোটিন বোল','restaurant_food',405,690,53,15,3,40,20,20),
  (59111,'Subway Club Protein Bowl','সাবওয়ে ক্লাব প্রোটিন বোল','restaurant_food',418,410,21,16,3,44,20,25),
  (59112,'Subway Veggie Patty Protein Bowl','সাবওয়ে ভেজি প্যাটি প্রোটিন বোল','restaurant_food',404,540,33,44,19,22,20,6),

  # ── BREAKFAST ──────────────────────────────────────────────────────────────
  (59113,'Subway 6" Bacon Egg & Cheese Sub','সাবওয়ে বেকন এগ চিজ সাব (৬ ইঞ্চি)','breakfast',193,550,30,43,2,26,100,100),
  (59114,'Subway 6" Black Forest Ham Egg & Cheese Sub','সাবওয়ে হ্যাম এগ চিজ সাব (৬ ইঞ্চি)','breakfast',207,500,25,43,2,26,90,100),
  (59115,'Subway 6" Egg & Cheese Sub','সাবওয়ে এগ চিজ সাব (৬ ইঞ্চি)','breakfast',178,470,24,42,2,21,90,100),
  (59116,'Subway 6" Steak Egg & Cheese Sub','সাবওয়ে স্টেক এগ চিজ সাব (৬ ইঞ্চি)','breakfast',221,540,26,43,2,31,90,100),
  (59117,'Subway Bacon Egg & Cheese Wrap','সাবওয়ে বেকন এগ চিজ র‍্যাপ','breakfast',325,900,56,57,2,42,20,30),
  (59118,'Subway Black Forest Ham Egg & Cheese Wrap','সাবওয়ে হ্যাম এগ চিজ র‍্যাপ','breakfast',351,810,46,58,2,42,20,30),
  (59119,'Subway Egg & Cheese Wrap','সাবওয়ে এগ চিজ র‍্যাপ','breakfast',295,740,44,55,2,32,20,30),
  (59120,'Subway Steak Egg & Cheese Wrap','সাবওয়ে স্টেক এগ চিজ র‍্যাপ','breakfast',366,860,48,57,2,48,20,35),

  # ── 8" PIZZA ───────────────────────────────────────────────────────────────
  (59121,'Subway 8" Cheese Pizza','সাবওয়ে চিজ পিজ্জা (৮ ইঞ্চি)','pizza',293,700,22,95,4,29,40,35),
  (59122,'Subway 8" Bacon Pizza','সাবওয়ে বেকন পিজ্জা (৮ ইঞ্চি)','pizza',308,780,28,96,4,34,40,35),
  (59123,'Subway 8" Meatball Pizza','সাবওয়ে মিটবল পিজ্জা (৮ ইঞ্চি)','pizza',330,810,31,98,5,35,40,35),
  (59124,'Subway 8" Pepperoni Pizza','সাবওয়ে পেপারোনি পিজ্জা (৮ ইঞ্চি)','pizza',311,780,29,96,5,33,40,35),

  # ── SLIDERS ────────────────────────────────────────────────────────────────
  (59125,'Subway Ham & Jack Slider','সাবওয়ে হ্যাম জ্যাক স্লাইডার','snack',71,160,4,21,0,10,45,45),
  (59126,'Subway Italian Spice Slider','সাবওয়ে ইতালিয়ান স্পাইস স্লাইডার','snack',72,250,15,21,0,9,45,45),
  (59127,'Subway Little Cheesesteak Slider','সাবওয়ে চিজস্টেক স্লাইডার','snack',71,180,7,21,1,8,45,45),
  (59128,'Subway Turkey Slider','সাবওয়ে টার্কি স্লাইডার','snack',88,230,12,20,1,12,50,50),

  # ── BREADS ─────────────────────────────────────────────────────────────────
  (59129,'Subway Artisan Italian Bread (6")','সাবওয়ে আর্টিজান ইতালিয়ান রুটি (৬ ইঞ্চি)','bread',71,210,2,39,1,8,80,90),
  (59130,'Subway Hearty Multigrain Bread (6")','সাবওয়ে হার্টি মাল্টিগ্রেইন রুটি (৬ ইঞ্চি)','bread',71,200,3,36,3,9,2,10),
  (59131,'Subway Jalapeno Cheddar Bread (6")','সাবওয়ে জালাপেনো চেডার রুটি (৬ ইঞ্চি)','bread',82,240,5,39,2,9,90,90),
  (59132,'Subway Artisan Flatbread','সাবওয়ে আর্টিজান ফ্ল্যাটব্রেড','bread',78,220,4,40,1,7,0,15),
  (59133,'Subway 12" Wrap Bread','সাবওয়ে ১২ ইঞ্চি র‍্যাপ রুটি','bread',102,300,8,50,2,8,6,15),
  (59134,'Subway Mini Artisan Italian Bread','সাবওয়ে মিনি আর্টিজান রুটি','bread',47,140,2,26,0,5,60,60),

  # ── INDIVIDUAL PROTEINS ────────────────────────────────────────────────────
  (59135,'Subway Grilled Chicken Protein','সাবওয়ে গ্রিলড চিকেন (প্রোটিন)','meat',71,80,2,1,0,16,0,2),
  (59136,'Subway Oven-Roasted Turkey Protein','সাবওয়ে ওভেন রোস্টেড টার্কি (প্রোটিন)','meat',57,60,2,0,0,11,0,10),
  (59137,'Subway Black Forest Ham Protein','সাবওয়ে হ্যাম (প্রোটিন)','meat',57,70,2,2,0,10,0,2),
  (59138,'Subway Tuna Protein','সাবওয়ে টুনা (প্রোটিন)','meat',74,250,23,0,0,12,0,2),
  (59139,'Subway Roast Beef Protein','সাবওয়ে রোস্ট বিফ (প্রোটিন)','meat',71,80,2,2,0,15,0,2),
  (59140,'Subway Steak Protein','সাবওয়ে স্টেক (প্রোটিন)','meat',71,110,5,2,0,17,0,6),
  (59141,'Subway Meatballs','সাবওয়ে মিটবল','meat',139,250,18,13,2,12,4,8),
  (59142,'Subway Bacon (2 strips)','সাবওয়ে ব্যাকন (২ পিস)','meat',15,80,6,1,0,5,0,2),
  (59143,'Subway Egg Patty','সাবওয়ে এগ প্যাটি','egg',85,180,15,2,0,10,2,6),
  (59144,'Subway Veggie Patty Protein','সাবওয়ে ভেজি প্যাটি (প্রোটিন)','snack',85,170,9,17,8,6,0,0),
  (59145,'Subway Rotisserie-Style Chicken','সাবওয়ে রোটিসেরি চিকেন','meat',71,90,4,0,0,15,0,2),

  # ── CONDIMENTS & SAUCES ───────────────────────────────────────────────────
  (59146,'Subway Baja Chipotle Sauce','সাবওয়ে বাজা চিপোটলে সস','snack',14,70,7,1,0,0,0,0),
  (59147,'Subway BBQ Sauce','সাবওয়ে বিবিকিউ সস','snack',14,25,0,6,0,0,0,0),
  (59148,'Subway Mayonnaise','সাবওয়ে মেয়োনিজ','snack',14,100,11,0,0,0,0,0),
  (59149,'Subway Honey Mustard Sauce','সাবওয়ে হানি মাস্টার্ড সস','snack',14,60,5,3,0,0,0,0),
  (59150,'Subway MVP Parmesan Vinaigrette','সাবওয়ে পার্মেজান ভিনেগ্রেট','snack',14,60,6,1,0,0,0,0),
  (59151,'Subway Peppercorn Ranch Sauce','সাবওয়ে পেপারকর্ন র‌্যাঞ্চ সস','snack',14,80,8,1,0,0,0,0),
  (59152,'Subway Roasted Garlic Aioli','সাবওয়ে রোস্টেড গার্লিক আইওলি','snack',14,80,9,1,0,0,0,0),
  (59153,'Subway Sweet Onion Teriyaki Sauce','সাবওয়ে সুইট অনিয়ন তেরিয়াকি সস','snack',14,30,0,7,0,0,0,0),
  (59154,'Subway Creamy Sriracha Sauce','সাবওয়ে ক্রিমি শ্রীরাচা সস','snack',14,40,4,2,0,0,2,0),
  (59155,'Subway Hot Honey Sauce','সাবওয়ে হট হানি সস','snack',14,30,0,8,0,0,0,0),
  (59156,'Subway Olive Oil Blend','সাবওয়ে অলিভ অয়েল ব্লেন্ড','snack',5,45,5,0,0,0,0,0),

  # ── COOKIES & DESSERTS ─────────────────────────────────────────────────────
  (59157,'Subway Chocolate Chip Cookie','সাবওয়ে চকোলেট চিপ কুকি','sweet',45,210,10,30,0,2,2,10),
  (59158,'Subway Double Chocolate Cookie','সাবওয়ে ডাবল চকোলেট কুকি','sweet',45,210,9,29,1,2,2,10),
  (59159,'Subway Oatmeal Raisin Cookie','সাবওয়ে ওটমিল রেজিন কুকি','sweet',45,200,8,30,1,3,2,6),
  (59160,'Subway Raspberry Cheesecake Cookie','সাবওয়ে রাসবেরি চিজকেক কুকি','sweet',45,210,9,29,0,2,2,6),
  (59161,'Subway White Chip Macadamia Nut Cookie','সাবওয়ে ম্যাকাডামিয়া নাট কুকি','sweet',45,210,10,28,0,2,2,6),

  # ── SOUPS ──────────────────────────────────────────────────────────────────
  (59162,'Subway Broccoli Cheddar Soup','সাবওয়ে ব্রকোলি চেডার স্যুপ','soup',227,200,13,16,0,9,20,2),
  (59163,'Subway Chicken Noodle Soup','সাবওয়ে চিকেন নুডল স্যুপ','soup',227,70,3,6,0,7,2,0),
  (59164,'Subway Loaded Baked Potato Soup','সাবওয়ে বেকড পটেটো স্যুপ','soup',227,200,14,17,1,9,10,2),
]

# ── European Indian items (per-100g already, add directly) ───────────────────
EUROPEAN_INDIAN = [
  {'id':59001,'en':'Chicken Bhuna (European Indian Restaurant)','bn':'চিকেন ভুনা (ইউরোপিয়ান রেস্টুরেন্ট স্টাইল)','cat':'restaurant_food','s':'100g','k':140,'p':12.0,'c':6.5,'f':7.5,'fi':1.2,'ca':18,'fe':0.9,'src':'local'},
  {'id':59002,'en':'Chicken Vindaloo (European Indian Restaurant)','bn':'চিকেন ভিন্ডালু','cat':'restaurant_food','s':'100g','k':135,'p':13.5,'c':5.0,'f':7.0,'fi':1.0,'ca':16,'fe':1.0,'src':'local'},
]

# ── Build Subway items per-100g ───────────────────────────────────────────────
SUBWAY_ITEMS = []
for row in RAW:
    fid, en, bn, cat, sv, k, fat, carb, fib, pro, ca_pct, fe_pct = row
    # Convert per-serving → per-100g
    k100  = p100(k,   sv)
    f100  = p100(fat, sv)
    c100  = p100(carb, sv)
    fi100 = p100(fib, sv)
    p100v = p100(pro, sv)
    # ca: %DV * 1300mg (Ca DV) * 100/sv_g → mg per 100g
    ca100 = round(ca_pct / 100 * 1300 * 100 / sv, 1)
    # fe: %DV * 18mg (Fe DV) * 100/sv_g → mg per 100g
    fe100 = round(fe_pct / 100 * 18 * 100 / sv, 2)
    SUBWAY_ITEMS.append({
        'id': fid, 'en': en, 'bn': bn, 'cat': cat,
        's': f'per serving ({sv}g)',
        'k': k100, 'p': p100v, 'c': c100, 'f': f100, 'fi': fi100,
        'ca': ca100, 'fe': fe100, 'src': 'subway_us',
    })

NEW_ITEMS = EUROPEAN_INDIAN + SUBWAY_ITEMS

# ── Load dataset & add ────────────────────────────────────────────────────────
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

with open(DATASET, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
print('Saved.')
