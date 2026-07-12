"""
Food Dataset Canonicalization & QA Pipeline v1.0
=================================================
Run : py tools/canonicalize_pipeline.py
Input : assets/data/food_master_v10.json   (5 000 records)
Outputs: tools/output/
  canonical_foods.json   – one record per canonical food group
  food_variants.json     – variant rows linked to canonical ids
  qa_report.json         – structured issue list (severity / field / message)
  normalization_log.json – every transformation applied to each record
  qa_summary.csv         – compact issue counts by type and severity

Side-effect:
  Patches food_master_v10.json in-place:
    • merges vit_c → vc
    • promotes na/sod → sod (sodium)
    • fills missing micro fields with 0.0
    • fills missing canonical / quality_score
    • recomputes blanket-40 quality scores using data-richness formula
"""

from __future__ import annotations
import json, re, unicodedata, csv, pathlib, hashlib
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

# ── paths ─────────────────────────────────────────────────────────────────────
ROOT   = pathlib.Path(__file__).parent.parent
SRC    = ROOT / "assets" / "data" / "food_master_v10.json"
OUTDIR = pathlib.Path(__file__).parent / "output"

# ── constants ─────────────────────────────────────────────────────────────────
REQUIRED_FIELDS  = {"id", "en", "bn", "cat", "k", "p", "c", "f"}
MICRO_FIELDS     = {"ca", "fe", "zn", "mg", "pot", "va", "vc", "vd", "b12", "fi"}
NUMERIC_FIELDS   = {"k", "p", "c", "f", "fi", "ca", "fe", "zn", "mg",
                    "pot", "va", "vc", "vd", "b12", "alc_g"}
MACRO_ENERGY_TOL = 0.25   # 25 % tolerance for kcal vs macro sum
SUSPICIOUS_KCAL  = 900    # per 100 g – flag if higher

# Source trust base (0–100)
SOURCE_TRUST = {
    "indb": 90, "ifct": 90, "icmr_ifct": 90, "usda": 88,
    "fatsecret_usda": 85, "bd_fct": 85, "icmr_2004": 85,
    "ijcmas_2020": 85, "odia": 80, "deutsche_see_ciqual": 80,
    "pizzahut_india": 78, "mcdonalds_india": 78, "kfc_india": 78,
    "subway_us": 78, "dominos_india": 78, "haldiram": 76, "maggi_in": 75,
    "brand": 75, "brand_official": 80, "fatsecret_in": 65,
    "curated_estimate": 60, "user_curated": 50, "local": 45, "": 30,
}
CONFIDENCE_BONUS = {
    "very_high": 10, "high": 5, "medium": 0, "low": -5, "very_low": -10, "": 0,
}

# ── helpers ───────────────────────────────────────────────────────────────────
def _slug(text: str) -> str:
    """Lowercase, strip accents, collapse non-alphanumeric to single space."""
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[^a-z0-9\s]", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()

def _canon_name(en: str) -> str:
    """Strip parenthetical qualifiers then slug the first 4 words."""
    en = re.sub(r"\(.*?\)", "", en)
    words = _slug(en).split()[:4]
    return " ".join(words)

def _canon_key(en: str, cat: str) -> str:
    return f"{_canon_name(en)}|{cat.lower()}"

def _stable_id(key: str) -> str:
    return hashlib.md5(key.encode()).hexdigest()[:8]

# ── Step 1 – load ─────────────────────────────────────────────────────────────
def load_input() -> list[dict]:
    with SRC.open(encoding="utf-8") as fh:
        return json.load(fh)

