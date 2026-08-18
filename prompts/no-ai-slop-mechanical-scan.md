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

**`when-the-data-points-at-the-person-who-hired-you.md` fixed (21 → 8
em-dashes).** Same mojibake pattern again in the chat-pasted copy, again
not trusted or used. The separately-delivered Downloads copy was
confirmed clean before writing: zero mojibake, em-dash count exactly 8.
Diffed line-by-line against live: every change is a pure punctuation
conversion (em-dash to comma or colon), no wording or content changed
anywhere. Both Amy Edmondson references are left untouched by the fix;
this file's one weasel-attribution hit on the first reference remains
the already-established false positive (real named source, no
same-sentence parenthetical year), not a new finding. Em-dash-over-cap
count: 27 → 26. Re-run confirms near-duplicate pairs still at 1 and
weasel-attribution file count still at 5.

**`symptoms-states-and-why-the-distinction-matters.md` fixed (20 → 8
em-dashes).** Same mojibake pattern again in the chat-pasted copy, not
trusted or used. The separately-delivered Downloads copy was confirmed
clean before writing: zero mojibake, em-dash count exactly 8. The live
file is CRLF and the Downloads file is LF, which made the raw diff look
like a full rewrite; re-diffed with `--strip-trailing-cr` to confirm the
real content changes are all pure punctuation conversions (em-dash to
colon or comma), no wording changes. CRLF preserved on write (Windows
Python's `write_text` translates `\n` to the platform line separator by
default, matching every prior fix in this batch).

**Flagged, not fixed: stale state count.** The piece states "Principal
Resolution has identified fifty-seven institutional states." Confirmed
against the live MOB (`tools/_mob.txt`, `the_inner_circle` taxonomy
expansion row): the locked engine state count is 58, with
`the_inner_circle` added as the 58th state. "Fifty-seven" is a stale
pre-expansion figure. Left untouched in this pass per instruction, held
for Pete's call as a separate, deliberate correction, not folded into
the em-dash cleanup. Em-dash-over-cap count: 26 → 25. Re-run confirms
near-duplicate pairs still at 1 and weasel-attribution file count still
at 5.

**`earned-effectiveness-conversation-framework.md` fixed (19 → 8
em-dashes).** Same mojibake pattern again in the chat-pasted copy, not
trusted or used. The separately-delivered Downloads copy was confirmed
clean before writing: zero mojibake, em-dash count exactly 8. Diffed
against live (`--strip-trailing-cr`, live CRLF vs. source LF): one change
was caught that was not a pure punctuation conversion and not disclosed
as part of the fix -- the section heading "Why the sequence gets
shortcut — and what it costs" (sentence case, matching the file's other
three headings) became "Why the Sequence Gets Shortcut: What It Costs"
(title case). Flagged to Pete before applying; confirmed apply-as-
delivered. Em-dash-over-cap count: 25 → 24. Re-run confirms near-
duplicate pairs still at 1 and weasel-attribution file count still at 5.

**`symptoms-states-and-why-the-distinction-matters.md` — "fifty-seven" →
"fifty-eight" correction applied on top of the em-dash fix (73c577e).**
Supersedes only the state-count figure flagged in that fix, per Pete's
confirmation against the live MOB. Chat-pasted copy again showed the
mojibake artifact and was not used; Downloads copy confirmed clean,
diffed against the currently-live file, and the only change present was
the single word swap, nothing else touched. Em-dash count unaffected
(still 8) — no change to the em-dash-over-cap total or any other
mechanical-scan metric.

**`the-problem-they-brought-you-is-not-always-the-problem.md` fixed
(19 → 8 em-dashes).** Same mojibake pattern again in the chat-pasted
copy, not trusted or used. The separately-delivered Downloads copy was
confirmed clean before writing: zero mojibake, em-dash count exactly 8.
Diffed against live (`--strip-trailing-cr`): every change is a pure
punctuation conversion (mostly em-dash to colon, one to a period break),
no wording or content changes anywhere. Em-dash-over-cap count: 24 → 23.
Re-run confirms near-duplicate pairs still at 1 and weasel-attribution
file count still at 5.

