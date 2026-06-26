"""
audit_fix.py — Apply audit fixes to food_master_v7_2.json

Fixes:
  1. Remove 6 true duplicates (inferior entry removed, better entry kept)
  2. Fix 5 items with physically impossible fat values (> 100g per 100g)
  3. Recalculate kcal for items where |stored - calculated| > 200 and
     all individual macros are plausible (p<60, c<100, f<80)
"""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'

# ── 1. TRUE DUPLICATES TO REMOVE ─────────────────────────────────────────────
# (keep ID listed in "keep", remove ID listed here)
REMOVE_IDS = {
    1410,   # Maachha Jhola  — duplicate of 30012 Machha Jhola (better BN + nutrition)
    232,    # Shorshe Ilish  — duplicate of 4012 Sorshe Ilish (k=320 inflated)
    588,    # Shammi kebab   — duplicate of 60017 Shami Kebab (k=174 too low, BN wrong)
    349,    # Mutton chops   — duplicate of 3037 Mutton Chop
    518,    # Mal pua        — duplicate of 96022 Malpua (k=847.9 impossible, BN typo)
    350,    # Mutton do piaza— duplicate of 3021 Mutton Do Pyaza (k=603.1 impossible, BN typo)
}

# ── 2. IMPOSSIBLE FAT FIXES (fat > 100g per 100g serving) ───────────────────
# Corrected values from USDA / ICMR reference data
FAT_FIXES = {
    455: {'f': 40.0,  'k': 420},   # French dressing (was f=160.4) — ~40g fat /100g
    524: {'f': 75.0,  'k': 700},   # Mayonnaise (was f=131) — USDA: ~75g fat /100g
    543: {'f': 28.0,  'k': 380},   # Papdi (was f=125.2) — fried snack ~28g fat /100g
    620: {'f': 12.0,  'k': 120},   # Veg manchurian (was f=120.2) — ~12g fat /100g
    762: {'f': 35.0,  'k': 530},   # Banana chips (was f=120) — ~35g fat /100g
}

data = json.load(open(DATASET, encoding='utf-8'))
print(f'Loaded {len(data)} items')

# ── Step 1: Remove duplicates ─────────────────────────────────────────────────
before = len(data)
data = [d for d in data if d['id'] not in REMOVE_IDS]
removed = before - len(data)
print(f'Removed {removed} duplicate entries (IDs: {sorted(REMOVE_IDS)})')

# ── Step 2: Fix impossible fat values ─────────────────────────────────────────
id_map = {d['id']: d for d in data}
fat_fixed = 0
for fid, fix in FAT_FIXES.items():
    if fid in id_map:
        item = id_map[fid]
        old_f = item.get('f', '?')
        old_k = item.get('k', '?')
        item.update(fix)
        print(f'  FAT FIX [{fid}] {item["en"]}: f={old_f}→{fix["f"]}, k={old_k}→{fix["k"]}')
        fat_fixed += 1
    else:
        print(f'  FAT FIX [{fid}]: NOT FOUND (already removed or bad ID)')
print(f'Fat fixes applied: {fat_fixed}')

# ── Step 3: Recalculate kcal for large divergence ────────────────────────────
# Only fix if all individual macros are plausible (not per-item values)
# Thresholds: p<60, c<100, f<80 — if all pass, recalc is safe
kcal_fixed = 0
for item in data:
    p = item.get('p', 0) or 0
    c = item.get('c', 0) or 0
    f = item.get('f', 0) or 0
    k = item.get('k', 0) or 0
    if p > 60 or c > 100 or f > 80:
        continue   # macros look like per-item values; skip
    calc = round(p * 4 + c * 4 + f * 9, 1)
    if calc == 0:
        continue   # skip zero-calorie items (diet drinks etc.)
    diff = abs(k - calc)
    if diff > 200:
        print(f'  KCAL FIX [{item["id"]}] {item["en"]}: stored={k}, calc={calc}, diff={diff}')
        item['k'] = calc
        kcal_fixed += 1

print(f'Kcal recalculations: {kcal_fixed}')

# ── Save ──────────────────────────────────────────────────────────────────────
print(f'\nFinal item count: {len(data)}')
with open(DATASET, 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False, separators=(',', ':'))
print('Saved.')
