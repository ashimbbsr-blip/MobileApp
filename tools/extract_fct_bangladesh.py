"""
Extract food composition data from Bangladesh FCT PDF and merge into the app dataset.
"""
import pdfplumber
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

PDF_PATH = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\FCT_10_2_14_final_version.pdf'
MASTER_PATH = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v5_3.json'
INDEX_EN_PATH = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_en_v5_3.json'
INDEX_BN_PATH = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_bn_v5_3.json'

CODE_RE = re.compile(r'^(\d{2}_\d{4})\s+(.+)$')
NUM_RE = re.compile(r'^\(?\[?-?[\d.]+\]?\)?$')

# Food category mapping based on code prefix
CAT_MAP = {
    '01': 'cereal',
    '02': 'legume',
    '03': 'vegetable',
    '04': 'fruit',
    '05': 'vegetable',   # tubers/roots
    '06': 'fish',
    '07': 'meat',
    '08': 'dairy',
    '09': 'oil',
    '10': 'sugar',
    '11': 'beverage',
    '12': 'spice',
    '13': 'mixed',
}

CAT_LABEL = {
    'cereal': 'grain',
    'legume': 'legume',
    'vegetable': 'vegetable',
    'fruit': 'fruit',
    'fish': 'fish',
    'meat': 'meat',
    'dairy': 'dairy',
    'oil': 'fat',
    'sugar': 'sweet',
    'beverage': 'beverage',
    'spice': 'spice',
    'mixed': 'dish',
}


def safe_float(s):
    """Parse a number string, stripping brackets/parens, return None if invalid."""
    if s is None:
        return None
    s = s.strip().strip('[]()').strip()
    try:
        return float(s)
    except ValueError:
        return None


def parse_proximate_line(line):
    """
    Parse a proximate data line:
    code  EN_name  BN_name  edible_coeff  (kcal) kJ  water  protein  fat  carb  fiber  ash
    Returns dict or None.
    """
    line = line.strip()
    m = re.match(r'(\d{2}_\d{4})\s+(.+)', line)
    if not m:
        return None
    code = m.group(1)
    rest = m.group(2)

    # Extract energy: looks like (324) 1360 or just 1360
    # Format: ... edible_coef  (kcal) kJ  water protein fat carb fiber ash
    # Try to find the edible coefficient (1.00 or 0.XX)
    # Then numeric sequence at end
    nums_at_end = re.findall(r'[\d.]+', rest)
    # We expect at least: edible_coeff, kcal_in_parens, kJ, water, protein, fat, carb, [fiber], [ash]
    # The English name and Bengali name are mixed text

    # Strategy: find the edible portion coefficient (the first standalone decimal like 1.00, 0.6, etc.)
    # Then extract trailing numbers
    ep_match = re.search(r'\b(1\.00|0\.\d{2})\b', rest)
    if not ep_match:
        return None

    ep_pos = ep_match.start()
    name_part = rest[:ep_pos].strip()
    numbers_part = rest[ep_pos:].strip()

    # Extract all numbers from numbers_part
    # kcal is in parens: (324) then kJ then water protein fat carb fiber ash
    nums = re.findall(r'\([\d.]+\)|[\d.]+', numbers_part)
    nums_clean = [n.strip('()') for n in nums]

    if len(nums_clean) < 5:
        return None

    # First num is edible coeff, second is kcal (in parens), third is kJ,
    # then water, protein, fat, carb, fiber, ash
    try:
        idx = 0
        edible = float(nums_clean[idx]); idx += 1
        kcal = float(nums_clean[idx]); idx += 1
        kj = float(nums_clean[idx]); idx += 1
        water = float(nums_clean[idx]); idx += 1
        protein = float(nums_clean[idx]); idx += 1
        fat = float(nums_clean[idx]); idx += 1
        carb = float(nums_clean[idx]); idx += 1
        fiber = float(nums_clean[idx]) if idx < len(nums_clean) else None; idx += 1
        ash = float(nums_clean[idx]) if idx < len(nums_clean) else None
    except (ValueError, IndexError):
        return None

    return {
        'code': code,
        '_name_part': name_part,
        'kcal': kcal,
        'protein': protein,
        'fat': fat,
        'carb': carb,
        'fiber': fiber,
    }


