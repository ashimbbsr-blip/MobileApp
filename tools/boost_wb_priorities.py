"""
Boost search_priority for WB/Odisha v9 foods so they appear prominently
in category browse and search results in this Bengal-focused app.

Priority tiers (for reference):
  90  = butter chicken, very common pan-Indian
  80-88 = common INDB foods (fish cutlet, rohu raw, etc.)
  70-79 = WB/regional famous dishes
  65-69 = WB district specials, Odisha foods
  55-64 = less common regional items
  45-54 = very specific items (kept as-is for now)
"""
import json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FOOD_MASTER = 'assets/data/food_master_v9_0.json'

# ── Name-pattern → priority boost ─────────────────────────────────────────────
# Each entry: (list of EN name substrings, new_priority)
# Applied in order; first match wins.

PRIORITY_RULES = [
    # ── Tier 1 (90): Absolute Bengali/WB icons — must appear first ────────────
    (['Shorshe Ilish', 'Sorshe Ilish', 'Hilsa Besara', 'Hooghly Hilsa',
      'Howrah Shorshe Ilish', 'Nadia Style',
      'Dab Chingri', 'Chingri Malai Curry', 'Golda Chingri Malai',
      'Kolkata Biryani', 'Mutton Biryani Kolkata', 'Chicken Biryani Kolkata',
      'Kosha Mangsho', 'Howrah Mutton',
      'Mishti Doi', 'Nolen Gur',
      'Mughlai Paratha', 'Moghlai Porota',
      'Bhetki Fish Fry', 'Bhetki Cutlet', 'Bhetki Paturi'], 90),

    # ── Tier 2 (88): Major Bengali dishes & sweets ────────────────────────────
    (['Rasgulla', 'Rosogolla', 'Roshogolla', 'Rasagola',
      'Langcha', 'Mihidana', 'Sitabhog',
      'Chhanar Kofta', 'Malai Kofta',
      'Mutton Rezala', 'Gauda Mutton',
      'Ilish Kalia', 'Doi Ilish', 'Ilish Bhapa', 'Ilish Paturi', 'Ilish Roast',
      'Hilsa Curry',
      'Chingri Sorshe', 'Chingri Kalia', 'Chingri Jhal',
      'Aloo Posto', 'Posto Bora',
      'Mishti Doi (Terracotta', 'Bangaon Mishti Doi', 'Bardhaman Mishti Doi',
      'Howrah Rasgulla', 'Chinsurah Rosogolla',
      'Fish Fry Bengali', 'Kabiraji',
      'Doi Katla', 'Doi Rui', 'Rui Kalia'], 88),

    # ── Tier 3 (85): Popular WB fish/prawn/meat preparations ─────────────────
    (['Chingri Bhuna', 'Chingri Narikel', 'Potol Chingri', 'Bandhakopi Chingri',
      'Mocha Chingri', 'Chingri Kabiraji',
      'Ucche Posto', 'Jhinge Posto', 'Potol Posto', 'Chingri Posto',
      'Posto Bata', 'Ghatal Alu Posto',
      'Ilish Tok', 'Chingri Malai Roast',
      'Bhetki Butter Garlic', 'Bhetki Continental', 'Bhetki Florentine',
      'Chitol Muitha', 'Chitol Peti',
      'Doi Chire', 'Panta Bhat',
      'Bardhaman Alu Posto', 'Bardhaman Mutton',
      'Tangra Macher', 'Parshe Fry', 'Mourala Fry',
      'Mochar Ghonto', 'Bishnupur Mocha', 'Birbhum Mochar',
      'Bardhaman Mochar',
      'Thor Chorchori', 'Chhanar Dalna',
      'Sar Bhaja', 'Sarbhaja', 'Sar Puria', 'Sarpuria'], 85),

    # ── Tier 4 (82): Sandesh / sweet varieties + WB pithe ────────────────────
    (['Sandesh', 'Sondesh', 'Nolen Gur Sandesh', 'Patali Gur Sandesh',
      'Patisapta', 'Chitoi Pitha', 'Pithe', 'Pitha',
      'Chhanar Payesh', 'Nolen Gur Payesh',
      'Jilipi', 'Langcha (Shaktigarh)',
      'Mecha Sandesh', 'Kancha Golla',
      'Bardhaman Nolen Gur', 'Basirhat Nolen Gur',
      'Bolpur Chhanar', 'Kalna Chhanar',
      'Danadar', 'Jolbhora', 'Chhanar Murki', 'Murki'], 82),

    # ── Tier 5 (80): Kolkata street + famous district dishes ─────────────────
    (['Kolkata', 'Howrah', 'Santragachi',
      'Bardhaman', 'Krishnanagar', 'Nabadwip', 'Shaktigarh',
      'Hooghly', 'Basirhat', 'Bangaon', 'Nadia',
      'Fulkopi Roast', 'Kochur Mukhi',
      'Aam Panna', 'Dab-er-Jol', 'Gandharaj Ghol',
      'Malda Fazli', 'Malda Himsagar', 'Malda Aam',
      'Fish Biryani', 'Prawn Biryani', 'Egg Biryani',
      'Ghee Rice', 'Nawabi Pulao', 'Zafrani Pulao'], 80),

    # ── Tier 6 (78): Other WB districts + Mayapur/temple ─────────────────────
    (['Murshidabad', 'Birbhum', 'Bankura', 'Purulia',
      'Medinipur', 'Bishnupur', 'Digha', 'Tamluk',
      'Bolpur', 'Santiniketan', 'Malda',
      'Hasnabad', 'Balurghat', 'Mahananda', 'Gangarampur',
      'Raiganj', 'Ghatal', 'Kalna', 'Katwa', 'Egra',
      'Bally ', 'Domjur', 'Ichamati', 'Arambagh',
      'Mayapur', 'ISKCON', 'Belur Math', 'Habisha',
      'Panchamrit', 'Makhana Prasad', 'Boondi Prasad',
      'Charanamrit'], 78),

    # ── Tier 7 (75): Odisha iconic foods ─────────────────────────────────────
    (['Pahala Rasagola', 'Salepur Rasagola',
      'Chhena Gaja', 'Chhena Poda', 'Chhena Jhilli', 'Chhena Khai', 'Chhena Murki',
      'Khaja (Mahaprasad)', 'Kanika', 'Khechudi',
      'Pakhala', 'Dalama', 'Dalima', 'Santula',
      'Ganjam', 'Gopalpur Crab', 'Kandhamal',
      'Tanka Torani', 'Macha Besara', 'Macha Patrapoda',
      'Chingudi Besara', 'Chingudi Kalia', 'Chingudi Biryani',
      'Mandia', 'Pheni', 'Gaja', 'Rasabali'], 75),

    # ── Tier 8 (72): NI breads & other v9 new additions ──────────────────────
    (['Butter Kulcha', 'Coin Paratha', 'Laccha Paratha', 'Warqi Paratha',
      'Rumali Roti', 'Butter Naan', 'Garlic Naan',
      'Kashmiri Pulao', 'Dum Pulao',
      'Chingri Narkel', 'Choto Mouri', 'Atrai River',
      'Bhetki Newburg', 'Bhetki Meuniere',
      'Wild Mushroom', 'Purulia Bamboo', 'Purulia Dhuska',
      'Islampur Litti', 'Raiganj Dhuska'], 72),
]

