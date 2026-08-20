# No-AI-Slop Remediation Plan — /book Corpus

Status: **ALL THREE PHASES CLOSED (this session). No-AI-slop remediation
project complete.** Pete-confirmed 3-phase structure (Claude.ai), scope
for each phase pulled from `prompts/no-ai-slop-book-audit-findings.md`
(~438 findings, 87 files audited, zero clean) and then re-verified
against live file content before any edit — several scope items turned
out to already be resolved by an earlier, unrelated project (see Phase 2
below) or to be intentional device reuse rather than defects (see Phase
1, items 1/2/4/5). Phase 3 was originally gated on the ~August 23
Quarterly Step-Back's visual-identity-philosophy resolution but was
pulled forward per Pete's explicit instruction and closed ahead of that
gate — see Phase 3 below for the full closure record, and the
Step-Back note at the end of that section.

---

## Phase 1 — Verbatim reuse — CLOSED

**Goal:** every file says what it says in its own words. Where two files
share an obvious "better" version of the same content, keep one canonical
instance and rewrite the other(s) to say the same thing genuinely
differently — not just swap a synonym.

**Real scope, after re-verification against live content (this session):**
only items 3, 6, and 7 were genuine, still-live duplication. Items 1, 2, 4,
and 5 were checked directly against current file content and found
resolved or not applicable — reusing the findings doc's original numbering
so the record stays traceable:

1. `"Everything before that is just planning."` — **RESOLVED, not by this
   plan.** The phrase no longer exists in either `toxic-culture.md` or
   `silosolation.md` — both were touched by the 2026-08-17 em-dash/citation
   project (commits `57eb39d`, `e50b07b`) and the duplicate line was
   removed as a side effect. Confirmed via direct grep, zero matches
   anywhere in the corpus.
2. The "leader who cannot understand why morale is low..." triad —
   **NOT APPLICABLE, intentional device reuse, Pete-confirmed.**
   `everyone-is-defensive-and-no-one-knows-why.md` and
   `the-room-that-never-pushes-back.md` are explicitly paired/mirrored
   memo pieces on the same dynamic from two angles. Both already vary the
   concrete specifics in their parallel triads ("flagged the problem"
   /"resignation letter"/"low-drama" vs. "said anything in the room"
   /"calendar full of meetings"/"easy to work with") — a deliberate
   structural echo between companion pieces, not copy-paste duplication.
   Left untouched.
