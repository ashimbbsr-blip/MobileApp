"""
fix_v6_1.py — Three targeted fixes on food_master_v6_1.json

Fix 1: Mineral gaps — fill ca/fe/zn from ICMR 2017 + BD FCT 2013 for raw/simple foods
Fix 2: Column-shift clarification — 15/17 BD FCT candidates are NOT shifts (fiber explains
       the energy gap). 2 soups have genuine data corruption; flagged, not patched.
Fix 3: Category recategorisation — 30 compound dishes moved out of "fruit" to correct
       categories (sweet, beverage, snack, vegetable, breakfast)

Output: food_master_v6_2.json + audit reports
"""

import json
from pathlib import Path

BASE = Path(__file__).parent.parent / "assets" / "data"

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def save(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {path}")

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 1 — MINERAL VALUES FROM ICMR 2017 + BD FCT 2013
# Keys: id → (ca, fe, zn, source_note)
# ═══════════════════════════════════════════════════════════════════════════════

MINERAL_FILLS = {
    # -- FRUITS (ICMR 2017, per 100g edible) ----------------------------------─
    238:  (10,    1.00, 0.04, "ICMR-2017"),   # Apple
    245:  (17,    0.90, 0.20, "ICMR-2017"),   # Banana
    262:  (18,    0.30, 0.20, "ICMR-2017"),   # Guava
    266:  (37,    0.50, 0.13, "ICMR-2017"),   # Jackfruit
    267:  (14,    0.30, 0.09, "ICMR-2017"),   # Mango
    295:  (11,    0.50, 0.10, "ICMR-2017"),   # Watermelon
    1253: (15,    1.20, 0.20, "ICMR-2017"),   # Jambolan
    1255: (29,    0.07, 0.06, "USDA-FNDDS"),  # Java apple
    1257: (26,    0.60, 0.06, "BD-FCT-2013"), # Lemon Kagoji

    # -- EGGS (BD FCT 2013 / ICMR 2017) --------------------------------------─
    640:  (56,    2.70, 1.30, "BD-FCT-2013"), # Boiled egg
    1350: (56,    1.80, 1.30, "BD-FCT-2013"), # Egg chicken farmed raw
    1351: (56,    2.70, 1.30, "BD-FCT-2013"), # Egg chicken native raw
    1353: (64,    2.70, 1.40, "BD-FCT-2013"), # Egg duck whole raw
    1355: (56,    2.70, 1.30, "BD-FCT-2013"), # Egg chicken native boiled
    1356: (64,    2.70, 1.40, "BD-FCT-2013"), # Egg duck whole boiled

    # -- BD FCT VEGETABLES — leafy greens --------------------------------------
    1111: (150,   3.00, 0.50, "BD-FCT-2013"), # Amaranth stem
    1112: (40,    1.00, 0.50, "BD-FCT-2013"), # Bean scarlet runner
    1114: (16,    0.80, 0.35, "BD-FCT-2013"), # Beet root red
    1121: (37,    0.70, 0.80, "BD-FCT-2013"), # Cowpea pods and seeds raw
    1147: (37,    0.70, 0.80, "BD-FCT-2013"), # Cowpea boiled
    1156: (1130,  3.90, 1.20, "ICMR-2017"),   # Agathi raw (sesbania)
    1157: (170,   4.20, 0.50, "BD-FCT-2013"), # Alligator weed
    1172: (26,    1.50, 0.30, "BD-FCT-2013"), # Fern leaves
    1179: (99,    2.70, 0.53, "ICMR-2017"),   # Spinach raw
    1181: (107,   2.10, 0.50, "BD-FCT-2013"), # Sweet potato leaves SP4
    1183: (80,    1.80, 0.40, "BD-FCT-2013"), # Sweet potato leaves SP8
    1180: (96,    2.00, 0.50, "BD-FCT-2013"), # Sweet potato leaves raw
    1184: (77,    1.70, 0.40, "ICMR-2017"),   # Water spinach
    1185: (120,   0.40, 0.40, "ICMR-2017"),   # Watercress
    1165: (100,   5.80, 0.70, "ICMR-2017"),   # Bottle gourd leaves
    1175: (303,  11.60, 0.40, "ICMR-2017"),   # Jute leaves
    1160: (200,   3.00, 0.60, "ICMR-2017"),   # Amaranth leaves green

    # -- BD FCT VEGETABLES — tubers / roots ----------------------------------─
    1195: (30,    0.80, 0.40, "BD-FCT-2013"), # Sweet potato white raw
    1196: (17,    0.50, 0.30, "BD-FCT-2013"), # Yam tuber raw
    1198: (10,    0.70, 0.30, "BD-FCT-2013"), # Potato Diamond boiled
    1202: (17,    0.50, 0.30, "BD-FCT-2013"), # Yam tuber boiled

    # -- BD FCT VEGETABLES — herbs --------------------------------------------─
    1229: (171,   6.30, 0.70, "BD-FCT-2013"), # Indian pennywort

    # -- GRAINS ----------------------------------------------------------------
    1085: (17,    1.30, 0.80, "ICMR-2017"),   # Semolina wheat raw
    1096: (14,    2.30, 1.10, "ICMR-2017"),   # Ruti (wheat roti)

    # -- FISH (BD FCT 2013 / ICMR 2017) --------------------------------------─
    1321: (30,    0.70, 1.00, "BD-FCT-2013"), # Rohu river raw
    1323: (323,   2.25, 1.90, "ICMR-2017"),   # Speckled shrimp raw
    1326: (30,    0.70, 0.50, "BD-FCT-2013"), # Spotted snakehead raw

    # -- SWEETENERS / CONDIMENTS (ICMR 2017) ----------------------------------
    1390: (230,   7.00, 0.50, "ICMR-2017"),   # Betel leaves raw
    1391: (5,     0.40, 0.22, "ICMR-2017"),   # Honey
    1392: (80,    2.60, 0.14, "ICMR-2017"),   # Jaggery sugarcane solid
    1393: (108,   6.80, 0.30, "ICMR-2017"),   # Jaggery date palm solid
    1394: (108,   6.80, 0.30, "ICMR-2017"),   # Jaggery liquid date palm
    1395: (1,     0.05, 0.01, "ICMR-2017"),   # Sugar white
}

# ═══════════════════════════════════════════════════════════════════════════════
# FIX 3 — CATEGORY RECATEGORISATION (fruit → correct)
# ═══════════════════════════════════════════════════════════════════════════════

CAT_FIXES = {
    # sweet — pies, soufflés, burfi, payasam, malpua, cheesecake, pastry
    239: "sweet",   # Apple banana pie
    240: "sweet",   # Apple cinnamon pie
    243: "sweet",   # Apple sago payasam
    244: "sweet",   # Apple snowballs
    250: "sweet",   # Coconut burfi
    252: "sweet",   # Coconut finger
    254: "sweet",   # Cold orange souffle
    255: "sweet",   # Cold pineapple souffle
    265: "sweet",   # Hot orange souffle
    268: "sweet",   # Mango cheesecake
    269: "sweet",   # Mango malpua
    276: "sweet",   # Orange chiffon pie
    281: "sweet",   # Orange souffle
    285: "sweet",   # Pineapple pastry
    287: "sweet",   # Pineapple souffle

    # beverage — milkshakes
    247: "beverage",  # Banana milkshake
    270: "beverage",  # Mango milkshake
    279: "beverage",  # Orange milkshake
    284: "beverage",  # Pineapple milkshake

    # snack — chutneys, pickles, coconut condiments, pastes
    246: "snack",   # Banana groundnut paste/puree
    249: "snack",   # Beans with coconut
    251: "snack",   # Coconut chutney
    253: "snack",   # Coconut pickle
    257: "snack",   # Dates chutney
    272: "snack",   # Mango pickle

    # vegetable — savory fruit-based curries / preparations
    290: "vegetable",  # Raw banana kofta curry
    292: "vegetable",  # Raw papaya with coconut
    293: "vegetable",  # Raw turnip with coconut
    294: "vegetable",  # Vegetable curry with coconut

    # breakfast — egg-based preparations
    280: "breakfast",  # Orange omelette/omlet
}

# ═══════════════════════════════════════════════════════════════════════════════
# COLUMN-SHIFT ANALYSIS RESULT
# ═══════════════════════════════════════════════════════════════════════════════

# 15 BD FCT candidates where est + 2*fi matches k within 5% — these are VALID.
# The BD FCT uses "available carbohydrates" (net carbs); kcal is calculated
# including fiber at 2 kcal/g. No nutrition change needed.
BDFCT_VALID_IDS = {
    1115, 1121, 1125, 1138, 1141, 1147, 1152,
    1160, 1165, 1175, 1180, 1181, 1183, 1222, 1229,
}

# 2 soups with genuine data corruption (implausible p values even post-swap)
SOUP_DATA_ERRORS = {
    996:  "Curried Cauliflower soup — p=23.4g implausible; est=443 vs k=130; needs ICMR source row",
    1052: "Spinach soup — p=53.0g impossible; est=918 vs k=164; needs ICMR source row",
}

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    records = load(BASE / "food_master_v6_1.json")
    id_map  = {r["id"]: i for i, r in enumerate(records)}
    total   = len(records)
    print(f"Loaded {total} records from food_master_v6_1.json")

    mineral_filled     = []
    category_changes   = []

    # -- FIX 1: minerals ------------------------------------------------------─
    print("\n-- Fix 1: Mineral fills --")
    for rid, (ca, fe, zn, src) in MINERAL_FILLS.items():
        idx = id_map.get(rid)
        if idx is None:
            print(f"  WARN: ID {rid} not found")
            continue
        r = records[idx]
        old_ca = r.get("ca", 0) or 0
        old_fe = r.get("fe", 0) or 0
        old_zn = r.get("zn", 0) or 0
        # Detect implausible existing values from PDF extraction errors
        # fe > 30 mg for a vegetable is physically impossible
        implausible = (old_fe > 30) or (old_ca > 0 and old_ca < 5 and ca > 50)

        if old_ca == 0 and old_fe == 0 and old_zn == 0:
            r["ca"] = ca
            r["fe"] = fe
            r["zn"] = zn
            mineral_filled.append({
                "id": rid, "en": r["en"],
                "ca": ca, "fe": fe, "zn": zn, "source": src,
                "note": "filled (was zero)",
            })
        elif implausible:
            print(f"  OVERRIDE [{rid}] {r['en']} -- had implausible ca={old_ca} fe={old_fe} zn={old_zn}")
            r["ca"] = ca
            r["fe"] = fe
            r["zn"] = zn
            mineral_filled.append({
                "id": rid, "en": r["en"],
                "ca": ca, "fe": fe, "zn": zn, "source": src,
                "note": f"overrode implausible ca={old_ca} fe={old_fe} zn={old_zn}",
            })
        else:
            print(f"  SKIP [{rid}] {r['en']} -- already has minerals ca={old_ca} fe={old_fe} zn={old_zn}")

    print(f"  Minerals filled: {len(mineral_filled)}")

    # -- FIX 2: column-shift report (no nutrition changes) ----------------------
    print("\n-- Fix 2: Column-shift analysis --")
    column_shift_final = {
        "methodology_note": (
            "BD FCT 2013 uses 'available carbohydrates' (net carbs) in the c field. "
            "Energy is calculated as 4*p + 4*c + 9*f + 2*fi, not 4*p + 4*c + 9*f. "
            "Adding fiber at 2 kcal/g resolves the apparent 30–45%% energy gap for 15 records."
        ),
        "bdfct_valid_no_change_needed": sorted(BDFCT_VALID_IDS),
        "data_errors_need_source": [
            {"id": rid, "note": note}
            for rid, note in SOUP_DATA_ERRORS.items()
        ],
    }
    print(f"  BD FCT valid (no change): {len(BDFCT_VALID_IDS)}")
    print(f"  Data errors (no change, needs source): {len(SOUP_DATA_ERRORS)}")

    # -- FIX 3: category recategorisation --------------------------------------
    print("\n-- Fix 3: Category recategorisation --")
    for rid, new_cat in CAT_FIXES.items():
        idx = id_map.get(rid)
        if idx is None:
            print(f"  WARN: ID {rid} not found")
            continue
        r = records[idx]
        old_cat = r.get("cat", "")
        if old_cat == new_cat:
            continue
        r["cat"] = new_cat
        category_changes.append({
            "id": rid, "en": r["en"],
            "from": old_cat, "to": new_cat,
        })

    print(f"  Category changes: {len(category_changes)}")
    for ch in category_changes:
        print(f"    [{ch['id']}] {ch['en']}: {ch['from']} -> {ch['to']}")

    # -- SAVE OUTPUTS ----------------------------------------------------------
    print("\n-- Saving files --")
    save(BASE / "food_master_v6_2.json", records)
    save(BASE / "mineral_fills_report.json",      mineral_filled)
    save(BASE / "category_changes_report.json",   category_changes)
    save(BASE / "column_shift_final_report.json", column_shift_final)

    # -- SUMMARY --------------------------------------------------------------─
    print("\n" + "="*60)
    print("FINAL SUMMARY — v6.2 fixes")
    print("="*60)
    print(f"  Total records:              {total}")
    print(f"  Minerals filled:            {len(mineral_filled)}")
    print(f"  Category recategorisations: {len(category_changes)}")
    print(f"  Column-shift (BD FCT ok):   {len(BDFCT_VALID_IDS)}")
    print(f"  Column-shift (data errors): {len(SOUP_DATA_ERRORS)} (unfixable without source)")
    print("="*60)

    # verify category distribution
    cat_dist = {}
    for r in records:
        c = r.get("cat", "")
        cat_dist[c] = cat_dist.get(c, 0) + 1
    print("\nCategory distribution after fix:")
    for cat, cnt in sorted(cat_dist.items(), key=lambda x: -x[1]):
        print(f"  {cnt:4d}  {cat}")

if __name__ == "__main__":
    main()
