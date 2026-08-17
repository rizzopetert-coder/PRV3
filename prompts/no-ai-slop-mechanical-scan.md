# No-AI-Slop Mechanical Scan — /book Corpus

Status: **Investigation only. Grep/regex-based counting, not a rewrite, not a
subjective close-read.** Tooling: `tools/diag_book_mechanical_scan.py`
(read-only, reusable). No content edited.

**Scope correction, stated up front:** this scans the **full 87-file
published corpus**, not "the remaining ~79" as originally framed.
`prompts/no-ai-slop-fix-tracking.md` — which would identify exactly which 8
files were already fixed this session — was referenced in the request that
produced this scan but was not actually available (not attached, not present
in the repo) when this ran. Excluding a guessed set of 8 files would have
risked silently mis-scoping the result, so this covers everything. Any file
already fixed will simply show its current, presumably-improved counts here;
nothing below assumes a file is unfixed.

---

## Task 4 result — the case_pattern closing-line claim, confirmed and extended

The three named files (`what-the-organization-decided-he-was-worth.md`,
`the-first-one-out-the-door.md`, `the-resignation-that-ended-a-department.md`)
were read directly against the live repo. **Confirmed**: all three end with
the same "Every organization has that window..." construction. Checked
against the other three `case_pattern` files the original audit flagged as
sharing this pattern (`what-ready-didnt-include.md`, `one-exception-at-a-time.md`,
`built-for-comfort.md`) — **all six** case_pattern files carry this closing,
not "5 of 6" as the original audit estimated:

| file | closing line |
|---|---|
| what-the-organization-decided-he-was-worth.md | "The window to build these structures is before you need them. Every organization has that window. Most organizations are in it right now." |
| the-resignation-that-ended-a-department.md | "The window to do that mapping is not the exit interview. It is every year before the exit interview. Every organization has that window. Most organizations are in it right now." |
| what-ready-didnt-include.md | "Every organization has that window. Most organizations are in it right now." |
| one-exception-at-a-time.md | "Every organization has that window. Most organizations are in it right now." |
| built-for-comfort.md | "Every organization has that window. Most organizations are in it right now." |
| the-first-one-out-the-door.md | "The window to do this is the first departure. Every organization has that window. Most organizations spend it writing a job posting." |

Pairwise LCS match rates: 4 of the 6 are **100% identical** on their shared
middle clause; `the-first-one-out-the-door.md` and
`the-resignation-that-ended-a-department.md` vary the final beat (67% and
64% respectively) but share the identical "Every organization has that
window" core. This is the entire `case_pattern` content type sharing one
closing template, not a coincidental overlap in a subset of it.

---

## Task 3 — mechanical scan, full corpus, one row per file

### Em-dash count > 8 (locked MOB standard) — 45 of 87 files exceed it

Mechanical counts run notably higher than the earlier close-read audit's
manual counts in several cases (e.g. `candor-as-an-organizational-variable.md`
was read as 19, mechanically counts at **28**; `what-the-organization-decided-he-was-worth.md`
was read as 15, mechanically counts at **24**) — the exact count is more
complete than a close-read sample, which is the reason this pass exists.

