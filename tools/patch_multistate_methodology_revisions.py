"""
PRV3 -- Four revisions (originally scoped as three, plus one follow-up)
to prompts/friction-tax-multistate-compounding-methodology.md, per
Pete's instructions:

1. Rename "frequency loading" -> "multi-channel severity loading"
   (prose term + the frequency_loading variable name), throughout.
2. Add an N=1 continuity guard to Step 3: without it, a single
   identified state whose own criterion scores happen to span multiple
   channels would incorrectly trigger loading, breaking the exact
   single-state parity Step 2's own continuity requirement establishes.
   This is a real formula correction, not just wording.
3. Add a frozen-range requirement to Step 2: the min-max normalization
   bounds applied to combined_criterion_score must be fixed, pre-defined
   constants set at design time, not derived dynamically from whichever
   states happen to be identified in a session -- combined_criterion_
   score's range differs from a single state's raw_score range once
   geometric-decay aggregation is applied, so new bounds must be
   independently pinned before implementation.
4. FOLLOW-UP -- replace Step 3's rationale paragraph entirely, dropping
   the frequency-vs-severity actuarial framing that revision 1's rename
   put in direct tension with itself, rather than patching around it.
   Folded into the SAME anchor block as revision 2 (both touch the same
   paragraph pair, and the N=1 guard's anchor already spans this
   rationale paragraph) rather than a separate sequential replacement,
   to avoid any anchor-ordering ambiguity. Pete's supplied replacement
   text used "--" for its one dash; normalized to a real em-dash (--)
   to match this file's own established convention (9 confirmed real
   em-dash occurrences elsewhere in the file, zero double-hyphens) --
   flagged, not silent.

Usage:
  python tools/patch_multistate_methodology_revisions.py --dry-run
  python tools/patch_multistate_methodology_revisions.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
TARGET_FILE = REPO_ROOT / "prompts" / "friction-tax-multistate-compounding-methodology.md"


# ---------------------------------------------------------------------------
# 1. Rename: header, formula line, final formula, next-steps items 2 and 3.
# ---------------------------------------------------------------------------

HEADER_OLD = (
    "### Step 3 — Frequency loading (implements Factor B), applied separately and multiplicatively\n"
)
HEADER_NEW = (
    "### Step 3 — Multi-Channel Severity Loading (implements Factor B), applied separately and multiplicatively\n"
)

FORMULA_OLD = (
    "breadth = count of the 4 criteria where combined_criterion_score[k] > 0\n"
    "frequency_loading = 1.0 + 0.05 * (breadth - 1)   [yields 1.00 / 1.05 / 1.10 / 1.15 for breadth 1/2/3/4]\n"
)
FORMULA_NEW = (
    "breadth = count of the 4 criteria where combined_criterion_score[k] > 0\n"
    "multi_channel_severity_loading = 1.0 + 0.05 * (breadth - 1)   [yields 1.00 / 1.05 / 1.10 / 1.15 for breadth 1/2/3/4]\n"
)

FINAL_FORMULA_OLD = (
    "low = adjusted_baseline * combined_multiplier * frequency_loading * severity_scalar\n"
)
FINAL_FORMULA_NEW = (
    "low = adjusted_baseline * combined_multiplier * multi_channel_severity_loading * severity_scalar\n"
)

STEP2_NEXTITEM_OLD = (
    "2. Resolve the frequency_loading constant (0.05) — placeholder pending Pete's input or calibration.\n"
)
STEP2_NEXTITEM_NEW = (
    "2. Resolve the multi_channel_severity_loading constant (0.05) — placeholder pending Pete's input or calibration.\n"
)

STEP3_NEXTITEM_OLD = (
    "3. CC implementation: replace compute_friction_tax()'s mean_multiplier step with combined_criterion_score aggregation per Step 1, add frequency_loading per Step 3, verify single-state continuity explicitly, update tests.\n"
)
STEP3_NEXTITEM_NEW = (
    "3. CC implementation: replace compute_friction_tax()'s mean_multiplier step with combined_criterion_score aggregation per Step 1, add multi_channel_severity_loading per Step 3, verify single-state continuity explicitly, update tests.\n"
)


# ---------------------------------------------------------------------------
# 2. N=1 continuity guard, inserted into Step 3 (after the rationale
#    paragraph, before the FLAGGED placeholder-constant paragraph).
# ---------------------------------------------------------------------------

STEP3_GUARD_ANCHOR_OLD = (
    "Deliberately kept separate from and multiplicative against the severity multiplier from Step 2, not blended into it. Actuarial rationale: breadth-across-criteria represents FREQUENCY (likelihood something in this risk profile materializes at all), not SEVERITY (how bad it is if it does). Conflating frequency and severity into one number is a modeling error per standard actuarial practice (attritional risk is priced via expected value; frequency and severity are typically modeled as separate components even when combined into one final rate).\n"
    "\n"
    "FLAGGED: the 0.05 increment is a placeholder, not a researched or structurally-derived constant (unlike the geometric decay in Step 1, which is structurally motivated). Requires Pete's judgment or further calibration before implementation, not to be treated as locked.\n"
)

STEP3_GUARD_ANCHOR_NEW = (
    "Deliberately kept separate from and multiplicative against the severity multiplier from Step 2, not blended into it. Rationale (revised from an earlier frequency/severity framing that overstated an actuarial analogy this instrument doesn't fully earn): breadth-across-criteria measures how many distinct damage channels a diagnosed condition spans simultaneously — a dimension of systemic coupling and diversification, not the depth of harm within any single channel (which Step 2 already captures), and not classical actuarial frequency (how often a loss event recurs over time). An organization whose identified states hit all four channels at once is structurally more exposed than one with the same combined severity concentrated in a single channel, independent of either being more 'frequent' in any insurance sense. This is additive information to Step 2's depth measure, not a restatement of it: Step 2 asks how bad each affected channel is, Step 3 asks how many channels are affected at once.\n"
    "\n"
    "Continuity requirement (N=1): when exactly one state is identified, multi_channel_severity_loading MUST equal 1.0 regardless of how many criteria that single state's own scores span. The breadth-based formula above applies only when two or more states are identified (N >= 2). Without this guard, a single identified state whose own criterion scores happen to span multiple channels (e.g. a state scoring above zero on all four criteria) would incorrectly trigger loading, breaking the exact single-state parity that Step 2's own continuity requirement establishes. This must be verified explicitly during implementation, not assumed.\n"
    "\n"
    "FLAGGED: the 0.05 increment is a placeholder, not a researched or structurally-derived constant (unlike the geometric decay in Step 1, which is structurally motivated). Requires Pete's judgment or further calibration before implementation, not to be treated as locked.\n"
)


# ---------------------------------------------------------------------------
# 3. Frozen-range requirement, appended to Step 2's existing continuity
#    requirement paragraph.
# ---------------------------------------------------------------------------

STEP2_CONTINUITY_OLD = (
    "Continuity requirement: with exactly one identified state, this formula MUST collapse exactly to that state's own existing STATE_MULTIPLIERS entry — zero discontinuity from current single-state behavior. This must be verified explicitly during implementation, not assumed.\n"
)

STEP2_CONTINUITY_NEW = (
    "Continuity requirement: with exactly one identified state, this formula MUST collapse exactly to that state's own existing STATE_MULTIPLIERS entry — zero discontinuity from current single-state behavior. This must be verified explicitly during implementation, not assumed.\n"
    "\n"
    "Frozen-range requirement: the min-max normalization bounds applied to combined_criterion_score must be fixed, pre-defined constants set at design time, not derived dynamically from whichever states happen to be identified in a given session or from empirically observed data. combined_criterion_score's range is not the same as a single state's raw_score range ([0, 8] under Calibration Set 3) once geometric-decay aggregation across multiple states is applied, so the theoretical min/max used for interpolation here must be independently defined and locked before implementation, analogous to how Set 3's own [0, 8] to [1.0, 1.4] mapping was frozen at design time rather than computed from observed data.\n"
)


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count == 0:
        print(f"ABORT -- anchor not found: {label}", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches): {label}", file=sys.stderr)
        sys.exit(1)
    return text.replace(old, new)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = TARGET_FILE.read_text(encoding="utf-8")

    text = _replace_once(text, HEADER_OLD, HEADER_NEW, "Step 3 header rename")
    text = _replace_once(text, FORMULA_OLD, FORMULA_NEW, "frequency_loading formula rename")
    text = _replace_once(text, STEP3_GUARD_ANCHOR_OLD, STEP3_GUARD_ANCHOR_NEW, "rationale rewrite + N=1 continuity guard insertion")
    text = _replace_once(text, FINAL_FORMULA_OLD, FINAL_FORMULA_NEW, "final formula rename")
    text = _replace_once(text, STEP2_CONTINUITY_OLD, STEP2_CONTINUITY_NEW, "frozen-range requirement insertion")
    text = _replace_once(text, STEP2_NEXTITEM_OLD, STEP2_NEXTITEM_NEW, "next-steps item 2 rename")
    text = _replace_once(text, STEP3_NEXTITEM_OLD, STEP3_NEXTITEM_NEW, "next-steps item 3 rename")

    print("=" * 78)
    print("1. RENAME -- Step 3 header")
    print("=" * 78)
    print("--- OLD ---")
    print(HEADER_OLD.rstrip("\n"))
    print("--- NEW ---")
    print(HEADER_NEW.rstrip("\n"))

    print("\n" + "=" * 78)
    print("1. RENAME -- formula line")
    print("=" * 78)
    print("--- OLD ---")
    print(FORMULA_OLD.rstrip("\n"))
    print("--- NEW ---")
    print(FORMULA_NEW.rstrip("\n"))

    print("\n" + "=" * 78)
    print("2 + 4. NEW -- rationale paragraph replaced, N=1 continuity guard inserted (Step 3)")
    print("=" * 78)
    print("--- OLD ---")
    print(STEP3_GUARD_ANCHOR_OLD.rstrip("\n"))
    print("--- NEW ---")
    print(STEP3_GUARD_ANCHOR_NEW.rstrip("\n"))

    print("\n" + "=" * 78)
    print("1. RENAME -- final formula")
    print("=" * 78)
    print("--- OLD ---")
    print(FINAL_FORMULA_OLD.rstrip("\n"))
    print("--- NEW ---")
    print(FINAL_FORMULA_NEW.rstrip("\n"))

    print("\n" + "=" * 78)
    print("3. NEW -- frozen-range requirement (inserted into Step 2)")
    print("=" * 78)
    print("--- OLD ---")
    print(STEP2_CONTINUITY_OLD.rstrip("\n"))
    print("--- NEW ---")
    print(STEP2_CONTINUITY_NEW.rstrip("\n"))

    print("\n" + "=" * 78)
    print("1. RENAME -- Next steps items 2 and 3")
    print("=" * 78)
    print("--- OLD ---")
    print(STEP2_NEXTITEM_OLD.rstrip("\n"))
    print(STEP3_NEXTITEM_OLD.rstrip("\n"))
    print("--- NEW ---")
    print(STEP2_NEXTITEM_NEW.rstrip("\n"))
    print(STEP3_NEXTITEM_NEW.rstrip("\n"))

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    TARGET_FILE.write_text(text, encoding="utf-8")
    print(f"\nWROTE {TARGET_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
