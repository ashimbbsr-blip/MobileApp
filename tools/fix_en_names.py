"""
Fix English food names in the bd_fct entries:
1. Strip Bengali transliteration words appended to English names
2. Remove garbled/invalid entries
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

MASTER   = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v5_3.json'
INDEX_EN = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_en_v5_3.json'
INDEX_BN = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_bn_v5_3.json'

# Known Bengali transliteration words that may be appended to English names
BN_TRANS_WORDS = {
    'jaab', 'gota', 'bhutta', 'atta', 'shukna', 'kaon', 'cheena', 'bajra',
    'popcorn', 'chira', 'veja', 'muri', 'khoi', 'sooji', 'jowar', 'semai',
    'khichuri', 'ruti', 'pawruti', 'maida', 'gom', 'biscuit', 'misti',
    'bonruti', 'plain', 'cholar', 'mashkalai', 'maskalai', 'mung', 'mungkalai',
    'khesari', 'mosur', 'motor', 'arhar', 'soyabean', 'gari', 'chola',
    'data', 'shim', 'beet', 'begun', 'makhon', 'badhakopi', 'gajor', 'fulkopi',
    'kancha', 'borboti', 'shosa', 'sajna', 'rosun', 'chalkumra', 'korola',
    'lau', 'potol', 'jhinga', 'chichinga', 'dhundul', 'kakrol', 'dheros',
    'piaj', 'pepe', 'motorshuti', 'mistikumra', 'mula', 'tomato', 'paka',
    'shalgom', 'bok', 'malancha', 'kanta', 'lal', 'sobuj', 'chukai',
    'bat', 'kalo', 'shobuj', 'dima', 'dheki', 'methi', 'pui', 'pat',
    'notay', 'palong', 'misti', 'helencha', 'kolmee', 'kochur', 'mukhi',
    'dudh', 'kochu', 'ole', 'mann', 'diamond', 'bon', 'alu', 'surjomukhi',
    'hizlee', 'chilgoza', 'narikel', 'china', 'tisi', 'poddo', 'sarisha',
    'pesta', 'mistikumrar', 'til', 'akhrot', 'tejpata', 'elach', 'darchini',
    'labongo', 'dhone', 'dhonia', 'jira', 'mauri', 'ada', 'thankuni',
    'lebur', 'jayitri', 'jayfol', 'golmorich', 'posto', 'holud', 'apel',
    'nashpati', 'kola', 'sagar', 'madar', 'nona', 'kamranga', 'atafol',
    'khorma', 'khejur', 'kodbel', 'amloki', 'dumur', 'angur', 'halka',
    'peyara', 'bivinno', 'amra', 'kalojam', 'jamrul', 'golapjam', 'boroi',
    'lebu', 'kagoji', 'mushambee', 'lichu', 'aam', 'fazli', 'langra',
    'futi', 'komola', 'malta', 'taal', 'gab', 'anaros', 'joldugee',
    'bedana', 'zambura', 'tetul', 'tarmuz', 'bel', 'fesha', 'shutki',
    'teli', 'sorpunti', 'bata', 'boal', 'foli', 'kalbaush', 'bacha',
    'pabda', 'katla', 'koi', 'chital', 'poa', 'kachki', 'kajuli',
    'gulsha', 'guizza', 'vetkee', 'bele', 'ilish', 'chapila', 'gonia',
    'ayre', 'chela', 'fulchela', 'narkeli', 'mola', 'mrigal', 'jhinuk',
    'pangas', 'rupchanda', 'rui', 'nodir', 'tuna', 'magur', 'shing',
    'tatkini', 'shol', 'telapia', 'gorur', 'koliza', 'kima', 'mohisher',
    'murgir', 'hasher', 'khaseer', 'verar', 'shukorer', 'haaree', 'kabab',
    'dim', 'farm', 'deshi', 'ghol', 'poneer', 'doi', 'mohiser', 'chagoler',
    'shaldudh', 'mayer', 'payesh', 'makhon', 'tular', 'kod', 'ghee',
    'gorur', 'dalda', 'bonoshpati', 'margarine', 'mayonnaise', 'sorishar',
    'palm', 'tel', 'soybean', 'daber', 'coffee', 'likar', 'cha', 'pata',
    'baking', 'pan', 'modhu', 'gur', 'akh', 'nolen', 'chini', 'sada',
    'dudh', 'akher', 'ross', 'komol', 'paniyo', 'powder', 'sabarang',
    'simei', 'kochu', 'shak', 'lobon', 'chara', 'siddha',
}

# Standard English food name words (these should NOT be stripped)
EN_STANDARD = {
    'raw', 'dried', 'boiled', 'fried', 'cooked', 'fresh', 'frozen',
    'whole', 'grain', 'flour', 'seeds', 'leaves', 'root', 'stem',
    'skin', 'peeled', 'split', 'dehulled', 'milled', 'polished',
    'unripe', 'ripe', 'mature', 'immature', 'green', 'red', 'yellow',
    'white', 'black', 'brown', 'dark', 'light', 'pale', 'orange',
    'without', 'with', 'included', 'excluded', 'boneless', 'bones',
    'lean', 'fat', 'salted', 'unsweetened', 'sweetened', 'skimmed',
    'powdered', 'powder', 'ground', 'whole-grain', 'cob', 'pod',
    'pulp', 'kernel', 'flesh', 'milk', 'cream', 'butter', 'oil',
    'mixed', 'species', 'combined', 'breeds', 'farmed', 'native',
    'female', 'male', 'yolk', 'white', 'whole', 'soft', 'hard',
    'infusion', 'juice', 'extract', 'flakes', 'puffed', 'popped',
    'parboiled', 'sunned', 'refined', 'unrefined', 'fortified',
    'defatted', 'desiccated', 'liquid', 'solid', 'sliced', 'mashed',
    'paste', 'sauce', 'curry', 'stew', 'fry', 'baked', 'roasted',
    'steamed', 'broiled', 'grilled', 'smoked', 'canned', 'fermented',
    'salt', 'added', 'without', 'salt', 'free', 'low', 'high',
    'medium', 'large', 'small', 'giant', 'dwarf', 'wild', 'cultivated',
    'domestic', 'imported', 'local', 'hybrid', 'variety', 'type',
    'eyes', 'fins', 'head', 'tail', 'fillet', 'steak', 'chop',
    'mince', 'liver', 'heart', 'kidney', 'breast', 'leg', 'wing',
    'thigh', 'neck', 'back', 'rib', 'loin', 'shoulder', 'rump',
}


def looks_like_transliteration(word):
    """Check if a word looks like Bengali transliteration (not standard English)."""
    w = word.lower().strip('*,./-()')
    if not w:
        return False
    if w in EN_STANDARD:
        return False
    if w in BN_TRANS_WORDS:
        return True
    # Single capitalized word that's not a standard English food term
    if word[0].isupper() and w not in EN_STANDARD and len(w) > 2:
        # Check if it looks more like a transliteration (no common English food suffixes)
        if not any(w.endswith(suf) for suf in ['ed', 'ing', 'er', 'est', 'ive', 'al', 'ous', 'ish']):
            return True
    return False


def clean_en_name(name):
    """Remove Bengali transliteration words from the end of English food names."""
    name = name.strip().rstrip('*').strip()

    # Remove known transliteration patterns at the end
    # Split into words and find where the transliteration starts
    words = name.split()
    if not words:
        return name

    # Check from the end: remove consecutive transliteration words
    keep_up_to = len(words)
    for i in range(len(words) - 1, -1, -1):
        w = words[i].strip('*,./-()')
        if looks_like_transliteration(words[i]):
            keep_up_to = i
        else:
            break

    cleaned = ' '.join(words[:keep_up_to]).strip().rstrip('*,').strip()
    return cleaned if cleaned else name


def is_valid_food_name(name):
    """Check if the name looks like a real food name."""
    if len(name) < 4:
        return False
    if re.match(r'^\d', name):
        return False
    # Should contain at least one alphabet character
    if not re.search(r'[a-zA-Z]{3,}', name):
        return False
    return True


def main():
    with open(MASTER, 'r', encoding='utf-8') as f:
        master = json.load(f)

    # Existing non-bd_fct items for duplicate checking
    existing_en = {item['en'].lower().strip() for item in master if item.get('src') != 'bd_fct'}

    cleaned = 0
    removed = 0
    kept = []

    for item in master:
        if item.get('src') != 'bd_fct':
            kept.append(item)
            continue

        # Clean English name
        old_en = item['en']
        new_en = clean_en_name(old_en)

        if not is_valid_food_name(new_en):
            removed += 1
            print(f"  REMOVE: '{old_en}' -> '{new_en}'")
            continue

        # Check for duplicates after cleaning
        if new_en.lower().strip() in existing_en:
            removed += 1
            print(f"  DUP: '{new_en}'")
            continue

        if new_en != old_en:
            cleaned += 1
            print(f"  CLEAN: '{old_en}' -> '{new_en}'")
            item['en'] = new_en

        kept.append(item)
        existing_en.add(new_en.lower().strip())

    print(f"\nCleaned {cleaned} names, removed {removed} entries.")
    print(f"Remaining: {len(kept)} (bd_fct: {sum(1 for i in kept if i.get('src')=='bd_fct')})")

    # Rebuild indexes
    new_index_en = sorted(
        [{'id': it['id'], 'en': it['en'], 'bn': it['bn'], 'k': it['k']} for it in kept],
        key=lambda x: x['en'].lower()
    )
    new_index_bn = sorted(
        [{'id': it['id'], 'en': it['en'], 'bn': it['bn'], 'k': it['k']} for it in kept],
        key=lambda x: x['bn']
    )

    with open(MASTER, 'w', encoding='utf-8') as f:
        json.dump(kept, f, ensure_ascii=False, separators=(',', ':'))
    with open(INDEX_EN, 'w', encoding='utf-8') as f:
        json.dump(new_index_en, f, ensure_ascii=False, separators=(',', ':'))
    with open(INDEX_BN, 'w', encoding='utf-8') as f:
        json.dump(new_index_bn, f, ensure_ascii=False, separators=(',', ':'))

    print("Files updated.")


if __name__ == '__main__':
    main()