# Catch-all by ID range: any new v9 food not matched above gets baseline 68
NEW_FOOD_ID_THRESHOLD = 24000
NEW_FOOD_BASE_PRIORITY = 68

def main():
    with open(FOOD_MASTER, encoding='utf-8') as f:
        foods = json.load(f)

    changed = 0
    for food in foods:
        fid = food.get('id', 0)
        en = food.get('en', '')
        current_priority = food.get('search_priority') or 50

        # Don't lower already-high priorities from INDB base unless we're promoting WB icons
        # Allow overwrite if new priority > current (always boost, never lower)


        new_priority = None

        # Check name-pattern rules
        for patterns, priority in PRIORITY_RULES:
            if any(p.lower() in en.lower() for p in patterns):
                new_priority = priority
                break

        # ID-range catch-all for new v9 foods
        if new_priority is None and fid >= NEW_FOOD_ID_THRESHOLD:
            new_priority = NEW_FOOD_BASE_PRIORITY

        if new_priority is not None and new_priority > current_priority:
            food['search_priority'] = new_priority
            changed += 1

    print(f'Updated priorities for {changed} foods')

    # Verify top fish foods now
    fish = [f for f in foods if f.get('cat') == 'fish']
    fish.sort(key=lambda x: -(x.get('search_priority') or 50))
    print('\nTop 10 fish by priority after boost:')
    for f in fish[:10]:
        print(f'  [{f.get("search_priority",50)}] {f["en"]}')

    with open(FOOD_MASTER, 'w', encoding='utf-8') as f:
        json.dump(foods, f, ensure_ascii=False, separators=(',', ':'))
    print(f'\nSaved {FOOD_MASTER}')

if __name__ == '__main__':
    main()
