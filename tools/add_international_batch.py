"""
add_international_batch.py
Add ~177 international restaurant/cafe foods to food_master_v8_2.json.
Sources: user-curated estimates (Thai, Japanese/Sushi, Falooda, Cakes,
         Milkshakes, Chocolates, Burger King, Bakery/Pastry, Turkish/Doner).
"""
import json, sys, re
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8')

DATASET = Path('assets/data/food_master_v8_2.json')
PARSED  = Path('tools/_batch_parsed.json')

# ── Category mapping ──────────────────────────────────────────────────────────
CAT_MAP = {
    'dessert': 'sweet',
    'cake':    'sweet',
}
# Items that have no cat field: assign by name-keyword heuristics
KEYWORD_CAT = [
    (['whopper','crispy burger','bk veggie','paneer king','paneer royale',
      'chicken nuggets','french fries','veg wrap','chicken wrap'],         'fast_food'),
    (['chocolate shake (medium)'],                                          'beverage'),
    (['croissant','danish pastry','muffin','donut','turnover','cheese danish',
      'strudel','cream puff','profiterole','eclair','baklava'],             'bakery'),
    (['doner','shish kebab','kebab plate','lahmacun','durum','adana kebab',
      'falafel wrap','turkish fries','doner salad','iskender'],             'street_food'),
    (['milk chocolate','dark chocolate','white chocolate','ruby chocolate',
      'toblerone','milka','lindt','kinder','ferrero','raffaello'],          'chocolate'),
]

# ── Near-duplicates to skip (EN name lowercased) ──────────────────────────────
# These exist under slightly different names in earlier batches of this very
# user message — first-encounter wins via case-insensitive EN dedup.
EXTRA_SKIP = {
    # Batch-10 repeats exact names from batch-8 → caught by dedup automatically
    # Batch-9 / batch-10 near-names that differ by 1 word:
    'lindt lindor milk chocolate truffles',   # ≈ "Lindt Lindor Milk Chocolate Truffle"
    'lindt excellence 70% cocoa',             # ≈ "Lindt Excellence Dark Chocolate 70%"
    'milka alpenmilch chocolate',             # ≈ "Milka Alpine Milk Chocolate"
}

# ── Field mapping helpers ─────────────────────────────────────────────────────
FIELD_DROP = {'id', 'note', 'sf', 'su', 'so'}

def assign_cat(en: str) -> str:
    el = en.lower()
    for kws, cat in KEYWORD_CAT:
        if any(k in el for k in kws):
            return cat
    return 'other'

def make_keywords(item: dict) -> list:
    en = item.get('en', '')
    bn = item.get('bn', '')
    cat = item.get('cat', '')
    # tokenise EN into words ≥3 chars
    words = [w.lower() for w in re.findall(r"[A-Za-z0-9'&]+", en) if len(w) >= 3]
    kw = list(dict.fromkeys(words))  # dedup, preserve order
    # add category-specific tags
    if cat == 'thai':
        kw += ['thai food', 'thai cuisine', 'southeast asian']
    elif cat == 'japanese':
        kw += ['japanese food', 'sushi', 'japanese cuisine']
    elif cat == 'sweet' and 'falooda' in en.lower():
        kw += ['falooda', 'indian dessert', 'cold dessert', 'kulfi falooda']
    elif cat == 'sweet' and 'cake' in en.lower():
        kw += ['cake', 'bakery', 'dessert', 'celebration cake']
    elif cat == 'beverage' and 'milkshake' in en.lower():
        kw += ['milkshake', 'shake', 'cold drink', 'milk based']
    elif cat == 'chocolate':
        kw += ['chocolate', 'candy', 'confectionery', 'sweet']
    elif cat == 'fast_food':
        kw += ['fast food', 'burger king', 'bk', 'burger', 'quick service']
    elif cat == 'bakery':
        kw += ['bakery', 'pastry', 'baked goods']
    elif cat == 'street_food':
        kw += ['kebab', 'turkish food', 'doner', 'street food', 'middle eastern']
    return kw

def convert(item: dict) -> dict:
    out = {}
    for k, v in item.items():
        if k in FIELD_DROP:
            continue
        if k == 'kp':
            out['pot'] = v
        elif k == 'na':
            out['sod'] = v
        elif k == 'so':
            # 'so' is sodium in grams in some batches → convert to mg
            out['sod'] = round(v * 1000)
        elif k == 'vc':
            out['vit_c'] = v
        else:
            out[k] = v
    # Fix category
    cat = out.get('cat', '')
    if not cat:
        out['cat'] = assign_cat(out.get('en', ''))
    else:
        out['cat'] = CAT_MAP.get(cat, cat)
    # Ensure serving size default
    if 's' not in out:
        out['s'] = '100g'
    # Add source + quality
    if 'src' not in out:
        out['src'] = 'user_curated'
    if 'quality_score' not in out:
        out['quality_score'] = 72
    # Generate keywords
    out['kw'] = make_keywords(out)
    return out


def main():
    data = json.loads(DATASET.read_text(encoding='utf-8'))
    batch = json.loads(PARSED.read_text(encoding='utf-8'))

    before     = len(data)
    max_id     = max(item['id'] for item in data)
    next_id    = max_id + 1
    existing   = {item['en'].strip().lower() for item in data}

    added = skipped_dup = skipped_extra = 0

    for raw_item in batch:
        en_key = raw_item.get('en', '').strip().lower()

        # Skip near-duplicate names defined above
        if en_key in EXTRA_SKIP:
            print(f"  SKIP (near-dup): {raw_item['en']}")
            skipped_extra += 1
            continue

        # Skip if already in dataset
        if en_key in existing:
            print(f"  SKIP (dup): {raw_item['en']}")
            skipped_dup += 1
            continue

        item = convert(raw_item)
        item['id'] = next_id
        next_id += 1
        data.append(item)
        existing.add(en_key)
        print(f"  ADD id={item['id']:6d} [{item['cat']:12s}]: {item['en']}")
        added += 1

    print(f"\nBefore: {before}  Added: {added}  Skipped-dup: {skipped_dup}  "
          f"Skipped-near-dup: {skipped_extra}  After: {len(data)}")
    DATASET.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Saved → {DATASET}")


if __name__ == '__main__':
    main()
