"""
normalize_bn_v6_6.py — Context-aware Bengali normalization (v6_5 → v6_6)

Rules applied only when the English name confirms the intent:
  A  Whole       → ওহোলে  → হোল
  B  Vegetarian  → ভেগেতারিান → ভেজিটেরিয়ান
  C  Smoothie    → সমুথিে → স্মুদি
  D  Pulse       → পুলসে  → ডাল          (already 0 hits from v6_4)
  E  Molasses    → ামযলাসে → মোলাসেস     (already 0 hits from v6_4)

Never performs global string replacement — every record is checked against
its English name before any Bengali text is modified.
"""

import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATA_DIR = Path("assets/data")
IN_FILE  = DATA_DIR / "food_master_v6_5.json"
OUT_FOOD = DATA_DIR / "food_master_v6_6.json"
OUT_EN   = DATA_DIR / "index_en_v6_6.json"
OUT_BN   = DATA_DIR / "index_bn_v6_6.json"
OUT_CAND = DATA_DIR / "bn_normalization_candidates.json"
OUT_MR   = DATA_DIR / "bn_manual_review.json"
OUT_RPT  = DATA_DIR / "bn_normalization_report.json"

# ── Rule table ────────────────────────────────────────────────────────────────
# Each rule: (en_keyword, bn_pattern, bn_replacement, confidence, rule_id)
RULES = [
    ("whole",       "ওহোলে",      "হোল",          99, "A"),
    ("vegetarian",  "ভেগেতারিান", "ভেজিটেরিয়ান", 99, "B"),
    ("smoothie",    "সমুথিে",     "স্মুদি",        99, "C"),
    ("pulse",       "পুলসে",      "ডাল",           97, "D"),
    ("molasses",    "ামযলাসে",    "মোলাসেস",       99, "E"),
]

CONFIDENCE_THRESHOLD = 95   # below this → manual review, no auto-fix


# ── Index builders ────────────────────────────────────────────────────────────

def tokenize_en(text: str) -> list[str]:
    parts = re.sub(r"[^a-z0-9\s]", " ", text.lower()).split()
    return [p for p in parts if len(p) >= 2]

def tokenize_bn(text: str) -> list[str]:
    if not text:
        return []
    return [w[:2] for w in re.split(r"[\s,/\-\.।]+", text) if len(w) >= 2]

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


# ── Unicode validation ────────────────────────────────────────────────────────

def is_bengali(ch: str) -> bool:
    return 0x0980 <= ord(ch) <= 0x09FF

def validate_bn(text: str) -> list[str]:
    issues = []
    # leading combining vowel sign
    if text and unicodedata.category(text[0]) in ("Mc", "Mn"):
        issues.append("leading_vowel_sign")
    # consecutive identical codepoints (OCR doubling)
    for i in range(len(text) - 1):
        if text[i] == text[i + 1] and is_bengali(text[i]):
            issues.append(f"doubled_char_{text[i]}_at_{i}")
    # look for residual ASCII alpha inside bengali string
    if any(c.isascii() and c.isalpha() for c in text if is_bengali(text[0])):
        issues.append("ascii_in_bengali")
    return issues


# ── Phase 1 — find candidates ─────────────────────────────────────────────────

def find_candidates(records: list[dict]) -> list[dict]:
    patterns = [r[1] for r in RULES]
    cands = []
    for r in records:
        bn = r.get("bn") or ""
        matched = [pat for pat in patterns if pat in bn]
        if matched:
            cands.append({
                "id": r["id"],
                "en": r.get("en", ""),
                "bn": bn,
                "patterns_found": matched,
            })
    return cands


# ── Phase 2 — context-aware replacement ──────────────────────────────────────

