"""
PRV3 -- Record Pete's ratification of all seven candidate-to-state
mappings as final disposition, closing the item first flagged Session
63 (no P-10 rename log; trace's Signal Map/QSM matches were inference,
not a confirmed Pete decision). Documentation only -- no engine/ or
web/ changes, no taxonomy modifications; the states already exist and
are unchanged.

Located the item in Section 13's open-items table (line ~1239, "
Consolidation mapping — seven experiments to 47-state taxonomy"), not
as a separate Section 13a Decision Register row -- confirmed via
direct grep, only two matches for the relevant language exist in the
file: this table row and the historical Session 63 log entry (left
untouched, append-only per established convention).

Also closes this row's OTHER stale claim while here: its text still
said E2/E3/E6/E7 consolidation-mapping was "the actual remaining
work," but that was itself closed at Session 65 (44 raw candidates,
all final dispositions) -- confirmed via the MOB's own S65 log entry.
Pete's own task instructions independently referenced "consolidation-
mapping effort S65" as an already-closed item, consistent with fixing
this here rather than leaving an internally contradictory row (closed
on one point, silent-stale on the other).

Updates Section 13b's Priority Queue item 8 to drop the now-closed
sub-items from its description, per Pete's exact drafted text.

Usage:
  python tools/patch_mob_seven_candidates_ratified.py --dry-run
  python tools/patch_mob_seven_candidates_ratified.py --write
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

# ---------------------------------------------------------------------
# 1. Version bump
# ---------------------------------------------------------------------

edit(
    MOB,
    "\\\\\\#\\\\\\# MOB v4.96",
    "\\\\\\#\\\\\\# MOB v4.97",
)

# ---------------------------------------------------------------------
# 2. Section 13 open-items table row -- close it, record the ratification
# ---------------------------------------------------------------------

edit(
    MOB,
    '| Consolidation mapping — seven experiments to 47-state taxonomy | PARTIALLY CLOSED. The Squeeze, E1 (10/10 candidates), E4 (10/10), and E5 (8/8) fully resolved and committed — research/seven-experiments/consolidation-mapping-trace.md, commit 806b0121 (2026-06-26). Confirmed drops: Purpose Deficit (eliminated), Workforce Planning Myopia (collapsed into Reactive Talent Management). Remaining open scope is narrower than previously stated: E2 (Litigation), E3 (Glassdoor/Indeed), E6 (HR Conference), E7 (Org Psych) have no consolidation-mapping output yet — that is the actual remaining work, not a from-scratch ~80-candidate trace. Separate open question the trace itself surfaced, unresolved by this audit: seven candidates marked "STATE — survives" in the original 108-candidate filter run (Manager Investment Failure, Market Exposure, Values Misrepresentation, Implementation Courage Deficit, Disclosure Misalignment, Safety Culture Deficit, Security Culture Gap) do not appear under any name in taxonomy.ts, and no P-10 rename log exists to explain it. The trace proposes high-confidence matches to existing states via Signal Map/Question Signal Map cross-reference, but this is inference, not a confirmed Pete decision or documented rename — genuine open question for Pete. |',
    '| Consolidation mapping — seven experiments to 47-state taxonomy | CLOSED (this session). The Squeeze, E1 (10/10 candidates), E4 (10/10), and E5 (8/8) fully resolved and committed — research/seven-experiments/consolidation-mapping-trace.md, commit 806b0121 (2026-06-26). Confirmed drops: Purpose Deficit (eliminated), Workforce Planning Myopia (collapsed into Reactive Talent Management). E2/E3/E6/E7 consolidation-mapping (previously listed here as "the actual remaining work") was itself closed at Session 65 (44 raw candidates, all final dispositions, badge-verified) — this row\'s prior "remaining scope" framing was stale, corrected here. **RATIFIED this session:** the seven candidates marked "STATE — survives" in the original 108-candidate filter run (Manager Investment Failure, Market Exposure, Values Misrepresentation, Implementation Courage Deficit, Disclosure Misalignment, Safety Culture Deficit, Security Culture Gap) are confirmed as Pete\'s final disposition, mapped respectively to the_dormant_talent, pay_exposure, the_culture_that_wasnt, the_broken_compass, dueling_narratives, the_unreported_hazard, the_unlocked_door. This is the exact genuine open question Session 63 flagged (no P-10 rename log exists; the trace\'s Signal Map/Question Signal Map cross-reference was inference, not a confirmed Pete decision) — now resolved by explicit ratification, not silently assumed. Evidentiary basis, recorded accurately rather than as a uniform "all seven equally confirmed": six of seven (Manager Investment Failure, Market Exposure, Values Misrepresentation, Implementation Courage Deficit, Disclosure Misalignment, Security Culture Gap) were backed by direct quote-to-quote mechanism matches between the original filter run and the Signal Map/QSM. The seventh, Safety Culture Deficit -> the_unreported_hazard, rested on categorical/structural placement only (presumed "safety branch" of a document that also has a security branch), with no direct quote-level echo of the original candidate\'s own language — genuinely weaker evidence than its six siblings. Pete reviewed this specific distinction (surfaced via this session\'s research pass) and ratified all seven anyway, including this one, with the evidentiary gap explicitly disclosed before the decision, not glossed over — if this mapping is ever revisited, the record should show it was a known-weaker case ratified with eyes open, not a mapping nobody noticed was thinner. Closes the consolidation-mapping thread of the seven-experiments-to-methodology-series workstream entirely. |',
)

# ---------------------------------------------------------------------
# 3. Section 13b Priority Queue item 8 -- drop closed sub-items
# ---------------------------------------------------------------------

edit(
    MOB,
    "8. The seven-experiments-to-methodology-series workstream (citation audit prioritizing E2/E5/E7, two-question test pass, consolidation-mapping against 57-state taxonomy, PCD-as-editorial-throughline framing decision).",
    '8. The seven-experiments-to-methodology-series workstream -- remaining open items: PCD-as-editorial-throughline framing decision; three unaudited Gemini citations (Gallup 2026 "$10 trillion" figure, a 2024 psych-safety-scale review citing 217 studies, a 2023/24 safety-culture meta-analysis citing 136 samples). Citation audit (S61), two-question test pass (S54), and consolidation-mapping against the 57-state taxonomy (S65 for E2/E3/E6/E7; seven-candidate ratification this session) are all closed -- dropped from this item\'s description accordingly.',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
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
