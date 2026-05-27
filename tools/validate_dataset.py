"""
Dataset validation gate — run before committing a new food_master JSON.
Exits with code 1 if any check fails.
Usage: py tools/validate_dataset.py [path/to/food_master.json]
"""
import json
import sys
import os

DATASET = sys.argv[1] if len(sys.argv) > 1 else "assets/data/food_master_v5_3.json"

ERRORS = []
WARNINGS = []


def err(msg):
    ERRORS.append(msg)


def warn(msg):
    WARNINGS.append(msg)


def check(items):
    ids = set()
    en_names = {}

    for item in items:
        iid = item.get("id")
        name = item.get("en", "")

        # Duplicate id check
        if iid in ids:
            err(f"Duplicate id={iid} ({name!r})")
        ids.add(iid)

        # Duplicate English name
        if name in en_names:
            warn(f"Duplicate name {name!r} (ids {en_names[name]} and {iid})")
        en_names[name] = iid

        k = item.get("k", 0)
        p = item.get("p", 0)
        c = item.get("c", 0)
        f = item.get("f", 0)

        # kJ-as-kcal: kcal > 900 is suspicious for most foods
        if k > 900 and item.get("cat") not in ("fat", "alcohol"):
            warn(f"id={iid} ({name!r}): k={k} may be kJ (> 900 kcal)")

        # Macro energy sum vs stated kcal — allow 20% tolerance
        macro_kcal = p * 4 + c * 4 + f * 9
        if k > 10 and macro_kcal > 10:
            ratio = macro_kcal / k
            if ratio > 1.25 or ratio < 0.75:
                err(
                    f"id={iid} ({name!r}): macro-kcal {macro_kcal:.0f} "
                    f"vs stated {k} kcal (ratio {ratio:.2f})"
                )

        # Fat=0 with non-zero calories is suspicious for non-plant foods
        if f == 0 and k > 50 and item.get("cat") in ("fish", "meat", "dairy"):
            warn(f"id={iid} ({name!r}): fat=0 for cat={item.get('cat')!r}")

        # Protein implausibly high (> 50 g/100 g) outside protein powders
        if p > 50 and item.get("cat") not in ("protein", "supplement"):
            warn(f"id={iid} ({name!r}): protein={p}g seems high")

        # Fat implausibly high (> 80 g/100 g)
        if f > 80:
            warn(f"id={iid} ({name!r}): fat={f}g seems very high")


def main():
    if not os.path.exists(DATASET):
        print(f"ERROR: {DATASET} not found", file=sys.stderr)
        sys.exit(1)

    with open(DATASET, encoding="utf-8") as fh:
        items = json.load(fh)

    print(f"Validating {len(items)} items in {DATASET} ...")
    check(items)

    if WARNINGS:
        print(f"\n{len(WARNINGS)} WARNING(S):")
        for w in WARNINGS:
            print(f"  WARN  {w}")

    if ERRORS:
        print(f"\n{len(ERRORS)} ERROR(S):")
        for e in ERRORS:
            print(f"  ERR   {e}")
        print("\nValidation FAILED.")
        sys.exit(1)
    else:
        print(f"\nValidation PASSED ({len(WARNINGS)} warnings).")


if __name__ == "__main__":
    main()