| file | em-dash count |
|---|---|
| candor-as-an-organizational-variable | 28 |
| how-to-tell-if-the-organization-will-actually-change | 27 |
| built-for-comfort | 26 |
| one-exception-at-a-time | 24 |
| psychological-safety-walked-into-a-meeting | 24 |
| what-the-organization-decided-he-was-worth | 24 |
| earned-effectiveness | 23 |
| hr-is-the-table | 21 |
| what-their-resistance-is-actually-telling-you | 21 |
| when-the-data-points-at-the-person-who-hired-you | 21 |
| symptoms-states-and-why-the-distinction-matters | 20 |
| earned-effectiveness-conversation-framework | 19 |
| the-problem-they-brought-you-is-not-always-the-problem | 19 |
| the-resignation-that-ended-a-department | 19 |
| matrix-organization | 17 |
| toxic-culture | 17 |
| anchor | 16 |
| silosolation | 16 |
| leadership-deafness | 15 |
| the-policy-lag | 15 |
| the-unlocked-door | 15 |
| decision-paralysis | 14 |
| the-first-one-out-the-door | 14 |
| the-lost-map | 14 |
| the-unreported-hazard | 14 |
| what-ready-didnt-include | 14 |
| why-blaming-the-person-almost-never-fixes-the-problem | 14 |
| accountability | 13 |
| groundhog-day | 13 |
| the-overloaded-manager | 13 |
| the-paper-tiger | 13 |
| the-untouchable | 13 |
| everyone-is-defensive-and-no-one-knows-why | 12 |
| succession-planning | 12 |
| velocity-of-truth | 12 |
| why-your-team-stopped-disagreeing-with-you | 12 |
| feedback-nobody-wants-to-say | 11 |
| no-margin-for-error | 11 |
| the-tolerated-violation | 11 |
| dueling-narratives | 10 |
| intellectual-bottleneck | 10 |
| narrative-lock | 10 |
| the-room-that-never-pushes-back | 10 |
| crisis-as-catalyst-for-clarity | 9 |
| the-unformed-leader | 9 |

**Note:** `why-blaming-the-person-almost-never-fixes-the-problem.md` shows 14
em dashes here — per the fix-tracking request, this file was supposedly
brought to the ≤8 standard already this session, but the *live* file (this
scan's only source, since the tracking doc wasn't available) still shows 14.
Either the em-dash pass on this file hasn't been applied to the live file
yet, or it wasn't part of what was fixed — can't distinguish without the
actual tracking doc. Flagged, not resolved here.

### Binary-contrast count ≥ 3 — 59 of 87 files

Loose regex match on "X isn't/wasn't/doesn't/aren't ... It's/It is/They are
Y." spanning one to two sentences — a candidate-flagging heuristic, not a
certified count; false positives are possible on legitimate contrastive
prose, false negatives on contrasts phrased without the canonical
"not...it is" shape.

| file | count | file | count |
|---|---|---|---|
| what-their-resistance-is-actually-telling-you | 13 | culture-drift | 5 |
| when-the-data-points-at-the-person-who-hired-you | 11 | psychological-safety-walked-into-a-meeting | 5 |
| hr-is-the-table | 10 | symptoms-states-and-why-the-distinction-matters | 5 |
| what-not-to-document | 10 | the-burned-credibility | 5 |
| candor-as-an-organizational-variable | 9 | the-fracture | 5 |
| earned-effectiveness-conversation-framework | 9 | the-suppression-filter | 5 |
| feedback-nobody-wants-to-say | 9 | what-the-organization-decided-he-was-worth | 5 |
| anchor | 8 | why-blaming-the-person-almost-never-fixes-the-problem | 5 |
| earned-effectiveness | 8 | exit-pattern | 4 |
| what-ready-didnt-include | 8 | narrative-lock | 4 |
| effectiveness-dies-in-darkness | 7 | risk-of-family-friction | 4 |
| how-to-tell-if-the-organization-will-actually-change | 7 | the-founders-grip | 4 |
| intellectual-bottleneck | 7 | the-lost-map | 4 |
| the-problem-they-brought-you-is-not-always-the-problem | 7 | the-paper-tiger | 4 |
| the-tolerated-violation | 7 | velocity-of-truth | 4 |
| built-for-comfort | 6 | what-nobody-says | 4 |
| cost-of-flying-blind | 6 | *(30 more files at exactly 3 — full list in tool output)* | 3 |
| crisis-as-catalyst-for-clarity | 6 | | |
| dueling-narratives | 6 | | |
| heard-and-ignored | 6 | | |
| pay-exposure | 6 | | |
| the-first-one-out-the-door | 6 | | |
| the-room-that-never-pushes-back | 6 | | |

