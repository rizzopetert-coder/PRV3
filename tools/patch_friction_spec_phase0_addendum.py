"""
Patch prompts/friction-tax-rebuild-build-spec.md with the Phase 0 corrections and
rulings (Pete, 2026-09-30). Existing sections are annotated in place with a pointer
to the addendum, not rewritten. The only value changes are the two Section 6b rows
and the two Section 3 q cells that R3 recomputes from the rounded JOLTS rates.

Usage:
    python tools/patch_friction_spec_phase0_addendum.py --dry-run
    python tools/patch_friction_spec_phase0_addendum.py --write
"""

import sys
from pathlib import Path

SPEC = Path(__file__).resolve().parents[1] / "prompts" / "friction-tax-rebuild-build-spec.md"
ADD = "(addendum)"

ADDENDUM = """
## Phase 0 corrections and rulings (Pete, 2026-09-30)

This addendum supersedes the sections it names. Existing sections are annotated in place with a pointer here. Phase 0 baseline: `tools/capture_legal_baseline.py` and `tools/fixtures/legal_compliance_baseline.*`, commits `6c067fd`, `517dbed`, `fc87f9a`, pushed 2026-09-30. Check with `python tools/capture_legal_baseline.py --check`.

### Stage numbering

Section 10 steps map to the stages used in Phase 0 reporting: Stage 1 = step 2 (state criteria), Stage 2 = step 3 (org list ownership), Stage 3 = step 4 (wage refresh), Stage 4 = step 5 (two-channel function), Stage 5 = step 6 (condensed), Stage 6 = step 7 (web types and consumers), Stage 7 = step 8 (tests and full verification), Stage 8 = step 9 (production round-trip).

### Rulings

- **R1. Legal keeps a frozen May 2023 wage table.** Add `_LEGAL_WAGE_DATA_MAY2023` to `engine/friction_tax.py`, a copy of the current `_INDUSTRY_WAGE_DATA` values, with a comment explaining that Legal must stay byte-identical to the Phase 0 baseline while friction wages move to May 2025. The Ohio compensatory formula (`engine/friction_tax.py:3973`, `_oh_compensatory_damages_pricing`) and `tools/test_friction_tax.py:1933` read the frozen table. It is added in Stage 3 before `_INDUSTRY_WAGE_DATA` is replaced. Evidence for the need: changing one industry's wage in memory changed 42 of 870 baseline blocks, every one under an Ohio jurisdiction set. Moving Legal to May 2025 wages is a separate future decision, not acted on here. Carry it to the 13b item at closeout.
- **R2. The condensed figure moves behind `FRICTION_DOLLARS_VISIBLE`.** The "Estimated cost of one departure in this pattern" block in `web/components/CondensedOutput.tsx` (render at about lines 133-146) is gated by the flag in this build, joining Stage 5's scope. The "roughly 50-75%" copy is removed, not reworded, because it contradicts the verified 0.333 figure. When the flag is false the condensed report shows no dollar figure. The existing unavailable note ("A benchmark figure isn't available for the industry provided.") is reused only if it reads correctly for a hidden figure. If it does not, the copy is proposed to Pete and the work stops. The flag stays false throughout the build.
- **R3. JOLTS rates are stored as the rounded 2-decimal monthly values in Section 3.** The annual q is that monthly value times 12 (Retail & Hospitality 3.37 x 12 = 40.44%, Nonprofit & Education 1.64 x 12 = 19.68%, the rest unchanged). The Section 6b worked figures are recomputed from these values. Old figures, computed from unrounded weighted rates (3.3670 and 1.6395), kept for the record: 12 / Retail & Hospitality turnover $28,497, total $63,898. 400 / Nonprofit & Education turnover $800,891, total $2,844,132. All other rows are unchanged. Fixtures follow the rounded values.
- **R4. Gzip storage of the canonical JSON baseline is accepted.** The hash is over the uncompressed canonical bytes.
- **R5. Decision 14 implementation.** Remove `inaction_cost_low` and `inaction_cost_high` from `ServiceCostComparison` and from the payload, with no replacement fields. The two lines read directly from the new `friction_tax_estimate` (typical-loss point estimate) and the existing `legal_tail_risk_exposure` (tail-risk range). Before Stage 4, list every consumer of `inaction_cost_*` across the engine, API, web and tests, and confirm none needs a dedicated field. If one does, stop and report it. `tools/test_phase1_report_data.py:188-191` changes with this.
- **R6. The share-payload name guard test moves from Stage 6 to Stage 4**, into the same commit that introduces `friction_receipts` and `channels`. It must fail if a share payload, at write (`share/create`) or at read (`getShareRecord`), carries `friction_tax_estimate`, `legal_tail_risk_band`, `friction_receipts` or `channels`. The current read-side strip (`web/lib/share-store.ts:53-62`) names only the first two, so the guard asserts on the returned payload rather than relying on the strip.

### Phase 0 corrections

- `web/lib/types.ts` line drift: `friction_tax_estimate` is at :375, the ledger at :382, `legal_tail_risk_exposure` at :385 and `inaction_cost_*` at :578-579. The spec's :377, :384 and :520 are comments, and :581 is `service_estimate_high`.
- `web/components/CondensedOutput.tsx:130` is a comment. The render is at about :133-146.
- `web/app/api/share/create/route.ts:189` is `intake: mapIntake(...)`. `share/create` no longer carries any friction field (`2e56044`, `8680886`), so any "pass-through" wording about it is stale. The shareable payload is a whitelist at write and `getShareRecord` strips two named fields at read.
- Missing from Section 8: `tools/test_phase1_report_data.py:188-191`, `web/app/api/share/create/route.test.ts`, `web/lib/share-store.test.ts` (keep both as strip guards).
- The `engine/friction_tax.py` docstring (lines 7-8 and 31) says 54 cells, 9 industries and 57 states. Live is 66, 11 and 58. It is fixed in Stage 4.
- The BLS OEWS management share (11-0000) is not an engine input (decision 5). It stays in the verification doc as research.
- The `/api/condensed-complete` response shape change (`condensed_financial_range`, `api/engine.py:285`) is under the live production round-trip rule. No `vercel.json` route and no new FastAPI endpoint is added by this spec.

### W and q primary-source check (Claude Code, 2026-09-30)

The verification doc records the method for W (Section 2b mapping, `nat3d_M2025_dl.xlsx`) but contains no W table and no JOLTS values, so both were checked against primary files this session. W: `oesm25in4.zip` (`nat3d_M2025_dl.xlsx`, and `nat3d_owner_M2025_dl.xlsx` for privately owned rows 611 and 622), all-occupation A_MEAN weighted by TOT_EMP over the Section 2b mapping. All 11 match Section 3 to the dollar, and employment totals match Section 2b. The ownership codes disclosed in Section 3 were confirmed (713 and 721 are code 57, 491 is code 1, government 999000 is code 123). q: BLS JOLTS Table 22, annual average quits rates, 2025 column (read from bls.gov/news.release/jolts.t22.htm, last modified March 13, 2026). The Table 22 footnote defines the annual average as the sum of 12 monthly quits as a percent of the sum of 12 monthly employment, so the value is an average monthly rate and x12 annualizes it. All nine direct rows match. The two blended rows recompute from OEWS employment: Retail & Hospitality 3.367 rounds to 3.37, Nonprofit & Education 1.6395 rounds to 1.64. No Section 3 value changed.
"""

