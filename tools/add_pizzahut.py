import json, sys
sys.stdout.reconfigure(encoding='utf-8')

path = 'assets/data/food_master_v7_2.json'
data = json.load(open(path, encoding='utf-8'))

def ps(id_, en, bn, w, n, k, c, p, fi, f):
    sw = round(w / n, 1)
    kws = list({t.lower() for t in en.split()} | {'pizza','pizzahut','পিৎজা'})
    return {'id':id_,'en':en,'bn':bn,'cat':'pizza','s':f'{sw}g',
            'k':round(k/n,1),'p':round(p/n,1),'c':round(c/n,1),
            'f':round(f/n,1),'fi':round(fi/n,1),
            'ca':0.0,'fe':0.0,'zn':0.0,'kw':kws,'src':'pizzahut_india'}

def ph(id_, en, bn, w, k, c, p, fi, f, cat):
    kws = list({t.lower() for t in en.split()} | {'pizzahut'})
    return {'id':id_,'en':en,'bn':bn,'cat':cat,'s':f'{w}g',
            'k':k,'p':p,'c':c,'f':f,'fi':fi,
            'ca':0.0,'fe':0.0,'zn':0.0,'kw':kws,'src':'pizzahut_india'}

# ---- Pan Pizza Personal (4 slices) IDs 98001-98029 ----
pan_p = [
    ('Margherita Pan Pizza (Personal)','মার্ঘেরিটা প্যান পিৎজা (পার্সোনাল)',248,725.1,101.6,31.9,8.2,21.2),
    ('Schezwan Margherita Pan Pizza (Personal)','শেজওয়ান মার্ঘেরিটা পিৎজা (পার্সোনাল)',248,743.7,104.0,31.7,9.0,22.3),
    ('Corn n Cheese Pan Pizza (Personal)','কর্ন এন চিজ পিৎজা (পার্সোনাল)',272,869.1,131.9,36.0,7.7,22.0),
    ('Veggie Feast Pan Pizza (Personal)','ভেজি ফিস্ট পিৎজা (পার্সোনাল)',306,822.8,122.1,35.8,8.5,21.2),
    ('Spiced Paneer Pan Pizza (Personal)','স্পাইসড পনির পিৎজা (পার্সোনাল)',296,815.5,95.0,43.3,13.8,29.1),
    ('Mexican Fiesta Veg Pan Pizza (Personal)','মেক্সিকান ফিয়েস্তা পিৎজা (পার্সোনাল)',322,855.6,108.9,36.9,9.8,30.3),
    ('Tandoori Paneer Pan Pizza (Personal)','তান্দুরি পনির পিৎজা (পার্সোনাল)',318,1064.7,152.8,35.7,14.1,34.5),
    ('Country Feast Pan Pizza (Personal)','কান্ট্রি ফিস্ট পিৎজা (পার্সোনাল)',334,815.2,134.2,33.5,14.4,16.1),
    ('Ultimate Tandoori Veggie Pan Pizza (Personal)','আল্টিমেট তান্দুরি ভেজি পিৎজা (পার্সোনাল)',340,1067.5,156.4,32.3,11.2,34.7),
    ('Veggie Supreme Pan Pizza (Personal)','ভেজি সুপ্রিম পিৎজা (পার্সোনাল)',336,853.2,110.8,35.5,8.9,28.8),
    ('Mazedar Makhni Paneer Pan Pizza (Personal)','মজেদার মাখনি পনির পিৎজা (পার্সোনাল)',306,879.9,100.7,40.1,8.5,35.2),
    ('Royal Spice Paneer Pan Pizza (Personal)','রয়েল স্পাইস পনির পিৎজা (পার্সোনাল)',359,895.1,101.2,40.2,14.6,36.6),
    ('Kadhai Paneer Pan Pizza (Personal)','কড়াই পনির পিৎজা (পার্সোনাল)',355,1170.8,171.5,39.8,14.6,36.2),
    ('Southern Fiery Paneer Pan Pizza (Personal)','সাউদার্ন ফায়ারি পনির পিৎজা (পার্সোনাল)',363,1197.5,175.3,41.6,14.7,36.7),
    ('Bold BBQ Veggies Pan Pizza (Personal)','বোল্ড বিবিকিউ ভেজি পিৎজা (পার্সোনাল)',322,779.1,108.2,38.5,10.2,21.4),
    ('Chicken Sausage Pan Pizza (Personal)','চিকেন সোসেজ পিৎজা (পার্সোনাল)',288,891.5,98.5,36.2,9.4,39.2),
    ('Sausage Sweet Corn Pan Pizza (Personal)','সোসেজ সুইট কর্ন পিৎজা (পার্সোনাল)',300,829.8,105.7,37.5,19.5,28.5),
    ('Sizzling Schezwan Chicken Pan Pizza (Personal)','সিজলিং শেজওয়ান চিকেন পিৎজা (পার্সোনাল)',276,763.2,99.8,40.0,13.5,22.7),
    ('Dhabe Da Keema Pan Pizza (Personal)','ধাবে দা কিমা পিৎজা (পার্সোনাল)',320,864.7,99.5,40.0,13.7,34.1),
    ('Chicken Pepperoni Pan Pizza (Personal)','চিকেন পেপারোনি পিৎজা (পার্সোনাল)',292,877.6,100.7,29.7,9.5,39.5),
    ('Chicken Tikka Pan Pizza (Personal)','চিকেন টিক্কা পিৎজা (পার্সোনাল)',288,792.5,97.2,35.3,13.7,29.2),
    ('Murg Malai Chicken Pan Pizza (Personal)','মুর্গ মালাই চিকেন পিৎজা (পার্সোনাল)',316,850.9,108.0,43.2,7.8,27.3),
    ('Chicken Supreme Pan Pizza (Personal)','চিকেন সুপ্রিম পিৎজা (পার্সোনাল)',326,890.7,94.8,47.8,10.4,35.6),
    ('Chicken Tikka Supreme Pan Pizza (Personal)','চিকেন টিক্কা সুপ্রিম পিৎজা (পার্সোনাল)',326,870.7,99.1,45.1,8.6,32.7),
    ('Nawabi Murg Makhni Pan Pizza (Personal)','নবাবি মুর্গ মাখনি পিৎজা (পার্সোনাল)',346,870.4,103.5,44.1,13.2,31.1),
    ('Triple Chicken Feast Pan Pizza (Personal)','ট্রিপল চিকেন ফিস্ট পিৎজা (পার্সোনাল)',368,963.9,90.8,48.3,10.9,45.3),
    ('Royal Spice Chicken Pan Pizza (Personal)','রয়েল স্পাইস চিকেন পিৎজা (পার্সোনাল)',358,990.2,121.0,44.4,15.9,36.5),
    ('Kadhai Chicken Pan Pizza (Personal)','কড়াই চিকেন পিৎজা (পার্সোনাল)',350,955.2,116.9,42.4,15.1,35.4),
    ('Southern Fiery Chicken Pan Pizza (Personal)','সাউদার্ন ফায়ারি চিকেন পিৎজা (পার্সোনাল)',354,977.7,128.9,50.3,16.7,29.0),
]