# ── Step 2 – parse & schema-normalise ─────────────────────────────────────────
def parse_records(raw: list[dict]) -> tuple[list[dict], list[dict]]:
    """Return (records, log_entries). Mutates records in-place."""
    log: list[dict] = []

    for r in raw:
        rid = r.get("id", "?")

        # ── merge duplicate vitamin C fields ──────────────────────────────────
        if "vit_c" in r:
            if r.get("vc", 0) == 0 and r["vit_c"] > 0:
                r["vc"] = float(r["vit_c"])
                log.append({"id": rid, "action": "merge_vit_c",
                             "detail": f"vit_c={r['vit_c']} promoted to vc"})
            del r["vit_c"]

        # ── normalise sodium: na / sod → sod ─────────────────────────────────
        if "na" in r and "sod" not in r:
            r["sod"] = float(r.pop("na"))
            log.append({"id": rid, "action": "rename_na_to_sod",
                         "detail": f"na renamed to sod={r['sod']}"})
        elif "na" in r:
            del r["na"]   # sod already exists – drop duplicate

        # ── promote servingUnit into s if s is bare numeric ──────────────────
        if "servingUnit" in r:
            s = str(r.get("s", ""))
            if s.isdigit() and r["servingUnit"] in ("g", "ml"):
                r["s"] = f"{s}{r['servingUnit']}"
                log.append({"id": rid, "action": "fix_serving_unit",
                             "detail": f"s={r['s']}"})
            del r["servingUnit"]

        # ── fill missing micronutrient fields with 0.0 ───────────────────────
        for mf in MICRO_FIELDS:
            if mf not in r:
                r[mf] = 0.0
                # only log if not a near-universal gap (vd, b12 are common misses)
                if mf not in ("vd", "b12", "va", "vc", "mg", "pot"):
                    log.append({"id": rid, "action": "fill_default",
                                 "detail": f"{mf}=0.0 (was absent)"})

        # ── fill missing canonical ────────────────────────────────────────────
        if "canonical" not in r:
            r["canonical"] = False

        # ── ensure aliases is a list ─────────────────────────────────────────
        if "aliases" not in r or r["aliases"] is None:
            r["aliases"] = []

        # ── coerce all numeric fields ─────────────────────────────────────────
        for nf in NUMERIC_FIELDS:
            if nf in r:
                try:
                    r[nf] = float(r[nf])
                except (TypeError, ValueError):
                    r[nf] = 0.0
                    log.append({"id": rid, "action": "coerce_numeric",
                                 "detail": f"{nf} coerced to 0.0"})

    return raw, log

# ── Step 3 – text normalisation ───────────────────────────────────────────────
_BN_STRIP = re.compile(r"[​-‏﻿]")   # zero-width + BOM

def normalize_text(records: list[dict], log: list[dict]) -> None:
    for r in records:
        rid = r.get("id", "?")
        # English name
        en_orig = r.get("en", "")
        en_new  = re.sub(r"\s+", " ", en_orig.strip())
        if en_new != en_orig:
            r["en"] = en_new
            log.append({"id": rid, "action": "normalize_en", "detail": repr(en_orig)})

        # Bengali name – strip zero-width chars, double spaces
        bn_orig = r.get("bn", "")
        bn_new  = _BN_STRIP.sub("", re.sub(r"\s+", " ", bn_orig.strip()))
        if bn_new != bn_orig:
            r["bn"] = bn_new
            log.append({"id": rid, "action": "normalize_bn", "detail": repr(bn_orig)})

        # Aliases – deduplicate and strip
        aliases = r.get("aliases", [])
        clean   = list(dict.fromkeys(a.strip() for a in aliases if a.strip()))
        if clean != aliases:
            r["aliases"] = clean

# ── Step 4 – canonical keys ───────────────────────────────────────────────────
def build_canonical_keys(records: list[dict]) -> None:
    for r in records:
        r["_canon_key"]  = _canon_key(r["en"], r.get("cat", ""))
        r["_canon_id"]   = _stable_id(r["_canon_key"])

