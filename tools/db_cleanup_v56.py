"""
DB Audit & Repair v5.6
Input:  food_master_v5_5.json (current)
        food_master_v5_4.json (reference — restore regressions from here)
Output: food_master_v5_6.json
        index_en_v5_6.json
        index_bn_v5_6.json
        nutrition_regression_report.json
        bn_corrections_report.json
        micronutrient_gap_report.json
"""

import json, re, sys, os, unicodedata
from collections import defaultdict
from copy import deepcopy

sys.stdout.reconfigure(encoding="utf-8")

ROOT    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA    = os.path.join(ROOT, "assets", "data")
REPORTS = os.path.join(ROOT, "tools", "reports")
os.makedirs(REPORTS, exist_ok=True)

MASTER_V4  = os.path.join(DATA, "food_master_v5_4.json")
MASTER_V5  = os.path.join(DATA, "food_master_v5_5.json")
MASTER_OUT = os.path.join(DATA, "food_master_v5_6.json")
IDX_EN_OUT = os.path.join(DATA, "index_en_v5_6.json")
IDX_BN_OUT = os.path.join(DATA, "index_bn_v5_6.json")

def rp(name):
    return os.path.join(REPORTS, name)

# ── Load both versions ────────────────────────────────────────────────────────
with open(MASTER_V4, encoding="utf-8") as fh:
    v4_list = json.load(fh)
with open(MASTER_V5, encoding="utf-8") as fh:
    v5_list = json.load(fh)

v4 = {x["id"]: x for x in v4_list}
v5 = {x["id"]: x for x in v5_list}

items = deepcopy(v5_list)   # working copy — we patch this
id_to = {it["id"]: it for it in items}

print(f"Loaded v5_4: {len(v4)} items")
print(f"Loaded v5_5: {len(v5)} items (working copy)")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 1 — NUTRITION REGRESSION DETECTION & RESTORE
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 1: NUTRITION REGRESSION DETECTION ═══")

# A regression is when ANY macro (p, c, f) dropped by >80% in v5_5 vs v5_4
# AND the kcal stayed similar (<30% change).
# Signature: the v5_5 repair divided macros by 10 or 100 but could not
# correspondingly fix kcal, leaving the record internally inconsistent.

MACRO_DROP_THRESHOLD = 0.80    # >80% drop in a single macro
KCAL_SIMILAR_THRESHOLD = 0.30  # kcal changed by <30% → "similar" (bad repair)

regression_report = []
restored_count    = 0

for item in items:
    iid = item["id"]
    a   = v4.get(iid)   # v5_4 reference
    if not a:
        continue         # new item added in v5_5 that wasn't in v5_4 — skip

    k_v4 = float(a.get("k", 0))
    k_v5 = float(item.get("k", 0))

    # Kcal similarity check
    k_changed_pct = abs(k_v4 - k_v5) / max(k_v4, 1)
    kcal_is_similar = k_changed_pct < KCAL_SIMILAR_THRESHOLD

    regressed_fields = []
    for fld in ["p", "c", "f"]:
        va = float(a.get(fld, 0))
        vb = float(item.get(fld, 0))
        if va > 0:
            drop = (va - vb) / va
            if drop > MACRO_DROP_THRESHOLD:
                regressed_fields.append({
                    "field": fld,
                    "v5_4_value": va,
                    "v5_5_value": vb,
                    "drop_pct": round(drop * 100, 1),
                })

    if not regressed_fields or not kcal_is_similar:
        # Either no regression, or kcal also changed proportionally
        # (meaning v5_5 correctly scaled per-100g → per-serving)
        continue

    # ── Regression confirmed — restore nutrition from v5_4 ───────────────────
    # Restore: p, c, f, fi (macros + fiber)
    # Keep: k from v5_5 (it was not changed, so same either way)
    # Never invent or estimate — copy verbatim from v5_4
    restored_fields = {}
    for fld in ["p", "c", "f", "fi"]:
        old_v5 = item.get(fld)
        new_val = a.get(fld)
        if new_val is not None:
            item[fld] = new_val
            restored_fields[fld] = {"from_v5_5": old_v5, "restored_to": new_val}

    regression_report.append({
        "id": iid,
        "en": item.get("en"),
        "serving": item.get("s"),
        "k_v5_4": k_v4,
        "k_v5_5": k_v5,
        "k_change_pct": round(k_changed_pct * 100, 1),
        "regressed_fields": regressed_fields,
        "restored_fields": restored_fields,
        "note": (
            "Serving was non-gram (e.g. '1 bowl') — v5_5 repair extracted wrong "
            "serving weight and incorrectly scaled macros. Restored from v5_4."
            if not re.search(r"\d+(?:\.\d+)?\s*g", str(item.get("s", "")), re.I)
            else "Macro decimal-shift repair was incorrect. Restored from v5_4."
        ),
    })
    restored_count += 1