# ---- Pan Pizza Medium (6 slices) IDs 98030-98058 ----
pan_m = [
    ('Margherita Pan Pizza (Medium)','মার্ঘেরিটা প্যান পিৎজা (মিডিয়াম)',471,1377.1,193.0,60.7,15.5,40.3),
    ('Schezwan Margherita Pan Pizza (Medium)','শেজওয়ান মার্ঘেরিটা পিৎজা (মিডিয়াম)',471,1412.4,197.5,60.3,17.0,42.4),
    ('Corn n Cheese Pan Pizza (Medium)','কর্ন এন চিজ পিৎজা (মিডিয়াম)',525,1677.4,254.5,69.4,14.9,42.4),
    ('Veggie Feast Pan Pizza (Medium)','ভেজি ফিস্ট পিৎজা (মিডিয়াম)',597,1605.3,238.3,69.8,16.7,41.4),
    ('Spiced Paneer Pan Pizza (Medium)','স্পাইসড পনির পিৎজা (মিডিয়াম)',579,1595.2,185.9,84.8,27.1,56.9),
    ('Mexican Fiesta Veg Pan Pizza (Medium)','মেক্সিকান ফিয়েস্তা পিৎজা (মিডিয়াম)',621,1650.2,210.1,71.2,18.8,58.4),
    ('Tandoori Paneer Pan Pizza (Medium)','তান্দুরি পনির পিৎজা (মিডিয়াম)',612,2049.1,294.1,68.6,27.2,66.5),
    ('Country Feast Pan Pizza (Medium)','কান্ট্রি ফিস্ট পিৎজা (মিডিয়াম)',672,1640.2,270.0,67.3,28.9,32.3),
    ('Ultimate Tandoori Veggie Pan Pizza (Medium)','আল্টিমেট তান্দুরি ভেজি পিৎজা (মিডিয়াম)',657,2062.9,302.3,62.4,21.6,67.1),
    ('Veggie Supreme Pan Pizza (Medium)','ভেজি সুপ্রিম পিৎজা (মিডিয়াম)',651,1653.1,214.7,68.8,17.2,55.9),
    ('Mazedar Makhni Paneer Pan Pizza (Medium)','মজেদার মাখনি পনির পিৎজা (মিডিয়াম)',600,1725.4,197.4,78.6,16.7,69.1),
    ('Bold BBQ Veggies Pan Pizza (Medium)','বোল্ড বিবিকিউ ভেজি পিৎজা (মিডিয়াম)',612,1480.8,205.7,73.2,19.5,40.6),
    ('Royal Spice Paneer Pan Pizza (Medium)','রয়েল স্পাইস পনির পিৎজা (মিডিয়াম)',720,1795.1,202.9,80.6,29.4,73.4),
    ('Kadhai Paneer Pan Pizza (Medium)','কড়াই পনির পিৎজা (মিডিয়াম)',709,2338.3,342.4,79.4,29.2,72.3),
    ('Southern Fiery Paneer Pan Pizza (Medium)','সাউদার্ন ফায়ারি পনির পিৎজা (মিডিয়াম)',727,2398.4,351.1,83.2,29.4,73.4),
    ('Chicken Sausage Pan Pizza (Medium)','চিকেন সোসেজ পিৎজা (মিডিয়াম)',549,1699.5,187.7,69.0,17.9,74.7),
    ('Sausage Sweet Corn Pan Pizza (Medium)','সোসেজ সুইট কর্ন পিৎজা (মিডিয়াম)',582,1609.7,205.1,72.7,37.9,55.4),
    ('Sizzling Schezwan Chicken Pan Pizza (Medium)','সিজলিং শেজওয়ান চিকেন পিৎজা (মিডিয়াম)',528,1460.0,190.9,76.5,25.9,43.4),
    ('Dhabe Da Keema Pan Pizza (Medium)','ধাবে দা কিমা পিৎজা (মিডিয়াম)',615,1661.8,191.2,76.8,26.4,65.5),
    ('Chicken Pepperoni Pan Pizza (Medium)','চিকেন পেপারোনি পিৎজা (মিডিয়াম)',561,1686.1,193.6,57.0,18.2,76.0),
    ('Chicken Tikka Pan Pizza (Medium)','চিকেন টিক্কা পিৎজা (মিডিয়াম)',642,1766.5,216.8,78.6,30.6,65.0),
    ('Murg Malai Chicken Pan Pizza (Medium)','মুর্গ মালাই চিকেন পিৎজা (মিডিয়াম)',612,1647.9,209.1,83.8,15.1,52.9),
    ('Chicken Supreme Pan Pizza (Medium)','চিকেন সুপ্রিম পিৎজা (মিডিয়াম)',642,1754.1,186.6,94.1,20.4,70.1),
    ('Chicken Tikka Supreme Pan Pizza (Medium)','চিকেন টিক্কা সুপ্রিম পিৎজা (মিডিয়াম)',633,1690.6,192.4,87.5,16.8,63.5),
    ('Nawabi Murg Makhni Pan Pizza (Medium)','নবাবি মুর্গ মাখনি পিৎজা (মিডিয়াম)',678,1705.5,202.7,86.4,25.9,61.0),
    ('Triple Chicken Feast Pan Pizza (Medium)','ট্রিপল চিকেন ফিস্ট পিৎজা (মিডিয়াম)',717,1878.1,177.0,94.1,21.3,88.2),
    ('Royal Spice Chicken Pan Pizza (Medium)','রয়েল স্পাইস চিকেন পিৎজা (মিডিয়াম)',702,1941.7,237.3,87.0,31.2,71.6),
    ('Kadhai Chicken Pan Pizza (Medium)','কড়াই চিকেন পিৎজা (মিডিয়াম)',684,1866.6,228.5,82.8,29.4,69.1),
    ('Southern Fiery Chicken Pan Pizza (Medium)','সাউদার্ন ফায়ারি চিকেন পিৎজা (মিডিয়াম)',695,1919.6,253.0,98.7,32.7,57.0),
]

