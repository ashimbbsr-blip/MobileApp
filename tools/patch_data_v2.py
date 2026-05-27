"""
Data quality patch v2 — fixes four categories of bad data in food_master_v5_3.json
Run from project root: py tools/patch_data_v2.py
"""
import json
import shutil
import os
from datetime import datetime

DATASET = "assets/data/food_master_v5_3.json"

# ── Reference values (USDA FoodData Central, per 100 g) ──────────────────────

NUT_FIXES = {
    1204: {"k": 584, "p": 20.8, "c": 20.0, "f": 51.5},  # Sunflower seeds
    1205: {"k": 553, "p": 18.2, "c": 30.2, "f": 43.9},  # Cashew nuts
    1206: {"k": 673, "p": 13.7, "c": 13.1, "f": 68.4},  # Chilgoza pine (pine nuts)
    1207: {"k": 197, "p":  2.3, "c":  2.8, "f": 21.3},  # Coconut milk
    1208: {"k": 650, "p":  6.9, "c": 25.0, "f": 65.0},  # Coconut, desiccated
    1209: {"k": 354, "p":  3.3, "c": 15.2, "f": 33.5},  # Coconut, mature kernel
    1210: {"k": 567, "p": 25.8, "c": 16.1, "f": 49.2},  # Groundnuts/Peanut raw
    1211: {"k": 534, "p": 18.3, "c": 28.9, "f": 42.2},  # Linseed/Flaxseed
    1212: {"k": 332, "p": 15.4, "c": 63.4, "f":  2.0},  # Lotus seeds, dried
    1213: {"k":  89, "p":  4.3, "c": 17.3, "f":  0.6},  # Lotus seeds, green
    1214: {"k": 508, "p": 26.1, "c": 28.1, "f": 36.2},  # Mustard seeds, dried
    1215: {"k": 562, "p": 20.2, "c": 27.2, "f": 45.3},  # Pistachio nuts, dried
    1216: {"k": 559, "p": 30.2, "c": 10.7, "f": 49.1},  # Pumpkin seeds, dried
    1217: {"k": 573, "p": 17.7, "c": 23.5, "f": 49.7},  # Sesame seeds, whole
    1234: {"k": 525, "p": 18.0, "c": 28.1, "f": 41.6},  # Poppy seeds
}

SOUP_FIXES = {
    # Items where macro-derived kcal ≫ stated kcal — cross-row contamination
    851: {"k":  45, "p": 1.5, "f": 1.2, "c":  7.5},   # Clear tomato soup
    853: {"k":  60, "p": 2.0, "f": 1.5, "c":  9.0},   # Cold summer garden soup
    857: {"k": 150, "p": 4.5, "f": 6.0, "c": 20.0},   # French onion soup
    860: {"k":  95, "p": 5.5, "f": 1.5, "c": 15.0},   # Green pea soup
    864: {"k": 100, "p": 2.5, "f": 1.8, "c": 18.5},   # Millet soup
    865: {"k":  75, "p": 3.5, "f": 1.5, "c": 11.5},   # Minestrone soup
    866: {"k": 150, "p": 7.5, "f": 6.0, "c": 16.5},   # Mulligatawny soup
    867: {"k": 100, "p": 6.0, "f": 2.5, "c": 13.0},   # Talaumein soup
}

# BD FCT fish items where p and f are swapped AND k is in kJ
# Evidence: k/4.184 gives plausible kcal; treating p-field as fat and
# back-calculating protein from energy gives values matching known species data.
FISH_IDS_PF_SWAPPED = {
    1275, 1276, 1278, 1280, 1282, 1283, 1284, 1285,
    1286, 1287, 1288, 1291, 1294, 1295, 1296, 1298,
    1299, 1300, 1301, 1304, 1306, 1307, 1309, 1310,
    1311, 1312, 1320, 1323, 1326,
}

KJ_PER_KCAL = 4.184


def patch(items):
    stats = {"fish": 0, "nuts": 0, "milk": 0, "soups": 0}

    for item in items:
        iid = item.get("id")

        # ── Fish: kJ→kcal conversion + p/f field swap ─────────────────────
        if iid in FISH_IDS_PF_SWAPPED:
            kcal = round(item["k"] / KJ_PER_KCAL, 0)
            fat = item["p"]           # stored in wrong column
            protein = max(0.0, round((kcal - fat * 9) / 4, 1))
            item["k"] = int(kcal)
            item["p"] = protein
            item["f"] = round(fat, 1)
            stats["fish"] += 1

        # ── Nuts/Seeds: replace with USDA reference values ─────────────────
        elif iid in NUT_FIXES:
            ref = NUT_FIXES[iid]
            item["k"] = ref["k"]
            item["p"] = ref["p"]
            item["c"] = ref["c"]
            item["f"] = ref["f"]
            stats["nuts"] += 1

        # ── Milk powder: fix kJ→kcal, restore carbs, correct fat ──────────
        elif iid == 1362:
            item["k"] = 496      # 2080 kJ ÷ 4.184 ≈ 496 kcal
            item["p"] = 26.3     # USDA whole milk powder
            item["c"] = 38.4
            item["f"] = 26.7
            item["fi"] = 0.0
            stats["milk"] += 1

        # ── Soups: replace cross-row-contaminated macros ───────────────────
        elif iid in SOUP_FIXES:
            ref = SOUP_FIXES[iid]
            item["k"] = ref["k"]
            item["p"] = ref["p"]
            item["f"] = ref["f"]
            item["c"] = ref["c"]
            stats["soups"] += 1

    return stats


def main():
    if not os.path.exists(DATASET):
        print(f"ERROR: {DATASET} not found. Run from project root.")
        return

    # Backup
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = f"{DATASET}.bak.{ts}"
    shutil.copy2(DATASET, bak)
    print(f"Backup: {bak}")

    with open(DATASET, encoding="utf-8") as f:
        items = json.load(f)

    total_before = len(items)
    stats = patch(items)

    with open(DATASET, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=None, separators=(",", ":"))

    print(f"Done. {total_before} items total.")
    print(f"  Fish fixed (kJ+p/f swap): {stats['fish']}")
    print(f"  Nuts/Seeds (USDA ref):    {stats['nuts']}")
    print(f"  Milk powder:              {stats['milk']}")
    print(f"  Soups (row mismatch):     {stats['soups']}")


if __name__ == "__main__":
    main()
