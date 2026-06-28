"""Rebuild search_index_v2.json from food_master_v8_1.json."""
import json, re, collections, sys
sys.stdout.reconfigure(encoding='utf-8')

INPUT = 'assets/data/food_master_v8_1.json'
OUTPUT = 'assets/data/search_index_v2.json'

data = json.load(open(INPUT, encoding='utf-8'))
print(f'Loaded {len(data)} items')

STOPWORDS = {'and','the','with','of','in','a','an','or','for','to','at','by'}

def en_tokens(text):
    return [t for t in re.findall(r'[a-z0-9]+', (text or '').lower())
            if len(t) >= 2 and t not in STOPWORDS]

def bn_tokens(text):
    return [t for t in re.findall(r'[ঀ-৿]+', text or '') if len(t) >= 2]

def add_pfx(bucket, token, fid, pri):
    for l in range(2, len(token) + 1):
        bucket[token[:l]].append((pri, fid))

en_pfx = collections.defaultdict(list)
bn_pfx = collections.defaultdict(list)
al_idx = collections.defaultdict(list)
fm_idx = collections.defaultdict(list)

for item in data:
    fid = item['id']
    pri = item.get('search_priority', 50)
    fam = item.get('family', 'other')
    toks = set()
    for src in [item.get('en', ''), *item.get('kw', []), *item.get('aliases', [])]:
        toks.update(en_tokens(src))
    for tok in toks:
        add_pfx(en_pfx, tok, fid, pri)
    for tok in bn_tokens(item.get('bn', '')):
        add_pfx(bn_pfx, tok, fid, pri)
    for al in item.get('aliases', []):
        for tok in en_tokens(al):
            al_idx[tok].append((pri, fid))
    fm_idx[fam].append((pri, fid))

def sort_bkt(lst, cap=200):
    seen, out = set(), []
    for pri, fid in sorted(lst, key=lambda x: -x[0]):
        if fid not in seen:
            seen.add(fid); out.append(fid)
            if len(out) >= cap:
                break
    return out

top100 = [d['id'] for d in sorted(data, key=lambda x: -x.get('search_priority', 0))[:100]]

idx_v2 = {
    'version': 2, 'created': '2026-06-28', 'total_foods': len(data),
    'en_prefix':   {k: sort_bkt(v)      for k, v in en_pfx.items()},
    'bn_prefix':   {k: sort_bkt(v)      for k, v in bn_pfx.items()},
    'alias_lookup': {k: sort_bkt(v, 50) for k, v in al_idx.items()},
    'family_index': {k: sort_bkt(v)     for k, v in fm_idx.items()},
    'top_foods':   top100,
}

with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(idx_v2, f, ensure_ascii=False, separators=(',', ':'))

en_count = sum(len(v) for v in idx_v2['en_prefix'].values())
bn_count = sum(len(v) for v in idx_v2['bn_prefix'].values())
print(f'EN prefix tokens : {len(idx_v2["en_prefix"])}')
print(f'BN prefix tokens : {len(idx_v2["bn_prefix"])}')
print(f'EN index entries : {en_count}')
print(f'BN index entries : {bn_count}')
print(f'Families         : {len(idx_v2["family_index"])}')
print(f'Saved → {OUTPUT}')
