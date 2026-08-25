Superseded — conflicts with current locked 58-state taxonomy as of SCD-WCS Phase 5 ship (f88a7c2). Kept for historical record only.

# State Removal — Final Instructions

## The actual problem

The MOB Section 5 list contains 47 names, not 45. The two eliminated/collapsed states
were removed from the taxonomy before the name register audit but their evocative names
still appear in the MOB list. The cross-reference method cannot find them because they
are present in both the MOB and states.py.

## What to do

Step 1 — Remove invisible_performance_management from states.py.
This is confirmed: it appears in states.py but not in the MOB. It is the pre-rename
clinical name for The Paper Tiger.

Step 2 — Add The Paper Tiger to states.py if not already present.
The Paper Tiger is the correct evocative name. It belongs in Aptitude.

Step 3 — Identify the second removal by examining the MOB list directly.
The two names that should NOT be in the MOB list are the evocative-name equivalents of:
- Purpose Deficit (eliminated — no evocative name assigned, was eliminated before naming)
- Workforce Planning Myopia (collapsed into Reactive Talent Management — no standalone
  evocative name assigned)

Search the MOB Section 5 list for any state that:
(a) does not appear in the PRV3_State_Taxonomy_Profiles.docx profiled states, OR
(b) does not appear in the PRV3_Question_Signal_Map.md signal targets

That state is the second removal candidate. Surface it to Pete for confirmation before removing.

Step 4 — After Pete confirms, remove the second state, update validate.py count to 45,
run validation, confirm count = 45, then proceed to Step 3 of the build sequence.