# ── Step 5 – group variants ───────────────────────────────────────────────────
def group_variants(records: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        groups[r["_canon_key"]].append(r)
    return dict(groups)

# ── Step 6 – trust scoring ────────────────────────────────────────────────────
def _data_richness(r: dict) -> int:
    """0-50 bonus based on how complete the nutrition data is."""
    score = 0
    if r.get("p", 0) >= 0 and r.get("c", 0) >= 0 and r.get("f", 0) >= 0:
        score += 10
    if r.get("fi", 0) > 0:
        score += 5
    if r.get("ca", 0) > 0 and r.get("fe", 0) > 0:
        score += 8
    if r.get("vc", 0) > 0 or r.get("va", 0) > 0:
        score += 8
    if r.get("vc", 0) > 0 and r.get("va", 0) > 0:
        score += 5
    if r.get("s") and str(r["s"]).strip():
        score += 5
    if len(r.get("bn", "")) > 3:
        score += 5
    if r.get("aliases"):
        score += 2
    if r.get("family"):
        score += 2
    return score

def score_trust(records: list[dict], log: list[dict]) -> None:
    for r in records:
        rid  = r.get("id", "?")
        src  = r.get("src", "")
        conf = r.get("nutrition_confidence", "")

        src_base  = SOURCE_TRUST.get(src, 35)
        conf_b    = CONFIDENCE_BONUS.get(conf, 0)
        richness  = _data_richness(r)
        canon_b   = 5 if r.get("canonical") else 0
        trust     = min(100, src_base + conf_b + canon_b + int(richness * 0.3))
        r["_trust_score"] = trust

        # ── recompute quality_score for blanket-40 and missing items ─────────
        qs = r.get("quality_score")
        if qs is None or qs == 40:
            # Data-richness formula
            base  = {
                "indb": 70, "bd_fct": 65, "usda": 68, "icmr_2004": 65,
                "icmr_ifct": 65, "ijcmas_2020": 65,
                "pizzahut_india": 62, "mcdonalds_india": 62, "kfc_india": 62,
                "subway_us": 62, "dominos_india": 62, "haldiram": 60,
                "brand": 58, "brand_official": 62,
                "curated_estimate": 52, "user_curated": 48,
                "local": 45, "": 35,
            }.get(src, 45)
            new_qs = min(90, base + richness)
            old_qs = qs
            r["quality_score"] = new_qs
            log.append({"id": rid, "action": "quality_score_recomputed",
                         "old": old_qs, "new": new_qs,
                         "detail": f"richness={richness} src={src}"})

# ── Step 7 – validate ─────────────────────────────────────────────────────────
@dataclass
class Issue:
    severity: str        # critical / high / medium / low
    issue_type: str
    record_id: Any
    field: str
    message: str
    actual: Any   = None
    expected: Any = None

def validate_rows(records: list[dict], groups: dict[str, list[dict]]) -> list[Issue]:
    issues: list[Issue] = []
    seen_ids: dict[int, list] = defaultdict(list)

    for r in records:
        rid = r.get("id")
        en  = r.get("en", "")

        # ── duplicate ids ──────────────────────────────────────────────────────
        seen_ids[rid].append(en)

        # ── required fields ────────────────────────────────────────────────────
        for rf in REQUIRED_FIELDS:
            if rf not in r or r[rf] is None or r[rf] == "":
                issues.append(Issue("high", "missing_required_field",
                                     rid, rf, f"'{rf}' is missing or empty"))

        # ── invalid numerics ───────────────────────────────────────────────────
        if r.get("k", 0) < 0:
            issues.append(Issue("high", "negative_calories",
                                 rid, "k", f"kcal={r['k']} is negative"))
        if r.get("k", 0) > SUSPICIOUS_KCAL:
            issues.append(Issue("medium", "suspicious_high_calories",
                                 rid, "k", f"kcal={r['k']} >900 per 100g",
                                 actual=r["k"], expected=f"<{SUSPICIOUS_KCAL}"))
        for mf in ("p", "c", "f"):
            if r.get(mf, 0) > 100:
                issues.append(Issue("high", "macro_exceeds_100g",
                                     rid, mf, f"{mf}={r[mf]}g >100g per 100g",
                                     actual=r[mf]))
        for mf in ("p", "c", "f"):
            if r.get(mf, 0) < 0:
                issues.append(Issue("high", "negative_macro",
                                     rid, mf, f"{mf}={r[mf]} is negative"))

        # ── macro-energy consistency ───────────────────────────────────────────
        expected_k = (r.get("p", 0) * 4 + r.get("c", 0) * 4
                      + r.get("f", 0) * 9 + r.get("alc_g", 0) * 7)
        actual_k   = r.get("k", 0)
        if expected_k > 5:
            pct_off = abs(actual_k - expected_k) / expected_k
            if pct_off > MACRO_ENERGY_TOL:
                issues.append(Issue(
                    "medium" if pct_off < 0.50 else "high",
                    "macro_calorie_mismatch",
                    rid, "k",
                    f"Reported {actual_k:.1f} kcal; macros sum to "
                    f"{expected_k:.1f} kcal ({pct_off*100:.0f}% off)",
                    actual=round(actual_k, 1),
                    expected=round(expected_k, 1),
                ))

        # ── suspicious serving size ────────────────────────────────────────────
        s_str = str(r.get("s", ""))
        s_num = re.search(r"(\d+\.?\d*)", s_str)
        if s_num:
            sv = float(s_num.group(1))
            if sv > 2000:
                issues.append(Issue("medium", "suspicious_serving_size",
                                     rid, "s",
                                     f"Serving size '{s_str}' seems very large"))
            if sv == 0:
                issues.append(Issue("low", "zero_serving_size",
                                     rid, "s", "Serving size is 0"))

        # ── empty Bengali name ─────────────────────────────────────────────────
        if not r.get("bn", "").strip():
            issues.append(Issue("medium", "missing_bengali_name",
                                 rid, "bn", "Bengali name is empty"))

        # ── likely mislabelled canonical ──────────────────────────────────────
        if r.get("canonical") and r.get("src") in ("local", "user_curated"):
            qs = r.get("quality_score", 0)
            if qs < 50:
                issues.append(Issue("low", "low_quality_canonical",
                                     rid, "canonical",
                                     f"canonical=True but quality_score={qs} and src={r['src']}"))

    # ── duplicate ids ──────────────────────────────────────────────────────────
    for rid, names in seen_ids.items():
        if len(names) > 1:
            issues.append(Issue("critical", "duplicate_id",
                                 rid, "id",
                                 f"ID {rid} appears {len(names)} times: {names[:3]}"))

    # ── alias collisions (same alias text under different canonical groups) ────
    alias_map: dict[str, set[str]] = defaultdict(set)
    for r in records:
        ck = r["_canon_key"]
        for a in r.get("aliases", []):
            alias_map[a.lower()].add(ck)
    for alias, keys in alias_map.items():
        if len(keys) > 1:
            issues.append(Issue("low", "alias_collision",
                                 None, "aliases",
                                 f"alias '{alias}' maps to {len(keys)} canonical groups"))

    # ── canonical groups with only 1 item that is canonical=False ─────────────
    for key, grp in groups.items():
        canonical_members = [x for x in grp if x.get("canonical")]
        if not canonical_members and len(grp) > 0:
            # pick the highest-trust item and recommend it as canonical
            best = max(grp, key=lambda x: x.get("_trust_score", 0))
            issues.append(Issue("low", "no_canonical_in_group",
                                 best.get("id"), "_canon_key",
                                 f"Group '{key}' has {len(grp)} items but none "
                                 f"marked canonical; suggest id={best['id']}"))

    return issues

# ── Step 8 – build outputs ────────────────────────────────────────────────────
def build_outputs(records: list[dict],
                  groups: dict[str, list[dict]],
                  issues: list[Issue],
                  log: list[dict]) -> dict[str, Any]:

    # ── canonical_foods.json ───────────────────────────────────────────────────
    canonical_foods = []
    for key, grp in groups.items():
        # Representative: highest trust, prefer canonical=True
        rep = max(grp,
                  key=lambda x: (int(x.get("canonical", False)),
                                 x.get("_trust_score", 0)))
        # Merge all aliases from the group
        all_aliases: list[str] = []
        for item in grp:
            all_aliases.extend(item.get("aliases", []))
            # Include English name variants as aliases
            if item is not rep:
                en_slug = _slug(item["en"])
                if en_slug not in [_slug(a) for a in all_aliases]:
                    all_aliases.append(item["en"])
        # Include Bengali names as aliases
        for item in grp:
            bn = item.get("bn", "")
            if bn and bn not in all_aliases:
                all_aliases.append(bn)
        all_aliases = list(dict.fromkeys(a for a in all_aliases if a.strip()))

        canon_rec = {
            "canonical_key": key,
            "canonical_id":  rep["_canon_id"],
            "representative_id": rep["id"],
            "en":            rep["en"],
            "bn":            rep["bn"],
            "cat":           rep.get("cat", ""),
            "family":        rep.get("family", ""),
            "trust_score":   rep["_trust_score"],
            "quality_score": rep.get("quality_score", 0),
            "src":           rep.get("src", ""),
            "nutrition_confidence": rep.get("nutrition_confidence", ""),
            "variant_count": len(grp),
            "variant_ids":   [x["id"] for x in grp if x is not rep],
            "all_aliases":   all_aliases,
            "nutrition": {
                "k": rep.get("k", 0), "p": rep.get("p", 0),
                "c": rep.get("c", 0), "f": rep.get("f", 0),
                "fi": rep.get("fi", 0), "ca": rep.get("ca", 0),
                "fe": rep.get("fe", 0), "zn": rep.get("zn", 0),
                "mg": rep.get("mg", 0), "pot": rep.get("pot", 0),
                "va": rep.get("va", 0), "vc": rep.get("vc", 0),
                "vd": rep.get("vd", 0), "b12": rep.get("b12", 0),
            },
            "serving": rep.get("s", ""),
        }
        canonical_foods.append(canon_rec)

    canonical_foods.sort(key=lambda x: -x["trust_score"])

    # ── food_variants.json ────────────────────────────────────────────────────
    food_variants = []
    for key, grp in groups.items():
        if len(grp) < 2:
            continue
        rep = max(grp,
                  key=lambda x: (int(x.get("canonical", False)),
                                 x.get("_trust_score", 0)))
        for item in grp:
            if item is rep:
                continue
            differs = []
            for fld in ("en", "s", "src", "cat", "k"):
                if item.get(fld) != rep.get(fld):
                    differs.append(fld)
            food_variants.append({
                "variant_id":    item["id"],
                "canonical_key": key,
                "canonical_representative_id": rep["id"],
                "en":            item["en"],
                "bn":            item.get("bn", ""),
                "src":           item.get("src", ""),
                "trust_score":   item["_trust_score"],
                "quality_score": item.get("quality_score", 0),
                "differs_in":    differs,
                "nutrition_k":   item.get("k", 0),
                "serving":       item.get("s", ""),
            })

    food_variants.sort(key=lambda x: x["canonical_key"])

    # ── qa_report.json ────────────────────────────────────────────────────────
    qa_report = []
    for iss in issues:
        qa_report.append({
            "severity":   iss.severity,
            "issue_type": iss.issue_type,
            "record_id":  iss.record_id,
            "field":      iss.field,
            "message":    iss.message,
            "actual":     iss.actual,
            "expected":   iss.expected,
        })
    qa_report.sort(key=lambda x: {"critical":0,"high":1,"medium":2,"low":3}
                   .get(x["severity"], 4))

    # ── normalization_log.json ────────────────────────────────────────────────
    norm_log = sorted(log, key=lambda x: (str(x.get("id", "")), x.get("action","")))

    return {
        "canonical_foods": canonical_foods,
        "food_variants":   food_variants,
        "qa_report":       qa_report,
        "normalization_log": norm_log,
    }

# ── Step 9 – write files ──────────────────────────────────────────────────────
def write_files(outputs: dict[str, Any], records: list[dict]) -> None:
    OUTDIR.mkdir(parents=True, exist_ok=True)

    def jdump(path: pathlib.Path, obj: Any) -> None:
        path.write_text(
            json.dumps(obj, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"  wrote {path.name} ({path.stat().st_size // 1024} KB,"
              f" {len(obj)} records)")

    jdump(OUTDIR / "canonical_foods.json", outputs["canonical_foods"])
    jdump(OUTDIR / "food_variants.json",   outputs["food_variants"])
    jdump(OUTDIR / "qa_report.json",       outputs["qa_report"])
    jdump(OUTDIR / "normalization_log.json", outputs["normalization_log"])

    # ── qa_summary.csv ────────────────────────────────────────────────────────
    from collections import Counter
    counts: Counter = Counter()
    sev_for: dict[str, str] = {}
    ids_for: dict[str, list] = defaultdict(list)
    for iss in outputs["qa_report"]:
        k = iss["issue_type"]
        counts[k] += 1
        sev_for[k] = iss["severity"]
        if iss["record_id"] is not None:
            ids_for[k].append(str(iss["record_id"]))

    csv_path = OUTDIR / "qa_summary.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["issue_type", "severity", "count", "example_ids"])
        for issue_type, cnt in sorted(counts.items(),
                                      key=lambda x: (
                                          {"critical":0,"high":1,"medium":2,"low":3}
                                          .get(sev_for.get(x[0],"low"), 4), -x[1])):
            examples = ",".join(ids_for[issue_type][:5])
            w.writerow([issue_type, sev_for[issue_type], cnt, examples])
    print(f"  wrote {csv_path.name} ({csv_path.stat().st_size} bytes,"
          f" {len(counts)} issue types)")

    # ── patch source file ─────────────────────────────────────────────────────
    # Remove internal pipeline keys before saving
    clean = []
    for r in records:
        rc = {k: v for k, v in r.items() if not k.startswith("_")}
        clean.append(rc)
    SRC.write_text(
        json.dumps(clean, ensure_ascii=False, separators=(",", ":")),
        encoding="utf-8"
    )
    print(f"  patched {SRC.name} in-place ({SRC.stat().st_size // 1024} KB)")

# ── main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    print("=== Food Dataset Canonicalization Pipeline v1.0 ===\n")

    print("1. Loading input …")
    raw = load_input()
    print(f"   {len(raw)} records loaded\n")

    print("2. Parsing & schema-normalising …")
    records, log = parse_records(raw)
    print(f"   {len(log)} schema fixes applied\n")

    print("3. Normalising text …")
    normalize_text(records, log)
    print(f"   {len(log)} total log entries so far\n")

    print("4. Building canonical keys …")
    build_canonical_keys(records)

    print("5. Grouping variants …")
    groups = group_variants(records)
    single = sum(1 for g in groups.values() if len(g) == 1)
    multi  = len(groups) - single
    print(f"   {len(groups)} canonical groups "
          f"({single} singletons, {multi} with variants)\n")

    print("6. Scoring trust & recomputing quality scores …")
    score_trust(records, log)
    recomputed = sum(1 for e in log if e.get("action") == "quality_score_recomputed")
    print(f"   {recomputed} quality scores recomputed\n")

    print("7. Validating …")
    issues = validate_rows(records, groups)
    by_sev: Counter = Counter(i.severity for i in issues)
    print(f"   {len(issues)} issues found: "
          + ", ".join(f"{s}={by_sev[s]}"
                      for s in ("critical","high","medium","low") if s in by_sev)
          + "\n")

    print("8. Building outputs …")
    outputs = build_outputs(records, groups, issues, log)
    print(f"   {len(outputs['canonical_foods'])} canonical food groups\n")

    print("9. Writing files …")
    write_files(outputs, records)

    print()
    print("=== Summary ===")
    print(f"  Records processed  : {len(records)}")
    print(f"  Canonical groups   : {len(groups)}")
    print(f"  Variants linked    : {len(outputs['food_variants'])}")
    print(f"  Schema fixes       : {len(log)}")
    print(f"  QA issues          : {len(issues)}")
    sev_order = ["critical","high","medium","low"]
    for s in sev_order:
        if by_sev.get(s):
            print(f"    {s:8}: {by_sev[s]}")
    print(f"  Quality scores fixed : {recomputed}")
    print(f"\nAll outputs in: {OUTDIR}/")


if __name__ == "__main__":
    from collections import Counter
    main()
