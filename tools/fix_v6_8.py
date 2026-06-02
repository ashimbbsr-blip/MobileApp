"""
fix_v6_8.py — Produces food_master_v6_8.json + index_en/bn_v6_8.json

Fixes applied
─────────────
1.  Alcohol alc_g field  — Replaces the fat-as-ethanol proxy with a proper
    alc_g (grams of ethanol per serving) field. Fat is corrected to actual
    dietary fat (≈0 for pure spirits; ≈0 for beer). Calorie balance preserved.
    Affected IDs: 1424 (Beer Strong), 1425 (Whiskey), 1426 (Rum), 1427 (Vodka).

2.  Column-swap heuristic  — Detects remaining macro/calorie mismatches where
    the fat and carb columns appear swapped (BD FCT column-shift artifact).
    Applies the swap only when:
      a) |k - calc| / k > 20%  (real mismatch)
      b) Swapping f↔c reduces error to < 10%
      c) Post-swap fat ≤ 40 g (physically plausible)
      d) Post-swap carbs ≥ 0 g
    Does NOT touch items already corrected in v6_7 (poori, tamarind, B12 fill).
"""

import json, re, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

SRC    = "assets/data/food_master_v6_7.json"
DEST   = "assets/data/food_master_v6_8.json"
EN_IDX = "assets/data/index_en_v6_8.json"
BN_IDX = "assets/data/index_bn_v6_8.json"

# ── helpers ──────────────────────────────────────────────────────────────────

def round2(v): return round(float(v), 2)

def mismatch_pct(k, p, c, f, alc_g=0.0):
    calc = p * 4 + c * 4 + f * 9 + alc_g * 7
    if k <= 0:
        return 0.0
    return abs(k - calc) / k * 100

# ── load ─────────────────────────────────────────────────────────────────────

with open(SRC, encoding='utf-8') as fh:
    data = json.load(fh)

by_id = {item['id']: item for item in data}
changes = []

# ════════════════════════════════════════════════════════════════════════════
# FIX 1 — Proper alcohol_g field for ethanol-carrying items
#
# Real values derived from ABV × volume × ethanol density (0.789 g/ml):
#   Beer Strong 330ml 8% ABV : ethanol_g = 330 × 0.08 × 0.789 = 20.8 g
#   Spirits 30ml 40% ABV     : ethanol_g = 30 × 0.40 × 0.789 = 9.5 g
#
# Fat for pure spirits is effectively 0.  Beer has trace fat (≈0).
# Stored kcal (k) remains as-is — it was correct in v6_7.
# ════════════════════════════════════════════════════════════════════════════

ALCOHOL_G_FIXES = {
    # id: (alc_g, p, c, f)  — fat set to 0; alc_g × 7 ≈ stored k (minus carb contribution)
    1424: (20.6, 0.0, 16.0, 0.0),   # Beer Strong 330ml — 20.6×7 + 16×4 = 144.2+64 = 208.2 ≈ 208
    1425: ( 9.9, 0.0,  0.0, 0.0),   # Whiskey 30ml      — 9.9×7 = 69.3 ≈ 69
    1426: ( 9.1, 0.0,  0.0, 0.0),   # Rum 30ml          — 9.1×7 = 63.7 ≈ 64
    1427: ( 9.1, 0.0,  0.0, 0.0),   # Vodka 30ml        — 9.1×7 = 63.7 ≈ 64
}

for fid, (alc_g, p, c, f) in ALCOHOL_G_FIXES.items():
    if fid not in by_id:
        print(f"  WARN: ID {fid} not found, skipping")
        continue
    item = by_id[fid]
    old_f = item.get('f', 0)
    item['alc_g'] = round2(alc_g)
    item['p'] = round2(p)
    item['c'] = round2(c)
    item['f'] = round2(f)
    err = mismatch_pct(item['k'], p, c, f, alc_g)
    changes.append(
        f"ALCO   ID {fid:4d} {item.get('en',''):<30} "
        f"alc_g={alc_g}g  fat {old_f}→{f}g  Δ={err:.1f}%"
    )
    # Remove ethanol_proxy tag — no longer needed
    kw = item.get('kw') or []
    if 'ethanol_proxy' in kw:
        kw.remove('ethanol_proxy')
    item['kw'] = kw

# ════════════════════════════════════════════════════════════════════════════
# FIX 2 — Column-swap heuristic for remaining macro/calorie mismatches
#
# BD FCT column-shift pattern: fat and carb columns were transposed during
# PDF extraction.  Symptom: stored fat >> expected fat for the food category,
# stored carbs << expected.  The calorie mismatch resolves if we swap them.
# ════════════════════════════════════════════════════════════════════════════

