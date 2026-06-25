"""
add_batch_foods.py — Add batch food groups to food_master_v7_2.json

Groups added:
  1. New sweets (Manda 100038, Makha Sandesh 100039) — 8 dups skipped
  2. Papad snacks (IDs 13001–13005)
  3. Haldiram namkeen (IDs 13101–13110) — cat normalized to snack
  4. Packaged snacks (IDs 13201–13215) — cat normalized to snack
  5. Fruits/Berries (IDs 15001–15020) — cat normalized from berry→fruit

Pre-normalization of existing categories:
  namkeen → snack, packaged_snack → snack, berry → fruit

Usage:
  py tools/add_batch_foods.py
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATASET = Path(__file__).parent.parent / "assets" / "data" / "food_master_v7_2.json"

# ---------------------------------------------------------------------------
# Category pre-normalization map (applied to existing items in-place)
# ---------------------------------------------------------------------------
CAT_NORM = {
    "namkeen": "snack",
    "packaged_snack": "snack",
    "berry": "fruit",
}

# ---------------------------------------------------------------------------
# New food items to add
# ---------------------------------------------------------------------------

NEW_SWEETS = [
    # Only Manda and Makha Sandesh are new; the rest are skipped as dups.
    {
        "id": 100038,
        "en": "Manda",
        "bn": "মান্দা",
        "cat": "sweet",
        "s": "100g",
        "k": 278, "p": 3.8, "c": 55.0, "f": 4.2,
        "fi": 2.1, "ca": 18, "fe": 0.9,
        "kw": ["sweet", "manda", "bengali", "mithai"],
        "src": "local",
    },
    {
        "id": 100039,
        "en": "Makha Sandesh",
        "bn": "মাখা সন্দেশ",
        "cat": "sweet",
        "s": "100g",
        "k": 298, "p": 10.5, "c": 34.0, "f": 13.0,
        "fi": 0.0, "ca": 245, "fe": 0.4,
        "kw": ["sweet", "sandesh", "makha", "bengali", "chenna", "mithai"],
        "src": "local",
    },
]

# Dups — listed so the skip-logic can verify; no data needed.
SWEET_DUPS = [
    "Mihidana", "Sitabhog", "Rajbhog", "Langcha",
    "Khaja", "Chhanar Jilipi", "Kheer Kadam", "Pantua",
]

NEW_PAPADS = [
    {
        "id": 13001, "en": "Urad Papad", "bn": "উড়দ পাপড়",
        "cat": "snack", "s": "100g",
        "k": 370, "p": 22.0, "c": 58.0, "f": 3.5, "fi": 4.0, "ca": 55, "fe": 4.0,
        "kw": ["snack", "papad", "urad", "dal", "roasted", "crispy"],
        "src": "local",
    },
    {
        "id": 13002, "en": "Moong Papad", "bn": "মুগ পাপড়",
        "cat": "snack", "s": "100g",
        "k": 360, "p": 24.0, "c": 55.0, "f": 2.5, "fi": 5.0, "ca": 60, "fe": 3.8,
        "kw": ["snack", "papad", "moong", "dal", "roasted", "crispy"],
        "src": "local",
    },
    {
        "id": 13003, "en": "Masala Papad", "bn": "মসলা পাপড়",
        "cat": "snack", "s": "100g",
        "k": 190, "p": 8.0, "c": 22.0, "f": 7.0, "fi": 3.5, "ca": 45, "fe": 1.8,
        "kw": ["snack", "papad", "masala", "spiced", "starter"],
        "src": "local",
    },
    {
        "id": 13004, "en": "Roasted Papad", "bn": "রোস্টেড পাপড়",
        "cat": "snack", "s": "100g",
        "k": 340, "p": 21.0, "c": 54.0, "f": 2.0, "fi": 4.0, "ca": 55, "fe": 3.5,
        "kw": ["snack", "papad", "roasted", "low fat", "crispy"],
        "src": "local",
    },
    {
        "id": 13005, "en": "Fried Papad", "bn": "তেলে ভাজা পাপড়",
        "cat": "snack", "s": "100g",
        "k": 510, "p": 20.0, "c": 48.0, "f": 25.0, "fi": 4.0, "ca": 55, "fe": 3.5,
        "kw": ["snack", "papad", "fried", "deep fried", "crispy"],
        "src": "local",
    },
]

NEW_HALDIRAM = [
    {
        "id": 13101, "en": "Haldiram Aloo Bhujia", "bn": "হলদিরাম আলু ভুজিয়া",
        "cat": "snack", "s": "100g",
        "k": 579, "p": 7.2, "c": 42.4, "f": 42.3, "fi": 0.5, "ca": 50, "fe": 2.5,
        "kw": ["snack", "haldiram", "aloo", "bhujia", "sev", "namkeen", "potato"],
        "src": "haldiram",
    },
    {
        "id": 13102, "en": "Haldiram Bhujia Sev", "bn": "হলদিরাম ভুজিয়া সেভ",
        "cat": "snack", "s": "100g",
        "k": 560, "p": 12.0, "c": 46.0, "f": 38.0, "fi": 1.0, "ca": 55, "fe": 3.0,
        "kw": ["snack", "haldiram", "bhujia", "sev", "namkeen", "besan"],
        "src": "haldiram",
    },
    {
        "id": 13103, "en": "Haldiram Navratan Mixture", "bn": "হলদিরাম নবরত্ন মিশ্রণ",
        "cat": "snack", "s": "100g",
        "k": 545, "p": 11.0, "c": 45.0, "f": 36.0, "fi": 5.0, "ca": 65, "fe": 3.0,
        "kw": ["snack", "haldiram", "navratan", "mixture", "namkeen", "mix"],
        "src": "haldiram",
    },
    {
        "id": 13104, "en": "Haldiram All In One", "bn": "হলদিরাম অল ইন ওয়ান",
        "cat": "snack", "s": "100g",
        "k": 540, "p": 10.0, "c": 48.0, "f": 35.0, "fi": 4.5, "ca": 60, "fe": 2.8,
        "kw": ["snack", "haldiram", "all in one", "mixture", "namkeen"],
        "src": "haldiram",
    },
    {
        "id": 13105, "en": "Haldiram Kaju Mixture", "bn": "হলদিরাম কাজু মিশ্রণ",
        "cat": "snack", "s": "100g",
        "k": 575, "p": 12.0, "c": 38.0, "f": 42.0, "fi": 4.0, "ca": 70, "fe": 3.5,
        "kw": ["snack", "haldiram", "kaju", "cashew", "mixture", "namkeen"],
        "src": "haldiram",
    },
    {
        "id": 13106, "en": "Haldiram Tasty Nuts", "bn": "হলদিরাম টেস্টি নাটস",
        "cat": "snack", "s": "100g",
        "k": 590, "p": 18.0, "c": 28.0, "f": 46.0, "fi": 7.0, "ca": 85, "fe": 4.0,
        "kw": ["snack", "haldiram", "nuts", "mixed nuts", "tasty", "namkeen"],
        "src": "haldiram",
    },
    {
        "id": 13107, "en": "Haldiram Moong Dal", "bn": "হলদিরাম মুগ ডাল",
        "cat": "snack", "s": "100g",
        "k": 540, "p": 22.0, "c": 38.0, "f": 32.0, "fi": 6.0, "ca": 65, "fe": 3.5,
        "kw": ["snack", "haldiram", "moong", "dal", "fried", "namkeen"],
        "src": "haldiram",
    },
    {
        "id": 13108, "en": "Haldiram Nut Cracker", "bn": "হলদিরাম নাট ক্র্যাকার",
        "cat": "snack", "s": "100g",
        "k": 555, "p": 14.0, "c": 44.0, "f": 36.0, "fi": 5.0, "ca": 70, "fe": 3.0,
        "kw": ["snack", "haldiram", "nut", "cracker", "nuts", "namkeen"],
        "src": "haldiram",
    },
    {
        "id": 13109, "en": "Haldiram Punjabi Tadka", "bn": "হলদিরাম পাঞ্জাবি তড়কা",
        "cat": "snack", "s": "100g",
        "k": 535, "p": 11.0, "c": 49.0, "f": 33.0, "fi": 4.0, "ca": 58, "fe": 2.8,
        "kw": ["snack", "haldiram", "punjabi", "tadka", "spiced", "namkeen"],
        "src": "haldiram",
    },
    {
        "id": 13110, "en": "Haldiram Diet Mixture", "bn": "হলদিরাম ডায়েট মিশ্রণ",
        "cat": "snack", "s": "100g",
        "k": 500, "p": 12.0, "c": 46.0, "f": 29.0, "fi": 8.0, "ca": 80, "fe": 3.5,
        "kw": ["snack", "haldiram", "diet", "mixture", "low fat", "namkeen"],
        "src": "haldiram",
    },
]

NEW_PACKAGED = [
    {
        "id": 13201, "en": "Lay's Classic Salted", "bn": "লেজ ক্লাসিক সল্টেড",
        "cat": "snack", "s": "100g",
        "k": 536, "p": 6.7, "c": 53.0, "f": 34.0, "fi": 4.5, "ca": 25, "fe": 1.4,
        "kw": ["snack", "lays", "chips", "potato", "salted", "packaged"],
        "src": "brand",
    },
    {
        "id": 13202, "en": "Lay's Magic Masala", "bn": "লেজ ম্যাজিক মসালা",
        "cat": "snack", "s": "100g",
        "k": 540, "p": 6.5, "c": 54.0, "f": 34.0, "fi": 4.2, "ca": 28, "fe": 1.5,
        "kw": ["snack", "lays", "chips", "potato", "masala", "packaged", "spicy"],
        "src": "brand",
    },
    {
        "id": 13203, "en": "Lay's Cream and Onion", "bn": "লেজ ক্রিম অ্যান্ড অনিয়ন",
        "cat": "snack", "s": "100g",
        "k": 535, "p": 6.6, "c": 54.0, "f": 33.0, "fi": 4.0, "ca": 30, "fe": 1.4,
        "kw": ["snack", "lays", "chips", "potato", "cream", "onion", "packaged"],
        "src": "brand",
    },
    {
        "id": 13204, "en": "Lay's Spanish Tomato Tango", "bn": "লেজ স্প্যানিশ টমেটো ট্যাঙ্গো",
        "cat": "snack", "s": "100g",
        "k": 538, "p": 6.5, "c": 55.0, "f": 33.0, "fi": 4.0, "ca": 28, "fe": 1.5,
        "kw": ["snack", "lays", "chips", "potato", "tomato", "spanish", "packaged"],
        "src": "brand",
    },
    {
        "id": 13205, "en": "Lay's Hot and Sweet Chilli", "bn": "লেজ হট অ্যান্ড সুইট চিলি",
        "cat": "snack", "s": "100g",
        "k": 540, "p": 6.4, "c": 55.0, "f": 33.0, "fi": 4.0, "ca": 28, "fe": 1.5,
        "kw": ["snack", "lays", "chips", "potato", "chilli", "sweet", "hot", "packaged"],
        "src": "brand",
    },
    {
        "id": 13206, "en": "Kurkure Masala Munch", "bn": "কুরকুরে মসালা মাঞ্চ",
        "cat": "snack", "s": "100g",
        "k": 547, "p": 7.0, "c": 58.0, "f": 32.0, "fi": 3.0, "ca": 20, "fe": 1.8,
        "kw": ["snack", "kurkure", "masala", "munch", "puffed", "packaged", "spicy"],
        "src": "brand",
    },
    {
        "id": 13207, "en": "Kurkure Chilli Chatka", "bn": "কুরকুরে চিলি চাটকা",
        "cat": "snack", "s": "100g",
        "k": 548, "p": 7.0, "c": 58.0, "f": 32.0, "fi": 3.0, "ca": 20, "fe": 1.8,
        "kw": ["snack", "kurkure", "chilli", "chatka", "puffed", "packaged", "spicy"],
        "src": "brand",
    },
    {
        "id": 13208, "en": "Kurkure Green Chutney", "bn": "কুরকুরে গ্রিন চাটনি",
        "cat": "snack", "s": "100g",
        "k": 545, "p": 7.2, "c": 57.0, "f": 32.0, "fi": 3.2, "ca": 22, "fe": 1.8,
        "kw": ["snack", "kurkure", "green", "chutney", "puffed", "packaged"],
        "src": "brand",
    },
    {
        "id": 13209, "en": "Kurkure Solid Masti", "bn": "কুরকুরে সলিড মস্তি",
        "cat": "snack", "s": "100g",
        "k": 544, "p": 7.0, "c": 57.0, "f": 32.0, "fi": 3.0, "ca": 20, "fe": 1.8,
        "kw": ["snack", "kurkure", "solid", "masti", "puffed", "packaged"],
        "src": "brand",
    },
    {
        "id": 13210, "en": "Kurkure Hyderabadi Hungama", "bn": "কুরকুরে হায়দরাবাদি হাঙ্গামা",
        "cat": "snack", "s": "100g",
        "k": 548, "p": 7.0, "c": 58.0, "f": 32.0, "fi": 3.0, "ca": 20, "fe": 1.8,
        "kw": ["snack", "kurkure", "hyderabadi", "hungama", "puffed", "packaged", "spicy"],
        "src": "brand",
    },
    {
        "id": 13211, "en": "Bingo Mad Angles Achaari Masti", "bn": "বিঙ্গো ম্যাড অ্যাঙ্গেলস আচারি মস্তি",
        "cat": "snack", "s": "100g",
        "k": 520, "p": 7.0, "c": 60.0, "f": 28.0, "fi": 3.5, "ca": 22, "fe": 1.5,
        "kw": ["snack", "bingo", "mad angles", "achaari", "masti", "triangle", "packaged"],
        "src": "brand",
    },
    {
        "id": 13212, "en": "Bingo Mad Angles Tomato Madness", "bn": "বিঙ্গো ম্যাড অ্যাঙ্গেলস টমেটো ম্যাডনেস",
        "cat": "snack", "s": "100g",
        "k": 522, "p": 7.0, "c": 60.0, "f": 28.0, "fi": 3.5, "ca": 22, "fe": 1.5,
        "kw": ["snack", "bingo", "mad angles", "tomato", "madness", "triangle", "packaged"],
        "src": "brand",
    },
    {
        "id": 13213, "en": "Bingo Tedhe Medhe", "bn": "বিঙ্গো টেঢে মেঢে",
        "cat": "snack", "s": "100g",
        "k": 515, "p": 9.0, "c": 57.0, "f": 27.0, "fi": 4.0, "ca": 30, "fe": 2.0,
        "kw": ["snack", "bingo", "tedhe medhe", "noodle snack", "packaged", "masala"],
        "src": "brand",
    },
    {
        "id": 13214, "en": "Uncle Chipps Spicy Treat", "bn": "আঙ্কল চিপস স্পাইসি ট্রিট",
        "cat": "snack", "s": "100g",
        "k": 535, "p": 6.0, "c": 54.0, "f": 34.0, "fi": 4.0, "ca": 25, "fe": 1.3,
        "kw": ["snack", "uncle chipps", "chips", "potato", "spicy", "packaged"],
        "src": "brand",
    },
    {
        "id": 13215, "en": "Doritos Nacho Cheese", "bn": "ডোরিটোস নাচো চিজ",
        "cat": "snack", "s": "100g",
        "k": 495, "p": 7.5, "c": 63.0, "f": 24.0, "fi": 4.8, "ca": 120, "fe": 1.5,
        "kw": ["snack", "doritos", "nacho", "cheese", "tortilla", "packaged"],
        "src": "brand",
    },
]

NEW_FRUITS = [
    {
        "id": 15001, "en": "Apple", "bn": "আপেল",
        "cat": "fruit", "s": "100g",
        "k": 52, "p": 0.3, "c": 13.8, "f": 0.2, "fi": 2.4, "ca": 6, "fe": 0.1,
        "kw": ["fruit", "apple", "red", "green", "seb"],
        "src": "usda",
    },
    {
        "id": 15002, "en": "Pear", "bn": "নাশপাতি",
        "cat": "fruit", "s": "100g",
        "k": 57, "p": 0.4, "c": 15.2, "f": 0.1, "fi": 3.1, "ca": 9, "fe": 0.2,
        "kw": ["fruit", "pear", "nashpati", "নাশপাতি"],
        "src": "usda",
    },
    {
        "id": 15003, "en": "Strawberry", "bn": "স্ট্রবেরি",
        "cat": "fruit", "s": "100g",
        "k": 32, "p": 0.7, "c": 7.7, "f": 0.3, "fi": 2.0, "ca": 16, "fe": 0.4,
        "kw": ["fruit", "strawberry", "berry", "red berry"],
        "src": "usda",
    },
    {
        "id": 15004, "en": "Raspberry", "bn": "রাস্পবেরি",
        "cat": "fruit", "s": "100g",
        "k": 52, "p": 1.2, "c": 11.9, "f": 0.7, "fi": 6.5, "ca": 25, "fe": 0.7,
        "kw": ["fruit", "raspberry", "berry", "red berry", "high fiber"],
        "src": "usda",
    },
    {
        "id": 15005, "en": "Blackberry", "bn": "ব্ল্যাকবেরি",
        "cat": "fruit", "s": "100g",
        "k": 43, "p": 1.4, "c": 9.6, "f": 0.5, "fi": 5.3, "ca": 29, "fe": 0.6,
        "kw": ["fruit", "blackberry", "berry", "dark berry"],
        "src": "usda",
    },
    {
        "id": 15006, "en": "Blueberry", "bn": "ব্লুবেরি",
        "cat": "fruit", "s": "100g",
        "k": 57, "p": 0.7, "c": 14.5, "f": 0.3, "fi": 2.4, "ca": 6, "fe": 0.3,
        "kw": ["fruit", "blueberry", "berry", "antioxidant"],
        "src": "usda",
    },
    {
        "id": 15007, "en": "Bilberry", "bn": "বিলবেরি",
        "cat": "fruit", "s": "100g",
        "k": 48, "p": 0.7, "c": 11.0, "f": 0.5, "fi": 2.8, "ca": 15, "fe": 0.5,
        "kw": ["fruit", "bilberry", "berry", "wild blueberry"],
        "src": "usda",
    },
    {
        "id": 15008, "en": "Gooseberry", "bn": "গুজবেরি",
        "cat": "fruit", "s": "100g",
        "k": 44, "p": 0.9, "c": 10.2, "f": 0.6, "fi": 4.3, "ca": 25, "fe": 0.3,
        "kw": ["fruit", "gooseberry", "berry", "amla like", "sour"],
        "src": "usda",
    },
    {
        "id": 15009, "en": "Red Currant", "bn": "লাল কারেন্ট",
        "cat": "fruit", "s": "100g",
        "k": 56, "p": 1.4, "c": 13.8, "f": 0.2, "fi": 4.3, "ca": 33, "fe": 1.0,
        "kw": ["fruit", "red currant", "currant", "berry", "sour"],
        "src": "usda",
    },
    {
        "id": 15010, "en": "Black Currant", "bn": "কালো কারেন্ট",
        "cat": "fruit", "s": "100g",
        "k": 63, "p": 1.4, "c": 15.4, "f": 0.4, "fi": 4.3, "ca": 55, "fe": 1.5,
        "kw": ["fruit", "black currant", "currant", "berry", "antioxidant"],
        "src": "usda",
    },
    {
        "id": 15011, "en": "Lingonberry", "bn": "লিঙ্গনবেরি",
        "cat": "fruit", "s": "100g",
        "k": 43, "p": 0.8, "c": 9.1, "f": 0.5, "fi": 3.0, "ca": 20, "fe": 0.4,
        "kw": ["fruit", "lingonberry", "berry", "nordic", "sour"],
        "src": "usda",
    },
    {
        "id": 15012, "en": "Cherry", "bn": "চেরি",
        "cat": "fruit", "s": "100g",
        "k": 63, "p": 1.1, "c": 16.0, "f": 0.2, "fi": 2.1, "ca": 13, "fe": 0.4,
        "kw": ["fruit", "cherry", "cherri", "sweet", "red"],
        "src": "usda",
    },
    {
        "id": 15013, "en": "Plum", "bn": "বরই",
        "cat": "fruit", "s": "100g",
        "k": 46, "p": 0.7, "c": 11.4, "f": 0.3, "fi": 1.4, "ca": 6, "fe": 0.2,
        "kw": ["fruit", "plum", "boroi", "বরই", "stone fruit"],
        "src": "usda",
    },
    {
        "id": 15014, "en": "Damson Plum", "bn": "ড্যামসন বরই",
        "cat": "fruit", "s": "100g",
        "k": 50, "p": 0.8, "c": 12.5, "f": 0.3, "fi": 1.8, "ca": 8, "fe": 0.3,
        "kw": ["fruit", "damson", "plum", "stone fruit", "dark plum"],
        "src": "usda",
    },
    {
        "id": 15015, "en": "Apricot", "bn": "খুবানি",
        "cat": "fruit", "s": "100g",
        "k": 48, "p": 1.4, "c": 11.1, "f": 0.4, "fi": 2.0, "ca": 13, "fe": 0.4,
        "kw": ["fruit", "apricot", "khubani", "খুবানি", "orange fruit"],
        "src": "usda",
    },
    {
        "id": 15016, "en": "Peach", "bn": "পিচ",
        "cat": "fruit", "s": "100g",
        "k": 39, "p": 0.9, "c": 9.5, "f": 0.3, "fi": 1.5, "ca": 6, "fe": 0.3,
        "kw": ["fruit", "peach", "pich", "stone fruit", "fuzzy"],
        "src": "usda",
    },
    {
        "id": 15017, "en": "Nectarine", "bn": "নেকটারিন",
        "cat": "fruit", "s": "100g",
        "k": 44, "p": 1.1, "c": 10.6, "f": 0.3, "fi": 1.7, "ca": 6, "fe": 0.3,
        "kw": ["fruit", "nectarine", "stone fruit", "smooth peach"],
        "src": "usda",
    },
    {
        "id": 15018, "en": "Quince", "bn": "কুইন্স",
        "cat": "fruit", "s": "100g",
        "k": 57, "p": 0.4, "c": 15.3, "f": 0.1, "fi": 1.9, "ca": 11, "fe": 0.7,
        "kw": ["fruit", "quince", "sour fruit", "yellow fruit"],
        "src": "usda",
    },
    {
        "id": 15019, "en": "Elderberry", "bn": "এল্ডারবেরি",
        "cat": "fruit", "s": "100g",
        "k": 73, "p": 0.7, "c": 18.4, "f": 0.5, "fi": 7.0, "ca": 38, "fe": 1.6,
        "kw": ["fruit", "elderberry", "berry", "high fiber", "antioxidant"],
        "src": "usda",
    },
    {
        "id": 15020, "en": "Cranberry", "bn": "ক্র্যানবেরি",
        "cat": "fruit", "s": "100g",
        "k": 46, "p": 0.5, "c": 12.2, "f": 0.1, "fi": 4.6, "ca": 8, "fe": 0.2,
        "kw": ["fruit", "cranberry", "berry", "sour", "uti"],
        "src": "usda",
    },
]

ALL_NEW_GROUPS = [
    ("Sweets", NEW_SWEETS),
    ("Papads", NEW_PAPADS),
    ("Haldiram Namkeen", NEW_HALDIRAM),
    ("Packaged Snacks", NEW_PACKAGED),
    ("Fruits / Berries", NEW_FRUITS),
]


def normalize_kw(kw):
    """Ensure kw is a list of strings."""
    if kw is None:
        return []
    if isinstance(kw, str):
        return [t.strip() for t in kw.split() if t.strip()]
    return list(kw)


def main():
    print(f"Loading dataset from {DATASET}")
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    print(f"Loaded {len(data)} items")

    # ------------------------------------------------------------------
    # Phase 0 — Pre-normalize existing categories + kw
    # ------------------------------------------------------------------
    cat_changes = 0
    for item in data:
        old_cat = item.get("cat", "")
        new_cat = CAT_NORM.get(old_cat)
        if new_cat:
            item["cat"] = new_cat
            cat_changes += 1
        # Normalize kw to list while we're here
        item["kw"] = normalize_kw(item.get("kw"))

    print(f"Pre-normalized {cat_changes} category values in existing items")

    # ------------------------------------------------------------------
    # Build set of existing English names (lower-cased) for dup detection
    # ------------------------------------------------------------------
    existing_names = {item["en"].strip().lower() for item in data}
    existing_ids = {item["id"] for item in data}

    # ------------------------------------------------------------------
    # Phase 1 — Add new items
    # ------------------------------------------------------------------
    added = 0
    skipped = 0

    for group_name, group_items in ALL_NEW_GROUPS:
        group_added = 0
        group_skipped = 0
        for item in group_items:
            name_key = item["en"].strip().lower()
            if name_key in existing_names:
                print(f"  SKIP (dup): {item['en']}")
                group_skipped += 1
                skipped += 1
                continue
            if item["id"] in existing_ids:
                print(f"  SKIP (id conflict {item['id']}): {item['en']}")
                group_skipped += 1
                skipped += 1
                continue
            # Ensure kw is a list
            item["kw"] = normalize_kw(item.get("kw", []))
            # Ensure src is present
            if "src" not in item:
                item["src"] = "local"
            data.append(item)
            existing_names.add(name_key)
            existing_ids.add(item["id"])
            group_added += 1
            added += 1
        print(f"Group '{group_name}': added {group_added}, skipped {group_skipped}")

    # ------------------------------------------------------------------
    # Write back
    # ------------------------------------------------------------------
    print(f"\nTotal items before: {len(data) - added}")
    print(f"Total items after:  {len(data)}")
    print(f"Added: {added}  |  Skipped (dups): {skipped}")

    DATASET.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nSaved to {DATASET}")


if __name__ == "__main__":
    main()