**Correction to the earlier audit, confirmed by direct spot-check of the
actual regex matches (not a false-positive artifact — verified real):**
`what-not-to-document.md` was characterized in the original DETECT pass as
"the clear outlier and comparatively the cleanest" file in the corpus, and
specifically as carrying the binary-contrast reflex "far less densely than
the other 15 files." The mechanical count found **10 real instances** — tied
for the 4th-highest count in the entire 87-file corpus, not "far less
dense." Verified by direct inspection of all 10 matches: `"isn't dishonest.
It"`, `"isn't really the recipient. It"`, `"doesn't just fail to help. It"`,
`"isn't always the decision itself. It"`, `"isn't the underlying fact. It"`,
`"aren't the ones who feel more certain. They"`, `"doesn't excuse the
responsibility. It"`, `"isn't a mistake anyone made on purpose. It"`,
`"isn't the one with the thickest file. It"`, `"isn't writing less. It"` —
all genuine, all the canonical shape. The file's em-dash cleanliness (0,
genuinely the best in the corpus) and its use of real numbered lists instead
of bolded pseudo-bullets both still hold — but "cleanest file overall" needs
qualifying to "cleanest on em-dash and formatting, not on binary contrast."

### Weasel attribution — 6 of 87 files, only 1 uncorrected instance is a real false positive

| file | hits | detail |
|---|---|---|
| why-blaming-the-person-almost-never-fixes-the-problem | 5 | Matches the original audit's 4 findings plus one more ("Change the structure instead, and the research shows something genuinely different") not previously itemized. **Per this session's fix-tracking request, this file's 4 weasel claims were supposedly replaced with named citations already — the live file still shows all 5 unnamed. Same status as the em-dash note above: can't confirm whether the fix was applied without the actual tracking doc.** |
| candor-as-an-organizational-variable | 2 | "In a study of 65,672 employees..." and "The same research found..." — neither names the study/source in-sentence. |
| intellectual-bottleneck | 1 | "Research on power and social cognition shows..." — no named source. |
| leadership-deafness | 1 | "The research on this is brutal." — no named source, no citation. |
| psychological-safety-walked-into-a-meeting | 1 | "The research on this is fairly consistent..." — no named source. |
| when-the-data-points-at-the-person-who-hired-you | 1 | **False positive, confirmed by direct read:** "Amy Edmondson's foundational research on psychological safety..." — this *does* name a real, real source (Amy Edmondson, the actual psychological-safety researcher); the mechanical pattern only excludes matches with a parenthetical year attached, which this sentence doesn't have. Flagged as clean on manual review, not a real finding. |

### Near-duplicate closing paragraphs across files — 14 pairs, all within the 6-file case_pattern cluster documented in Task 4 above

No new cross-file duplicate closings were found outside the `case_pattern`
cluster already covered by Task 4 — the earlier audit's separately-noted
"Everything before that is just planning." exact match between
`toxic-culture.md` and `silosolation.md` didn't surface here because both
files' actual final paragraphs are longer and structured differently; that
specific sentence sits mid-closing-paragraph in both, not as the literal
last line, so the last-paragraph-only comparison this scan runs missed it.
Confirms the original audit's finding still stands — it's a limitation of
this scan's method (last-paragraph-only), not a retraction.

---

## Full per-file table (all 87 files, all four metrics)

Complete raw output, sorted by em-dash count descending, preserved for
reference: see `tools/diag_book_mechanical_scan.py`'s stdout — reproducible
on demand, not re-pasted here in full to keep this document a usable length.
The subsets above cover every file that crossed a threshold on any metric;
files at zero across the board are only `transition-paralysis` (0
binary-contrast) among files with real em-dash counts, and no file scored
zero on all four metrics simultaneously.

---

## Explicitly not done here

No content edited. No decision made about which files to prioritize for a
fix pass. Tasks 1 and 2 from the original request (applying the 8 revised
files, adding the 5 new citations to `book-citations.ts`) are held —
`prompts/no-ai-slop-fix-tracking.md` needs to actually be provided before
either can proceed responsibly.
