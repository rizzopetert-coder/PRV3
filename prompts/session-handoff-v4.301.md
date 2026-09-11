# Session Handoff — MOB v4.301

Direct extract/reformatting of `tools/_mob.txt` Section 16's 2026-09-11
closeout entry (built_to_fail drift investigation). Section 16 is
authoritative; this file is a portable copy for quick reference at the
start of the next session, not an independent record.

## One-line summary

Root-caused the `built_to_fail` false-rank-1 drift carried at MOB v4.300
Priority Queue item 1. The "52/175 -> 80/175" figure in that record was
wrong — the real, twice-confirmed number is 70/175; the incidental "80"
observed during EXP-IPM-02 reflected a stale intermediate state, not a
fresh HEAD measurement. Full decomposition of the confirmed 52 -> 70
drift completed via isolated git worktrees at every contributing commit.
**No engine code changed this session** — the one concretely identified
fix candidate (`the_arbitrary_standard`'s primary_dimension label
desync) turned out to already be shipped in `49f8796` (2026-09-10, the
prior session), confirmed directly via `git show` before writing
anything further.

## Shipped this session

**MOB correction only, no engine change.** `tools/_mob.txt` Priority
Queue item 1 corrected with the full drift decomposition:

- **+10** (Candidate C, `322ea93`) — deliberate, understood, not a bug.
- **+18** (`f88a7c2`, five-state re-authoring) — only **+2** directly
  attributable to this commit (`the_arbitrary_standard`'s
  primary_dimension desync). The remaining **+16** is a confirmed real
  ripple across 13 states this commit never touched — mechanism not
  identified, now its own scoped item (see Priority Queue below).
- **-10** (`49f8796` + `e8f82a8`, both 2026-09-10, before this
  investigation began) — fixed a bug already baked into Phase 9's own
  original 52 baseline (a legacy byte-identical vector duplicate between
  `built_to_fail` and `the_paper_tiger`'s pre-`f88a7c2` vector), not new
  damage from this drift's own commit range.

Background, out of scope, not actioned: `the_second_close` loses 3 of
its own profiles to `built_to_fail` constantly across every commit
checked, unrelated vector shapes — a separate, pre-existing, flat
problem already noted in a prior MOB entry.

**Verification discipline note:** this session's own mid-investigation
notes initially proposed a code fix for `the_arbitrary_standard`'s
label. Checked before writing anything — `git show 49f8796 --
engine/data/states.py` showed it was already correct, fixed the day
before. Surfaced to Pete via AskUserQuestion rather than silently
applying a no-op fix or dropping the discrepancy.

## Status: built_to_fail false-rank-1 drift — CLOSED

The specific drift Pete asked about (52 → 80/70) is now fully explained
and corrected in the record. One new, explicitly-scoped item opens in
its place (the 16-profile ripple, below) — it is a different, newly
discovered mechanism, not a reopening of this one.

## Updated Priority Queue

1. ~~`built_to_fail` false-rank-1 baseline drift~~ — CLOSED this
   session, see above.
2. **NEW** — `built_to_fail`'s 16-profile ripple from `f88a7c2`.
   Confirmed real (16 of 175 profiles across 13 unrelated states),
   mechanism not identified. Needs its own dedicated investigation
   session, not a quick follow-up.
3. AssemblyPanel/CTA merge (Option C) — design pass, not urgent.
4. `invisible_performance_management` thin question-wiring — low
   priority, revisit if the calibration bar tightens.
5. `invisible_performance_management`/`the_founders_grip` vector
   duplicate — latent, no urgency.
6. `_oh_is_small_employer()` — built and tested, not wired in. Revisit
   when a real OH pricing path is scoped.
7. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) — documented
   approximation, revisit only if wired into a real pricing path.
8. **Quarterly Step-Back** — last run August 22 per this queue's own
   carried-forward text, now multiple sessions overdue. Flag prominently
   at next session open.

## Files to attach next session, by likely task

- **Always:** `tools/_mob.txt` (current version), `CLAUDE.md`.
- **If picking up the `built_to_fail` 16-profile ripple investigation:**
  `tools/calibration_runner.py`, `engine/data/states.py`,
  `engine/data/salience.py` — expect to need git worktrees at `322ea93`
  and `f88a7c2` again for per-profile winner diffs, same method used
  this session.
- **If picking up the AssemblyPanel/CTA merge (Option C):**
  `web/app/diagnostic/page.tsx`, `web/components/AssemblyPanel.tsx`.
- **If wiring `_oh_is_small_employer()` into a real pricing path:**
  `engine/friction_tax.py`, `engine/data/intake.py` (if net_worth/
  economic_loss ever get added).
- **If running the overdue Quarterly Step-Back:** no specific files —
  full project assessment per the dual-sourced format (CLAUDE.md's own
  Quarterly Step-Back section).