# ---- Pan Pizza Large (8 slices) IDs 98059-98088 ----
pan_l = [
    ('Margherita Pan Pizza (Large)','মার্ঘেরিটা প্যান পিৎজা (লার্জ)',776,2268.8,317.9,99.9,25.6,66.4),
    ('Schezwan Margherita Pan Pizza (Large)','শেজওয়ান মার্ঘেরিটা পিৎজা (লার্জ)',796,2386.9,333.8,101.9,28.7,71.6),
    ('Corn n Cheese Pan Pizza (Large)','কর্ন এন চিজ পিৎজা (লার্জ)',852,2722.2,413.0,112.7,24.2,68.8),
    ('Veggie Feast Pan Pizza (Large)','ভেজি ফিস্ট পিৎজা (লার্জ)',972,2613.6,388.0,113.7,27.1,67.4),
    ('Spiced Paneer Pan Pizza (Large)','স্পাইসড পনির পিৎজা (লার্জ)',948,2611.8,304.3,138.8,44.3,93.2),
    ('Mexican Fiesta Veg Pan Pizza (Large)','মেক্সিকান ফিয়েস্তা পিৎজা (লার্জ)',1004,2667.9,339.6,115.1,30.4,94.4),
    ('Tandoori Paneer Pan Pizza (Large)','তান্দুরি পনির পিৎজা (লার্জ)',1000,3348.1,480.6,112.2,44.5,108.6),
    ('Country Feast Pan Pizza (Large)','কান্ট্রি ফিস্ট পিৎজা (লার্জ)',1088,2655.5,437.2,109.0,46.9,52.3),
    ('Ultimate Tandoori Veggie Pan Pizza (Large)','আল্টিমেট তান্দুরি ভেজি পিৎজা (লার্জ)',1068,3353.4,491.3,101.5,35.1,109.1),
    ('Veggie Supreme Pan Pizza (Large)','ভেজি সুপ্রিম পিৎজা (লার্জ)',1056,2681.5,348.2,111.6,27.9,90.6),
    ('Mazedar Makhni Paneer Pan Pizza (Large)','মজেদার মাখনি পনির পিৎজা (লার্জ)',984,2829.6,323.7,128.9,27.4,113.3),
    ("Farmer's Pick Pan Pizza (Large)","ফার্মার্স পিক পিৎজা (লার্জ)",1056,2580.4,341.0,125.9,15.5,79.2),
    ('Veg Exotica Pan Pizza (Large)','ভেজ এক্সোটিকা পিৎজা (লার্জ)',1000,2255.3,341.4,85.0,30.2,61.1),
    ('Royal Spice Paneer Pan Pizza (Large)','রয়েল স্পাইস পনির পিৎজা (লার্জ)',1161,2951.4,352.6,116.8,48.8,130.1),
    ('Kadhai Paneer Pan Pizza (Large)','কড়াই পনির পিৎজা (লার্জ)',1146,2848.5,323.4,119.9,35.4,136.7),
    ('Southern Fiery Paneer Pan Pizza (Large)','সাউদার্ন ফায়ারি পনির পিৎজা (লার্জ)',1152,2742.0,337.1,112.6,45.6,115.0),
    ('Chicken Sausage Pan Pizza (Large)','চিকেন সোসেজ পিৎজা (লার্জ)',904,2798.4,309.1,113.6,29.5,123.1),
    ('Sausage Sweet Corn Pan Pizza (Large)','সোসেজ সুইট কর্ন পিৎজা (লার্জ)',924,2555.6,325.7,115.4,60.1,87.9),
    ('Sizzling Schezwan Chicken Pan Pizza (Large)','সিজলিং শেজওয়ান চিকেন পিৎজা (লার্জ)',820,2267.4,296.5,118.9,40.2,67.3),
    ('Dhabe Da Keema Pan Pizza (Large)','ধাবে দা কিমা পিৎজা (লার্জ)',992,2680.6,308.4,124.0,42.5,105.7),
    ('Chicken Pepperoni Pan Pizza (Large)','চিকেন পেপারোনি পিৎজা (লার্জ)',924,2777.1,318.8,93.9,30.0,125.1),
    ('Chicken Tikka Pan Pizza (Large)','চিকেন টিক্কা পিৎজা (লার্জ)',1016,2795.6,343.0,124.4,48.4,102.9),
    ('Murg Malai Chicken Pan Pizza (Large)','মুর্গ মালাই চিকেন পিৎজা (লার্জ)',1016,2735.8,347.1,139.1,25.1,87.9),
    ('Chicken Supreme Pan Pizza (Large)','চিকেন সুপ্রিম পিৎজা (লার্জ)',1056,2885.3,307.0,154.7,33.5,115.2),
    # fat corrected: PDF shows 10.0g; kcal balance gives (2809.6-319.7*4-145.4*4)/9 = 105.5g
    ('Chicken Tikka Supreme Pan Pizza (Large)','চিকেন টিক্কা সুপ্রিম পিৎজা (লার্জ)',1052,2809.6,319.7,145.4,27.9,105.5),
    ('Nawabi Murg Makhni Pan Pizza (Large)','নবাবি মুর্গ মাখনি পিৎজা (লার্জ)',1132,2847.5,338.5,144.3,43.3,101.8),
    ('Triple Chicken Feast Pan Pizza (Large)','ট্রিপল চিকেন ফিস্ট পিৎজা (লার্জ)',1164,3048.9,287.3,152.8,34.6,143.2),
    ('Royal Spice Chicken Pan Pizza (Large)','রয়েল স্পাইস চিকেন পিৎজা (লার্জ)',1116,2650.2,355.3,104.7,36.4,98.1),
    ('Kadhai Chicken Pan Pizza (Large)','কড়াই চিকেন পিৎজা (লার্জ)',1101,2967.1,275.5,209.2,37.4,117.7),
    ('Southern Fiery Chicken Pan Pizza (Large)','সাউদার্ন ফায়ারি চিকেন পিৎজা (লার্জ)',1107,2666.3,327.7,106.2,35.6,111.4),
]