def parse_mineral_line(line):
    """
    Parse a mineral line: code  EN_name  Ca Fe Mg P K Na Zn Cu
    """
    line = line.strip()
    m = re.match(r'(\d{2}_\d{4})\s+(.+)', line)
    if not m:
        return None
    code = m.group(1)
    rest = m.group(2)

    nums = re.findall(r'-?[\d.]+', rest)
    if len(nums) < 4:
        return None
    try:
        ca = float(nums[0])
        fe = float(nums[1])
        mg = float(nums[2])
        p = float(nums[3])
        k = float(nums[4]) if len(nums) > 4 else None
        na = float(nums[5]) if len(nums) > 5 else None
        zn = float(nums[6]) if len(nums) > 6 else None
    except (ValueError, IndexError):
        return None

    return {'code': code, 'ca': ca, 'fe': fe, 'mg': mg, 'pot': k, 'zn': zn}


def parse_vitamin_line(line):
    """
    Parse a vitamin line: code  EN_name  VitA Retinol BetaCar VitD VitE Thiamin Riboflavin Niacin B6 Folate VitC
    """
    line = line.strip()
    m = re.match(r'(\d{2}_\d{4})\s+(.+)', line)
    if not m:
        return None
    code = m.group(1)
    rest = m.group(2)

    nums = re.findall(r'[\[\(]?-?[\d.]+[\]\)]?', rest)
    nums_clean = [n.strip('[]()') for n in nums]

    if len(nums_clean) < 3:
        return None
    try:
        va = float(nums_clean[0])   # Vitamin A RAE (mcg)
        # retinol = nums_clean[1]
        # beta_car = nums_clean[2]
        vd = float(nums_clean[3]) if len(nums_clean) > 3 else None   # Vitamin D (mcg)
        # ve = nums_clean[4]
        # thiamin = nums_clean[5]
        # riboflavin = nums_clean[6]
        # niacin = nums_clean[7]
        # b6 = nums_clean[8]
        # folate = nums_clean[9]
        vc = float(nums_clean[10]) if len(nums_clean) > 10 else None  # Vitamin C (mg)
    except (ValueError, IndexError):
        return None

    return {'code': code, 'va': va, 'vd': vd, 'vc': vc}


def extract_name_parts(name_part):
    """
    Separate English name from Bengali name in the mixed name_part string.
    Bengali characters are in Unicode range U+0980-U+09FF.
    """
    bn_chars = re.compile(r'[ঀ-৿]+')
    en_chars = re.compile(r'[A-Za-z0-9,./\-()\' ]+')

    # Find runs of Bengali text
    bn_parts = bn_chars.findall(name_part)
    # Remaining (after removing Bengali) is English
    en_part = bn_chars.sub('', name_part).strip()
    # Clean up extra spaces
    en_part = re.sub(r'\s+', ' ', en_part).strip()
    bn_part = ' '.join(p.strip() for p in bn_parts if p.strip())

    return en_part, bn_part


def classify_page(text):
    if 'Food name in Bengali' in text or ('Edible' in text and 'portion' in text and 'Protein' in text):
        return 'proximate'
    if 'Ca (mg)' in text or 'Fe (mg)' in text:
        return 'mineral'
    if 'Thiamin' in text or ('Vitamin A' in text and 'Retinol' in text):
        return 'vitamin'
    return None


CODE_START_RE = re.compile(r'^\d{2}_\d{4}')


def extract_food_blocks(text, page_type):
    """Extract food data blocks from a page's text."""
    results = []
    current_code = None
    current_lines = []

    for raw_line in text.split('\n'):
        stripped = raw_line.strip()
        if not stripped:
            continue
        # Skip header/SD/n lines
        if re.match(r'^(SD or|n\s*\d*$|Code\s|Food name|Edible|Energy|Water|Protein|Ca \(|Fe \(|Vitamin|Beta|Thiamin|Ribof|Niacin|Folate|Retinol)', stripped):
            continue

        if CODE_START_RE.match(stripped):
            # Save previous block
            if current_code and current_lines:
                combined = ' '.join(current_lines)
                if page_type == 'proximate':
                    r = parse_proximate_line(combined)
                elif page_type == 'mineral':
                    r = parse_mineral_line(combined)
                elif page_type == 'vitamin':
                    r = parse_vitamin_line(combined)
                else:
                    r = None
                if r:
                    results.append(r)
            current_code = stripped[:7]
            current_lines = [stripped]
        elif current_code:
            # Continuation line (Bengali name or split values)
            current_lines.append(stripped)

    # Last block
    if current_code and current_lines:
        combined = ' '.join(current_lines)
        if page_type == 'proximate':
            r = parse_proximate_line(combined)
        elif page_type == 'mineral':
            r = parse_mineral_line(combined)
        elif page_type == 'vitamin':
            r = parse_vitamin_line(combined)
        else:
            r = None
        if r:
            results.append(r)

    return results


