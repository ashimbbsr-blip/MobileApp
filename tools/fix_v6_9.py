"""
fix_v6_9.py — Produces food_master_v6_9.json + index_en/bn_v6_9.json

Fixes applied
─────────────
1.  Biryani keyword unification  — All biryani items get both 'biryani' and
    'biriyani' spellings in keywords so either search hits all variants.
    Chicken biryani renamed to 'Chicken biryani/biriyani' for name consistency.

2.  Category fixes — Items miscategorised in the dataset are corrected:
    a) 'grain' items that are bread/roti → 'bread'  (Ruti, Odia Puri, bun/roll, white bread)
    b) 'snack' items that are legumes → 'legume'  (whole urad/moong/masoor, etc.)
    c) 'grain' biscuit → 'sweet'

3.  Dal keyword fill  — All legume-category items get 'dal' added to keywords
    for better discoverability when users search 'dal'.

4.  Roti keyword fill — All bread-category items get 'roti' added to keywords.
"""

import json, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

SRC    = "assets/data/food_master_v6_8.json"
DEST   = "assets/data/food_master_v6_9.json"
EN_IDX = "assets/data/index_en_v6_9.json"
BN_IDX = "assets/data/index_bn_v6_9.json"

with open(SRC, encoding='utf-8') as fh:
    data = json.load(fh)

by_id = {item['id']: item for item in data}
changes = []

def add_kw(item, *words):
    kw = list(item.get('kw') or [])
    added = []
    for w in words:
        if w not in kw:
            kw.append(w)
            added.append(w)
    item['kw'] = kw
    return added

# ════════════════════════════════════════════════════════════════════════════
# FIX 1 — Biryani keyword unification
# ════════════════════════════════════════════════════════════════════════════

BIRYANI_IDS = {678, 684, 697, 1430}

for fid in BIRYANI_IDS:
    if fid not in by_id:
        continue
    item = by_id[fid]
    added = add_kw(item, 'biryani', 'biriyani', 'rice')
    changes.append(f"BIRYANI ID {fid:4d} {item.get('en',''):<40} +kw={added}")

# Rename chicken biryani for consistency with mutton/vegetable naming
if 1430 in by_id:
    old_en = by_id[1430]['en']
    if '/' not in old_en:
        by_id[1430]['en'] = 'Chicken biryani/biriyani'
        changes.append(f"RENAME  ID 1430 '{old_en}' → 'Chicken biryani/biriyani'")

# ════════════════════════════════════════════════════════════════════════════
# FIX 2 — Category corrections
# ════════════════════════════════════════════════════════════════════════════

# 2a  Grain → bread  (roti/bread items mistakenly in grain)
GRAIN_TO_BREAD = {
    1069,  # Bread, bun/roll
    1070,  # Bread, white, for toasting
    1096,  # Ruti* Ruti  (Bengali Roti)
    1419,  # Odia Puri
}
for fid in GRAIN_TO_BREAD:
    if fid in by_id:
        item = by_id[fid]
        item['cat'] = 'bread'
        add_kw(item, 'bread', 'roti')
        changes.append(f"CAT     ID {fid:4d} grain → bread  {item.get('en','')}")

# 2b  Grain → sweet  (biscuit)
if 1091 in by_id:
    by_id[1091]['cat'] = 'sweet'
    changes.append(f"CAT     ID 1091 grain → sweet  {by_id[1091].get('en','')}")

# 2c  Snack → legume  (whole/dried lentils and beans)
SNACK_TO_LEGUME = {
    450,   # Dry washed urad
    512,   # Lentils and semolina porridge
    593,   # Sour lentils
    617,   # Urad sabut special
    618,   # Urad special dehusked
    632,   # Whole masoor
    633,   # Whole moong
    635,   # Whole urad
}
for fid in SNACK_TO_LEGUME:
    if fid in by_id:
        item = by_id[fid]
        item['cat'] = 'legume'
        add_kw(item, 'dal', 'lentil')
        changes.append(f"CAT     ID {fid:4d} snack → legume  {item.get('en','')}")

# ════════════════════════════════════════════════════════════════════════════
# FIX 3 — Dal keyword fill for all legume items
# ════════════════════════════════════════════════════════════════════════════

dal_kw_added = 0
for item in data:
    if item.get('cat') == 'legume':
        added = add_kw(item, 'dal')
        if added:
            dal_kw_added += 1

changes.append(f"DALWKW  Added 'dal' keyword to {dal_kw_added} legume items")

# ════════════════════════════════════════════════════════════════════════════
# FIX 4 — Roti keyword fill for all bread items
# ════════════════════════════════════════════════════════════════════════════

roti_kw_added = 0
for item in data:
    if item.get('cat') == 'bread':
        added = add_kw(item, 'roti', 'bread')
        if added:
            roti_kw_added += 1

changes.append(f"ROTIKW  Added 'roti/bread' keyword to {roti_kw_added} bread items")

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

def is_bengali(text):
    return any('ঀ' <= ch <= '৿' for ch in text)

def tokenise_en(text):
    return [w.lower() for w in re.split(r'[\s/\-,]+', text) if len(w) >= 2]

def tokenise_bn(text):
    return [w for w in re.split(r'[\s/\-,।]+', text) if len(w) >= 2]

idx_en = defaultdict(set)
idx_bn = defaultdict(set)

for item in data:
    iid = item['id']
    en_name  = item.get('en', '') or ''
    bn_name  = item.get('bn', '') or ''
    keywords = item.get('kw',  []) or []

    for token in tokenise_en(en_name) + [k.lower() for k in keywords if not is_bengali(k)]:
        if len(token) >= 2:
            idx_en[token[:2]].add(iid)
        if len(token) >= 3:
            idx_en[token[:3]].add(iid)

    if bn_name and is_bengali(bn_name):
        for token in tokenise_bn(bn_name):
            if len(token) >= 2:
                idx_bn[token[:2]].add(iid)

out_en = {k: sorted(v) for k, v in idx_en.items()}
out_bn = {k: sorted(v) for k, v in idx_bn.items()}

with open(EN_IDX, 'w', encoding='utf-8') as fh:
    json.dump(out_en, fh, ensure_ascii=False, separators=(',', ':'))

with open(BN_IDX, 'w', encoding='utf-8') as fh:
    json.dump(out_bn, fh, ensure_ascii=False, separators=(',', ':'))

total_en = sum(len(v) for v in out_en.values())
total_bn = sum(len(v) for v in out_bn.values())
print()
print(f"✓ EN index: {len(out_en)} prefixes, {total_en} refs")
print(f"✓ BN index: {len(out_bn)} prefixes, {total_bn} refs")

# ── Category count summary ───────────────────────────────────────────────────
from collections import Counter
cats = Counter(item.get('cat','?') for item in data)
print()
print("Category distribution in v6_9:")
for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {cat:<15} {cnt:3d} items")
print("Done.")
