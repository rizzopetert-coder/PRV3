"""
PRV3 -- Fix the remaining 7 "3-4x" liquidated-damages errors in
experiment-2-employment-litigation-taxonomy.html, surfaced by a broader
grep after the first 2 spots were corrected last commit. All 9 instances
(2 already fixed + these 7) trace to the same unverified original claim,
not 9 separate research errors.

4 are the same FLSA wage-and-hour mechanism already corrected (lines
627, 966, 1053, 1086: 2x federal, states may separately permit treble
damages). 3 are FMLA (lines 720, 736, 1032) -- same 2x doubling
principle but a distinct statute (29 U.S.C. Sec 2617(a)(1)(A)(iii)) with
its own structural note: FMLA lacks FLSA's DOL-administrative-settlement
pathway at scale, so the administrative-vs-litigation framing used for
FLSA does not carry over here.

Also updates the Decision Register entry (tools/_mob.txt) added last
commit to reflect the full scope: 9 total instances, not 2.

Usage:
  python tools/patch_e2_remaining_multiplier_fixes.py --dry-run
  python tools/patch_e2_remaining_multiplier_fixes.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


E2 = "research/seven-experiments/experiment-2-employment-litigation-taxonomy.html"

# --- FLSA-mechanism (same fix as the 2 already corrected) ---

edit(
    E2,
    '<div class="data-item"><div class="data-label">Cost Multiplier</div><div class="data-val">3–4x back wages</div></div>',
    '<div class="data-item"><div class="data-label">Cost Multiplier</div><div class="data-val">2x back wages (federal); some states separately permit treble damages under state law</div></div>',
)

edit(
    E2,
    'The multiplier — back wages plus liquidated damages plus attorney fees — produces 3–4x the underlying back wages as the effective organizational cost.',
    'The multiplier — back wages plus liquidated damages plus attorney fees — produces 2x the underlying back wages as the effective organizational cost under federal law; some states separately permit treble damages.',
)

edit(
    E2,
    '<div class="nc-financial">EPI estimates $50B+ in annual wage theft — more than all property crime combined. Class action settlements in the tens of millions for large employers. 3–4x multiplier on underlying back wages through liquidated damages and attorney fees.</div>',
    '<div class="nc-financial">EPI estimates $50B+ in annual wage theft — more than all property crime combined. Class action settlements in the tens of millions for large employers. 2x multiplier on underlying back wages through liquidated damages and attorney fees under federal law; some states separately permit treble damages.</div>',
)

edit(
    E2,
    '<td>3–4x back wages (class)</td>',
    '<td>2x back wages (federal); some states permit treble damages separately</td>',
)

# --- FMLA-mechanism (2x correction, distinct structural note) ---

edit(
    E2,
    '<div class="data-item"><div class="data-label">Cost Multiplier</div><div class="data-val">3–4x economic loss</div></div>',
    '<div class="data-item"><div class="data-label">Cost Multiplier</div><div class="data-val">2x economic loss (liquidated damages double back pay by default under 29 U.S.C. § 2617(a)(1)(A)(iii) unless employer proves good faith)</div></div>',
)

edit(
    E2,
    'FMLA violations produce back pay, liquidated damages equal to back pay, and attorney fees — typically 3–4x the underlying economic loss.',
    'FMLA violations produce back pay, liquidated damages equal to back pay, and attorney fees — liquidated damages double back pay by default; courts award them unless the employer proves good faith and reasonable grounds. Unlike FLSA, FMLA claims are rarely resolved administratively, so this doubling is the norm rather than an escalation from a lower administrative baseline.',
)

edit(
    E2,
    '<div class="nc-financial">Average ADA settlement: $75K–$150K. FMLA violations: 3–4x economic loss in back pay, liquidated damages, and attorney fees. Preventable — legal training and HR access cost a fraction of a single claim.</div>',
    '<div class="nc-financial">Average ADA settlement: $75K–$150K. FMLA violations: liquidated damages double back pay by default (29 U.S.C. § 2617(a)(1)(A)(iii)) unless the employer proves good faith; FMLA claims are rarely resolved administratively, so this doubling is the norm, not an escalation. Preventable — legal training and HR access cost a fraction of a single claim.</div>',
)


# ============================================================
# tools/_mob.txt -- update the Decision Register entry to full scope
# ============================================================

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.81",
    "\\\\\\#\\\\\\# MOB v4.82",
)

edit(
    "tools/_mob.txt",
    '| DOL liquidated-damages multiplier correction -- RESOLVED (self-correction, same session) | 3 | Closed -- corrected before this session\'s work is committed | N/A | The DOL mechanism-caveat fix committed earlier this session (research/seven-experiments/experiment-2-employment-litigation-taxonomy.html, 4 spots) stated the litigation-path liquidated-damages multiplier as a range ("3-4x" in one spot, "2-4x" in another) without independent verification at the time. Confirmed via multiple independent legal sources during this session\'s Legal/Compliance Addendum 2 work: the federal FLSA liquidated-damages standard is a flat 2x (back wages plus an equal amount, "double damages") -- there is no federal 3x or 4x tier. A small number of states (Massachusetts confirmed) separately permit treble (3x) damages under state wage law, a distinct legal avenue, not an extension of the federal multiplier. This corrects content committed earlier this SAME session, not a legacy error carried forward from a prior one. Direct re-check also found Addendum 2\'s own framing ("all 4 spots need \'2-4x\' corrected") was not quite right: only 2 of the 4 originally-fixed spots (lines 643 and 1018) actually contained multiplier language -- the other 2 (626, the DOL Recovery data label; 1124, the closing findings sentence) never stated a multiplier and needed no further correction, confirmed by direct re-check of the live file rather than assumed from the addendum\'s own count. | This session (Claude Code) | Closed -- no further check-in |',
    '''| DOL/FLSA/FMLA liquidated-damages multiplier correction -- RESOLVED, full scope (self-correction, same session) | 3 | Closed -- all instances corrected before this session's work is committed | N/A | The DOL mechanism-caveat fix committed earlier this session stated the litigation-path liquidated-damages multiplier as a "3-4x"/"2-4x" range without independent verification at the time. Confirmed via multiple independent legal sources: the federal FLSA liquidated-damages standard is a flat 2x ("double damages") -- no federal 3x or 4x tier exists. A small number of states (Massachusetts confirmed) separately permit treble (3x) damages under state wage law, a distinct legal avenue, not an extension of the federal multiplier. **Full scope, confirmed by a broader repo-wide grep after the first pass, not assumed complete at 2 or 4:** 9 total instances of this same unverified "3-4x" claim existed in research/seven-experiments/experiment-2-employment-litigation-taxonomy.html, all traced to the same original error, not 9 independent research mistakes -- 2 FLSA wage-and-hour spots corrected first pass (lines 643, 1018), 4 more FLSA wage-and-hour spots found and corrected second pass (lines 627, 966, 1053, 1086), and 3 FMLA spots found and corrected second pass (lines 720, 736, 1032) with a distinct structural note: FMLA's liquidated-damages doubling (29 U.S.C. Sec 2617(a)(1)(A)(iii)) is the same 2x principle as FLSA but a different statute, and FMLA lacks FLSA's DOL-administrative-settlement pathway at scale, so FLSA's administrative-vs-litigation escalation framing does not carry over to FMLA content. Of the original 4 spots first flagged for the DOL figure/mechanism-caveat fix, only 2 (643, 1018) ever contained multiplier language -- 626 and 1124 never stated one and needed no correction, confirmed by direct re-check rather than assumed. | This session (Claude Code) | Closed -- no further check-in |''',
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
