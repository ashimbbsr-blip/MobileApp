"""
BD_FCT Nutrition Audit & Repair Pipeline
Input:  food_master_v5_6.json
Output: food_master_v5_7.json + 7 reports

Systematic errors detected in BD_FCT import:
  Pattern A — kJ stored as kcal (confirmed for 7+ items)
  Pattern B — kJ stored as kcal + fat/carbs columns swapped (9 grain items)
  Pattern C — kJ suspected but macros inconsistent (manual review)
  Pattern D — energy mismatch without clear root cause (manual review)
"""

import json, re, sys, os
from collections import defaultdict
from copy import deepcopy

sys.stdout.reconfigure(encoding="utf-8")

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA    = os.path.join(ROOT, "assets", "data")
REPORTS = os.path.join(ROOT, "tools", "reports")
os.makedirs(REPORTS, exist_ok=True)

MASTER_IN  = os.path.join(DATA, "food_master_v5_6.json")
MASTER_OUT = os.path.join(DATA, "food_master_v5_7.json")
KJ_FACTOR  = 4.184

def rp(name):
    return os.path.join(REPORTS, name)

# ── Load ──────────────────────────────────────────────────────────────────────
with open(MASTER_IN, encoding="utf-8") as fh:
    ALL_FOODS = json.load(fh)

bd_fct_raw = [x for x in ALL_FOODS if x.get("src") == "bd_fct"]
print(f"Loaded {len(ALL_FOODS)} total items")
print(f"BD_FCT records: {len(bd_fct_raw)}")


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def macro_vals(item):
    return (
        float(item.get("p",  0)),
        float(item.get("c",  0)),
        float(item.get("f",  0)),
        float(item.get("fi", 0)),
        float(item.get("k",  0)),
    )

def est(p, c, f):
    return round(4 * p + 4 * c + 9 * f, 2)

def diff_pct(stored, estimated):
    if estimated <= 0:
        return None
    return abs(stored - estimated) / estimated

def serving_grams(s):
    m = re.search(r"(\d+(?:\.\d+)?)\s*g", str(s), re.I)
    return float(m.group(1)) if m else None

# Category kcal benchmark ranges (per 100g)
CAT_RANGES = {
    "rice":       (50,  450),
    "grain":      (200, 450),
    "bread":      (150, 450),
    "vegetable":  (10,  150),
    "salad":      (10,  150),
    "fruit":      (15,  400),
    "fish":       (50,  350),
    "meat":       (100, 500),
    "egg":        (130, 220),
    "dairy":      (15,  950),   # skim milk to ghee
    "legume":     (50,  400),
    "snack":      (50,  650),
    "sweet":      (100, 700),
    "soup":       (10,  200),
    "beverage":   (0,   150),
    "breakfast":  (50,  450),
    "dessert":    (100, 700),
}

# Fat categories where high fat is legitimate (don't flag f>60)
HIGH_FAT_CATS = {"dairy"}      # dairy covers ghee/butter/oil
HIGH_FAT_FOODS = {             # individual food IDs known to be high-fat legitimate
    1206, 1208, 1209, 1210, 1216,   # nuts/seeds/coconut — confirmed ~480-675 kcal and high fat
    1368, 1369, 1370, 1371, 1372,   # oils, butter, ghee
    1373, 1374, 1375, 1376, 1377, 1378, 1379,
}

# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — BD_FCT INVENTORY
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 1: BD_FCT INVENTORY ═══")

inventory = []
for x in bd_fct_raw:
    p, c, f, fi, k = macro_vals(x)
    ek = est(p, c, f)
    dp = diff_pct(k, ek)
    inventory.append({
        "id":  x["id"],
        "en":  x.get("en"),
        "bn":  x.get("bn"),
        "cat": x.get("cat"),
        "s":   x.get("s"),
        "k":   k, "p": p, "c": c, "f": f, "fi": fi,
        "ca":  float(x.get("ca", 0)),
        "fe":  float(x.get("fe", 0)),
        "zn":  float(x.get("zn", 0)),
        "mg":  float(x.get("mg", 0)) if "mg" in x else 0,
        "pot": float(x.get("pot", 0)) if "pot" in x else 0,
        "est_kcal": ek,
        "diff_pct": round(dp * 100, 1) if dp is not None else None,
    })

