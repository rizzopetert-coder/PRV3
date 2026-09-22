"""
tools/_mob.txt: add two flagged-for-later items from tonight's sleuth
work session.

Pete's instruction named a "Flagged for later" section. Confirmed
before writing this script: no section by that exact name exists
anywhere in the file (checked against the complete top-level heading
list, Sections 1-16 -- nothing matches). The closest real match is the
unnamed open-items bucket table inside Section 13 ("Current
Workstream"), which already holds exactly this kind of parked/deferred,
non-urgent item (e.g. the /book navigation Phase 3/4 deferred-scope row
immediately preceding the insertion point here). Placed there, flagged
explicitly rather than guessing at a nonexistent heading or inventing
a new section unasked.

Two new rows, inserted immediately before the table's closing "see
Section 13a" pointer row (kept as the section's final housekeeping
note, unchanged):

1. The 92 pre-existing WCAG AA contrast failures sleuth's full-site
   crawl surfaced (.text-gray-400/.text-gray-500, eyebrow labels on
   /about/* and every /book/memo|case_pattern/* piece) -- confirmed
   unrelated to the ServiceSidebar fix shipped this session, not
   touched.
2. The Training & Development teaser's three-way hardcoded duplication
   (ServiceSidebar.tsx, training-and-development/page.tsx's H1,
   ServicesPageContent.tsx) -- reworded in place this session per
   Pete's explicit instruction to leave the duplication itself
   unconsolidated.

Usage:
    python tools/patch_mob_flagged_for_later_sleuth_findings.py --dry-run
    python tools/patch_mob_flagged_for_later_sleuth_findings.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

ANCHOR = '| Structural/scope decisions (Tier 3) | Tracked in the dedicated Decision Register, Section 13a — not duplicated here. See Section 13a for status, named blockers, and next check-in dates. |\n'

NEW_ROWS = (
    '| sleuth-discovered WCAG AA contrast debt | 92 pre-existing WCAG AA `color-contrast` failures (`.text-gray-400`/`.text-gray-500` text, `.text-xs.tracking-widest.uppercase` eyebrow labels) across `/about/*` and every `/book/memo|case_pattern/*` piece -- discovered by `tools/sleuth`\'s full-site crawl this session, not touched. Confirmed unrelated to the ServiceSidebar teaser contrast fix shipped the same session (different elements, different root cause). The recurring eyebrow-label selector suggests a single shared-component fix, similar in kind to the ServiceSidebar fix, just a different component -- likely candidate for a future pass. |\n'
    '| Training & Development teaser -- hardcoded in 3 places | The "Training built around what your people actually need..." sentence exists as three independently hardcoded copies (`web/components/ServiceSidebar.tsx`, `web/app/training-and-development/page.tsx`\'s H1, `web/components/ServicesPageContent.tsx`) -- all three reworded in place this session (sleuth-flagged coaching-as-noun -> verb-only fix), but the underlying duplication was explicitly left unconsolidated per Pete\'s instruction, not a refactor scope-creep. Worth a single-source refactor if any of the three drifts again. |\n'
)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    count = content.count(ANCHOR)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(ANCHOR, NEW_ROWS + ANCHOR, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found exactly once, insertion would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