# (anchor substring, replacement) pairs. Each anchor must occur exactly once.
REPLACEMENTS = [
    ("Every code reference below was read live on 2026-09-30.",
     "Every code reference below was read live on 2026-09-30. Phase 0 corrections and rulings (Pete, 2026-09-30) are in the addendum at the end of this file and supersede the sections they name."),
    ("| REPLACE with OEWS May 2025 (Section 3), new citation ids |",
     "| REPLACE with OEWS May 2025 (Section 3), new citation ids. **R1 " + ADD + ": Legal keeps a frozen copy, `_LEGAL_WAGE_DATA_MAY2023`, because the Ohio compensatory formula reads this table directly (`:3973`).** |"),
    ("| KEEP, returns May 2025 |",
     "| KEEP, returns May 2025. **R2 " + ADD + ": the condensed figure it feeds moves behind `FRICTION_DOLLARS_VISIBLE`.** |"),
    ("| sends a numeric string | latent: Path 1 sharing is disabled (DiagnosticFlow.tsx:930). Fix when sharing is enabled. |",
     "| sends a numeric string | latent: Path 1 sharing is disabled (DiagnosticFlow.tsx:930). Fix when sharing is enabled. Phase 0 correction " + ADD + ": `share/create` no longer carries any friction field (`2e56044`, `8680886`). |"),
    ("| REPLACE with wage x 0.333 (P9), single value |",
     "| REPLACE with wage x 0.333 (P9), single value. **R2 " + ADD + ": the figure also moves behind `FRICTION_DOLLARS_VISIBLE` and the \"roughly 50-75%\" copy is removed.** |"),
    ("| 3.37, Retail trade 2.6 and Accommodation and food services 4.2 weighted by OEWS employment | 40.4% |",
     "| 3.37, Retail trade 2.6 and Accommodation and food services 4.2 weighted by OEWS employment | 40.44% (R3 " + ADD + ": 3.37 x 12) |"),
    ("weighted by OEWS May 2025 employment | 19.7% |",
     "weighted by OEWS May 2025 employment | 19.68% (R3 " + ADD + ": 1.64 x 12) |"),
    ("W (May 2025) is the employment-weighted mean of the 3-digit NAICS",
     "R3 " + ADD + ": q is stored as the rounded 2-decimal monthly rate shown above, times 12. W and q were verified against primary files on 2026-09-30, see the addendum. W (May 2025) is the employment-weighted mean of the 3-digit NAICS"),
    ("`:377`, `:384`, `:520` (payload fields), `:581` (`inaction_cost_*`).",
     "`:377`, `:384`, `:520` (payload fields), `:581` (`inaction_cost_*`). Phase 0 correction " + ADD + ": the live lines are :375, :382, :385 and :578-579. R5 " + ADD + " removes `inaction_cost_*`."),
    ("`web/app/api/share/create/route.ts:189` (pass-through, type changes only).",
     "`web/app/api/share/create/route.ts:189` (pass-through, type changes only). Phase 0 correction " + ADD + ": stale, `share/create` carries no friction field since `2e56044`."),
    ("`web/components/CondensedOutput.tsx:130` (range to single value).",
     "`web/components/CondensedOutput.tsx:130` (range to single value). Phase 0 correction " + ADD + ": :130 is a comment, the render is at about :133-146. R2 " + ADD + " gates it behind `FRICTION_DOLLARS_VISIBLE` and removes the \"roughly 50-75%\" copy."),
    ("not a sum, since one is a point and the other a range (Decision 14).",
     "not a sum, since one is a point and the other a range (Decision 14). **R5 " + ADD + ": implemented by removing the fields with no replacement.**"),
    ("A single differing byte fails the test and blocks the build.",
     "A single differing byte fails the test and blocks the build. Phase 0 " + ADD + ": recorded in `6c067fd`, `517dbed`, `fc87f9a`, gzip storage accepted (R4), check with `python tools/capture_legal_baseline.py --check`."),
    ("plus the server-render test that no friction dollar reaches the report screen (stays as is).",
     "plus the server-render test that no friction dollar reaches the report screen (stays as is). Phase 0 correction " + ADD + ", also in scope: `tools/test_phase1_report_data.py:188-191` (changes with R5), and `web/app/api/share/create/route.test.ts` and `web/lib/share-store.test.ts` (keep as strip guards, R6 adds the name guard in Stage 4)."),
]