with open(rp("bd_fct_inventory.json"), "w", encoding="utf-8") as fh:
    json.dump(inventory, fh, ensure_ascii=False, indent=2)

print(f"  Inventory written: {len(inventory)} records")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — HARD NUTRITION LIMITS (100g serving)
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 2: HARD LIMIT VIOLATIONS ═══")

hard_violations = []

for x in bd_fct_raw:
    p, c, f, fi, k = macro_vals(x)
    iid = x["id"]
    cat = x.get("cat", "")
    issues = []

    # k > 900: flag unless it's an oil/fat item where that's expected
    if k > 900 and iid not in HIGH_FAT_FOODS and cat != "dairy":
        issues.append(f"k={k}>900kcal (not a fat food)")

    # Protein >60g per 100g: only possible in protein isolates
    if p > 60:
        issues.append(f"protein={p}>60g/100g")

    # Fat >60g per 100g: impossible for non-fat foods
    if f > 60 and iid not in HIGH_FAT_FOODS and cat not in HIGH_FAT_CATS:
        issues.append(f"fat={f}>60g/100g (implausible for {cat})")

    # Carbs >100g per 100g: physically impossible
    if c > 100:
        issues.append(f"carbs={c}>100g/100g (impossible)")

    # Fiber > carbs: fiber is a component of carbs
    if fi > c and fi > 0.5:
        issues.append(f"fiber={fi}>carbs={c}")

    if issues:
        hard_violations.append({
            "id": iid, "en": x.get("en"), "cat": cat, "s": x.get("s"),
            "k": k, "p": p, "c": c, "f": f, "fi": fi,
            "violations": issues,
        })

with open(rp("bd_fct_hard_limit_violations.json"), "w", encoding="utf-8") as fh:
    json.dump(hard_violations, fh, ensure_ascii=False, indent=2)

print(f"  Hard-limit violations: {len(hard_violations)}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — ENERGY VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 3: ENERGY VALIDATION ═══")

energy_mismatches = []

for x in bd_fct_raw:
    p, c, f, fi, k = macro_vals(x)
    ek = est(p, c, f)
    if ek <= 0:
        continue
    dp = diff_pct(k, ek)
    if dp is not None and dp > 0.30:
        energy_mismatches.append({
            "id": x["id"], "en": x.get("en"), "cat": x.get("cat"),
            "k": k, "p": p, "c": c, "f": f, "fi": fi,
            "est_kcal": ek, "diff_pct": round(dp * 100, 1),
            "k_div_est": round(k / ek, 3) if ek > 0 else None,
        })

energy_mismatches.sort(key=lambda x: -x["diff_pct"])

with open(rp("bd_fct_energy_mismatch.json"), "w", encoding="utf-8") as fh:
    json.dump(energy_mismatches, fh, ensure_ascii=False, indent=2)