**`matrix-organization.md` fixed — first of the Tier 3 signature-closer
group (prose 16 → 8 em-dashes; raw, including the exempt
`"— Principal Resolution"` line: 17 → 9).** Chat-pasted copy showed the
mojibake artifact including inside the signature line itself, not
trusted or used. Downloads copy confirmed clean: zero mojibake, raw
em-dash count exactly 9 as claimed (8 prose + 1 exempt signature line,
per the MOB v4.183 exemption). Diffed against live
(`--strip-trailing-cr`): every change is a pure punctuation conversion
(em-dash to colon, comma, or period break), signature line untouched, no
wording or content changes anywhere. The mechanical scan tool itself
doesn't apply the signature exemption, so it still nominally lists this
file at raw count 9 (>8) — the corpus-wide "over cap" total (23) is
unaffected by this fix for that reason, but per the locked exemption
this file's actual prose count is 8, at cap, not over — see the updated
closer-files table below. Near-duplicate pairs and weasel-attribution
file count both still unaffected.

**`leadership-deafness.md` fixed — second Tier 3 signature-closer file
(prose 13 → 8 em-dashes; raw, including the exempt signature line: 14 →
9), plus its one weasel-attribution hit's underlying citation problem
resolved.** Chat-pasted copy showed the mojibake artifact, including
inside the signature line, and was not used. Downloads copy confirmed
clean, raw em-dash count exactly 9 as claimed. The citation fix was
independently verified before applying, not just taken on claim: the
live text's "The research on this is brutal ... it literally changes
your brain" overclaimed Keltner's actual research, which is behavioral
(facial-expression matching, empathy/perspective-taking tasks) — confirmed
via WebSearch against *The Power Paradox*'s actual findings. The
neural/mirror-neuron TMS evidence belongs to a separate study (Obhi,
McMaster University), also confirmed real via WebSearch and never
Keltner's own work. Same overclaim pattern already corrected elsewhere in
the corpus as `HC-103` (confirmed present in `book-citations.ts`, no new
citation entry needed). Fixed to "is consistent ... makes you worse at
reading other people," with "spent decades" corrected to "spent over two
decades," matching Keltner's actual ~20+ year research span. All other
diff hunks are pure em-dash-to-comma conversions, signature line
untouched. The mechanical scan's weasel-attribution hit on this file
persists after the fix ("The research on this is consistent" has no
same-sentence name) — this is the same established shape-only false
positive as the other 4 files on this list; Keltner is named in the very
next sentence. Weasel-attribution file count and near-duplicate pairs
both unaffected.

**`the-untouchable.md` fixed — third Tier 3 signature-closer file (prose
12 → 8 em-dashes; raw, including the exempt signature line: 13 → 9).**
Chat-pasted copy showed the mojibake artifact, including inside the
signature line, and was not used. Downloads copy confirmed clean, raw
em-dash count exactly 9 as claimed. Diffed against live
(`--strip-trailing-cr`): all 3 changes are pure punctuation conversions
(em-dash to colon or comma), no wording changes. No named claims in this
file requiring citation verification. Signature line untouched. Raw scan
tool still lists this file nominally at 9 (>8) since it doesn't apply the
signature exemption — total unaffected, same reason as
`matrix-organization.md`. Weasel-attribution file count and near-
duplicate pairs both unaffected.

**`succession-planning.md` fixed — fourth Tier 3 signature-closer file
(prose 11 → 8 em-dashes; raw, including the exempt signature line: 12 →
9).** Chat-pasted copy showed the mojibake artifact, including inside the
signature line, and was not used. Downloads copy confirmed clean, raw
em-dash count exactly 9 as claimed. Diffed against live
(`--strip-trailing-cr`): exactly 2 changes, one paired-dash aside
converted to commas and one single dash converted to a colon; the other
4 paired-dash asides in the file were left intact, no wording changes. No
named claims in this file requiring citation verification. Signature
line untouched. Raw scan tool still lists this file nominally at 9 (>8)
for the same exemption-blind reason as the prior two Tier 3 fixes — total
unaffected. Weasel-attribution file count and near-duplicate pairs both
unaffected.

