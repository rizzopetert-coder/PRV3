# No-AI-Slop Mechanical Scan — /book Corpus

Status: **Investigation only. Grep/regex-based counting, not a rewrite, not a
subjective close-read.** Tooling: `tools/diag_book_mechanical_scan.py`
(read-only, reusable). No content edited by this doc or this scan.

**Re-run notice: this is the second, current run.** The first run happened
before the 8-file no-ai-slop fix batch landed live and before the em-dash
signature-line exemption was locked (MOB v4.183); its numbers are now stale
and are not reproduced here. This version reflects the corpus exactly as it
stands after all 8 fixes (`prompts/no-ai-slop-fix-tracking.md`) and the 3
new `book-citations.ts` entries are live. Re-run for one reason: to make
sure the manual-review queue gets built from current state, not against
work that's already done.

**Scope, unchanged from the first run:** the full 87-file published corpus,
confirmed via direct `book-manifest.ts` parse (87 `status: "published"`
entries, all 87 loaded successfully).

---

## What changed since the first run

- **Em-dash-over-cap count dropped from 45 to 37 files.** All 8 just-fixed
  files dropped out of the over-cap list — `built-for-comfort.md` (was 26,
  now 7), `one-exception-at-a-time.md` (was 24, now 7),
  `everyone-is-defensive-and-no-one-knows-why.md` (was 12, now 8),
  `the-room-that-never-pushes-back.md` (was 10, now 8), `toxic-culture.md`
  (was 17, now 8), `silosolation.md` (was 16, now 8), `anchor.md` (was 16,
  now 8), `why-blaming-the-person-almost-never-fixes-the-problem.md` (was
  14, now 8). All 8 land exactly at the ≤8 cap, none under-shoot it.
- **Near-duplicate closing pairs dropped from 39 to 8.** The
  `built-for-comfort.md`/`one-exception-at-a-time.md` pair no longer
  100%-matches (each now has a piece-specific ending) — they now show only a
  69% match on the shared "Every organization has that window" opening
  clause, which both pieces still use verbatim (see the still-open cluster
  below). The `toxic-culture.md`/`silosolation.md` exact-duplicate kicker
  pair is fully gone — both now have distinct, piece-specific closings.
- **Weasel-attribution count for `why-blaming...md` dropped from 5 to 1.**
  The 4 originally-flagged unnamed claims are now named citations, confirmed
  present in the live text. One residual hit remains, addressed below —
  it's a shape-only false-positive, not a real finding.
- **`why-blaming...md`'s binary-contrast count rose to 6** (wasn't in the
  ≥3 list at all in the first run). The added citation paragraphs introduced
  new "not X. It's Y."-shaped sentences as part of the real content fix, not
  something to chase — informational only, per the standing "not a required
  fix" framing for this metric.

**Still open, unresolved by this batch:** a **4-file cluster** —
`what-the-organization-decided-he-was-worth.md`,
`the-resignation-that-ended-a-department.md`, `what-ready-didnt-include.md`,
`the-first-one-out-the-door.md` — still shares the "Every organization has
that window..." closing, 3 of the 4 pairs at 100%/67%/64% match. This is
exactly the cluster `prompts/no-ai-slop-fix-tracking.md` already flagged as
"three more likely affected" (plus `what-ready-didnt-include.md`, which
turns out to already share the exact line too) — not new, but now the
*only* remaining instance of this specific duplicate, since the other two
case_pattern files that had it are fixed.

---

## Current em-dash count > 8 — 37 of 87 files

| file | em-dash count | file | em-dash count |
|---|---|---|---|
| candor-as-an-organizational-variable | 28 | accountability | 13 |
| how-to-tell-if-the-organization-will-actually-change | 27 | groundhog-day | 13 |
| psychological-safety-walked-into-a-meeting | 24 | the-overloaded-manager | 13 |
| what-the-organization-decided-he-was-worth | 24 | the-paper-tiger | 13 |
| earned-effectiveness | 23 | the-untouchable | 13 |
| hr-is-the-table | 21 | succession-planning | 12 |
| what-their-resistance-is-actually-telling-you | 21 | velocity-of-truth | 12 |
| when-the-data-points-at-the-person-who-hired-you | 21 | why-your-team-stopped-disagreeing-with-you | 12 |
| symptoms-states-and-why-the-distinction-matters | 20 | feedback-nobody-wants-to-say | 11 |
| earned-effectiveness-conversation-framework | 19 | no-margin-for-error | 11 |
| the-problem-they-brought-you-is-not-always-the-problem | 19 | the-tolerated-violation | 11 |
| the-resignation-that-ended-a-department | 19 | dueling-narratives | 10 |
| matrix-organization | 17 | intellectual-bottleneck | 10 |
| leadership-deafness | 15 | narrative-lock | 10 |
| the-policy-lag | 15 | crisis-as-catalyst-for-clarity | 9 |
| the-unlocked-door | 15 | the-unformed-leader | 9 |
| decision-paralysis | 14 | | |
| the-first-one-out-the-door | 14 | | |
| the-lost-map | 14 | | |
| the-unreported-hazard | 14 | | |
| what-ready-didnt-include | 14 | | |

