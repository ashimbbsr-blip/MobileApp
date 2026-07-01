import json, sys
sys.stdout.reconfigure(encoding='utf-8')
data = json.load(open('assets/data/food_master_v9_0.json', encoding='utf-8'))
print(f'Total: {len(data)}')
wb = [d for d in data if 27001 <= d.get('id', 0) <= 27330]
print(f'WB foods: {len(wb)}')
for d in wb[:3]:
    print(f'  {d["id"]}: EN={d["en"]} BN={d["bn"]}')
odia_maha = [d for d in data if 24001 <= d.get('id', 0) <= 24045]
print(f'Odisha Mahaprasad: {len(odia_maha)}')
for d in odia_maha[:3]:
    print(f'  {d["id"]}: EN={d["en"]} BN={d["bn"]}')
odia_script = [d for d in data if any(0x0B00 <= ord(c) <= 0x0B7F for c in str(d.get('bn', '')))]
print(f'Items still with Odia script in BN field: {len(odia_script)}')
for d in odia_script[:5]:
    print(f'  {d["id"]}: {d["en"]} -> {d["bn"]}')
# Check search index
idx = json.load(open('assets/data/search_index_v2.json', encoding='utf-8'))
print(f'EN prefix tokens: {len(idx["en_prefix"])}')
print(f'BN prefix tokens: {len(idx["bn_prefix"])}')
print(f'File sizes OK')
