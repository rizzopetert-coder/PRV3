# Category E, Direction 3 — Editorial/Typographic Hero: Cluster Display Spec

Status: DRAFT, concept approved by Pete with a real structural correction based on live data. 
Not yet built, not yet through Gemini review.

## Origin
Direction 3 explores de-emphasizing the geometric visualization in favor of typographic 
hierarchy for the headline condition, per the Output Precision principle ("a verdict that names 
one true thing is worth more than a report that names nothing new"). Pete's concern before any 
build: a single bold headline risks implying the named condition is the only one worth 
attention, when multiple conditions are often genuinely co-present.

## Real data behind the concern (verified this session, read-only investigation)
58 real high_confidence calibration profiles run through the actual engine pipeline 
(rank_states → apply_signal_floor → route_output):
- 100% land in multi-state output mode. Zero clean single-state results.
- Qualified-state count: min 2, max 32, median 7, mean 11.8.
- In 29/58 (50%), every qualified state rounds to the identical displayed percentage — the 
  qualification gate (SCD_WCS_ALIGNMENT_THRESHOLD floor plus a 0.05 cosine-unit relative margin 
  gate in check_signal_gate()) routinely produces tight clustering, not a rare edge case.

Conclusion: a fixed 2-state or 3-state tier would undersell the real picture in a large share 
of profiles. Design for a variable-length cluster instead.

## Design direction, corrected
- Headline condition keeps the largest typographic treatment — still one verdict named with 
  confidence, still honoring Output Precision.
- Eyebrow language softened: replace "CONDITION IDENTIFIED" (implies singularity) with 
  something like "MOST PROMINENT PATTERN" (signals rank without claiming exclusivity).
- Below the headline: a variable-length cluster display, not a fixed tier. Real typographic 
  presence (not the current flat bulleted list) for co-present states, with a display cap and 
  a "+N more" affordance for the long tail — needs to gracefully handle both a 2-state case and 
  a 32-state case without either looking sparse or overwhelming.
- "Also Present" section label likely needs replacing too — current framing undersells how tied 
  these routinely are (median 7, half the time literally indistinguishable by displayed %).

## Open, unresolved
- Exact display cap for the cluster (show top 3? top 5? scale the cap to how tight the 
  clustering is?) — design decision, not yet made.
- Exact softened copy for eyebrow/section labels — not yet drafted.
- Whether the underlying qualification-gate math (the 0.05 margin) should change, or only the 
  display of it — this file assumes display-only; any gate-threshold change would be a separate, 
  larger decision requiring its own scoping.

## Next steps
Needs Gemini architecture review before build (touches PrivateOutput.tsx rendering and 
potentially how qualified-state data is shaped for display). Not started.