# Section 6b rows (R3): replaced whole, old figures are recorded in the addendum.
ROW_REPLACEMENTS = [
    ("| 12 / Retail & Hospitality |",
     "| 12 / Retail & Hospitality | $42,024 | 3.37, 40.44% | $504,288 | $35,401 | $28,522 | $63,923 | 7.02% | 5.7% | 12.7% |"),
    ("| 400 / Nonprofit & Education |",
     "| 400 / Nonprofit & Education | $72,765 | 1.64, 19.68% | $29,106,000 | $2,043,241 | $801,127 | $2,844,368 | 7.02% | 2.8% | 9.8% |"),
]

# Appended to the end of the line that starts with the prefix.
LINE_APPENDS = [
    ("4. **Wage refresh.**",
     " **R1 " + ADD + ": first add `_LEGAL_WAGE_DATA_MAY2023` (a copy of the current values) and point the Ohio formula and `tools/test_friction_tax.py:1933` at it, then replace `_INDUSTRY_WAGE_DATA`. `--check` must stay byte-identical. The condensed figure changes here too, see R2.**"),
    ("5. **Two-channel function.**",
     " **Phase 0 " + ADD + ": R5 removes `inaction_cost_*`, R6 adds the share-payload name guard in this stage's commit, and the `engine/friction_tax.py` docstring (54 cells, 9 industries, 57 states) is fixed here.**"),
    ("6. **Condensed.**",
     " **R2 " + ADD + ": also gate the figure behind `FRICTION_DOLLARS_VISIBLE` and remove the \"roughly 50-75%\" copy. `/api/condensed-complete` shape change needs a live round-trip.**"),
    ("7. **Web types and consumers.**",
     " **R6 " + ADD + ": the share-payload name guard moved to step 5.**"),
]


def apply(text: str) -> str:
    for anchor, new in REPLACEMENTS:
        n = text.count(anchor)
        if n != 1:
            raise SystemExit(f"ANCHOR COUNT {n} (need 1): {anchor[:80]!r}")
        text = text.replace(anchor, new)
    lines = text.split("\n")
    for prefix, new_line in ROW_REPLACEMENTS:
        idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        if len(idx) != 1:
            raise SystemExit(f"ROW COUNT {len(idx)} (need 1): {prefix!r}")
        lines[idx[0]] = new_line
    for prefix, extra in LINE_APPENDS:
        idx = [i for i, l in enumerate(lines) if l.startswith(prefix)]
        if len(idx) != 1:
            raise SystemExit(f"LINE COUNT {len(idx)} (need 1): {prefix!r}")
        lines[idx[0]] = lines[idx[0]] + extra
    text = "\n".join(lines).rstrip("\n") + "\n"
    return text + ADDENDUM


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    raw = SPEC.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    text = raw.replace("\r\n", "\n")
    if "## Phase 0 corrections and rulings" in text:
        raise SystemExit("addendum already present, refusing to apply twice")
    new = apply(text)
    print(f"spec: {len(text.splitlines())} -> {len(new.splitlines())} lines, "
          f"{len(REPLACEMENTS)} inline, {len(ROW_REPLACEMENTS)} rows, {len(LINE_APPENDS)} step annotations, newline={'CRLF' if crlf else 'LF'}")
    if mode == "--write":
        out = new.replace("\n", "\r\n") if crlf else new
        SPEC.write_bytes(out.encode("utf-8"))
        print("WROTE", SPEC)
    else:
        print("DRY RUN, nothing written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