with open(rp("nutrition_regression_report.json"), "w", encoding="utf-8") as fh:
    json.dump(regression_report, fh, ensure_ascii=False, indent=2)

print(f"  Regressions detected:   {len(regression_report)}")
print(f"  Records restored:       {restored_count}")

# Breakdown: non-gram serving vs gram serving
non_gram = sum(
    1 for r in regression_report
    if not re.search(r"\d+(?:\.\d+)?\s*g", r.get("serving","") or "", re.I)
)
print(f"  → Non-gram serving (bowl/plate/pcs): {non_gram}")
print(f"  → Gram serving (decimal shift error): {len(regression_report) - non_gram}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 2 — BENGALI FIELD SCAN FOR OCR PATTERNS
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 2: BENGALI OCR PATTERN SCAN ═══")

# These are English words that appear in Bengali script —
# either OCR artifacts or transliteration errors.
# Pattern → (English equivalent, description)
OCR_PATTERNS = [
    ("ানদ",     "and",     "English conjunction 'and' in Bengali script"),
    ("ওিথ",     "with",    "English preposition 'with' in Bengali script"),
    ("ফলউর",    "flour",   "English word 'flour' in Bengali script"),
    ("দরোপস",   "drops",   "English word 'drops' in Bengali script"),
    ("করিসপয",  "crispy",  "English word 'crispy' in Bengali script"),
    ("কুসতারদ", "custard", "English word 'custard' in Bengali script"),
    ("সআউকে",   "sauce",   "English word 'sauce' in Bengali script"),
]

bn_corrections = []

for item in items:
    iid = item["id"]
    bn  = item.get("bn", "")
    if not bn:
        continue

    found_patterns = []
    for pattern, eng_word, description in OCR_PATTERNS:
        if pattern in bn:
            found_patterns.append({
                "pattern":     pattern,
                "english_word": eng_word,
                "description": description,
            })

    if found_patterns:
        bn_corrections.append({
            "id":       iid,
            "en":       item.get("en"),
            "bn":       bn,
            "patterns": found_patterns,
            "action":   "MANUAL_REVIEW — do not auto-correct; requires proper Bengali translation",
        })

with open(rp("bn_corrections_report.json"), "w", encoding="utf-8") as fh:
    json.dump(bn_corrections, fh, ensure_ascii=False, indent=2)

print(f"  Bengali OCR issues found: {len(bn_corrections)}")
for entry in bn_corrections[:5]:
    patterns_found = [p["english_word"] for p in entry["patterns"]]
    print(f"  id={entry['id']:5d} [{entry['en'][:30]:<30}] patterns={patterns_found}")
if len(bn_corrections) > 5:
    print(f"  ... and {len(bn_corrections)-5} more")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 3 — MICRONUTRIENT GAP REPORT
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 3: MICRONUTRIENT GAP REPORT ═══")

micro_gap = []
for item in items:
    ca = float(item.get("ca", 0))
    fe = float(item.get("fe", 0))
    zn = float(item.get("zn", 0))
    if ca == 0 and fe == 0 and zn == 0:
        micro_gap.append({
            "id":  item["id"],
            "en":  item.get("en"),
            "bn":  item.get("bn"),
            "cat": item.get("cat"),
            "src": item.get("src"),
            "note": "ca=0 AND fe=0 AND zn=0 — micronutrient data missing",
        })

with open(rp("micronutrient_gap_report.json"), "w", encoding="utf-8") as fh:
    json.dump(micro_gap, fh, ensure_ascii=False, indent=2)

print(f"  Items with ca=fe=zn=0: {len(micro_gap)}")

# Category breakdown
by_cat = defaultdict(int)
by_src = defaultdict(int)
for g in micro_gap:
    by_cat[g["cat"]] += 1
    by_src[g["src"]] += 1
print(f"  By category: {dict(sorted(by_cat.items(), key=lambda x: -x[1])[:6])}")
print(f"  By source:   {dict(sorted(by_src.items(), key=lambda x: -x[1]))}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 4 — INDEX REBUILD
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 4: INDEX REBUILD ═══")

items.sort(key=lambda x: x["id"])

def build_en_index(food_items):
    idx = defaultdict(set)
    for item in food_items:
        fid = item["id"]
        for word in re.findall(r"[a-z]+", item.get("en", "").lower()):
            if len(word) >= 2: idx[word[:2]].add(fid)
            if len(word) >= 3: idx[word[:3]].add(fid)
        for kw in item.get("kw", []):
            for word in re.findall(r"[a-z]+", str(kw).lower()):
                if len(word) >= 2: idx[word[:2]].add(fid)
                if len(word) >= 3: idx[word[:3]].add(fid)
    return {k: sorted(v) for k, v in idx.items()}

def build_bn_index(food_items):
    idx = defaultdict(set)
    for item in food_items:
        fid = item["id"]
        for word in item.get("bn", "").split():
            w = word.strip()
            if len(w) >= 1:
                prefix = w[:2]
                if any(0x0980 <= ord(ch) <= 0x09FF for ch in prefix):
                    idx[prefix].add(fid)
    return {k: sorted(v) for k, v in idx.items()}

idx_en = build_en_index(items)
idx_bn = build_bn_index(items)

all_ids    = {it["id"] for it in items}
en_indexed = {fid for ids in idx_en.values() for fid in ids}
bn_indexed = {fid for ids in idx_bn.values() for fid in ids}
orphan_en  = sorted(all_ids - en_indexed)
orphan_bn  = sorted(all_ids - bn_indexed)

print(f"  EN tokens: {len(idx_en)},  orphan IDs: {len(orphan_en)}")
print(f"  BN tokens: {len(idx_bn)},  orphan IDs: {len(orphan_bn)}")
if orphan_en:
    print(f"  EN orphans: {orphan_en}")


# ══════════════════════════════════════════════════════════════════════════════
# PHASE 5 — WRITE OUTPUTS
# ══════════════════════════════════════════════════════════════════════════════
print("\n═══ PHASE 5: WRITE OUTPUTS ═══")

with open(MASTER_OUT, "w", encoding="utf-8") as fh:
    json.dump(items, fh, ensure_ascii=False, separators=(",", ":"))
print(f"  Written: {MASTER_OUT}")

with open(IDX_EN_OUT, "w", encoding="utf-8") as fh:
    json.dump(idx_en, fh, ensure_ascii=False, separators=(",", ":"))
print(f"  Written: {IDX_EN_OUT}")

with open(IDX_BN_OUT, "w", encoding="utf-8") as fh:
    json.dump(idx_bn, fh, ensure_ascii=False, separators=(",", ":"))
print(f"  Written: {IDX_BN_OUT}")

print(f"  Reports: {REPORTS}")


# ══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "═" * 60)
print("  DATABASE v5.6 — FINAL SUMMARY")
print("═" * 60)
print(f"  Foods in v5_4 (reference):        {len(v4)}")
print(f"  Foods in v5_5 (input):            {len(v5)}")
print(f"  Foods in v5_6 (output):           {len(items)}")
print()
print(f"  Nutrition regressions detected:   {len(regression_report)}")
print(f"    → Non-gram serving (bowl/pcs):  {non_gram}")
print(f"    → Gram serving (shift error):   {len(regression_report) - non_gram}")
print(f"  Records restored from v5_4:       {restored_count}")
print()
print(f"  Bengali OCR issues flagged:       {len(bn_corrections)}")
print(f"  Items with ca=fe=zn=0:            {len(micro_gap)}")
print()
print(f"  EN index tokens:                  {len(idx_en)}")
print(f"  BN index tokens:                  {len(idx_bn)}")
print(f"  Orphan IDs (EN):                  {len(orphan_en)}")
print(f"  Orphan IDs (BN):                  {len(orphan_bn)}")
print("═" * 60)

# ── Spot-check known regression examples ─────────────────────────────────────
print("\nSpot-check (known regression examples):")
SPOT_CHECK = [169, 171, 172, 1430, 1431, 1433]
for sid in SPOT_CHECK:
    a  = v4.get(sid, {})
    b  = v5.get(sid, {})
    c_ = id_to.get(sid, {})
    print(
        f"  id={sid:5d} [{a.get('en','?')[:28]:<28}]"
        f"  p: v4={a.get('p','?')}  v5={b.get('p','?')}  v6={c_.get('p','?')}"
        f"  c: v4={a.get('c','?')}  v6={c_.get('c','?')}"
        f"  f: v4={a.get('f','?')}  v6={c_.get('f','?')}"
    )
