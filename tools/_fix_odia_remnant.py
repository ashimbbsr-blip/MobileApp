"""Fix any remaining Odia script characters in bn fields."""
import json, sys
sys.stdout.reconfigure(encoding='utf-8')

ODIA_TO_BN = {
    'ଅ': 'অ', 'ଆ': 'আ', 'ଇ': 'ই', 'ଈ': 'ঈ', 'ଉ': 'উ', 'ଊ': 'ঊ',
    'ଋ': 'ঋ', 'ଏ': 'এ', 'ଐ': 'ঐ', 'ଓ': 'ও', 'ଔ': 'ঔ',
    'କ': 'ক', 'ଖ': 'খ', 'ଗ': 'গ', 'ଘ': 'ঘ', 'ଙ': 'ঙ',
    'ଚ': 'চ', 'ଛ': 'ছ', 'ଜ': 'জ', 'ଝ': 'ঝ', 'ଞ': 'ঞ',
    'ଟ': 'ট', 'ଠ': 'ঠ', 'ଡ': 'ড', 'ଢ': 'ঢ', 'ଣ': 'ণ',
    'ତ': 'ত', 'ଥ': 'থ', 'ଦ': 'দ', 'ଧ': 'ধ', 'ନ': 'ন',
    'ପ': 'প', 'ଫ': 'ফ', 'ବ': 'ব', 'ଭ': 'ভ', 'ମ': 'ম',
    'ଯ': 'য', 'ର': 'র', 'ଲ': 'ল', 'ଳ': 'ল',
    'ଶ': 'শ', 'ଷ': 'ষ', 'ସ': 'স', 'ହ': 'হ',
    'ା': 'া', 'ି': 'ি', 'ୀ': 'ী', 'ୁ': 'ু', 'ୂ': 'ূ',
    'ୃ': 'ৃ', 'େ': 'ে', 'ୈ': 'ৈ', 'ୋ': 'ো', 'ୌ': 'ৌ',
    '୍': '্', 'ଁ': 'ঁ', 'ଂ': 'ং', 'ଃ': 'ঃ', '଼': '়',
}

def purge_odia(text):
    result = []
    for c in text:
        if 0x0B00 <= ord(c) <= 0x0B7F:
            mapped = ODIA_TO_BN.get(c, '')
            result.append(mapped)
        else:
            result.append(c)
    return ''.join(result)

data = json.load(open('assets/data/food_master_v9_0.json', encoding='utf-8'))
fixed = 0
for item in data:
    bn = item.get('bn', '')
    if any(0x0B00 <= ord(c) <= 0x0B7F for c in str(bn)):
        item['bn'] = purge_odia(bn)
        fixed += 1

print(f'Fixed {fixed} items')
json.dump(data, open('assets/data/food_master_v9_0.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('Saved')
# Verify
remaining = [d for d in data if any(0x0B00 <= ord(c) <= 0x0B7F for c in str(d.get('bn', '')))]
print(f'Remaining Odia in bn: {len(remaining)}')
