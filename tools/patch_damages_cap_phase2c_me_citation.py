"""
engine/friction_tax.py: Phase 2c (ME) -- citation comment only, no
engine logic change. Confirmed before writing: ME already resolves
PRICED via the generic curve with is_floor=True automatically (the
same "generic state_specific_tiers fallthrough" AR/DE/TN/TX sit in),
exactly the target state Phase 2a's AR/DE/TN build already
demonstrated needs zero code -- ME is data population into the
already-shipped architecture, not a new mechanism, per
prompts/damages-cap-treatment-phase2-spec.md's Phase 2c scoping.

Two corrections to the PRIOR comment, both confirmed against primary
source (mainelegislature.org) this session, not the prior MOB/comment
phrasing:

1. 5 M.R.S. Sec4613(2)(B)(7) and (8) are two separate remedies, not one
   joint provision -- the prior citation cited them together as
   "(7)-(8)". (7) is civil penal damages (non-employment/<=14-employee
   cases, tiered by violation order). (8) is the real employment tier
   table (15+ employees, tiered by headcount). Split apart in the new
   citation field.
2. The prior comment stated the top employment bracket as "$500,000" --
   that was actually the 201-500 tier's figure; the real top bracket
   (501+) is $1,000,000. The prior verification pass stopped one tier
   short. Corrected here against the full, current (8)(e)(i)-(iv) table.

Two new unmodeled carve-outs added, stated by the statute itself, not
invented -- (8)(f) (42 U.S.C. Sec1981 stacking, itself uncapped) and
(8)(h) (disparate-impact-only claims exempt from the tier caps) --
is_floor=True (already automatic for every state_specific_tiers state)
is the existing caveat mechanism for both, same semantics as TX's own
claim-type carve-out.

Usage:
    python tools/patch_damages_cap_phase2c_me_citation.py --dry-run
    python tools/patch_damages_cap_phase2c_me_citation.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/friction_tax.py')

ME_ENTRY_OLD = '''    "ME": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        # <15 employees: "civil penal damages" only (not traditional
        # compensatory/punitive), tiered $20,000 (1st order) / $50,000
        # (2nd order) / $100,000 (3rd+ order). 15+ employees: traditional
        # compensatory and punitive damages, tiered up to $500,000 at the
        # top employer-size bracket -- exceeds Title VII's $300,000
        # federal maximum. Only the <15 tiers and the $500,000 ceiling
        # were independently verified this session -- intermediate
        # 15+-employee tier breakpoints were NOT verified; confirm
        # against 5 M.R.S. §4613(2)(B)(7)-(8) directly before relying on
        # them for anything beyond the applicability gate this field
        # doesn't yet drive.
        damages_cap_treatment="state_specific_tiers",
        confidence="CONFIRMED",
        citation="Maine Human Rights Act, 5 M.R.S. §4572; §4613(2)(B)(7)-(8).",
    ),'''

ME_ENTRY_NEW = '''    "ME": StateCoverageThreshold(
        thresholds={"general": 1},  # all sizes
        # 5 M.R.S. Sec4613(2)(B)(7) and (8) are TWO SEPARATE remedies,
        # not one joint provision -- confirmed directly against
        # mainelegislature.org this session, current through Oct. 1,
        # 2025 (last amended PL 2023, c. 263, Sec1). Corrects this
        # entry's own prior citation, which cited them jointly as
        # "(7)-(8)" -- that conflation is fixed in the citation field
        # below.
        #
        # (7): "civil penal damages" (not traditional compensatory/
        # punitive) for non-employment cases, or employment cases with
        # <=14 employees, tiered by VIOLATION ORDER, not headcount --
        # $20,000 (1st order) / $50,000 (2nd order) / $100,000 (3rd+
        # order).
        #
        # (8)(e)(i)-(iv): the real employment tier table, for
        # "intentional employment discrimination with respondents who
        # have more than 14 employees" (15+), tiered by HEADCOUNT --
        # $100,000 (15-100) / $300,000 (101-200) / $500,000 (201-500) /
        # $1,000,000 (501+). Corrects this entry's own prior comment,
        # which stated the top bracket as "$500,000" -- that was the
        # 201-500 tier's own figure, not the true 501+ ceiling; the
        # prior verification pass stopped one tier short.
        #
        # Two unmodeled carve-outs, stated by the statute itself, not
        # invented -- is_floor=True (already automatic for every
        # state_specific_tiers state) is the existing caveat mechanism
        # for both, same "may understate the real answer" semantics
        # TX's own is_floor=True already carries for its claim-type
        # carve-out:
        #   (8)(f): this cap does NOT limit recovery under 42 U.S.C.
        #   Sec1981, which has no statutory cap of its own -- real
        #   potential for a complaining party's actual recovery to
        #   exceed this table's figure via stacking.
        #   (8)(h): the tier caps do not apply to claims unlawful
        #   solely due to disparate impact.
        damages_cap_treatment="state_specific_tiers",
        confidence="CONFIRMED",
        citation="Maine Human Rights Act, 5 M.R.S. §4572; §4613(2)(B)(7) (civil penal damages, non-employment/<=14-employee cases, a distinct provision); §4613(2)(B)(8) (employment tier table, 15+ employees).",
    ),'''

EDITS = [
    ('ME entry -- verified tier table, split citation, two new carve-outs', ME_ENTRY_OLD, ME_ENTRY_NEW),
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
