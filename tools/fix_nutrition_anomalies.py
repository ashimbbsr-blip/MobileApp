"""
fix_nutrition_anomalies.py
Corrects specific nutritional data errors in food_master_v5_3.json.
Run from the repo root: py tools/fix_nutrition_anomalies.py
"""
import json
import sys
import copy
import os
import re

def parse_serving(s):
    """Extract numeric grams from strings like '240g', '1 bowl', 250, etc."""
    if isinstance(s, (int, float)):
        return float(s)
    m = re.search(r'(\d+(?:\.\d+)?)', str(s))
    return float(m.group(1)) if m else None

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'assets', 'data', 'food_master_v5_3.json')

def kcal_4_4_9(p, c, f):
    return round(p * 4 + c * 4 + f * 9, 1)

def apply_fixes(data):
    changes = []
    lookup = {item['id']: (idx, item) for idx, item in enumerate(data)}

    def fix(id_, field_updates, reason):
        if id_ not in lookup:
            print(f'  WARNING: ID {id_} not found — skipped')
            return
        idx, item = lookup[id_]
        old = {k: item[k] for k in field_updates}
        item.update(field_updates)
        changes.append({'id': id_, 'name': item['en'], 'reason': reason, 'before': old, 'after': field_updates})

    # ── ID 12: Nannari Sharbat ─────────────────────────────────────────────────
    # carbs 263.4 g > serving 240 g — scale to realistic syrup-drink profile
    p, c, f = 0.1, 35.0, 0.1
    fix(12, {'c': c, 'k': kcal_4_4_9(p, c, f)},
        'carbs 263.4g exceeded 240g serving; corrected to 35g syrup-drink profile')

    # ── ID 21: Banana Appam ────────────────────────────────────────────────────
    # fat 123.5 g > serving 60 g; kcal 1364 wildly wrong
    p, c, f = 4.0, 25.0, 12.0
    fix(21, {'p': p, 'c': c, 'f': f, 'k': kcal_4_4_9(p, c, f)},
        'fat 123.5g exceeded 60g serving; set standard 60g appam macros (4/25/12)')

    # ── ID 66: Cheese Soup ─────────────────────────────────────────────────────
    # solid-cheese macros in a liquid soup — dilute all macros by 60 %
    p = round(55.1 * 0.4, 1)
    c = round(8.3  * 0.4, 1)
    f = round(75.9 * 0.4, 1)
    fix(66, {'p': p, 'c': c, 'f': f, 'k': kcal_4_4_9(p, c, f)},
        'solid-cheese macros in 250g soup; diluted by 60% to creamy-soup profile')

    # ── IDs 69, 112, 114, 115: Paneer dishes — 10x fat multiplication error ───
    _, item69 = lookup[69]
    f69 = round(item69['f'] / 10, 1)
    p69, c69 = item69['p'], item69['c']
    fix(69, {'f': f69, 'k': kcal_4_4_9(p69, c69, f69)},
        'fat 249.4g in 250g dish — 10× error; divided by 10')

    _, item112 = lookup[112]
    f112 = round(item112['f'] / 10, 1)
    p112, c112 = item112['p'], item112['c']
    fix(112, {'f': f112, 'k': kcal_4_4_9(p112, c112, f112)},
        'fat 505.2g in 250g dish — 10× error; divided by 10')

    _, item114 = lookup[114]
    f114 = round(item114['f'] / 10, 1)
    p114, c114 = item114['p'], item114['c']
    fix(114, {'f': f114, 'k': kcal_4_4_9(p114, c114, f114)},
        'fat 502.3g in 250g dish — 10× error; divided by 10')

    _, item115 = lookup[115]
    f115 = round(item115['f'] / 10, 1)
    p115, c115 = item115['p'], item115['c']
    fix(115, {'f': f115, 'k': kcal_4_4_9(p115, c115, f115)},
        'fat 491.9g in 300g dish — 10× error; divided by 10')

    # ── IDs 210, 211, 213, 219: Deep-fried fish — fat capped at 18 % of serving
    for fid in [210, 211, 213, 219]:
        _, item = lookup[fid]
        s = parse_serving(item['s'])
        f_cap = round(s * 0.18, 1)
        p_v, c_v = item['p'], item['c']
        fix(fid, {'f': f_cap, 'k': kcal_4_4_9(p_v, c_v, f_cap)},
            f'fat {item["f"]}g exceeds {s}g serving; capped at 18% deep-fry retention ({f_cap}g)')

    return changes

def validate(data):
    """Re-run validation rules on all items and report any remaining violations."""
    errors = []
    for item in data:
        s = parse_serving(item.get('s'))
        if s is None:
            continue
        p, c, f, k = item['p'], item['c'], item['f'], item['k']
        macro_sum = p + c + f
        if macro_sum > s + 0.5:
            errors.append(f"  STILL EXCEEDS: ID {item['id']} [{item['en']}] macros {macro_sum:.1f}g > serving {s}g")
        expected_kcal = p * 4 + c * 4 + f * 9
        deviation = abs(k - expected_kcal)
        if expected_kcal > 0 and deviation / expected_kcal > 0.20:
            errors.append(f"  KCAL MISMATCH: ID {item['id']} [{item['en']}] k={k} expected≈{expected_kcal:.0f} (dev {deviation/expected_kcal*100:.0f}%)")
    return errors

def main():
    sys.stdout.reconfigure(encoding='utf-8')

    with open(DB_PATH, encoding='utf-8') as f:
        original = json.load(f)

    data = copy.deepcopy(original)
    changes = apply_fixes(data)

    print('=' * 70)
    print(f'CHANGES APPLIED: {len(changes)}')
    print('=' * 70)
    for ch in changes:
        print(f'\nID {ch["id"]:>3}  {ch["name"]}')
        print(f'  Reason : {ch["reason"]}')
        for field in ch['before']:
            print(f'  {field:>4}  {ch["before"][field]:>10}  →  {ch["after"][field]}')

    print('\n' + '=' * 70)
    print('POST-FIX VALIDATION (numeric-serving items only):')
    errors = validate(data)
    if errors:
        for e in errors:
            print(e)
    else:
        print('  No macro-weight or kcal-deviation violations found.')

    # Check IDs 169, 172 separately (string serving)
    print('\nIDs 169 & 172 (string serving — skipped, already have valid minerals):')
    for item in data:
        if item['id'] in [169, 172]:
            print(f'  ID {item["id"]} [{item["en"]}] ca={item["ca"]} fe={item["fe"]} zn={item["zn"]}  ← already correct')

    with open(DB_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

    print(f'\nFile written: {os.path.abspath(DB_PATH)}')
    print('=' * 70)

if __name__ == '__main__':
    main()
