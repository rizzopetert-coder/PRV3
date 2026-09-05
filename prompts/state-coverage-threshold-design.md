# State-Aware Coverage-Threshold Gate — Design (Gemini-Reviewed, Revised)

Companion to `prompts/friction-tax-legal-compliance-methodology.md` (Addendum 9's "Coverage-threshold caveat," Clusters 1/2/4b). Built 2026-09-05. This doc is the durable design record — the spec Gemini reviewed and revised, and what was actually built against.

## Why this exists

`prompts/friction-tax-legal-compliance-methodology.md` flagged, but never resolved, a real gap: Clusters 1, 2, and 4b priced Legal/Compliance exposure using the federal ADA/Title VII 15-employee threshold as an implicit assumption, with no code ever actually checking it — and no state-law awareness at all, even though many states set their own employer-size threshold well below 15 (New York: 4, California: 5, Illinois: 1). A client in PRV3's "Under 25" headcount bucket sitting in New York was never distinguished from one sitting in a state with no lower threshold, despite a real legal difference in whether the exposure applies at all.

## Design revision — Gemini's three adopted changes

Gemini reviewed the original design and three changes were adopted over it:

1. **`thresholds: dict[str, int]` instead of a `harassment_any_size: bool` flag.** The original design special-cased harassment as a boolean carve-out. The revised design generalizes it to a claim-type keyed dict (`{"general": int, "harassment": int, ...}`), extensible to future claim-type-specific carve-outs (retaliation, pregnancy, etc.) without a schema change. A claim type with no override simply isn't a key — resolution falls through to `"general"`.
2. **Confidence-gated seed data (`CONFIRMED` vs `PARTIAL`), with PARTIAL never driving a dollar-affecting determination.** Rather than only seeding the handful of independently-verified states and leaving the rest absent, every US jurisdiction (50 states + DC) gets a real entry — but `resolve_coverage_gate()` structurally prevents an unverified `PARTIAL` entry from ever being the reason a coverage determination changes, surfacing it as a qualitative flag instead.
3. **Explicit aggregate-headcount limitation, not silently assumed away.** PRV3 collects only aggregate national headcount, not per-state employee counts — this is called out as a known, tracked limitation rather than quietly built around.

## Data structure

```python
@dataclass(frozen=True)
class StateCoverageThreshold:
    thresholds: dict[str, int]           # claim_type -> minimum headcount for coverage
    damages_cap_treatment: str           # "uncapped" | "state_specific_tiers" | "federal_cap_applies"
    confidence: str                      # "CONFIRMED" | "PARTIAL"
    citation: str

STATE_COVERAGE_THRESHOLDS: dict[str, StateCoverageThreshold]  # keyed by 2-letter state code
```

Lives in `engine/friction_tax.py`, adjacent to the Legal/Compliance dollar-curve constants it gates. `engine/data/jurisdiction.py`'s `JURISDICTION_TABLE` is imported read-only, purely as the authoritative 51-jurisdiction key set the PARTIAL fill-in iterates over — **`jurisdiction.py`, `JURISDICTION_TABLE`, and `resolve_jurisdiction_flags()` are untouched**, confirmed by Gemini review as a fully separate mechanism (transparency/retaliation/procedural policy flags) with zero overlap.

## Seed data

### CONFIRMED (7 states) — independently verified against primary statute text this session, not aggregator-only

| State | Thresholds | Damages cap | Citation |
|---|---|---|---|
| CA | general=5, harassment=1 | uncapped | Cal. Gov. Code §12926(d), §12940(a) |
| NY | general=4, harassment=1 | uncapped | NYSHRL, N.Y. Exec. Law §§292,296,297; 2019 amendments S.6577/A.8421 (uncapped incl. punitive — corrects a common but wrong "$10,000 cap" claim, which is housing-only/pre-2019) |
| MA | general=6 | uncapped | M.G.L. c. 151B §4; Haddad v. Wal-Mart Stores, Inc., 455 Mass. 91 (2009). **Fontaine v. Philip Morris (argued Nov 5, 2025) is a pending case that could affect punitive-damages doctrine — flagged for future revisit, not treated as resolved.** |
| IL | general=1 | federal_cap_applies (modeled — real nuance: IHRA allows uncapped compensatory but NO punitive damages, distinct from CA/NY/MA/WA's genuine "uncapped") | 775 ILCS 5/2-101(B)(1)(a), P.A. 101-0430 eff. July 1 2020 — applies to ALL protected categories including race, confirmed via current statute text correcting an aggregator source that incorrectly claimed race-discrimination still required 15+ under stale pre-2020 law |
| WA | general=8 | uncapped (compensatory; no state-specific punitive cap identified) | RCW 49.60.040; Blakely v. City of Vancouver |
| AK | general=1 | federal_cap_applies (**damages_cap_treatment itself NOT independently verified this session — only the threshold is CONFIRMED; defaulted conservatively per explicit instruction, flagged in code comment**) | AS 18.80.300(5): "employer means a person...who has one or more employees" |
| WV | general=12 | federal_cap_applies (same unverified-damages-cap caveat as AK) | W. Va. Code §5-11-3(d); WV CSR 77-7-2 |

The schema doesn't support a sub-field confidence level (only one `confidence` per entry). Per explicit instruction, AK/WV's overall entry confidence stays `CONFIRMED` (the threshold is real) while `damages_cap_treatment` defaults to `federal_cap_applies` with an inline code comment flagging it as unverified — not a schema change.

### PARTIAL (44 remaining jurisdictions: all other states + DC)

**Sourced, but not independently verified this session.** An untracked file, `research/jurisdiction-research-headcount.md` (a 50-state survey, same session, produced via secondary aggregators — Justia, Blanchard & Walker — and law-firm summaries), was found during this build already sitting in the repo without being referenced in the task itself. Flagged to Pete before use, since it wasn't part of the original spec and its own confidence bar is looser than this build's 7-state CONFIRMED set (several of its own rows are marked "CONFIRMED (secondary source)" — a standard the source document's own Caveats section admits isn't primary-statute-text verification: *"these should be statute-verified before use in a paid product"*). Pete's decision: use it to enrich the 44 PARTIAL entries with its real per-state figures rather than a uniform placeholder — all 44 stay `confidence="PARTIAL"` regardless of what that source document calls its own rows, since none meet this build's primary-statute-text bar.

Each of the 44 entries now carries the source document's actual reported threshold, a `damages_cap_treatment` mapped from its damages description (`"uncapped"` where the source explicitly says so; `"state_specific_tiers"` where a state sets its own distinct cap, tier structure, or bars punitive damages entirely; `"federal_cap_applies"` as the default wherever the source didn't confirm a cap), and a citation naming both the underlying statute and the source document. Two harassment carve-outs beyond the CONFIRMED set were also captured (`AZ`: harassment=1, `MD`: harassment=1). Real internal conflicts the source document flags itself (Alaska: 1 vs. 2 employees; West Virginia: 12 vs. 15) are left unresolved here — worth noting they cross-validate against this build's own CONFIRMED AK/WV entries, which independently landed on the same lower figures (1 and 12) via primary statute text.

Populated as real dict entries (not simply absent) so `resolve_coverage_gate()`'s flip-detection and qualitative-only flag logic have genuine per-state data to reason against, and so a future session can upgrade any one of these to `CONFIRMED` with a real primary-source pass, without a schema change. `research/jurisdiction-research-headcount.md` itself is now tracked in git as the cited source.

## `resolve_coverage_gate()`

```python
def resolve_coverage_gate(headcount: int, jurisdictions: list[str], claim_type: str = "general") -> CoverageResult
```

1. For each jurisdiction in the input with `confidence == "CONFIRMED"`, look up `thresholds.get(claim_type, thresholds["general"])`.
2. Take the **minimum** threshold across all CONFIRMED jurisdictions found (most-protective-wins — same shape as `jurisdiction.py`'s existing highest-restriction pattern, a different table).
3. If no CONFIRMED jurisdiction is present, fall back to the federal threshold for `claim_type` — 15 for anything not explicitly `"fmla"`, 50 for `"fmla"`.
4. Compare `headcount` against the resolved threshold. Return `applies`, `threshold`, `driving_jurisdiction` (the CONFIRMED state that produced the answer, or `None` for the federal fallback), and `confidence` (`"CONFIRMED"` | `"FEDERAL_FALLBACK"`).
5. **PARTIAL-state-could-have-flipped-it flag:** when a CONFIRMED-driven answer is returned but a PARTIAL jurisdiction was also present in the input, check whether including that PARTIAL jurisdiction's own threshold (via the same most-protective-wins rule) would have flipped `applies`. If so, `partial_state_flag=True` even though the returned number came from CONFIRMED data alone.
6. **Empty or PARTIAL-only input:** if `jurisdictions` is empty, or contains only PARTIAL-confidence jurisdictions with no CONFIRMED jurisdiction present, the numeric gate still uses the federal fallback (never a PARTIAL jurisdiction's own unverified number) — but `partial_state_flag=True` whenever a PARTIAL jurisdiction was actually named in the input, naming which one(s) via `partial_jurisdictions_considered`, so a caller can compose a specific caveat rather than a generic one.

Both step 5 and step 6 signal through the same `partial_state_flag`/`partial_jurisdictions_considered` fields — `confidence` tells the caller which of the two situations occurred.

## Aggregate-headcount limitation (explicit, tracked)

PRV3 collects only aggregate national headcount (`IntakeData.headcount`), not per-state employee counts. This gate necessarily compares that aggregate against the most-protective threshold across selected jurisdictions. This can overstate coverage if a specific claim would legally arise from a single low-count location rather than the org's total headcount — and whether a given state's own threshold counts aggregate or in-state-only headcount is itself state-specific and **unresearched this session**. Neither counting method is assumed correct. Documented as a code comment on `resolve_coverage_gate()` and tracked below as an explicit open item.

## Output-generation constraint (not yet applicable — nothing consumes `CoverageResult` for output today)

`compute_legal_compliance_exposure()`'s own header comment already states it is "NOT wired into `compute_friction_tax()`'s return dict, `engine/contract.py` [output], or `web/lib/types.ts` — that integration is separately scoped." Nothing downstream currently renders Legal/Compliance dollar figures to a client at all, so there is no existing output-generation code path to wire `CoverageResult`'s `partial_state_flag`/`confidence` into yet. Recorded here as a real constraint for whenever that output integration is built: **the output must never imply nationwide applicability of a single state's law when multiple jurisdictions are selected** — if `driving_jurisdiction` is set, the output should name that specific state, not present the figure as if it applies everywhere the client operates.

## Integration

- **Clusters 1 and 2** (`_single_state_legal_pricing()`): call `resolve_coverage_gate(headcount, jurisdictions, claim_type="general")` before computing any exposure figure. Not covered → `LegalPricingStatus.NOT_APPLICABLE` (dollar_range=None) — genuinely zero/not-applicable, the existing status for "doesn't apply at all," not a new one.
- **Cluster 4b** (`_cluster_4_curve_for_org_type()`): the gate runs *after* ruling out "Publicly traded" (4a) and "Government" (4c) — those two are out of scope for this coverage question entirely — and *before* the existing `_CLUSTER_4B_CEILING_BY_HEADCOUNT` bucket lookup. Not covered → `NOT_APPLICABLE`, same as above.
- Both integration points default `claim_type="general"` — **no per-state claim-type mapping was built** (e.g. which of the 30 Legal-scoring states represents a harassment claim specifically, which could resolve to a lower CONFIRMED threshold). That would be new clinical judgment beyond this build's scope, not inferred from the taxonomy here.
- `compute_legal_compliance_exposure()`'s new `jurisdictions` parameter defaults to `None`/`[]`, so every pre-existing call site (tests, `calibration_runner.py`) keeps working unchanged — an empty list falls through to the federal threshold, which every real org_size value used anywhere in this project's test/calibration data already clears.
- `engine/contract.py`'s live call site now passes `jurisdictions=session.intake.jurisdictions` — the real intake field, already collected today (though see Next Steps: intake's live UI only ever populates a single-element list).

## Testing

`tools/test_friction_tax.py`, new tests 33-40 (93 → 121 checks): `STATE_COVERAGE_THRESHOLDS` structural checks (51-key coverage, exactly 7 CONFIRMED, every entry has a `general` key and non-empty citation); single-CONFIRMED-state resolution; multi-state most-protective-wins (order-independent); federal fallback for empty input, including the `fmla` vs `general` threshold split; `claim_type` changing the resolved threshold for a state with both (CA general=5 vs harassment=1); PARTIAL-only input never reaching `confidence="CONFIRMED"` while still raising the qualitative flag; the PARTIAL-state-could-have-flipped-it case (via a temporary monkey-patch of TX's entry, since real seed data — every PARTIAL defaulted to 15 — can never actually trigger this path on its own); and 7 integration tests confirming the gate is genuinely wired into Clusters 1, 2, and 4b end-to-end through `compute_legal_compliance_exposure()` (including that 4a/4c remain unaffected, and that passing a real `jurisdictions=["NY"]` value changes the outcome for a headcount that fails the federal threshold but clears NY's).

## Explicit non-changes

`engine/data/jurisdiction.py`, `JURISDICTION_TABLE`, `resolve_jurisdiction_flags()` — untouched, confirmed by Gemini review as a fully separate mechanism.

## Next steps (open, not started here)

- **Per-state employee-counting method (aggregate vs. in-state-only) for coverage-threshold purposes — not yet researched, currently defaults to aggregate headcount as a conservative simplification.** Also added to `prompts/friction-tax-legal-compliance-methodology.md`'s open-items list.
- The 44 PARTIAL jurisdictions now have a real secondary-source figure each (`research/jurisdiction-research-headcount.md`), but still need primary-statute-text verification before any of them can upgrade to CONFIRMED — that document's own Caveats section names the conflicts and secondary-source-only rows most worth prioritizing (Alaska, West Virginia, Illinois's already-resolved race-discrimination conflict, Virginia's tiered thresholds, and damages-cap data for Texas/Tennessee/Florida/Colorado specifically).
- `damages_cap_treatment` is captured in the schema but not yet consumed anywhere — a future pricing extension could adjust Cluster 1/2/4b's dollar ceiling by state (e.g. CA/NY/MA/WA's "uncapped" status vs. Cluster 1's flat $450K ceiling), but that's a separate, larger design question from the applicability gate built here.
- Per-state claim-type mapping (which of the 30 Legal-scoring states is harassment-flavored vs. general) — not resolved, `claim_type="general"` used uniformly in the integration.
- AK/WV's `damages_cap_treatment` sub-field needs independent verification (currently a flagged, conservative default alongside a CONFIRMED threshold).
- Output-generation wiring (the "never imply nationwide applicability" constraint above) has no real consumer yet, since Legal/Compliance dollar output isn't wired into any client-facing surface at all today.