# ---- TnC Pizza (8 slices) IDs 98089-98117 ----
tnc = [
    ('Margherita TnC Pizza','মার্ঘেরিটা টিএনসি পিৎজা',380,1112.8,152.9,49.8,13.0,33.4),
    ('Schezwan Margherita TnC Pizza','শেজওয়ান মার্ঘেরিটা টিএনসি পিৎজা',384,1187.1,166.6,48.7,14.8,36.9),
    ('Corn n Cheese TnC Pizza','কর্ন এন চিজ টিএনসি পিৎজা',432,1312.8,180.6,58.8,15.3,39.5),
    ('Veggie Feast TnC Pizza','ভেজি ফিস্ট টিএনসি পিৎজা',504,1380.7,198.2,63.3,19.7,35.9),
    ('Spiced Paneer TnC Pizza','স্পাইসড পনির টিএনসি পিৎজা',492,1392.4,168.0,69.4,20.9,49.3),
    ('Mexican Fiesta TnC Pizza','মেক্সিকান ফিয়েস্তা টিএনসি পিৎজা',536,1384.4,182.2,60.9,16.6,46.0),
    ('Tandoori Paneer TnC Pizza','তান্দুরি পনির টিএনসি পিৎজা',520,1693.4,224.9,69.6,23.0,57.0),
    ('Country Feast TnC Pizza','কান্ট্রি ফিস্ট টিএনসি পিৎজা',560,1580.7,261.6,72.5,24.2,43.3),
    ('Ultimate Tandoori Veggie TnC Pizza','আল্টিমেট তান্দুরি ভেজি টিএনসি পিৎজা',580,2288.6,236.3,59.5,19.4,58.4),
    ('Veggie Supreme TnC Pizza','ভেজি সুপ্রিম টিএনসি পিৎজা',568,1464.2,193.1,59.9,15.7,50.3),
    ('Mazedar Makhni Paneer TnC Pizza','মজেদার মাখনি পনির টিএনসি পিৎজা',512,1482.4,168.1,65.9,15.1,61.2),
    ('Royal Spice Paneer TnC Pizza','রয়েল স্পাইস পনির টিএনসি পিৎজা',656,1718.1,186.7,78.6,25.8,78.7),
    ('Kadhai Paneer TnC Pizza','কড়াই পনির টিএনসি পিৎজা',638,1692.1,183.7,82.6,19.0,73.9),
    ('Southern Fiery Paneer TnC Pizza','সাউদার্ন ফায়ারি পনির টিএনসি পিৎজা',646,1633.2,208.9,65.2,26.4,65.5),
    ('Bold BBQ Veggies TnC Pizza','বোল্ড বিবিকিউ ভেজি টিএনসি পিৎজা',524,1391.3,182.2,78.0,16.8,39.1),
    ('Dhabe Da Keema TnC Pizza','ধাবে দা কিমা টিএনসি পিৎজা',660,1916.7,227.5,79.7,27.7,76.9),
    ('Sausage Sweet Corn TnC Pizza','সোসেজ সুইট কর্ন টিএনসি পিৎজা',496,1396.4,181.3,61.0,28.7,49.1),
    ('Sizzling Schezwan Chicken TnC Pizza','সিজলিং শেজওয়ান চিকেন টিএনসি পিৎজা',440,1259.2,170.0,64.8,20.7,36.3),
    ('Nawabi Murg Makhni TnC Pizza','নবাবি মুর্গ মাখনি টিএনসি পিৎজা',592,1592.3,192.7,75.9,22.9,57.3),
    ('Murg Malai Chicken TnC Pizza','মুর্গ মালাই চিকেন টিএনসি পিৎজা',524,1567.8,169.0,70.2,14.1,68.0),
    ('Triple Chicken Feast TnC Pizza','ট্রিপল চিকেন ফিস্ট টিএনসি পিৎজা',632,1748.2,175.9,82.5,18.0,79.2),
    ('Chicken Supreme TnC Pizza','চিকেন সুপ্রিম টিএনসি পিৎজা',560,1590.2,177.8,83.2,20.2,60.7),
    ('Chicken Tikka Supreme TnC Pizza','চিকেন টিক্কা সুপ্রিম টিএনসি পিৎজা',548,1501.2,173.9,77.4,15.6,55.1),
    ('Chicken Sausage TnC Pizza','চিকেন সোসেজ টিএনসি পিৎজা',460,1434.3,159.5,58.1,18.0,62.6),
    ('Chicken Pepperoni TnC Pizza','চিকেন পেপারোনি টিএনসি পিৎজা',448,1395.1,165.2,46.1,16.5,61.1),
    ('Chicken Tikka TnC Pizza','চিকেন টিক্কা টিএনসি পিৎজা',528,1491.7,186.2,67.4,25.1,53.0),
    ('Southern Fiery Chicken TnC Pizza','সাউদার্ন ফায়ারি চিকেন টিএনসি পিৎজা',616,1444.3,159.4,75.6,20.5,60.6),
    ('Kadhai Chicken TnC Pizza','কড়াই চিকেন টিএনসি পিৎজা',608,1590.0,183.4,82.9,22.0,63.2),
    ('Royal Spice Chicken TnC Pizza','রয়েল স্পাইস চিকেন টিএনসি পিৎজা',626,1543.3,179.5,82.8,21.0,59.6),
]

