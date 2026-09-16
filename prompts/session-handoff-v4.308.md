# Session Handoff — MOB v4.308

Direct extract/reformatting of `tools/_mob.txt` Section 16's second
2026-09-16 closeout entry. Section 16 is authoritative; this file is a
portable copy for quick reference at the start of the next session, not
an independent record.

## One-line summary

An unusually long, dense session — one planned build (item 9) that
expanded into original statutory and data research well beyond its
original scope, plus three items surfaced live during the session
itself (12, 13, 14), none planned in advance. Items 5, 7, 8, 9, 12, 13,
and 14 are all **CLOSED**; item 10 is status-corrected (live/
consequential, not resolved); item 11 is untouched, still due next
week, not overdue.

## Status breakdown

1-4, 6. Unchanged since the prior closeout (v4.304) — see `tools/_mob.txt`.
5, 7, 8. CLOSED — unchanged since v4.304, restated for completeness.
9. **CLOSED — see dedicated sub-summary below, two distinct pieces.**
10. NAICS-vs-"Manufacturing & Industrial" mapping gap (OH) — status
    remains corrected, not resolved: live and consequential in a real
    pricing path today, the underlying gap itself untouched.
11. Quarterly Step-Back — untouched this session, still due next week
    per Pete's prior correction. Not overdue.
12. Share-link 500 "Corrupt record" — **CLOSED.** `@upstash/redis`'s
    `automaticDeserialization` default double-parsed an already-parsed
    value, dated to the June 13 2026 Upstash migration (`2d2da5d`),
    fixed commit `5e04d4b`.
13. Share PAGE still 404'd after item 12's fix — **CLOSED.** A second,
    independent bug: the page's own internal self-fetch to
    `process.env.VERCEL_URL` blocked by this project's `ssoProtection`
    setting. Fixed via a shared `web/lib/share-store.ts` Redis read,
    commit `fd70585`.
14. "Contact us" CTAs never functional — **CLOSED.** The diagnostic's
    "Start a conversation" button had no `onClick` at any point since
    the project's first web-layer commit; `/ask`'s working mailto was
    unreachable from anywhere in the live site. Both wired/linked,
    commit `023447f`.

## Item 9, in detail — two distinct pieces, both Gemini-reviewed twice

**(a) OH compensatory-damages pricing.** Engine wiring — Ohio's real
R.C. 2315.21 formula into Clusters 1, 2, 4b via
`_oh_compensatory_damages_pricing()`, commit `2dff83f` — plus UI
framing — `has_uncollected_net_worth_caveat` propagated end-to-end,
commit `eec2e1b`. First Gemini review: the original architecture-gate
design pass. Second: the verification pass that caught the Texas
`is_floor` "precedent" fabrication (see verification pattern below).

**(b) The `is_floor` arc.** A follow-on investigation found one caveat
sentence couldn't honestly cover all 32/36 `is_floor` jurisdictions —
three genuinely different situations bundled under one flag. Shipped 7
verified per-state caveats: FL/ID/KS/VA's flat_cap component-vs-total
mismatch, AR/MD/TN's verified statutory carve-outs, commit `e643bfd`.
DE and CO were researched and explicitly excluded, not overlooked — DE
because no carve-out was found in either direction, CO because its own
good-faith-defense mechanism points the opposite direction from every
other caveat in the set. First Gemini review: the per-state-caveat
lookup design, before any code was written. Second: the verification
pass that caught the `SEVERITY_TIER_DESCRIPTIONS` misattribution (see
below).

## Items 12, 13, 14 — not planned, worth stating plainly

All three are pre-existing production issues, unrelated to tonight's
item 9/10 work, caught only through live verification:

- **12 and 13** were found because Pete tested a real production share
  link mid-session and it 404'd — a live user action, not a scheduled
  check.
- **14** was Pete noticing a dead "Contact us" button in the live
  product.
- All three predate this session by weeks to months — item 14 since
  the project's literal first commit — and were simply never caught
  until someone actually clicked the real thing in production.

## Verification pattern worth carrying forward

This session's real find rate came from checking live behavior, not
from planning:

- **Three Gemini fabrications**, each a distinct failure mode: a
  jurisdiction/mechanism conflation (the original `is_floor` "may
  understate" framing), an invented `is_floor` "precedent" tied to the
  wrong state (Texas, when the actual mechanism is a blanket
  category-wide default, not a purpose-built flag), and a
  misattributed file location (`SEVERITY_TIER_DESCRIPTIONS` cited as
  living in `contract.py`; it actually lives in `engine/severity.py`).
- **One clamp miscalibration**, caught only by looking at the real
  computed data: the OH jurisdiction multiplier's first-pass 0.8x-1.2x
  clamp pinned 78% of all 51 jurisdictions to one bound against the
  real EEOC/QCEW distribution.
- **Two live production bugs** (items 12/13's share-link failures, and
  item 14's dead button) that static code review would not have
  caught — both required an actual click-through against the real
  deployed app.

None of these five findings were anticipated at session start. The
pattern across all of them: verify against the live, real thing
(production behavior, real computed numbers, primary source) before
treating a claim, a calibration, or a shipped feature as confirmed.

## Files to attach next session, by likely task

- **Always:** `tools/_mob.txt` (current version), `CLAUDE.md`.
- **No current open item requires other files pre-attached.** Items 5,
  7, 8, 9, 12, 13, and 14 are closed; item 10 is dormant until
  something wires into it; item 11 isn't yet due and needs no specific
  files (a full project assessment, per its own dual-sourced format).
