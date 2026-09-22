"""
web/components/{StoryPageContent,MethodPageContent,ServicesPageContent}.tsx:
revisit the deliberate "eyebrow labels stay neutral gray" decision now
that the real AA-failure count is known, per Pete's explicit
instruction this pass -- not a silent reversal, and not "just make it
high contrast."

Before/after visual reasoning, not just ratio numbers:

CURRENT (text-gray-400, #99A1AF): a light, cool, faintly blue-gray.
Genuinely subtle -- reads as "barely there" against the paper/field
backgrounds it sits on, which is exactly why it fails AA (2.34-2.6:1
against these pages' real bg-background). The low-emphasis INTENT
succeeded; the specific color chosen to achieve it didn't clear
contrast.

PROPOSED (text-(--slate), the v2 token, not text-oxide-text): per
theme, #5C6B66 (Warm, a muted sage-green-gray), #8FA39C (Dark, a soft
blue-green), #6E7276 (Neutral, a neutral warm gray). Darker than
gray-400 -- has to be, to clear 4.5:1 -- but still a desaturated,
muted tone, not a bold color. Deliberately NOT text-oxide-text (used
elsewhere in this same pass for book/toc's body copy): oxide is this
design system's general ACCENT color (warm rust-brown in Warm/Dark,
blue in Neutral) -- more attention-grabbing, not more recessive, and
would read as promoting these labels rather than keeping them quiet.
--slate is already the established sitewide "present but backgrounded"
role -- NavBar's nav links, ServiceSidebar's teaser copy, and this
same file family's own filter-adjacent UI all use it for exactly this
"secondary, not primary" quality. Using it here isn't introducing a
new visual language for these labels; it's extending the one role this
design system already has for "quietly secondary text" to the one
remaining spot still using a raw, non-reactive Tailwind gray instead.

Verified live via actual axe-core measurement (not hand-calculated
ratios) against each page's real bg-background, all three themes,
before writing this script: 0 remaining color-contrast violations on
/about/story, /about/method, /about/services after the swap.

Scope: exactly the instances that were previously deliberately left as
gray-400 (StoryPageContent x5, MethodPageContent x2, ServicesPageContent
x1) -- the same 8 instances flagged, not fixed, in the prior sleuth
pass. Nothing else touched.

Usage:
    python tools/patch_contrast_about_family_eyebrows.py --dry-run
    python tools/patch_contrast_about_family_eyebrows.py --write
"""
import argparse
import pathlib
import sys

STORY_PATH = pathlib.Path('web/components/StoryPageContent.tsx')
METHOD_PATH = pathlib.Path('web/components/MethodPageContent.tsx')
SERVICES_PATH = pathlib.Path('web/components/ServicesPageContent.tsx')

STORY_ANCHORS = [
    ('<p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">The Work</p>',
     '<p className="font-ui text-xs tracking-widest uppercase text-(--slate) mb-2">The Work</p>'),
    ('<p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">The Practice</p>',
     '<p className="font-ui text-xs tracking-widest uppercase text-(--slate) mb-2">The Practice</p>'),
    ('<p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">The Method</p>',
     '<p className="font-ui text-xs tracking-widest uppercase text-(--slate) mb-2">The Method</p>'),
    ('<p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">The Relationship</p>',
     '<p className="font-ui text-xs tracking-widest uppercase text-(--slate) mb-2">The Relationship</p>'),
    ('<p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">The Standard</p>',
     '<p className="font-ui text-xs tracking-widest uppercase text-(--slate) mb-2">The Standard</p>'),
]

METHOD_ANCHORS = [
    ('<p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">The Evidence</p>',
     '<p className="font-ui text-xs tracking-widest uppercase text-(--slate) mb-2">The Evidence</p>'),
    ('<p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">What This Isn&apos;t</p>',
     '<p className="font-ui text-xs tracking-widest uppercase text-(--slate) mb-2">What This Isn&apos;t</p>'),
]

SERVICES_ANCHORS = [
    ('<p className="font-ui text-sm text-gray-400 leading-relaxed mt-12">',
     '<p className="font-ui text-sm text-(--slate) leading-relaxed mt-12">'),
]

FILES = [
    (STORY_PATH, STORY_ANCHORS),
    (METHOD_PATH, METHOD_ANCHORS),
    (SERVICES_PATH, SERVICES_ANCHORS),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    results = []
    for path, anchors in FILES:
        content = path.read_text(encoding='utf-8')
        new_content = content
        for old, new in anchors:
            count = new_content.count(old)
            if count != 1:
                print(f'ERROR: {path}: anchor found {count} times, expected exactly 1.', file=sys.stderr)
                print(f'Anchor:\n{old[:150]}', file=sys.stderr)
                sys.exit(1)
            new_content = new_content.replace(old, new, 1)
        results.append((path, content, new_content))

    if args.dry_run:
        print('DRY RUN -- all anchors found exactly once across all 3 files, replacements would apply cleanly.')
        for path, old_content, new_content in results:
            print(f'{path}: old length {len(old_content)}, new length {len(new_content)}, delta {len(new_content) - len(old_content)}')
    else:
        for path, old_content, new_content in results:
            path.write_text(new_content, encoding='utf-8')
            print(f'WRITE complete: {path} (delta {len(new_content) - len(old_content)})')


if __name__ == '__main__':
    main()
