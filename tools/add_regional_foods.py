import json, sys

new_items = [
  # SOUTH INDIAN (11 items: skip Plain Dosa,Masala Dosa,Idli,Sambar,Coconut Chutney,Tomato Chutney,Curd Rice,Lemon Rice,Tamarind Rice)
  {'id':20003,'en':'Mysore Masala Dosa','bn':'মাইসোর মাসালা দোসা','cat':'breakfast','s':'100g','k':225,'p':5.7,'c':33.5,'f':7.0,'fi':2.3,'ca':24,'fe':1.5},
  {'id':20004,'en':'Rava Dosa','bn':'রাভা দোসা','cat':'breakfast','s':'100g','k':205,'p':5.0,'c':34.0,'f':5.0,'fi':1.7,'ca':16,'fe':1.3},
  {'id':20005,'en':'Onion Dosa','bn':'পেঁয়াজ দোসা','cat':'breakfast','s':'100g','k':190,'p':5.0,'c':31.0,'f':4.2,'fi':2.0,'ca':20,'fe':1.2},
  {'id':20006,'en':'Set Dosa','bn':'সেট দোসা','cat':'breakfast','s':'100g','k':195,'p':5.5,'c':32.0,'f':4.0,'fi':1.6,'ca':20,'fe':1.1},
  {'id':20008,'en':'Rava Idli','bn':'রাভা ইডলি','cat':'breakfast','s':'100g','k':180,'p':5.0,'c':28.0,'f':5.5,'fi':1.8,'ca':18,'fe':1.0},
  {'id':20009,'en':'Medu Vada','bn':'মেদু বড়া','cat':'snack','s':'100g','k':295,'p':8.0,'c':28.0,'f':16.0,'fi':4.0,'ca':42,'fe':2.0},
  {'id':20013,'en':'Pongal','bn':'পোঙ্গল','cat':'breakfast','s':'100g','k':165,'p':5.0,'c':24.0,'f':5.0,'fi':2.0,'ca':16,'fe':1.1},
  {'id':20014,'en':'Ven Pongal','bn':'ভেন পোঙ্গল','cat':'breakfast','s':'100g','k':175,'p':5.5,'c':24.0,'f':6.0,'fi':2.0,'ca':18,'fe':1.2},
  {'id':20018,'en':'Bisibele Bath','bn':'বিসিবেলে বাথ','cat':'rice','s':'100g','k':145,'p':4.5,'c':22.0,'f':4.0,'fi':2.5,'ca':20,'fe':1.0},
  {'id':20019,'en':'Upma','bn':'উপমা','cat':'breakfast','s':'100g','k':160,'p':4.5,'c':24.0,'f':5.0,'fi':2.0,'ca':14,'fe':1.0},
  {'id':20020,'en':'Pesarattu','bn':'পেসারাট্টু','cat':'breakfast','s':'100g','k':185,'p':8.0,'c':25.0,'f':5.0,'fi':4.5,'ca':35,'fe':2.5},
  # ODIA (30 items: skip in-DB and Odia-script bn fields replaced with Bengali)
  {'id':30003,'en':'Ghanta Tarkari','bn':'ঘান্টা তরকারি','cat':'vegetable','s':'100g','k':92,'p':3.0,'c':12.0,'f':3.5,'fi':4.0,'ca':45,'fe':1.4},
  {'id':30007,'en':'Dahi Pakhala','bn':'দই পখাল','cat':'rice','s':'100g','k':85,'p':2.5,'c':14.0,'f':1.8,'fi':0.2,'ca':52,'fe':0.2},
  {'id':30008,'en':'Badi Chura','bn':'বড়ি চুরা','cat':'snack','s':'100g','k':265,'p':16.0,'c':25.0,'f':11.0,'fi':6.0,'ca':68,'fe':3.2},
  {'id':30009,'en':'Chhatu Rai','bn':'ছাতু রাই','cat':'vegetable','s':'100g','k':88,'p':3.5,'c':8.5,'f':4.5,'fi':2.5,'ca':22,'fe':1.0},
  {'id':30012,'en':'Machha Jhola','bn':'মাছের ঝোল','cat':'fish','s':'100g','k':132,'p':17.0,'c':3.0,'f':5.0,'fi':0.4,'ca':36,'fe':1.0},
  {'id':30013,'en':'Chingudi Jhola','bn':'চিংড়ি ঝোল','cat':'fish','s':'100g','k':138,'p':19.5,'c':2.8,'f':5.0,'fi':0.4,'ca':92,'fe':1.3},
  {'id':30014,'en':'Chingudi Checha','bn':'চিংড়ি চেঁচা','cat':'fish','s':'100g','k':158,'p':20.0,'c':3.2,'f':7.0,'fi':0.5,'ca':88,'fe':1.4},
  {'id':30015,'en':'Crab Curry','bn':'কাঁকড়ার কারি','cat':'fish','s':'100g','k':125,'p':18.0,'c':2.5,'f':4.5,'fi':0.2,'ca':68,'fe':1.2},
  {'id':30016,'en':'Mutton Curry Odisha Style','bn':'ওড়িয়া মাটন কারি','cat':'meat','s':'100g','k':235,'p':18.5,'c':4.5,'f':16.0,'fi':0.6,'ca':24,'fe':2.6},
  {'id':30017,'en':'Mutton Kasa','bn':'মাটন কষা','cat':'meat','s':'100g','k':255,'p':19.0,'c':4.0,'f':18.0,'fi':0.5,'ca':22,'fe':2.7},
  {'id':30018,'en':'Chicken Curry Odisha Style','bn':'ওড়িয়া চিকেন কারি','cat':'meat','s':'100g','k':205,'p':19.5,'c':3.5,'f':12.5,'fi':0.4,'ca':20,'fe':1.4},
  {'id':30019,'en':'Chicken Kasa','bn':'চিকেন কষা','cat':'meat','s':'100g','k':225,'p':20.5,'c':4.0,'f':14.5,'fi':0.5,'ca':22,'fe':1.5},
  {'id':30020,'en':'Muga Dalma','bn':'মুগ ডালমা','cat':'legume','s':'100g','k':112,'p':5.8,'c':15.2,'f':2.0,'fi':3.6,'ca':36,'fe':1.7},
  {'id':30029,'en':'Kakara Pitha','bn':'কাকরা পিঠা','cat':'sweet','s':'100g','k':325,'p':4.2,'c':52.0,'f':11.0,'fi':1.0,'ca':30,'fe':0.7},
  {'id':30032,'en':'Poda Pitha','bn':'পোড়া পিঠা','cat':'sweet','s':'100g','k':285,'p':5.0,'c':48.0,'f':8.0,'fi':1.5,'ca':55,'fe':0.9},
  {'id':30033,'en':'Aloo Bharta Odisha Style','bn':'ওড়িয়া আলু ভর্তা','cat':'vegetable','s':'100g','k':105,'p':2.2,'c':16.5,'f':3.2,'fi':2.2,'ca':12,'fe':0.7},
  {'id':30034,'en':'Baigana Poda','bn':'বেগুন পোড়া','cat':'vegetable','s':'100g','k':78,'p':2.1,'c':8.2,'f':3.8,'fi':3.1,'ca':22,'fe':0.8},
  {'id':30035,'en':'Oou Khatta','bn':'ওউ খাটা','cat':'vegetable','s':'100g','k':92,'p':1.2,'c':20.0,'f':1.2,'fi':2.4,'ca':18,'fe':0.4},
  {'id':30036,'en':'Tomato Khatta','bn':'টমেটো খাটা','cat':'snack','s':'100g','k':82,'p':1.0,'c':18.0,'f':1.0,'fi':1.8,'ca':16,'fe':0.5},
  {'id':30037,'en':'Ambila','bn':'অম্বিলা','cat':'soup','s':'100g','k':58,'p':1.5,'c':10.5,'f':1.0,'fi':1.5,'ca':18,'fe':0.5},
  {'id':30038,'en':'Khata Mitha Dal','bn':'খাটা মিঠা ডাল','cat':'legume','s':'100g','k':118,'p':5.5,'c':16.5,'f':2.4,'fi':3.0,'ca':30,'fe':1.5},
  {'id':30039,'en':'Poi Saag Bhaja','bn':'পুঁই শাক ভাজা','cat':'shaak','s':'100g','k':60,'p':2.8,'c':6.5,'f':2.0,'fi':3.5,'ca':88,'fe':2.0},
  {'id':30040,'en':'Kosala Saag Bhaja','bn':'কোসলা শাক ভাজা','cat':'shaak','s':'100g','k':62,'p':3.0,'c':6.0,'f':2.1,'fi':3.7,'ca':105,'fe':2.4},
  {'id':30041,'en':'Mandia Porridge','bn':'মাণ্ডিয়া জাউ','cat':'grain','s':'100g','k':98,'p':3.0,'c':18.0,'f':1.2,'fi':2.5,'ca':120,'fe':1.8},
  {'id':30042,'en':'Mandia Pitha','bn':'মাণ্ডিয়া পিঠা','cat':'grain','s':'100g','k':215,'p':5.0,'c':40.0,'f':3.0,'fi':4.0,'ca':140,'fe':2.2},
  {'id':30043,'en':'Jagannath Mahaprasad Rice','bn':'জগন্নাথ মহাপ্রসাদ ভাত','cat':'rice','s':'100g','k':130,'p':2.5,'c':28.0,'f':0.5,'fi':0.3,'ca':8,'fe':0.3},
  {'id':30044,'en':'Mahura','bn':'মহুরা','cat':'vegetable','s':'100g','k':96,'p':3.0,'c':12.0,'f':3.5,'fi':4.2,'ca':48,'fe':1.5},
  {'id':30045,'en':'Besan Tarkari','bn':'বেসন তরকারি','cat':'vegetable','s':'100g','k':118,'p':5.5,'c':12.0,'f':5.0,'fi':2.8,'ca':34,'fe':1.8},
  {'id':30047,'en':'Prawn Besara','bn':'চিংড়ি বেসরা','cat':'fish','s':'100g','k':152,'p':19.0,'c':3.2,'f':6.0,'fi':0.5,'ca':96,'fe':1.4},
  {'id':30048,'en':'Fish Ambila','bn':'মাছ অম্বিলা','cat':'fish','s':'100g','k':138,'p':17.0,'c':3.0,'f':5.5,'fi':0.4,'ca':38,'fe':1.0},
  {'id':30049,'en':'Chingudi Malai Curry Odisha Style','bn':'ওড়িয়া চিংড়ি মালাই কারি','cat':'fish','s':'100g','k':185,'p':17.5,'c':4.5,'f':10.0,'fi':0.5,'ca':82,'fe':1.2},
  {'id':30050,'en':'Badi Chura Ghassa','bn':'বড়ি চুরা ঘষা','cat':'snack','s':'100g','k':240,'p':15.0,'c':22.0,'f':10.0,'fi':5.5,'ca':60,'fe':3.0},
  # MADHYA PRADESH (skip Poha,Mutton Keema,Chicken Korma; Sabudana Khichdi/Vada kept here, skip Maharashtra dups; Paneer Butter Masala kept here)
  {'id':40002,'en':'Indori Poha','bn':'ইন্দোরি পোহা','cat':'breakfast','s':'100g','k':195,'p':4.8,'c':35.5,'f':4.0,'fi':2.5,'ca':22,'fe':1.3},
  {'id':40003,'en':'Poha Jalebi','bn':'পোহা জেলেবি','cat':'breakfast','s':'100g','k':285,'p':4.0,'c':55.0,'f':5.8,'fi':1.8,'ca':20,'fe':1.0},
  {'id':40004,'en':'Sabudana Khichdi','bn':'সাবুদানা খিচুড়ি','cat':'breakfast','s':'100g','k':175,'p':3.5,'c':28.0,'f':5.5,'fi':1.8,'ca':15,'fe':0.8},
  {'id':40005,'en':'Sabudana Vada','bn':'সাবুদানা বড়া','cat':'snack','s':'100g','k':285,'p':5.5,'c':34.0,'f':13.0,'fi':2.0,'ca':22,'fe':1.0},
  {'id':40006,'en':'Bhutte Ka Kees','bn':'ভুট্টে কা কিস','cat':'snack','s':'100g','k':145,'p':4.0,'c':21.0,'f':5.0,'fi':2.8,'ca':18,'fe':0.9},
  {'id':40007,'en':'Dal Bafla','bn':'ডাল বাফলা','cat':'legume','s':'100g','k':220,'p':8.0,'c':31.0,'f':6.5,'fi':4.2,'ca':28,'fe':2.2},
  {'id':40008,'en':'Sev Tamatar','bn':'সেভ টমেটার','cat':'vegetable','s':'100g','k':165,'p':4.2,'c':14.0,'f':10.0,'fi':2.5,'ca':24,'fe':1.1},
  {'id':40009,'en':'Ratlami Sev','bn':'রতলামী সেভ','cat':'snack','s':'100g','k':540,'p':15.0,'c':43.0,'f':35.0,'fi':5.5,'ca':48,'fe':3.8},
  {'id':40010,'en':'Garadu','bn':'গারাডু','cat':'snack','s':'100g','k':185,'p':2.2,'c':28.0,'f':7.5,'fi':3.5,'ca':20,'fe':0.8},
  {'id':40011,'en':'Bhopali Gosht Korma','bn':'ভোপালি গোশত কোরমা','cat':'meat','s':'100g','k':245,'p':18.0,'c':4.5,'f':17.0,'fi':0.6,'ca':24,'fe':2.8},
  {'id':40013,'en':'Bhopali Chicken Curry','bn':'ভোপালি চিকেন কারি','cat':'meat','s':'100g','k':205,'p':20.0,'c':3.8,'f':12.0,'fi':0.4,'ca':20,'fe':1.4},
  {'id':40015,'en':'Paneer Butter Masala','bn':'পনির বাটার মসলা','cat':'dairy','s':'100g','k':265,'p':9.5,'c':8.5,'f':21.0,'fi':1.2,'ca':220,'fe':0.6},
  {'id':40016,'en':'Dahi Bada','bn':'দই বড়া','cat':'snack','s':'100g','k':165,'p':6.0,'c':18.0,'f':7.0,'fi':1.5,'ca':78,'fe':1.2},
  {'id':40017,'en':'Mawa Bati','bn':'মাওয়া বাটি','cat':'sweet','s':'100g','k':420,'p':8.0,'c':48.0,'f':22.0,'fi':0.0,'ca':185,'fe':0.5},
  {'id':40018,'en':'Mawa Jalebi','bn':'মাওয়া জেলেবি','cat':'sweet','s':'100g','k':435,'p':7.0,'c':60.0,'f':18.0,'fi':0.2,'ca':145,'fe':0.5},
  {'id':40019,'en':'Malpua','bn':'মালপুয়া','cat':'sweet','s':'100g','k':365,'p':5.5,'c':52.0,'f':15.0,'fi':0.8,'ca':95,'fe':0.7},
  {'id':40020,'en':'Shrikhand','bn':'শ্রিখণ্ড','cat':'sweet','s':'100g','k':255,'p':7.5,'c':28.0,'f':12.0,'fi':0.0,'ca':220,'fe':0.2},
  # MAHARASHTRA (skip Sabudana Khichdi 50006, Sabudana Vada 50007, Shrikhand 50024 - already added above)
  {'id':50001,'en':'Misal','bn':'মিসাল','cat':'breakfast','s':'100g','k':145,'p':6.5,'c':20.0,'f':4.8,'fi':4.2,'ca':42,'fe':1.8},
  {'id':50002,'en':'Misal Pav','bn':'মিসাল পাও','cat':'breakfast','s':'100g','k':210,'p':6.2,'c':32.0,'f':6.2,'fi':3.0,'ca':36,'fe':1.7},
  {'id':50003,'en':'Vada Pav','bn':'বড়া পাও','cat':'snack','s':'100g','k':295,'p':7.5,'c':40.0,'f':11.5,'fi':3.5,'ca':28,'fe':1.6},
  {'id':50004,'en':'Batata Vada','bn':'বাটাটা বড়া','cat':'snack','s':'100g','k':255,'p':5.5,'c':28.0,'f':13.0,'fi':3.2,'ca':24,'fe':1.2},
  {'id':50005,'en':'Kanda Poha','bn':'কান্দা পোহা','cat':'breakfast','s':'100g','k':180,'p':4.5,'c':33.0,'f':3.5,'fi':2.2,'ca':18,'fe':1.1},
  {'id':50008,'en':'Thalipeeth','bn':'থালিপীঠ','cat':'breakfast','s':'100g','k':240,'p':8.5,'c':34.0,'f':7.0,'fi':5.0,'ca':32,'fe':2.4},
  {'id':50009,'en':'Pithla','bn':'পিঠলা','cat':'vegetable','s':'100g','k':110,'p':5.5,'c':10.5,'f':4.5,'fi':2.2,'ca':26,'fe':1.8},
  {'id':50010,'en':'Pithla Bhakri','bn':'পিঠলা ভাকরি','cat':'bread','s':'100g','k':185,'p':6.0,'c':29.0,'f':5.0,'fi':4.5,'ca':32,'fe':2.1},
  {'id':50011,'en':'Jowar Bhakri','bn':'জোয়ার ভাকরি','cat':'bread','s':'100g','k':220,'p':6.8,'c':45.0,'f':1.8,'fi':6.0,'ca':25,'fe':2.7},
  {'id':50012,'en':'Bharli Vangi','bn':'ভরলি ভাঙ্গি','cat':'vegetable','s':'100g','k':135,'p':3.5,'c':10.5,'f':8.5,'fi':4.0,'ca':42,'fe':1.4},
  {'id':50013,'en':'Matki Usal','bn':'মাটকি উসাল','cat':'legume','s':'100g','k':125,'p':7.5,'c':18.0,'f':2.5,'fi':5.0,'ca':34,'fe':2.3},
  {'id':50014,'en':'Usal','bn':'উসাল','cat':'legume','s':'100g','k':118,'p':6.8,'c':17.0,'f':2.2,'fi':4.6,'ca':30,'fe':2.0},
  {'id':50015,'en':'Zunka','bn':'ঝুনকা','cat':'vegetable','s':'100g','k':125,'p':6.0,'c':11.0,'f':5.8,'fi':2.5,'ca':28,'fe':1.9},
  {'id':50016,'en':'Kothimbir Vadi','bn':'কোথম্বির বড়ি','cat':'snack','s':'100g','k':220,'p':8.0,'c':22.0,'f':10.0,'fi':4.5,'ca':65,'fe':2.5},
  {'id':50017,'en':'Sol Kadhi','bn':'সোল কড়ি','cat':'beverage','s':'100g','k':65,'p':1.2,'c':4.5,'f':5.0,'fi':0.5,'ca':28,'fe':0.3},
  {'id':50018,'en':'Kolhapuri Chicken','bn':'কোলহাপুরি চিকেন','cat':'meat','s':'100g','k':215,'p':20.5,'c':4.0,'f':13.0,'fi':0.8,'ca':24,'fe':1.5},
  {'id':50019,'en':'Kolhapuri Mutton','bn':'কোলহাপুরি মাটন','cat':'meat','s':'100g','k':255,'p':19.0,'c':4.5,'f':18.0,'fi':0.7,'ca':22,'fe':2.8},
  {'id':50020,'en':'Bombil Fry','bn':'বোম্বিল ভাজা','cat':'fish','s':'100g','k':190,'p':20.0,'c':4.0,'f':10.0,'fi':0.5,'ca':55,'fe':1.4},
  {'id':50021,'en':'Puran Poli','bn':'পুরণ পোলি','cat':'sweet','s':'100g','k':325,'p':8.0,'c':56.0,'f':8.0,'fi':3.2,'ca':32,'fe':2.0},
  {'id':50022,'en':'Modak','bn':'মোদক','cat':'sweet','s':'100g','k':290,'p':4.5,'c':52.0,'f':7.0,'fi':2.2,'ca':18,'fe':0.8},
  {'id':50023,'en':'Ukadiche Modak','bn':'উকাদিচে মোদক','cat':'sweet','s':'100g','k':245,'p':4.0,'c':45.0,'f':5.0,'fi':2.0,'ca':16,'fe':0.7},
  {'id':50025,'en':'Basundi','bn':'বাসুন্দি','cat':'sweet','s':'100g','k':215,'p':6.5,'c':24.0,'f':10.0,'fi':0.0,'ca':190,'fe':0.2},
  # DELHI (skip Butter Chicken,Chicken Korma,Mutton Korma,Kulfi in DB; Paneer Butter Masala skip dup of 40015)
  {'id':60001,'en':'Chole Bhature','bn':'ছোলে ভাটুরে','cat':'legume','s':'100g','k':245,'p':7.8,'c':31.5,'f':9.5,'fi':5.2,'ca':42,'fe':2.1},
  {'id':60002,'en':'Chole','bn':'ছোলে','cat':'legume','s':'100g','k':165,'p':7.5,'c':21.0,'f':5.0,'fi':5.8,'ca':48,'fe':2.4},
  {'id':60003,'en':'Bhature','bn':'ভাটুরে','cat':'bread','s':'100g','k':305,'p':7.0,'c':42.0,'f':12.0,'fi':1.8,'ca':18,'fe':1.3},
  {'id':60004,'en':'Rajma Chawal','bn':'রাজমা চাওয়াল','cat':'legume','s':'100g','k':145,'p':5.5,'c':25.0,'f':2.5,'fi':4.2,'ca':28,'fe':1.6},
  {'id':60005,'en':'Kadhi Chawal','bn':'কড়ি চাওয়াল','cat':'rice','s':'100g','k':128,'p':4.5,'c':18.5,'f':4.0,'fi':1.2,'ca':65,'fe':0.9},
  {'id':60006,'en':'Aloo Tikki','bn':'আলু টিক্কি','cat':'snack','s':'100g','k':210,'p':4.2,'c':26.0,'f':10.0,'fi':3.0,'ca':20,'fe':1.0},
  {'id':60007,'en':'Aloo Tikki Chaat','bn':'আলু টিক্কি চাট','cat':'snack','s':'100g','k':185,'p':5.0,'c':24.0,'f':8.0,'fi':3.5,'ca':55,'fe':1.4},
  {'id':60008,'en':'Papdi Chaat','bn':'পাপড়ি চাট','cat':'snack','s':'100g','k':220,'p':5.5,'c':28.0,'f':10.0,'fi':2.5,'ca':60,'fe':1.5},
  {'id':60009,'en':'Dahi Bhalla','bn':'দই ভল্লা','cat':'snack','s':'100g','k':165,'p':6.0,'c':18.0,'f':7.0,'fi':1.5,'ca':78,'fe':1.2},
  {'id':60010,'en':'Golgappa','bn':'গোলগাপ্পা','cat':'snack','s':'100g','k':155,'p':4.0,'c':29.0,'f':2.0,'fi':2.8,'ca':22,'fe':1.1},
  {'id':60011,'en':'Matar Kulcha','bn':'মটর কুলচা','cat':'legume','s':'100g','k':185,'p':6.5,'c':29.0,'f':4.5,'fi':4.2,'ca':34,'fe':1.8},
  {'id':60012,'en':'Kulcha','bn':'কুলচা','cat':'bread','s':'100g','k':265,'p':8.0,'c':48.0,'f':4.0,'fi':1.8,'ca':22,'fe':1.5},
  {'id':60014,'en':'Chicken Tikka','bn':'চিকেন টিক্কা','cat':'meat','s':'100g','k':195,'p':25.0,'c':2.5,'f':8.0,'fi':0.2,'ca':18,'fe':1.2},
  {'id':60016,'en':'Seekh Kebab','bn':'সিক কাবাব','cat':'meat','s':'100g','k':255,'p':20.0,'c':2.0,'f':18.0,'fi':0.2,'ca':24,'fe':2.5},
  {'id':60017,'en':'Shami Kebab','bn':'শামি কাবাব','cat':'meat','s':'100g','k':245,'p':18.5,'c':5.0,'f':16.0,'fi':1.0,'ca':26,'fe':2.2},
  {'id':60019,'en':'Paneer Tikka','bn':'পনির টিক্কা','cat':'dairy','s':'100g','k':250,'p':14.0,'c':6.0,'f':18.0,'fi':0.8,'ca':310,'fe':0.8},
  {'id':60021,'en':'Jalebi','bn':'জেলেবি','cat':'sweet','s':'100g','k':390,'p':2.5,'c':78.0,'f':8.0,'fi':0.0,'ca':20,'fe':0.4},
  {'id':60022,'en':'Rabri','bn':'রাবড়ি','cat':'sweet','s':'100g','k':285,'p':6.5,'c':28.0,'f':16.0,'fi':0.0,'ca':220,'fe':0.2},
  {'id':60024,'en':'Moong Dal Halwa','bn':'মুগ ডাল হালুয়া','cat':'sweet','s':'100g','k':410,'p':8.0,'c':42.0,'f':22.0,'fi':2.2,'ca':55,'fe':1.6},
  {'id':60025,'en':'Daulat Ki Chaat','bn':'দৌলত কি চাট','cat':'sweet','s':'100g','k':145,'p':4.5,'c':18.0,'f':6.0,'fi':0.0,'ca':125,'fe':0.2},
  # RAJASTHANI (skip Panchmel Dal in-DB, Sev Tamatar/Malpua/Moong Dal Halwa/Rabdi dup)
  {'id':70001,'en':'Dal Baati','bn':'ডাল বাটি','cat':'legume','s':'100g','k':225,'p':8.5,'c':30.0,'f':7.5,'fi':4.5,'ca':32,'fe':2.4},
  {'id':70002,'en':'Baati','bn':'বাটি','cat':'bread','s':'100g','k':265,'p':8.0,'c':42.0,'f':7.0,'fi':3.2,'ca':22,'fe':2.0},
  {'id':70003,'en':'Churma','bn':'চুরমা','cat':'sweet','s':'100g','k':420,'p':7.0,'c':58.0,'f':18.0,'fi':4.0,'ca':28,'fe':1.8},
  {'id':70004,'en':'Dal Baati Churma','bn':'ডাল বাটি চুরমা','cat':'legume','s':'100g','k':310,'p':8.0,'c':40.0,'f':12.0,'fi':4.0,'ca':30,'fe':2.1},
  {'id':70005,'en':'Gatte Ki Sabzi','bn':'গাট্টে কি সবজি','cat':'vegetable','s':'100g','k':165,'p':7.0,'c':12.0,'f':9.5,'fi':2.5,'ca':45,'fe':1.8},
  {'id':70006,'en':'Ker Sangri','bn':'কের সাংরি','cat':'vegetable','s':'100g','k':135,'p':4.5,'c':15.0,'f':6.0,'fi':6.0,'ca':75,'fe':2.2},
  {'id':70008,'en':'Bajra Roti','bn':'বাজরা রুটি','cat':'bread','s':'100g','k':235,'p':8.0,'c':44.0,'f':2.5,'fi':8.0,'ca':27,'fe':3.5},
  {'id':70009,'en':'Missi Roti','bn':'মিসি রুটি','cat':'bread','s':'100g','k':250,'p':9.0,'c':38.0,'f':5.0,'fi':5.0,'ca':35,'fe':2.8},
  {'id':70011,'en':'Laal Maas','bn':'লাল মাস','cat':'meat','s':'100g','k':255,'p':20.0,'c':3.0,'f':18.0,'fi':0.5,'ca':24,'fe':2.8},
  {'id':70012,'en':'Safed Maas','bn':'সাফেদ মাস','cat':'meat','s':'100g','k':275,'p':19.0,'c':4.0,'f':20.0,'fi':0.4,'ca':28,'fe':2.6},
  {'id':70013,'en':'Jungli Maas','bn':'জংলি মাস','cat':'meat','s':'100g','k':235,'p':22.0,'c':1.5,'f':16.0,'fi':0.2,'ca':20,'fe':2.7},
  {'id':70014,'en':'Mohan Maas','bn':'মোহন মাস','cat':'meat','s':'100g','k':290,'p':18.0,'c':5.0,'f':22.0,'fi':0.4,'ca':35,'fe':2.5},
  {'id':70015,'en':'Rajasthani Kadhi','bn':'রাজস্থানি কড়ি','cat':'vegetable','s':'100g','k':105,'p':4.0,'c':10.0,'f':5.5,'fi':1.0,'ca':72,'fe':0.9},
  {'id':70016,'en':'Papad Ki Sabzi','bn':'পাপড় কি সবজি','cat':'vegetable','s':'100g','k':145,'p':6.5,'c':10.0,'f':8.5,'fi':2.0,'ca':55,'fe':1.6},
  {'id':70018,'en':'Mirchi Vada','bn':'মির্চি বড়া','cat':'snack','s':'100g','k':275,'p':6.5,'c':30.0,'f':14.0,'fi':3.5,'ca':28,'fe':1.5},
  {'id':70019,'en':'Pyaz Kachori','bn':'পেঁয়াজ কচুরি','cat':'snack','s':'100g','k':360,'p':8.0,'c':40.0,'f':18.0,'fi':3.5,'ca':25,'fe':1.8},
  {'id':70020,'en':'Dal Kachori','bn':'ডাল কচুরি','cat':'snack','s':'100g','k':340,'p':9.0,'c':38.0,'f':16.0,'fi':4.0,'ca':30,'fe':2.0},
  {'id':70021,'en':'Ghevar','bn':'ঘেওয়ার','cat':'sweet','s':'100g','k':430,'p':5.0,'c':60.0,'f':18.0,'fi':0.5,'ca':85,'fe':0.8},
  {'id':70023,'en':'Mawa Kachori','bn':'মাওয়া কচুরি','cat':'sweet','s':'100g','k':445,'p':7.0,'c':52.0,'f':22.0,'fi':1.0,'ca':105,'fe':0.8},
  {'id':70024,'en':'Balushahi','bn':'বালুশাহি','cat':'sweet','s':'100g','k':425,'p':4.0,'c':65.0,'f':16.0,'fi':0.5,'ca':18,'fe':0.5},
  # NORTH BENGAL (skip Chicken Chowmein in DB)
  {'id':80001,'en':'Momo Steamed','bn':'স্টিম মোমো','cat':'snack','s':'100g','k':190,'p':8.5,'c':28.0,'f':4.5,'fi':1.5,'ca':18,'fe':1.2},
  {'id':80002,'en':'Chicken Momo','bn':'চিকেন মোমো','cat':'snack','s':'100g','k':210,'p':11.5,'c':24.0,'f':7.0,'fi':1.5,'ca':20,'fe':1.3},
  {'id':80003,'en':'Fried Momo','bn':'ফ্রাইড মোমো','cat':'snack','s':'100g','k':285,'p':9.0,'c':28.0,'f':15.0,'fi':1.5,'ca':22,'fe':1.3},
  {'id':80004,'en':'Thukpa','bn':'থুকপা','cat':'noodle','s':'100g','k':95,'p':4.0,'c':15.0,'f':2.0,'fi':1.5,'ca':18,'fe':0.8},
  {'id':80005,'en':'Chicken Thukpa','bn':'চিকেন থুকপা','cat':'noodle','s':'100g','k':110,'p':6.0,'c':14.0,'f':3.0,'fi':1.4,'ca':20,'fe':1.0},
  {'id':80006,'en':'Wai Wai Chaat','bn':'ওয়াই ওয়াই চাট','cat':'snack','s':'100g','k':315,'p':7.0,'c':42.0,'f':13.0,'fi':2.0,'ca':24,'fe':1.4},
  {'id':80007,'en':'Phaley','bn':'ফালে','cat':'bread','s':'100g','k':260,'p':8.0,'c':36.0,'f':9.0,'fi':2.0,'ca':25,'fe':1.5},
  {'id':80008,'en':'Shabaley','bn':'শাবালে','cat':'snack','s':'100g','k':295,'p':10.0,'c':30.0,'f':14.0,'fi':1.5,'ca':22,'fe':1.6},
  {'id':80009,'en':'Sel Roti','bn':'সেল রুটি','cat':'bread','s':'100g','k':345,'p':5.5,'c':62.0,'f':8.0,'fi':1.0,'ca':16,'fe':0.8},
  {'id':80010,'en':'Gundruk','bn':'গুন্দ্রুক','cat':'vegetable','s':'100g','k':42,'p':3.5,'c':6.0,'f':0.6,'fi':4.5,'ca':110,'fe':2.4},
  {'id':80011,'en':'Gundruk Soup','bn':'গুন্দ্রুক স্যুপ','cat':'soup','s':'100g','k':35,'p':2.5,'c':5.0,'f':0.5,'fi':2.5,'ca':80,'fe':1.8},
  {'id':80012,'en':'Kinema Curry','bn':'কিনেমা কারি','cat':'vegetable','s':'100g','k':145,'p':12.0,'c':8.0,'f':6.5,'fi':4.0,'ca':65,'fe':2.0},
  {'id':80013,'en':'Aloo Dum Darjeeling Style','bn':'দার্জিলিং আলুর দম','cat':'vegetable','s':'100g','k':125,'p':2.5,'c':16.0,'f':5.5,'fi':2.5,'ca':18,'fe':0.8},
  {'id':80014,'en':'Ningro Curry','bn':'নিংরো কারি','cat':'vegetable','s':'100g','k':65,'p':3.5,'c':7.0,'f':2.5,'fi':4.0,'ca':65,'fe':1.8},
  {'id':80015,'en':'Chhurpi','bn':'ছুরপি','cat':'dairy','s':'100g','k':310,'p':28.0,'c':4.0,'f':20.0,'fi':0.0,'ca':720,'fe':0.5},
  {'id':80016,'en':'Chhurpi Soup','bn':'ছুরপি স্যুপ','cat':'soup','s':'100g','k':75,'p':5.5,'c':5.0,'f':4.0,'fi':0.3,'ca':110,'fe':0.2},
  {'id':80017,'en':'Pork Curry Nepali Style','bn':'নেপালি পোর্ক কারি','cat':'meat','s':'100g','k':275,'p':19.0,'c':3.0,'f':20.0,'fi':0.5,'ca':18,'fe':1.4},
  {'id':80018,'en':'Chicken Chilli','bn':'চিকেন চিলি','cat':'meat','s':'100g','k':185,'p':17.0,'c':8.0,'f':9.0,'fi':1.0,'ca':20,'fe':1.1},
  {'id':80019,'en':'Veg Chowmein','bn':'ভেজ চাউমিন','cat':'noodle','s':'100g','k':175,'p':4.5,'c':26.0,'f':5.5,'fi':2.0,'ca':22,'fe':1.0},
  # BENGALI SPECIALS (skip Sitabhog,Mihidana,Langcha,Khaja,Kheer Kadam - all in DB)
  {'id':90105,'en':'Makha Sandesh','bn':'মাখা সন্দেশ','cat':'sweet','s':'100g','k':285,'p':10.5,'c':30.0,'f':12.0,'fi':0.0,'ca':250,'fe':0.3},
  # BIHARI (skip Sattu Drink,Ghugni in DB; Khaja dup; Malpua dup)
  {'id':95001,'en':'Litti','bn':'লিট্টি','cat':'bread','s':'100g','k':245,'p':8.5,'c':38.0,'f':6.5,'fi':5.8,'ca':38,'fe':2.6},
  {'id':95002,'en':'Litti Chokha','bn':'লিট্টি চোকা','cat':'bread','s':'100g','k':190,'p':6.5,'c':29.0,'f':5.0,'fi':4.8,'ca':32,'fe':2.0},
  {'id':95003,'en':'Baingan Chokha','bn':'বেগুন চোকা','cat':'vegetable','s':'100g','k':78,'p':2.2,'c':9.0,'f':3.5,'fi':3.5,'ca':28,'fe':0.9},
  {'id':95004,'en':'Aloo Chokha','bn':'আলু চোকা','cat':'vegetable','s':'100g','k':105,'p':2.5,'c':18.0,'f':2.5,'fi':2.5,'ca':16,'fe':0.8},
  {'id':95005,'en':'Sattu Paratha','bn':'সাত্তু পরোটা','cat':'bread','s':'100g','k':275,'p':10.0,'c':38.0,'f':8.0,'fi':6.0,'ca':42,'fe':2.8},
  {'id':95007,'en':'Dal Pitha','bn':'ডাল পিঠা','cat':'snack','s':'100g','k':185,'p':7.0,'c':30.0,'f':3.5,'fi':3.0,'ca':22,'fe':1.5},
  {'id':95008,'en':'Thekua','bn':'ঠেকুয়া','cat':'sweet','s':'100g','k':420,'p':6.0,'c':65.0,'f':16.0,'fi':2.0,'ca':22,'fe':1.3},
  {'id':95011,'en':'Kadhi Bari','bn':'কড়ি বড়ি','cat':'legume','s':'100g','k':125,'p':5.0,'c':12.0,'f':6.0,'fi':1.5,'ca':72,'fe':1.1},
  {'id':95012,'en':'Bihari Fish Curry','bn':'বিহারি মাছের ঝোল','cat':'fish','s':'100g','k':145,'p':16.5,'c':3.0,'f':7.0,'fi':0.5,'ca':32,'fe':1.2},
  {'id':95013,'en':'Champaran Mutton','bn':'চম্পারণ মাটন','cat':'meat','s':'100g','k':255,'p':18.5,'c':3.0,'f':18.0,'fi':0.5,'ca':20,'fe':2.8},
  {'id':95014,'en':'Bihari Kebab','bn':'বিহারি কাবাব','cat':'meat','s':'100g','k':235,'p':21.0,'c':3.0,'f':15.0,'fi':0.3,'ca':18,'fe':2.2},
  # JHARKHAND
  {'id':95101,'en':'Dhuska','bn':'ধুসকা','cat':'snack','s':'100g','k':255,'p':6.5,'c':35.0,'f':10.0,'fi':2.5,'ca':24,'fe':1.5},
  {'id':95102,'en':'Rugra Mushroom Curry','bn':'রুগড়া মাশরুম তরকারি','cat':'vegetable','s':'100g','k':95,'p':4.5,'c':8.0,'f':4.5,'fi':3.0,'ca':20,'fe':1.4},
  {'id':95103,'en':'Marua Roti','bn':'মাড়ুয়া রুটি','cat':'bread','s':'100g','k':235,'p':7.5,'c':44.0,'f':2.0,'fi':4.5,'ca':320,'fe':3.5},
  {'id':95104,'en':'Chilka Roti','bn':'ছিলকা রুটি','cat':'bread','s':'100g','k':215,'p':8.5,'c':35.0,'f':3.0,'fi':5.0,'ca':35,'fe':2.2},
  {'id':95105,'en':'Handia Rice Beer','bn':'হাড়িয়া','cat':'beverage','s':'100g','k':55,'p':0.8,'c':10.0,'f':0.1,'fi':0.0,'ca':6,'fe':0.1},
  {'id':95106,'en':'Bamboo Shoot Curry','bn':'বাঁশকোঁড়ল তরকারি','cat':'vegetable','s':'100g','k':68,'p':3.0,'c':7.0,'f':2.8,'fi':3.5,'ca':32,'fe':1.1},
  {'id':95107,'en':'Peetha','bn':'পিঠা','cat':'snack','s':'100g','k':195,'p':4.5,'c':38.0,'f':2.0,'fi':1.2,'ca':18,'fe':0.8},
  {'id':95108,'en':'Mutton Curry Tribal Style','bn':'আদিবাসী মাটন কারি','cat':'meat','s':'100g','k':235,'p':19.0,'c':2.5,'f':16.0,'fi':0.3,'ca':18,'fe':2.7},
  {'id':95109,'en':'Fish Curry Tribal Style','bn':'আদিবাসী মাছের ঝোল','cat':'fish','s':'100g','k':140,'p':17.0,'c':2.0,'f':6.5,'fi':0.3,'ca':28,'fe':1.1},
  {'id':95110,'en':'Arsa Roti','bn':'আরসা রুটি','cat':'sweet','s':'100g','k':390,'p':4.5,'c':70.0,'f':10.0,'fi':1.0,'ca':18,'fe':0.7},
]

# Verify no ID duplicates within batch
ids = [x['id'] for x in new_items]
id_set = set()
dups = []
for i in ids:
    if i in id_set:
        dups.append(i)
    id_set.add(i)
if dups:
    print(f'DUPLICATE IDs in batch: {dups}', file=sys.stderr)
    sys.exit(1)

print(f'New items to add: {len(new_items)}')

# Load existing data
with open('assets/data/food_master_v7_2.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

existing_ids = {item['id'] for item in data}
conflicts = [x for x in new_items if x['id'] in existing_ids]
if conflicts:
    print(f'ID conflicts with existing: {[x["id"] for x in conflicts]}', file=sys.stderr)
    sys.exit(1)

existing_en = {item['en'].lower() for item in data}
name_conflicts = [x for x in new_items if x['en'].lower() in existing_en]
if name_conflicts:
    print(f'Name conflicts: {[x["en"] for x in name_conflicts]}', file=sys.stderr)
    sys.exit(1)

data.extend(new_items)
with open('assets/data/food_master_v7_2.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

print(f'Total items after: {len(data)}')
print('Done.')