# ---- Ultimate Cheese Personal (4 slices) IDs 98118-98123 ----
uc_p = [
    ('Margherita Ultimate Cheese Pizza (Personal)','মার্ঘেরিটা আল্টিমেট চিজ পিৎজা (পার্সোনাল)',342,970.9,136.7,42.0,10.7,30.8),
    ('Veggie Supreme Ultimate Cheese Pizza (Personal)','ভেজি সুপ্রিম আল্টিমেট চিজ পিৎজা (পার্সোনাল)',437,1103.7,146.1,43.2,10.5,40.9),
    ('Tandoori Paneer Ultimate Cheese Pizza (Personal)','তান্দুরি পনির আল্টিমেট চিজ পিৎজা (পার্সোনাল)',416,1436.7,204.4,48.6,17.7,51.1),
    ('Triple Chicken Feast Ultimate Cheese Pizza (Personal)','ট্রিপল চিকেন আল্টিমেট চিজ পিৎজা (পার্সোনাল)',468,1218.4,122.5,62.8,12.5,55.8),
    ('Chicken Sausage Ultimate Cheese Pizza (Personal)','চিকেন সোসেজ আল্টিমেট চিজ পিৎজা (পার্সোনাল)',384,1132.9,131.8,45.9,11.9,49.2),
    ('Chicken Tikka Ultimate Cheese Pizza (Personal)','চিকেন টিক্কা আল্টিমেট চিজ পিৎজা (পার্সোনাল)',415,1152.4,145.6,50.4,18.5,43.3),
]

# ---- Ultimate Cheese Medium (6 slices) IDs 98124-98129 ----
uc_m = [
    ('Veggie Supreme Ultimate Cheese Pizza (Medium)','ভেজি সুপ্রিম আল্টিমেট চিজ পিৎজা (মিডিয়াম)',809,2043.3,270.4,79.9,19.5,75.6),
    ('Tandoori Paneer Ultimate Cheese Pizza (Medium)','তান্দুরি পনির আল্টিমেট চিজ পিৎজা (মিডিয়াম)',763,2635.0,374.9,89.1,32.4,93.8),
    ('Margherita Ultimate Cheese Pizza (Medium)','মার্ঘেরিটা আল্টিমেট চিজ পিৎজা (মিডিয়াম)',617,1751.5,246.6,75.7,19.3,55.7),
    ('Triple Chicken Feast Ultimate Cheese Pizza (Medium)','ট্রিপল চিকেন আল্টিমেট চিজ পিৎজা (মিডিয়াম)',879,2288.5,230.0,117.9,23.5,104.9),
    ('Chicken Sausage Ultimate Cheese Pizza (Medium)','চিকেন সোসেজ আল্টিমেট চিজ পিৎজা (মিডিয়াম)',703,2074.0,241.4,84.0,21.7,90.1),
    ('Chicken Tikka Ultimate Cheese Pizza (Medium)','চিকেন টিক্কা আল্টিমেট চিজ পিৎজা (মিডিয়াম)',771,2141.0,270.4,93.6,34.3,80.4),
]

new_foods = []
for i,(en,bn,w,k,c,p,fi,f) in enumerate(pan_p):
    new_foods.append(ps(98001+i,en,bn,w,4,k,c,p,fi,f))
for i,(en,bn,w,k,c,p,fi,f) in enumerate(pan_m):
    new_foods.append(ps(98030+i,en,bn,w,6,k,c,p,fi,f))
for i,(en,bn,w,k,c,p,fi,f) in enumerate(pan_l):
    new_foods.append(ps(98059+i,en,bn,w,8,k,c,p,fi,f))
for i,(en,bn,w,k,c,p,fi,f) in enumerate(tnc):
    new_foods.append(ps(98089+i,en,bn,w,8,k,c,p,fi,f))
for i,(en,bn,w,k,c,p,fi,f) in enumerate(uc_p):
    new_foods.append(ps(98118+i,en,bn,w,4,k,c,p,fi,f))
for i,(en,bn,w,k,c,p,fi,f) in enumerate(uc_m):
    new_foods.append(ps(98124+i,en,bn,w,6,k,c,p,fi,f))

# ---- Crafted Flatzz (whole item) IDs 98130-98136 ----
new_foods += [
    ph(98130,'Paneer Makhni Masala Flatzz','পনির মাখনি মাসালা ফ্ল্যাটজ',427,1165.6,151.6,44.0,13.2,45.5,'pizza'),
    ph(98131,'Overloaded Veggies Flatzz','ওভারলোডেড ভেজি ফ্ল্যাটজ',467,1134.1,143.7,51.0,14.6,42.7,'pizza'),
    ph(98132,'Fiery Schezwan Veggie Flatzz','ফায়ারি শেজওয়ান ভেজি ফ্ল্যাটজ',411,1083.7,136.5,49.0,13.4,40.9,'pizza'),
    ph(98133,'Smokey BBQ Veggie Flatzz','স্মোকি বিবিকিউ ভেজি ফ্ল্যাটজ',421,1084.4,137.3,47.5,12.5,41.2,'pizza'),
    ph(98134,'Keema Masala Flatzz','কিমা মাসালা ফ্ল্যাটজ',436,1202.7,144.4,52.1,15.2,49.6,'pizza'),
    ph(98135,'Ultimate Chicken Flatzz','আল্টিমেট চিকেন ফ্ল্যাটজ',472,1208.7,142.4,56.7,18.1,49.8,'pizza'),
    ph(98136,'Tandoori Chicken Flatzz','তান্দুরি চিকেন ফ্ল্যাটজ',473,1221.0,148.2,57.2,18.3,48.4,'pizza'),
]

# ---- Melts (per 2-piece) IDs 98137-98144 ----
new_foods += [
    ph(98137,'Cheezy Cheese Veg Melt','চিজি চিজ ভেজ মেল্ট',244,723.0,98.2,22.7,7.7,26.6,'snack'),
    ph(98138,'Cheezy Cheese Chicken Melt','চিজি চিজ চিকেন মেল্ট',260,698.0,86.1,25.7,8.4,30.4,'snack'),
    ph(98139,'Loaded Veggie BBQ Melt','লোডেড ভেজি বিবিকিউ মেল্ট',272,694.7,101.0,18.6,9.0,24.4,'snack'),
    ph(98140,'Loaded Chicken BBQ Melt','লোডেড চিকেন বিবিকিউ মেল্ট',294,970.5,129.8,32.6,10.0,35.7,'snack'),
    ph(98141,'Royal Spice Paneer Melt','রয়েল স্পাইস পনির মেল্ট',254,697.7,77.7,28.7,7.6,30.2,'snack'),
    ph(98142,'Kadhai Paneer Melt','কড়াই পনির মেল্ট',272,734.1,82.7,30.5,6.5,31.3,'snack'),
    ph(98143,'Kadhai Chicken Melt','কড়াই চিকেন মেল্ট',280,926.2,123.8,31.9,9.0,33.7,'snack'),
    ph(98144,'Royal Spice Chicken Melt','রয়েল স্পাইস চিকেন মেল্ট',284,951.0,127.8,32.6,9.1,34.4,'snack'),
]

