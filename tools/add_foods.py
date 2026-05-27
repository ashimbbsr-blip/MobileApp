"""
Add and patch foods in the dataset.
- Patches 9 existing items (adds Bengali name + micronutrients, corrects wrong macros)
- Adds 6 new unique items with IDs 1430-1435
- Updates both search indexes
Run from project root: py tools/add_foods.py
"""
import json, shutil, re
from datetime import datetime

MASTER   = "assets/data/food_master_v5_3.json"
IDX_EN   = "assets/data/index_en_v5_3.json"
IDX_BN   = "assets/data/index_bn_v5_3.json"

# ── User-provided data (normalised to dataset schema) ─────────────────────────
#  serv→s | fib→fi | na removed | cat remapped to UI categories

ALL_ITEMS = [
    {"id": 1430, "en": "Chicken biryani",       "bn": "চিকেন বিরিয়ানি",
     "cat": "rice",      "s": "1 bowl",
     "k": 392, "p": 17.5, "c": 41.2, "f": 16.8, "fi": 2.1,
     "ca": 38,  "fe": 2.4, "zn": 1.9,
     "kw": ["chicken","biryani","rice","indian","bengali","non veg","dinner"],
     "src": "local"},

    {"id": 1431, "en": "Luchi alur dom",         "bn": "লুচি আলুর দম",
     "cat": "breakfast",  "s": "1 plate",
     "k": 468, "p": 8.4,  "c": 52.0, "f": 24.5, "fi": 4.1,
     "ca": 44,  "fe": 2.3, "zn": 1.1,
     "kw": ["luchi","alur dom","bengali","breakfast","fried","potato"],
     "src": "local"},

    {"id": 1432, "en": "Chingri malaikari",      "bn": "চিংড়ি মালাইকারি",
     "cat": "fish",       "s": "1 bowl",
     "k": 312, "p": 21.4, "c": 8.2,  "f": 21.0, "fi": 1.2,
     "ca": 96,  "fe": 2.0, "zn": 1.8,
     "kw": ["prawn","chingri","bengali","seafood","coconut","malaikari"],
     "src": "local"},

    {"id": 1433, "en": "Mutton kosha",           "bn": "মাটন কষা",
     "cat": "meat",       "s": "1 bowl",
     "k": 418, "p": 24.6, "c": 7.4,  "f": 31.5, "fi": 1.5,
     "ca": 42,  "fe": 3.4, "zn": 4.2,
     "kw": ["mutton","kosha","bengali","meat","spicy"],
     "src": "local"},

    {"id": 1434, "en": "Pakhala bhata",          "bn": "ପଖାଳ ଭାତ",
     "cat": "rice",       "s": "1 bowl",
     "k": 142, "p": 3.8,  "c": 28.5, "f": 1.8,  "fi": 0.8,
     "ca": 36,  "fe": 0.7, "zn": 0.5,
     "kw": ["pakhala","odia","fermented rice","summer","light"],
     "src": "local"},

    {"id": 1435, "en": "Egg roll Kolkata style", "bn": "এগ রোল",
     "cat": "snack",      "s": "1 pc (150g)",
     "k": 346, "p": 13.4, "c": 32.8, "f": 18.2, "fi": 2.4,
     "ca": 72,  "fe": 2.5, "zn": 1.6,
     "kw": ["egg roll","kolkata","street food","wrap","snack"],
     "src": "local"},
]

# ── Patches for existing duplicates ─────────────────────────────────────────
#  Only fields that differ or were missing. 'id' is the key.
PATCHES = {
    948: {"bn": "আলু পোস্ত",  "cat": "vegetable", "s": "1 bowl",
          "k": 228, "p": 4.8,  "c": 18.5, "f": 15.6, "fi": 3.4,
          "ca": 112, "fe": 1.7, "zn": 1.3,
          "kw": ["aloo posto","potato","posto","bengali","veg","lunch"]},

    968: {"bn": "শুক্তো",     "cat": "vegetable", "s": "1 bowl",
          "k": 126, "p": 3.6,  "c": 14.8, "f": 5.9,  "fi": 5.2,
          "ca": 68,  "fe": 1.9, "zn": 0.8,
          "kw": ["shukto","bengali","vegetable","traditional","veg","bitter"]},

    169: {"bn": "মিষ্টি দই", "cat": "dessert", "s": "1 bowl",
          "k": 218, "p": 6.1,  "c": 28.4, "f": 8.6,  "fi": 0.0,
          "ca": 210, "fe": 0.2, "zn": 0.8,
          "kw": ["mishti doi","sweet yogurt","dessert","bengali","dairy"]},

    917: {"bn": "রসমালাই",   "cat": "dessert", "s": "2 pcs",
          "k": 246, "p": 7.2,  "c": 29.5, "f": 10.2, "fi": 0.0,
          "ca": 248, "fe": 0.4, "zn": 0.9,
          "kw": ["rasmalai","sweet","dessert","milk","bengali"]},

    171: {"bn": "পাটিসাপটা", "cat": "dessert", "s": "2 pcs",
          "k": 284, "p": 6.5,  "c": 38.2, "f": 11.0, "fi": 1.8,
          "ca": 96,  "fe": 1.2, "zn": 0.7,
          "kw": ["pithe","patishapta","dessert","bengali","sweet"]},

    172: {"bn": "পায়েশ",    "cat": "dessert", "s": "1 bowl",
          "k": 224, "p": 5.4,  "c": 31.7, "f": 8.2,  "fi": 0.6,
          "ca": 182, "fe": 0.5, "zn": 0.6,
          "kw": ["payesh","kheer","rice pudding","dessert","milk"]},

    441: {"bn": "ডালমা",     "cat": "dal",     "s": "1 bowl",
          "k": 188, "p": 8.9,  "c": 24.8, "f": 5.4,  "fi": 6.2,
          "ca": 72,  "fe": 2.1, "zn": 1.1,
          "kw": ["dalma","odia","dal","vegetable","healthy"]},

    415: {"bn": "ଛେନା ପୋଡ଼ା", "cat": "dessert", "s": "1 slice (80g)",
          "k": 265, "p": 9.4,  "c": 24.2, "f": 14.5, "fi": 0.0,
          "ca": 240, "fe": 0.5, "zn": 1.0,
          "kw": ["chhena poda","odia","dessert","cheese sweet","baked"]},

    790: {"bn": "ঘুগনি",     "cat": "snack",   "s": "1 bowl",
          "k": 212, "p": 9.2,  "c": 31.6, "f": 5.4,  "fi": 7.1,
          "ca": 54,  "fe": 2.8, "zn": 1.2,
          "kw": ["ghugni","street food","peas","bengali","snack"]},
}


