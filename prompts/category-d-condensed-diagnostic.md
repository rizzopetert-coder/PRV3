# Category D — Free Condensed Diagnostic: Concept Sketch

Status: DRAFT, exploratory. Not yet approved for build. Captures the concept as of 2026-08-11
so it survives context loss — nothing here is locked.

## Goal
A <5-minute free experience producing a real-but-thin report — a taste of the full diagnostic,
functioning as a lead-capture point that fills the funnel toward the paid full Dx and, 
downstream, services.

## 1. Question Selection
Target: 8-10 questions, ~30 sec/question including reading time, fits under 5 minutes.

Selection criteria (candidates to be pulled from real engine/data/questions.py content, not 
guessed from memory):
- Drawn entirely from the existing 42 core questions — zero new content authored, zero new 
  taxonomy, zero calibration risk.
- Spread across all four dimension clusters (Aptitude/Authority/Alliance/Attitude) — not 
  weighted toward one.
- Prefer questions with the broadest state_targets fan-out over narrow single-state questions.
- Exclude any question that only makes sense with prior context (the six positions that needed 
  the dangling-pronoun rewrite, or any question authored as a mid-sequence continuation) — every 
  condensed-tier question must stand alone.

## 2. Result Shape — same structure as full report, truncated

| Full Report | Condensed Report |
|---|---|
| Top state + secondary ("Also Present") states | Top state only |
| Full indicator list | 2-3 indicators |
| Two-paragraph synthesis | One paragraph |
| Full Friction Tax estimate | Simple benchmark-based figure |
| — | New: explicit "partial read" framing + CTA to unlock full diagnostic |

Truncation should be visible, not silently omitted (e.g., "3 more indicators identified" shown 
greyed/locked) — the limitation itself is part of the pitch.

## 3. Financial Insight Mechanic
A single generic benchmark (e.g., cost-of-turnover as % of payroll) applied against the 
headcount/payroll already collected at intake — straight multiplication, NOT Friction Tax's 
multi-state compounding model. Full Friction Tax stays exclusively behind the full paid Dx.

Before this ships: the specific benchmark figure requires a Demographic Applicability Filter 
pass (source's actual population boundary, confirm coverage of the free tier's realistic 
respondent range, check the extremes) per the existing locked protocol 
(prompts/demographic-applicability-filter-protocol.md) — lighter lift than Friction Tax since 
it's one static figure, not a multi-input formula, but the same discipline applies.

## 4. Funnel / CTA
Condensed report ends with a "Get your full diagnostic" CTA. Downstream mechanics (self-serve 
paid checkout vs. lead-capture-then-manual-code) are explicitly NOT part of this build.

## 5. Sequencing
1. Now: build and ship the condensed tier. Full diagnostic stays exactly as-is (free, ungated).
2. Later, separate decision: paywall/lead-capture for the full Dx — not blocking Phase 1.

## Open questions (unresolved, Pete's call)
- Is 8-10 questions the right count, or does Pete want to see concrete candidate question 
  lists first before locking the number?
- Visible truncation (greyed/locked additional indicators) vs. silent omission — no decision yet.
- Full-Dx gating mechanism (paywall vs. lead-capture vs. hybrid) — explicitly out of scope for 
  this phase, to be decided separately once the condensed tier is live.
