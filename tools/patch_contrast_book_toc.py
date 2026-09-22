"""
web/app/book/toc/page.tsx: fix real WCAG AA contrast failures on the
page's un-migrated legacy text (h1, intro paragraphs, filter labels,
counter, and the two "terms guide"/"clear filters" trigger buttons).

Root cause, confirmed by reading the file, not assumed from selectors:
this page has two eras of styling coexisting. The per-chip hover/tap
trigger (this file's own comment, line 122-129) was built deliberately
using v3 tokens specifically to avoid "ConstellationField's own
un-migrated bg-white/text-charcoal/text-gray-500 classes" -- but that
same discipline was never applied to this page's OWN h1, intro
paragraphs, filter-section labels, or its two secondary-action buttons,
which still use the same un-migrated static/raw classes as the thing
the newer code explicitly avoided.

Only Dark theme was actually failing for text-charcoal/text-gray-600
(the h1 measured 1.17:1 against Dark's near-black field -- essentially
unreadable; v1 charcoal was never designed to render on anything but a
light background). text-gray-400/text-gray-500 fail in Warm and
Neutral too (2.34-2.6:1), and are presumed to fail in Dark as well
(not independently re-verified per-instance there, but the same raw,
non-theme-reactive Tailwind gray classes with no reason to behave
differently).

Fix: text-charcoal -> text-ink (h1; --ink is this project's primary
text token, verified high-contrast in all three themes by design).
text-gray-600/text-gray-400/text-gray-500 -> text-oxide-text for all
six instances below -- not a new choice, this file already uses
text-oxide-text for equivalent secondary/label text on its own filter
chips (line 557) two lines above the labels being fixed here. Verified
via direct contrast calculation against each theme's own correct field
color before choosing it: 5.42:1 (Warm), 5.93:1 (Dark), 7.23:1
(Neutral) -- comfortable margin in all three, not borderline.

NOT touched, flagged separately: the state-signature badges (line 308,
`text-slate border-slate`, the v1 static blue #4A6B85) -- fixing those
means either changing their color identity (swapping to the
theme-reactive --slate token changes the hue per theme, not just
its darkness) or choosing a darker blue specifically for Dark, a real
design decision, not a mechanical token swap like this fix.

Usage:
    python tools/patch_contrast_book_toc.py --dry-run
    python tools/patch_contrast_book_toc.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/app/book/toc/page.tsx')

ANCHORS = [
    (
        '<h1 className="font-display text-3xl text-charcoal mb-4">All States</h1>',
        '<h1 className="font-display text-3xl text-ink mb-4">All States</h1>',
    ),
    (
        '<p className="font-ui text-base text-gray-600 mb-4">\n        The full set of organizational conditions the diagnostic identifies. Filter by dimension,\n        by signature, or both.\n      </p>',
        '<p className="font-ui text-base text-oxide-text mb-4">\n        The full set of organizational conditions the diagnostic identifies. Filter by dimension,\n        by signature, or both.\n      </p>',
    ),
    (
        '<p className="font-ui text-base text-gray-600 mb-4">{LAYER1_ADDITION}</p>',
        '<p className="font-ui text-base text-oxide-text mb-4">{LAYER1_ADDITION}</p>',
    ),
    (
        '<p className="font-mono text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n            Dimension\n          </p>',
        '<p className="font-mono text-[11px] uppercase tracking-wide text-oxide-text mb-2">\n            Dimension\n          </p>',
    ),
    (
        '<p className="font-mono text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n            Signature\n          </p>',
        '<p className="font-mono text-[11px] uppercase tracking-wide text-oxide-text mb-2">\n            Signature\n          </p>',
    ),
    (
        'className="font-ui text-xs text-gray-500 hover:text-hover-ink underline"',
        'className="font-ui text-xs text-oxide-text hover:text-hover-ink underline"',
    ),
    (
        '<p className="font-ui text-sm text-gray-400 mb-6">',
        '<p className="font-ui text-sm text-oxide-text mb-6">',
    ),
    (
        'className="font-ui text-sm text-gray-500 hover:text-hover-ink transition-colors underline decoration-dotted underline-offset-2"',
        'className="font-ui text-sm text-oxide-text hover:text-hover-ink transition-colors underline decoration-dotted underline-offset-2"',
    ),
    (
        '<p className="font-ui text-sm text-gray-500 mt-8">\n          No conditions match the selected filters.\n        </p>',
        '<p className="font-ui text-sm text-oxide-text mt-8">\n          No conditions match the selected filters.\n        </p>',
    ),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    new_content = content
    for old, new in ANCHORS:
        count = new_content.count(old)
        if count != 1:
            print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
            print(f'Anchor:\n{old[:150]}', file=sys.stderr)
            sys.exit(1)
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print('DRY RUN -- all 9 anchors found exactly once, replacements would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