def load_bengali_names(pdf_path):
    """
    Dedicated pass to extract Bengali names from proximate pages.
    Bengali text appears on the same line or very next line after the code + English name.
    """
    bn_map = {}  # code -> bengali name
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ''
            if classify_page(text) != 'proximate':
                continue
            lines = text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                m = re.match(r'(\d{2}_\d{4})\s+(.*)', line)
                if not m:
                    continue
                code = m.group(1)
                rest = m.group(2)
                # Look for Bengali chars in rest or next line
                bn_re = re.compile(r'[ঀ-৿][ঀ-৿\s,./\-]*')
                bn_found = bn_re.findall(rest)
                if not bn_found and i + 1 < len(lines):
                    bn_found = bn_re.findall(lines[i + 1])
                if bn_found:
                    bn_name = ' '.join(p.strip() for p in bn_found if p.strip())
                    if code not in bn_map and bn_name:
                        bn_map[code] = bn_name
    return bn_map


def extract_all(pdf_path):
    """Extract all food data from the PDF."""
    prox_data = {}   # code -> proximate fields
    min_data = {}    # code -> mineral fields
    vit_data = {}    # code -> vitamin fields
    # Also: English name from proximate page
    en_names = {}
    bn_names = {}

    print("Pass 1: Extracting Bengali names...")
    bn_names = load_bengali_names(pdf_path)
    print(f"  Found {len(bn_names)} Bengali names")

    print("Pass 2: Extracting nutritional data...")
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ''
            ptype = classify_page(text)
            if not ptype:
                continue

            blocks = extract_food_blocks(text, ptype)
            for block in blocks:
                code = block['code']
                if ptype == 'proximate':
                    np = block.get('_name_part', '')
                    en, bn = extract_name_parts(np)
                    if en and code not in en_names:
                        en_names[code] = en.strip()
                    if bn and code not in bn_names:
                        bn_names[code] = bn.strip()
                    prox_data[code] = {k: v for k, v in block.items() if k not in ('code', '_name_part')}
                elif ptype == 'mineral':
                    min_data[code] = {k: v for k, v in block.items() if k != 'code'}
                elif ptype == 'vitamin':
                    vit_data[code] = {k: v for k, v in block.items() if k != 'code'}

    print(f"  Proximate: {len(prox_data)}, Mineral: {len(min_data)}, Vitamin: {len(vit_data)}")
    print(f"  English names: {len(en_names)}, Bengali names: {len(bn_names)}")
    return prox_data, min_data, vit_data, en_names, bn_names


