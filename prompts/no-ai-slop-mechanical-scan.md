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

**Tier 2 progress: `candor-as-an-organizational-variable.md` fixed (28 → 7
em-dashes).** This one carried a real citation-accuracy problem, not just
missing names — the live text attributed three genuinely separate Gallup
studies (65,672 employees/14.9% turnover; 530 work units/12.5%
productivity; 469 business units/8.9% profitability) to "the same
research." Independently confirmed via WebSearch before applying: these
are three distinct studies with different sample sets, and Gallup's "How
Fast Feedback Fuels Performance" report (also independently confirmed
real) is the correct named source for the separate 3.6x/80% frequency
claim. Fixed to attribute each figure to its own source.

**Side effect worth flagging so it isn't misread as regression:** this
file's own weasel-attribution count in the mechanical scan rose from 2 to
4 hits after the fix, not down. All 4 are the same class of false positive
already on record for `when-the-data-points-at-the-person-who-hired-you.md`'s
"Amy Edmondson" case — the regex only recognizes a named source when a
parenthetical year sits in the same sentence; prose-style attribution
("Gallup's research on...", "Separate Gallup studies found...") names the
real source just as validly but doesn't match that narrow shape. The fix
made the article's sourcing *more* explicit (more sentences now name
Gallup by name for their specific claim), which paradoxically trips the
narrow pattern more often, not because sourcing got worse. Confirmed by
direct read of all 4 matches, not assumed.

Em-dash-over-cap count: 33 → 32.

**`how-to-tell-if-the-organization-will-actually-change.md` fixed (27 → 8
em-dashes, right at the cap).** Diffed line-by-line against live: every
change is a pure punctuation conversion, em-dash to comma or colon, no
wording or content changed anywhere. No weasel-attribution claims in this
file, nothing to independently verify. Em-dash-over-cap count: 32 → 31.

**`psychological-safety-walked-into-a-meeting.md` fixed (24 → 8
em-dashes), its one weasel-attribution hit resolved.** The live text's
"The research on this is fairly consistent: psychological safety is built
through demonstrated response, not declared intent" is replaced with an
attribution to Edmondson's own follow-up work (*The Fearless
Organization*, 2019), naming her three specific leader behaviors —
setting the stage, inviting participation, responding productively.
Independently confirmed via WebSearch before applying: Edmondson's book
does name exactly these three behaviors, and she's already the piece's
established named authority (cited earlier in the same file for the
original definition) — a correct-attribution fix to an already-real
source, not a new unverified claim. All other diff lines confirmed pure
em-dash-to-comma/colon conversions. Em-dash-over-cap count: 31 → 30.
Weasel-attribution file count: 6 → 5.

**`earned-effectiveness.md` fixed (23 → 8 em-dashes).** Diffed line-by-line
against live: every change is a pure punctuation conversion (mostly
em-dash to colon, matching the piece's heavy use of "X is not Y — it is
Z" definitional constructions; a few to periods/commas), no wording or
content changed anywhere. No weasel-attribution claims in this file.
Em-dash-over-cap count: 30 → 29.

**`hr-is-the-table.md` fixed (21 → 8 em-dashes).** Diffed line-by-line
against live: every change is a pure punctuation conversion (em-dash to
comma or colon), no wording or content changed anywhere, including the
Tracy Keogh/HP opening story. That story's attribution (Tracy Keogh, CHRO
at HP, "HR is the table," referenced on The Talent War Podcast) was
independently verified via WebSearch before applying, confirmed genuine.
No weasel-attribution claims in this file. Em-dash-over-cap count: 29 →
28. Re-run confirms near-duplicate pairs still at 1 and weasel-attribution
file count still at 5, both unaffected by this fix.

**`what-their-resistance-is-actually-telling-you.md` fixed (21 → 8
em-dashes).** This file's chat-pasted copy showed the recurring mojibake
artifact (stray "â" characters in place of em-dashes) and was not trusted
or used. The separately-delivered Downloads copy was confirmed clean
before writing: zero mojibake, em-dash count exactly 8. Diffed
line-by-line against live: every change is a pure punctuation conversion
(em-dash to comma or colon), no wording or content changed anywhere. No
weasel-attribution claims in this file. Em-dash-over-cap count: 28 → 27.
Re-run confirms near-duplicate pairs still at 1 and weasel-attribution
file count still at 5, both unaffected by this fix.

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

**Update (fourth run): the case_pattern cluster is now fully resolved to
one deliberately-accepted pair.** Third run found 3 residual near-duplicate
pairs in this cluster (documented in git history for this file, not
reproduced here); Pete's read on them: the real, broader issue was that 5
of the 6 case_pattern endings shared the same "spend it [gerund]-ing"
grammatical template regardless of topic — exactly the kind of cross-piece
echo a consecutive read would catch even though no two sentences were
identical. `what-ready-didnt-include.md`, `the-first-one-out-the-door.md`,
and `the-resignation-that-ended-a-department.md` were each re-revised to
break the construction (verified byte-clean before applying — no mojibake,
em-dash count unchanged at 7 in all 3, diff confirmed only the closing line
changed). `what-the-organization-decided-he-was-worth.md`'s "hoping"
ending was deliberately left as one instance of the construction, for
variety rather than eliminating it outright.

**Re-ran the scan after applying, not just trusted the diffs — corpus-wide
near-duplicate pairs: 3 → 1.** The one remaining pair is
`built-for-comfort.md`/`one-exception-at-a-time.md` (69% match, shared
"Every organization has that window" opening), explicitly left untouched
by design — it predates this batch, wasn't part of what got flagged, and
reopening already-shipped files without a specific reason wasn't judged
worth it. This is now a settled, deliberate state, not an open item.

---

## Current em-dash count > 8 — 33 of 87 files

Dropped from 37 to 33 with the Tier 1 cluster fix: `what-the-organization-decided-he-was-worth.md`
(was 24), `the-resignation-that-ended-a-department.md` (was 19),
`the-first-one-out-the-door.md` and `what-ready-didnt-include.md` (both
were 14) all now sit at 7, under the cap.

| file | em-dash count | file | em-dash count |
|---|---|---|---|
| candor-as-an-organizational-variable | 28 | the-paper-tiger | 13 |
| how-to-tell-if-the-organization-will-actually-change | 27 | the-untouchable | 13 |
| psychological-safety-walked-into-a-meeting | 24 | succession-planning | 12 |
| earned-effectiveness | 23 | velocity-of-truth | 12 |
| hr-is-the-table | 21 | why-your-team-stopped-disagreeing-with-you | 12 |
| what-their-resistance-is-actually-telling-you | 21 | feedback-nobody-wants-to-say | 11 |
| when-the-data-points-at-the-person-who-hired-you | 21 | no-margin-for-error | 11 |
| symptoms-states-and-why-the-distinction-matters | 20 | the-tolerated-violation | 11 |
| earned-effectiveness-conversation-framework | 19 | dueling-narratives | 10 |
| the-problem-they-brought-you-is-not-always-the-problem | 19 | intellectual-bottleneck | 10 |
| matrix-organization | 17 | narrative-lock | 10 |
| leadership-deafness | 15 | crisis-as-catalyst-for-clarity | 9 |
| the-policy-lag | 15 | the-unformed-leader | 9 |
| the-unlocked-door | 15 | | |
| decision-paralysis | 14 | | |
| the-lost-map | 14 | | |
| the-unreported-hazard | 14 | | |
| accountability | 13 | | |
| groundhog-day | 13 | | |
| the-overloaded-manager | 13 | | |

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
