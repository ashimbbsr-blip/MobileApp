"""
add_compendium_8.py
Add 8 foods missing from the dataset, sourced from:
  - "Local Food Compendium 2017" (Odisha) — Energy, Ca, Fe, Vit-C
  - ICMR / IFCT 2017 — Carbohydrates, Fiber, and supplemental minerals
All values are per 100 g edible portion.
"""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

DATASET = Path(__file__).parent.parent / "assets" / "data" / "food_master_v8_2.json"

NEW_FOODS = [
    # -------------------------------------------------------------------------
    # 1. Finger Millet / Ragi (whole grain, raw)
    # Ca=344mg notable — highest of any cereal
    # Carbs derived: (328 - 7.3×4 - 1.3×9) / 4 ≈ 71.8g (ICMR confirms ~72g)
    # -------------------------------------------------------------------------
    {
        "en": "Finger Millet (Ragi, Raw)",
        "bn": "রাগি (কাঁচা)",
        "cat": "grain",
        "k": 328, "p": 7.3, "c": 72.0, "f": 1.3, "fi": 3.6,
        "ca": 344, "fe": 3.9,
        "mg": 146,
        "s": "100g",
        "src": "icmr_ifct",
        "quality_score": 80,
        "kw": ["ragi", "finger millet", "nachni", "marua", "millet", "grain",
               "cereal", "high calcium", "gluten free", "whole grain"]
    },
    # -------------------------------------------------------------------------
    # 2. Field Bean / Hyacinth Bean (whole, raw)
    # Dolichos lablab — "Dongarani" in Odia, "Val dal" in Gujarati
    # Carbs derived: (347 - 24.9×4 - 0.8×9) / 4 ≈ 60.1g
    # -------------------------------------------------------------------------
    {
        "en": "Field Bean (Dry, Raw)",
        "bn": "ফিল্ড বিন (শুকনো)",
        "cat": "legume",
        "k": 347, "p": 24.9, "c": 60.0, "f": 0.8, "fi": 5.0,
        "ca": 60, "fe": 2.7,
        "s": "100g",
        "src": "icmr_ifct",
        "quality_score": 75,
        "kw": ["field bean", "hyacinth bean", "val dal", "dolichos", "lablab",
               "legume", "pulse", "dry bean", "protein"]
    },
    # -------------------------------------------------------------------------
    # 3. Ridge Gourd (raw)
    # "Jhinge" in Bengali, "Turai" in Hindi, "Luffa acutangula"
    # Carbs derived: (17 - 0.5×4 - 0.1×9) / 4 ≈ 3.5g
    # -------------------------------------------------------------------------
    {
        "en": "Ridge Gourd (Raw)",
        "bn": "ঝিঙে (কাঁচা)",
        "cat": "vegetable",
        "k": 17, "p": 0.5, "c": 3.5, "f": 0.1, "fi": 0.5,
        "ca": 18, "fe": 0.4,
        "s": "100g",
        "src": "icmr_ifct",
        "quality_score": 78,
        "kw": ["ridge gourd", "jhinge", "turai", "toori", "ribbed gourd",
               "luffa", "vegetable", "low calorie", "summer vegetable"]
    },
    # -------------------------------------------------------------------------
    # 4. Yellow Pumpkin / Sweet Pumpkin (raw)
    # "Mishti Kumra" in Bengali, "Kaddu" in Hindi, "Cucurbita maxima"
    # Carbs derived: (25 - 1.4×4 - 0.1×9) / 4 ≈ 4.6g
    # -------------------------------------------------------------------------
    {
        "en": "Yellow Pumpkin (Raw)",
        "bn": "মিষ্টি কুমড়া (কাঁচা)",
        "cat": "vegetable",
        "k": 25, "p": 1.4, "c": 4.6, "f": 0.1, "fi": 0.5,
        "ca": 10, "fe": 0.4,
        "s": "100g",
        "src": "icmr_ifct",
        "quality_score": 78,
        "kw": ["pumpkin", "yellow pumpkin", "sweet pumpkin", "kaddu", "kumra",
               "mishti kumra", "vegetable", "low calorie", "beta carotene"]
    },
    # -------------------------------------------------------------------------
    # 5. Ivy Gourd / Kovai (raw)
    # "Telakucha" in Bengali, "Kundri" in Odia/Hindi, "Coccinia grandis"
    # Carbs derived: (18 - 1.2×4 - 0.1×9) / 4 ≈ 3.1g
    # -------------------------------------------------------------------------
    {
        "en": "Ivy Gourd (Raw)",
        "bn": "টেলাকুচা (কাঁচা)",
        "cat": "vegetable",
        "k": 18, "p": 1.2, "c": 3.1, "f": 0.1, "fi": 1.6,
        "ca": 40, "fe": 0.4,
        "s": "100g",
        "src": "icmr_ifct",
        "quality_score": 78,
        "kw": ["ivy gourd", "kovai", "kundri", "tindora", "tindola", "telakucha",
               "coccinia", "vegetable", "low calorie", "diabetic friendly"]
    },
    # -------------------------------------------------------------------------
    # 6. Pumpkin Leaves (raw)
    # "Kumra Shak" in Bengali — notable for Ca=392mg and high iron
    # Iron (7.0mg) and Vit-C (17mg) from ICMR supplement (compendium had gaps)
    # Carbs derived: (57 - 4.6×4 - 0.8×9) / 4 ≈ 7.9g
    # -------------------------------------------------------------------------
    {
        "en": "Pumpkin Leaves (Raw)",
        "bn": "কুমড়া শাক (কাঁচা)",
        "cat": "shaak",
        "k": 57, "p": 4.6, "c": 7.9, "f": 0.8, "fi": 2.0,
        "ca": 392, "fe": 7.0,
        "s": "100g",
        "src": "icmr_ifct",
        "quality_score": 78,
        "kw": ["pumpkin leaf", "pumpkin leaves", "pumpkin greens", "kumra shak",
               "leafy green", "shaak", "high calcium", "high iron", "bengali greens"]
    },
    # -------------------------------------------------------------------------
    # 7. Wild Yam (raw)
    # "Bon Aloo" in Bengali, "Langalkanda" in Odia — locally foraged tuber
    # Carbs derived: (110 - 2.5×4 - 0.3×9) / 4 ≈ 24.3g
    # -------------------------------------------------------------------------
    {
        "en": "Wild Yam (Raw)",
        "bn": "বন আলু (কাঁচা)",
        "cat": "vegetable",
        "k": 110, "p": 2.5, "c": 24.3, "f": 0.3, "fi": 1.0,
        "ca": 20, "fe": 1.0,
        "s": "100g",
        "src": "icmr_ifct",
        "quality_score": 72,
        "kw": ["wild yam", "yam", "bon aloo", "langalkanda", "jungle yam",
               "tuber", "root vegetable", "foraged", "odia", "tribal food"]
    },
    # -------------------------------------------------------------------------
    # 8. Jamun / Java Plum (raw)
    # "Kalo Jam" in Bengali, "Syzygium cumini" — known for high iron in fruit
    # Using IFCT 2017 macros (more accurate); Ca/Fe cross-checked with compendium
    # Energy: 60 kcal | Carbs: 13.5g | Protein: 0.9g | Fat: 0.3g
    # -------------------------------------------------------------------------
    {
        "en": "Jamun (Java Plum, Raw)",
        "bn": "কালো জাম (কাঁচা)",
        "cat": "fruit",
        "k": 60, "p": 0.9, "c": 13.5, "f": 0.3, "fi": 0.6,
        "ca": 28, "fe": 2.2,
        "s": "100g",
        "src": "icmr_ifct",
        "quality_score": 80,
        "kw": ["jamun", "java plum", "black plum", "indian blackberry", "kalo jam",
               "jambul", "fruit", "antioxidant", "summer fruit", "diabetic friendly"]
    },
]


def main():
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    before = len(data)
    max_id = max(item["id"] for item in data)
    next_id = max_id + 1
    existing_en = {item["en"].strip().lower() for item in data}

    added = skipped = 0
    for item in NEW_FOODS:
        key = item["en"].strip().lower()
        if key in existing_en:
            print(f"  SKIP (duplicate): {item['en']}")
            skipped += 1
            continue
        item = dict(item)
        item["id"] = next_id
        next_id += 1
        data.append(item)
        existing_en.add(key)
        print(f"  ADD id={item['id']}: {item['en']}")
        added += 1

    print(f"\nBefore: {before}  Added: {added}  Skipped: {skipped}  After: {len(data)}")
    DATASET.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved → {DATASET}")


if __name__ == "__main__":
    main()
