"""Audit and fix remaining issues in bd_fct entries."""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

MASTER   = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\food_master_v5_3.json'
INDEX_EN = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_en_v5_3.json'
INDEX_BN = r'C:\Users\ideapad\IdeaProjects\MobileApp\assets\data\index_bn_v5_3.json'

# Manual overrides for specific entries: en (current stored value) -> (correct_en, correct_bn)
OVERRIDES = {
    'Barley, whole-grain, raw':             ('Barley, whole-grain, raw', 'যব, গোটা শস্য, কাঁচা'),
    'Rice flaked':                          ('Rice flakes, white grain, raw', 'চিড়া'),
    'Chal':                                 ('Rice, parboiled, milled, raw', 'চাল, সিদ্ধ, ঢেঁকিছাটা'),
    'Beef handi':                           ('Beef handi kabab', 'হাঁড়ি কাবাব (গরু)'),
    'Milk, cow, whole fat (pasteurized':    ('Milk, cow, whole fat (pasteurized, UTH)', 'গরুর দুধ, পাস্তুরিত'),
    'Sesame oil Tiler':                     ('Sesame oil', 'তিলের তেল'),
    'Dudh Tea infusion (with sugar and milk powder': ('Tea, milk tea (with sugar and milk powder)', 'দুধ চা (চিনি ও গুঁড়া দুধ সহ)'),
    'Jaggery/Panela, date palm Gur, Jaggery/Panela, date': ('Jaggery/Panela, date palm', 'খেজুর গুড়'),
    'Jagggery liquid, date palm Nolen Jagggery liquid, date': ('Jaggery, liquid, date palm', 'নলেন গুড়'),
    'Sweet potato leaves, SP4, dark green, mature': ('Sweet potato leaves, SP4, dark green, mature, raw', 'মিষ্টি আলুর শাক (SP4)'),
    'Sweet potato leaves, SP7, dark green, mature': ('Sweet potato leaves, SP7, dark green, mature, raw', 'মিষ্টি আলুর শাক (SP7)'),
    'Sweet potato leaves, SP8, light green, mature': ('Sweet potato leaves, SP8, light green, mature, raw', 'মিষ্টি আলুর শাক (SP8)'),
    'Lady’s finger-tomato bhuna':      ('Lady\'s finger-tomato bhuna', 'ঢ্যাঁড়শ-টমেটো ভুনা'),
    'Plain pulao':                          ('Plain pulao', 'সাদা পোলাও'),
    'Coffee, Coffee infusion (instant with sugar and milk': ('Coffee, instant, with sugar and milk', 'তাৎক্ষণিক কফি (চিনি ও দুধ সহ)'),
    'Tea, infusion (with sugar) Likar Tea, infusion (with sugar)': ('Tea, infusion (with sugar)', 'লিকার চা (চিনিসহ)'),
    'Sugar cane Juice Akher Sugar cane Juice': ('Sugar cane juice', 'আখের রস'),
    'Soft drinks, carbonated Komol Soft drinks, carbonated': ('Soft drinks, carbonated', 'কোমল পানীয়'),
    'Soya milk (not sweetened) Soybean Soya milk (not sweetened)': ('Soya milk (not sweetened)', 'সয়াবিনের দুধ'),
    'Coffee, powder Coffee Coffee, powder': ('Coffee, powder', 'কফি পাউডার'),
    'Coconut water Daber Coconut water': ('Coconut water', 'ডাবের পানি'),
    'Tea, powder Cha Tea, powder': ('Tea, powder', 'চা পাতা'),
    'Baking powder Baking Baking powder': ('Baking powder', 'বেকিং পাউডার'),
    'Betel leaves, raw Pan Betel leaves, raw': ('Betel leaves, raw', 'পান পাতা'),
    'Honey Modhu Honey': ('Honey', 'মধু'),
    'Jaggery, sugarcane, solid Gur, Jaggery, sugarcane, solid': ('Jaggery, sugarcane, solid', 'গুড়, আখ'),
    'Sugar, white Chini, Sugar, white': ('Sugar, white', 'চিনি, সাদা'),
    'Nutmeg, dried Jayfol Nutmeg, dried': ('Nutmeg, dried', 'জয়ফল'),
    'Poppy seeds Posto Poppy seeds': ('Poppy seeds', 'পোস্তদানা'),
    'Turmeric, dried Holud Turmeric, dried': ('Turmeric, dried', 'হলুদ'),
    'Spearmint leaves, fresh Pudina Spearmint leaves, fresh': ('Spearmint leaves, fresh', 'পুদিনা পাতা'),
    'Pepper, black Golmorich Pepper, black': ('Pepper, black', 'গোলমরিচ'),
}

# Entries to remove (garbled/invalid entries that have no fix)
TO_REMOVE = {
    'Chal,', 'Bhat,', 'Mung', 'Chola', 'Cholar', 'Dheros', 'Begun',
    'Lal', 'Notay', 'Koi,', 'Chital,', 'Poa,', 'Kachki,', 'Taal,',
    'Dewa', 'Bangee, paka', 'Barb, Pool barb, eyes included, raw',
    'Anchovy, Gold spotted grebadier, raw',
    'Indian threadfin, without bones, raw',
    'Prawn, Birma river prawn, raw',
    'Prawn, Giant river prawn, raw',
    'Prawn, Giant tiger prawn, raw',
    'Prawn, Hairy river prawn, raw',
    'Prawn, Indian white prawn, raw',
    'Mullet, Gold spot, raw',
    'Pomfret, Silver, dried',
    'Pomfret, Silver, without bones, raw',
    'Giant sea perch, whole, dried',
    'Silver carp, without bones, raw Silver',
    'Minnow, Finescale razorbelly, dried',
    'Barb, Olive, raw',
    'Kakila,', 'Payesh',  # Payesh already in existing dataset
    'Frog, legs, raw',
    'Pigeon meat, raw',
    'Egg, chicken, farmed, boiled* (without salt)',  # same as native boiled
    'Kuria labeo, without bones, raw',
    'Palmyra palm, cotyledon, raw',
}


def main():
    with open(MASTER, 'r', encoding='utf-8') as f:
        master = json.load(f)

    existing_en = {item['en'].lower().strip() for item in master if item.get('src') != 'bd_fct'}
    kept = []
    fixed = 0
    removed = 0

    for item in master:
        if item.get('src') != 'bd_fct':
            kept.append(item)
            continue

        en = item['en']

        # Remove garbled entries
        if en in TO_REMOVE or en.rstrip('*').strip() in TO_REMOVE:
            removed += 1
            print(f"  REMOVE: '{en}'")
            continue

        # Check override
        if en in OVERRIDES:
            new_en, new_bn = OVERRIDES[en]
            if new_en.lower().strip() in existing_en:
                removed += 1
                print(f"  DUP OVERRIDE: '{en}' -> '{new_en}'")
                continue
            item['en'] = new_en
            item['bn'] = new_bn
            fixed += 1
            print(f"  FIX: '{en}' -> '{new_en}' / '{new_bn}'")
            existing_en.add(new_en.lower().strip())

        kept.append(item)

    print(f"\nFixed: {fixed}, Removed: {removed}")
    print(f"Remaining bd_fct: {sum(1 for i in kept if i.get('src')=='bd_fct')}")
    print(f"Total: {len(kept)}")

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