# ---- Flavour Fun Pizza (4 slices) IDs 98145-98153 ----
ff = [
    ('Classic Corn Flavour Fun Pizza','ক্লাসিক কর্ন ফ্লেভার ফান পিৎজা',248,790.7,105.9,17.2,11.8,33.1),
    ('Classic Onion Capsicum Flavour Fun Pizza','ক্লাসিক অনিয়ন ক্যাপসিকাম পিৎজা',254,780.5,110.3,16.3,9.1,30.4),
    ('Chatpata Chicken Feast Flavour Fun Pizza','চাটপাটা চিকেন ফ্লেভার ফান পিৎজা',304,892.3,117.4,25.6,7.3,35.6),
    ('Classic Herbed Chicken Capsicum Pizza','ক্লাসিক হার্বড চিকেন ক্যাপসিকাম পিৎজা',266,880.5,105.4,25.5,7.9,39.6),
    ('Cheesy Spicy Delight Pizza','চিজি স্পাইসি ডিলাইট পিৎজা',240,881.2,100.9,31.3,7.6,39.1),
    ('Spicy Sweetcorn Onion Chilli Pizza','স্পাইসি সুইটকর্ন অনিয়ন চিলি পিৎজা',268,875.7,117.1,20.8,8.0,36.0),
    ('Chatpata Tomato Onion Chilli Pizza','চাটপাটা টমেটো অনিয়ন চিলি পিৎজা',266,873.0,114.6,19.9,7.4,37.2),
    ('Chilli Paneer Sizzle Pizza','চিলি পনির সিজল পিৎজা',298,887.7,114.8,25.7,21.8,36.2),
    ('Classic Chicken Pepperoni Onion Pizza','ক্লাসিক চিকেন পেপারোনি পিৎজা',256,850.4,113.8,18.6,13.8,35.6),
]
for i,(en,bn,w,k,c,p,fi,f) in enumerate(ff):
    new_foods.append(ps(98145+i,en,bn,w,4,k,c,p,fi,f))

# ---- Chicken Wings IDs 98154-98161 ----
new_foods += [
    ph(98154,'Spicy Baked Chicken Wings (4pc)','স্পাইসি বেকড চিকেন উইংস (৪ পিস)',148,280.4,13.5,28.2,3.4,17.4,'meat'),
    ph(98155,'BBQ Chicken Wings (4pc)','বিবিকিউ চিকেন উইংস (৪ পিস)',178,367.4,18.4,34.5,4.9,17.4,'meat'),
    ph(98156,'Spicy Baked Chicken Wings (6pc)','স্পাইসি বেকড চিকেন উইংস (৬ পিস)',222,420.6,20.3,42.4,5.1,26.1,'meat'),
    ph(98157,'BBQ Chicken Wings (6pc)','বিবিকিউ চিকেন উইংস (৬ পিস)',267,551.2,27.5,51.7,7.3,26.0,'meat'),
    ph(98158,'Baked Royal Spice Chicken Wings (6pc)','বেকড রয়েল স্পাইস উইংস (৬ পিস)',237,542.3,25.1,46.5,5.7,28.4,'meat'),
    ph(98159,'Baked Royal Spice Chicken Wings (4pc)','বেকড রয়েল স্পাইস উইংস (৪ পিস)',157,359.2,16.6,30.8,3.8,18.8,'meat'),
    ph(98160,'Baked Southern Fiery Chicken Wings (6pc)','বেকড সাউদার্ন ফায়ারি উইংস (৬ পিস)',231,520.9,24.0,44.4,5.8,27.5,'meat'),
    ph(98161,'Baked Southern Fiery Chicken Wings (4pc)','বেকড সাউদার্ন ফায়ারি উইংস (৪ পিস)',153,345.0,15.9,29.4,3.9,18.2,'meat'),
]

# ---- Dips IDs 98162-98165 ----
new_foods += [
    ph(98162,'Momo Dip Pizza Hut','মোমো ডিপ',15,17.6,2.5,0.4,0.0,0.6,'snack'),
    ph(98163,'Veg Mayonnaise Dip Pizza Hut','ভেজ মেয়োনেজ ডিপ',15,55.4,1.9,0.1,0.0,5.3,'snack'),
    ph(98164,'Jalapeno Pepper Dip Pizza Hut','জালাপেনো পেপার ডিপ',20,49.1,1.8,0.2,0.0,4.6,'snack'),
    ph(98165,'Tomato Ketchup Pizza Hut','টমেটো কেচাপ পিৎজা হাট',8,11.2,2.7,0.1,0.0,0.0,'snack'),
]

# ---- Garlic Breads IDs 98166-98177 ----
new_foods += [
    ph(98166,'Classic Bread Stix Pizza Hut','ক্লাসিক ব্রেড স্টিক্স',180,517.0,111.2,15.6,4.4,2.2,'bread'),
    ph(98167,'Loaded Bread Stix Pizza Hut','লোডেড ব্রেড স্টিক্স',210,673.0,113.2,16.4,4.4,18.3,'bread'),
    ph(98168,'Garlic Bread Cheese Pizza Hut','গার্লিক ব্রেড চিজ',136,493.6,54.8,10.4,4.1,31.7,'bread'),
    ph(98169,'Garlic Bread Spicy Supreme','গার্লিক ব্রেড স্পাইসি সুপ্রিম',156,540.3,58.4,10.5,5.4,29.4,'bread'),
    ph(98170,'Exotica Veggie Garlic Bread','এক্সোটিকা ভেজি গার্লিক ব্রেড',174,781.6,72.0,13.4,6.2,48.9,'bread'),
    ph(98171,'Kadhai Garlic Bread','কড়াই গার্লিক ব্রেড',198,740.7,77.6,14.5,6.9,41.4,'bread'),
    ph(98172,'Southern Fiery Garlic Bread','সাউদার্ন ফায়ারি গার্লিক ব্রেড',190,732.6,78.1,13.6,6.7,40.7,'bread'),
    ph(98173,'Indi Garlic Bread Combo','ইন্ডি গার্লিক ব্রেড কম্বো',194,736.7,77.9,14.0,6.8,41.0,'bread'),
    ph(98174,'Masala Keema Garlic Bread','মাসালা কিমা গার্লিক ব্রেড',184,813.6,70.6,17.8,2.7,51.1,'bread'),
    ph(98175,'Kadhai Keema Garlic Bread','কড়াই কিমা গার্লিক ব্রেড',230,1007.9,93.8,22.5,3.3,60.3,'bread'),
    ph(98176,'Southern Fiery Keema Garlic Bread','সাউদার্ন ফায়ারি কিমা গার্লিক ব্রেড',222,969.1,90.1,21.8,3.1,57.9,'bread'),
    ph(98177,'Indi Keema Garlic Bread Combo','ইন্ডি কিমা গার্লিক ব্রেড কম্বো',226,988.5,92.0,22.2,3.2,59.1,'bread'),
]

