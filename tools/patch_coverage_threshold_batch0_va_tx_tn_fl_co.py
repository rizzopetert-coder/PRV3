"""
engine/friction_tax.py: PARTIAL-state verification workstream, Batch 0.
Flips VA/TX/TN/FL/CO from PARTIAL to CONFIRMED against primary statute
text (independently verified by Pete this session -- direct web search
against official state statute sites, FindLaw, Justia, LegiScan).

Seven anchored edits, applied atomically (all must match or nothing is
written):
  1. StateCoverageThreshold docstring -- documents the new fourth
     damages_cap_treatment value, "state_specific_flat" (a real,
     independent state cap that's a single number, not tiered by
     employer size -- distinct from state_specific_tiers, where real
     tiers exist, and federal_cap_applies, where no independent state
     cap exists at all). Added because VA and FL's real caps are both
     flat, single-number caps, and no existing value described that
     shape without being misleading to a future reader (or the
     "future pricing extension" this field is captured for).
  2. VA entry -- threshold corrected 6 -> 5 (SB 637, eff. 2026-07-01,
     unifies the threshold at 5 across all protected classes and claim
     types, repealing the prior 5-20-employee age-only carve-out
     entirely). damages_cap_treatment corrected state_specific_tiers ->
     state_specific_flat (flat $350,000 cap, Va. Code §8.01-38.1, not
     tiered -- the old value was equally wrong for VA as for FL, just
     not flagged until this batch's cross-check).
  3. TX entry -- threshold and damages_cap_treatment confirmed
     accurate as-is (real tiers, Tex. Lab. Code §21.2585(d)); citation
     stripped of the secondary-source reference.
  4. TN entry -- same, confirmed accurate (real tiers, T.C.A.
     §4-21-313(a)); citation stripped of the "(secondary source)"
     qualifier.
  5. FL entry -- damages_cap_treatment corrected state_specific_tiers
     -> state_specific_flat (flat $100,000 cap, Fla. Stat. §760.11(5),
     not tiered).
  6. CO entry -- threshold and damages_cap_treatment confirmed
     accurate as-is (real tiers: $10,000 at 1-4 employees, $25,000 at
     5-14, federal Title VII tiers apply at 15+, C.R.S.
     §24-34-405(3)(d)(I) and (II)(A)/(II)(B)); citation stripped of
     the secondary-source reference.
  7. CONFIRMED-count assertion -- 7 -> 12, state list extended. Without
     this, the module fails to import the moment a sixth PARTIAL entry
     flips to CONFIRMED, breaking every test in the suite, not just
     friction_tax's own.

Quick cross-check performed before writing this patch (not a full
re-audit, scoped exactly as instructed): TX/TN/CO's own entries and
all 7 existing CONFIRMED entries (CA/NY/MA/IL/WA/AK/WV) checked for
the same state_specific_flat-mislabeled-as-something-else pattern.
None found -- TX/TN/CO are all genuinely tiered as documented; IL's
federal_cap_applies is a different, already-flagged imperfect fit (IHRA
allows uncapped compensatory but zero punitive damages, not a flat-cap
situation); AK/WV's federal_cap_applies is honestly marked unverified
this session, not a confirmed mislabeling. Nothing else in this batch's
scope needs correcting under the new fourth value.

Usage:
    python tools/patch_coverage_threshold_batch0_va_tx_tn_fl_co.py --dry-run
    python tools/patch_coverage_threshold_batch0_va_tx_tn_fl_co.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

EDIT_1_OLD = '''    damages_cap_treatment: "uncapped" | "state_specific_tiers" |
                      "federal_cap_applies". Captured for a future pricing
                      extension (adjusting Cluster 1/2/4b's dollar ceiling
                      by state) -- NOT yet consumed by resolve_coverage_gate()
                      or the Cluster 1/2/4b integration below, which only
                      gates applicability, not dollar amount. See the design
                      doc's "Next steps."'''

EDIT_1_NEW = '''    damages_cap_treatment: "uncapped" | "state_specific_tiers" |
                      "state_specific_flat" | "federal_cap_applies".
                      "uncapped": no damages cap at all. "state_specific_
                      tiers": the state has its own independent statutory
                      cap that scales in real tiers by employer size (e.g.
                      TX, TN, CO -- distinct dollar figures at distinct
                      headcount bands). "state_specific_flat": the state
                      has its own independent statutory cap, but it's a
                      single number regardless of employer size (e.g. VA,
                      FL -- not tiered, and not deferring to federal).
                      "federal_cap_applies": no independent state cap
                      exists at all, so the federal Title VII tiered
                      schedule fills the gap by default. Captured for a
                      future pricing extension (adjusting Cluster 1/2/4b's
                      dollar ceiling by state) -- NOT yet consumed by
                      resolve_coverage_gate() or the Cluster 1/2/4b
                      integration below, which only gates applicability,
                      not dollar amount. See the design doc's "Next steps."'''

EDIT_2_OLD = '''    "VA": StateCoverageThreshold(
        # Source flags this row itself as "nuanced/conflicting": 6+ for most
        # discrimination, 5+ for unlawful-discharge claims specifically.
        # General figure (6) used here.
        thresholds={"general": 6},
        damages_cap_treatment="state_specific_tiers",  # punitive subject to Virginia's general $350,000 cap
        confidence="PARTIAL",
        citation="Virginia Human Rights Act, as amended by the Virginia Values Act 2020, Va. Code §2.2-3905. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_2_NEW = '''    "VA": StateCoverageThreshold(
        thresholds={"general": 5},
        damages_cap_treatment="state_specific_flat",  # flat $350,000 punitive cap, Va. Code §8.01-38.1 (confirmed unchanged)
        confidence="CONFIRMED",
        citation="Va. Code §2.2-3905, as amended by SB 637 (Va. Acts ch. 950, 2026), eff. July 1, 2026 -- Virginia Human Rights Act employer threshold now 5, applying uniformly across all protected classes and claim types; the prior 5-20-employee age-discrimination-only carve-out is repealed entirely, not just the general threshold.",
    ),'''

EDIT_3_OLD = '''    "TX": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="state_specific_tiers",  # own tiered caps mirroring federal, Tex. Lab. Code §21.2585
        confidence="PARTIAL",
        citation="Texas Labor Code ch. 21 / Texas Commission on Human Rights Act. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_3_NEW = '''    "TX": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="state_specific_tiers",  # $50,000 (<101 employees) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+), Tex. Lab. Code §21.2585(d) -- §21.2585(f) removes this cap entirely for sexual-assault and sex-based-harassment/retaliation claims specifically, not currently modeled by claim type
        confidence="CONFIRMED",
        citation="Texas Labor Code ch. 21 / Texas Commission on Human Rights Act.",
    ),'''

EDIT_4_OLD = '''    "TN": StateCoverageThreshold(
        thresholds={"general": 8},
        damages_cap_treatment="state_specific_tiers",  # caps compensatory/punitive by employer size
        confidence="PARTIAL",
        citation="Tennessee Human Rights Act, T.C.A. §4-21-102 (secondary source). research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_4_NEW = '''    "TN": StateCoverageThreshold(
        thresholds={"general": 8},
        damages_cap_treatment="state_specific_tiers",  # $25,000 (8-14 employees) / $50,000 (15-100) / $100,000 (101-200) / $200,000 (201-500) / $300,000 (500+), T.C.A. §4-21-313(a)
        confidence="CONFIRMED",
        citation="Tennessee Human Rights Act, T.C.A. §4-21-102.",
    ),'''

EDIT_5_OLD = '''    "FL": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="state_specific_tiers",  # punitive capped at $100,000 under FCRA
        confidence="PARTIAL",
        citation="Florida Civil Rights Act, Fla. Stat. §760.10. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_5_NEW = '''    "FL": StateCoverageThreshold(
        thresholds={"general": 15},
        damages_cap_treatment="state_specific_flat",  # flat $100,000 punitive cap, no size-based tiers, Fla. Stat. §760.11(5) (confirmed consistent across a decade of statute versions)
        confidence="CONFIRMED",
        citation="Florida Civil Rights Act, Fla. Stat. §760.10.",
    ),'''

EDIT_6_OLD = '''    "CO": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes / no minimum
        damages_cap_treatment="state_specific_tiers",  # capped by employer size, federal-style shape
        confidence="PARTIAL",
        citation="CADA, C.R.S. §24-34-402; POWR Act (SB 23-172) eff. Aug. 7, 2023. research/jurisdiction-research-headcount.md.",
    ),'''

EDIT_6_NEW = '''    "CO": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes / no minimum
        damages_cap_treatment="state_specific_tiers",  # $10,000 (1-4 employees) / $25,000 (5-14 employees), then federal Title VII tiers apply at 15+, C.R.S. §24-34-405(3)(d)(I) and (II)(A)/(II)(B)
        confidence="CONFIRMED",
        citation="CADA, C.R.S. §24-34-402; POWR Act (SB 23-172) eff. Aug. 7, 2023.",
    ),'''

EDIT_7_OLD = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 7, (
    "Expected exactly 7 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV)"
)'''

EDIT_7_NEW = '''assert sum(1 for v in STATE_COVERAGE_THRESHOLDS.values() if v.confidence == "CONFIRMED") == 12, (
    "Expected exactly 12 CONFIRMED states (CA, NY, MA, IL, WA, AK, WV, VA, TX, TN, FL, CO)"
)'''

EDITS = [
    ('docstring: fourth damages_cap_treatment value', EDIT_1_OLD, EDIT_1_NEW),
    ('VA entry', EDIT_2_OLD, EDIT_2_NEW),
    ('TX entry', EDIT_3_OLD, EDIT_3_NEW),
    ('TN entry', EDIT_4_OLD, EDIT_4_NEW),
    ('FL entry', EDIT_5_OLD, EDIT_5_NEW),
    ('CO entry', EDIT_6_OLD, EDIT_6_NEW),
    ('CONFIRMED-count assertion', EDIT_7_OLD, EDIT_7_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
