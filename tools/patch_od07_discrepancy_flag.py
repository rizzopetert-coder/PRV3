"""
PRV3 -- Flag a discrepancy in the OD-07 Decision Register row (Section
13a): its own text says OD-07 exists only as "three working mockups,
not yet built into the live site," but direct read this session
confirmed it IS live on DiagnosticFlow.tsx, page.tsx, and
PrivateOutput.tsx (the three-theme --ink/--field token system and the
live-mode ConstellationField both render in production on those files
today). NOT resolving whether this shipping was intentional (Section
14's "Visual identity v2 shipped" entry references a later Gemini-
cleared dimension_summary wiring, commit 9c52e7d) or unplanned scope
creep during the /diagnostic reskin -- just recording that the row's
claim and the live codebase currently disagree, pending Pete's design
review (see prompts/diagnostic-reskin-stages-4-5-rescope.md).

Usage:
  python tools/patch_od07_discrepancy_flag.py --dry-run
  python tools/patch_od07_discrepancy_flag.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.92",
    "\\\\\\#\\\\\\# MOB v4.93",
)

edit(
    "tools/_mob.txt",
    "| OD-07 — Visual concept for the methodology (Topology vs. Constellation) — CLOSED | 3 | Closed | Resolved via a hybrid Constellation-Topology model, not either concept alone — Gemini-cleared architecture review confirmed the hybrid satisfies the original comparative-review objection (closing on Topology alone, without evaluating Constellation, was previously flagged as unsound process). Structure: 4-axis weighted quadrilateral (Aptitude/Authority/Alliance/Attitude), vertices derived from session-actual dimensional scores — Constellation's structural model, preserving P-11's dual-axis dimensional read rather than abstracting it away. Severity overlay: localized contour rings (Topology's technique), radiating exclusively from the dominant (highest-severity) axis vertex, not ambient across the whole shape. General accent (--oxide/--oxide-text) at Emerging/Entrenched severity; reserved accent (--urgency/--urgency-text) at Endemic only, preserving the existing single-meaning-color discipline established during the earlier token-system work. Token discipline, explicit: the homepage/ambient decorative version is capped below Endemic intensity and never uses the reserved token — confirmed as a deliberate constraint, not an oversight, since a decorative loop cycling through \"Endemic\" with no real diagnosis behind it would devalue the signal the reserved color exists to protect. Reference implementations exist as three working mockups, not yet built into the live site: three-theme token system (Warm/Dark/Neutral), homepage ambient motif (continuous linear-interpolation animation, capped severity), and full results-page implementation (weighted quadrilateral + severity rings, real synthesis copy). Originally tracked as OD-07 in the MOB's retired Section 12 \"Open Decisions\" register (pre-v3.0) — folded into this Decision Register on closure since that structure no longer exists in the current file; historical ID preserved here for continuity | This session (2026-07-21) | Closed — no further check-in. Building the three reference mockups into the live site is separate, un-scoped future work, not tracked as an open item here |",
    '''| OD-07 — Visual concept for the methodology (Topology vs. Constellation) — CLOSED (design decision), but see DISCREPANCY flag below | 3 | Closed (the hybrid-model decision itself) -- but this row's own "not yet built into the live site" claim is confirmed stale, flagged not resolved | Resolved via a hybrid Constellation-Topology model, not either concept alone — Gemini-cleared architecture review confirmed the hybrid satisfies the original comparative-review objection (closing on Topology alone, without evaluating Constellation, was previously flagged as unsound process). Structure: 4-axis weighted quadrilateral (Aptitude/Authority/Alliance/Attitude), vertices derived from session-actual dimensional scores — Constellation's structural model, preserving P-11's dual-axis dimensional read rather than abstracting it away. Severity overlay: localized contour rings (Topology's technique), radiating exclusively from the dominant (highest-severity) axis vertex, not ambient across the whole shape. General accent (--oxide/--oxide-text) at Emerging/Entrenched severity; reserved accent (--urgency/--urgency-text) at Endemic only, preserving the existing single-meaning-color discipline established during the earlier token-system work. Token discipline, explicit: the homepage/ambient decorative version is capped below Endemic intensity and never uses the reserved token — confirmed as a deliberate constraint, not an oversight, since a decorative loop cycling through "Endemic" with no real diagnosis behind it would devalue the signal the reserved color exists to protect. Reference implementations exist as three working mockups, not yet built into the live site: three-theme token system (Warm/Dark/Neutral), homepage ambient motif (continuous linear-interpolation animation, capped severity), and full results-page implementation (weighted quadrilateral + severity rings, real synthesis copy). Originally tracked as OD-07 in the MOB's retired Section 12 "Open Decisions" register (pre-v3.0) — folded into this Decision Register on closure since that structure no longer exists in the current file; historical ID preserved here for continuity. **DISCREPANCY FLAGGED (this session, confirmed by direct read, not assumed):** the "not yet built into the live site" claim directly above no longer matches the live codebase -- the three-theme --ink/--field token system and the live-mode ConstellationField (weighted quadrilateral + severity rings, real dimension_summary data) are BOTH live in production today on web/components/DiagnosticFlow.tsx, web/app/diagnostic/page.tsx, and web/components/PrivateOutput.tsx. Not resolved here whether this was intentional, later-reviewed shipping (Section 14's "Visual identity v2 shipped" entry references a subsequent Gemini-cleared dimension_summary wiring, commit 9c52e7d, for exactly the live-mode ConstellationField piece) or unplanned scope creep during the /diagnostic reskin work (prompts/diagnostic-reskin-stages-4-5-rescope.md) -- just recording that this row's own text and the live codebase currently disagree, pending Pete's design review of OD-07 live on those three files. | This session (2026-07-21); discrepancy flagged this session (Claude Code) | Reopened for awareness only, not action -- Pete's design review of OD-07 live on the three Stage 3 files will determine whether this row needs correcting or whether the live shipping is confirmed intentional and this flag can close |''',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
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
