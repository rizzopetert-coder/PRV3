"""
Legal/Compliance byte-identical baseline: capture and check.

prompts/friction-tax-rebuild-build-spec.md Section 8 requires that Legal/
Compliance outputs are byte-identical before and after the friction tax
rebuild. This script records that baseline from the unchanged engine, and
re-checks it after any refactor commit.

What it covers (two blocks, hashed separately and together):

  GRID  compute_legal_compliance_exposure() and
        compute_legal_per_state_breakdown() for every one of the 58 states as a
        single-state input, across: headcounts 12, 60, 175, 400, 800, 1200 (the
        integers named in the spec, 1200 exceeds the intake cap on purpose),
        all 11 industries, all 6 org types, and a fixed set of jurisdiction
        lists (JURISDICTION_SETS below).

  CAL   private_output.legal_tail_risk_exposure for each of the 175
        calibration profiles, run through tools/calibration_runner.py's own
        run_profile() pipeline, with the profile's own intake unchanged.

Storage (under tools/fixtures/):
  legal_compliance_baseline.json.gz   full canonical JSON, gzip mtime=0
  legal_compliance_baseline.sha256.json   manifest: sha256 of the UNCOMPRESSED
                                      canonical bytes, per-block hashes, the
                                      per-(state, jurisdiction set) hashes used
                                      to localise a diff, and provenance
The hash is over the canonical JSON bytes, never over the gzip file.

Modes:
  --dry-run   compute, print counts and hashes, write nothing (default)
  --write     compute and write both fixture files (refuses to overwrite)
  --check     compute and compare to the stored manifest, exit 1 on any
              difference and name the first differing blocks

Never regenerate the fixture after a refactor. A --check failure blocks the
build, it is not a prompt to re-baseline.
"""

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

FIXTURE_DIR = REPO / "tools" / "fixtures"
GZ_PATH = FIXTURE_DIR / "legal_compliance_baseline.json.gz"
MANIFEST_PATH = FIXTURE_DIR / "legal_compliance_baseline.sha256.json"

HEADCOUNTS = (12, 60, 175, 400, 800, 1200)

# Fixed jurisdiction lists. Chosen to hit every branch the Legal path reads:
# no jurisdiction (federal threshold), OH (state_specific_tiers with the
# compensatory-damages formula), CA, CO, AR, MD, TN (per-state caveats and
# flat/uncapped treatments), TX, NY, WY, DC (coverage thresholds without a
# jurisdiction multiplier row), order-dependent ties (OH,TX vs TX,OH), a
# three-state mix, and an unknown code.
JURISDICTION_SETS = (
    [],
    ["OH"], ["CA"], ["CO"], ["AR"], ["MD"], ["TN"], ["TX"], ["NY"], ["WY"], ["DC"],
    ["OH", "TX"], ["TX", "OH"], ["CA", "NY", "TX"],
    ["ZZ"],
)


def _canon(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
                      default=str).encode("utf-8")


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _call(fn, *args):
    # An exception is part of the recorded behavior, not a capture failure.
    try:
        return fn(*args)
    except Exception as e:  # noqa: BLE001
        return {"__exception__": f"{type(e).__name__}: {e}"}


def compute_grid() -> dict:
    """{ "<state>|<jur index>": [ [headcount, industry, org_type, total, breakdown], ... ] }"""
    from engine.friction_tax import (
        compute_legal_compliance_exposure, compute_legal_per_state_breakdown,
    )
    from engine.data.intake import INTAKE_FIELDS
    from engine.data.states import STATE_PROFILES

    industries = list(INTAKE_FIELDS["industry"])
    org_types = list(INTAKE_FIELDS["org_type"])
    blocks = {}
    for sid in sorted(STATE_PROFILES):
        for ji, jur in enumerate(JURISDICTION_SETS):
            rows = []
            for hc in HEADCOUNTS:
                for ind in industries:
                    for ot in org_types:
                        total = _call(compute_legal_compliance_exposure, [sid], hc, ind, ot, list(jur))
                        brk = _call(compute_legal_per_state_breakdown, [sid], hc, ind, ot, list(jur))
                        rows.append([hc, ind, ot, total, brk])
            blocks[f"{sid}|{ji}"] = rows
    return blocks


