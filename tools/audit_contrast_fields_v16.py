"""
PRV3 — Session 18 Contrast Field Verification (v16)

Confirms all 19 locked field values are exactly as specified.
Any deviation is a hard stop.

Usage:
  python tools/audit_contrast_fields_v16.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.questions import _build_library

LOCKED_FIELDS = [
    # (question_id, option_id, field_name, required_value)
    ("Q02", "B", "authority_liability",  0.25),
    ("Q02", "B", "aptitude_liability",  -0.15),
    ("Q02", "B", "attitude_liability",  -0.10),
    ("Q04", "D", "authority_liability",  0.60),
    ("Q04", "D", "attitude_liability",   0.30),
    ("Q04", "D", "alliance_liability",  -0.15),
    ("Q10", "C", "aptitude_liability",   0.60),
    ("Q10", "C", "authority_liability",  0.30),
    ("Q10", "C", "authority_asset",     -0.10),
    ("Q11", "C", "attitude_liability",   0.50),
    ("Q11", "C", "authority_liability",  0.05),
    ("Q15", "C", "attitude_liability",   0.50),
    ("Q15", "C", "authority_liability",  0.25),
    ("Q15", "C", "alliance_liability",  -0.15),
    ("Q23", "C", "authority_liability",  0.50),
    ("Q23", "C", "aptitude_liability",   0.10),
    ("Q23", "D", "authority_liability",  0.50),
    ("Q23", "D", "aptitude_liability",   0.25),
    ("Q23", "D", "attitude_liability",  -0.15),
]


def main():
    lib = _build_library()

    print(f"\nSession 18 Contrast Field Verification — v16")
    print("=" * 64)

    passed = 0
    failed = 0
    results = []

    for qid, opt_id, field, required in LOCKED_FIELDS:
        q = lib.get(qid)
        if q is None:
            results.append((False, qid, opt_id, field, required, "QUESTION_NOT_FOUND"))
            failed += 1
            continue

        opt = next((o for o in q.answer_options if o.option_id == opt_id), None)
        if opt is None:
            results.append((False, qid, opt_id, field, required, "OPTION_NOT_FOUND"))
            failed += 1
            continue

        actual = opt.dimensional_contributions.get(field, 0.0)
        ok = abs(actual - required) < 1e-9
        results.append((ok, qid, opt_id, field, required, actual))
        if ok:
            passed += 1
        else:
            failed += 1

    for ok, qid, opt_id, field, required, actual in results:
        status = "PASS" if ok else "FAIL"
        mark = "  " if ok else "!!"
        print(f"  {mark} [{status}] {qid}-{opt_id} {field}: required={required}  actual={actual}")

    print(f"\nResult: {passed}/19 passed, {failed} failed.")

    if failed > 0:
        print("\n[HARD STOP] Contrast field verification failed. Do not proceed.")
        sys.exit(1)
    else:
        print("\n[OK] All 19 locked fields verified.")
        sys.exit(0)


if __name__ == "__main__":
    main()
