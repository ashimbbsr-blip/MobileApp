"""
add_brand_products.py — Add branded packaged food products to food_master_v7_2.json

Brands: Amul (54001-54015), Britannia (51001-51015), Parle (52001-52012),
        Coca-Cola (53001-53015), PepsiCo (53101-53120),
        Cadbury (53201-53220), OMFED (53301-53315)

Note: Amul IDs reassigned from 50001-50015 → 54001-54015 (50xxx conflicts with Maharashtra foods)
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

NEW_ITEMS = [
  # ── AMUL (54001-54015) ───────────────────────────────────────────────────
  {'id':54001,'en':'Amul Gold Milk','bn':'আমুল গোল্ড দুধ','brand':'Amul','cat':'dairy','s':'100ml','k':87,'p':3.0,'c':5.0,'f':6.0,'fi':0.0,'ca':120,'fe':0.0,'src':'brand'},
  {'id':54002,'en':'Amul Taaza Milk','bn':'আমুল তাজা দুধ','brand':'Amul','cat':'dairy','s':'100ml','k':58,'p':3.0,'c':4.7,'f':3.0,'fi':0.0,'ca':110,'fe':0.0,'src':'brand'},
  {'id':54003,'en':'Amul Cow Milk','bn':'আমুল গরুর দুধ','brand':'Amul','cat':'dairy','s':'100ml','k':69,'p':3.1,'c':4.9,'f':4.0,'fi':0.0,'ca':116,'fe':0.0,'src':'brand'},
  {'id':54004,'en':'Amul Fresh Paneer','bn':'আমুল ফ্রেশ পনির','brand':'Amul','cat':'paneer','s':'100g','k':296,'p':20.0,'c':4.5,'f':22.0,'fi':0.0,'ca':480,'fe':0.0,'src':'brand'},
  {'id':54005,'en':'Amul Butter','bn':'আমুল বাটার','brand':'Amul','cat':'butter','s':'100g','k':724,'p':0.5,'c':0.0,'f':80.7,'fi':0.0,'ca':18,'fe':0.0,'src':'brand'},
  {'id':54006,'en':'Amul Ghee','bn':'আমুল ঘি','brand':'Amul','cat':'ghee','s':'100g','k':900,'p':0.0,'c':0.0,'f':100.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':54007,'en':'Amul Cheese','bn':'আমুল চিজ','brand':'Amul','cat':'cheese','s':'100g','k':311,'p':20.0,'c':4.8,'f':25.0,'fi':0.0,'ca':700,'fe':0.2,'src':'brand'},
  {'id':54008,'en':'Amul Cheese Slice','bn':'আমুল চিজ স্লাইস','brand':'Amul','cat':'cheese','s':'100g','k':311,'p':20.0,'c':4.8,'f':25.0,'fi':0.0,'ca':700,'fe':0.2,'src':'brand'},
  {'id':54009,'en':'Amul Masti Dahi','bn':'আমুল মাস্তি দই','brand':'Amul','cat':'curd','s':'100g','k':65,'p':3.1,'c':4.4,'f':3.8,'fi':0.0,'ca':120,'fe':0.1,'src':'brand'},
  {'id':54010,'en':'Amul Curd','bn':'আমুল দই','brand':'Amul','cat':'curd','s':'100g','k':61,'p':3.4,'c':4.5,'f':3.1,'fi':0.0,'ca':120,'fe':0.1,'src':'brand'},
  {'id':54011,'en':'Amul Buttermilk','bn':'আমুল বাটারমিল্ক','brand':'Amul','cat':'beverage','s':'100ml','k':23,'p':1.2,'c':2.5,'f':0.8,'fi':0.0,'ca':80,'fe':0.0,'src':'brand'},
  {'id':54012,'en':'Amul Lassi','bn':'আমুল লস্যি','brand':'Amul','cat':'beverage','s':'100ml','k':87,'p':3.0,'c':12.8,'f':3.0,'fi':0.0,'ca':110,'fe':0.0,'src':'brand'},
  {'id':54013,'en':'Amul Fresh Cream','bn':'আমুল ফ্রেশ ক্রিম','brand':'Amul','cat':'dairy','s':'100ml','k':310,'p':2.2,'c':4.2,'f':30.0,'fi':0.0,'ca':80,'fe':0.1,'src':'brand'},
  {'id':54014,'en':'Amul Mithai Mate','bn':'আমুল মিঠাই মেট','brand':'Amul','cat':'dessert','s':'100g','k':327,'p':8.0,'c':55.0,'f':8.5,'fi':0.0,'ca':280,'fe':0.2,'src':'brand'},
  {'id':54015,'en':'Amul Slim n Trim Milk','bn':'আমুল স্লিম এন ট্রিম দুধ','brand':'Amul','cat':'dairy','s':'100ml','k':35,'p':3.1,'c':5.0,'f':0.5,'fi':0.0,'ca':120,'fe':0.0,'src':'brand'},
  # ── BRITANNIA (51001-51015) ──────────────────────────────────────────────
  {'id':51001,'en':'Britannia Marie Gold','bn':'ব্রিটানিয়া মেরি গোল্ড','brand':'Britannia','cat':'biscuit','s':'100g','k':445,'p':7.8,'c':77.0,'f':11.5,'fi':2.5,'ca':35,'fe':3.2,'src':'brand'},
  {'id':51002,'en':'Britannia Good Day Butter Cookies','bn':'ব্রিটানিয়া গুড ডে বাটার কুকিজ','brand':'Britannia','cat':'biscuit','s':'100g','k':520,'p':6.0,'c':65.0,'f':26.0,'fi':2.0,'ca':28,'fe':2.0,'src':'brand'},
  {'id':51003,'en':'Britannia Good Day Cashew','bn':'ব্রিটানিয়া গুড ডে কাজু','brand':'Britannia','cat':'biscuit','s':'100g','k':520,'p':6.3,'c':65.5,'f':25.5,'fi':2.2,'ca':42,'fe':2.1,'src':'brand'},
  {'id':51004,'en':'Britannia Bourbon','bn':'ব্রিটানিয়া বোরবন','brand':'Britannia','cat':'biscuit','s':'100g','k':492,'p':5.9,'c':67.0,'f':22.0,'fi':2.8,'ca':40,'fe':3.1,'src':'brand'},
  {'id':51005,'en':'Britannia Milk Bikis','bn':'ব্রিটানিয়া মিল্ক বিকিস','brand':'Britannia','cat':'biscuit','s':'100g','k':467,'p':7.0,'c':70.0,'f':18.0,'fi':2.0,'ca':150,'fe':3.0,'src':'brand'},
  {'id':51006,'en':'Britannia NutriChoice Digestive','bn':'ব্রিটানিয়া নিউট্রিচয়েস ডাইজেস্টিভ','brand':'Britannia','cat':'biscuit','s':'100g','k':483,'p':8.5,'c':60.0,'f':22.5,'fi':9.8,'ca':52,'fe':3.6,'src':'brand'},
  {'id':51007,'en':'Britannia 50-50','bn':'ব্রিটানিয়া ৫০-৫০','brand':'Britannia','cat':'biscuit','s':'100g','k':487,'p':6.8,'c':67.5,'f':21.0,'fi':2.3,'ca':28,'fe':2.4,'src':'brand'},
  {'id':51008,'en':'Britannia 50-50 Maska Chaska','bn':'ব্রিটানিয়া ৫০-৫০ মাস্কা চাস্কা','brand':'Britannia','cat':'biscuit','s':'100g','k':525,'p':6.2,'c':63.5,'f':28.0,'fi':2.0,'ca':30,'fe':2.2,'src':'brand'},
  {'id':51009,'en':'Britannia Jim Jam','bn':'ব্রিটানিয়া জিম জ্যাম','brand':'Britannia','cat':'biscuit','s':'100g','k':483,'p':5.5,'c':69.0,'f':20.5,'fi':1.8,'ca':34,'fe':2.2,'src':'brand'},
  {'id':51010,'en':'Britannia Little Hearts','bn':'ব্রিটানিয়া লিটল হার্টস','brand':'Britannia','cat':'biscuit','s':'100g','k':486,'p':5.8,'c':68.0,'f':21.5,'fi':2.1,'ca':26,'fe':2.3,'src':'brand'},
  {'id':51011,'en':'Britannia Tiger Original','bn':'ব্রিটানিয়া টাইগার অরিজিনাল','brand':'Britannia','cat':'biscuit','s':'100g','k':455,'p':7.2,'c':73.0,'f':15.0,'fi':2.1,'ca':32,'fe':3.2,'src':'brand'},
  {'id':51012,'en':'Britannia Whole Wheat Bread','bn':'ব্রিটানিয়া হোল হুইট ব্রেড','brand':'Britannia','cat':'bread','s':'100g','k':245,'p':8.8,'c':45.5,'f':3.4,'fi':6.5,'ca':120,'fe':3.5,'src':'brand'},
  {'id':51013,'en':'Britannia Brown Bread','bn':'ব্রিটানিয়া ব্রাউন ব্রেড','brand':'Britannia','cat':'bread','s':'100g','k':246,'p':8.5,'c':46.0,'f':3.2,'fi':6.2,'ca':110,'fe':3.4,'src':'brand'},
  {'id':51014,'en':'Britannia Cheese Slices','bn':'ব্রিটানিয়া চিজ স্লাইস','brand':'Britannia','cat':'cheese','s':'100g','k':315,'p':20.0,'c':5.0,'f':25.0,'fi':0.0,'ca':700,'fe':0.2,'src':'brand'},
  {'id':51015,'en':'Britannia Suji Rusk','bn':'ব্রিটানিয়া সুজি রাস্ক','brand':'Britannia','cat':'rusk','s':'100g','k':433,'p':10.5,'c':72.0,'f':11.2,'fi':2.5,'ca':42,'fe':2.8,'src':'brand'},
  # ── PARLE (52001-52012) ──────────────────────────────────────────────────
  {'id':52001,'en':'Parle-G Original','bn':'পার্লে-জি অরিজিনাল','brand':'Parle','cat':'biscuit','s':'100g','k':451,'p':6.8,'c':78.2,'f':11.5,'fi':1.5,'ca':30,'fe':3.5,'src':'brand'},
  {'id':52002,'en':'Parle Monaco Classic','bn':'পার্লে মোনাকো ক্লাসিক','brand':'Parle','cat':'biscuit','s':'100g','k':489,'p':8.0,'c':66.0,'f':21.0,'fi':2.2,'ca':32,'fe':3.0,'src':'brand'},
  {'id':52003,'en':'Parle Krackjack','bn':'পার্লে ক্র্যাকজ্যাক','brand':'Parle','cat':'biscuit','s':'100g','k':500,'p':7.0,'c':67.0,'f':23.0,'fi':2.1,'ca':35,'fe':3.0,'src':'brand'},
  {'id':52004,'en':'Parle Hide & Seek Chocolate Chip','bn':'পার্লে হাইড অ্যান্ড সিক চকোলেট চিপ','brand':'Parle','cat':'cookie','s':'100g','k':531,'p':5.8,'c':62.5,'f':29.0,'fi':2.7,'ca':40,'fe':3.2,'src':'brand'},
  {'id':52005,'en':'Parle Hide & Seek Fab Chocolate','bn':'পার্লে হাইড অ্যান্ড সিক ফ্যাব চকোলেট','brand':'Parle','cat':'cookie','s':'100g','k':528,'p':6.0,'c':61.8,'f':29.2,'fi':2.8,'ca':42,'fe':3.1,'src':'brand'},
  {'id':52006,'en':'Parle 20-20 Butter Cookies','bn':'পার্লে ২০-২০ বাটার কুকিজ','brand':'Parle','cat':'cookie','s':'100g','k':522,'p':6.3,'c':64.5,'f':27.0,'fi':2.0,'ca':38,'fe':2.9,'src':'brand'},
  {'id':52007,'en':'Parle Milk Shakti','bn':'পার্লে মিল্ক শক্তি','brand':'Parle','cat':'biscuit','s':'100g','k':463,'p':8.2,'c':72.0,'f':15.2,'fi':2.1,'ca':220,'fe':4.2,'src':'brand'},
  {'id':52008,'en':'Parle Kreams Orange','bn':'পার্লে ক্রিমস অরেঞ্জ','brand':'Parle','cat':'biscuit','s':'100g','k':503,'p':5.5,'c':68.0,'f':23.0,'fi':1.8,'ca':28,'fe':2.5,'src':'brand'},
  {'id':52009,'en':'Parle Kreams Chocolate','bn':'পার্লে ক্রিমস চকোলেট','brand':'Parle','cat':'biscuit','s':'100g','k':506,'p':5.6,'c':67.2,'f':23.5,'fi':1.9,'ca':30,'fe':2.6,'src':'brand'},
  {'id':52010,'en':'Parle Top Cookies','bn':'পার্লে টপ কুকিজ','brand':'Parle','cat':'cookie','s':'100g','k':519,'p':6.2,'c':65.0,'f':26.5,'fi':2.0,'ca':35,'fe':2.8,'src':'brand'},
  {'id':52011,'en':'Parle Melody','bn':'পার্লে মেলোডি','brand':'Parle','cat':'candy','s':'100g','k':414,'p':1.2,'c':92.5,'f':4.0,'fi':0.0,'ca':18,'fe':0.4,'src':'brand'},
  {'id':52012,'en':'Parle Mango Bite','bn':'পার্লে ম্যাঙ্গো বাইট','brand':'Parle','cat':'candy','s':'100g','k':392,'p':0.2,'c':97.0,'f':0.3,'fi':0.0,'ca':6,'fe':0.2,'src':'brand'},
  # ── COCA-COLA (53001-53015) ──────────────────────────────────────────────
  {'id':53001,'en':'Coca-Cola Original Taste','bn':'কোকা-কোলা অরিজিনাল','brand':'Coca-Cola','cat':'beverage','s':'100ml','k':42,'p':0.0,'c':10.6,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53002,'en':'Coca-Cola Zero Sugar','bn':'কোকা-কোলা জিরো সুগার','brand':'Coca-Cola','cat':'beverage','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53003,'en':'Thums Up','bn':'থামস আপ','brand':'Coca-Cola','cat':'beverage','s':'100ml','k':44,'p':0.0,'c':11.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53004,'en':'Thums Up XForce','bn':'থামস আপ এক্সফোর্স','brand':'Coca-Cola','cat':'energy_drink','s':'100ml','k':44,'p':0.0,'c':11.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53005,'en':'Sprite','bn':'স্প্রাইট','brand':'Coca-Cola','cat':'beverage','s':'100ml','k':41,'p':0.0,'c':10.3,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53006,'en':'Sprite Zero Sugar','bn':'স্প্রাইট জিরো সুগার','brand':'Coca-Cola','cat':'beverage','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53007,'en':'Fanta Orange','bn':'ফ্যান্টা অরেঞ্জ','brand':'Coca-Cola','cat':'beverage','s':'100ml','k':48,'p':0.0,'c':12.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53008,'en':'Limca','bn':'লিমকা','brand':'Coca-Cola','cat':'beverage','s':'100ml','k':42,'p':0.0,'c':10.5,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53009,'en':'Limca GlucoCharge','bn':'লিমকা গ্লুকোচার্জ','brand':'Coca-Cola','cat':'sports_drink','s':'100ml','k':27,'p':0.0,'c':6.8,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53010,'en':'Maaza Mango Drink','bn':'মাজা ম্যাঙ্গো ড্রিংক','brand':'Coca-Cola','cat':'juice','s':'100ml','k':61,'p':0.2,'c':15.2,'f':0.0,'fi':0.2,'ca':8,'fe':0.1,'src':'brand'},
  {'id':53011,'en':'Minute Maid Pulpy Orange','bn':'মিনিট মেইড পাল্পি অরেঞ্জ','brand':'Coca-Cola','cat':'juice','s':'100ml','k':48,'p':0.3,'c':11.8,'f':0.0,'fi':0.3,'ca':10,'fe':0.1,'src':'brand'},
  {'id':53012,'en':'Minute Maid Apple','bn':'মিনিট মেইড আপেল','brand':'Coca-Cola','cat':'juice','s':'100ml','k':46,'p':0.1,'c':11.4,'f':0.0,'fi':0.1,'ca':8,'fe':0.1,'src':'brand'},
  {'id':53013,'en':'Schweppes Soda Water','bn':'শ্‌ওয়েপস সোডা ওয়াটার','brand':'Coca-Cola','cat':'water','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53014,'en':'Kinley Soda','bn':'কিনলে সোডা','brand':'Coca-Cola','cat':'water','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53015,'en':'Kinley Packaged Drinking Water','bn':'কিনলে প্যাকেটজাত পানীয় জল','brand':'Coca-Cola','cat':'water','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  # ── PEPSICO (53101-53120) ────────────────────────────────────────────────
  {'id':53101,'en':'Pepsi','bn':'পেপসি','brand':'PepsiCo','cat':'beverage','s':'100ml','k':42,'p':0.0,'c':10.6,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53102,'en':'Pepsi Black','bn':'পেপসি ব্ল্যাক','brand':'PepsiCo','cat':'beverage','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53103,'en':'7UP','bn':'সেভেন আপ','brand':'PepsiCo','cat':'beverage','s':'100ml','k':42,'p':0.0,'c':10.5,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53104,'en':'7UP Zero Sugar','bn':'সেভেন আপ জিরো সুগার','brand':'PepsiCo','cat':'beverage','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53105,'en':'Mirinda Orange','bn':'মিরিন্ডা অরেঞ্জ','brand':'PepsiCo','cat':'beverage','s':'100ml','k':48,'p':0.0,'c':12.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53106,'en':'Mountain Dew','bn':'মাউন্টেন ডিউ','brand':'PepsiCo','cat':'beverage','s':'100ml','k':46,'p':0.0,'c':11.5,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53107,'en':'Mountain Dew Ice','bn':'মাউন্টেন ডিউ আইস','brand':'PepsiCo','cat':'beverage','s':'100ml','k':42,'p':0.0,'c':10.5,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53108,'en':'Mountain Dew Zero Sugar','bn':'মাউন্টেন ডিউ জিরো সুগার','brand':'PepsiCo','cat':'beverage','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53109,'en':'Slice Mango Drink','bn':'স্লাইস ম্যাঙ্গো ড্রিংক','brand':'PepsiCo','cat':'juice','s':'100ml','k':60,'p':0.2,'c':15.0,'f':0.0,'fi':0.2,'ca':8,'fe':0.1,'src':'brand'},
  {'id':53110,'en':'Tropicana Orange Delight','bn':'ট্রপিকানা অরেঞ্জ ডিলাইট','brand':'PepsiCo','cat':'juice','s':'100ml','k':45,'p':0.5,'c':10.8,'f':0.0,'fi':0.2,'ca':11,'fe':0.1,'src':'brand'},
  {'id':53111,'en':'Tropicana Mixed Fruit Delight','bn':'ট্রপিকানা মিক্সড ফ্রুট ডিলাইট','brand':'PepsiCo','cat':'juice','s':'100ml','k':48,'p':0.4,'c':11.5,'f':0.0,'fi':0.3,'ca':10,'fe':0.2,'src':'brand'},
  {'id':53112,'en':'Tropicana Apple Delight','bn':'ট্রপিকানা আপেল ডিলাইট','brand':'PepsiCo','cat':'juice','s':'100ml','k':46,'p':0.2,'c':11.2,'f':0.0,'fi':0.2,'ca':8,'fe':0.1,'src':'brand'},
  {'id':53113,'en':'Tropicana Guava Delight','bn':'ট্রপিকানা পেয়ারা ডিলাইট','brand':'PepsiCo','cat':'juice','s':'100ml','k':49,'p':0.3,'c':12.0,'f':0.0,'fi':0.3,'ca':12,'fe':0.2,'src':'brand'},
  {'id':53114,'en':'Tropicana Litchi Delight','bn':'ট্রপিকানা লিচু ডিলাইট','brand':'PepsiCo','cat':'juice','s':'100ml','k':50,'p':0.2,'c':12.4,'f':0.0,'fi':0.2,'ca':9,'fe':0.1,'src':'brand'},
  {'id':53115,'en':'Gatorade Lemon','bn':'গেটোরেড লেমন','brand':'PepsiCo','cat':'sports_drink','s':'100ml','k':24,'p':0.0,'c':6.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53116,'en':'Gatorade Orange','bn':'গেটোরেড অরেঞ্জ','brand':'PepsiCo','cat':'sports_drink','s':'100ml','k':24,'p':0.0,'c':6.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53117,'en':'Aquafina Packaged Drinking Water','bn':'অ্যাকোয়াফিনা প্যাকেটজাত পানীয় জল','brand':'PepsiCo','cat':'water','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53118,'en':'Aquafina Soda','bn':'অ্যাকোয়াফিনা সোডা','brand':'PepsiCo','cat':'water','s':'100ml','k':0,'p':0.0,'c':0.0,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53119,'en':'Sting Energy Drink','bn':'স্টিং এনার্জি ড্রিংক','brand':'PepsiCo','cat':'energy_drink','s':'100ml','k':47,'p':0.0,'c':11.8,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  {'id':53120,'en':'Sting Gold Rush','bn':'স্টিং গোল্ড রাশ','brand':'PepsiCo','cat':'energy_drink','s':'100ml','k':47,'p':0.0,'c':11.8,'f':0.0,'fi':0.0,'ca':0,'fe':0.0,'src':'brand'},
  # ── CADBURY (53201-53220) ────────────────────────────────────────────────
  {'id':53201,'en':'Cadbury Dairy Milk','bn':'ক্যাডবেরি ডেইরি মিল্ক','brand':'Cadbury','cat':'chocolate','s':'100g','k':534,'p':7.3,'c':57.5,'f':30.0,'fi':2.1,'ca':230,'fe':2.2,'src':'brand'},
  {'id':53202,'en':'Cadbury Dairy Milk Silk','bn':'ক্যাডবেরি ডেইরি মিল্ক সিল্ক','brand':'Cadbury','cat':'chocolate','s':'100g','k':548,'p':6.9,'c':55.5,'f':33.5,'fi':2.2,'ca':240,'fe':2.3,'src':'brand'},
  {'id':53203,'en':'Cadbury Dairy Milk Fruit & Nut','bn':'ক্যাডবেরি ডেইরি মিল্ক ফ্রুট অ্যান্ড নাট','brand':'Cadbury','cat':'chocolate','s':'100g','k':530,'p':7.5,'c':54.0,'f':31.0,'fi':3.8,'ca':225,'fe':2.5,'src':'brand'},
  {'id':53204,'en':'Cadbury Dairy Milk Crackle','bn':'ক্যাডবেরি ডেইরি মিল্ক ক্র্যাকল','brand':'Cadbury','cat':'chocolate','s':'100g','k':531,'p':7.2,'c':58.0,'f':29.5,'fi':2.2,'ca':228,'fe':2.2,'src':'brand'},
  {'id':53205,'en':'Cadbury Dairy Milk Roast Almond','bn':'ক্যাডবেরি ডেইরি মিল্ক রোস্ট আলমন্ড','brand':'Cadbury','cat':'chocolate','s':'100g','k':540,'p':8.2,'c':52.5,'f':32.0,'fi':4.2,'ca':235,'fe':2.6,'src':'brand'},
  {'id':53206,'en':'Cadbury Dairy Milk Whole Nut','bn':'ক্যাডবেরি ডেইরি মিল্ক হোল নাট','brand':'Cadbury','cat':'chocolate','s':'100g','k':545,'p':8.6,'c':50.5,'f':34.0,'fi':4.8,'ca':238,'fe':2.7,'src':'brand'},
  {'id':53207,'en':'Cadbury Dairy Milk Silk Oreo','bn':'ক্যাডবেরি সিল্ক ওরিও','brand':'Cadbury','cat':'chocolate','s':'100g','k':550,'p':6.5,'c':56.0,'f':34.0,'fi':2.0,'ca':235,'fe':2.3,'src':'brand'},
  {'id':53208,'en':'Cadbury Dairy Milk Silk Fruit & Nut','bn':'ক্যাডবেরি সিল্ক ফ্রুট অ্যান্ড নাট','brand':'Cadbury','cat':'chocolate','s':'100g','k':547,'p':7.3,'c':54.0,'f':33.8,'fi':3.5,'ca':236,'fe':2.5,'src':'brand'},
  {'id':53209,'en':'Cadbury Dairy Milk Silk Bubbly','bn':'ক্যাডবেরি সিল্ক বাবলি','brand':'Cadbury','cat':'chocolate','s':'100g','k':545,'p':6.8,'c':55.0,'f':33.2,'fi':2.0,'ca':232,'fe':2.2,'src':'brand'},
  {'id':53210,'en':'Cadbury 5 Star','bn':'ক্যাডবেরি ফাইভ স্টার','brand':'Cadbury','cat':'chocolate','s':'100g','k':488,'p':5.1,'c':63.0,'f':24.0,'fi':1.5,'ca':170,'fe':1.8,'src':'brand'},
  {'id':53211,'en':'Cadbury 5 Star Oreo','bn':'ক্যাডবেরি ফাইভ স্টার ওরিও','brand':'Cadbury','cat':'chocolate','s':'100g','k':495,'p':5.2,'c':62.0,'f':25.0,'fi':1.8,'ca':172,'fe':1.9,'src':'brand'},
  {'id':53212,'en':'Cadbury Perk','bn':'ক্যাডবেরি পার্ক','brand':'Cadbury','cat':'chocolate','s':'100g','k':515,'p':5.8,'c':63.5,'f':26.0,'fi':2.2,'ca':160,'fe':2.0,'src':'brand'},
  {'id':53213,'en':'Cadbury Perk Double','bn':'ক্যাডবেরি পার্ক ডাবল','brand':'Cadbury','cat':'chocolate','s':'100g','k':520,'p':5.9,'c':63.0,'f':26.5,'fi':2.3,'ca':162,'fe':2.0,'src':'brand'},
  {'id':53214,'en':'Cadbury Gems','bn':'ক্যাডবেরি জেমস','brand':'Cadbury','cat':'chocolate','s':'100g','k':500,'p':4.8,'c':71.0,'f':21.0,'fi':1.3,'ca':140,'fe':1.5,'src':'brand'},
  {'id':53215,'en':'Cadbury Fuse','bn':'ক্যাডবেরি ফিউজ','brand':'Cadbury','cat':'chocolate','s':'100g','k':510,'p':8.5,'c':55.0,'f':28.0,'fi':3.8,'ca':180,'fe':2.4,'src':'brand'},
  {'id':53216,'en':'Cadbury Bournville Classic','bn':'ক্যাডবেরি বর্নভিল ক্লাসিক','brand':'Cadbury','cat':'dark_chocolate','s':'100g','k':540,'p':6.8,'c':46.0,'f':36.0,'fi':8.5,'ca':60,'fe':11.0,'src':'brand'},
  {'id':53217,'en':'Cadbury Bournville Cranberry','bn':'ক্যাডবেরি বর্নভিল ক্র্যানবেরি','brand':'Cadbury','cat':'dark_chocolate','s':'100g','k':535,'p':6.5,'c':48.0,'f':35.0,'fi':8.2,'ca':62,'fe':10.5,'src':'brand'},
  {'id':53218,'en':'Cadbury Bournville Raisin & Nut','bn':'ক্যাডবেরি বর্নভিল কিশমিশ ও বাদাম','brand':'Cadbury','cat':'dark_chocolate','s':'100g','k':545,'p':7.4,'c':47.0,'f':36.5,'fi':8.8,'ca':68,'fe':10.8,'src':'brand'},
  {'id':53219,'en':'Cadbury Choclairs Gold','bn':'ক্যাডবেরি চকলেয়ার্স গোল্ড','brand':'Cadbury','cat':'candy','s':'100g','k':430,'p':2.5,'c':75.0,'f':12.0,'fi':0.5,'ca':90,'fe':0.8,'src':'brand'},
  {'id':53220,'en':'Cadbury Eclairs','bn':'ক্যাডবেরি ইক্লেয়ার্স','brand':'Cadbury','cat':'candy','s':'100g','k':425,'p':2.4,'c':76.0,'f':11.0,'fi':0.4,'ca':88,'fe':0.8,'src':'brand'},
  # ── OMFED (53301-53315) ──────────────────────────────────────────────────
  {'id':53301,'en':'OMFED Premium Cow Milk','bn':'ওমফেড প্রিমিয়াম গরুর দুধ','brand':'OMFED','cat':'dairy','s':'100ml','k':64,'p':3.3,'c':4.8,'f':3.5,'fi':0.0,'ca':155,'fe':0.0,'src':'brand'},
  {'id':53302,'en':'OMFED Toned Milk','bn':'ওমফেড টোনড মিল্ক','brand':'OMFED','cat':'dairy','s':'100ml','k':58,'p':3.0,'c':4.8,'f':3.0,'fi':0.0,'ca':110,'fe':0.0,'src':'brand'},
  {'id':53303,'en':'OMFED Gold Premium Milk','bn':'ওমফেড গোল্ড প্রিমিয়াম মিল্ক','brand':'OMFED','cat':'dairy','s':'100ml','k':70,'p':3.3,'c':4.8,'f':4.5,'fi':0.0,'ca':120,'fe':0.0,'src':'brand'},
  {'id':53304,'en':'OMFED A2 Desi Cow Milk','bn':'ওমফেড এ২ দেশি গরুর দুধ','brand':'OMFED','cat':'dairy','s':'100ml','k':60,'p':3.1,'c':4.8,'f':3.2,'fi':0.0,'ca':120,'fe':0.0,'src':'brand'},
  {'id':53305,'en':'OMFED Plus UHT Milk','bn':'ওমফেড ইউএইচটি মিল্ক','brand':'OMFED','cat':'dairy','s':'100ml','k':58,'p':3.0,'c':4.8,'f':3.0,'fi':0.0,'ca':110,'fe':0.0,'src':'brand'},
  {'id':53306,'en':'OMFED Plain Curd','bn':'ওমফেড টক দই','brand':'OMFED','cat':'curd','s':'100g','k':61,'p':3.5,'c':4.7,'f':3.0,'fi':0.0,'ca':120,'fe':0.1,'src':'brand'},
  {'id':53307,'en':'OMFED Sweet Curd','bn':'ওমফেড মিষ্টি দই','brand':'OMFED','cat':'curd','s':'100g','k':145,'p':3.8,'c':24.0,'f':3.8,'fi':0.0,'ca':130,'fe':0.1,'src':'brand'},
  {'id':53308,'en':'OMFED Lassi','bn':'ওমফেড লাচ্ছি','brand':'OMFED','cat':'beverage','s':'100ml','k':78,'p':2.8,'c':11.5,'f':2.5,'fi':0.0,'ca':100,'fe':0.1,'src':'brand'},
  {'id':53309,'en':'OMFED Buttermilk','bn':'ওমফেড ঘোল','brand':'OMFED','cat':'beverage','s':'100ml','k':40,'p':2.2,'c':4.5,'f':1.2,'fi':0.0,'ca':80,'fe':0.0,'src':'brand'},
  {'id':53310,'en':'OMFED Flavo Elaichi','bn':'ওমফেড এলাচি ফ্লেভার মিল্ক','brand':'OMFED','cat':'beverage','s':'100ml','k':84,'p':3.1,'c':12.5,'f':2.8,'fi':0.0,'ca':120,'fe':0.0,'src':'brand'},
  {'id':53311,'en':'OMFED Flavo Kesar','bn':'ওমফেড কেশর ফ্লেভার মিল্ক','brand':'OMFED','cat':'beverage','s':'100ml','k':85,'p':3.1,'c':12.7,'f':2.8,'fi':0.0,'ca':120,'fe':0.0,'src':'brand'},
  {'id':53312,'en':'OMFED Paneer','bn':'ওমফেড পনির','brand':'OMFED','cat':'paneer','s':'100g','k':296,'p':18.5,'c':2.5,'f':23.0,'fi':0.0,'ca':208,'fe':0.4,'src':'brand'},
  {'id':53313,'en':'OMFED Table Butter','bn':'ওমফেড বাটার','brand':'OMFED','cat':'butter','s':'100g','k':717,'p':0.8,'c':0.6,'f':81.0,'fi':0.0,'ca':24,'fe':0.0,'src':'brand'},
  {'id':53314,'en':'OMFED Ghee','bn':'ওমফেড ঘি','brand':'OMFED','cat':'ghee','s':'100g','k':900,'p':0.0,'c':0.0,'f':100.0,'fi':0.0,'ca':2,'fe':0.0,'src':'brand'},
  {'id':53315,'en':'OMFED Dairy Whitener','bn':'ওমফেড ডেইরি হোয়াইটনার','brand':'OMFED','cat':'milk_powder','s':'100g','k':500,'p':24.0,'c':39.0,'f':27.0,'fi':0.0,'ca':900,'fe':0.3,'src':'brand'},
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
