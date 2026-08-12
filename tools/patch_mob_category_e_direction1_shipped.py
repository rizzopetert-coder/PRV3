"""
PRV3 -- MOB update: Category E Direction 1 (rendering + motion quality
upgrade) shipped. Records both corrected Gemini findings from this
build's verification pass as further confirmed instances of the standing
Gemini-verification-catches-real-errors pattern.

Version bump v4.145 -> v4.146: a Direction 1 build closes, touching
shipped presentation-layer code.

Usage:
  python tools/patch_mob_category_e_direction1_shipped.py --dry-run
  python tools/patch_mob_category_e_direction1_shipped.py --write
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
    "| tools/diagnostic_fast_forward.py -- confirmed structurally unusable against current infrastructure, PARKED | N/A -- dev tooling, not a Tier 1-4 workflow item | Parked, not urgent -- rework-or-retire decision needed whenever Pete picks it up | N/A | Found while scoping live-verification for Category E Direction 1 -- attempted to use the tool's \"jump\" mode as a fast path to reach the real results page without a full 42-question manual walkthrough. Blocked before any run: the tool's own _guard_not_production() check (line 191-195) explicitly refuses prv-3.vercel.app, the known Production alias -- a deliberate safety guard, not worked around. Confirmed no Preview environment exists to point --base-url at instead (consistent with the no-Preview-environment default already on record -- every commit to main deploys straight to Production). Not a bug introduced this session -- a real consequence of infrastructure that changed after the tool was built (it was designed and live-verified against a real Preview deployment that no longer exists). VERCEL_AUTOMATION_BYPASS_SECRET also not present in this shell's environment, confirmed separately, though moot given the production guard alone already blocks any run. | This session (Claude Code) | Pete's call -- rework (e.g. an explicit --i-know-this-is-production override, or retarget to whatever replaces the Preview tier if one is ever reintroduced) or retire the tool. Not blocking anything else -- live verification of production-facing changes falls back to a real manual walkthrough or Pete's own claude-in-chrome session in the meantime |"
)

NEW_ROW = (
    '\n'
    '| Category E Direction 1 (rendering + motion quality upgrade) -- SHIPPED | 3 | **Closed -- built, verified, live before/after check via Pete\'s claude-in-chrome, not a manual walkthrough** | N/A | Gemini architecture review cleared Direction 1 with four verification gates -- two confirmed accurate (dimension_summary genuinely exists, 0.0-1.0 normalized per axis, Gemini-cleared; tier-gating color resolver already correctly hard-gates --color-rust to severity_tier === "Endemic" with no interpolation), two corrected before any code was written -- both further confirmed instances of the standing Gemini-verification-catches-real-errors pattern already logged multiple times this project. **Correction 1 (mounting points):** Gemini characterized the OD-07 rollback (commit b8860b5) as reverting /diagnostic\'s active mounting points "back to flat v1" -- the rollback commit\'s own message says it plainly: "Recolors rather than removes ConstellationField... the real dimension_summary-driven weighted-dimension shape... keeps rendering, now in v1 colors." Direct code read confirmed live-mode ConstellationField was already actively mounted in PrivateOutput.tsx with real dimension_summary data -- the real state was BETTER than Gemini\'s framing implied, not worse: nothing needed reactivating, the wiring was already live in production. Bonus finding surfaced by the same check: two files (web/lib/types.ts\'s DimensionSummary comment, ConstellationField.tsx\'s own file header) still carried stale "not yet wired, pending review" language describing a state that was no longer true -- same status-line-not-swept staleness pattern already logged multiple times this project, fixed as part of this build. **Correction 2 (data-emphasis enum):** Gemini\'s motion-code snippet used data-emphasis="primary"|"dimmed" -- confirmed via the live CSS utility (globals.css) and real usage (page.tsx, AssemblyPanel.tsx) that the actual, implemented enum is "primary"|"secondary"|"receded". "dimmed" appears nowhere in the codebase -- a fabricated value, not a stale-but-once-real one. Motion code built against the real enum instead. **Framer Motion, confirmed absent from package.json** -- Pete\'s explicit call: CSS transitions only, no new dependency. BUILD: centroid-tracking radial gradient fill on ConstellationField\'s live-mode shape (slate/charcoal core fading to paper, origin at the real arithmetic-mean centroid of the four weighted vertices, replacing the prior flat color-mix fill); per-axis vertex glow (4 independent feGaussianBlur filters, blur radius and opacity both scaled to that axis\'s real dimension_summary weight, dominant vertex glowing in the tier-gated accent color, all others --color-slate -- same color rule the existing dots/rings already used, not a new one); depth stacking (a low-alpha --color-charcoal backing stroke behind the main shape); recede/resolve motion upgrade (globals.css\'s [data-emphasis] transition split per target state -- 350ms cubic-bezier(0.16,1,0.3,1) entering "primary"/resolve, 250ms cubic-bezier(0.4,0,0.2,1) entering "secondary"/"receded"/recede -- exploiting the standard CSS technique where transition timing is picked up from the property\'s new computed value, zero JS). Tier-gated color resolver (severityAccentTokens()) untouched, confirmed already correct. Scope confirmed live mode only (LiveField) -- ambient mode\'s decorative KEYFRAMES-driven rendering has no real dimension_summary to scale a data-driven glow against, so its own craft upgrade (if wanted) is a separate future pass, not bundled here. VERIFICATION: tsc --noEmit clean. ConstellationField.test.ts 12/12 pass, confirming severityAccentTokens()/dominantAxis()/computeFrame() untouched. Full vitest run surfaced 6 pre-existing session-store.test.ts failures (hardcoded sequence-length assertions predating this session\'s earlier N=44->42 recalibration) -- confirmed unrelated via git-stash before/after comparison (identical failures with zero Category E changes present), not fixed here, flagged as a separate real gap. Live before/after screenshot verification held for Pete via claude-in-chrome against Production post-push, same method already used for Q05 and the A.2/A.3 checks this session -- no browser tool available in this Claude Code session, confirmed via fresh tool search before asking, not assumed. Diff reviewed and approved by Pete before commit. | This session (Claude Code) | Pete\'s call -- reopen if the live before/after check surfaces a rendering issue; otherwise closed, Directions 2/3 stay concept-level per the existing sequencing row until Pete decides to explore further |\n'
)


def apply(dry_run: bool) -> int:
    changed = 0
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count != 1:
        print(f"ERROR: {MOB} -- expected 1 match for anchor, found {count}")
        return 1
    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROW, 1)
    if dry_run:
        print(f"OK (dry-run): {MOB} -- anchor found, would insert 1 new row")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"WRITTEN: {MOB} -- 1 new row inserted")
    changed += 1

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.145", "\\\\\\#\\\\\\# MOB v4.146"),
        ("CLAUDE.md", "| MOB version | v4.145 |", "| MOB version | v4.146 |"),
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
