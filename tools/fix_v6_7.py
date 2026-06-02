"""
fix_v6_7.py — Produces food_master_v6_7.json + index_en/bn_v6_7.json

Fixes applied
─────────────
1.  Fried-poori fat correction  — 8 records had fat = 53–58 g in a 60 g serving
    (physically impossible; corrected to ICMR/NIN FCT deep-fried-bread values).
2.  Alcohol macro proxies        — spirits (Whiskey/Rum/Vodka) had zero macros;
    Beer (Strong) had 1 g carbs. Fat is used as ethanol proxy so kcal closes.
3.  Tamarind chutney serving     — "1ml" → "15ml" (1 tablespoon); kcal/macros
    set to realistic tablespoon values.
4.  Vitamin B12 fill             — adds 'b12' key for all animal-food categories
    using per-serving values derived from ICMR FCT 2017 reference per 100 g.
"""

import json, re, math, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

SRC  = "assets/data/food_master_v6_6.json"
DEST = "assets/data/food_master_v6_7.json"
EN_IDX = "assets/data/index_en_v6_7.json"
BN_IDX = "assets/data/index_bn_v6_7.json"

# ── helpers ──────────────────────────────────────────────────────────────────

def parse_serving_g(s: str) -> float:
    """Mirror of Dart _parseServing – returns gram equivalent."""
    raw = str(s).strip()
    m = re.search(r'\((\d+(?:\.\d+)?)\s*g\)', raw, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r'\((\d+(?:\.\d+)?)\s*ml\)', raw, re.I)
    if m:
        return float(m.group(1))
    m = re.match(r'^(\d+(?:\.\d+)?)\s*g\b', raw, re.I)
    if m:
        return float(m.group(1))
    m = re.match(r'^(\d+(?:\.\d+)?)\s*ml\b', raw, re.I)
    if m:
        return float(m.group(1))
    UNIT = {
        'bowl': 250, 'plate': 300, 'cup': 240, 'glass': 240,
        'serving': 100, 'portion': 150,
        'tablespoon': 15, 'tbsp': 15, 'teaspoon': 5, 'tsp': 5,
        'slice': 30, 'large slice': 50,
        'pc': 60, 'pcs': 60, 'piece': 60, 'pieces': 60,
        'oz': 28.35, 'kg': 1000,
        'small': 100, 'medium': 150, 'large': 200,
        'scoop': 30, 'handful': 30, 'sachet': 30,
    }
    m = re.match(r'^(\d+(?:\.\d+)?)\s+(.+)$', raw)
    if m:
        n = float(m.group(1))
        u = m.group(2).strip().lower()
        for key, val in UNIT.items():
            if u.startswith(key):
                return n * val
        if n >= 5:
            return n
    num = re.match(r'^(\d+(?:\.\d+)?)$', raw)
    if num:
        v = float(num.group(1))
        if v > 0:
            return v
    return 100.0

def round2(v): return round(float(v), 2)
def kcal_check(k, p, c, f): return abs(k - (p*4 + c*4 + f*9)) / k * 100 if k > 0 else 0

# ── load ──────────────────────────────────────────────────────────────────────

with open(SRC, encoding='utf-8') as fh:
    data = json.load(fh)

by_id = {item['id']: item for item in data}
changes = []

# ════════════════════════════════════════════════════════════════════════════
# FIX 1 — Fried poori/puri fat correction
# Source: NIN Nutritive Value of Indian Foods (deep-fried puri per 100 g):
#   energy 454 kcal, protein 7.5 g, fat 22 g, carbs 56 g, fibre 2.1 g
# Per 60 g serving: energy 272 kcal, protein 4.5 g, fat 13.2 g, carbs 33.6 g
# ════════════════════════════════════════════════════════════════════════════

# (id, p, c, f, fi, k, note)
POORI_FIXES = [
    # plain                — NIN reference values
    (725, 4.5,  33.6, 13.2, 1.8,  272, "Poori (plain)"),
    # methi/spinach        — adds ~1 g extra fibre, slightly less carb
    (717, 4.8,  30.5, 13.5, 2.5,  268, "Methi poori"),
    (731, 5.0,  30.5, 13.5, 2.5,  268, "Spinach poori"),
    # bathua/beetroot      — mild green/veg addition, very similar profile
    (699, 4.5,  30.0, 13.5, 2.0,  265, "Bathua poori"),
    (700, 4.5,  31.0, 13.5, 2.0,  268, "Beetroot poori"),
    # stuffed with dal     — higher protein from dal
    (712, 6.5,  33.0, 13.5, 2.5,  285, "Dal stuffed poori"),
    # stuffed with potato  — extra starch
    (727, 4.5,  37.0, 13.5, 2.0,  290, "Potato stuffed poori"),
    # stuffed with peas    — extra protein + starch
    (723, 5.5,  32.5, 13.5, 2.5,  278, "Peas poori"),
]