# ---- Pastas IDs 98178-98187 ----
new_foods += [
    ph(98178,'Classic Mushroom Pasta Pizza Hut','ক্লাসিক মাশরুম পাস্তা',262,604.6,70.3,11.0,6.5,31.0,'noodle'),
    ph(98179,'Tomato Twist Red Sauce Pasta','টমেটো টুইস্ট রেড সস পাস্তা',296,519.0,42.6,35.4,12.1,23.0,'noodle'),
    ph(98180,'Cosy Comfort White Sauce Pasta','কোজি কমফোর্ট হোয়াইট সস পাস্তা',322,664.0,57.4,37.6,6.6,31.6,'noodle'),
    ph(98181,'Cosy Comfort White Sauce Chicken Pasta','কোজি কমফোর্ট হোয়াইট সস চিকেন পাস্তা',330,878.0,59.2,40.7,8.0,53.2,'noodle'),
    ph(98182,'Spicy Red Schezwan Pasta','স্পাইসি রেড শেজওয়ান পাস্তা',304,579.2,78.0,11.5,15.0,24.6,'noodle'),
    ph(98183,'Spicy Red Schezwan Chicken Pasta','স্পাইসি রেড শেজওয়ান চিকেন পাস্তা',324,577.5,81.8,14.8,17.3,21.3,'noodle'),
    ph(98184,'Tandoori Paneer Pasta Pizza Hut','তান্দুরি পনির পাস্তা',318,737.6,83.0,14.8,16.1,38.5,'noodle'),
    ph(98185,'Tandoori Murg Pasta Pizza Hut','তান্দুরি মুর্গ পাস্তা',322,687.8,79.1,14.8,19.7,34.7,'noodle'),
    ph(98186,'Penne McN Cheese Pasta','পেন ম্যাক এন চিজ পাস্তা',320,727.6,74.1,14.7,16.3,41.4,'noodle'),
    ph(98187,'Penne McN Cheese Chicken Pasta','পেন ম্যাক এন চিজ চিকেন পাস্তা',344,770.0,112.5,17.0,18.5,42.5,'noodle'),
]

# ---- Sides IDs 98188-98194 ----
new_foods += [
    ph(98188,'Jalapeno Poppers Pizza Hut (4pc)','জালাপেনো পপার্স',90,225.3,27.1,6.1,0.0,10.3,'snack'),
    ph(98189,'Sprinkled Fries Pizza Hut','স্প্রিংকেলড ফ্রাইস',110,224.2,40.4,4.3,5.0,5.0,'snack'),
    ph(98190,'Cheezy Sprinkled Fries Pizza Hut','চিজি স্প্রিংকেলড ফ্রাইস',110,233.9,40.0,4.4,4.3,6.3,'snack'),
    ph(98191,'Baked Cheesy Momo Veg Pizza Hut','বেকড চিজি মোমো (ভেজ)',161,317.2,39.5,10.9,5.0,12.8,'snack'),
    ph(98192,'Cheesy Pocket Pizza Hut (2pc)','চিজি পকেট (২ পিস)',276,805.0,112.0,24.4,8.1,30.6,'snack'),
    ph(98193,'Indi Cheesy Pocket Pizza Hut (2pc)','ইন্ডি চিজি পকেট (২ পিস)',296,815.7,106.1,26.8,8.9,33.6,'snack'),
    ph(98194,'Baked Cheesy Momo Non Veg Pizza Hut','বেকড চিজি মোমো (নন-ভেজ)',161,404.1,91.9,15.5,3.5,14.9,'snack'),
]

# ---- Desserts IDs 98195-98198 ----
new_foods += [
    ph(98195,'Choco Volcano Pizza Hut','চকো ভলকানো',82,261.7,45.7,5.7,2.6,12.8,'sweet'),
    ph(98196,'Choco Vanilla Romance Pizza Hut','চকো ভ্যানিলা রোমান্স',55,90.5,17.9,1.4,0.4,1.6,'sweet'),
    ph(98197,'Ebony Ivory Brownie Pizza Hut','এবনি আইভরি ব্রাউনি',118,380.6,51.3,5.1,1.5,17.2,'sweet'),
    ph(98198,'Brow-wow-nie Pizza Hut','ব্রাউনি পিৎজা হাট',55,272.7,38.1,3.3,1.3,11.9,'sweet'),
]

