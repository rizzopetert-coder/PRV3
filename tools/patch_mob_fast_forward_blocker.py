"""
PRV3 -- MOB update: tools/diagnostic_fast_forward.py confirmed structurally
unusable against this project's current infrastructure. Found while
scoping live-verification for Category E Direction 1 -- attempted to use
it as a fast path to reach the real results page, hit its own
_guard_not_production() safety check refusing prv-3.vercel.app, and
confirmed no Preview environment exists to point it at instead.

PARKED, not urgent -- needs a rework-or-retire decision from Pete
whenever he wants to pick it up.

Usage:
  python tools/patch_mob_fast_forward_blocker.py --dry-run
  python tools/patch_mob_fast_forward_blocker.py --write
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
    "| Category E (visual identity refresh) -- concept + sequencing approved, Gemini review required before build | 3 | **Approved direction -- Gemini architecture review required before Direction 1 build starts, not done yet** | Gemini architecture review of Direction 1 (structural/rendering-system decision touching OD-07's shipped token infrastructure -- globals.css tokens, ThemeSwitcher.tsx) has not happened. No code changes until it clears | prompts/category-e-visual-identity-refresh.md written -- a durable planning artifact, no code changes. Context: session opened on Pete's critique that the site \"looks sterile,\" specifically the existing 4-axis quadrilateral (OD-07's ConstellationField) reading as \"cheap and rudimentary.\" Governing constraint, explicit: the fix is craft-execution quality within the existing locked 3-color discipline (Principal Brief's Saint-Exupery restraint principle + the \"magnanimous but unflinching\" Core Reframe), not new decoration on top of it -- rust stays reserved for Endemic severity only, unchanged. Sequencing approved by Pete: Direction 1 (rendering-quality upgrade -- soft radial gradients, severity-scaled vertex glow, layering/depth, plus upgraded recede/resolve motion to spring physics/layered timing, reactivating OD-07's dormant infrastructure rather than building from zero) starts first as the lowest-risk test of whether \"cheap-looking\" is a craft problem (most likely) or a concept problem. Directions 2 (four-dial instrument-panel reframe, one gauge per Aptitude/Authority/Alliance/Attitude) and 3 (editorial/typographic hero, de-emphasizing the geometric shape entirely in favor of bold typography per the Output Precision principle) stay concept-level, explored only after Direction 1's result is seen -- Pete's own sequencing call, not a technical dependency. No visual mockups exist yet for any direction. | This session (Claude Code) | Pete's call -- reopen once ready to send Direction 1 to Gemini for architecture review; no code changes before that clears |"
)

NEW_ROW = (
    '\n'
    '| tools/diagnostic_fast_forward.py -- confirmed structurally unusable against current infrastructure, PARKED | N/A -- dev tooling, not a Tier 1-4 workflow item | Parked, not urgent -- rework-or-retire decision needed whenever Pete picks it up | N/A | Found while scoping live-verification for Category E Direction 1 -- attempted to use the tool\'s "jump" mode as a fast path to reach the real results page without a full 42-question manual walkthrough. Blocked before any run: the tool\'s own _guard_not_production() check (line 191-195) explicitly refuses prv-3.vercel.app, the known Production alias -- a deliberate safety guard, not worked around. Confirmed no Preview environment exists to point --base-url at instead (consistent with the no-Preview-environment default already on record -- every commit to main deploys straight to Production). Not a bug introduced this session -- a real consequence of infrastructure that changed after the tool was built (it was designed and live-verified against a real Preview deployment that no longer exists). VERCEL_AUTOMATION_BYPASS_SECRET also not present in this shell\'s environment, confirmed separately, though moot given the production guard alone already blocks any run. | This session (Claude Code) | Pete\'s call -- rework (e.g. an explicit --i-know-this-is-production override, or retarget to whatever replaces the Preview tier if one is ever reintroduced) or retire the tool. Not blocking anything else -- live verification of production-facing changes falls back to a real manual walkthrough or Pete\'s own claude-in-chrome session in the meantime |\n'
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
        (MOB, "\\\\\\#\\\\\\# MOB v4.144", "\\\\\\#\\\\\\# MOB v4.145"),
        ("CLAUDE.md", "| MOB version | v4.144 |", "| MOB version | v4.145 |"),
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