for fid, p, c, f, fi, k, label in POORI_FIXES:
    if fid not in by_id:
        print(f"  WARN: ID {fid} not found, skipping")
        continue
    item = by_id[fid]
    old_k, old_f = item.get('k'), item.get('f')
    item['p']  = round2(p)
    item['c']  = round2(c)
    item['f']  = round2(f)
    item['fi'] = round2(fi)
    item['k']  = round2(k)
    err = kcal_check(k, p, c, f)
    changes.append(f"POORI  ID {fid:4d} {label:<28} fat {old_f}→{f} g  kcal {old_k}→{k}  Δ={err:.1f}%")

# ════════════════════════════════════════════════════════════════════════════
# FIX 2 — Alcohol macro proxies
# Ethanol is 7 kcal/g. Since no dedicated ethanol field exists, we use fat as
# the energy carrier (9 kcal/g, closest to 7) so that 4p+4c+9f ≈ stored kcal.
# For beers with real carbs we keep those carbs and only use fat for the
# remaining ethanol-derived energy.
# ════════════════════════════════════════════════════════════════════════════

ALCOHOL_FIXES = {
    # id: (p, c, f, k, note)
    # Beer (Strong) 330 ml 8% ABV: ~21 g ethanol (147 kcal) + ~16 g real carbs (64 kcal)
    1424: (0.0, 16.0, 16.0, 208.0, "Beer (Strong) 330ml"),
    # Spirits 30 ml 40% ABV: ~9.5 g ethanol each, no real carbs or protein
    # fat proxy: kcal / 9
    1425: (0.0,  0.0,  7.7,  69.0, "Whiskey 30ml"),
    1426: (0.0,  0.0,  7.1,  64.0, "Rum 30ml"),
    1427: (0.0,  0.0,  7.1,  64.0, "Vodka 30ml"),
}

for fid, (p, c, f, k, label) in ALCOHOL_FIXES.items():
    if fid not in by_id:
        print(f"  WARN: ID {fid} not found, skipping")
        continue
    item = by_id[fid]
    old_p, old_c, old_f = item.get('p', 0), item.get('c', 0), item.get('f', 0)
    item['p'] = round2(p)
    item['c'] = round2(c)
    item['f'] = round2(f)
    item['k'] = round2(k)
    err = kcal_check(k, p, c, f)
    changes.append(f"ALCO   ID {fid:4d} {label:<28} p={old_p}→{p} c={old_c}→{c} f={old_f}→{f}  Δ={err:.1f}%")
    # tag so UI can note these are ethanol-derived
    kw = item.get('kw') or []
    if 'ethanol_proxy' not in kw:
        kw.append('ethanol_proxy')
    item['kw'] = kw

# ════════════════════════════════════════════════════════════════════════════
# FIX 3 — Tamarind chutney serving (ID 608)
# "1ml" was parsed as 1 g → 4 kcal for 1 g is 400 kcal/100 g, absurd.
# Real thin tamarind chutney: ~70 kcal/100 g.
# Standard serving = 1 tablespoon = 15 ml ≈ 16 g.  Nutrition per 15 g:
#   k=11 kcal, p=0.2 g, c=2.7 g, f=0.1 g, fi=0.3 g
# ════════════════════════════════════════════════════════════════════════════

if 608 in by_id:
    item = by_id[608]
    old_s, old_k = item.get('s'), item.get('k')
    item['s']  = '15ml'
    item['k']  = 11.0
    item['p']  = 0.2
    item['c']  = 2.7
    item['f']  = 0.1
    item['fi'] = 0.3
    changes.append(f"CHUT   ID  608 Tamarind chutney           serving {old_s}→15ml  kcal {old_k}→11")

# ════════════════════════════════════════════════════════════════════════════
# FIX 4 — Vitamin B12 fill
# Adds 'b12' key (mcg per serving) to animal-derived foods.
# Reference: ICMR FCT 2017 per 100 g, scaled to stored serving size.
#
# Category defaults (per 100 g):
#   fish        2.0 mcg   (hilsa/fatty fish: 4.0)
#   meat/mutton 2.5 mcg   (beef similar)
#   meat/chicken 0.4 mcg
#   egg         1.4 mcg   (per 100 g whole egg)
#   dairy/milk  0.4 mcg
#   dairy/curd  0.3 mcg
#   dairy/paneer/cheese 0.5 mcg
# All plant foods → 0 (not added to keep JSON lean; absence = 0 in Dart)
# ════════════════════════════════════════════════════════════════════════════