# ---- Beverages IDs 98199-98223 ----
new_foods += [
    ph(98199,'Lemon Mint Mojito Pizza Hut','লেমন মিন্ট মোজিটো',220,132.8,33.2,0.0,0.0,0.0,'beverage'),
    ph(98200,'Fresh Lime Soda Salty Pizza Hut','ফ্রেশ লাইম সোডা (নোনতা)',215,43.0,0.0,0.0,0.0,0.0,'beverage'),
    ph(98201,'Fresh Lime Soda Sweet Pizza Hut','ফ্রেশ লাইম সোডা (মিষ্টি)',215,43.0,10.8,0.0,0.0,0.0,'beverage'),
    ph(98202,'Fresh Lime Soda Sweet Salty Pizza Hut','ফ্রেশ লাইম সোডা (মিষ্টি-নোনতা)',216,43.0,10.8,0.0,0.0,0.0,'beverage'),
    ph(98203,'Masala Pop Pizza Hut','মাসালা পপ',280,217.6,53.3,0.0,0.0,0.0,'beverage'),
    ph(98204,'Masala Lemonade Pizza Hut','মাসালা লেমোনেড',250,134.0,32.2,0.2,0.1,0.4,'beverage'),
    ph(98205,'Masala Pepsi Pizza Hut','মাসালা পেপসি',250,126.5,30.9,0.2,0.1,0.4,'beverage'),
    ph(98206,'Masala Mirinda Pizza Hut','মাসালা মিরিন্ডা',250,156.5,38.2,0.2,0.1,0.4,'beverage'),
    ph(98207,'Pepsi Pizza Hut','পেপসি পিৎজা হাট',250,107.5,27.3,0.0,0.0,0.0,'beverage'),
    ph(98208,'7UP Pizza Hut','সেভেন আপ পিৎজা হাট',250,115.0,28.5,0.0,0.0,0.0,'beverage'),
    ph(98209,'Mirinda Pizza Hut','মিরিন্ডা পিৎজা হাট',250,137.5,34.5,0.0,0.0,0.0,'beverage'),
    ph(98210,'Pepsi Black Pizza Hut','পেপসি ব্ল্যাক পিৎজা হাট',250,0.0,0.0,0.0,0.0,0.0,'beverage'),
    ph(98211,'7UP Zero Sugar Pizza Hut','সেভেন আপ জিরো সুগার',250,3.0,0.0,0.0,0.0,0.0,'beverage'),
    ph(98212,'Masala Lemonade 7UP Zero Sugar','মাসালা লেমোনেড জিরো সুগার',250,22.0,3.7,0.2,0.2,0.4,'beverage'),
    ph(98213,'Sunfeast Mango Smoothie 300ml','সানফিস্ট ম্যাঙ্গো স্মুদি ৩০০মল',300,249.0,52.2,3.0,0.0,3.0,'beverage'),
    ph(98214,'Sunfeast Mango Smoothie with Vanilla Scoop','সানফিস্ট ম্যাঙ্গো স্মুদি ভ্যানিলা',355,361.0,65.6,4.9,0.0,8.6,'beverage'),
    ph(98215,'Sunfeast Dark Fantasy Chocolate Shake 300ml','সানফিস্ট চকোলেট শেক ৩০০মল',300,327.0,52.5,9.0,0.0,9.0,'beverage'),
    ph(98216,'Sunfeast Dark Fantasy Chocolate Shake with Vanilla','সানফিস্ট চকোলেট শেক ভ্যানিলা',355,439.0,65.5,10.9,0.0,14.6,'beverage'),
    ph(98217,'Cappuccino Pizza Hut','কাপুচিনো পিৎজা হাট',185,84.0,13.0,5.0,0.0,1.0,'beverage'),
    ph(98218,'Desi Style Latte Pizza Hut','দেশি স্টাইল ল্যাটে',189,100.0,16.0,6.0,0.0,2.0,'beverage'),
    ph(98219,'Hot Chocolate Pizza Hut','হট চকোলেট পিৎজা হাট',202,134.0,25.0,4.0,0.0,1.0,'beverage'),
    ph(98220,'Masala Chai Pizza Hut','মাসালা চা পিৎজা হাট',194,85.0,16.0,2.0,0.0,1.0,'beverage'),
    ph(98221,'Cold Coffee Pizza Hut','কোল্ড কফি পিৎজা হাট',235,136.0,24.0,5.0,0.0,2.0,'beverage'),
    ph(98222,'Cold Chocolate Pizza Hut','কোল্ড চকোলেট পিৎজা হাট',245,140.0,27.0,4.0,0.0,1.0,'beverage'),
    ph(98223,'Frappe Mocha Pizza Hut','ফ্র্যাপে মোকা পিৎজা হাট',243,163.0,29.0,6.0,0.0,3.0,'beverage'),
]

# ---- Golden Hand Stretched (6 slices) IDs 98224-98231 ----
ghs = [
    ('Desi Paneer Golden Hand Stretched 100% Mozzarella','দেশি পনির গোল্ডেন হ্যান্ড স্ট্রেচড',304,787.8,88.8,39.9,11.2,32.5),
    ('Veggie Lover Golden Hand Stretched 100% Mozzarella','ভেজি লাভার গোল্ডেন হ্যান্ড স্ট্রেচড',304,727.8,101.7,27.8,11.3,25.8),
    ('Desi Paneer Golden Hand Stretched WCD','দেশি পনির গোল্ডেন হ্যান্ড স্ট্রেচড ডব্লিউসিডি',308,856.5,84.7,33.6,11.1,44.7),
    ('Veggie Lover Golden Hand Stretched WCD','ভেজি লাভার গোল্ডেন হ্যান্ড স্ট্রেচড ডব্লিউসিডি',305,710.6,90.3,25.0,11.6,30.2),
    ('Spicy Tikka Golden Hand Stretched WCD','স্পাইসি টিক্কা গোল্ডেন হ্যান্ড স্ট্রেচড',304,786.4,94.2,37.7,12.5,31.3),
    ('Double Chicken Feast Golden Hand Stretched 100% Mozzarella','ডাবল চিকেন ফিস্ট গোল্ডেন হ্যান্ড স্ট্রেচড',307,805.0,90.3,41.2,9.9,33.2),
    # carb corrected: PDF shows 38.3g (same as protein=38.3g — OCR error); kcal balance gives ~82.0g
    ('Spicy Tikka Golden Hand Stretched 100% Mozzarella','স্পাইসি টিক্কা গোল্ডেন হ্যান্ড স্ট্রেচড মোজারেলা',304,727.8,82.0,38.3,11.9,27.4),
    ('Double Chicken Feast Golden Hand Stretched WCD','ডাবল চিকেন ফিস্ট গোল্ডেন হ্যান্ড স্ট্রেচড ডব্লিউসিডি',309,833.4,89.9,36.5,10.5,38.6),
]
for i,(en,bn,w,k,c,p,fi,f) in enumerate(ghs):
    new_foods.append(ps(98224+i,en,bn,w,6,k,c,p,fi,f))

# Conflict check
existing_ids = {d['id'] for d in data}
conflicts = [nf for nf in new_foods if nf['id'] in existing_ids]
if conflicts:
    print(f'CONFLICTS: {[c["id"] for c in conflicts]}')
    sys.exit(1)

print(f'Adding {len(new_foods)} Pizza Hut items')
data.extend(new_foods)
print(f'New total: {len(data)} items')

with open(path, 'w', encoding='utf-8') as fp:
    json.dump(data, fp, ensure_ascii=False, separators=(',', ':'))
print('Done.')
