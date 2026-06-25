"""Add 20 Gujarati foods to food_master_v8_0.json (IDs 100001-100020)."""
import json, pathlib, sys

ROOT  = pathlib.Path(__file__).parent.parent
DATA  = ROOT / "assets/data/food_master_v8_0.json"

# Gujarati foods — categories fixed:
#   curry  → soup   (Gujarati Kadhi is a yogurt-based curry/soup)
#   main   → legume (Dal Dhokli is a lentil dal with wheat dumplings)
ITEMS = [
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

def main():
    with open(DATA, encoding="utf-8") as f:
        data = json.load(f)

    existing_ids = {item["id"] for item in data if isinstance(item.get("id"), int)}
    conflicts = [x["id"] for x in ITEMS if x["id"] in existing_ids]
    if conflicts:
        print(f"ERROR: ID conflicts found: {conflicts}")
        sys.exit(1)

    data.extend(ITEMS)
    with open(DATA, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))

    print(f"Added {len(ITEMS)} Gujarati foods (IDs 100001-100020)")
    print(f"New total: {len(data)} items")

if __name__ == "__main__":
    main()