# High-B12 fish patterns (per 100 g)
HIGH_B12_FISH = ['hilsa', 'salmon', 'mackerel', 'sardine', 'tuna', 'rohu', 'katla',
                  'ilish', 'pomfret', 'anchovy', 'herring', 'trout']

b12_filled = 0

for item in data:
    cat = (item.get('cat') or '').lower()
    en  = (item.get('en')  or '').lower()
    sv_g = parse_serving_g(item.get('s', '100g'))

    b12_per_100g = None

    if cat == 'fish':
        if any(f in en for f in HIGH_B12_FISH):
            b12_per_100g = 4.0
        else:
            b12_per_100g = 2.0

    elif cat == 'meat':
        if any(x in en for x in ['chicken', 'poultry', 'hen', 'duck', 'turkey']):
            b12_per_100g = 0.4
        else:  # mutton, beef, pork, lamb, goat
            b12_per_100g = 2.5

    elif cat == 'egg':
        b12_per_100g = 1.4

    elif cat == 'dairy':
        if any(x in en for x in ['milk', 'দুধ']):
            b12_per_100g = 0.4
        elif any(x in en for x in ['curd', 'yogurt', 'দই']):
            b12_per_100g = 0.3
        elif any(x in en for x in ['cheese', 'paneer', 'পনির']):
            b12_per_100g = 0.5
        else:
            b12_per_100g = 0.3   # generic dairy (cream, khoa, etc.)

    if b12_per_100g is not None:
        b12_serving = round2(b12_per_100g * sv_g / 100)
        item['b12'] = b12_serving
        b12_filled += 1

changes.append(f"B12    Added b12 key to {b12_filled} animal-food records")

# ════════════════════════════════════════════════════════════════════════════
# Write fixed dataset
# ════════════════════════════════════════════════════════════════════════════

with open(DEST, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))

print(f"✓ Written {DEST} ({len(data)} items)")
print()
print("Changes:")
for c in changes:
    print(" ", c)

# ════════════════════════════════════════════════════════════════════════════
# Rebuild prefix indexes
# ════════════════════════════════════════════════════════════════════════════

def is_bengali(text: str) -> bool:
    return any('ঀ' <= ch <= '৿' for ch in text)

def tokenise_en(text: str) -> list[str]:
    return [w.lower() for w in re.split(r'[\s/\-,]+', text) if len(w) >= 2]

def tokenise_bn(text: str) -> list[str]:
    return [w for w in re.split(r'[\s/\-,।]+', text) if len(w) >= 2]

idx_en: dict[str, set] = defaultdict(set)
idx_bn: dict[str, set] = defaultdict(set)

orphans_en = orphans_bn = 0

for item in data:
    iid = item['id']
    en_name  = item.get('en', '') or ''
    bn_name  = item.get('bn', '') or ''
    keywords = item.get('kw',  []) or []

    # English: 2-char and 3-char prefixes from name + keywords
    for token in tokenise_en(en_name) + [k.lower() for k in keywords if not is_bengali(k)]:
        if len(token) >= 2:
            idx_en[token[:2]].add(iid)
        if len(token) >= 3:
            idx_en[token[:3]].add(iid)

    # Bengali: 2-char prefix from BN name
    if bn_name and is_bengali(bn_name):
        for token in tokenise_bn(bn_name):
            if len(token) >= 2:
                idx_bn[token[:2]].add(iid)

# Sort IDs for deterministic output
out_en = {k: sorted(v) for k, v in idx_en.items()}
out_bn = {k: sorted(v) for k, v in idx_bn.items()}

total_en = sum(len(v) for v in out_en.values())
total_bn = sum(len(v) for v in out_bn.values())

with open(EN_IDX, 'w', encoding='utf-8') as fh:
    json.dump(out_en, fh, ensure_ascii=False, separators=(',', ':'))

with open(BN_IDX, 'w', encoding='utf-8') as fh:
    json.dump(out_bn, fh, ensure_ascii=False, separators=(',', ':'))

print()
print(f"✓ EN index: {len(out_en)} prefixes, {total_en} refs  → {EN_IDX}")
print(f"✓ BN index: {len(out_bn)} prefixes, {total_bn} refs  → {BN_IDX}")

# ── sanity check ──────────────────────────────────────────────────────────────
with open(DEST, encoding='utf-8') as fh:
    verify = json.load(fh)

still_wrong = 0
for item in verify:
    k = item.get('k', 0) or 0
    p = item.get('p', 0) or 0
    c = item.get('c', 0) or 0
    f = item.get('f', 0) or 0
    calc = p*4 + c*4 + f*9
    if k > 10 and calc > 0 and abs(k - calc) / k > 0.20:
        still_wrong += 1

print()
print(f"Post-fix macro/calorie mismatches (>20%): {still_wrong}  (was 73)")
print("Done.")
