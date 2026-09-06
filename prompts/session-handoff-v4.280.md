# Session Handoff — MOB v4.280

**This file supersedes `prompts/session-handoff-v4.279.md`.** That file was written earlier the same session (2026-09-05), before the Quarterly Step-Back ran on top of it. Both are kept per the standing additive-only convention (never overwritten) — this one is the current latest.

Direct extract/reformat of `tools/_mob.txt` Section 16's final closeout entry for this session ("QUARTERLY STEP-BACK... second run under the dual-sourced format"). Section 16 is authoritative if these ever diverge.

---

## Files to attach next session

- `tools/_mob.txt` — always.
- `CLAUDE.md` — always.
- `prompts/prv3-quarterly-step-back-2026-09-05.md` — if resuming any of the three new decision items below.
- If picking up primary-statute verification for the ~30 remaining PARTIAL coverage-threshold states: `engine/friction_tax.py` and `prompts/state-coverage-threshold-design.md`.

## What happened this session, in one line

Four workstreams (STATE_CAUSATION_OVERRIDES closure, silosolation fix, coverage-threshold gate build, Vercel cleanup) closed out earlier the same day (`session-handoff-v4.279.md`), then a full dual-sourced Quarterly Step-Back ran on top — one day before it was due, and only because Pete manually triggered it.

## Quarterly Step-Back — key outcome

Full record: `prompts/prv3-quarterly-step-back-2026-09-05.md`. Both Claude.ai's initial assessment and Claude Code's independent cold verification converged on the same honest read: **the engineering is verifiably rigorous and improving; whether the product works for anyone besides Pete remains genuinely unanswered** — not avoided, just never yet forced to an answer.

**One overstated claim corrected:** Claude.ai's assessment stated as settled fact that production's Redis aggregate list is "entirely test sessions." Neither pass could re-verify this — Production's credentials are properly Sensitive-masked. What was independently confirmed instead: zero mentions of any real signed client anywhere in tracked MOB history. That absence, not the specific carried-forward count, is the real verified fact.

**Three genuinely new findings from the cold pass**, now tracked as their own Section 13a rows (not just narrative):
1. Today's coverage-threshold gate build has **zero live effect** — `compute_legal_compliance_exposure()` isn't wired into any client-facing output path.
2. Preview's Redis credentials are plaintext-retrievable via `vercel env pull`; Production's are properly masked — a real asymmetry.
3. `prv-3`'s live `ssoProtection` config (`"all_except_custom_domains"`) doesn't match observed unauthenticated live access — unreconciled.

## New open items (Section 13a/13b — discoverable without reading the full Step-Back file)

- **Decide whether to wire the Legal/Compliance module into live output** — a real product decision, code is ready either way.
- **Fix the Preview Redis credential exposure** (flag it Sensitive in the Vercel dashboard).
- **Resolve the `ssoProtection` discrepancy** before trusting either the config or the observed behavior as production's real access-control truth.
- **`extreme_high_confidence` calibration tier at 0/1** (Priority Queue item 9) — worth a dedicated investigation, not urgent.
- **OSHA backfill figure corrected in the Priority Queue itself** (item 7): 17 states need backfill, not the previously-tracked "14."
- **Priority Queue items 1 and 3 corrected** — both had been claiming "no automated tests" since before 2026-08-26, contradicting item 2's own already-accurate correction. Fixed in place this session.

## Cadence

Next Quarterly Step-Back due on or near **September 19, 2026** (biweekly from this run) — `CLAUDE.md` updated accordingly. This one did not fire on its own; worth watching whether the next one does.
