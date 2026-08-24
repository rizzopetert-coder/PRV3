# Candidate C Re-evaluation — Correction: Already Shipped, Not Open for Re-evaluation

Date: 2026-08-24. This task item was framed as "direction was held, then reversed — re-evaluation is live." Direct verification finds this doesn't match current reality — flagged explicitly per standing instruction, rather than either redoing already-completed work or silently skipping the item.

## What's actually true, confirmed directly against live code

Candidate C (`invisible_performance_management` / `the_unexamined_algorithm` differentiation) is **shipped and closed**, this session, commit `322ea93`. Confirmed by reading the real, current values directly from `engine/data/states.py` via a live Python import — not cited from the MOB narrative:

```
IPM authority_liability: 0.2   (was 0.25 — matches the shipped change exactly)
UEA aptitude_liability:  0.3   (was 0.35 — matches the shipped change exactly)
```

This matches the full history already on record: the built_to_fail own-profile-loss investigation confirmed the original hold-reason was permanently unavailable (not just pending), Pete's sequencing decision was to ship as originally designed, a final re-evaluation against the current baseline confirmed the case byte-identical to every prior audit, and it shipped. The SCD-WCS Decision Register row in `tools/_mob.txt` was updated with this closure this session.

## The likely source of this task item's framing

"Direction was held, then reversed" is an accurate description of Candidate C's *history* — it was genuinely held pending sequencing, and Pete's decision genuinely reversed that hold, resulting in it shipping. But that history describes an event that already **concluded** (the hold was reversed *toward shipping*, and shipping already happened), not an *ongoing, still-open* re-evaluation. The task's phrasing "re-evaluation is live" appears to describe a state that was accurate earlier in this multi-session arc but is no longer current — the same class of staleness this whole session has been built around catching, just this time in a task instruction rather than in the MOB itself.

## What this means for the rest of this item's ask

The task also asked to "re-run the relevant validation (same standard as the built_to_fail/invisible_performance_management magnitude-vs-geometry work — concentration sweep, cross-validation, not a single-pass check)" and "report a definitive recommendation." Given Candidate C is already shipped, re-running that validation now would be re-litigating a closed decision, not resolving an open one — not done here, consistent with the standing project discipline of not reopening locked decisions without a real reason to. If Pete intended something else by this item (e.g., re-evaluating whether the *shipped* Candidate C values need further adjustment in light of Item 7's tie-break finding or Item 10's taxonomy-wide scoping work below), that's a distinct, new question — not what "re-evaluation" of the original hold/ship decision would mean, and would need to be stated as its own task rather than assumed here.

**No action taken on Candidate C's actual values.** Reported as a correction, per the explicit instruction to flag contradictions rather than silently absorb them.