def build_food_items(prox_data, min_data, vit_data, en_names, bn_names):
    """Combine all data into food items matching app dataset format."""
    # Also manually handle common Bengali food name translations
    # for items where Bengali OCR didn't work (most FCT PDFs don't have Bengali in them)

    # Manual Bengali names for key foods (when OCR fails)
    manual_bn = {
        '01_0001': 'যব, সম্পূর্ণ শস্য',
        '01_0002': 'বনরুটি, বান/রোল',
        '01_0003': 'পাউরুটি',
        '01_0004': 'ভুট্টা আটা',
        '01_0005': 'ভুট্টা, হলুদ, শুকনো',
        '01_0006': 'কাউন',
        '01_0007': 'চিনা, গোটা দানা',
        '01_0009': 'পপকর্ন, ভুট্টা',
        '01_0011': 'চিড়া, ভেজা',
        '01_0013': 'চাল, BR-11, সিদ্ধ, কোলেছাটা',
        '01_0025': 'চাল, আতপ, HYV, কোলেছাটা',
        '01_0026': 'সুজি, গম',
        '01_0027': 'জোয়ার',
        '01_0028': 'ভুট্টা, মিষ্টি, হলুদ',
        '01_0029': 'সেমাই, গম',
        '01_0034': 'মিষ্টি বিস্কুট',
        '01_0035': 'খিচুড়ি',
        '01_0037': 'ভাত, BR-28',
        '01_0041': 'ভাত, আতপ, বসা ভাত',
        '01_0042': 'রুটি',
        '02_0001': 'মটরশুঁটি, কালো, কাঁচা',
        '02_0002': 'মটরশুঁটি, সবুজ, কাঁচা',
        '02_0003': 'ছোলা, কাঁচা',
        '02_0004': 'মসুর ডাল, কাঁচা',
        '02_0005': 'মুগ ডাল, কাঁচা',
        '02_0006': 'মাষকলাই ডাল, কাঁচা',
        '02_0007': 'সয়াবিন, কাঁচা',
        '02_0008': 'মটরশুঁটি, হলুদ, কাঁচা',
        '02_0009': 'অড়হর ডাল, কাঁচা',
        '02_0010': 'মুগ ডাল, সিদ্ধ',
        '02_0011': 'মসুর ডাল, সিদ্ধ',
        '02_0012': 'ছোলার ডাল, সিদ্ধ',
        '03_0001': 'আলু, কাঁচা',
        '03_0002': 'মিষ্টি আলু, কাঁচা',
        '03_0003': 'গাজর, কাঁচা',
        '03_0004': 'বেগুন, কাঁচা',
        '03_0005': 'ফুলকপি, কাঁচা',
        '03_0006': 'শিম, কাঁচা',
        '03_0007': 'মরিচ, সবুজ, কাঁচা',
        '03_0008': 'ধনেপাতা, কাঁচা',
        '03_0009': 'শসা, কাঁচা',
        '03_0010': 'ঢ্যাঁড়শ, কাঁচা',
        '03_0011': 'পেঁয়াজ, কাঁচা',
        '03_0012': 'টমেটো, পাকা, কাঁচা',
        '03_0013': 'মিষ্টি কুমড়া, কাঁচা',
        '03_0014': 'লাউ, কাঁচা',
        '03_0015': 'পালং শাক, কাঁচা',
        '03_0016': 'লাল শাক, কাঁচা',
        '03_0017': 'মুলা, কাঁচা',
        '03_0018': 'কচুর লতি, কাঁচা',
        '03_0019': 'কলার মোচা, কাঁচা',
        '03_0020': 'পাটশাক, কাঁচা',
        '03_0021': 'কাঁচা কলা, কাঁচা',
        '03_0022': 'পেঁপে, কাঁচা',
        '03_0023': 'করলা, কাঁচা',
        '03_0024': 'ঝিঙা, কাঁচা',
        '03_0025': 'চিচিঙ্গা, কাঁচা',
        '03_0026': 'কাঁকরোল, কাঁচা',
        '03_0027': 'পটল, কাঁচা',
        '03_0028': 'কুমড়া, কাঁচা',
        '03_0029': 'ডাঁটাশাক, কাঁচা',
        '03_0030': 'কলমিশাক, কাঁচা',
        '04_0001': 'আম, পাকা',
        '04_0002': 'কলা, পাকা',
        '04_0003': 'কাঁঠাল, পাকা',
        '04_0004': 'পেয়ারা, পাকা',
        '04_0005': 'আনারস, পাকা',
        '04_0006': 'তরমুজ, পাকা',
        '04_0007': 'পেঁপে, পাকা',
        '04_0008': 'আপেল, পাকা',
        '04_0009': 'আমড়া, পাকা',
        '04_0010': 'জামরুল, পাকা',
        '04_0011': 'আমলকি, পাকা',
        '04_0012': 'লিচু, পাকা',
        '04_0013': 'বরই, পাকা',
        '04_0014': 'নারকেল, পাকা',
        '04_0015': 'তেঁতুল, পাকা',
        '04_0016': 'খেজুর',
        '04_0017': 'কমলা',
        '04_0018': 'লেবু',
        '04_0019': 'বাতাবি লেবু',
        '04_0020': 'সফেদা',
        '04_0021': 'জাম',
        '04_0022': 'কদবেল',
        '04_0023': 'বেল',
        '04_0024': 'শরিফা',
        '04_0025': 'চালতা',
        '04_0026': 'জলপাই',
        '04_0027': 'কলা, কাঁচা',
        '04_0028': 'পেঁপে, কাঁচা',
        '05_0001': 'আলু, কাঁচা',
        '05_0002': 'মিষ্টি আলু, কাঁচা',
        '05_0003': 'কচু, কাঁচা',
        '05_0004': 'কাসাভা, কাঁচা',
        '05_0009': 'মুখীকচু, কাঁচা',
        '05_0011': 'শালগম, কাঁচা',
        '05_0014': 'মূলা, কাঁচা',
        '05_0015': 'বীট, কাঁচা',
        '06_0001': 'রুই মাছ, কাঁচা',
        '06_0002': 'কাতলা মাছ, কাঁচা',
        '06_0003': 'মৃগেল মাছ, কাঁচা',
        '06_0004': 'ইলিশ মাছ, কাঁচা',
        '06_0005': 'পাঙ্গাস মাছ, কাঁচা',
        '06_0006': 'তেলাপিয়া মাছ, কাঁচা',
        '06_0007': 'শিং মাছ, কাঁচা',
        '06_0008': 'মাগুর মাছ, কাঁচা',
        '06_0009': 'পুঁটি মাছ, কাঁচা',
        '06_0010': 'কই মাছ, কাঁচা',
        '06_0011': 'শোল মাছ, কাঁচা',
        '06_0012': 'বোয়াল মাছ, কাঁচা',
        '06_0013': 'বাইম মাছ, কাঁচা',
        '06_0014': 'টেংরা মাছ, কাঁচা',
        '06_0015': 'চিংড়ি, কাঁচা',
        '06_0016': 'কাঁকড়া, কাঁচা',
        '06_0017': 'ইলিশ মাছ, ভাজা',
        '06_0018': 'রুই মাছ, ভাজা',
        '06_0019': 'চিংড়ি ভুনা',
        '07_0001': 'গরুর মাংস, কাঁচা',
        '07_0002': 'ছাগলের মাংস, কাঁচা',
        '07_0003': 'মুরগির মাংস, কাঁচা',
        '07_0004': 'হাঁসের মাংস, কাঁচা',
        '07_0005': 'ভেড়ার মাংস, কাঁচা',
        '07_0006': 'শূকরের মাংস, কাঁচা',
        '07_0007': 'গরুর কলিজা, কাঁচা',
        '07_0008': 'মুরগির কলিজা, কাঁচা',
        '07_0009': 'গরুর মাংস, রান্না',
        '07_0010': 'মুরগির মাংস, রান্না',
        '07_0016': 'ডিম, মুরগি, কাঁচা',
        '07_0017': 'ডিম, হাঁস, কাঁচা',
        '07_0018': 'ডিম, মুরগি, সিদ্ধ',
        '08_0001': 'দুধ, গরু, তাজা',
        '08_0002': 'দুধ, ছাগল, তাজা',
        '08_0003': 'দই, গরুর দুধ',
        '08_0004': 'পনির',
        '08_0005': 'মাখন',
        '08_0006': 'ঘি, গরু',
        '08_0017': 'দুধ, গুঁড়া, পূর্ণ ক্রিম',
        '08_0018': 'দুধ, গুঁড়া, স্কিম',
        '08_0019': 'কনডেন্সড মিল্ক',
        '08_0031': 'দই, সেট',
        '08_0032': 'মিষ্টি দই',
        '08_0033': 'ছানা',
        '09_0001': 'সয়াবিন তেল',
        '09_0002': 'সরিষার তেল',
        '09_0003': 'নারকেল তেল',
        '09_0016': 'পামওয়েল',
        '09_0017': 'মাছের তেল',
        '09_0018': 'ঘি',
        '10_0001': 'চিনি, সাদা',
        '10_0002': 'গুড়, খেজুর',
        '10_0003': 'মধু',
        '11_0001': 'চা, কালো',
        '11_0002': 'কফি',
        '12_0001': 'হলুদ, গুঁড়া',
        '12_0002': 'মরিচ, শুকনো, গুঁড়া',
        '12_0003': 'জিরা',
        '12_0004': 'ধনে, গুঁড়া',
        '12_0005': 'আদা, কাঁচা',
        '12_0006': 'রসুন, কাঁচা',
        '12_0007': 'পেঁয়াজ, শুকনো',
        '13_0001': 'মুগ ডালের খিচুড়ি',
        '13_0002': 'মাছের ঝোল',
        '13_0003': 'মুরগির তরকারি',
    }

    all_codes = set(prox_data.keys()) | set(min_data.keys()) | set(vit_data.keys())
    items = []

    for code in sorted(all_codes):
        prox = prox_data.get(code, {})
        mins = min_data.get(code, {})
        vits = vit_data.get(code, {})

        kcal = prox.get('kcal')
        if not kcal:
            continue  # Skip entries without energy data

        en = en_names.get(code, '').strip()
        # Clean up English name
        en = re.sub(r'\s+', ' ', en).strip('*').strip()
        if not en:
            continue

        # Bengali name: priority: OCR from proximate page > manual map
        bn = bn_names.get(code, '') or manual_bn.get(code, '')
        if not bn:
            # Transliterate or use English as fallback
            bn = en  # will be replaced manually

        # Determine category
        cat_prefix = code[:2]
        cat = CAT_MAP.get(cat_prefix, 'dish')
        cat = CAT_LABEL.get(cat, 'dish')

        # Keywords from English name
        kw = list(set(w.lower() for w in re.findall(r'[A-Za-z]+', en) if len(w) > 2))

        item = {
            'en': en,
            'bn': bn,
            's': '100g',
            'k': round(kcal, 1),
            'p': round(prox.get('protein', 0) or 0, 1),
            'c': round(prox.get('carb', 0) or 0, 1),
            'f': round(prox.get('fat', 0) or 0, 1),
            'fi': round(prox.get('fiber', 0) or 0, 1) if prox.get('fiber') else 0.0,
            'ca': round(mins.get('ca', 0) or 0, 1),
            'fe': round(mins.get('fe', 0) or 0, 2),
            'zn': round(mins.get('zn', 0) or 0, 2),
            'cat': cat,
            'kw': sorted(kw),
            'src': 'bd_fct',
            'va': round(vits.get('va', 0) or 0, 1),
            'vc': round(vits.get('vc', 0) or 0, 1),
            'vd': round(vits.get('vd', 0) or 0, 2),
            'mg': round(mins.get('mg', 0) or 0, 1),
            'pot': round(mins.get('pot', 0) or 0, 1),
        }
        items.append((code, item))

    return items


