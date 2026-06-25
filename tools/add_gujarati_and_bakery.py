"""
Add Gujarati (IDs 100001-100020) and Bakery (IDs 100021+) foods to
food_master_v7_2.json — the pipeline source file.
Skips any item whose English name already exists (case-insensitive).
"""
import json, pathlib, sys

ROOT  = pathlib.Path(__file__).parent.parent
DATA  = ROOT / "assets/data/food_master_v7_2.json"

# ── Gujarati foods ─────────────────────────────────────────────────────────────
GUJARATI = [
  {"id":100001,"en":"Dhokla","bn":"ঢোকলা","cat":"snack","s":"100g","k":165,"p":7.5,"c":28.0,"f":3.0,"fi":2.5,"ca":32,"fe":1.5,"kw":["dhokla","gujarati","steamed","fermented","chickpea"],"src":"local"},
  {"id":100002,"en":"Khaman","bn":"খামান","cat":"snack","s":"100g","k":180,"p":8.0,"c":30.0,"f":3.5,"fi":2.8,"ca":38,"fe":1.7,"kw":["khaman","gujarati","steamed","chickpea","besan"],"src":"local"},
  {"id":100003,"en":"Handvo","bn":"হান্ডভো","cat":"snack","s":"100g","k":205,"p":8.5,"c":26.0,"f":7.5,"fi":4.0,"ca":42,"fe":1.8,"kw":["handvo","gujarati","baked","lentil","rice","savory cake"],"src":"local"},
  {"id":100004,"en":"Thepla","bn":"থেপলা","cat":"bread","s":"100g","k":265,"p":8.0,"c":42.0,"f":8.0,"fi":5.5,"ca":58,"fe":2.4,"kw":["thepla","gujarati","flatbread","roti","spiced"],"src":"local"},
  {"id":100005,"en":"Methi Thepla","bn":"মেথি থেপলা","cat":"bread","s":"100g","k":250,"p":8.5,"c":39.0,"f":7.0,"fi":6.0,"ca":72,"fe":2.8,"kw":["methi thepla","fenugreek flatbread","gujarati","thepla","methi roti"],"src":"local"},
  {"id":100006,"en":"Gujarati Kadhi","bn":"গুজরাটি কড়ি","cat":"soup","s":"100g","k":78,"p":3.0,"c":8.5,"f":3.5,"fi":0.5,"ca":105,"fe":0.4,"kw":["kadhi","gujarati kadhi","yogurt curry","sweet kadhi","buttermilk soup"],"src":"local"},
  {"id":100007,"en":"Sev Tameta","bn":"সেভ টমেটো","cat":"vegetable","s":"100g","k":145,"p":3.5,"c":12.0,"f":9.0,"fi":2.5,"ca":32,"fe":1.0,"kw":["sev tameta","sev tomato","gujarati","sev tamatar"],"src":"local"},
  {"id":100008,"en":"Undhiyu","bn":"উন্ধিয়ু","cat":"vegetable","s":"100g","k":155,"p":4.8,"c":18.0,"f":7.0,"fi":5.5,"ca":68,"fe":1.8,"kw":["undhiyu","undho","gujarati","mixed vegetable","fenugreek dumpling"],"src":"local"},
  {"id":100009,"en":"Ringan No Olo","bn":"রিঙ্গন নো ওলো","cat":"vegetable","s":"100g","k":88,"p":2.5,"c":10.0,"f":4.0,"fi":3.0,"ca":28,"fe":0.9,"kw":["ringan no olo","brinjal bharta","eggplant gujarati","baingan"],"src":"local"},
  {"id":100010,"en":"Bhindi Sambhariya","bn":"ভিন্ডি সাম্ভারিয়া","cat":"vegetable","s":"100g","k":135,"p":4.0,"c":11.0,"f":8.0,"fi":4.5,"ca":78,"fe":1.5,"kw":["bhindi sambhariya","stuffed okra","bhindi","gujarati","masala bhindi"],"src":"local"},
  {"id":100011,"en":"Dal Dhokli","bn":"ডাল ঢোকলি","cat":"legume","s":"100g","k":145,"p":5.5,"c":21.0,"f":4.0,"fi":3.0,"ca":34,"fe":1.5,"kw":["dal dhokli","dhokli","gujarati dal","lentil dumplings","toor dal"],"src":"local"},
  {"id":100012,"en":"Khichu","bn":"খিচু","cat":"snack","s":"100g","k":120,"p":2.5,"c":26.0,"f":0.8,"fi":1.2,"ca":12,"fe":0.6,"kw":["khichu","rice khichu","gujarati","rice flour snack","papdi no lot"],"src":"local"},
  {"id":100013,"en":"Fafda","bn":"ফাফড়া","cat":"snack","s":"100g","k":455,"p":13.0,"c":40.0,"f":27.0,"fi":4.0,"ca":45,"fe":2.5,"kw":["fafda","gujarati fafda","chickpea strips","besan snack","fafra"],"src":"local"},
  {"id":100014,"en":"Gathiya","bn":"গাঠিয়া","cat":"snack","s":"100g","k":510,"p":12.0,"c":45.0,"f":32.0,"fi":4.0,"ca":40,"fe":2.2,"kw":["gathiya","ganthiya","besan snack","gujarati","chickpea flour"],"src":"local"},
  {"id":100015,"en":"Kachori Gujarati Style","bn":"গুজরাটি কচুরি","cat":"snack","s":"100g","k":365,"p":8.0,"c":38.0,"f":20.0,"fi":3.5,"ca":28,"fe":1.8,"kw":["kachori","gujarati kachori","moong dal kachori","deep fried"],"src":"local"},
  {"id":100016,"en":"Basundi","bn":"বাসুন্দি","cat":"sweet","s":"100g","k":210,"p":6.0,"c":24.0,"f":10.0,"fi":0.0,"ca":220,"fe":0.2,"kw":["basundi","milk dessert","rabdi","gujarati sweet","condensed milk dessert"],"src":"local"},
  {"id":100017,"en":"Shrikhand","bn":"শ্রিখণ্ড","cat":"sweet","s":"100g","k":250,"p":7.0,"c":30.0,"f":11.0,"fi":0.0,"ca":180,"fe":0.2,"kw":["shrikhand","strained yogurt dessert","srikhand","amrakhand","hung curd sweet"],"src":"local"},
  {"id":100018,"en":"Sukhdi","bn":"সুখডি","cat":"sweet","s":"100g","k":445,"p":5.5,"c":55.0,"f":22.0,"fi":2.0,"ca":32,"fe":1.8,"kw":["sukhdi","gol papdi","wheat jaggery sweet","gujarati sweet","sheera"],"src":"local"},
  {"id":100019,"en":"Mohanthal","bn":"মোহনথাল","cat":"sweet","s":"100g","k":470,"p":8.0,"c":52.0,"f":26.0,"fi":2.0,"ca":48,"fe":1.5,"kw":["mohanthal","besan barfi","gujarati mithai","chickpea flour fudge"],"src":"local"},
  {"id":100020,"en":"Ghughra","bn":"ঘুঘরা","cat":"sweet","s":"100g","k":395,"p":6.0,"c":52.0,"f":18.0,"fi":2.0,"ca":28,"fe":1.2,"kw":["ghughra","gujiya","sweet dumpling","gujarati ghughra","karanji"],"src":"local"},
]

