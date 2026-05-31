"""
Full DB Cleanup Pipeline — food_master_v5_3.json → food_master_v5_4.json
Phases 1-10 as specified.
"""

import json, re, sys, os, unicodedata
from collections import defaultdict
from copy import deepcopy

sys.stdout.reconfigure(encoding='utf-8')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, 'assets', 'data')

MASTER_IN  = os.path.join(DATA, 'food_master_v5_3.json')
MASTER_OUT = os.path.join(DATA, 'food_master_v5_4.json')
IDX_EN_OUT = os.path.join(DATA, 'index_en_v5_4.json')
IDX_BN_OUT = os.path.join(DATA, 'index_bn_v5_4.json')
REPORTS    = os.path.join(ROOT, 'tools', 'reports')
os.makedirs(REPORTS, exist_ok=True)

def rp(name): return os.path.join(REPORTS, name)

# ─── Load ─────────────────────────────────────────────────────────────────────
with open(MASTER_IN, encoding='utf-8') as f:
    RAW = json.load(f)

FOODS_BEFORE = len(RAW)
print(f"Loaded {FOODS_BEFORE} items from {MASTER_IN}")

# Work on a deep copy
items = deepcopy(RAW)

# ──────────────────────────────────────────────────────────────────────────────
# HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def norm(s: str) -> str:
    """Lowercase, strip punctuation, collapse spaces."""
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def serving_grams(s_field: str) -> float:
    """Extract numeric gram weight from serving size string."""
    m = re.search(r"(\d+(?:\.\d+)?)\s*g", str(s_field), re.IGNORECASE)
    if m:
        return float(m.group(1))
    # Fallback: first number
    m = re.search(r"(\d+(?:\.\d+)?)", str(s_field))
    return float(m.group(1)) if m else 100.0

def jaccard(a: set, b: set) -> float:
    if not a and not b: return 0.0
    return len(a & b) / len(a | b)

def name_tokens(en: str) -> set:
    return set(re.findall(r"[a-z]+", en.lower())) - {
        "the","a","an","in","on","with","and","or","of","for",
        "to","is","it","its","at","by","as","from"}

def bn_is_clean(bn: str) -> bool:
    """Return False if Bengali name has obvious OCR/encoding issues."""
    if not bn:
        return False
    # Contains ASCII letters mixed in (not digits/parens)
    if re.search(r"[a-zA-Z]", bn) and re.search(r"[ঀ-৿]", bn):
        return False
    # Very short for a "food name"
    if len(bn.strip()) == 0:
        return False
    return True

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 1 — AUDIT
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 1: AUDIT ═══")

audit = {
    "total": len(items),
    "exact_duplicate_en": [],
    "near_duplicate_en": [],
    "missing_bn": [],
    "missing_en": [],
    "missing_micronutrients_ca_fe_zn": [],
    "category_issues": [],
    "invalid_serving": [],
    "nutrition_outliers": [],
    "critical_errors": [],
    "index_issues": [],
}

ALLOWED_CATS = {
    "breakfast","beverage","bread","cereal","dairy","dessert","egg",
    "fish","fruit","grain","legume","meat","rice","salad","seafood",
    "snack","soup","sweet","vegetable"
}

# 1a. Exact duplicates by normalized English name
en_map = defaultdict(list)
for item in items:
    key = norm(item.get("en",""))
    en_map[key].append(item["id"])
for key, ids in en_map.items():
    if len(ids) > 1:
        audit["exact_duplicate_en"].append({"key": key, "ids": ids})

