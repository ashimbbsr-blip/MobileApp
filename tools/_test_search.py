import json, sys, re
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('assets/data/food_master.json', encoding='utf-8'))

def score(food, q):
    en = food.get('en','').lower()
    bn = (food.get('bn','') or '').lower()
    kw = ' '.join(food.get('kw',[]))
    if en == q or bn == q: return 100
    if en.startswith(q) or bn.startswith(q): return 80
    if len(q) == 1:
        for w in re.split(r'[\s/\-]+', en):
            if w.startswith(q): return 70
        return 0
    if q in en or q in bn: return 60
    if q in kw: return 40
    return 0

for query in ['rice', 'chicken', 'dal', 'fish', 'bi', 'ch']:
    results = [(score(f, query), f['en'], f.get('bn','')) for f in data if score(f, query) > 0]
    results.sort(reverse=True)
    print(f'Query "{query}": {len(results)} results')
    for s,en,bn in results[:5]:
        print(f'  [{s}] {en} / {bn}')
    print()