3. `"the practitioner who learns to sit with it rather than fill it..."`
   — **RESOLVED, FIXED THIS SESSION.** Re-verification found the lead-in
   clauses were already distinct ("sit with that pause rather than move
   past it" vs. "sit with it rather than fill it") but the trailing clause
   — "will consistently surface what the instrument alone cannot reach" —
   was still verbatim-identical in both `candor-as-an-organizational-
   variable.md` and `symptoms-states-and-why-the-distinction-matters.md`.
   `symptoms-states...md` kept canonical (its "fill it" verb is the more
   specific, tied directly to "silence" named in the same sentence).
   `candor-as-an-organizational-variable.md`'s trailing clause rewritten
   to "...often learns more from it than from anything said afterward" —
   nothing else in either piece touched.
4. The `"'Here is what the instrument surfaced...' is a different sentence
   than '...', and it produces a different conversation"` framing device —
   **NOT APPLICABLE, intentional device reuse.** Same finding as item 2:
   `when-the-data-points-at-the-person-who-hired-you.md` and
   `the-problem-they-brought-you-is-not-always-the-problem.md` already use
   different quoted example sentences within the shared connective
   structure ('"[X]" is a different sentence than "[Y]," and it produces a
   [more] [productive/different] conversation'). A reused rhetorical
   device with piece-specific content, not a blind copy. Left untouched.
5. `"[State] does not always look like X. Sometimes it looks like Y."`
   opening template — **NOT APPLICABLE, already varied.** Confirmed intact
   and already piece-specific in `one-exception-at-a-time.md` (framed
   around `the-broken-compass`) and `built-for-comfort.md` (framed around
   `leadership-deafness`). No duplication beyond the shared template shape
   itself. Left untouched.
6. `"Every organization has that window."` closing-line opener —
   **RESOLVED, FIXED THIS SESSION.** Direct verification found the
   findings doc's "5 of 6 near-verbatim" framing overstated it: only 2 of
   the 6 candidate `case_pattern` files literally share the phrase
   (`built-for-comfort.md`, `one-exception-at-a-time.md`); the other 4
   already vary it into a piece-specific "The window to [X] is [Y]"
   construction. `built-for-comfort.md` kept canonical, untouched.
   `one-exception-at-a-time.md`'s opening clause rewritten to "That window
   closes one exception at a time" — tied to the piece's own recurring
   "exception" motif instead of the borrowed generic phrase. Its own
   already-good callback ("Most spend it approving one more reasonable
   exception") is unchanged.
7. `"A different organization has..."` anaphora opening consecutive
   paragraphs — **RESOLVED, FIXED THIS SESSION, per-file assessment
   below.** All 4 confirmed candidate files (`the-first-one-out-the-
   door.md`, `the-resignation-that-ended-a-department.md`,
   `what-ready-didnt-include.md`, `what-the-organization-decided-he-was-
   worth.md`) read individually, not assumed to need fixing just because
   flagged:
   - `the-resignation-that-ended-a-department.md` — phrase appears
     **once**, followed immediately by an already-varied construction
     ("In a different organization, the concern she raised triggers...").
     Not a repetition at all within the piece. **Left untouched.**
   - `the-first-one-out-the-door.md` — **2** consecutive paragraphs, each
     introducing a genuinely distinct idea, no internal repetition within
     either paragraph. Controlled 2-part parallel, reads intentional.
     **Left untouched.**
   - `what-ready-didnt-include.md` — **3** consecutive paragraphs, 5 total
     occurrences (2 of the 3 paragraphs also repeated the phrase
     mid-paragraph). Borderline. Light variation applied: paragraph 1's
     opener kept as the anchor; paragraphs 2 and 3's openers and
     mid-paragraph repeats varied via pronoun/subject substitution ("That
     organization" / "It" / "The same organization"), both "also"
     connectors' cascading intent preserved.
   - `what-the-organization-decided-he-was-worth.md` — **5** fully
     consecutive paragraphs, 6 total occurrences in a 9-line span (one
     paragraph repeated the phrase internally). Clearest case of the
     four — reads as running out of transitions, not a deliberate device.
     Real fix applied: paragraph 1's opener kept as the anchor; the
     remaining 4 paragraphs' openers (and the one internal repeat) varied
     the same way as above.

**Exit criterion, met:** re-ran the reuse check against live content for
every scoped item (not a fresh full DETECT pass, since only 3 of 87 files
needed edits) — zero remaining exact or near-exact cross-file matches for
items 3, 6, and 7. Items 1, 2, 4, 5 documented above with the reasoning
for why no further action applies.

**Incidental finding, logged not fixed:** while assessing item 7, found a
fifth reuse pattern the original DETECT pass didn't name — a one-line pivot
sentence ("What changes/is different is [X]") immediately preceding the
"A different organization has..." section in all 4 `case_pattern` files
checked for item 7:
- `the-first-one-out-the-door.md`: "What changes is what happens after the
  first departure."
- `the-resignation-that-ended-a-department.md`: "What is different is
  what happens in March."
- `what-ready-didnt-include.md`: "What is different is one structural
  decision made earlier, at a calmer moment, before anyone knew a service
  line was coming."
- `what-the-organization-decided-he-was-worth.md`: "What changes is what
  the organization built before any of this happened, not because anyone
  saw this coming, but because someone, at a calmer moment, asked the
  right question and didn't look away from the answer."

Not fixed this session — flagged for a future pass, not part of this
session's scope. Whether it warrants its own remediation item (same
shared-device-vs-duplication judgment call as items 2/4/5/6/7 above) is
undecided.

---

## Phase 2 — Mechanical — CLOSED, pre-resolved before this plan was written

**Goal, as originally scoped:** em-dash cap enforcement on the outlier
files; resolve the unnamed-source claims in
`why-blaming-the-person-almost-never-fixes-the-problem.md`.

**Real finding: both items were already resolved before this session, by
a separate, already-closed project — verified, not assumed, this session.**

The DETECT audit that produced `prompts/no-ai-slop-book-audit-findings.md`
ran 2026-08-16 (commit `6e42d36`) and reported high em-dash counts
(`earned-effectiveness.md` at 19, `candor-as-an-organizational-
variable.md` at 19, `built-for-comfort.md` at 18, etc.) and 4 unnamed-
source claims in `why-blaming-the-person-almost-never-fixes-the-
problem.md`. The **em-dash-cap remediation project ran the very next day**
(2026-08-17, commits `f231059` through `3dfd965`) and swept the entire
87-file corpus down to the locked cap of 8 — `earned-effectiveness.md`
went 23 → 8 (commit `cabf27b`), `candor-as-an-organizational-variable.md`
was trimmed the same day, and the citation-accuracy pass in that same
project added 3 new `book-citations.ts` entries (Mitchell & Wood 1980,
Heinrich 1931, Blume/Ford/Baldwin/Huang 2010) that resolved 3 of the 4
unnamed-source claims directly.

**Verified this session, not assumed:** pulled real per-file em-dash
counts for all 87 files. Current distribution: 9,9,9,9,9,9 (the 6 known,
already-confirmed-clean "Tier 3 signature-closer" exemption files) → flat
plateau at 8 (38 files) → smoothly declining to 0. No cliff, no outlier
group — the premise behind "the 3 outlier files" no longer holds, because
the files it would have named were already fixed one day after the audit
that flagged them, before this plan was ever written. Also re-checked
`why-blaming-the-person-almost-never-fixes-the-problem.md`'s remaining
mechanical weasel-attribution hit ("research on training and behavior
change keeps producing...") — it is immediately followed, same paragraph,
by a real citation: "(Blume, Ford, Baldwin, and Huang, 2010)." No
unattributed claim remains.

**Exit criterion, already met before this plan existed:** no file over
the locked em-dash-per-piece cap (confirmed, this session); zero
unattributed factual claims remaining in
`why-blaming-the-person-almost-never-fixes-the-problem.md` (confirmed,
this session).

---

## Phase 3 — Structural template variation — CLOSED

**Originally gated on the ~August 23 Quarterly Step-Back's visual-identity-
philosophy resolution.** Pulled forward per Pete's explicit instruction,
ahead of that conversation, and closed this session — ahead of the gate
it was originally waiting on. See the Step-Back note at the end of this
section. Direction confirmed: **CONSERVATIVE** — fewer rhetorical
flourishes, quieter confidence, not bolder or more expressive.

**Real scope, re-verified against live content this session (findings
doc's numbers didn't hold up under direct file inspection, same pattern
as several Phase 1 items):**

- **43 of 64 methodology files** share the skeleton (horizontal rule +
  3+ bolded diagnostic-signs pseudo-bullets), not "roughly 58 of 87."
  Full file list on record in this session's scoping report.
- **First/Second/Third fix-list device: 7 files**, not "roughly half."
- **CTA closing block: 8 files** (`accountability`, `business-case`,
  `matrix-organization`, `silosolation`, `succession-planning`,
  `the-broken-compass`, `the-untouchable`, `toxic-culture`) — "a subset"
  held up.
- **"X isn't Y. It's Z." as a genuine two-clause heading pivot: 8
  instances**, not "a dozen-plus" — `groundhog-day`,
  `invisible-influence-architecture`, `the-founders-grip`,
  `paper-shield`, `the-paper-tiger`, `the-pay-fog`, `the-second-close`,
  `the-suppression-filter`. A broader, related family of single-clause
  negation headings (~9-10 more files, e.g. "This Isn't a Communication
  Problem") exists but is a different, less repetitive construction —
  not part of this remediation.

**Governing constraint, still locked:** vary execution, keep the
skeleton. The diagnostic-signs bullets and the CTA block's *structure*
are functional navigation aids, not stylistic tics — left untouched.
Restraint applies to sentence-level prose (headings, hooks, kickers, and
the CTA block's closing invitation line specifically), not to the
scaffolding.

### Heading construction — CLOSED

Of the 8 true two-clause headings, 2 shared the identical construction
with another file despite different wording:
- `the-founders-grip.md` / `the-suppression-filter.md`: both
  "[X] Isn't a Person. It's a [abstract noun]." `the-suppression-
  filter.md` kept as-is (fuller, more specific). `the-founders-grip.md`
  rewritten to "The Structure Behind the Bottleneck" — matches its own
  sibling headings' plain declarative style rather than reaching for a
  different device.
- `paper-shield.md` / `the-paper-tiger.md`: both "[X] Isn't Lying. It's
  [Y]." `paper-shield.md` kept as-is (more vivid — "stopped describing
  this place"). `the-paper-tiger.md` rewritten to "How the Fine Reviews
  Add Up" — tied to the piece's own central image, avoids echoing its
  own later "The Gap You'd Actually See" heading.

The other 6 headings earn their construction (each correcting a real,
piece-specific misconception) and were left untouched.

### Hook/kicker menu — piloted, tightened, ready to scale

**Opener shapes:** (1) plain definitional statement, no anecdote
framing; (2) brief concrete ordinary-moment scene; (3) direct diagnostic
question; (4) name the underlying mechanism in sentence one.

**Closer shapes:** (1) plain statement of practical stakes; (2) quiet
one-sentence "what this requires"; (3) direct callback to the opener's
named pattern; (4) aphoristic kicker — the exception, not the default.

**Rule added after the pilot:** if a file's current hook/kicker already
reads restrained, leave it. The goal is reducing flourish where it
exists, not rewriting every file for variety's own sake.

**Shape 3 (diagnostic question), tightened after the pilot:** the
question must have a genuine, variable answer the reader doesn't already
know going in, and must not stack multiple loaded claims into one
"gotcha" sentence. A plain diagnostic question invites real
self-assessment ("Does your organization have X, and when did Y last
happen?"); a rhetorical question presupposes its own answer and
functions as a dramatic accusation dressed as inquiry ("How many of your
people already know X, have already done Y, and are simply waiting for
Z?"). If a shape-3 draft reads as the second kind, use a plainer
question or a different shape entirely.

**Pilot (5 files, deliberately varied subject matter) — findings and
resolution:**
- `built-to-fail.md` (opener 1, closer 2) and `decision-paralysis.md`
  (opener 1, closer 4) — clean results, no issues.
- `pay-exposure.md` (opener 3) — first draft violated the tightened
  shape-3 rule above (a stacked, loaded rhetorical question). Rewritten
  to a genuine diagnostic question with a real, variable answer.
- `the-untouchable.md` (opener 4) — surfaced a real tonal seam between a
  newly-quiet opener and its still-salesy CTA close ("we should talk").
  Resolved by Task 2's CTA-prose pass (below), not by softening the
  opener.
- `hr-capture.md` (opener 2, closer 3) — the file was already restrained
  before the pilot touched it; applying the "concrete scene" shape
  *added* flourish that wasn't there, the wrong direction. Fully
  reverted to its original hook and kicker (not just the closer — the
  closer's "next employee" callback only made sense against the
  opener's invented scene, so both had to revert together for the file
  to make sense again). This is the finding behind the new rule above.

### CTA-block prose — piloted on the-untouchable.md, ready to extend to the other 7

**Finding:** direct read of all 8 CTA-block files found "we should talk"
used as the literal closing invitation line in **7 of 8** — the same
kind of near-verbatim cross-file reuse Phase 1 targeted, not just a tone
problem specific to one file. (`toxic-culture.md` is the one exception,
using "that's the work we do.")

**Approach, applied to `the-untouchable.md` as the highest-flourish test
case:** keep the block's real job intact — header, framing paragraph,
the italicized diagnostic question (the block's genuine functional
hook), and the "— Principal Resolution" signature all untouched. Only
the final closing-invitation line changes, and it changes to something
piece-specific, not a second repeated template phrase substituted for
the first. `the-untouchable.md`'s new close — "If you're ready to stop
managing around it, that's where we'd start." — ties back to the
block's own already-established "That's where..." language two
sentences earlier in the same section, rather than borrowing new
phrasing. **The other 7 CTA-block files each need their own
piece-specific closing line when touched, not a copy of this one** —
scoped for Phase 3's file-by-file rollout, not decided in advance here.

### Rollout — all 38 remaining files resolved, batches 1-4

Applied the finalized menu and CTA-prose approach across the remaining
38 skeleton files (5 had already been resolved via the pilot), assessed
restraint-first per file in batches of 8-10, dry-run before each write.

**Final result: 14 of 43 skeleton files (33%) needed a real hook/kicker
change.** 2 more got heading-only fixes with hook/kicker left untouched
(`the-founders-grip.md`, `the-paper-tiger.md`). 27 files needed nothing.

**The CTA-block correlation, confirmed and quantified across the full
rollout:** all **8 of 8** CTA-block files needed changes (100%). Of the
other 35 non-CTA files, only **6** needed changes (17%) — CTA-block
pieces were touched at roughly 6x the rate of everything else. Working
theory, not confirmed further: CTA-block pieces were likely authored
with more "hook the reader" intent from the start, which is exactly the
register this phase targeted.

**Final shape distribution, openers (14 touched files):** shape 1
(plain definitional) 4, shape 2 (concrete scene) 2, shape 3 (diagnostic
question) 3, shape 4 (name the mechanism) 5. Shape 4 was the plurality
pick but not from repeated phrasing — the 5 instances (`the-untouchable`,
`accountability`, `business-case`, `the-policy-lag`, `toxic-culture`)
each name a different mechanism in different words.

**Final shape distribution, closers (6 non-CTA files touched — CTA
files get their own piece-specific line, tracked separately below):**
shape 1 (plain stakes) 2, shape 2 (quiet "what this requires") 3, shape
3 (callback) 0, shape 4 (aphoristic) 1.

**Batch-by-batch:** Batch 1 (9 files, alphabetical) — 3 touched
(`accountability.md`, `anchor.md`, `business-case.md`), 6 left alone.
Batch 2 (10 files) — 4 touched, all 4 of that batch's CTA-block files
(`matrix-organization.md`, `silosolation.md`, `succession-planning.md`,
`the-broken-compass.md`), 6 left alone; self-corrected mid-batch when 3
of 4 first drafts converged on the same underlying construction (a
plain claim followed by a condensed illustrative example) — revised
`succession-planning.md` to a genuinely different construction (a real
diagnostic question, no definitional lead-in) before finalizing. Batch 3
(10 files) — 2 touched (`the-policy-lag.md`, `the-undefined-role.md`), 8
left alone (0 of this batch's files were CTA-block). Batch 4 (9 files,
the last batch) — 1 touched (`toxic-culture.md`, the 8th and final
CTA-block file, also the single most heavily flourished hook in the
entire 87-file corpus — condensed from 9 paragraphs to 2), 8 left alone.

### A recurring blind spot, caught twice — worth flagging for any future remediation work

**The lesson:** checking new text for distinct *wording* against other
files is not the same as checking it for distinct *construction*, and
this session missed the second check twice, in two different
categories, before finally catching it.

1. **Batch 2, mid-batch (openers):** 3 of 4 first-draft openers for that
   batch converged on the same underlying move (plain claim + condensed
   illustrative example) despite using different words and, on the
   original shape log, different shape labels. Caught and corrected
   before writing (`succession-planning.md` revised) — see above.
2. **Final DETECT-style re-check, after all 4 batches were already
   applied (CTA closes):** 6 of the 8 CTA closing lines had converged on
   the same idea — "where this begins/starts" — with 4 using the
   literal phrase "starts with" (`accountability.md`,
   `succession-planning.md`, `the-broken-compass.md`, `toxic-culture.md`)
   and 2 more using close cousins (`silosolation.md`: "is where that
   begins"; `the-untouchable.md`: "that's where we'd start"). This one
   was NOT caught mid-batch, because CTA lines were tracked across
   batches for uniqueness against each other's exact wording, which they
   had — the shared construction underneath the different wording was
   the part that went unchecked until a dedicated final pass looked for
   it specifically. All 6 rewritten to genuinely distinct constructions
   before this closure was recorded.

**Why this is worth logging as its own lesson, not just folding into the
batch notes above:** the failure mode is the same shape both times —
distinct-wording checks passed, distinct-construction checks weren't
run until something forced them (a self-review mid-batch the first
time, a dedicated final re-scan the second) — and it happened *after*
the first catch had already been logged as a "watch for this" item.
Knowing about the failure mode didn't prevent a second instance of it in
a different category. For any future content remediation work at this
scale: build the construction-level check into the process from the
start (e.g., a running list of each file's closing/opening *shape*, not
just its final sentence, checked against the list before each write),
rather than relying on catching it via review after the fact a second
time.

### CTA-block prose — CLOSED, all 8 files

Extended from the pilot's `the-untouchable.md` test case to all 7
remaining CTA-block files. Each got its own piece-specific closing line,
confirmed distinct in both wording and construction from the other 7
(see the blind-spot note above for how that got verified properly).
Final 8 closing lines on record in Section 13a.

### Step-Back note

This closes Phase 3 — and the full 3-phase remediation project — ahead
of the ~August 23 Quarterly Step-Back that Phase 3 was originally gated
on. It is no longer blocking on that conversation. The Step-Back's own
visual-identity-philosophy discussion may still want to reference this
work's outcome (the real skeleton/heading/CTA-line numbers, the
conservative-direction execution, the construction-level blind spot) as
input, since it's the same underlying "professionally crafted vs.
AI-generated" question at the copy layer that the original findings doc
connected to the visual question — just no longer a dependency either
direction.

---

## Out-of-scope finding, not part of this remediation

**"We should talk" also appears, unscoped, in 4 files outside the
43-file skeleton set:** `exit-pattern.md`, `leadership-deafness.md`,
`no-margin-for-error.md`, `the-basement-standard.md` — found during
Phase 3's final DETECT-style re-check. All 4 were correctly excluded
from Phase 3 (confirmed against the original scoping pass: none have the
bolded diagnostic-signs skeleton this remediation was scoped around),
so this isn't a rollout gap. It means the "we should talk" duplication
problem extends beyond what any phase of this project covered. **Not
touched. Not actioned.** Flagged here for a future decision on whether
it's worth its own pass — a much smaller scope than Phase 3 (4 files,
one line each), if and when Pete wants to open it.

---

## Cross-references

- Full findings, all 6 batches, complete per-file detail:
  `prompts/no-ai-slop-book-audit-findings.md` (commit 6e42d36).
- Visual-identity-philosophy open question (Phase 3's gate):
  `prompts/visual-identity-philosophy-open-question.md`.
- Em-dash-cap remediation project, 2026-08-17: the project that
  pre-resolved Phase 2 (see above) — commits `e50b07b`, `57eb39d`,
  `f231059` through `3dfd965`, `29376a8`, `cabf27b`. Session log entry:
  MOB Section 16, 2026-08-17 close.
