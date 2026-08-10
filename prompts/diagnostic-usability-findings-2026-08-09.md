# Diagnostic Usability Findings -- 2026-08-09 (live test, Pete's wife, first real user)

## A. Functional/UX bugs (verifiable, Tier 1 candidates)
1. No "Other" option in the "significant events" checklist section.
2. Q06 is designed as select-all-that-apply but does not function as a multi-select
   in the live UI.
3. No back / forward / reset buttons anywhere in the diagnostic flow.
4. Q42 needs a "no" answer option -- currently missing.
5. Suspected repeat questions somewhere in the sequence -- not yet identified which ones.
6. General question: are there enough answer options on every question regardless of
   scoring intent, or do some questions force a choice that doesn't fit the respondent's
   real situation?

## B. Question content/design ambiguity (needs Pete's judgment on intent, not pure
   engineering -- verify actual question text against engine/data/questions.py before
   any fix)
1. Q05 -- needs reword (no detail yet on what's wrong).
2. Q33 -- "How many people have held this exact role before you, and what's the
   organization's read on why they left?" -- ambiguous whether this is about the
   respondent specifically or someone else, and whether it's asking for a specific
   number or general sense.
3. Q34 -- confusing in the same way as Q33; reads like an unlabeled/unsequenced
   follow-up to Q33 but isn't marked as one.
4. Q35 -- "Who?" -- ambiguous subject reference.
5. Q37 -- unclear what it's asking about; reads like an unlabeled follow-up.
6. Q40 -- flagged, no detail captured yet.
7. Q43 -- same ambiguity issue as Q33/Q34/Q35/Q37 (unclear subject reference and/or
   unclear whether it's a labeled follow-up). Detail not yet captured -- flag for the
   same question-text review as the others in this section.
8. Broader design concern: some questions seem to assume the respondent is already
   coming in with a specific problem in mind. Pete's intent: this should diagnose
   patterns/symptoms generally, not test a pre-conceived problem. May require a pass
   across multiple questions, not a single fix.

### B-addendum: Numbering resolved, root cause identified (live-verified 2026-08-09)

Pete's Section B numbers (Q05, Q33, Q34, Q35, Q37, Q40, Q43) are on-screen display
position, not engine question_id -- confirmed via direct browser walkthrough (not
reconstructed from static file reads). The display position stays stable regardless
of inserted follow-up/checkpoint screens (those use their own "FOLLOW-UP NX"
labeling and don't consume a position number), but position-to-engine-question_id
offset jumps at the point where the excluded Aptitude-addenda range (literal engine
Q35-39) is skipped from the Phase 1 sequence -- offset is +2 before that gap, +7
after it.

Confirmed live text for every flagged position:
- Q33: "How many people have held this exact role before you, and what's the
  organization's read on why they left?"
- Q34: "When you've raised the gap between the scope and the resources you actually
  have, what's happened?"
- Q35: "When a decision needs that one person's approval and they're unavailable,
  what happens?"
- Q37: "Who actually knows about this, and what's happened as a result?"
- Q40: "Has anything changed for this manager -- additional support, delegated
  authority, or reduced scope -- since it became clear they were stretched?"
- Q43: "When someone in this group makes a costly mistake, what happens to them?"

Root cause identified across all six: each is written as a mid-conversation follow-up
carrying a pronoun with no on-screen antecedent ("this," "that one person," "this
manager," "this group") but rendered with zero visual distinction from a fresh,
standalone question -- no "continuing from your last answer" framing, no indent, no
label. This is very likely one shared root cause, not six unrelated wording problems.
Q05 not yet re-examined live -- still needs its own look.

Separately (relevant to Section C): the diagnostic can terminate before all 44
questions once sufficient dimensional signal is reached (confirmed live -- one full
walkthrough ended at a condition report around position 15; a second walkthrough with
a different answer path reached Q44/44 cleanly). This is real and path-dependent, not
guaranteed either way -- relevant to Pete's earlier note about the diagnostic feeling
like it assumes a pre-conceived problem.

### B-addendum-2: Root cause splits into two distinct problems (investigated 2026-08-09)

Investigated whether the six flagged questions (positions 33/34/35/37/40/43 = engine
Q40/Q41/Q42/Q44/Q47/Q50) share one root cause. They don't -- it splits 5-and-1.

**Structural facts confirmed:**
- No follow-up relationship is modeled in the data for any of the six --
  severity_follow_on_id is deliberately None on all of them (per the Q40-51 batch's
  own authoring comment). Q40/Q41 share state_targets=['built_to_fail'] as a byproduct
  of authoring order, not a designed link.
- The "Follow-up NX" splice mechanism is closed and purpose-built -- exactly three
  hardcoded call sites (severity follow-ons, one Q28-off-Q06 special case, checkpoint
  distinguishers), no generic "declare a follow-up" pattern exists.
- Core vs. spliced is a binary, positional property in code (coreQuestionPosition()
  static membership check; DiagnosticFlow.tsx's "Follow-up" label only renders when
  label.kind === "spliced"). A core question cannot receive follow-up framing under
  current code -- there's no third state to add a flag to.

**The five (Q40/Q42/Q44/Q47/Q50): not a labeling problem.**
Checked each against its true immediate predecessor by state_targets, not just
position -- none are topical continuations. Each is the first or only Phase-1 question
for a new state (the_arbitrary_standard, the_overloaded_manager,
disparate_impact_architecture, motivational_architecture_failure, etc.), most of which
got only one question instead of the usual two-question pair. The dangling pronoun
("this manager," "this group," "who actually knows about this") presumes an
establishing/premise-setting question that was never authored for that state under
the Q40-51 batch's "minimal new authoring" scope constraint. Relabeling these as
"Follow-up" would be factually wrong -- there's no real parent. This is a
content-authoring gap: either rewrite each to be self-contained, or author the missing
premise question for that state.

**The one (Q41): genuine unlabeled continuation, but not a simple label swap either.**
Q41 ("the gap between scope and resources") is a real, content-verified continuation
of Q40. But the existing "Follow-up" mechanism is built exclusively for conditionally-
spliced questions (only some respondents see them, gated on a trigger) -- Q41 is
unconditional, static, core content, always asked. Displaying it as a follow-up via
the current system means either making it conditional (a real behavior change) or
building a new third label category ("linear but continuing," distinct from both
"core" and "spliced") that doesn't exist today. Either path is new mechanism work.

**Status:** no fix proposed. Needs a design decision from Pete before any engineering
-- and the decision differs by which of the six is in question. Not scheduled.

**Closure (2026-08-09):** all six rewritten -- Pete-approved stem changes to Q40,
Q41 (question_text and option D text), Q42, Q44, Q47, and Q50, removing every
dangling pronoun. dimensional_contributions unchanged on every option across all
six questions -- confirmed via diff before commit, not assumed. Full 172(+3)-profile
calibration suite held at 170/175 (58/58 HC), zero movement. Commit 52e99ac. Push
held pending Pete's live browser re-walk to confirm all six render correctly before
this goes to production.

### B-addendum-3: Gemini architecture review -- Structures 1/2 cleared, Structure 3
   parked with A5 (2026-08-09)

Gemini reviewed three conditional-follow-up structures for the diagnostic's question
sequence. Findings:

**Structures 1 (position 34/Q41, 3-deep chain) and 2 (position 36/Q43, 2-deep chain):
CLEARED.** Neither touches PHASE_1_QUESTION_SEQUENCE's core count -- both add new
spliced follow-up questions via the existing severity_follow_on_id mechanism, already
proven safe by every existing SEVER-## follow-on. Implementation in progress
(see commit reference once written).

**Structure 3 (positions 37/38/39, converting Q44/Q45/Q46 from core to spliced):
PARKED alongside A5.** Gemini's proposal would remove 2 questions from the core
sequence (44->42), triggering the identical engine/accumulation.py:539
scale = N / 44.0 landmine already confirmed this session via A5's Q29-removal attempt
(170/175->163/175 regression, comparable scope to the original MC_CENTROID_39
recalibration arc). Gemini's review characterized the fix as a routine "Phase 3: Monte
Carlo regen + pytest" step -- this contradicts our own direct, empirically-confirmed
experience this session that a core-count change of this kind requires a genuine
multi-session recalibration effort, not a routine regen. Worth noting as a
Gemini-confidence pattern distinct from citation fabrication (memory-tracked
separately): here it's understating known project-specific difficulty rather than
inventing a figure, but the same "confident precision that doesn't match ground truth"
shape.

Separately, Gemini's own review flagged that Q46 (the_arbitrary_standard) doesn't
share topical continuity with Q44/Q45 (the_tolerated_violation) and recommended NOT
chaining it under Q45 regardless of the calibration question -- this content issue is
unresolved and will need addressing whenever Structure 3 is picked back up, separate
from the N-count problem.

Decision: Structure 3 parked with A5 (Q16/Q29 duplicate removal) -- both hit the same
recalibration landmine and will be handled together in one dedicated future effort
rather than as two separate multi-session arcs. Not scheduled. Structures 1 and 2
proceed independently since they carry zero calibration risk.

**Implementation verification (2026-08-09), before any commit:** Part 0 verification
found Gemini's proposed ancestry-resolution snippet assumed answers_log entries carry
spliced_question_id/parent_question_id fields -- confirmed via direct read of
web/lib/session-store.ts that these fields don't exist. AnswerLogEntry is exactly
{question_id, option_id}. The real fix lives entirely in spliceLabel() (adding a third
parameter, the session's existing question_labels map, so a non-core parent's own
already-resolved label is used instead of falling back to its raw ID string) --
verified via 2 new automated tests (session-store.test.ts), both passing, plus the
full existing suite unchanged (same 5 pre-existing baseline failures, unrelated
hardcoded stale-length assertions). Structures 1 and 2 temporarily applied and tested
per standing discipline (same as the A5 test): full 172(+3)-profile calibration suite
held at 170/175 (58/58 HC), zero movement; validate.py 40/41 unchanged; tsc --noEmit
clean. Reverted after testing, holding for Pete's go-ahead before the real commit --
several genuine design/content judgment calls were flagged along the way (base-question
option count, SEVER-30/31/32 naming vs. the 29/29 severity_input_mapping convention,
placeholder option text for SEVER-30/31/32 beyond Pete's mandatory exact-text options)
rather than decided unilaterally.

## C. Report UX and copy
1. Sequencing: the two-paragraph synthesis description currently appears before the
   observable indicators list -- this ordering reads harsher than intended. Consider
   reversing (indicators first, synthesis after) or another resequencing.
2. Asset section tone example, flagged as unnecessarily harsh/backhanded for its
   position in the report:
   "Primary asset domain: Adaptive Capacity. The asset score here is low, and that
   deserves to be said plainly. There is some investment in people development, but
   it has not produced the returns expected, which suggests the underlying conditions
   have been working against it."
3. "Also Present" section (secondary states) is not useful to a user unfamiliar with
   PRV3's taxonomy. Pete is not against showing state names, but only if each is
   hyperlinked to its corresponding /book entry.
4. Broader principle (echoes a PRV2-era lesson): the final report is too
   taxonomy-forward overall. State names and the severity tier label are fine for
   internal/practitioner use but have no value to the client outside the PRV3
   ecosystem -- should not be bare client-facing copy. Diagnosis and severity should
   be communicated in plainspoken terms, consistent with brand voice, not taxonomy
   vocabulary.
5. No welcome/framing message at the start of the diagnostic. Pete's intent: state
   explicitly, by design, that the exercise reflects the respondent's own perceptions:
   Principal Resolution's actual services will bring more objective data and solution
   roadmaps later, via separately designed processes.

## D. Product/business idea (not a bug -- flag for consideration, not scheduled)
Gate or otherwise monetize the full diagnostic suite, but offer a free, condensed,
shorter version that gives limited exposure to its value -- must include at least
some narrative and financial insight, though not necessarily via the same mechanism
as the full version.

## E. Branding refresh -- OD-07 rollback context (separate thread, session-opened
   by Pete wanting to address the site's "sterile" feel)
No rationale for the b8860b5 OD-07 rollback (2026-08-03) is retrievable anywhere --
commit message, MOB, and MemPalace diary (which has a gap on that exact date) all
describe only the mechanics of the revert, never the reasoning. Confirmed via direct
search, not assumed. Revisiting OD-07 (or not) is a fresh decision for Pete, not one
that can be weighed against documented past judgment.

---
Status: raw capture, not yet triaged into the Priority Queue or actioned. Pete to
confirm sequencing before any item here is worked.