# ── Bakery foods (3 duplicates pre-screened: Black Forest Pastry,
#    Veg Sandwich, Chicken Sandwich) ──────────────────────────────────────────
BAKERY = [
  {"id":100021,"en":"Butter Croissant","bn":"বাটার ক্রোয়াসাঁ","cat":"bakery","s":"100g","k":406,"p":8.2,"c":45.8,"f":21.0,"fi":2.6,"ca":37,"fe":2.7,"kw":["croissant","butter croissant","pastry","french","bakery"],"src":"local"},
  {"id":100022,"en":"Chocolate Croissant","bn":"চকোলেট ক্রোয়াসাঁ","cat":"bakery","s":"100g","k":424,"p":8.0,"c":48.0,"f":22.0,"fi":3.1,"ca":42,"fe":3.0,"kw":["chocolate croissant","pain au chocolat","bakery","pastry"],"src":"local"},
  {"id":100023,"en":"Plain Muffin","bn":"প্লেইন মাফিন","cat":"bakery","s":"100g","k":377,"p":6.4,"c":53.0,"f":15.0,"fi":1.8,"ca":98,"fe":2.0,"kw":["muffin","plain muffin","bakery","baked"],"src":"local"},
  {"id":100024,"en":"Blueberry Muffin","bn":"ব্লুবেরি মাফিন","cat":"bakery","s":"100g","k":382,"p":5.9,"c":57.0,"f":15.0,"fi":2.0,"ca":90,"fe":1.8,"kw":["blueberry muffin","muffin","bakery","blueberry"],"src":"local"},
  {"id":100025,"en":"Chocolate Muffin","bn":"চকোলেট মাফিন","cat":"bakery","s":"100g","k":410,"p":6.0,"c":55.0,"f":18.0,"fi":3.2,"ca":95,"fe":2.5,"kw":["chocolate muffin","muffin","bakery","chocolate"],"src":"local"},
  {"id":100026,"en":"Chocolate Brownie","bn":"চকোলেট ব্রাউনি","cat":"bakery","s":"100g","k":466,"p":5.1,"c":61.0,"f":23.0,"fi":2.8,"ca":51,"fe":2.1,"kw":["brownie","chocolate brownie","fudge brownie","bakery"],"src":"local"},
  {"id":100027,"en":"Tea Cake","bn":"টি কেক","cat":"bakery","s":"100g","k":360,"p":6.0,"c":58.0,"f":11.0,"fi":1.5,"ca":78,"fe":1.7,"kw":["tea cake","cake","bakery","sponge cake"],"src":"local"},
  {"id":100028,"en":"Fruit Cake","bn":"ফ্রুট কেক","cat":"bakery","s":"100g","k":345,"p":4.5,"c":62.0,"f":9.0,"fi":2.2,"ca":60,"fe":1.5,"kw":["fruit cake","bakery","dried fruit","christmas cake"],"src":"local"},
  {"id":100029,"en":"Red Velvet Cake","bn":"রেড ভেলভেট কেক","cat":"bakery","s":"100g","k":365,"p":4.5,"c":50.0,"f":17.0,"fi":1.2,"ca":80,"fe":1.4,"kw":["red velvet cake","red velvet","cake","cream cheese frosting"],"src":"local"},
  {"id":100030,"en":"Cheesecake","bn":"চিজকেক","cat":"bakery","s":"100g","k":321,"p":6.0,"c":25.0,"f":22.0,"fi":0.5,"ca":95,"fe":0.8,"kw":["cheesecake","cheese cake","baked cheesecake","new york cheesecake"],"src":"local"},
  {"id":100031,"en":"Glazed Donut","bn":"গ্লেজড ডোনাট","cat":"bakery","s":"100g","k":412,"p":4.7,"c":51.0,"f":21.0,"fi":1.7,"ca":26,"fe":1.8,"kw":["donut","doughnut","glazed donut","bakery"],"src":"local"},
  {"id":100032,"en":"Vegetable Puff","bn":"ভেজিটেবল পাফ","cat":"bakery","s":"100g","k":338,"p":6.2,"c":34.0,"f":19.0,"fi":2.5,"ca":32,"fe":1.9,"kw":["vegetable puff","veg puff","puff pastry","bakery snack"],"src":"local"},
  {"id":100033,"en":"Paneer Puff","bn":"পনির পাফ","cat":"bakery","s":"100g","k":350,"p":8.5,"c":32.0,"f":20.0,"fi":2.0,"ca":110,"fe":1.8,"kw":["paneer puff","cottage cheese puff","puff pastry","bakery"],"src":"local"},
  {"id":100034,"en":"Chicken Puff","bn":"চিকেন পাফ","cat":"bakery","s":"100g","k":355,"p":10.5,"c":31.0,"f":20.0,"fi":1.8,"ca":28,"fe":1.5,"kw":["chicken puff","puff pastry","bakery snack","chicken pastry"],"src":"local"},
  {"id":100035,"en":"Chicken Patties","bn":"চিকেন প্যাটিস","cat":"bakery","s":"100g","k":345,"p":11.0,"c":29.0,"f":19.0,"fi":1.5,"ca":25,"fe":1.6,"kw":["chicken patties","chicken pattice","bakery","puff"],"src":"local"},
  {"id":100036,"en":"Grilled Veg Sandwich","bn":"গ্রিলড ভেজ স্যান্ডউইচ","cat":"bakery","s":"100g","k":275,"p":8.0,"c":30.0,"f":12.0,"fi":3.0,"ca":58,"fe":1.7,"kw":["grilled veg sandwich","grilled sandwich","toasted sandwich","bakery"],"src":"local"},
  {"id":100037,"en":"Garlic Bread","bn":"গার্লিক ব্রেড","cat":"bakery","s":"100g","k":350,"p":8.5,"c":47.0,"f":13.0,"fi":2.5,"ca":40,"fe":2.0,"kw":["garlic bread","garlic toast","bakery","bread"],"src":"local"},
]

def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    existing_ids   = {item["id"] for item in data if isinstance(item.get("id"), int)}
    existing_names = {item["en"].lower() for item in data if "en" in item}

    added = skipped = 0
    for item in GUJARATI + BAKERY:
        if item["id"] in existing_ids:
            print(f"  SKIP (dup ID {item['id']}): {item['en']}")
            skipped += 1
            continue
        if item["en"].lower() in existing_names:
            print(f"  SKIP (dup name): {item['en']}")
            skipped += 1
            continue
        data.append(item)
        existing_ids.add(item["id"])
        existing_names.add(item["en"].lower())
        added += 1

    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\nAdded {added} items, skipped {skipped} duplicates")
    print(f"New total in v7_2: {len(data)}")

if __name__ == "__main__":
    main()
