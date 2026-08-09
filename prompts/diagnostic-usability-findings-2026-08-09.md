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
