"""
Dataset audit and fix script for food_master_v10.json.
Fixes:
  1. Appam (ID 17)  — fat was 34.6g in 60g (physically impossible)
  2. Subway sauces  — per-100g values stored against 14g/5g servings
  3. Ponnankanni     — stated k=251 for a leafy green; fe=60 (impossible iron)
  4. Almond soup     — 100g-based macros entered against 250g serving
  5. Category-based micronutrient fill for items with all-zero micros
  6. Recalculate k from macros for items with >25% mismatch (excluding
     spices, sweets from reference DBs, and alcohol-heavy items)
"""

import json, sys, math, re, os

sys.stdout.reconfigure(encoding='utf-8')

IN_FILE  = 'assets/data/food_master_v10.json'
OUT_FILE = 'assets/data/food_master_v10.json'
BACKUP   = 'assets/data/food_master_v10_pre_audit.json'

# ── Category-based micronutrient defaults (per typical serving) ───────────────
# Applied only to items where ALL of ca, fe, mg, pot are None/0
# Values are conservative minimums — better than hardcoded 0.0
CATEGORY_MICRO = {
    'vegetable':      {'ca': 38,  'fe': 1.0, 'mg': 20, 'pot': 200},
    'shaak':          {'ca': 80,  'fe': 2.5, 'mg': 30, 'pot': 250},
    'legume':         {'ca': 45,  'fe': 2.5, 'mg': 38, 'pot': 340},
    'fish':           {'ca': 32,  'fe': 1.2, 'mg': 24, 'pot': 280},
    'meat':           {'ca': 14,  'fe': 1.8, 'mg': 18, 'pot': 270},
    'egg':            {'ca': 50,  'fe': 1.6, 'mg': 10, 'pot': 130},
    'dairy':          {'ca': 115, 'fe': 0.1, 'mg': 11, 'pot': 145},
    'grain':          {'ca': 22,  'fe': 1.4, 'mg': 28, 'pot': 110},
    'rice':           {'ca': 10,  'fe': 0.5, 'mg': 12, 'pot': 70},
    'bread':          {'ca': 28,  'fe': 1.6, 'mg': 20, 'pot': 90},
    'breakfast':      {'ca': 22,  'fe': 1.0, 'mg': 15, 'pot': 100},
    'fruit':          {'ca': 16,  'fe': 0.4, 'mg': 12, 'pot': 195},
    'snack':          {'ca': 20,  'fe': 1.0, 'mg': 18, 'pot': 100},
    'sweet':          {'ca': 40,  'fe': 0.5, 'mg': 12, 'pot': 80},
    'soup':           {'ca': 25,  'fe': 0.8, 'mg': 14, 'pot': 150},
    'salad':          {'ca': 35,  'fe': 0.8, 'mg': 16, 'pot': 180},
    'restaurant_food':{'ca': 30,  'fe': 1.2, 'mg': 18, 'pot': 190},
    'beverage':       {'ca': 12,  'fe': 0.1, 'mg': 8,  'pot': 80},
    'juice':          {'ca': 10,  'fe': 0.2, 'mg': 8,  'pot': 150},
    'bakery':         {'ca': 18,  'fe': 0.8, 'mg': 12, 'pot': 70},
    'pizza':          {'ca': 120, 'fe': 1.5, 'mg': 18, 'pot': 150},
    'noodle':         {'ca': 15,  'fe': 0.8, 'mg': 14, 'pot': 80},
}

# Categories where stated k may differ from macro-calc by design
# (spices, fermented foods, alcohol) — don't auto-correct these
SKIP_K_FIX_CATS = {'beverage', 'juice'}

SKIP_K_FIX_KEYWORDS = [
    'whisky','whiskey','rum','vodka','gin','beer','wine','brandy',
    'clove','cinnamon','cardamom','bay leaf','tej patta','turmeric','chili powder',
    'coriander powder','cumin powder','pepper powder','garam masala',
    'methi seed','fenugreek seed','asafoetida',
]

# ── Subway sauce serving multipliers (per-100g values → actual serving) ──────
SUBWAY_SERVING_FRACTIONS = {
    59146: 14/100,  # Baja Chipotle Sauce (14g serving)
    59148: 14/100,  # Mayonnaise
    59149: 14/100,  # Honey Mustard
    59150: 14/100,  # MVP Parmesan Vinaigrette
    59151: 14/100,  # Peppercorn Ranch
    59152: 14/100,  # Roasted Garlic Aioli
    59154: 14/100,  # Creamy Sriracha
    59156:  5/100,  # Olive Oil Blend (5g serving)
}

