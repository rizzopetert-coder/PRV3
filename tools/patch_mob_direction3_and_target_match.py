"""
PRV3 -- MOB update: two new Decision Register rows. (1) Category E
Direction 3 concept corrected from a fixed-tier design to a variable-
length cluster design, based on real distribution data pulled this
session -- written to prompts/category-e-direction3-cluster-display.md.
(2) Primary-state/intended-target match rate flagged as a standalone
investigation candidate (1/58 in real calibration data) -- written to
prompts/primary-state-target-match-finding.md. Both planning artifacts
only, no code changes.

Version bump v4.146 -> v4.147: two new durable planning docs + Decision
Register rows, not a session-log-only change.

Usage:
  python tools/patch_mob_direction3_and_target_match.py --dry-run
  python tools/patch_mob_direction3_and_target_match.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MOB = "tools/_mob.txt"

ANCHOR = (
    '| Category E Direction 1 (rendering + motion quality upgrade) -- SHIPPED | 3 | **Closed -- built, verified, live before/after check via Pete\'s claude-in-chrome, not a manual walkthrough** | N/A | Gemini architecture review cleared Direction 1 with four verification gates -- two confirmed accurate (dimension_summary genuinely exists, 0.0-1.0 normalized per axis, Gemini-cleared; tier-gating color resolver already correctly hard-gates --color-rust to severity_tier === "Endemic" with no interpolation), two corrected before any code was written -- both further confirmed instances of the standing Gemini-verification-catches-real-errors pattern already logged multiple times this project. **Correction 1 (mounting points):** Gemini characterized the OD-07 rollback (commit b8860b5) as reverting /diagnostic\'s active mounting points "back to flat v1" -- the rollback commit\'s own message says it plainly: "Recolors rather than removes ConstellationField... the real dimension_summary-driven weighted-dimension shape... keeps rendering, now in v1 colors." Direct code read confirmed live-mode ConstellationField was already actively mounted in PrivateOutput.tsx with real dimension_summary data -- the real state was BETTER than Gemini\'s framing implied, not worse: nothing needed reactivating, the wiring was already live in production. Bonus finding surfaced by the same check: two files (web/lib/types.ts\'s DimensionSummary comment, ConstellationField.tsx\'s own file header) still carried stale "not yet wired, pending review" language describing a state that was no longer true -- same status-line-not-swept staleness pattern already logged multiple times this project, fixed as part of this build. **Correction 2 (data-emphasis enum):** Gemini\'s motion-code snippet used data-emphasis="primary"|"dimmed" -- confirmed via the live CSS utility (globals.css) and real usage (page.tsx, AssemblyPanel.tsx) that the actual, implemented enum is "primary"|"secondary"|"receded". "dimmed" appears nowhere in the codebase -- a fabricated value, not a stale-but-once-real one. Motion code built against the real enum instead. **Framer Motion, confirmed absent from package.json** -- Pete\'s explicit call: CSS transitions only, no new dependency. BUILD: centroid-tracking radial gradient fill on ConstellationField\'s live-mode shape (slate/charcoal core fading to paper, origin at the real arithmetic-mean centroid of the four weighted vertices, replacing the prior flat color-mix fill); per-axis vertex glow (4 independent feGaussianBlur filters, blur radius and opacity both scaled to that axis\'s real dimension_summary weight, dominant vertex glowing in the tier-gated accent color, all others --color-slate -- same color rule the existing dots/rings already used, not a new one); depth stacking (a low-alpha --color-charcoal backing stroke behind the main shape); recede/resolve motion upgrade (globals.css\'s [data-emphasis] transition split per target state -- 350ms cubic-bezier(0.16,1,0.3,1) entering "primary"/resolve, 250ms cubic-bezier(0.4,0,0.2,1) entering "secondary"/"receded"/recede -- exploiting the standard CSS technique where transition timing is picked up from the property\'s new computed value, zero JS). Tier-gated color resolver (severityAccentTokens()) untouched, confirmed already correct. Scope confirmed live mode only (LiveField) -- ambient mode\'s decorative KEYFRAMES-driven rendering has no real dimension_summary to scale a data-driven glow against, so its own craft upgrade (if wanted) is a separate future pass, not bundled here. VERIFICATION: tsc --noEmit clean. ConstellationField.test.ts 12/12 pass, confirming severityAccentTokens()/dominantAxis()/computeFrame() untouched. Full vitest run surfaced 6 pre-existing session-store.test.ts failures (hardcoded sequence-length assertions predating this session\'s earlier N=44->42 recalibration) -- confirmed unrelated via git-stash before/after comparison (identical failures with zero Category E changes present), not fixed here, flagged as a separate real gap. Live before/after screenshot verification held for Pete via claude-in-chrome against Production post-push, same method already used for Q05 and the A.2/A.3 checks this session -- no browser tool available in this Claude Code session, confirmed via fresh tool search before asking, not assumed. Diff reviewed and approved by Pete before commit. | This session (Claude Code) | Pete\'s call -- reopen if the live before/after check surfaces a rendering issue; otherwise closed, Directions 2/3 stay concept-level per the existing sequencing row until Pete decides to explore further |'
)

NEW_ROWS = (
    '\n'
    '| Category E Direction 3 (editorial/typographic hero) -- concept corrected from fixed-tier to variable-length cluster, Gemini review required | 3 | **Approved concept, corrected by real data -- Gemini architecture review required before build, not done yet** | Gemini architecture review not done -- touches PrivateOutput.tsx rendering and potentially how qualified-state data is shaped for display. No code changes until it clears | prompts/category-e-direction3-cluster-display.md written -- a durable planning artifact, no code changes. Pete\'s concern before any build: a single bold typographic headline (Output Precision principle) risks implying the named condition is the only one worth attention, when multiple are often genuinely co-present. Read-only investigation this session (58 real high_confidence calibration profiles through the actual rank_states -> apply_signal_floor -> route_output pipeline, not synthetic injection) confirmed the concern with real numbers: 100% land in multi-state mode (zero clean single-state results); qualified-state count min 2, max 32, median 7, mean 11.8; in 29/58 (50%) every qualified state rounds to the identical displayed percentage -- the live margin gate (check_signal_gate()\'s 0.05 cosine-unit relative threshold) routinely produces tight clustering, not a rare edge case. Design corrected accordingly: a fixed 2- or 3-state tier (the original framing) would undersell the real picture in a large share of profiles -- Direction 3 now specifies a variable-length cluster display (display cap + "+N more" affordance) instead, headline keeps its typographic dominance (still one verdict named with confidence), eyebrow language softens from "CONDITION IDENTIFIED" toward something like "MOST PROMINENT PATTERN", and "Also Present" as a section label is flagged as likely needing replacement too. Three items explicitly left open, not decided here: exact display cap, exact softened copy, and whether this build stays display-only (assumed) versus ever touching the underlying 0.05 margin-gate math (explicitly out of scope, a separate larger decision if ever raised). | This session (Claude Code) | Pete\'s call -- reopen once ready to send Direction 3 to Gemini for architecture review; no code changes before that clears |\n'
    '| Primary-state / intended-target match rate -- FLAGGED, standalone investigation candidate | 3 | **Flagged, not investigated further -- Pete\'s call on if/when to open this thread** | N/A -- not scheduled | prompts/primary-state-target-match-finding.md written -- a durable planning artifact, no code changes. Surfaced as a side effect of the same Direction 3 data pull, not sought out deliberately: across the 58 real high_confidence profiles, the displayed primary_state (actual #1-by-score from rank_states()) matched the profile\'s own intended target state in only 1 of 58 cases -- the other 57 landed anywhere from rank 2 to rank 58 (dead last) among all states, usually surfacing inside the tied secondary cluster instead. Real but contextualized, not presented as a bare alarming number: this project\'s calibration suite has a long-locked cluster/top_3/prominence pass criterion, not rank-1 (Session 7 precedent, reconfirmed at Session 69 -- only built_to_fail was found to reliably achieve rank-1 anywhere in the taxonomy), and the calibration suite\'s own pass bar (SCD_WCS_CLUSTER_WINDOW = 0.35) is confirmed far more permissive than the live display\'s actual qualification gate (SCD_WCS_MARGIN_GATE = 0.05) -- so this is not a hidden calibration-suite failure, it\'s a distinct property of the live margin gate specifically, sitting underneath a pass bar already designed with wide tolerance in mind. Open question, explicitly not resolved: is 1/58 still inside what "cluster, not rank-1" was always expected to produce, or does it indicate more dimensional overlap between states than originally intended. Methodology caveat logged honestly: pulled via generate_answers()\'s systematic answer-selection heuristic, not organic human answers -- real respondent answers could spread scores less evenly, though the structural cause (states sharing closely related dimensional_vector profiles) is a taxonomy property, not a test-answer artifact, so some clustering would likely persist regardless. Not blocking Direction 3 -- the report should represent real multiplicity honestly either way. | This session (Claude Code) | Pete\'s call -- not scheduled, no forced check-in. Reopen only if Pete decides the 1/58 figure warrants its own dedicated investigation |\n'
)


def apply(dry_run: bool) -> int:
    changed = 0
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count != 1:
        print(f"ERROR: {MOB} -- expected 1 match for anchor, found {count}")
        return 1
    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROWS, 1)
    if dry_run:
        print(f"OK (dry-run): {MOB} -- anchor found, would insert 2 new rows")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"WRITTEN: {MOB} -- 2 new rows inserted")
    changed += 1

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.146", "\\\\\\#\\\\\\# MOB v4.147"),
        ("CLAUDE.md", "| MOB version | v4.146 |", "| MOB version | v4.147 |"),
    ]
    for rel_path, old, new in version_edits:
        p = REPO_ROOT / rel_path
        t = p.read_text(encoding="utf-8")
        c = t.count(old)
        if c != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {c}")
            return 1
        nt = t.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            p.write_text(nt, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1

    print(f"\n{changed}/3 edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
