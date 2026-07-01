"""Extract and parse all JSON arrays from the raw JSONL message."""
import sys, re, json
sys.stdout.reconfigure(encoding='utf-8')

raw = open('tools/_batch_raw.txt', encoding='utf-8-sig').read().strip()
# The raw file contains a JSONL-escaped string
unescaped = raw.replace('\\n', '\n').replace('\\"', '"').replace('\\\\', '\\')

print(f"Unescaped length: {len(unescaped)}")

# Find all top-level JSON arrays
all_items = []
pos = 0
batch_num = 0

while pos < len(unescaped):
    arr_start = unescaped.find('[', pos)
    if arr_start == -1:
        break

    # Find matching ]
    depth = 0
    arr_end = -1
    for i in range(arr_start, len(unescaped)):
        if unescaped[i] == '[':
            depth += 1
        elif unescaped[i] == ']':
            depth -= 1
            if depth == 0:
                arr_end = i
                break

    if arr_end == -1:
        print(f"No matching ] found starting from {arr_start}")
        break

    arr_text = unescaped[arr_start:arr_end+1]

    try:
        items = json.loads(arr_text)
        if items and isinstance(items, list) and isinstance(items[0], dict) and 'en' in items[0]:
            batch_num += 1
            print(f"\nBatch {batch_num}: {len(items)} items ({items[0]['en']} ... {items[-1]['en']})")
            all_items.extend(items)
        else:
            print(f"  Skipping non-food array at pos {arr_start} (first el: {items[0] if items else 'empty'})")
    except Exception as e:
        print(f"  Parse error at [{arr_start},{arr_end}]: {e}")

    pos = arr_end + 1

print(f"\n{'='*50}")
print(f"Total items found: {len(all_items)}")

# Save as clean JSON
with open('tools/_batch_parsed.json', 'w', encoding='utf-8') as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)
print(f"Saved to tools/_batch_parsed.json")

# Show category breakdown
from collections import Counter
cats = Counter(item.get('cat', 'MISSING') for item in all_items)
print(f"\nCategories:")
for cat, count in cats.most_common():
    print(f"  {cat}: {count}")

print(f"\nAll {len(all_items)} items:")
for i, item in enumerate(all_items, 1):
    print(f"  {i:3d}. {item['en']} | cat={item.get('cat','?')}")