print(f"  Energy mismatches (>30%): {len(energy_mismatches)}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — SYSTEMATIC ERROR DETECTION
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 4: SYSTEMATIC ERROR DETECTION ═══")

#
# Pattern A — kJ stored as kcal (simple: macros OK, only k is wrong)
#   k/4.184 matches est_from_macros within 15%
#
# Pattern B — kJ + fat/carbs column swap
#   Fat and carbs were swapped during import; k is also in kJ.
#   Signal: f > 45 AND c < 15 AND after swap+kJ, energy matches within 12%
#   Only for non-fat-food categories (grains, starchy foods, fruits)
#
# Pattern C — kJ suspected but poor macro match
#   k > threshold suggesting kJ, but after conversion still >20% off
#
# Pattern D — energy mismatch without clear kJ signature
#

# Categories where f>45 is biologically implausible (not oils/nuts)
LOW_FAT_CATS = {"grain","rice","bread","vegetable","fruit","legume","beverage",
                "soup","breakfast"}

patterns = {
    "A_kj_only":   [],
    "B_kj_swap":   [],
    "C_kj_unclear":[],
    "D_other":     [],
}

for x in bd_fct_raw:
    p, c, f, fi, k = macro_vals(x)
    iid = x["id"]
    cat = x.get("cat", "")
    en  = x.get("en", "")

    ek_norm = est(p, c, f)
    ek_swap = est(p, f, c)   # fat and carbs swapped

    kj_kcal      = round(k / KJ_FACTOR, 2)
    diff_norm     = diff_pct(k,      ek_norm)  # stored k vs est with macros as-is
    diff_kj_norm  = diff_pct(kj_kcal, ek_norm)  # kJ-converted k vs est as-is
    diff_kj_swap  = diff_pct(kj_kcal, ek_swap)  # kJ-converted k vs est after swap

    if ek_norm is None or ek_norm <= 5:
        continue

    record = {
        "id": iid, "en": en, "cat": cat,
        "k": k, "p": p, "c": c, "f": f,
        "est_kcal_current": round(ek_norm, 1),
        "est_kcal_swapped": round(ek_swap, 1),
        "kj_to_kcal": kj_kcal,
        "diff_current_pct":  round(diff_norm * 100,    1) if diff_norm    is not None else None,
        "diff_kj_norm_pct":  round(diff_kj_norm * 100, 1) if diff_kj_norm is not None else None,
        "diff_kj_swap_pct":  round(diff_kj_swap * 100, 1) if diff_kj_swap is not None else None,
    }

    # ── Pattern A: simple kJ (macros correct, only k wrong) ──────────────────
    if (diff_norm is not None and diff_norm > 0.30
            and diff_kj_norm is not None and diff_kj_norm < 0.15
            and iid not in HIGH_FAT_FOODS):
        patterns["A_kj_only"].append({**record, "pattern": "A_kj_only",
            "confidence": 97 if diff_kj_norm < 0.10 else 93})
        continue

    # ── Pattern B: kJ + fat/carbs column swap ────────────────────────────────
    # Signal: f >> c for a starchy/non-fat food, AND kJ+swap gives good match
    if (f > 45 and c < 15
            and cat in LOW_FAT_CATS
            and iid not in HIGH_FAT_FOODS
            and diff_kj_swap is not None and diff_kj_swap < 0.12
            and diff_norm > 0.30):
        patterns["B_kj_swap"].append({**record, "pattern": "B_kj_swap",
            "confidence": 96 if diff_kj_swap < 0.08 else 92})
        continue

    # ── Pattern C: kJ suspected but poor macro match (manual review) ─────────
    # kJ conversion would lower k, but doesn't resolve the energy inconsistency
    if (k > 250
            and diff_norm is not None and diff_norm > 0.30
            and diff_kj_norm is not None and diff_kj_norm < 0.35
            and iid not in HIGH_FAT_FOODS):
        patterns["C_kj_unclear"].append({**record, "pattern": "C_kj_unclear",
            "confidence": 60,
            "note": "kJ suspected but energy match is weak after conversion"})
        continue

    # ── Pattern D: other energy mismatch ─────────────────────────────────────
    if diff_norm is not None and diff_norm > 0.30:
        patterns["D_other"].append({**record, "pattern": "D_other",
            "confidence": 0,
            "note": "No clear systematic pattern identified"})

systematic_patterns = {
    "summary": {
        "A_kj_only":    len(patterns["A_kj_only"]),
        "B_kj_swap":    len(patterns["B_kj_swap"]),
        "C_kj_unclear": len(patterns["C_kj_unclear"]),
        "D_other":      len(patterns["D_other"]),
    },
    "A_kj_only":    patterns["A_kj_only"],
    "B_kj_swap":    patterns["B_kj_swap"],
    "C_kj_unclear": patterns["C_kj_unclear"],
    "D_other":      patterns["D_other"],
}

with open(rp("bd_fct_systematic_patterns.json"), "w", encoding="utf-8") as fh:
    json.dump(systematic_patterns, fh, ensure_ascii=False, indent=2)

print(f"  Pattern A (kJ only):          {len(patterns['A_kj_only'])}")
print(f"  Pattern B (kJ + swap):        {len(patterns['B_kj_swap'])}")
print(f"  Pattern C (kJ unclear):       {len(patterns['C_kj_unclear'])}")
print(f"  Pattern D (other mismatch):   {len(patterns['D_other'])}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — AUTO-REPAIR (confidence >= 95%)
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 5: AUTO-REPAIR ═══")

repair_report   = []
manual_review   = []
repaired_ids    = set()

# ── Repair Pattern A: k = round(k / 4.184) ───────────────────────────────────
for rec in patterns["A_kj_only"]:
    if rec["confidence"] < 95:
        manual_review.append({**rec, "reason_not_repaired": "confidence<95"})
        continue

    iid   = rec["id"]
    old_k = rec["k"]
    new_k = round(old_k / KJ_FACTOR, 1)

    repair_report.append({
        "id":           iid,
        "food":         rec["en"],
        "pattern":      "A — kJ stored as kcal",
        "confidence":   rec["confidence"],
        "old_values":   {"k": old_k},
        "new_values":   {"k": new_k},
        "repair_reason": (
            f"k={old_k} is in kJ not kcal. "
            f"k÷4.184={new_k} matches est_kcal={rec['est_kcal_current']} "
            f"within {rec['diff_kj_norm_pct']}%"
        ),
    })
    repaired_ids.add(iid)

# ── Repair Pattern B: swap c↔f then k = round(k / 4.184) ────────────────────
for rec in patterns["B_kj_swap"]:
    if rec["confidence"] < 95:
        manual_review.append({**rec, "reason_not_repaired": "confidence<95"})
        continue

    iid   = rec["id"]
    old_k = rec["k"]
    old_c = rec["c"]
    old_f = rec["f"]
    new_k = round(old_k / KJ_FACTOR, 1)
    new_c = old_f   # swap
    new_f = old_c   # swap

    repair_report.append({
        "id":           iid,
        "food":         rec["en"],
        "pattern":      "B — kJ as kcal + fat/carbs column swap",
        "confidence":   rec["confidence"],
        "old_values":   {"k": old_k, "c": old_c, "f": old_f},
        "new_values":   {"k": new_k, "c": new_c, "f": new_f},
        "repair_reason": (
            f"fat={old_f}g and carbs={old_c}g are biologically implausible for "
            f"a {rec['cat']} food (fat should be <10g, carbs ~60-85g). "
            f"After swap+kJ conversion: est={rec['est_kcal_swapped']} vs "
            f"k÷4.184={rec['kj_to_kcal']} (diff {rec['diff_kj_swap_pct']}%)"
        ),
    })
    repaired_ids.add(iid)

# ── Pattern C + D: all go to manual review ───────────────────────────────────
for rec in patterns["C_kj_unclear"] + patterns["D_other"]:
    manual_review.append({
        **rec,
        "reason_not_repaired": "confidence<95 — root cause unclear",
    })

# ── Hard-limit violations not covered by patterns ────────────────────────────
pattern_ids = {r["id"] for recs in patterns.values() for r in recs
               if isinstance(recs, list)}
for v in hard_violations:
    if v["id"] not in pattern_ids and v["id"] not in repaired_ids:
        manual_review.append({
            **v,
            "pattern": "hard_limit_violation",
            "confidence": 0,
            "reason_not_repaired": "Hard limit violated but no repair pattern matched",
        })

# Deduplicate manual review by ID
seen_manual = set()
manual_review_deduped = []
for r in manual_review:
    if r["id"] not in seen_manual:
        manual_review_deduped.append(r)
        seen_manual.add(r["id"])

with open(rp("bd_fct_repair_report.json"), "w", encoding="utf-8") as fh:
    json.dump(repair_report, fh, ensure_ascii=False, indent=2)

with open(rp("bd_fct_manual_review.json"), "w", encoding="utf-8") as fh:
    json.dump(manual_review_deduped, fh, ensure_ascii=False, indent=2)

print(f"  Auto-repairs queued:      {len(repair_report)}")
print(f"    Pattern A (kJ only):    {sum(1 for r in repair_report if 'A —' in r['pattern'])}")
print(f"    Pattern B (kJ+swap):    {sum(1 for r in repair_report if 'B —' in r['pattern'])}")
print(f"  Manual review:            {len(manual_review_deduped)}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 6 — CATEGORY BENCHMARKING
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 6: CATEGORY BENCHMARKING ═══")

cat_anomalies = []

# Build a map: repaired k for items already flagged for repair
repair_map = {}
for r in repair_report:
    if "k" in r["new_values"]:
        repair_map[r["id"]] = r["new_values"]["k"]

for x in bd_fct_raw:
    iid = x["id"]
    cat = x.get("cat", "")
    k   = repair_map.get(iid, float(x.get("k", 0)))   # use repaired k if available

    lo, hi = CAT_RANGES.get(cat, (0, 10000))
    if k < lo or k > hi:
        if iid in HIGH_FAT_FOODS:
            continue   # legitimate high-fat food
        cat_anomalies.append({
            "id": iid, "en": x.get("en"), "cat": cat,
            "k": float(x.get("k", 0)),
            "k_after_repair": k,
            "expected_range": f"{lo}–{hi}",
            "deviation": (
                f"below_floor by {lo - k:.0f}" if k < lo
                else f"above_ceiling by {k - hi:.0f}"
            ),
            "will_be_repaired": iid in repaired_ids,
        })

with open(rp("bd_fct_category_anomalies.json"), "w", encoding="utf-8") as fh:
    json.dump(cat_anomalies, fh, ensure_ascii=False, indent=2)

print(f"  Category anomalies: {len(cat_anomalies)}")
print(f"    Will be fixed by repair: {sum(1 for a in cat_anomalies if a['will_be_repaired'])}")
print(f"    Remaining after repair:  {sum(1 for a in cat_anomalies if not a['will_be_repaired'])}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 8 — APPLY REPAIRS → food_master_v5_7.json
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 8: APPLY REPAIRS ═══")

# Build repair lookup: id → {field: new_value}
apply_map = {}
for r in repair_report:
    apply_map[r["id"]] = r["new_values"]

# Work on a deep copy of ALL foods (BD_FCT + everything else)
patched = deepcopy(ALL_FOODS)
patches_applied = 0

for item in patched:
    if item["id"] not in apply_map:
        continue
    changes = apply_map[item["id"]]
    for field, new_val in changes.items():
        item[field] = new_val
    patches_applied += 1

# Verify no non-BD_FCT records were touched
non_bd_changed = sum(
    1 for item in patched
    if item.get("src") != "bd_fct" and item["id"] in apply_map
)
assert non_bd_changed == 0, "BUG: non-BD_FCT record was modified"

with open(MASTER_OUT, "w", encoding="utf-8") as fh:
    json.dump(patched, fh, ensure_ascii=False, separators=(",", ":"))

print(f"  Patches applied: {patches_applied}")
print(f"  Written: {MASTER_OUT}")


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═" * 62)
print("  BD_FCT AUDIT — FINAL SUMMARY")
print("═" * 62)
print(f"  Total BD_FCT records:           {len(bd_fct_raw)}")
print(f"  Hard-limit violations:          {len(hard_violations)}")
print(f"  Energy mismatches (>30%):       {len(energy_mismatches)}")
print()
print(f"  kJ conversion errors found:     {len(patterns['A_kj_only']) + len(patterns['B_kj_swap'])}")
print(f"    Pure kJ (Pattern A):          {len(patterns['A_kj_only'])}")
print(f"    kJ + column swap (Pattern B): {len(patterns['B_kj_swap'])}")
print(f"  kJ suspected/unclear (Pat. C):  {len(patterns['C_kj_unclear'])}")
print(f"  Other mismatches (Pattern D):   {len(patterns['D_other'])}")
print()
print(f"  Records auto-repaired:          {len(repair_report)}")
print(f"  Records needing manual review:  {len(manual_review_deduped)}")
print()
print(f"  Category anomalies found:       {len(cat_anomalies)}")
print(f"    Fixed by auto-repair:         {sum(1 for a in cat_anomalies if a['will_be_repaired'])}")
print(f"    Still needing attention:       {sum(1 for a in cat_anomalies if not a['will_be_repaired'])}")
print()

# Top 20 highest-risk foods (unrepaired, worst energy mismatch)
unrepaired_mismatches = [
    m for m in energy_mismatches
    if m["id"] not in repaired_ids
]
print("  Top 20 highest-risk unrepaired foods:")
print(f"  {'ID':>6} {'kcal':>7} {'est':>7} {'diff%':>7}  {'food'}")
print(f"  {'-'*60}")
for m in unrepaired_mismatches[:20]:
    print(
        f"  {m['id']:>6} {m['k']:>7.1f} {m['est_kcal']:>7.1f} "
        f"{m['diff_pct']:>6.1f}%  {m['en'][:38]}"
    )
print("═" * 62)

# Verify auto-repair results
print("\nVerification — spot-check repaired records:")
for r in repair_report[:12]:
    iid = r["id"]
    item = next((x for x in patched if x["id"] == iid), None)
    if item:
        p, c, f, fi, k = macro_vals(item)
        ek = est(p, c, f)
        dp = diff_pct(k, ek)
        print(
            f"  id={iid:5d} k={k:6.1f} est={ek:6.1f} diff={dp*100:5.1f}%  "
            f"[{item.get('en','')[:35]}]"
        )