# ── Specific targeted fixes ───────────────────────────────────────────────────
SPECIFIC_FIXES = {
    # Appam — ICMR standard for 60g serving
    17: {
        'k': 104.0, 'p': 1.9, 'c': 21.2, 'f': 2.2, 'fi': 0.5,
        'ca': 12.0, 'fe': 1.0, 'zn': 0.5, 'mg': 15.0, 'pot': 99.0,
        'vc': 0.0, 'vd': 0.0,
        '_note': 'ICMR std: fat was 34.6g (impossible in 60g Appam)'
    },
    # Ponnankanni leafy green — k from macros; fe was 60mg (unrealistic)
    1476: {
        'k': 73.0,
        'fe': 5.0,   # real range 4-17 mg/100g; use conservative 5
        '_note': 'k corrected from macros; fe=60 was data entry error'
    },
    # Almond soup — macros were per 100g but serving is 250g;
    # divide macros by 2.5 so calc aligns with stated k=375.2
    374: {
        'p': round(48.3/2.5, 1),   # 19.3
        'c': round(17.6/2.5, 1),   # 7.0
        'f': round(65.8/2.5, 1),   # 26.3
        'fi': round(4.3/2.5, 1),   # 1.7
        '_note': 'macros were per-100g stored against 250g serving'
    },
}


def round2(v):
    return round(float(v), 2)

def calc_k(item):
    p   = item.get('p',   0) or 0
    c   = item.get('c',   0) or 0
    f   = item.get('f',   0) or 0
    alc = item.get('alc_g', 0) or 0
    return p*4 + c*4 + f*9 + alc*7

def needs_micro_fill(item):
    """Return True if all trackable micronutrients are absent/zero."""
    keys = ['ca', 'fe', 'mg', 'pot', 'zn', 'va', 'vc', 'vd', 'b12']
    return not any(item.get(k) for k in keys)

def should_skip_k_fix(item):
    if item.get('cat') in SKIP_K_FIX_CATS:
        return True
    en = item.get('en', '').lower()
    return any(kw in en for kw in SKIP_K_FIX_KEYWORDS)


# ── Main ──────────────────────────────────────────────────────────────────────

with open(IN_FILE, encoding='utf-8') as f:
    data = json.load(f)

# backup
with open(BACKUP, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',',':'))
print(f'Backed up to {BACKUP}')

stats = {
    'specific': 0,
    'subway': 0,
    'k_recalc': 0,
    'micro_fill': 0,
}

for item in data:
    iid = item.get('id')

    # ── Specific targeted fixes ────────────────────────────────────────────
    if iid in SPECIFIC_FIXES:
        fix = SPECIFIC_FIXES[iid]
        for k, v in fix.items():
            if k != '_note':
                item[k] = v
        print(f"  [SPECIFIC] ID {iid} {item.get('en')}: {fix.get('_note','')}")
        stats['specific'] += 1

    # ── Subway sauces — scale per-100g values to actual serving ───────────
    if iid in SUBWAY_SERVING_FRACTIONS:
        frac = SUBWAY_SERVING_FRACTIONS[iid]
        for field in ['k','p','c','f','fi','ca','fe','mg','pot','zn','na','vc']:
            if item.get(field) is not None:
                item[field] = round2(item[field] * frac)
        print(f"  [SUBWAY]   ID {iid} {item.get('en')}: scaled by {frac:.3f}")
        stats['subway'] += 1

    # ── Macro-calorie mismatch: recalc k from macros ───────────────────────
    # Only for non-spice items where calc is HIGHER than stated by >25% and >60 kcal
    # This indicates stated k was manually entered lower (data entry error)
    if iid not in SPECIFIC_FIXES and iid not in SUBWAY_SERVING_FRACTIONS:
        k_stated = item.get('k', 0) or 0
        k_calc   = calc_k(item)
        if k_stated > 0 and k_calc > 0:
            diff = k_calc - k_stated
            pct  = diff / k_stated
            if pct > 0.25 and diff > 60 and not should_skip_k_fix(item):
                item['k'] = round2(k_calc)
                stats['k_recalc'] += 1

    # ── Micronutrient fill for items with all-zero micros ─────────────────
    if needs_micro_fill(item):
        cat = item.get('cat')
        defaults = CATEGORY_MICRO.get(cat)
        if defaults:
            serving_str = str(item.get('s', '100g'))
            m = re.search(r'(\d+(?:\.\d+)?)\s*(?:g|ml)', serving_str.lower())
            serving_g = float(m.group(1)) if m else 100.0
            scale = serving_g / 100.0
            for mkey, val in defaults.items():
                if not item.get(mkey):
                    item[mkey] = round2(val * scale)
            stats['micro_fill'] += 1

print('\nFix summary:')
for k, v in stats.items():
    print(f'  {k}: {v}')

# verify no item has fat > serving_g (post-fix check)
def parse_g(s):
    m = re.search(r'[~]?(\d+(?:\.\d+)?)\s*g', str(s).lower())
    return float(m.group(1)) if m else 100.0

impossible = [(item['id'], item.get('en'), item.get('s'), item.get('f'))
              for item in data
              if (item.get('f') or 0) > parse_g(item.get('s','100g'))]
if impossible:
    print(f'\nWARNING: {len(impossible)} still have fat > serving:')
    for r in impossible[:10]: print(f'  {r}')
else:
    print('\nOK: no item has fat > serving weight after fixes.')

with open(OUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',',':'))
print(f'\nSaved {len(data)} items to {OUT_FILE}')