**`no-margin-for-error.md` fixed — sixth and final Tier 3 signature-closer
file (prose 10 → 8 em-dashes; raw, including the exempt signature line:
11 → 9). This completes all 12 files in the signature-closer group.**
Chat-pasted copy showed the mojibake artifact, including inside the
signature line, and was not used. Downloads copy confirmed clean, raw
em-dash count exactly 9 as claimed. Diffed against live
(`--strip-trailing-cr`): exactly 2 changes, both pure punctuation
conversions (em-dash to colon, em-dash to comma). The closing paragraph's
deliberate triple "X — have it this week. Y — make it. Z — ask." parallel
construction was left fully intact by design, confirmed absent from the
diff. No named claims requiring citation verification. Signature line
untouched. Raw scan tool still lists this file nominally at 9 (>8) for
the same exemption-blind reason as the other 5 Tier 3 fixes — total
unaffected. Weasel-attribution file count and near-duplicate pairs both
unaffected.

**Correction (superseded below): 5 of 6 originally-over-cap
signature-closer files resolved, not all 6.** The Tier 3 go-ahead message
for `no-margin-for-error.md` said it would close out "all 6 files in the
Tier 3 signature-closer group" — checking that against the closer-files
table before taking it at face value found `accountability.md` (12
prose) still outstanding and never actually sent this session.

**`accountability.md` fixed — the sixth and last originally-over-cap
Tier 3 signature-closer file (prose 12 → 8 em-dashes; raw, including the
exempt signature line: 13 → 9). This now genuinely completes the group.**
Chat-pasted copy showed the mojibake artifact, including inside the
signature line, and was not used. Downloads copy confirmed clean, raw
em-dash count exactly 9 as claimed. Diffed against live
(`--strip-trailing-cr`): exactly 4 changes, all pure punctuation
conversions (em-dash to colon or comma), no wording changes. No named
claims requiring citation verification. Signature line untouched. Raw
scan tool still lists this file nominally at 9 (>8) for the same
exemption-blind reason as the other 5 Tier 3 fixes — total unaffected.

**All 12 signature-closer files now resolved:** `silosolation.md` and
`toxic-culture.md` (fixed in the original 8-file batch), plus
`accountability.md`, `matrix-organization.md`, `leadership-deafness.md`,
`the-untouchable.md`, `succession-planning.md`, and
`no-margin-for-error.md` (fixed this session as Tier 3) all sit at prose
count 8, at cap. `business-case.md`, `exit-pattern.md`,
`the-basement-standard.md`, and `the-broken-compass.md` were already
under cap and untouched. This closes out the Tier 3 queue in full.

**`intellectual-bottleneck.md` fixed — first Tier 4 file (10 → 8
em-dashes).** Chat-pasted copy showed the mojibake artifact, not used.
Downloads copy confirmed clean, em-dash count exactly 8. Before touching
anything, checked a flagged concern that this file's source might live
at a stale PRV2 path (`src/content/library/memo/...`) that never
migrated into the live corpus: that path doesn't exist anywhere in this
repo, and this file is confirmed present, published, and the only copy
(`web/content/book/memo/intellectual-bottleneck.md`, `LIB-049` in
`book-manifest.ts`) — no location ambiguity. The Keltner/power-cognition
claim already matched the corrected `HC-103` wording, so no citation fix
was needed here. Diffed against live (`--strip-trailing-cr`): exactly 2
pure em-dash-to-comma conversions, no wording changes. Em-dash-over-cap
count: 23 → 22. This file's existing weasel-attribution hit is unchanged
(the flagged sentence itself wasn't touched) — file count remains 5.
Near-duplicate pairs unaffected.

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

**Note: the rest of this doc's tables (this one plus "Current em-dash
count > 8" above) reflect corpus state as of the Tier 1 cluster fix and
have not been hand-synced against every fix since. The addenda paragraphs
above this section are the current, authoritative record — the tables
are being left as a historical snapshot rather than rewritten piecemeal.
Live numbers are always reproducible via `tools/diag_book_mechanical_scan.py`.**

| file | raw | prose (minus signature) | status |
|---|---|---|---|
| accountability.md | 9 | 8 | **ok — fixed this batch (Tier 3)** |
| leadership-deafness.md | 9 | 8 | **ok — fixed this batch (Tier 3)** |
| matrix-organization.md | 9 | 8 | **ok — fixed this batch (Tier 3)** |
| no-margin-for-error.md | 9 | 8 | **ok — fixed this batch (Tier 3)** |
| succession-planning.md | 9 | 8 | **ok — fixed this batch (Tier 3)** |
| the-untouchable.md | 9 | 8 | **ok — fixed this batch (Tier 3)** |
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
