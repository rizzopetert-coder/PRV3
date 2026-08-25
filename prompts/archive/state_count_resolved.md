Superseded — conflicts with current locked 58-state taxonomy as of SCD-WCS Phase 5 ship (f88a7c2). Kept for historical record only.

# State Count — Resolved

## The answer
The count is 45. There is no second removal.

The Paper Tiger and Invisible Performance Management are the same state.
- Invisible Performance Management: pre-rename clinical name, Authority cluster (wrong)
- The Paper Tiger: confirmed evocative name, Aptitude cluster (correct)
- The rename happened in Session 1 but did not propagate to all documents

## What states.py should contain after this step
- Remove invisible_performance_management — done
- Keep the_paper_tiger in Aptitude — correct
- Current count after IPM removal: 46
- Target count: 45

## Wait — recheck before proceeding
If current count is 46 after removing IPM and keeping Paper Tiger, there is still
one extra state. Surface the full 46-state list to Pete sorted by dimension so Pete
can identify the extra.

Do not guess. Do not remove anything without Pete's confirmation.
List all 46 state_ids grouped by primary_dimension and report to Pete.
