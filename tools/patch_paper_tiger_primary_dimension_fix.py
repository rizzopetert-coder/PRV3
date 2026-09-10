"""
engine/data/states.py: correct the_paper_tiger's primary_dimension
from "Aptitude" to "Authority".

Confirmed bug, not theoretical: primary_dimension drives which
dimension's answer options get maximized in
tools/calibration_runner.py's best_option_for_state() and
_build_synthetic_vector() (both key off profile.primary_dimension via
_DIM_TO_LIABILITY_FIELD). the_paper_tiger's real dimensional_vector
(Phase 5 re-authoring, 2026-08-25) is authority_liability=0.35
dominant, but primary_dimension was never updated alongside it --
still reads the pre-re-authoring "Aptitude" value.

Traced concretely against the_paper_tiger's real wired questions
(Q05/Q06/Q10/Q12/SEVER-21/Q36/Q39): with the buggy Aptitude field,
Q06 picks option D (authority_liability=0.00) instead of the correct
authority-maximizing option A/B (authority_liability=0.60) -- a lost
0.60 of authority signal. Q36 picks option E, which carries
authority_liability=-0.40 (actively negative), instead of the correct
neutral pick (authority_liability=0.00) -- an active penalty, not
just a missed gain. Net: 1.00 of authority_liability signal
the_paper_tiger's own generated answers currently never deliver.

Usage:
    python tools/patch_paper_tiger_primary_dimension_fix.py --dry-run
    python tools/patch_paper_tiger_primary_dimension_fix.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('engine/data/states.py')

OLD = '''_reg(_profile(
    state_id="the_paper_tiger",
    state_name="The Paper Tiger",
    primary_dimension="Aptitude",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Entrenched", sev_max="Entrenched",
    # Renamed from clinical name: Invisible Performance Management (profiles doc #33)
    resolution_family="Development + Roadmap",
))'''

NEW = '''_reg(_profile(
    state_id="the_paper_tiger",
    state_name="The Paper Tiger",
    # Corrected from "Aptitude" (this session): the Phase 5 re-authoring
    # (2026-08-25) already moved dimensional_vector to
    # authority_liability=0.35 dominant, per the real descriptive_prose
    # (documentation/accountability gap, not a skill/resourcing story),
    # but primary_dimension was never updated alongside it. Confirmed
    # via direct trace of tools/calibration_runner.py's
    # best_option_for_state(): the stale "Aptitude" value caused
    # generate_answers() to select aptitude-maximizing answer options
    # for the_paper_tiger's own wired questions instead of
    # authority-maximizing ones -- concretely, Q06 picked an option
    # carrying authority_liability=0.00 instead of the correct
    # authority-maximizing option's 0.60, and Q36 picked an option
    # carrying authority_liability=-0.40 (actively negative) instead of
    # a neutral 0.00 pick.
    primary_dimension="Authority",
    signal_weight="high",
    cluster_id=None,
    liability_axes=["Legal & Compliance", "Governance & Authority", "Financial & Economic"],
    asset_axes=["Governance Discipline", "Accountability Architecture"],
    sev_min="Entrenched", sev_max="Entrenched",
    # Renamed from clinical name: Invisible Performance Management (profiles doc #33)
    resolution_family="Development + Roadmap",
))'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    count = content.count(OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