def merge_into_dataset(new_items, master_path, index_en_path, index_bn_path):
    """Merge new food items into the existing dataset."""
    with open(master_path, 'r', encoding='utf-8') as f:
        master = json.load(f)
    with open(index_en_path, 'r', encoding='utf-8') as f:
        index_en = json.load(f)
    with open(index_bn_path, 'r', encoding='utf-8') as f:
        index_bn = json.load(f)

    # Build set of existing English names (lowercase) to avoid duplicates
    existing_en = {item['en'].lower().strip() for item in master}
    max_id = max(item['id'] for item in master)

    added = 0
    for code, item in new_items:
        en_lower = item['en'].lower().strip()
        # Skip if duplicate
        if en_lower in existing_en:
            continue
        max_id += 1
        item['id'] = max_id
        master.append(item)
        existing_en.add(en_lower)
        added += 1
        print(f"  + [{max_id}] {item['en']} / {item['bn']}")

    print(f"\nAdded {added} new food items. Total: {len(master)}")

    # Rebuild indexes
    # index_en: sorted list of {id, en, bn, k}
    # index_bn: sorted list of {id, en, bn, k}
    if added > 0:
        # Regenerate full index arrays
        new_index_en = sorted(
            [{'id': it['id'], 'en': it['en'], 'bn': it['bn'], 'k': it['k']} for it in master],
            key=lambda x: x['en'].lower()
        )
        new_index_bn = sorted(
            [{'id': it['id'], 'en': it['en'], 'bn': it['bn'], 'k': it['k']} for it in master],
            key=lambda x: x['bn']
        )

        with open(master_path, 'w', encoding='utf-8') as f:
            json.dump(master, f, ensure_ascii=False, separators=(',', ':'))
        with open(index_en_path, 'w', encoding='utf-8') as f:
            json.dump(new_index_en, f, ensure_ascii=False, separators=(',', ':'))
        with open(index_bn_path, 'w', encoding='utf-8') as f:
            json.dump(new_index_bn, f, ensure_ascii=False, separators=(',', ':'))
        print("Dataset files updated.")

    return added


if __name__ == '__main__':
    prox, mins, vits, en_names, bn_names = extract_all(PDF_PATH)
    items = build_food_items(prox, mins, vits, en_names, bn_names)
    print(f"\nTotal extractable items from FCT: {len(items)}")

    print("\nSample items:")
    for code, item in items[:5]:
        print(f"  {code}: {item['en']} / {item['bn']} — {item['k']} kcal")

    print("\nMerging into dataset...")
    added = merge_into_dataset(items, MASTER_PATH, INDEX_EN_PATH, INDEX_BN_PATH)
    print(f"\nDone. {added} items added.")
