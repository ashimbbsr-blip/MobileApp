"""
Script to:
1. Remove all beef items from food_master_v10.json
2. Add 22 new items (Mango Lassi, fritters, lettuce/salad items)
3. Renumber IDs sequentially from 1
"""
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

DATASET_PATH = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v10.json'

with open(DATASET_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} items")

# ── 1. Remove beef items ──────────────────────────────────────────────────────
# Criteria: en contains "beef" (case-insensitive) OR bn contains "গরু" OR
#           cat == "beef" OR family == "beef"
removed = []
kept = []
for item in data:
    en  = item.get('en', '')
    bn  = item.get('bn', '')
    cat = item.get('cat', '')
    fam = item.get('family', '')
    if (
        'beef' in en.lower()
        or 'গরু' in bn
        or cat == 'beef'
        or fam == 'beef'
    ):
        removed.append(item)
    else:
        kept.append(item)

print(f"\nBeef items removed: {len(removed)}")
cat_counts = {}
for item in removed:
    c = item.get('cat', 'unknown')
    cat_counts[c] = cat_counts.get(c, 0) + 1
print(f"Categories of removed items: {cat_counts}")
for item in removed:
    print(f"  [{item.get('cat')}] {item.get('en')} | {item.get('bn')}")

# ── 2. New items to add ───────────────────────────────────────────────────────
new_items = [
    # Mango Lassi – beverage
    {
        "en": "Mango Lassi",
        "bn": "আমের লস্যি",
        "s": "1 glass (~250ml)",
        "k": 220, "p": 7, "c": 36, "f": 5,
        "fi": 1.2, "sf": 3, "su": 31, "so": 0.2,
        "cat": "beverage",
        "family": "lassi",
        "kw": ["mango", "lassi", "drink", "beverage", "আমের", "লস্যি"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 60,
        "popularity_score": 70,
        "search_priority": 65,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Sesame Seed Fritters – snack
    {
        "en": "Sesame Seed Fritters",
        "bn": "তিলের বড়া",
        "s": "100g",
        "k": 315, "p": 9.2, "c": 21.5, "f": 22.3,
        "fi": 6.8, "sf": 3.4, "su": 2.8, "so": 0.9,
        "cat": "snack",
        "family": "fritter",
        "kw": ["sesame", "fritter", "bora", "তিল", "বড়া"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 50,
        "search_priority": 52,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Khoshla Leaf Fritters – snack
    {
        "en": "Khoshla Leaf Fritters",
        "bn": "খোশলা পাতার বড়া",
        "s": "100g",
        "k": 180, "p": 5.3, "c": 16.2, "f": 10.8,
        "fi": 4.5, "sf": 1.8, "su": 2.0, "so": 0.8,
        "cat": "snack",
        "family": "fritter",
        "kw": ["khoshla", "leaf", "fritter", "bora", "খোশলা", "পাতা", "বড়া"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 50,
        "popularity_score": 40,
        "search_priority": 45,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Gandal Leaf Fritters – snack
    {
        "en": "Gandal Leaf Fritters",
        "bn": "গাঁদাল পাতার বড়া",
        "s": "100g",
        "k": 178, "p": 5.5, "c": 15.8, "f": 10.6,
        "fi": 4.8, "sf": 1.8, "su": 1.9, "so": 0.8,
        "cat": "snack",
        "family": "fritter",
        "kw": ["gandal", "leaf", "fritter", "bora", "গাঁদাল", "পাতা", "বড়া"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 50,
        "popularity_score": 40,
        "search_priority": 45,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Bottle Gourd Leaf Fritters – snack
    {
        "en": "Bottle Gourd Leaf Fritters",
        "bn": "লাউ পাতার বড়া",
        "s": "100g",
        "k": 175, "p": 5.4, "c": 15.2, "f": 10.5,
        "fi": 4.6, "sf": 1.8, "su": 2.0, "so": 0.8,
        "cat": "snack",
        "family": "fritter",
        "kw": ["bottle gourd", "leaf", "fritter", "bora", "লাউ", "পাতা", "বড়া"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 50,
        "popularity_score": 45,
        "search_priority": 47,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Mashed Elephant Foot Yam – vegetable
    {
        "en": "Mashed Elephant Foot Yam",
        "bn": "ওল ভাতে",
        "s": "100g",
        "k": 118, "p": 2.2, "c": 26.5, "f": 1.2,
        "fi": 4.4, "sf": 0.3, "su": 1.2, "so": 0.4,
        "cat": "vegetable",
        "family": "yam",
        "kw": ["yam", "elephant foot", "mashed", "ওল", "ভাতে"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 50,
        "search_priority": 52,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Polta Leaf Fritters – snack
    {
        "en": "Polta Leaf Fritters",
        "bn": "পলতা পাতার বড়া",
        "s": "100g",
        "k": 182, "p": 5.7, "c": 16.0, "f": 10.9,
        "fi": 4.7, "sf": 1.8, "su": 2.1, "so": 0.8,
        "cat": "snack",
        "family": "fritter",
        "kw": ["polta", "leaf", "fritter", "bora", "পলতা", "পাতা", "বড়া"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 50,
        "popularity_score": 40,
        "search_priority": 45,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Iceberg Lettuce – salad
    {
        "en": "Iceberg Lettuce",
        "bn": "আইসবার্গ লেটুস",
        "s": "100g",
        "k": 14, "p": 0.9, "c": 3.0, "f": 0.1,
        "fi": 1.2, "sf": 0.0, "su": 2.0, "so": 0.01,
        "cat": "salad",
        "family": "lettuce",
        "kw": ["iceberg", "lettuce", "salad", "লেটুস"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 60,
        "popularity_score": 55,
        "search_priority": 57,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Romaine Lettuce – salad
    {
        "en": "Romaine Lettuce",
        "bn": "রোমেইন লেটুস",
        "s": "100g",
        "k": 17, "p": 1.2, "c": 3.3, "f": 0.3,
        "fi": 2.1, "sf": 0.0, "su": 1.2, "so": 0.02,
        "cat": "salad",
        "family": "lettuce",
        "kw": ["romaine", "lettuce", "salad", "লেটুস"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 60,
        "popularity_score": 55,
        "search_priority": 57,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Butterhead Lettuce – salad
    {
        "en": "Butterhead Lettuce",
        "bn": "বাটারহেড লেটুস",
        "s": "100g",
        "k": 13, "p": 1.4, "c": 2.2, "f": 0.2,
        "fi": 1.5, "sf": 0.0, "su": 1.2, "so": 0.02,
        "cat": "salad",
        "family": "lettuce",
        "kw": ["butterhead", "lettuce", "salad", "লেটুস"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 60,
        "popularity_score": 50,
        "search_priority": 55,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Lollo Rosso – salad
    {
        "en": "Lollo Rosso",
        "bn": "লোলো রোসো",
        "s": "100g",
        "k": 16, "p": 1.3, "c": 2.8, "f": 0.2,
        "fi": 2.0, "sf": 0.0, "su": 1.5, "so": 0.02,
        "cat": "salad",
        "family": "lettuce",
        "kw": ["lollo rosso", "lettuce", "salad", "লোলো", "রোসো"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 40,
        "search_priority": 47,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Lollo Bionda – salad
    {
        "en": "Lollo Bionda",
        "bn": "লোলো বিয়ন্ডা",
        "s": "100g",
        "k": 16, "p": 1.3, "c": 2.8, "f": 0.2,
        "fi": 2.0, "sf": 0.0, "su": 1.4, "so": 0.02,
        "cat": "salad",
        "family": "lettuce",
        "kw": ["lollo bionda", "lettuce", "salad", "লোলো", "বিয়ন্ডা"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 38,
        "search_priority": 46,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Oak Leaf Lettuce – salad
    {
        "en": "Oak Leaf Lettuce",
        "bn": "ওক লিফ লেটুস",
        "s": "100g",
        "k": 17, "p": 1.5, "c": 3.1, "f": 0.2,
        "fi": 2.2, "sf": 0.0, "su": 1.6, "so": 0.02,
        "cat": "salad",
        "family": "lettuce",
        "kw": ["oak leaf", "lettuce", "salad", "লেটুস"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 40,
        "search_priority": 47,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Lamb's Lettuce – salad
    {
        "en": "Lamb's Lettuce",
        "bn": "ফেল্ডসালাত",
        "s": "100g",
        "k": 21, "p": 2.0, "c": 3.6, "f": 0.4,
        "fi": 2.5, "sf": 0.1, "su": 0.7, "so": 0.03,
        "cat": "salad",
        "family": "lettuce",
        "kw": ["lamb's lettuce", "mache", "salad", "লেটুস"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 38,
        "search_priority": 46,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Arugula – salad
    {
        "en": "Arugula",
        "bn": "রুকোলা",
        "s": "100g",
        "k": 25, "p": 2.6, "c": 3.7, "f": 0.7,
        "fi": 1.6, "sf": 0.1, "su": 2.1, "so": 0.05,
        "cat": "salad",
        "family": "salad_leaf",
        "kw": ["arugula", "rocket", "salad", "রুকোলা"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 60,
        "popularity_score": 52,
        "search_priority": 56,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Baby Spinach – salad
    {
        "en": "Baby Spinach",
        "bn": "বেবি পালং শাক",
        "s": "100g",
        "k": 23, "p": 2.9, "c": 3.6, "f": 0.4,
        "fi": 2.2, "sf": 0.1, "su": 0.4, "so": 0.04,
        "cat": "salad",
        "family": "salad_leaf",
        "kw": ["baby spinach", "spinach", "salad", "পালং", "শাক"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 65,
        "popularity_score": 60,
        "search_priority": 62,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Mixed Leaf Salad – salad
    {
        "en": "Mixed Leaf Salad",
        "bn": "মিক্সড লিফ সালাদ",
        "s": "100g",
        "k": 18, "p": 1.5, "c": 3.0, "f": 0.3,
        "fi": 2.0, "sf": 0.1, "su": 1.3, "so": 0.03,
        "cat": "salad",
        "family": "salad_leaf",
        "kw": ["mixed leaf", "salad", "সালাদ"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 60,
        "popularity_score": 55,
        "search_priority": 57,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Baby Leaf Mix – salad
    {
        "en": "Baby Leaf Mix",
        "bn": "বেবি লিফ মিক্স",
        "s": "100g",
        "k": 20, "p": 1.8, "c": 3.2, "f": 0.3,
        "fi": 2.3, "sf": 0.1, "su": 1.2, "so": 0.03,
        "cat": "salad",
        "family": "salad_leaf",
        "kw": ["baby leaf", "mix", "salad", "সালাদ"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 60,
        "popularity_score": 52,
        "search_priority": 56,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Radicchio – salad
    {
        "en": "Radicchio",
        "bn": "রাডিকিও",
        "s": "100g",
        "k": 23, "p": 1.4, "c": 4.5, "f": 0.3,
        "fi": 2.0, "sf": 0.1, "su": 0.6, "so": 0.02,
        "cat": "salad",
        "family": "salad_leaf",
        "kw": ["radicchio", "chicory", "salad", "রাডিকিও"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 38,
        "search_priority": 46,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Endive – salad
    {
        "en": "Endive",
        "bn": "এন্ডিভ",
        "s": "100g",
        "k": 17, "p": 1.3, "c": 3.4, "f": 0.2,
        "fi": 3.1, "sf": 0.0, "su": 0.3, "so": 0.02,
        "cat": "salad",
        "family": "salad_leaf",
        "kw": ["endive", "chicory", "salad", "এন্ডিভ"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 38,
        "search_priority": 46,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Frisee Lettuce – salad
    {
        "en": "Frisee Lettuce",
        "bn": "ফ্রিজে সালাদ",
        "s": "100g",
        "k": 19, "p": 1.2, "c": 4.0, "f": 0.2,
        "fi": 3.1, "sf": 0.0, "su": 0.7, "so": 0.02,
        "cat": "salad",
        "family": "lettuce",
        "kw": ["frisee", "lettuce", "salad", "সালাদ"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 55,
        "popularity_score": 38,
        "search_priority": 46,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
    # Rocket & Baby Spinach Mix – salad
    {
        "en": "Rocket & Baby Spinach Mix",
        "bn": "রুকোলা ও বেবি পালং মিক্স",
        "s": "100g",
        "k": 24, "p": 2.5, "c": 3.5, "f": 0.5,
        "fi": 2.1, "sf": 0.1, "su": 1.2, "so": 0.04,
        "cat": "salad",
        "family": "salad_leaf",
        "kw": ["rocket", "baby spinach", "mix", "salad", "রুকোলা", "পালং"],
        "src": "manual",
        "nutrition_source": "manual",
        "nutrition_confidence": "medium",
        "quality_score": 60,
        "popularity_score": 50,
        "search_priority": 55,
        "aliases": [],
        "canonical": True,
        "ca": 0, "fe": 0, "zn": 0, "va": 0, "vc": 0, "vd": 0, "mg": 0, "pot": 0,
    },
]

print(f"\nNew items to add: {len(new_items)}")

# ── 3. Combine and renumber ──────────────────────────────────────────────────
final = kept + new_items

for idx, item in enumerate(final, start=1):
    item['id'] = idx

print(f"\nFinal dataset size: {len(final)}")
print(f"  Original: {len(data)}")
print(f"  Removed (beef): {len(removed)}")
print(f"  Added (new): {len(new_items)}")
print(f"  Expected: {len(data) - len(removed) + len(new_items)}")

# ── 4. Save ──────────────────────────────────────────────────────────────────
with open(DATASET_PATH, 'w', encoding='utf-8') as f:
    json.dump(final, f, ensure_ascii=False, separators=(',', ':'))

print(f"\nSaved to {DATASET_PATH}")
print("Done.")