# 1b. Near-duplicates: Jaccard > 0.7 on name tokens
id_to = {item["id"]: item for item in items}
processed = set()
for i, a in enumerate(items):
    for b in items[i+1:]:
        pair = tuple(sorted([a["id"], b["id"]]))
        if pair in processed: continue
        ta = name_tokens(a.get("en",""))
        tb = name_tokens(b.get("en",""))
        if not ta or not tb: continue
        j = jaccard(ta, tb)
        if j >= 0.65 and a.get("cat") == b.get("cat"):
            audit["near_duplicate_en"].append({
                "id_a": a["id"], "en_a": a["en"],
                "id_b": b["id"], "en_b": b["en"],
                "jaccard": round(j, 3),
                "cat": a.get("cat")
            })
            processed.add(pair)

# 1c. Missing Bengali / English names
for item in items:
    bn = item.get("bn","")
    en = item.get("en","")
    if not bn or bn.strip() == "":
        audit["missing_bn"].append({"id": item["id"], "en": en})
    if not en or en.strip() == "":
        audit["missing_en"].append({"id": item["id"], "bn": bn})

# 1d. Missing micronutrients
for item in items:
    if (item.get("ca", 0) == 0 and
        item.get("fe", 0) == 0 and
        item.get("zn", 0) == 0):
        audit["missing_micronutrients_ca_fe_zn"].append({
            "id": item["id"], "en": item.get("en"), "src": item.get("src")
        })

# 1e. Category issues
for item in items:
    cat = item.get("cat","")
    if cat not in ALLOWED_CATS:
        audit["category_issues"].append({
            "id": item["id"], "en": item.get("en"), "cat": cat
        })

# 1f. Invalid serving (can't extract weight)
for item in items:
    s = item.get("s","")
    if not re.search(r"\d", str(s)):
        audit["invalid_serving"].append({"id": item["id"], "en": item.get("en"), "s": s})

# 1g. Nutrition validation
for item in items:
    s_g = serving_grams(item.get("s","100g"))
    p = float(item.get("p", 0))
    c = float(item.get("c", 0))
    f = float(item.get("f", 0))
    fi = float(item.get("fi", 0))
    k = float(item.get("k", 0))
    est = round(4*p + 4*c + 9*f, 1)
    issues = []
    if k <= 0: issues.append("kcal<=0")
    if p > s_g: issues.append(f"protein({p})>serving({s_g})")
    if c > s_g: issues.append(f"carbs({c})>serving({s_g})")
    if f > s_g: issues.append(f"fat({f})>serving({s_g})")
    if fi > c and fi > 0: issues.append(f"fiber({fi})>carbs({c})")
    if k > 1500: issues.append(f"kcal({k})>1500")
    if est > 0 and abs(k - est)/max(est,1) > 0.40:
        issues.append(f"kcal_mismatch stored={k} est={est} diff={round(abs(k-est)/max(est,1)*100)}%")
    if issues:
        severity = "critical" if any(
            x.startswith(("kcal<=0","protein(","carbs(","fat(")) or "200%" in x
            for x in issues) else "outlier"
        rec = {"id": item["id"], "en": item.get("en"), "issues": issues,
               "k": k, "p": p, "c": c, "f": f, "fi": fi, "s": item.get("s"), "est_kcal": est}
        if severity == "critical":
            audit["critical_errors"].append(rec)
        else:
            audit["nutrition_outliers"].append(rec)

