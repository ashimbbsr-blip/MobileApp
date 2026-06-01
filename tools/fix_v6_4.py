"""
fix_v6_4.py — Bengali machine-transliteration normalization
Input:  assets/data/food_master_v6_3.json
Output: assets/data/food_master_v6_4.json
        assets/data/index_en_v6_4.json
        assets/data/index_bn_v6_4.json

Fixes systematic machine-transliteration errors identified in v6.3 audit.
No nutrition values or IDs are changed.
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path("assets/data")
IN_FILE  = DATA_DIR / "food_master_v6_3.json"
OUT_FOOD = DATA_DIR / "food_master_v6_4.json"
OUT_EN   = DATA_DIR / "index_en_v6_4.json"
OUT_BN   = DATA_DIR / "index_bn_v6_4.json"

# ─── Ordered fix table ────────────────────────────────────────────────────────
# Longer / more-specific patterns FIRST to prevent partial collisions.
ORDERED_FIXES = [
    # Slash-form canonical contractions
    ("বিরযানি/বিরিযানি",   "বিরিয়ানি"),        # biryani
    ("খিচদি/খিচরি",        "খিচুড়ি"),           # khichdi/khichri

    # Long multi-char patterns (most specific)
    ("ফেততুককিনে",         "ফেতুচিনি"),          # fettuccine
    ("কাসসেরোলে",          "ক্যাসারোল"),         # casserole
    ("সপাঘেততি",           "স্প্যাগেটি"),        # spaghetti
    ("কোনসোমমে",           "কনসোমে"),            # consommé
    ("মিনকেদ",             "কিমা করা"),          # minced
    ("ফলাততেনেদ",          "চেপ্টা"),            # flattened
    ("নামাক পারাস",        "নামক পারা"),          # namak paras
    ("জালফরেজি",           "জালফ্রেজি"),         # jalfrezi
    ("চিককপোস",            "ছোলা"),              # chickpeas (before standalone পো)
    ("বরিততলে",            "ব্রিটল"),            # brittle
    ("ামযলাসে",            "অ্যামিলেজ"),         # amylase (leading diacritic artifact)
    ("ডালিযা",             "ডালিয়া"),           # daliya
    ("পরেমিক্স",           "প্রিমিক্স"),         # premix
    ("লেনতিলস",            "মসুর"),              # lentils
    ("লাসাগনে",            "লাসাগনা"),           # lasagne

    # User-specified patterns
    ("ভেগেতাবলেস",         "সবজি"),              # vegetables (plural form first)
    ("ভেগেতাবলে",          "সবজি"),              # vegetable
    ("সতোকক",              "স্টক"),              # stock — MUST precede সতোক (steak)
    ("কুতলেত",             "কাটলেট"),            # cutlet
    ("পাততিেস",            "প্যাটিস"),           # patties
    ("সোযাবোন",            "সয়াবিন"),           # soyabean
    ("মুথিাস",             "মুঠিয়া"),            # muthias
    ("তিককি",              "টিক্কি"),            # tikki
    ("সতোক",               "স্টেক"),             # steak (after stock fixed above)
    ("বুরগের",             "বার্গার"),           # burger

    # Related patterns found in sweep
    ("পুলসে",              "ডাল"),               # pulse
    ("নামকইন",             "নামকিন"),            # namkeen
    ("চুনকস",              "চাংক্স"),            # chunks
    ("সেসামে",             "তিল"),               # sesame → proper Bengali
    ("কেরোল",              "সিরিয়াল"),          # cereal
    ("চাননা",              "চানা"),              # channa (double-ন)
    ("শামমি",              "শামি"),              # shammi (double-ম)
    ("চিললি",              "চিলি"),              # chilli (double-ল)
    ("খাততা",              "খাট্টা"),            # khatta (double-ত)
    ("সোযা",               "সয়া"),              # soya (after সোযাবোন fixed)
    ("সিখ ",               "শিখ "),              # seekh (trailing space guards against edge)
    ("মিনত ",              "পুদিনা "),           # mint (trailing space guards "মিনতাদে") → proper Bengali
    ("কিনগ",               "কিং"),               # king (ala king)
    ("সতির",               "স্টির"),             # stir (stir fry)
    ("মোত ",               "মাংস "),             # meat (trailing space avoids মোতি)
    ("দিপ",                "ডিপ"),               # dip
    ("সউর",                "টক"),                # sour → proper Bengali
    ("বেক ",               "বেকড "),             # baked (trailing space avoids edge)
]


def apply_fixes(text: str) -> tuple[str, list[tuple[str, str]]]:
    applied = []
    for old, new in ORDERED_FIXES:
        if old in text:
            text = text.replace(old, new)
            applied.append((old, new))
    return text, applied


# ─── Index builders ───────────────────────────────────────────────────────────

def tokenize_en(text: str) -> list[str]:
    parts = re.split(r"[\s,/\-\.।]+", text.lower())
    return [p for p in parts if len(p) >= 2]


def tokenize_bn(text: str) -> list[str]:
    if not text:
        return []
    tokens = []
    for word in re.split(r"[\s,/\-\.।]+", text):
        if len(word) >= 2:
            tokens.append(word[:2])
    return tokens


def rebuild_en_index(records: list[dict]) -> dict:
    idx: dict[str, list[int]] = defaultdict(list)
    for r in records:
        rid = r["id"]
        kw_raw = r.get("kw") or []
        kw_list = kw_raw if isinstance(kw_raw, list) else [kw_raw]
        for src in [r.get("en", "")] + kw_list:
            for tok in tokenize_en(src):
                for plen in (2, 3):
                    if len(tok) >= plen:
                        key = tok[:plen]
                        if rid not in idx[key]:
                            idx[key].append(rid)
    return dict(idx)


def rebuild_bn_index(records: list[dict]) -> dict:
    idx: dict[str, list[int]] = defaultdict(list)
    for r in records:
        rid = r["id"]
        for tok in tokenize_bn(r.get("bn", "")):
            if rid not in idx[tok]:
                idx[tok].append(rid)
    return dict(idx)


# ─── Main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    records: list[dict] = json.loads(IN_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(records)} records")

    fix_log: list[dict] = []
    total_repairs = 0

    for r in records:
        bn = r.get("bn") or ""
        if not bn:
            continue
        fixed, applied = apply_fixes(bn)
        if applied:
            fix_log.append({
                "id": r["id"],
                "en": r.get("en", ""),
                "before": bn,
                "after":  fixed,
                "patterns": [(o, n) for o, n in applied],
            })
            r["bn"] = fixed
            total_repairs += len(applied)

    print(f"\nRecords changed: {len(fix_log)}")
    print(f"Total pattern applications: {total_repairs}")

    # Print every change for review
    print("\n--- Changes ---")
    for entry in fix_log:
        print(f"  [{entry['id']:4d}] {entry['en']}")
        print(f"        before: {entry['before']}")
        print(f"        after:  {entry['after']}")
        for old, new in entry['patterns']:
            print(f"          {old} -> {new}")

    # Pattern summary
    counts: dict[str, int] = defaultdict(int)
    for entry in fix_log:
        for old, _ in entry["patterns"]:
            counts[old] += 1
    print("\n--- Pattern hit counts ---")
    for old, cnt in sorted(counts.items(), key=lambda x: -x[1]):
        new = next(n for o, n in ORDERED_FIXES if o == old)
        print(f"  {cnt:3d}x  {old} -> {new}")

    # Rebuild indexes
    idx_en = rebuild_en_index(records)
    idx_bn = rebuild_bn_index(records)

    # Orphan check
    all_ids = {r["id"] for r in records}
    en_orphans = sum(1 for ids in idx_en.values() for i in ids if i not in all_ids)
    bn_orphans = sum(1 for ids in idx_bn.values() for i in ids if i not in all_ids)

    # Save
    OUT_FOOD.write_text(json.dumps(records, ensure_ascii=False, separators=(",", ":")),
                        encoding="utf-8")
    OUT_EN.write_text(json.dumps(idx_en, ensure_ascii=False, separators=(",", ":")),
                      encoding="utf-8")
    OUT_BN.write_text(json.dumps(idx_bn, ensure_ascii=False, separators=(",", ":")),
                      encoding="utf-8")

    # Save fix log
    log_path = DATA_DIR / "bn_fix_v6_4_report.json"
    log_path.write_text(json.dumps(fix_log, ensure_ascii=False, indent=2),
                        encoding="utf-8")

    print(f"\nSaved {OUT_FOOD.name}: {len(records)} items")
    print(f"Saved {OUT_EN.name}: {len(idx_en)} tokens, {en_orphans} orphans")
    print(f"Saved {OUT_BN.name}: {len(idx_bn)} tokens, {bn_orphans} orphans")
    print(f"Saved bn_fix_v6_4_report.json: {len(fix_log)} changed records")


if __name__ == "__main__":
    main()