# IDs already corrected in v6_7 (skip to avoid double-patching)
ALREADY_FIXED_V67 = {608, 699, 700, 712, 717, 723, 725, 727, 731,
                     1424, 1425, 1426, 1427}

swap_fixed = 0
swap_skipped_details = []

for item in data:
    fid = item['id']
    if fid in ALREADY_FIXED_V67:
        continue

    k    = float(item.get('k', 0) or 0)
    p    = float(item.get('p', 0) or 0)
    c    = float(item.get('c', 0) or 0)
    f    = float(item.get('f', 0) or 0)
    alc  = float(item.get('alc_g', 0) or 0)

    if k <= 10:
        continue  # too small to matter

    err_orig = mismatch_pct(k, p, c, f, alc)
    if err_orig <= 20.0:
        continue  # already good

    # Try f↔c swap
    err_swap = mismatch_pct(k, p, f, c, alc)

    if (err_swap < 10.0          # swap brings it within 10%
            and c >= 0           # new fat (was c) is non-negative
            and c <= 40.0        # new fat is physically plausible
            and f >= 0):         # new carbs (was f) is non-negative
        item['c'] = round2(f)   # new carbs = old fat
        item['f'] = round2(c)   # new fat   = old carbs
        swap_fixed += 1
        changes.append(
            f"SWAP   ID {fid:4d} {item.get('en',''):<30} "
            f"f {f}→{round2(c)}g  c {c}→{round2(f)}g  "
            f"Δ {err_orig:.0f}%→{err_swap:.1f}%"
        )
    else:
        swap_skipped_details.append(
            f"       ID {fid:4d} {item.get('en',''):<30} "
            f"orig_err={err_orig:.0f}%  swap_err={err_swap:.0f}%  "
            f"f={f}  c={c}  (skipped — swap not confident)"
        )

changes.append(f"SWAP   Applied column-swap fix to {swap_fixed} items")

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

if swap_skipped_details:
    print()
    print(f"Skipped (swap not confident — {len(swap_skipped_details)} items):")
    for line in swap_skipped_details[:30]:
        print(line)
    if len(swap_skipped_details) > 30:
        print(f"  ... and {len(swap_skipped_details) - 30} more")

# ════════════════════════════════════════════════════════════════════════════
# Rebuild prefix indexes
# ════════════════════════════════════════════════════════════════════════════

def is_bengali(text: str) -> bool:
    return any('ঀ' <= ch <= '৿' for ch in text)

def tokenise_en(text: str) -> list:
    return [w.lower() for w in re.split(r'[\s/\-,]+', text) if len(w) >= 2]

def tokenise_bn(text: str) -> list:
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

total_en = sum(len(v) for v in out_en.values())
total_bn = sum(len(v) for v in out_bn.values())

with open(EN_IDX, 'w', encoding='utf-8') as fh:
    json.dump(out_en, fh, ensure_ascii=False, separators=(',', ':'))

with open(BN_IDX, 'w', encoding='utf-8') as fh:
    json.dump(out_bn, fh, ensure_ascii=False, separators=(',', ':'))

print()
print(f"✓ EN index: {len(out_en)} prefixes, {total_en} refs  → {EN_IDX}")
print(f"✓ BN index: {len(out_bn)} prefixes, {total_bn} refs  → {BN_IDX}")

# ── sanity check ─────────────────────────────────────────────────────────────

with open(DEST, encoding='utf-8') as fh:
    verify = json.load(fh)

still_wrong = []
for item in verify:
    k    = item.get('k', 0) or 0
    p    = item.get('p', 0) or 0
    c    = item.get('c', 0) or 0
    f    = item.get('f', 0) or 0
    alc  = item.get('alc_g', 0) or 0
    if k > 10 and mismatch_pct(k, p, c, f, alc) > 20:
        still_wrong.append(
            f"  ID {item['id']:4d} {item.get('en',''):<35} "
            f"k={k} calc={round2(p*4+c*4+f*9+alc*7)} Δ={mismatch_pct(k,p,c,f,alc):.0f}%"
        )

print()
print(f"Post-fix macro/calorie mismatches (>20%): {len(still_wrong)}  (was 67)")
if still_wrong:
    print("Remaining — need FCT manual cross-reference:")
    for line in still_wrong[:20]:
        print(line)
    if len(still_wrong) > 20:
        print(f"  ... and {len(still_wrong) - 20} more")
print("Done.")
