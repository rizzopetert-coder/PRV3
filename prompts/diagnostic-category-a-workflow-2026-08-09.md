# Diagnostic Category A Bug/Gap Workflow -- 2026-08-09

Source: prompts/diagnostic-usability-findings-2026-08-09.md, Section A.

## Stage 0+1 -- Investigation (this commit)
Read-only pass over engine/data/questions.py. No writes in this stage.

## Stage 2 -- Fix A1 (missing "Other" option)
web/lib/types.ts's SIGNIFICANT_EVENT_OPTIONS has no "Other" entry. Pending Pete's
call: free-text elaboration field, or flat value with no elaboration. Blocked on
that decision.

## Stage 3 -- Fix A4 (Q42 missing "no" option) + any Stage 1 findings Pete approves
Blocked on Stage 1's findings report and Pete's picks from it.

## Stage 4 -- Design brief: A2 (Q06 multi-select) + A3 (back/forward/reset)
Scoped together -- both touch FlowState and the session/answer API contract.
NOT a CC task -- Claude.ai drafts, Gemini architecture-reviews, per standing
protocol for structural decisions. Blocked on Gemini clearance.

## Stage 5 -- CC implementation of A2+A3 per cleared design
Live production UI change -- push held for Pete's own re-test before going live,
per the standing push-hold exception for unretested prod-facing surfaces.

Status: Stage 0+1 in progress as of this commit.
