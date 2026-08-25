Superseded — conflicts with current locked 58-state taxonomy as of SCD-WCS Phase 5 ship (f88a7c2). Kept for historical record only.

# State Removal — v3

## Confirmed so far
- invisible_performance_management: removed. correct.
- the_paper_tiger: added to Aptitude. correct. it belongs in the taxonomy.
- The Paper Tiger did not propagate to profiles doc or QSM during Session 1 rename.
  That is a document gap, not a removal signal. Do not use its absence as a removal indicator.

## The actual target
Current states.py count: 47
Target count: 45
Two net removals required from the original 47-profile starting point.
invisible_performance_management removal = 1 of 2.
One more removal needed.

## How to find the second removal
The two pre-taxonomy clinical names that were eliminated before the name register audit:
- Purpose Deficit — eliminated entirely, no evocative name assigned
- Workforce Planning Myopia — collapsed into Reactive Talent Management, no standalone evocative name

One of these became an evocative-named state in states.py in error — it was built into
the data layer but should not have been because it was eliminated or collapsed before
the name register existed.

Search states.py for any state whose resolution_family or description indicates it is:
(a) a root condition rather than a presenting condition, OR
(b) an operational/planning condition that a Principal would not recognize as their own problem

Cross-reference the 47 states.py entries against the 45-state QSM signal target list.
The QSM was built against the confirmed 45-state taxonomy. Any state_id in states.py
that has no corresponding entry in the QSM signal targets is the second removal candidate.

Surface the candidate to Pete for confirmation before removing.
Do not remove without Pete's confirmation.
After Pete confirms: remove, set validate.py count to 45, run validation, report result.