**Note on the signature-line exemption (MOB v4.183):** none of these 37
files use the `"— Principal Resolution"` closer, so none of these counts
need adjustment — the exemption only affects the 12 files that use that
closer (`accountability.md` through `the-untouchable.md` above are the
exception — 6 of the 12 closer-files are still over cap even after
subtracting the signature line; see the dedicated table below).

### The 12 files using the `"— [Author Name]"` closer — prose-only counts

| file | raw | prose (minus signature) | status |
|---|---|---|---|
| accountability.md | 13 | 12 | over cap |
| leadership-deafness.md | 15 | 14 | over cap |
| matrix-organization.md | 17 | 16 | over cap |
| no-margin-for-error.md | 11 | 10 | over cap |
| succession-planning.md | 12 | 11 | over cap |
| the-untouchable.md | 13 | 12 | over cap |
| silosolation.md | 8 | 7 | **ok — fixed this batch** |
| toxic-culture.md | 8 | 7 | **ok — fixed this batch** |
| business-case.md | 7 | 6 | ok |
| exit-pattern.md | 5 | 4 | ok |
| the-basement-standard.md | 7 | 6 | ok |
| the-broken-compass.md | 7 | 6 | ok |

`candor-as-an-organizational-variable.md` and
`symptoms-states-and-why-the-distinction-matters.md` do **not** use this
closer (confirmed by direct read of each file's actual last line in the
prior session) — their raw counts (28, 20) are genuine unadjusted prose,
already reflected correctly in the main table above.

---

## Binary-contrast count ≥ 3 — 59 of 87 files (informational, no fix required)

Unchanged in total count from the first run; individual numbers shifted for
the 8 fixed files as a side effect of their content changes, not a target of
this metric. Top of the list, unchanged in substance:

| file | count |
|---|---|
| what-their-resistance-is-actually-telling-you | 13 |
| when-the-data-points-at-the-person-who-hired-you | 11 |
| hr-is-the-table | 10 |
| what-not-to-document | 10 |
| candor-as-an-organizational-variable | 9 |
| earned-effectiveness-conversation-framework | 9 |
| feedback-nobody-wants-to-say | 9 |

**Standing correction, still valid:** `what-not-to-document.md` (10
instances) is clean on em-dash/formatting but not on binary contrast — see
the original scan doc's finding, unchanged by this re-run.

Full current per-file counts: reproducible via `tools/diag_book_mechanical_scan.py`'s stdout.

---

## Weasel attribution — 6 of 87 files, one real residual worth a look

| file | hits | detail |
|---|---|---|
| why-blaming-the-person-almost-never-fixes-the-problem | 1 | Residual: `"This is the same finding research on training and behavior change keeps producing, with real numbers attached."` — the sentence *immediately following* this one now names the real source (Blume, Ford, Baldwin & Huang, 2010) for the numbers being introduced. Shape-only false positive — the pattern flags "research...keeps producing" without a same-sentence name, but the name is one sentence later, attached to the actual figures. Not a real remaining weasel-attribution problem. |
| candor-as-an-organizational-variable | 2 | Unchanged from first run — "In a study of 65,672 employees..." and "The same research found..." — neither names the study/source in-sentence. |
| intellectual-bottleneck | 1 | Unchanged — "Research on power and social cognition shows..." — no named source. |
| leadership-deafness | 1 | Unchanged — "The research on this is brutal." — no named source, no citation. |
| psychological-safety-walked-into-a-meeting | 1 | Unchanged — "The research on this is fairly consistent..." — no named source. |
| when-the-data-points-at-the-person-who-hired-you | 1 | Unchanged, already-established false positive — "Amy Edmondson's foundational research..." names a real source, just without a same-sentence year. |

---

## Near-duplicate closing paragraphs — 8 pairs, all one cluster

All 8 pairs are permutations within the same 4-file group:
`what-the-organization-decided-he-was-worth.md`,
`the-resignation-that-ended-a-department.md`, `what-ready-didnt-include.md`,
`the-first-one-out-the-door.md`. Strongest matches:

| match | files |
|---|---|
| 100% | what-the-organization-decided-he-was-worth.md ↔ what-ready-didnt-include.md |
| 100% | the-resignation-that-ended-a-department.md ↔ what-ready-didnt-include.md |
| 74% | what-the-organization-decided-he-was-worth.md ↔ the-resignation-that-ended-a-department.md |
| 67% | the-first-one-out-the-door.md ↔ what-ready-didnt-include.md |
| 64% | the-first-one-out-the-door.md ↔ the-resignation-that-ended-a-department.md |

This is precisely the cluster `prompts/no-ai-slop-fix-tracking.md` already
named as the next piece of known work — nothing new surfaced here, this
confirms the fix-tracking doc's own scoping was accurate and it's now the
only remaining instance of this duplicate pattern in the corpus (the
`built-for-comfort.md`/`one-exception-at-a-time.md` and
`toxic-culture.md`/`silosolation.md` pairs are both resolved).

---

## Explicitly not done here

No content edited. No decision made about which files to prioritize beyond
what's below — see the queue recommendation in this session's chat summary.
