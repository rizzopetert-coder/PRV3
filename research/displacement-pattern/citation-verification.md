# Citation Verification: Displacement Pattern Attribution

**Verification date:** 2026-06-27
**Verifier:** Claude Code (Session 56)
**Claim under verification:** The informal "70% of organizational change programs fail" figure referenced in PRV3 E4 research (Consulting Engagement Postmortem Analysis)
**Tracked-claims entry:** `change-management-failure-rate` in `research/refresh-log/tracked-claims.json`

---

## Verification outcome

**The 70% figure is not empirically grounded.** Two independent peer-reviewed sources confirm this. The figure traces to secondary citation chains and a single unscientific 1993 estimate, not to studies that calculated failure rates from defined denominators.

The correct, empirically grounded range is **~30% to ~65%+**, depending on how failure is defined (unsuccessful program vs. no measurable effect in trials) and how long the observation period runs.

---

## Primary source: de Waal (2026)

**Full citation:** de Waal, A. (2026). Beyond the 70% Myth: What Do We Actually Know About Failure Rates in Improvement and Transformation Initiatives? *Journal of Engineering Management and Competitiveness (JEMC)*, Vol. 16, No. 1. DOI: 10.5937/JEMC2600001W

**Received:** 31 January 2026. **Accepted:** 12 February 2026.

**Key finding (page 6, verbatim):**
> "Depending on how failure is defined (unsuccessful program vs no-effect in trials), empirically grounded 'failure' can range from roughly ~30% to ~65%+, so treating 70% as a single universal figure is not justified."

**Abstract conclusion (verbatim):**
> "the evidence does not support treating '70% failure' as a universal planning parameter; failure prevalence is best understood as a distribution conditional on what is counted and for how long"

**Robustness labeling methodology:** de Waal applied a four-tier label to each of the 17 academic sources reviewed:
- **Label A** — rate calculated from study's own data with a transparent denominator (highest evidentiary quality)
- **Label B** — secondary citation: rate sourced from citing another paper without recalculating
- **Label C** — perceived rate: self-reported estimate rather than calculated rate
- **Label D** — unclear provenance: insufficient information to assess source

**Finding on label distribution:** Most academic claims citing ~70% are label B or D. Only two of the 17 reviewed sources are label A:

| Study | Finding | Label |
|---|---|---|
| Jones et al. (2021) | 27.5% of change programs unsuccessful | A |
| Hill et al. (2020) | 54.2%–100% no-effect rate on outcomes (depending on metric) | A |

The "~30% to ~65%+" range synthesizes these two label-A studies: Jones at the lower bound (Type 1, unsuccessful program definition) and Hill at the upper bound (Type 2, no-effect-in-trials definition).

---

## Secondary source: Hughes (2011)

**Full citation:** Hughes, M. (2011). Do 70 Per Cent of All Organizational Change Initiatives Really Fail? *Journal of Change Management*, 11(4), 451-464. DOI: 10.1080/14697017.2011.630506

**Finding:** The 70% figure traces to a single 1993 source (Kotter) that Hughes identifies as an explicitly unscientific estimate — not derived from a study with a defined population and denominator. Subsequent repetition in the literature is citation chain amplification of the original unscientific estimate, not independent verification.

---

## Integration decision

**Replacement language for E4 essay and any other /book content that cites the 70% figure:**

The figure is replaced with de Waal's empirically grounded range: *"roughly 30% to 65% or more, depending on how failure is defined and for how long it is measured"* (or equivalent phrasing that accurately represents the conditional nature of the range).

**Citation assignments for displacement-pattern essay:**
- **HC-HUGHES-2011** — direct textual connection: names the 1993 source chain and confirms lack of empirical basis
- **HC-DEWAAL-2026** — direct textual connection: provides the empirically grounded replacement range

Additional displacement-pattern citations (HC-ROSS-1977, HC-GREEN-1979, HC-SWIFT-2013, HC-REASON-1990, HC-SENGE-1990, HC-SAKS-2006) support the broader attribution and structural-reassertion argument and are assigned to the essay only where the final prose directly draws on them. See handoff acceptance criterion 3 and Gemini recommendation 3.

---

## File-level search results

Exhaustive grep across all .md, .ts, .tsx, .html files in the repo on 2026-06-27 for the pattern `70.{0,30}(fail|change|program|initiative|transform)` (case-insensitive):

- **`research/seven-experiments/experiment-4-consulting-engagement-postmortem-analysis.html`** — no match. This file discusses consulting failure patterns conceptually but does not cite the 70% statistic numerically.
- **`web/content/book/**`** — no matches in any committed or untracked /book content.
- **`tools/` and `documents/`** — matches are test suite output tables (FAIL/PASS status rows) and stale MOB backups; none cite the change-management failure-rate claim.

**Conclusion:** No live content file requires a 70% → de Waal range substitution. The displacement-pattern essay (essay-4) will be the first /book content to cite this research, using the verified range from the outset.

---

## tracked-claims.json update required

After essay-4 is committed, update `research/refresh-log/tracked-claims.json`:
- Change `last_verified` from `"not yet independently verified"` to `"2026-06-27 (de Waal 2026 confirms ~30% to ~65%+ range — see research/displacement-pattern/citation-verification.md)"`
- Add essay-4's slug to `used_in` once the essay is committed
