# No-AI-Slop Remediation Plan — /book Corpus

Status: **Plan only, no content rewritten yet.** Pete-confirmed 3-phase structure
(Claude.ai, this session), scope for each phase pulled directly from
`prompts/no-ai-slop-book-audit-findings.md` (~438 findings, 87 files audited,
zero clean). Ready to open Phase 1 on Pete's go-ahead.

---

## Phase 1 — Verbatim reuse (start now)

**Goal:** every file says what it says in its own words. Where two files share
an obvious "better" version of the same content, keep one canonical instance
and rewrite the other(s) to say the same thing genuinely differently — not
just swap a synonym.

**Scope — every specific reuse instance named in the findings doc:**

1. `"Everything before that is just planning."` — `toxic-culture.md` and
   `silosolation.md`, word-for-word identical.
2. The "leader who cannot understand why morale is low..." triad —
   `everyone-is-defensive-and-no-one-knows-why.md` and
   `the-room-that-never-pushes-back.md`, near-verbatim.
3. `"the practitioner who learns to sit with it rather than fill it..."` —
   `candor-as-an-organizational-variable.md` and
   `symptoms-states-and-why-the-distinction-matters.md`.
4. The `"'Here is what the instrument surfaced...' is a different sentence
   than '...', and it produces a different conversation"` framing device —
   `when-the-data-points-at-the-person-who-hired-you.md` and
   `the-problem-they-brought-you-is-not-always-the-problem.md`.
5. `"[State] does not always look like X. Sometimes it looks like Y."`
   opening template — confirmed in `one-exception-at-a-time.md` (framed
   around `the-broken-compass`) and `built-for-comfort.md` (framed around
   `leadership-deafness`).
6. `"Every organization has that window. Most organizations [are in it
   right now / spend it writing a job posting]."` closing line — near-
   verbatim across 5 of 6 `case_pattern` files:
   `what-the-organization-decided-he-was-worth.md`,
   `the-first-one-out-the-door.md`,
   `the-resignation-that-ended-a-department.md`,
   `what-ready-didnt-include.md`, `one-exception-at-a-time.md`,
   `built-for-comfort.md`. (The findings doc names all 6 as the candidate
   set but flags only 5 as actually matching near-verbatim — confirm which
   file is the outlier, if any, before rewriting; it may already be the
   canonical version worth keeping.)
7. `"A different organization has..."` anaphora opening 3-5 consecutive
   paragraphs — confirmed in "at least 4" `case_pattern` files, not
   individually named in the findings doc. **Gap, not yet enumerated:**
   identify the specific files before or during Phase 1 execution (a
   scoped re-grep of the `case_pattern` content type for this phrase is
   the fastest path) rather than guessing which 4+.

**Exit criterion:** re-run DETECT scoped specifically to reuse/duplication
patterns across all 87 files; confirm zero remaining exact or near-exact
cross-file matches, including the items 6/7 gaps closed above.

---

## Phase 2 — Mechanical (start now, parallel to Phase 1)

**Goal:** clear the two concrete, countable mechanical findings.

**Scope:**

- **Em-dash cap enforcement on the outlier files.** Raw counts from the
  findings doc, worst first: `candor-as-an-organizational-variable.md`
  (19), `earned-effectiveness.md` (19), `built-for-comfort.md` (18),
  `one-exception-at-a-time.md` (16), `why-blaming-the-person-almost-never-
  fixes-the-problem.md` (11, also carries the weasel-attribution finding
  below). **Flagging rather than assuming:** Pete's instruction named "the
  3 outlier files" without specifying which three by name or count — the
  most literal reading by raw em-dash count is the top 3
  (`candor-as-an-organizational-variable.md`, `earned-effectiveness.md`,
  `built-for-comfort.md`), but `one-exception-at-a-time.md` and
  `why-blaming-the-person-almost-never-fixes-the-problem.md` are close
  behind and were separately called out in the findings doc's "notably
  worse than the rest" bullet alongside `built-for-comfort.md`. Confirm
  the intended 3 (or whether all 5 above-11 files should be brought under
  cap while in this phase anyway, since the mechanical fix is identical
  regardless of which subset is prioritized first) before execution
  begins.
- **Resolve the 4 unnamed-source claims in
  `why-blaming-the-person-almost-never-fixes-the-problem.md`** ("research
  on how supervisors actually diagnose...", "a study of professional
  evaluators...", "one widely cited early study...", "research on
  training and behavior change...") — each either named/cited properly
  (matching the piece's own already-correctly-cited Lee Ross 1977
  reference) or cut entirely if no real source can be verified.

**Exit criterion:** no file over the locked em-dash-per-piece cap; zero
unattributed factual claims remaining in
`why-blaming-the-person-almost-never-fixes-the-problem.md`.

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
- Distinct, closed project: the em-dash-cap remediation that shipped
  2026-08-17 (87/87 published files, 0 genuinely over cap) addressed a
  different, narrower mechanical question (per-file em-dash count against
  the locked cap) and is not the same effort as this plan's Phase 2,
  which targets the specific outlier files this newer, fuller DETECT pass
  surfaced.
