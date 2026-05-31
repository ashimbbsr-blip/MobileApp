"""
Apply 34 manual Bengali corrections to food_master_v6_1.json,
then rebuild index_bn_v6_1.json (Bengali-only tokens).
IDs 1079/1094/1181/1183/1194 (mixed Latin variety codes) are intentionally left unchanged.
"""

import json, os, sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA     = os.path.join(ROOT, "assets", "data")
V61      = os.path.join(DATA, "food_master_v6_1.json")
IDX61    = os.path.join(DATA, "index_bn_v6_1.json")

# ── Manual corrections (id → corrected Bengali name) ──────────────────────────
MANUAL_FIXES = {
    56:  'মাখন আইসিং',                     # Butter icing         (িকিনগ→আইসিং)
    61:  'চিজ ওপেন স্যান্ডউইচ',            # Cheese open sandwich  (োপেন→ওপেন)
    81:  'ক্রিম অফ টমেটো স্যুপ',           # Cream of tomato soup  (োফ→অফ)
    120: 'পনির স্টাফড চেলা/চিলা',          # Paneer stuffed cheela/chilla
    150: 'মা ছানে কি ডাল',                 # Maa chaane ki dal     (মআ→মা, চাানে→ছানে)
    161: 'ভাত মুগ ডাল চেলা',               # Rice moong dal cheela (চেে লা→চেলা)
    212: 'মাছ ইন নারকেল দুধ',              # Fish in coconut milk  (িন→ইন)
    213: 'মাছ ওরলি',                       # Fish orly             (োরলয→ওরলি)
    280: 'কমলা অমলেট/অমলেট',              # Orange omelette/omlet
    363: 'ক্লাসিক ইতালিয়ান পাস্তা',        # Classic italian pasta
    397: 'বেসান বাথুা চিলা/চেলা',          # Besan bathua chilla/cheela
    436: 'ভুট্টা অমলেট/অমলেট',            # Corn omelette/omlet
    448: 'ড্রাই আরবি',                    # Dry arbi              (দরয ারবি→ড্রাই আরবি)
    451: 'ফার্মেন্টেড বাঁশ শুট আচার',     # Fermented bamboo shoot pickle
    456: 'ফরেনচ অমলেট/অমলেট',             # French omelette/omlet
    457: 'ফ্রিকাসি অফ মুশরুম',             # Fricassee of Mushroom (োফ→অফ, doubled স)
    468: 'গ্লেসে আইসিং',                  # Glace icing           (িকিনগ→আইসিং)
    479: 'গাম আইসিং',                     # Gum icing             (গুম→গাম, িকিনগ→আইসিং)
    520: 'মশলা আরবি',                     # Masala arbi           (ারবি→আরবি)
    558: 'সাদা অমলেট/অমলেট',              # Plain omelette/omlet
    562: 'পোশতিক চিলা/চেলা',              # Poshtik chilla/cheela
    565: 'পাফি অমলেট/অমলেট',              # Puffy omelette/omlet
    573: 'রয়্যাল আইসিং',                  # Royal icing           (িকিনগ→আইসিং)
    590: 'শিশু আহার',                     # Shishu ahar           (াহার→আহার)
    599: 'স্প্যানিশ অমলেট/অমলেট',         # Spanish omelette/omlet
    612: 'টমেটো অ্যাসপিক',               # Tomato aspic          (াসপিক→অ্যাসপিক)
    635: 'হোল উরদ',                       # Whole urad            (ওহোলে ুরাদ→হোল উরদ)
    648: 'ডিম ইন পেপার',                  # Egg in a pepper
    662: 'স্টাফড ডিম অমলেট/অমলেট',       # Stuffed egg omelette/omlet
    915: 'আনারস আপসাইড ডাউন পুডিং',      # Pineapple upside down pudding
    916: 'কুইন অফ পুডিং',                # Queen of pudding
    936: 'মিষ্টি ওপেন স্যান্ডউইচ',        # Sweet open sandwich   (োপেন→ওপেন)
    998: 'ডাচেস আলু',                    # Ducheese potato (duchess)
    999: 'দম আলু',                        # Dum aloo              (দুম ালু→দম আলু)
    # IDs 1079/1094/1181/1183/1194: mixed Latin variety codes (BR-28/SP4/SP8/Diamond)
    # These are correct — variety codes legitimately use Latin script.
}

# ── Load ───────────────────────────────────────────────────────────────────────
with open(V61, encoding="utf-8") as fh:
    items = json.load(fh)
print(f"Loaded {len(items)} items from food_master_v6_1.json")

id_map = {item["id"]: item for item in items}

# ── Apply fixes ────────────────────────────────────────────────────────────────
applied, not_found = [], []
for iid, new_bn in MANUAL_FIXES.items():
    if iid not in id_map:
        not_found.append(iid)
        continue
    old_bn = id_map[iid].get("bn", "")
    id_map[iid]["bn"] = new_bn
    applied.append((iid, id_map[iid]["en"], old_bn, new_bn))

print(f"Applied {len(applied)} manual fixes  |  not found: {not_found}")
for iid, en, old, new in applied:
    print(f"  id={iid:<4d}  {en[:35]:<35}  {old!r}")
    print(f"        {'':35}  → {new!r}")

# ── Save food_master_v6_1.json ─────────────────────────────────────────────────
v61_list = [id_map[item["id"]] for item in items]
with open(V61, "w", encoding="utf-8") as fh:
    json.dump(v61_list, fh, ensure_ascii=False, indent=2)
print(f"\nSaved {V61}")

# ── Rebuild index_bn_v6_1.json (Bengali block only) ───────────────────────────
BENGALI_START, BENGALI_END = 0x0980, 0x09FF

def is_bengali_prefix(token: str) -> bool:
    return len(token) >= 1 and BENGALI_START <= ord(token[0]) <= BENGALI_END

idx_bn = defaultdict(list)
for item in v61_list:
    bn = item.get("bn", "")
    iid = item["id"]
    if not bn:
        continue
    seen = set()
    for word in bn.split():
        if len(word) >= 2:
            prefix = word[:2]
            if is_bengali_prefix(prefix) and prefix not in seen and iid not in idx_bn[prefix]:
                idx_bn[prefix].append(iid)
                seen.add(prefix)

idx_bn = dict(idx_bn)
with open(IDX61, "w", encoding="utf-8") as fh:
    json.dump(idx_bn, fh, ensure_ascii=False, indent=2)
print(f"Saved {IDX61}  ({len(idx_bn)} Bengali tokens)")

# ── Quick sanity: no non-Bengali tokens ───────────────────────────────────────
bad = [t for t in idx_bn if not is_bengali_prefix(t)]
print(f"Non-Bengali tokens in new index: {bad}" if bad else "All index tokens are Bengali-only.")