def compute_cal() -> dict:
    """{ "<test_id>": legal_tail_risk_exposure or None } for the 175 profiles."""
    import calibration_runner as cr

    out = {}
    for tc in cr.ALL_PROFILES:
        out[tc.test_id] = cr.run_profile(tc)["private_output"]["legal_tail_risk_exposure"]
    return out


def compute_baseline() -> dict:
    grid = compute_grid()
    cal = compute_cal()
    return {"grid": grid, "cal": cal}


def summarize(baseline: dict) -> dict:
    grid, cal = baseline["grid"], baseline["cal"]
    grid_hash = _sha(_canon(grid))
    cal_hash = _sha(_canon(cal))
    full = _canon(baseline)
    n_rows = sum(len(v) for v in grid.values())
    return {
        "full_sha256": _sha(full),
        "full_canonical_bytes": len(full),
        "grid_sha256": grid_hash,
        "cal_sha256": cal_hash,
        "grid_blocks": {k: _sha(_canon(v)) for k, v in sorted(grid.items())},
        "cal_profiles": {k: _sha(_canon(v)) for k, v in sorted(cal.items())},
        "counts": {
            "states": len({k.split("|")[0] for k in grid}),
            "jurisdiction_sets": len(JURISDICTION_SETS),
            "headcounts": list(HEADCOUNTS),
            "grid_rows": n_rows,
            "grid_function_calls": n_rows * 2,
            "cal_profiles": len(cal),
            "cal_profiles_with_legal_block": sum(1 for v in cal.values() if v is not None),
            "exceptions_recorded": sum(
                1 for rows in grid.values() for r in rows
                for part in (r[3], r[4]) if isinstance(part, dict) and "__exception__" in part
            ),
        },
    }


def _git(*args) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True).stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true", help="compute and report, write nothing (default)")
    g.add_argument("--write", action="store_true", help="write the fixture files")
    g.add_argument("--check", action="store_true", help="compare current engine to the stored baseline")
    args = ap.parse_args()

    baseline = compute_baseline()
    summ = summarize(baseline)
    print(json.dumps({k: v for k, v in summ.items() if k not in ("grid_blocks", "cal_profiles")}, indent=2))

    if args.check:
        stored = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        if stored["full_sha256"] == summ["full_sha256"]:
            print("CHECK: byte-identical to baseline")
            return 0
        print("CHECK: DIFFERS from baseline")
        bad = [k for k, h in summ["grid_blocks"].items() if stored["grid_blocks"].get(k) != h]
        bad_cal = [k for k, h in summ["cal_profiles"].items() if stored["cal_profiles"].get(k) != h]
        print(f"  grid blocks differing: {len(bad)} of {len(summ['grid_blocks'])}, first 10: {bad[:10]}")
        print(f"  calibration profiles differing: {len(bad_cal)} of {len(summ['cal_profiles'])}, first 10: {bad_cal[:10]}")
        return 1

    if args.write:
        if GZ_PATH.exists() or MANIFEST_PATH.exists():
            print("REFUSING: baseline already exists. Never regenerate it.")
            return 2
        FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
        full = _canon(baseline)
        GZ_PATH.write_bytes(gzip.compress(full, compresslevel=9, mtime=0))
        manifest = {
            "purpose": "Legal/Compliance byte-identical baseline, friction tax rebuild spec Section 8",
            "captured_by": "tools/capture_legal_baseline.py --write",
            "engine_git_head": _git("rev-parse", "HEAD"),
            "engine_dirty_tracked_files": _git("status", "--porcelain", "--untracked-files=no", "--", "engine", "api").splitlines(),
            "hash_basis": "sha256 of the uncompressed canonical JSON bytes (sort_keys, compact separators, ascii)",
            "jurisdiction_sets": JURISDICTION_SETS,
            **summ,
        }
        MANIFEST_PATH.write_bytes((json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("utf-8"))
        print(f"WROTE {GZ_PATH.relative_to(REPO)} ({GZ_PATH.stat().st_size} bytes gz) and {MANIFEST_PATH.relative_to(REPO)}")
        return 0

    print("DRY RUN: nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