def apply_rules(record: dict) -> tuple[str, list[dict], list[dict]]:
    """Return (new_bn, applied_fixes, manual_review_items)."""
    en = record.get("en", "").lower()
    bn = record.get("bn") or ""
    applied = []
    manual  = []

    for en_kw, bn_pat, bn_rep, conf, rule_id in RULES:
        if bn_pat not in bn:
            continue
        if en_kw not in en:
            # Pattern present but English keyword absent — flag manual review
            manual.append({
                "id": record["id"], "en": record.get("en"), "bn": bn,
                "rule": rule_id, "bn_pattern": bn_pat, "bn_replacement": bn_rep,
                "reason": f"bn contains '{bn_pat}' but en does not contain '{en_kw}'",
                "confidence": 40,
            })
            continue
        if conf < CONFIDENCE_THRESHOLD:
            manual.append({
                "id": record["id"], "en": record.get("en"), "bn": bn,
                "rule": rule_id, "bn_pattern": bn_pat, "bn_replacement": bn_rep,
                "reason": f"confidence {conf} < threshold {CONFIDENCE_THRESHOLD}",
                "confidence": conf,
            })
            continue
        bn = bn.replace(bn_pat, bn_rep)
        applied.append({
            "rule": rule_id, "replaced": bn_pat, "with": bn_rep, "confidence": conf,
        })

    return bn, applied, manual


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    records: list[dict] = json.loads(IN_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(records)} records")

    # Phase 1
    candidates = find_candidates(records)
    OUT_CAND.write_text(json.dumps(candidates, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\nPhase 1 — candidates found: {len(candidates)}")
    for c in candidates:
        print(f"  [{c['id']:4d}] {c['en']:<46} bn={c['bn']}")
        print(f"         patterns: {c['patterns_found']}")

    # Phase 2 + 3
    fix_log    = []
    manual_log = []
    val_issues = []

    for r in records:
        bn_orig = r.get("bn") or ""
        bn_new, applied, manual = apply_rules(r)
        if applied:
            r["bn"] = bn_new
            fix_log.append({
                "id": r["id"], "en": r.get("en"),
                "before": bn_orig, "after": bn_new,
                "fixes": applied,
            })
        manual_log.extend(manual)

        # Phase 3 — validate result
        if bn_new:
            issues = validate_bn(bn_new)
            if issues:
                val_issues.append({"id": r["id"], "en": r.get("en"),
                                   "bn": bn_new, "issues": issues})

    print(f"\nPhase 2 — records modified: {len(fix_log)}")
    print(f"Phase 3 — validation issues: {len(val_issues)}")
    for v in val_issues:
        print(f"  [{v['id']:4d}] {v['en']}: {v['issues']}")

    print(f"\nPhase 5 — manual review items: {len(manual_log)}")
    OUT_MR.write_text(json.dumps(manual_log, ensure_ascii=False, indent=2),
                      encoding="utf-8")

    # Detail log
    print("\n--- Applied fixes ---")
    for entry in fix_log:
        print(f"  [{entry['id']:4d}] {entry['en']}")
        print(f"         before: {entry['before']}")
        print(f"         after:  {entry['after']}")
        for fx in entry["fixes"]:
            print(f"         Rule {fx['rule']}: '{fx['replaced']}' -> '{fx['with']}' (conf={fx['confidence']})")

    # Phase 4 — rebuild indexes
    idx_en = rebuild_en_index(records)
    idx_bn = rebuild_bn_index(records)

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

    report = {
        "summary": {
            "records_scanned": len(records),
            "candidates_found": len(candidates),
            "records_modified": len(fix_log),
            "manual_review": len(manual_log),
            "validation_issues": len(val_issues),
            "en_index_tokens": len(idx_en),
            "en_index_orphans": en_orphans,
            "bn_index_tokens": len(idx_bn),
            "bn_index_orphans": bn_orphans,
        },
        "fixes": fix_log,
        "validation_issues": val_issues,
    }
    OUT_RPT.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                       encoding="utf-8")

    print(f"\nPhase 4 — EN index: {len(idx_en)} tokens, {en_orphans} orphans")
    print(f"           BN index: {len(idx_bn)} tokens, {bn_orphans} orphans")
    print(f"\nSaved: {OUT_FOOD.name} ({len(records)} items)")
    print(f"Saved: {OUT_EN.name}")
    print(f"Saved: {OUT_BN.name}")
    print(f"Saved: {OUT_CAND.name} ({len(candidates)} items)")
    print(f"Saved: {OUT_MR.name} ({len(manual_log)} items)")
    print(f"Saved: {OUT_RPT.name}")


if __name__ == "__main__":
    main()
