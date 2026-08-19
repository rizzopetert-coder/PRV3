# No-AI-Slop Remediation Plan — /book Corpus

Status: **Phase 1 and Phase 2 CLOSED (this session).** Pete-confirmed
3-phase structure (Claude.ai), scope for each phase pulled from
`prompts/no-ai-slop-book-audit-findings.md` (~438 findings, 87 files
audited, zero clean) and then re-verified against live file content before
any edit — several scope items turned out to already be resolved by an
earlier, unrelated project (see Phase 2 below) or to be intentional device
reuse rather than defects (see Phase 1, items 1/2/4/5). Phase 3 remains
explicitly gated on the ~August 23 Quarterly Step-Back.

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

## Phase 3 — Structural template variation (EXPLICITLY GATED)

**Gate: the ~August 23 Quarterly Step-Back's visual-identity-philosophy
resolution.** Do not begin design or remediation work on this phase before
that conversation resolves — it's the same underlying "does this read as
professionally crafted or as AI-generated template" question the findings
doc already connects to the visual-identity-philosophy open question
(`prompts/visual-identity-philosophy-open-question.md`), now confirmed at
the copy layer with objective textual evidence rather than only a
subjective visual read. Resolving the visual question first avoids
building copy-layer remediation on an unsettled premise.

**Scope when unblocked:**

- The shared skeleton across roughly 58 of the 87 methodology-type files:
  hook paragraph → horizontal rule → a "diagnostic signs" section using
  exactly three bolded lead-sentence pseudo-bullets → (in about half the
  files) a "First/Second/Third" bolded fix-list using the same device →
  closing aphoristic "kicker" line → (in a subset, batch 2's pieces) an
  identical closing block (`## The Question We Ask` header, italicized
  question, "If you're ready to ___, we should talk." CTA, "— Principal
  Resolution" signature).
- The "X isn't Y. It's Z." binary-contrast construction's overuse —
  present in essentially every one of the 87 files, 2-6 times per piece,
  used as a section heading in a dozen-plus files.

**Governing constraint, already locked:** vary execution, keep the
skeleton. This is not a rebuild of the methodology-piece format — the
underlying structure (hook, diagnostic signs, fix-list, kicker) stays;
what needs to change is that ~58 files stop reading as one template
filled in 58 times, through genuine variation in how each piece executes
that structure.

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
