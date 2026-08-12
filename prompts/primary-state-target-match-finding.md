# Primary-State / Intended-Target Match Rate — Flagged Finding

Status: FLAGGED, not investigated further. Surfaced as a side effect of Category E Direction 3's 
pre-scoping data pull (this session). Not scheduled, not urgent, Pete's call on if/when to open 
this thread.

## The finding
Across the same 58 real high_confidence calibration profiles pulled for the Direction 3 spec: 
the displayed primary_state (the actual #1-by-score result from rank_states()) matched the 
profile's own intended target state in only 1 of 58 cases. In the other 57, the intended target 
landed anywhere from rank 2 to rank 58 (dead last) among all states — usually surfacing 
somewhere inside the tied secondary cluster instead of at rank 1.

## Context — this may be within expected design tolerance, not a new problem
This project's calibration suite has a long-locked, deliberate pass criterion: cluster/top_3/
prominence, not rank-1 (Session 7 precedent, reconfirmed at Session 69 when only built_to_fail 
was found to reliably achieve rank-1 anywhere in the 57/58-state taxonomy). The philosophy has 
always accepted that clean rank-1 wins are rare by design, given how much dimensional overlap 
exists across a taxonomy this size. The calibration suite's own pass bar (SCD_WCS_CLUSTER_WINDOW 
= 0.35) is also confirmed far more permissive than the live display's actual qualification gate 
(0.05) — so this isn't a hidden calibration-suite failure; it's a distinct property of the live 
margin gate specifically, sitting underneath a pass bar designed with wide tolerance already in 
mind.

## The open question
Is 1/58 still inside what "cluster/top_3, not rank-1" was always expected to produce, or does 
it indicate the taxonomy has more dimensional overlap between states than originally intended — 
worth a real investigation? Not resolved here. This file only records the finding and the 
context needed to evaluate it later, not a conclusion.

## Methodology caveat, honestly flagged
This used generate_answers()'s systematic answer-selection heuristic, not organic human answers 
— real respondent answers could spread scores less evenly than the calibration harness's 
formulaic selection does. The structural cause (states sharing closely related 
dimensional_vector profiles) is a property of the taxonomy itself though, not an artifact of 
test-answer generation, so some degree of clustering would likely persist with real answers, 
just perhaps less starkly tied.

## Status
Not blocking Category E Direction 3 — the report should represent real multiplicity honestly 
regardless of the answer to this question. Logged as its own thread, separate scope, no action 
scheduled.
