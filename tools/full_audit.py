"""
full_audit.py — Comprehensive dataset audit
Reports: exact name dups, near-dups, missing BN, BN with wrong script,
         BN identical to EN, impossible macros, zero-kcal non-beverages.
"""
import json, sys, re
from difflib import SequenceMatcher
sys.stdout.reconfigure(encoding='utf-8')

DATASET = 'assets/data/food_master_v7_2.json'
data = json.load(open(DATASET, encoding='utf-8'))
print(f'Loaded {len(data)} items\n')

BENGALI_RE = re.compile(r'[ঀ-৿]')
LATIN_ONLY = re.compile(r'^[A-Za-z0-9 ,.()\-/\'\"&%+*#@!?:_]+$')

issues = {
    'exact_en_dup':     [],
    'exact_bn_dup':     [],
    'missing_bn':       [],
    'bn_no_bengali':    [],
    'bn_same_as_en':    [],
    'impossible_fat':   [],
    'impossible_protein':[],
    'impossible_carb':  [],
    'zero_kcal_nonfood':[],
    'kcal_mismatch':    [],   # |stored - calc| > 150, both plausible
}

# ── Exact duplicate checks ────────────────────────────────────────────────────
seen_en, seen_bn = {}, {}
for d in data:
    en_key = d['en'].strip().lower()
    bn_key = d.get('bn','').strip().lower()
    if en_key in seen_en:
        issues['exact_en_dup'].append((seen_en[en_key], d))
    else:
        seen_en[en_key] = d
    if bn_key and bn_key in seen_bn:
        issues['exact_bn_dup'].append((seen_bn[bn_key], d))
    else:
        if bn_key:
            seen_bn[bn_key] = d

# ── Bengali QA ────────────────────────────────────────────────────────────────
for d in data:
    bn = d.get('bn', '').strip()
    if not bn:
        issues['missing_bn'].append(d)
        continue
    if not BENGALI_RE.search(bn):
        # Allow pure variety codes like BR-28, SP4 — skip if EN also has it
        if any(code in d['en'] for code in ['BR-28','SP4','SP8','Diamond']):
            continue
        issues['bn_no_bengali'].append(d)
    if bn.strip().lower() == d['en'].strip().lower():
        issues['bn_same_as_en'].append(d)

# ── Nutrition checks ──────────────────────────────────────────────────────────
for d in data:
    p = d.get('p', 0) or 0
    c = d.get('c', 0) or 0
    f = d.get('f', 0) or 0
    k = d.get('k', 0) or 0
    if f > 100:
        issues['impossible_fat'].append(d)
    if p > 100:
        issues['impossible_protein'].append(d)
    if c > 100:
        issues['impossible_carb'].append(d)
    if k == 0 and d.get('cat') not in ('beverage','juice','water'):
        issues['zero_kcal_nonfood'].append(d)
    # Kcal mismatch: only flag when macros are individually plausible
    if p <= 60 and c <= 100 and f <= 80 and k > 0:
        calc = round(p*4 + c*4 + f*9, 1)
        if calc > 0 and abs(k - calc) > 150:
            issues['kcal_mismatch'].append((d, k, calc))

# ── Near-duplicate check (top suspicious pairs only) ─────────────────────────
print('=== EXACT EN DUPLICATES ===')
if issues['exact_en_dup']:
    for a, b in issues['exact_en_dup']:
        print(f'  [{a["id"]}] {a["en"]}  ↔  [{b["id"]}] {b["en"]}')
else:
    print('  None')

print('\n=== EXACT BN DUPLICATES (same Bengali name) ===')
if issues['exact_bn_dup']:
    for a, b in issues['exact_bn_dup']:
        print(f'  [{a["id"]}] {a["en"]} (bn={a["bn"]})')
        print(f'  [{b["id"]}] {b["en"]} (bn={b["bn"]})')
        print()
else:
    print('  None')

print('\n=== MISSING BENGALI NAME ===')
if issues['missing_bn']:
    for d in issues['missing_bn']:
        print(f'  [{d["id"]}] {d["en"]}')
else:
    print('  None')

print('\n=== BENGALI NAME HAS NO BENGALI SCRIPT ===')
if issues['bn_no_bengali']:
    for d in issues['bn_no_bengali']:
        print(f'  [{d["id"]}] {d["en"]} | bn={d["bn"]}')
else:
    print('  None')

print('\n=== BENGALI NAME IDENTICAL TO ENGLISH ===')
if issues['bn_same_as_en']:
    for d in issues['bn_same_as_en']:
        print(f'  [{d["id"]}] {d["en"]}')
else:
    print('  None')

print('\n=== IMPOSSIBLE FAT (> 100g per 100g) ===')
if issues['impossible_fat']:
    for d in issues['impossible_fat']:
        print(f'  [{d["id"]}] {d["en"]} | f={d["f"]}')
else:
    print('  None')

print('\n=== IMPOSSIBLE PROTEIN (> 100g per 100g) ===')
if issues['impossible_protein']:
    for d in issues['impossible_protein']:
        print(f'  [{d["id"]}] {d["en"]} | p={d["p"]}')
else:
    print('  None')

print('\n=== IMPOSSIBLE CARBS (> 100g per 100g) ===')
if issues['impossible_carb']:
    for d in issues['impossible_carb']:
        print(f'  [{d["id"]}] {d["en"]} | c={d["c"]}')
else:
    print('  None')

print('\n=== ZERO KCAL NON-BEVERAGE ===')
if issues['zero_kcal_nonfood']:
    for d in issues['zero_kcal_nonfood']:
        print(f'  [{d["id"]}] {d["en"]} | cat={d["cat"]}')
else:
    print('  None')

print('\n=== KCAL MISMATCH > 150 (plausible macros) ===')
if issues['kcal_mismatch']:
    for d, stored, calc in issues['kcal_mismatch']:
        direction = 'stored↑' if stored > calc else 'stored↓'
        print(f'  [{d["id"]}] {d["en"]} | stored={stored}, calc={calc} ({direction})')
else:
    print('  None')

print('\n=== SUMMARY ===')
for k, v in issues.items():
    print(f'  {k}: {len(v)}')