# ── Index helpers ─────────────────────────────────────────────────────────────

def _is_bengali(text):
    return any(0x0980 <= ord(c) <= 0x09FF for c in text)


def _en_prefixes(text):
    """2-char and 3-char prefixes of every word in English text."""
    prefixes = set()
    for word in re.split(r'\s+', text.lower()):
        w = re.sub(r'[^a-z0-9]', '', word)
        if len(w) >= 2:
            prefixes.add(w[:2])
        if len(w) >= 3:
            prefixes.add(w[:3])
    return prefixes


def _bn_prefixes(text):
    """2-char prefix of every word in Bengali text."""
    prefixes = set()
    for word in text.split():
        if _is_bengali(word) and len(word) >= 2:
            prefixes.add(word[:2])
    return prefixes


def update_index(idx, prefixes, position):
    for pref in prefixes:
        bucket = idx.setdefault(pref, [])
        if position not in bucket:
            bucket.append(position)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    # Backup
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(MASTER, f"{MASTER}.bak.{ts}")
    print(f"Backup: {MASTER}.bak.{ts}")

    with open(MASTER, encoding="utf-8") as f:
        items = json.load(f)
    with open(IDX_EN, encoding="utf-8") as f:
        idx_en = json.load(f)
    with open(IDX_BN, encoding="utf-8") as f:
        idx_bn = json.load(f)

    by_id = {x["id"]: (i, x) for i, x in enumerate(items)}

    # ── 1. Patch duplicates ──────────────────────────────────────────────────
    patched = 0
    for did, patch in PATCHES.items():
        if did not in by_id:
            print(f"  WARN: id={did} not found, skipping patch")
            continue
        pos, item = by_id[did]
        item.update(patch)
        patched += 1
        # Index doesn't change for patched items (position unchanged)
        # but update Bengali index if it now has a bn name
        bn = item.get("bn", "")
        if bn and _is_bengali(bn):
            for pref in _bn_prefixes(bn):
                bucket = idx_bn.setdefault(pref, [])
                if pos not in bucket:
                    bucket.append(pos)

    print(f"Patched {patched} existing items.")

    # ── 2. Add new unique items ──────────────────────────────────────────────
    existing_en = {x["en"].strip().lower() for x in items}
    added = 0
    for item in ALL_ITEMS:
        if item["en"].strip().lower() in existing_en:
            print(f"  SKIP (already exists): {item['en']}")
            continue
        items.append(item)
        pos = len(items) - 1

        # English index: name + keywords
        en_text = item["en"] + " " + " ".join(item.get("kw", []))
        update_index(idx_en, _en_prefixes(en_text), pos)

        # Bengali index: bn name
        bn = item.get("bn", "")
        if bn and _is_bengali(bn):
            update_index(idx_bn, _bn_prefixes(bn), pos)

        added += 1
        print(f"  Added id={item['id']} '{item['en']}'")

    # ── 3. Write outputs ─────────────────────────────────────────────────────
    with open(MASTER, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, separators=(",", ":"))
    with open(IDX_EN, "w", encoding="utf-8") as f:
        json.dump(idx_en, f, ensure_ascii=False, separators=(",", ":"))
    with open(IDX_BN, "w", encoding="utf-8") as f:
        json.dump(idx_bn, f, ensure_ascii=False, separators=(",", ":"))

    print(f"\nDone. {len(items)} total items ({added} added, {patched} patched).")

    # ── 4. Quick validation ──────────────────────────────────────────────────
    print("\nMacro validation for touched items:")
    touched = [x for x in items if x.get("id") in set(PATCHES) | {i["id"] for i in ALL_ITEMS}]
    for item in touched:
        k = item.get("k", 0)
        macro = item.get("p", 0)*4 + item.get("c", 0)*4 + item.get("f", 0)*9
        ratio = macro / k if k else 0
        ok = 0.90 <= ratio <= 1.10
        print(f"  [{'OK' if ok else 'BAD'}] id={item['id']:4d} {item['en'][:35]:35s} ratio={ratio:.2f}")


if __name__ == "__main__":
    main()
