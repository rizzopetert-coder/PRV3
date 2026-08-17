# No-AI-Slop Audit — /book and /book/toc, Full Published Corpus

Status: **Investigation only. DETECT mode throughout — no files edited, no content
rewritten.** Covers every piece of shipped copy a real visitor sees on `/book`
and `/book/toc` — not a sample, the full set. Nothing here is a build task;
it's a record of what a systematic pass found, for Pete to decide what (if
anything) gets prioritized.

**Also governs standing:** tonight's earlier glossary-intersection candidate
filter labels (`prompts/book-toc-glossary-intersection-findings.md`) remain
**provisional**, per instruction, pending this pass. See the note at the very
end — this audit doesn't retract them, but it surfaces a much larger,
unrelated problem that should be resolved first.

---

## Scope and method

**`/book` — all 87 published articles**, confirmed via direct parse of
`web/lib/book-manifest.ts` (not assumed from file listing — 89 total pieces,
1 parked, 87 `status: "published"`, cross-checked against
`web/content/book/{contentType}/{slug}.md` via `web/lib/book-content.ts`'s
real content-loading path). Split into 6 batches of ~14-15 files, audited by
6 parallel subagents, each applying the no-ai-slop skill's full DETECT
methodology (banned words, empty phrases, weasel attribution, importance
puffery, binary contrasts, colon reveals, dramatic fragmentation, robotic
rhythm, fake-profound kickers, summary-recap endings, formatting slop,
em-dash clustering) to every file in full, independently.

**`/book/toc` — all 6 named sources**, audited directly (not delegated):
`taxonomy.ts` states[]/signatures[], `book-state-index.ts` descriptiveProse,
`book-taxonomy-labels.ts` PUBLIC_DIMENSION_LABELS, `page.tsx`
SIGNATURE_DEFINITIONS (Gestalt Pass Terminology Guide), `ConstellationField.tsx`
GESTALT_INFO — reusing tonight's earlier extraction tooling
(`tools/diag_book_toc_glossary_intersection.py`) to pull the full 143-entry
corpus, then grep + direct read against the same pattern list.

---

## /book — cross-cutting findings across all 87 files

**~438 total findings across 87 files. Zero files came back fully clean.**
Per-batch totals: 102, 68, 62, 63, 78, 65 (batches 1-6 respectively). Full
per-file detail preserved below.

**The single most significant finding is structural, not lexical:** the
majority of the ~58 state-diagnosis "methodology" pieces (the largest content
type) share what reads as one underlying template, not independent authorship:

1. A hook paragraph, then a horizontal rule
2. A "diagnostic signs" section using **exactly three bolded lead-sentence
   pseudo-bullets** dressed as prose (confirmed near-identically in at least
   10 files across batches 4, 5, and 6 — e.g. "**He was an excellent
   individual contributor before the promotion.**", "**A protected event
   happened first.**", "**Decisions get made in rooms that don't match the
   meeting invite.**")
3. In roughly half the files, a "First/Second/Third" bolded fix-list using
   the identical device
4. A closing **aphoristic "kicker" line** that reframes the piece's thesis as
   a mic-drop sentence — present in nearly every methodology file
5. In a subset (batch 2's pieces specifically), an identical closing block:
   `## The Question We Ask` header → italicized diagnostic question → "If
   you're ready to ___, we should talk." → "— Principal Resolution" signature

**Second most dominant: the "X isn't Y. It's Z." binary-contrast
construction**, present in essentially every one of the 87 files, frequently
2-6 times per piece, and — notably — used as a **section heading** in at
least a dozen files (`"The Chart Isn't Wrong. It's Obsolete."`,
`"Privacy Wasn't a Fix. It Was Just Cover."`, `"The Transaction Closed. The
Organization Didn't."`, `"Closed Is Not the Same as Fixed"`,
`"## This Is Not a Recruiting Problem"`, `"The Initiatives Aren't Failing.
They're Succeeding at the Wrong Target."`). This isn't an occasional device —
across the full corpus it functions as the house rhetorical signature.

**Third: em-dash clustering, near-universal.** Every batch confirmed the
overwhelming majority of files exceed the 3-per-piece threshold, several by a
wide margin: `candor-as-an-organizational-variable.md` and
`earned-effectiveness.md` each carried **19**; `the-unreported-hazard.md`,
`the-uninitiated.md`, `the-pay-fog.md`, `the-second-close.md` each carried 7;
`why-blaming-the-person-almost-never-fixes-the-problem.md` carried 11. A
handful of files were near-clean on this axis specifically:
`organizational-assessment.md` (1), `what-not-to-document.md` (0),
`effectiveness-dies-in-darkness.md` (2), `the-suppression-filter.md` (0).

**Fourth: literal, near-verbatim sentence reuse across unrelated pieces** —
not just shared structure, the same sentences:
- `"Everything before that is just planning."` — `toxic-culture.md` and
  `silosolation.md`, word for word.
- The "leader who cannot understand why morale is low..." triad —
  `everyone-is-defensive-and-no-one-knows-why.md` and
  `the-room-that-never-pushes-back.md`, near-verbatim.
- `"the practitioner who learns to sit with it rather than fill it..."` —
  `candor-as-an-organizational-variable.md` and
  `symptoms-states-and-why-the-distinction-matters.md`.
- The `"'Here is what the instrument surfaced...' is a different sentence
  than '...', and it produces a different conversation"` framing device —
  `when-the-data-points-at-the-person-who-hired-you.md` and
  `the-problem-they-brought-you-is-not-always-the-problem.md`.
- `"[State] does not always look like X. Sometimes it looks like Y."` opening
  template — at least 2 confirmed instances across `case_pattern` files
  (`the-broken-compass` framing in `one-exception-at-a-time.md`,
  `leadership-deafness` framing in `built-for-comfort.md`).
- `"Every organization has that window. Most organizations [are in it right
  now / spend it writing a job posting]."` closing line — near-verbatim
  across **5 of 6** `case_pattern` files
  (`what-the-organization-decided-he-was-worth.md`,
  `the-first-one-out-the-door.md`,
  `the-resignation-that-ended-a-department.md`,
  `what-ready-didnt-include.md`, `one-exception-at-a-time.md`,
  `built-for-comfort.md`).
- `"A different organization has..."` anaphora opening 3-5 consecutive
  paragraphs — confirmed in at least 4 `case_pattern` files.

**Fifth, narrower: weasel attribution**, concentrated almost entirely in one
file — `why-blaming-the-person-almost-never-fixes-the-problem.md` carries
four separate unnamed-source research claims ("research on how supervisors
actually diagnose...", "a study of professional evaluators...", "one widely
cited early study...", "research on training and behavior change...") —
notable because the same piece *does* correctly name one real source (Lee
Ross, 1977), making the inconsistency visible rather than a uniform habit.

**Banned words — minimal, but present:** "leverage" appeared **9 times**
across 3 files (`succession-planning.md`, `accountability.md`,
`the-untouchable.md`, including a section header literally titled "The
Leverage Problem"); "empower" once (`matrix-organization.md`); "robust"
twice (`feedback-nobody-wants-to-say.md`,
`psychological-safety-walked-into-a-meeting.md`); one "this changes
everything"-class hyperbole (`"This is the demonstration that changes
everything."`, `feedback-nobody-wants-to-say.md`). Otherwise clean —
delve/foster/utilize/facilitate/streamline/cutting-edge/paradigm
shift/tapestry/realm/meticulous/paramount/transformative etc. did not appear
anywhere in 87 files.

**Notably worse than the rest:** `methodology/anchor.md` (the only file with
a literal "Here's the thing:" throat-clearing opener plus a faux-insight
header plus two rhetorical self-answered-question setups, stacked on the
usual binary-contrast/em-dash load); `built-for-comfort.md` and
`one-exception-at-a-time.md` (heaviest em-dash density, 18 and 16, plus
stacked "A different organization has..." anaphora);
`why-blaming-the-person-almost-never-fixes-the-problem.md` (both em-dash
density and the only real weasel-attribution problem).

**Notably cleaner than the rest:** `what-not-to-document.md` (zero em dashes,
genuine numbered lists instead of bolded pseudo-bullets, still carries the
corpus's binary-contrast/kicker reflex but far more lightly);
`organizational-assessment.md`, `organizational-assessment-methodology.md`,
`anatomy-of-resentment.md`, `effectiveness-dies-in-darkness.md`,
`the-suppression-filter.md` — all came back with only 1-2 minor findings each.

---

## /book/toc — findings across all 6 sources (143 entries)

Much cleaner corpus, consistent with it having already been through explicit
brand-voice editing this session. Full detail already on record from the
same-evening pass (this section is a compressed restatement for one-document
completeness):

- **Zero** hits anywhere for banned words, empty phrases, weasel attribution,
  importance puffery, throat-clearing openers, summary-recap endings,
  rhetorical setups, negative listing, or em-dash clustering.
- **3 binary-contrast ("isn't X — it's Y") instances**, the same shape found
  dominating `/book`: `decision_paralysis`, `the_inner_circle`,
  `leadership_bottleneck` (signature) — the same house tic, present here in
  much smaller quantity.
- **3 colon-reveal instances**, two stacked in one entry
  (`motivational_architecture_failure`) plus one in `culture_erosion`'s
  coexistence copy.
- 2 borderline "not X but Y" constructions that read as legitimate clinical
  distinctions, not filler — named, not treated as clean flags.
- `PUBLIC_DIMENSION_LABELS`, `SIGNATURE_DEFINITIONS`, and `GESTALT_INFO` —
  fully clean, zero findings.

---

## What this means for tonight's glossary-intersection candidate labels

**Still provisional — this pass neither confirms nor retracts them.** The
six candidate filter labels drawn earlier tonight
(`prompts/book-toc-glossary-intersection-findings.md`) were built from
`/book/toc`'s taxonomy copy specifically, and that surface came back mostly
clean in this pass — nothing here disqualifies the underlying recurring
phrases they were drawn from.

But this pass surfaces a much bigger, separate problem sitting one level up:
the entire 87-piece published article corpus shares a near-uniform
house-style template and rhetorical tic set, at a scale that reads as
systemic rather than incidental. Before treating any new user-facing copy
work — including new filter-category labels — as ready to build, the more
consequential open question is whether Pete wants to address the article-level
pattern first. Layering new copy decisions on top of a foundation that
hasn't had that reckoning yet is the premature-sequencing risk worth naming
explicitly, not something to route around quietly.

---

## Full per-file findings, by batch (raw subagent output, preserved verbatim)

Reproduced in full below for anyone who wants to work a specific file
directly, rather than only the cross-cutting synthesis above.

### Batch 1 (15 files: candor-as-an-organizational-variable, symptoms-states-and-why-the-distinction-matters, when-the-data-points-at-the-person-who-hired-you, the-problem-they-brought-you-is-not-always-the-problem, how-to-tell-if-the-organization-will-actually-change, what-their-resistance-is-actually-telling-you, earned-effectiveness-conversation-framework, earned-effectiveness, anchor, anchor-problem, exit-calculation, feedback-nobody-wants-to-say, psychological-safety-walked-into-a-meeting, hr-is-the-table, organizational-assessment)

102 total findings. Dominant patterns: binary contrast in all 15 files (hr-is-the-table.md used the identical "This/These is/are not X. It/They is/are Y." shape five times in one short piece); em-dash clusters in 14 of 15 (candor-as-an-organizational-variable.md and earned-effectiveness.md at 19 each); dramatic fragmentation/robotic rhythm paired with fake-profound kickers in most pieces. Banned word "robust" x2 (feedback-nobody-wants-to-say.md, psychological-safety-walked-into-a-meeting.md). Worst file: methodology/anchor.md (only file with a literal "Here's the thing:" opener, faux-insight header, two rhetorical self-answered-question setups). Cleanest: memo/organizational-assessment.md (2 findings, 1 em dash).

### Batch 2 (14 files: organizational-assessment-methodology, succession-planning, business-case, accountability, matrix-organization, toxic-culture, the-untouchable, leadership-deafness, no-margin-for-error, exit-pattern, the-basement-standard, silosolation, the-broken-compass, decision-paralysis)

~68 total findings. Every file exceeds the em-dash threshold (4-12, toxic-culture.md and matrix-organization.md densest). 11 of 14 pieces share a near-identical closing template ("## The Question We Ask" header, italic question, "if you're ready to ___, we should talk" CTA, "— Principal Resolution" signature) plus a bolded-fragment-list device in 6+ pieces. Banned word "leverage" x9 across succession-planning.md, accountability.md, the-untouchable.md (including a section header "The Leverage Problem"); "empower" x1 (matrix-organization.md). toxic-culture.md and silosolation.md share one identical closing sentence verbatim ("Everything before that is just planning."). decision-paralysis.md is the one outlier that breaks from the closing template. Cleanest: organizational-assessment-methodology.md (1 finding, em-dash only).

### Batch 3 (14 files: the-undefined-role, the-policy-lag, the-lost-map, everyone-is-defensive-and-no-one-knows-why, the-room-that-never-pushes-back, what-the-organization-decided-he-was-worth, the-first-one-out-the-door, why-your-team-stopped-disagreeing-with-you, the-resignation-that-ended-a-department, what-ready-didnt-include, one-exception-at-a-time, built-for-comfort, anatomy-of-resentment, effectiveness-dies-in-darkness)

62 total findings. Em-dash overuse dominant: 137 em dashes across 14 files, 12 of 14 exceeding threshold; built-for-comfort.md (18), one-exception-at-a-time.md (16), what-the-organization-decided-he-was-worth.md (15) heaviest, all case_pattern pieces. Two shared structural templates confirmed across the 6 case_pattern files: an opening "[State] does not always look like X. Sometimes it looks like Y." naming device, and a closing "Every organization has that window. Most organizations [are in it right now/spend it writing a job posting]." aphorism, near-verbatim across 5 of 6 files. Interpretive metadiscourse ("that [last part/distinction] matters...") near-verbatim across 3 files. Cleanest: anatomy-of-resentment.md (4 em dashes only), effectiveness-dies-in-darkness.md (2 em dashes, below threshold).

### Batch 4 (14 files: cost-of-flying-blind, risk-of-family-friction, velocity-of-truth, politeness-tax, intellectual-bottleneck, crisis-as-catalyst-for-clarity, why-blaming-the-person-almost-never-fixes-the-problem, the-overloaded-manager, the-unformed-leader, the-dormant-talent, decision-blindness, what-nobody-says, heard-and-ignored, the-suppression-filter)

63 total findings, zero fully clean files. Zero banned words or empty filler phrases anywhere in the batch (confirmed by direct grep, not just read-through). Binary contrast in nearly every file. Em-dash density: why-blaming-the-person-almost-never-fixes-the-problem.md (11, highest in batch) and intellectual-bottleneck.md (9) heaviest; the-suppression-filter.md at 0 (cleanest on this axis). Seven of the eight methodology pieces (the-overloaded-manager through the-suppression-filter) share an identical structural device: a section with exactly three bolded lead sentences each followed by 1-2 sentences of explanation — a formula repeated near-verbatim across the entire methodology series. An "This is what separates/distinguishes X" interpretive-metadiscourse line recurs near-verbatim across 4 files. Weasel attribution concentrated in why-blaming-the-person-almost-never-fixes-the-problem.md alone (4 unnamed-source claims, contrasted against its own one correctly-named source, Lee Ross 1977).

### Batch 5 (14 files: culture-drift, the-burned-credibility, pay-exposure, built-to-fail, the-paper-tiger, the-unsolved-problem, the-tolerated-violation, the-unreported-hazard, the-unlocked-door, dueling-narratives, narrative-lock, the-wrong-reward, groundhog-day, the-founders-grip)

78 total findings, zero clean files. Binary contrast is overwhelmingly dominant here — ~40 instances across 14 files, recurring as a section-heading device in at least 7 of the 14 pieces. Em-dash clusters in all 14 (3 to 11, the-unreported-hazard.md heaviest). Fake-profound aphoristic kickers in 6 files, several echoing/restating an earlier phrase from the same piece rather than adding a new point. No banned words, empty phrases, weasel attribution, or importance puffery anywhere in the batch. Densest: the-unreported-hazard.md (11 em dashes) and pay-exposure.md (6 stacked binary contrasts). Comparatively cleanest: the-unlocked-door.md, the-wrong-reward.md.

### Batch 6 (16 files: invisible-influence-architecture, the-fracture, hr-capture, transition-paralysis, the-exposed, the-uninitiated, paper-shield, the-pay-fog, the-arbitrary-standard, the-unexamined-algorithm, the-second-close, invisible-burnout, the-culture-that-wasnt, the-inside-track, the-diversity-ceiling, what-not-to-document)

65 total findings. Zero hits on the banned-word list except one borderline, defensible use of "leverage" as a bargaining-power noun (the-second-close.md) — flagged for awareness only, not a real violation. Zero weasel attribution, importance puffery, throat-clearing openers, faux-insight setups, or rhetorical setups anywhere in the batch — this sub-corpus avoids those markers entirely. Three structural habits dominate instead: em-dash clusters (3-7 per piece, 15 of 16 files exceed threshold); binary-contrast constructions, frequently doubled into section headings ("The Chart Isn't Wrong. It's Obsolete.", "Privacy Wasn't a Fix. It Was Just Cover.", "The Transaction Closed. The Organization Didn't."); and a near-identical formatting template across all 15 methodology files in the batch — hook paragraph, rule, a "diagnostic signs" section with exactly three bolded pseudo-bullet lead sentences, an 8-of-15 "First/Second/Third" bolded fix-list, and a closing aphoristic kicker. what-not-to-document.md is the clear outlier: zero em dashes, genuine numbered lists instead of bolded pseudo-bullets, structurally the cleanest file in the entire /book corpus.
