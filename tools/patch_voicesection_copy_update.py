"""
web/app/page.tsx: replace VoiceSection's paragraph content with Pete's
final approved copy -- splits the original merged first paragraph into
two (4 paragraphs total), adds an inline link on "deeper conditions"
to the real, published symptoms/states methodology piece, and applies
the hero's existing font-semibold text-(--home-slate) emphasis
treatment to exactly the three named leadership behaviors.

Link styling: checked web/app/about/page.tsx for this site's
established inline-text-link convention (underline + a hover state,
not a bare Link) rather than inventing one. Adapted to this page's own
isolated .home-scope palette and its own hover convention (hover:opacity-90
transition-opacity, already used by the CTA button and WayfindingGrid
cards elsewhere on this exact page) instead of the global --hover-ink
token, which .home-scope deliberately never touches.

One correction applied against the literal copy text supplied: the
raw copy used HTML's `class="..."` on the <em> emphasis spans -- JSX
requires `className`, so that's corrected here, not a content change.

Spacing: preserves the mb-6/mb-4/mb-10 rhythm. Paragraph 1 (the first
half of the original merged paragraph) gets its own new mb-6, since
splitting one paragraph into two now needs a gap between them that
didn't exist before. Paragraph 2 keeps the mb-6 the original merged
paragraph already had. Paragraphs 3 and 4 are unchanged in style
(font-ui/opacity-80, mb-4/mb-10), only their text content changes.

Usage:
    python tools/patch_voicesection_copy_update.py --dry-run
    python tools/patch_voicesection_copy_update.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/app/page.tsx')

OLD = '''      <p className="font-display text-2xl md:text-3xl leading-relaxed text-(--home-ink) mb-6">
        Many of the &quot;people problems&quot; leaders describe are the
        symptoms of deeper conditions that are more challenging to work
        through. Because they&apos;re more challenging, and often require
        leaders to look in the mirror, it is often easier for leaders to
        believe they&apos;re a training or a PIP or a termination away from
        resolving their problems. But workplace performance and behaviors
        are significantly influenced by leadership behaviors: consistency,
        accountability, strong communication, and a fundamental
        understanding of the organization&apos;s values. Consistent
        leadership behaviors result in more consistent employee behaviors,
        and more consistent, more predictable results.
      </p>
      <p className="font-ui text-base leading-relaxed text-(--home-ink) opacity-80 mb-4">
        Clients don&apos;t need another framework or slide deck. They want a
        confidant and advisor with a perspective they know they can trust. A
        partner with a genuine understanding of their business, their
        history, their values, and what they&apos;re actually trying to
        build. And given all that, someone who can filter out the noise and
        give the objective truth.
      </p>
      <p className="font-ui text-base leading-relaxed text-(--home-ink) opacity-80 mb-10">
        I don&apos;t tell you what decision to make. Decide what&apos;s best
        for your business, and give me the marching orders. We&apos;ll help
        you get there.
      </p>'''

NEW = '''      <p className="font-display text-2xl md:text-3xl leading-relaxed text-(--home-ink) mb-6">
        Many of the &quot;people problems&quot; leaders describe are
        symptoms of{" "}
        <Link
          href="/book/methodology/symptoms-states-and-why-the-distinction-matters"
          className="text-(--home-slate) underline hover:opacity-90 transition-opacity"
        >
          deeper conditions
        </Link>{" "}
        that are more challenging to identify and work through. Because
        they&apos;re more challenging, and often require leaders to look in
        the mirror, it is often easier for leaders to believe they&apos;re a
        training, a performance improvement plan, or a termination away from
        resolution.
      </p>
      <p className="font-display text-2xl md:text-3xl leading-relaxed text-(--home-ink) mb-6">
        Workplace performance is significantly influenced by leadership
        behaviors:{" "}
        <em className="not-italic font-semibold text-(--home-slate)">
          consistency
        </em>
        ,{" "}
        <em className="not-italic font-semibold text-(--home-slate)">
          accountability
        </em>
        ,{" "}
        <em className="not-italic font-semibold text-(--home-slate)">
          strong communication
        </em>
        , and a fundamental understanding of the organization&apos;s values.
        Consistent leadership results in more consistent, more predictable
        results for employees and for the organization.
      </p>
      <p className="font-ui text-base leading-relaxed text-(--home-ink) opacity-80 mb-4">
        Clients don&apos;t need another framework or slide deck. They want a
        confidant, an advisor with experience and perspective they can trust.
        A partner with a genuine understanding of their business, their
        history, their values, and what they&apos;re actually trying to
        build. And given all that, someone who can filter out the noise and
        give them objective guidance.
      </p>
      <p className="font-ui text-base leading-relaxed text-(--home-ink) opacity-80 mb-10">
        We don&apos;t tell you what decisions to make. Decide what&apos;s
        best for your business, and we&apos;ll help you get there.
      </p>'''


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