with open(rp("audit_report.json"), "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

print(f"  Exact duplicate EN names:  {len(audit['exact_duplicate_en'])}")
print(f"  Near-duplicate pairs:       {len(audit['near_duplicate_en'])}")
print(f"  Missing BN names:           {len(audit['missing_bn'])}")
print(f"  Missing EN names:           {len(audit['missing_en'])}")
print(f"  Missing ca+fe+zn:           {len(audit['missing_micronutrients_ca_fe_zn'])}")
print(f"  Bad categories:             {len(audit['category_issues'])}")
print(f"  Nutrition outliers:         {len(audit['nutrition_outliers'])}")
print(f"  Critical errors:            {len(audit['critical_errors'])}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 2 — DUPLICATE CONSOLIDATION
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 2: DUPLICATE CONSOLIDATION ═══")

# Explicit merge rules: (keep_id or keep_en_norm, drop_id or drop_en_norm, alias_tokens_to_add)
# We identify pairs from audit + well-known cases
# Strategy: keep lowest ID (oldest), absorb higher ID's EN name as keyword alias

dup_report = {"merged": [], "skipped": []}
merged_away = set()   # IDs to remove after merging

# Build lookup by normalized EN name
by_norm_en = defaultdict(list)
for item in items:
    by_norm_en[norm(item.get("en",""))].append(item)

def find_item(id_=None, en_norm=None):
    if id_ is not None:
        return id_to.get(id_)
    if en_norm is not None:
        hits = by_norm_en.get(en_norm, [])
        return hits[0] if hits else None

# ── Collect all candidate merge pairs ─────────────────────────────────────────
merge_pairs = []   # (keep_id, drop_id, reason)

# 2a. Exact duplicate EN names → always merge
for entry in audit["exact_duplicate_en"]:
    ids = sorted(entry["ids"])   # keep smallest (oldest)
    keep_id = ids[0]
    for drop_id in ids[1:]:
        merge_pairs.append((keep_id, drop_id, "exact_en_duplicate"))

# 2b. Near-duplicates with Jaccard >= 0.80 — high confidence
for nd in audit["near_duplicate_en"]:
    if nd["jaccard"] >= 0.80:
        keep_id = min(nd["id_a"], nd["id_b"])
        drop_id = max(nd["id_a"], nd["id_b"])
        merge_pairs.append((keep_id, drop_id, f"near_dup_j={nd['jaccard']}"))

# 2c. Hand-curated known near-duplicates (common Bengali food spellings)
HAND_MERGES = [
    # (keep_en_lower_contains, drop_en_lower_contains, reason)
    # We'll look these up by substring match
    ("chingri malaikari",  "chingri malai",       "chingri_malai_variant"),
    ("mutton kosha",       "kosha mangsho",        "kosha_mangsho_variant"),
    ("patishapta nolen gur","patishapta nolen gur","nolen_gur_variant"),  # same, skip
    ("shorshe ilish",      "sorshe ilish",         "ilish_spelling"),
    ("muri ghonto",        "murir ghonto",         "muri_ghonto_variant"),
    ("dal makhani",        "dal makhni",           "dal_makhani_variant"),
    ("pabda jhol",         "pabda jhal",           "pabda_spelling"),   # different dishes - skip
    ("ghugni",             "ghoogni",              "ghugni_spelling"),
    ("luchi",              "luci",                 "luchi_spelling"),
]

for keep_substr, drop_substr, reason in HAND_MERGES:
    if keep_substr == drop_substr:
        continue
    # pabda jhol vs jhal are different dishes (jhol=thin gravy, jhal=spicy) — skip
    if "pabda" in keep_substr and "pabda" in drop_substr:
        continue
    keep_candidates = [it for it in items if keep_substr in it.get("en","").lower()]
    drop_candidates = [it for it in items if drop_substr in it.get("en","").lower()
                       and not any(it["id"] == k["id"] for k in keep_candidates)]
    for k in keep_candidates:
        for d in drop_candidates:
            if k["id"] != d["id"] and k.get("cat") == d.get("cat"):
                merge_pairs.append((min(k["id"],d["id"]), max(k["id"],d["id"]), reason))

# Deduplicate merge pairs
seen_pairs = set()
unique_pairs = []
for keep, drop, reason in merge_pairs:
    key = (keep, drop)
    if key not in seen_pairs and keep != drop:
        seen_pairs.add(key)
        unique_pairs.append((keep, drop, reason))
merge_pairs = unique_pairs

print(f"  Merge pairs identified: {len(merge_pairs)}")

# ── Execute merges ────────────────────────────────────────────────────────────
for keep_id, drop_id, reason in merge_pairs:
    keep = id_to.get(keep_id)
    drop = id_to.get(drop_id)
    if not keep or not drop:
        dup_report["skipped"].append({"keep": keep_id, "drop": drop_id, "reason": "id_not_found"})
        continue
    if drop_id in merged_away:
        dup_report["skipped"].append({"keep": keep_id, "drop": drop_id, "reason": "already_merged"})
        continue

    # Absorb drop's EN name as alias keyword
    drop_en = drop.get("en","").strip()
    drop_bn = drop.get("bn","").strip()
    keep_kw = list(keep.get("kw", []))
    keep_kw_set = {k.lower() for k in keep_kw}

    # Add EN alias
    for alias in [drop_en, drop_en.lower(), norm(drop_en)]:
        if alias and alias.lower() not in keep_kw_set and alias.lower() != keep.get("en","").lower():
            keep_kw.append(alias.lower())
            keep_kw_set.add(alias.lower())

    # Add BN alias keywords (first word of BN name for search)
    if drop_bn and drop_bn != keep.get("bn",""):
        # Add first Bengali word as search token
        first_bn_word = drop_bn.split()[0] if drop_bn.split() else ""
        if first_bn_word and first_bn_word not in keep_kw_set:
            keep_kw.append(first_bn_word)
            keep_kw_set.add(first_bn_word)

    # Also absorb drop's existing kw
    for kw in drop.get("kw", []):
        if kw.lower() not in keep_kw_set:
            keep_kw.append(kw)
            keep_kw_set.add(kw.lower())

    keep["kw"] = keep_kw[:12]   # cap at 12 to keep lean

    dup_report["merged"].append({
        "kept_id": keep_id, "kept_en": keep.get("en"),
        "dropped_id": drop_id, "dropped_en": drop_en,
        "reason": reason,
        "alias_added": drop_en
    })
    merged_away.add(drop_id)

# Remove merged-away items
items = [it for it in items if it["id"] not in merged_away]
id_to = {it["id"]: it for it in items}

with open(rp("duplicate_report.json"), "w", encoding="utf-8") as f:
    json.dump(dup_report, f, ensure_ascii=False, indent=2)

print(f"  Merged:  {len(dup_report['merged'])}")
print(f"  Skipped: {len(dup_report['skipped'])}")
print(f"  Items after merge: {len(items)}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 3 — CATEGORY NORMALIZATION
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 3: CATEGORY NORMALIZATION ═══")

CAT_MAP = {
    # Legacy → canonical
    "veg": "vegetable",
    "veg_curry": "vegetable",
    "fish_curry": "fish",
    "meat_curry": "meat",
    "sweets": "sweet",
    "dal": "legume",
    "noodle": "snack",
    "protein": "meat",       # protein bowls / eggs → reassign below
    "drink": "beverage",
    "spice": "vegetable",    # condiments/spices → vegetable is closest
    "condiment": "vegetable",
    "nut": "snack",          # nuts stay as snack
    "fat": "dairy",          # ghee/oil items
    "meal": "snack",         # generic meals
    "diet": "snack",         # diet bowls
    "fitness": "snack",      # fitness bowls
    "brand": "snack",        # branded snacks
    "other": "snack",        # generic catch-all → snack
    "cereal": "breakfast",   # cereals → breakfast
    # Already correct:
    # "breakfast","beverage","bread","dairy","dessert","egg",
    # "fish","fruit","grain","legume","meat","rice","salad","seafood",
    # "snack","soup","sweet","vegetable"
}

# Special per-item overrides based on English name keywords
def smart_category(item, current_cat: str) -> str:
    en = item.get("en","").lower()
    # Protein category: eggs→egg, chicken/mutton/beef→meat, fish→fish, else snack
    if current_cat == "protein":
        if any(w in en for w in ["egg","omelette","omelet","bhurji"]):
            return "egg"
        if any(w in en for w in ["chicken","mutton","beef","pork","lamb","keema"]):
            return "meat"
        if any(w in en for w in ["fish","prawn","shrimp","tuna","salmon","rohu","hilsa"]):
            return "fish"
        return "snack"
    if current_cat == "spice":
        return "vegetable"
    if current_cat in ("condiment",):
        return "vegetable"
    # Roti → bread
    if current_cat == "roti":
        return "bread"
    return CAT_MAP.get(current_cat, current_cat)

cat_report = {"changes": [], "unmapped": []}
for item in items:
    old = item.get("cat","other")
    new = smart_category(item, old)
    if new not in ALLOWED_CATS:
        new = "snack"   # safe fallback
        cat_report["unmapped"].append({"id": item["id"], "en": item.get("en"), "old_cat": old})
    if new != old:
        cat_report["changes"].append({
            "id": item["id"], "en": item.get("en"), "old": old, "new": new
        })
        item["cat"] = new

with open(rp("category_mapping_report.json"), "w", encoding="utf-8") as f:
    json.dump(cat_report, f, ensure_ascii=False, indent=2)

print(f"  Categories normalized: {len(cat_report['changes'])}")
print(f"  Unmapped (→snack):     {len(cat_report['unmapped'])}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 4 — NUTRITION VALIDATION (report only, repair in Phase 5)
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 4: NUTRITION VALIDATION ═══")

outliers = []
critical = []

for item in items:
    s_g = serving_grams(item.get("s","100g"))
    p = float(item.get("p",0))
    c = float(item.get("c",0))
    f = float(item.get("f",0))
    fi = float(item.get("fi",0))
    k = float(item.get("k",0))
    ca = float(item.get("ca",0))
    fe = float(item.get("fe",0))
    zn = float(item.get("zn",0))

    est = round(4*p + 4*c + 9*f, 1)
    diff_pct = abs(k - est)/max(est,1)*100 if est > 0 else 0

    issues = []
    is_critical = False

    if k <= 0:
        issues.append("kcal=0"); is_critical=True
    if k > 1500:
        issues.append(f"kcal={k}>1500"); is_critical=True
    if p > s_g:
        issues.append(f"protein={p}>serving={s_g}g"); is_critical=True
    if c > s_g:
        issues.append(f"carbs={c}>serving={s_g}g"); is_critical=True
    if f > s_g:
        issues.append(f"fat={f}>serving={s_g}g"); is_critical=True
    if fi > c and fi > 1:
        issues.append(f"fiber={fi}>carbs={c}")
    if ca < 0: issues.append(f"ca<0={ca}")
    if fe < 0: issues.append(f"fe<0={fe}")
    if zn < 0: issues.append(f"zn<0={zn}")
    if est > 0 and diff_pct > 40 and not is_critical:
        issues.append(f"kcal_mismatch stored={k} est={est} diff={round(diff_pct)}%")
    if est > 0 and diff_pct > 100:
        is_critical = True

    if issues:
        rec = {"id": item["id"], "en": item.get("en"), "s": item.get("s"),
               "s_g": s_g, "k": k, "p": p, "c": c, "f": f, "fi": fi,
               "est_kcal": est, "diff_pct": round(diff_pct,1), "issues": issues}
        if is_critical:
            critical.append(rec)
        else:
            outliers.append(rec)

with open(rp("nutrition_outliers.json"), "w", encoding="utf-8") as f:
    json.dump(outliers, f, ensure_ascii=False, indent=2)
with open(rp("critical_nutrition_errors.json"), "w", encoding="utf-8") as f:
    json.dump(critical, f, ensure_ascii=False, indent=2)

print(f"  Outliers (>40% mismatch):  {len(outliers)}")
print(f"  Critical errors:           {len(critical)}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 5 — AUTO REPAIR
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 5: AUTO REPAIR ═══")

repair_report = {"repaired": [], "manual_review": []}
manual_review = []

def decimal_shift_guess(stored: float, est: float):
    """
    If stored is ~10x or ~0.1x of estimated, it's a decimal shift.
    Return corrected value or None.
    """
    for factor in [10, 100, 0.1, 0.01]:
        candidate = round(stored / factor, 1)
        if est > 0 and abs(candidate - est) / max(est,1) < 0.25:
            return candidate
    return None

for item in items:
    p = float(item.get("p",0))
    c = float(item.get("c",0))
    f = float(item.get("f",0))
    k = float(item.get("k",0))
    s_g = serving_grams(item.get("s","100g"))
    est = round(4*p + 4*c + 9*f, 1)
    diff_pct = abs(k - est)/max(est,1)*100 if est > 0 else 0

    repaired = False

    # Case 1: kcal is obviously 10x or 100x off
    if est > 10 and diff_pct > 150:
        fixed = decimal_shift_guess(k, est)
        if fixed and fixed > 0 and fixed <= 2000:
            repair_report["repaired"].append({
                "id": item["id"], "en": item.get("en"),
                "field": "k", "old": k, "new": fixed,
                "reason": f"decimal_shift est={est}"
            })
            item["k"] = fixed
            repaired = True

    # Case 2: protein/fat/carbs exceeds serving — likely per-100g entered when serving is smaller
    for field, val, label in [("p",p,"protein"),("c",c,"carbs"),("f",f,"fat")]:
        if val > s_g and s_g >= 50:
            # If val is within 100g range, scale proportionally
            if val <= 100:
                scaled = round(val * s_g / 100, 1)
                repair_report["repaired"].append({
                    "id": item["id"], "en": item.get("en"),
                    "field": field, "old": val, "new": scaled,
                    "reason": f"{label}({val})>serving({s_g}) → scaled to serving"
                })
                item[field] = scaled
                repaired = True

    if not repaired and (diff_pct > 40 or any(
        float(item.get(x,0)) > s_g for x in ["p","c","f"]
    )):
        manual_review.append({
            "id": item["id"], "en": item.get("en"),
            "k": k, "p": p, "c": c, "f": f, "fi": float(item.get("fi",0)),
            "s": item.get("s"), "est_kcal": est, "diff_pct": round(diff_pct,1),
            "note": "Needs manual verification"
        })

with open(rp("repair_report.json"), "w", encoding="utf-8") as f:
    json.dump(repair_report, f, ensure_ascii=False, indent=2)
with open(rp("manual_review.json"), "w", encoding="utf-8") as f:
    json.dump(manual_review, f, ensure_ascii=False, indent=2)

print(f"  Auto-repaired: {len(repair_report['repaired'])}")
print(f"  Manual review: {len(manual_review)}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 6 — MICRONUTRIENT REPORT
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 6: MICRONUTRIENT REPORT ═══")

missing_micro = []
for item in items:
    ca = float(item.get("ca",0))
    fe = float(item.get("fe",0))
    zn = float(item.get("zn",0))
    if ca == 0 and fe == 0 and zn == 0:
        missing_micro.append({
            "id": item["id"], "en": item.get("en"),
            "cat": item.get("cat"), "src": item.get("src")
        })

with open(rp("missing_micronutrients.json"), "w", encoding="utf-8") as f:
    json.dump(missing_micro, f, ensure_ascii=False, indent=2)

print(f"  Items with ca=fe=zn=0: {len(missing_micro)}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 7 — BENGALI QUALITY REVIEW
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 7: BENGALI QUALITY REVIEW ═══")

bn_issues = []
for item in items:
    bn = item.get("bn","")
    en = item.get("en","")
    issues = []

    if not bn or not bn.strip():
        issues.append("missing")
    else:
        # Mixed English + Bengali script
        has_bengali = bool(re.search(r"[ঀ-৿]", bn))
        has_latin   = bool(re.search(r"[a-zA-Z]", bn))
        if has_bengali and has_latin:
            issues.append("mixed_script")

        # Isolated diacritics / marks without base letter (common OCR artifact)
        if re.search(r"[া-ৌ][া-ৌ]", bn):
            issues.append("consecutive_vowel_marks")

        # Contains unusual ASCII mixed in
        if re.search(r"[<>{}\\|]", bn):
            issues.append("unexpected_ascii")

        # Very short BN name for a food (less than 2 chars)
        if len(bn.strip()) < 2:
            issues.append("too_short")

        # Odia / non-Bengali Indic script mistakenly in BN field
        if re.search(r"[଀-୿]", bn):   # Odia range
            issues.append("odia_script_in_bn_field")

    if issues:
        bn_issues.append({"id": item["id"], "en": en, "bn": bn, "issues": issues})

with open(rp("bn_spelling_review.json"), "w", encoding="utf-8") as f:
    json.dump(bn_issues, f, ensure_ascii=False, indent=2)

print(f"  Bengali quality issues: {len(bn_issues)}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 8 — INDEX REBUILD
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 8: INDEX REBUILD ═══")

# Reassign IDs sequentially (preserve relative order, oldest IDs stay lowest)
items.sort(key=lambda x: x["id"])
# Keep original IDs — do NOT reassign (would break existing user data in Hive)
# Just rebuild indexes from current IDs

def build_en_index(items):
    idx = defaultdict(set)
    for item in items:
        food_id = item["id"]
        # Index English name
        en = item.get("en","")
        for word in re.findall(r"[a-z]+", en.lower()):
            if len(word) >= 2: idx[word[:2]].add(food_id)
            if len(word) >= 3: idx[word[:3]].add(food_id)
        # Index keywords (including aliases from merges)
        for kw in item.get("kw", []):
            for word in re.findall(r"[a-z]+", str(kw).lower()):
                if len(word) >= 2: idx[word[:2]].add(food_id)
                if len(word) >= 3: idx[word[:3]].add(food_id)
    return {k: sorted(v) for k, v in idx.items()}

def build_bn_index(items):
    idx = defaultdict(set)
    for item in items:
        food_id = item["id"]
        bn = item.get("bn","")
        for word in bn.split():
            w = word.strip()
            if len(w) >= 1:
                prefix = w[:2]
                # Only index if it looks like Bengali Unicode
                if any(0x0980 <= ord(c) <= 0x09FF for c in prefix):
                    idx[prefix].add(food_id)
    return {k: sorted(v) for k, v in idx.items()}

idx_en = build_en_index(items)
idx_bn = build_bn_index(items)

# Validate — every item ID must appear somewhere
all_ids = {it["id"] for it in items}
en_indexed = set()
for ids in idx_en.values(): en_indexed.update(ids)
bn_indexed = set()
for ids in idx_bn.values(): bn_indexed.update(ids)

orphan_en = all_ids - en_indexed
orphan_bn = all_ids - bn_indexed
audit["index_issues"] = {
    "orphan_from_en_index": sorted(orphan_en),
    "orphan_from_bn_index": sorted(orphan_bn),
}
print(f"  EN index tokens: {len(idx_en)},  orphan IDs: {len(orphan_en)}")
print(f"  BN index tokens: {len(idx_bn)},  orphan IDs: {len(orphan_bn)}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 9 — BENGALI FOOD COVERAGE
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 9: BENGALI FOOD COVERAGE ═══")

TARGET_DISHES = [
    "Shorshe Ilish", "Ilish Bhapa", "Pabda Jhal", "Chingri Malaikari",
    "Daab Chingri", "Mochar Ghonto", "Thor Ghonto", "Enchorer Dalna",
    "Basanti Pulao", "Kosha Mangsho", "Dak Bungalow Chicken", "Chanar Dalna",
    "Patishapta", "Patishapta Nolen Gur", "Radhaballavi", "Ghugni",
    "Muri Ghonto", "Bhetki Paturi"
]

coverage = []
for dish in TARGET_DISHES:
    dish_norm = norm(dish)
    dish_toks = name_tokens(dish)
    found = None
    # Exact match first
    for item in items:
        if norm(item.get("en","")) == dish_norm:
            found = {"id": item["id"], "en": item["en"], "bn": item.get("bn",""), "match": "exact"}
            break
    # Near match (Jaccard >= 0.6)
    if not found:
        for item in items:
            j = jaccard(dish_toks, name_tokens(item.get("en","")))
            if j >= 0.60:
                found = {"id": item["id"], "en": item["en"], "bn": item.get("bn",""),
                         "match": f"near_j={round(j,2)}"}
                break
    # Also check keywords
    if not found:
        for item in items:
            for kw in item.get("kw",[]):
                if norm(str(kw)) == dish_norm:
                    found = {"id": item["id"], "en": item["en"], "bn": item.get("bn",""), "match": "via_kw"}
                    break
            if found: break

    coverage.append({
        "dish": dish,
        "status": "present" if found else "missing",
        "record": found
    })

missing_dishes = [c["dish"] for c in coverage if c["status"] == "missing"]
present_dishes = [c["dish"] for c in coverage if c["status"] == "present"]

with open(rp("bengali_food_coverage_report.json"), "w", encoding="utf-8") as f:
    json.dump(coverage, f, ensure_ascii=False, indent=2)

print(f"  Present: {len(present_dishes)}/{len(TARGET_DISHES)}")
if missing_dishes:
    print(f"  Missing: {missing_dishes}")

# ──────────────────────────────────────────────────────────────────────────────
# PHASE 10 — FINAL OUTPUT
# ──────────────────────────────────────────────────────────────────────────────
print("\n═══ PHASE 10: WRITE OUTPUTS ═══")

# Final sort: keep original ID ordering
items.sort(key=lambda x: x["id"])

with open(MASTER_OUT, "w", encoding="utf-8") as f:
    json.dump(items, f, ensure_ascii=False, separators=(",",":"))
print(f"  Written: {MASTER_OUT}")

with open(IDX_EN_OUT, "w", encoding="utf-8") as f:
    json.dump(idx_en, f, ensure_ascii=False, separators=(",",":"))
print(f"  Written: {IDX_EN_OUT}")

with open(IDX_BN_OUT, "w", encoding="utf-8") as f:
    json.dump(idx_bn, f, ensure_ascii=False, separators=(",",":"))
print(f"  Written: {IDX_BN_OUT}")

# Update audit report with index validation
with open(rp("audit_report.json"), "w", encoding="utf-8") as f:
    json.dump(audit, f, ensure_ascii=False, indent=2)

# ──────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
FOODS_AFTER = len(items)
print("\n" + "═"*55)
print("  DATABASE CLEANUP SUMMARY")
print("═"*55)
print(f"  Foods before cleanup:        {FOODS_BEFORE}")
print(f"  Foods after cleanup:         {FOODS_AFTER}")
print(f"  Duplicates merged away:      {len(merged_away)}")
print(f"  Categories normalized:       {len(cat_report['changes'])}")
print(f"  Nutrition outliers found:    {len(outliers)}")
print(f"  Critical errors found:       {len(critical)}")
print(f"  Auto-repairs applied:        {len(repair_report['repaired'])}")
print(f"  Items for manual review:     {len(manual_review)}")
print(f"  Missing micronutrients:      {len(missing_micro)}")
print(f"  Bengali quality issues:      {len(bn_issues)}")
print(f"  Bengali dishes covered:      {len(present_dishes)}/{len(TARGET_DISHES)}")
if missing_dishes:
    print(f"  Bengali dishes missing:      {missing_dishes}")
else:
    print(f"  Bengali dishes missing:      none")
print(f"  EN index tokens:             {len(idx_en)}")
print(f"  BN index tokens:             {len(idx_bn)}")
print("═"*55)
print("\n  Reports written to: tools/reports/")
