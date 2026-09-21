"""
web/app/people-tactics-and-strategy/page.tsx,
web/app/training-and-development/page.tsx,
web/app/executive-advisory/page.tsx: replace each page's placeholder body
paragraph ("Full detail on this page is coming soon.") with Pete's locked
body copy plus a "Take the diagnostic ->" CTA link to /diagnostic.
Eyebrow and H1 untouched -- only the body section and CTA are new.

Markup conventions matched, not invented:
- Multi-paragraph body wrapped in a `space-y-4` div, same pattern
  web/app/about/page.tsx already uses for stacked body paragraphs.
- Each paragraph keeps the placeholder's own
  `font-ui text-sm text-(--slate)` treatment, adding `leading-relaxed`
  (established elsewhere, e.g. ContextOrientation.tsx, for multi-sentence
  body text at this size).
- CTA link uses `underline hover:opacity-90 transition-opacity`, this
  site's established inline-text-link convention (confirmed in both
  components/ServicesPageContent.tsx's "Learn more ->" link and
  web/app/page.tsx's inline links) -- not a new pattern. Colored
  `text-ink` (this page's own v2 token, mirroring how the placeholder's
  `text-(--slate)` already draws from the same --ink/--slate v2 set the
  H1 uses), since ServicesPageContent's oxide-text and app/page.tsx's
  --home-ink both belong to different, page-scoped token systems these
  three pages don't use.

Each file needs one new import (`next/link`) added alongside the
existing `next` Metadata import.

Content is Pete's copy verbatim, character-for-character -- only JSX
entity-escaping applied (&apos; for apostrophes, &amp; for the literal
"&" in "People Tactics & Strategy"), matching this codebase's existing
convention (see web/app/first-call/page.tsx, web/app/engage/page.tsx).
No wording changes. The one em dash in the Training & Development copy
("co-led -- your own leaders") is Pete's own confirmed-intentional text,
left exactly as supplied.

Also updates each file's header comment: the old "full body copy is an
explicit separate follow-up pass" line is now inaccurate since this pass
fills it in. Replaced with a short "shipped, see Section 16" pointer,
Pete's exact requested wording. Rest of each file's header comment
(the page-specific correction note and the route-slug history) is
untouched -- this replaces only the now-stale opening two lines.

Usage:
    python tools/patch_service_landing_body_copy.py --dry-run
    python tools/patch_service_landing_body_copy.py --write
"""
import argparse
import pathlib
import sys

IMPORT_OLD = '''import type { Metadata } from "next";'''
IMPORT_NEW = '''import type { Metadata } from "next";
import Link from "next/link";'''

PTS_HEADER_OLD = '''// Landing page shell (this session). Structure and the sidebar teaser copy
// only -- full body copy is an explicit separate follow-up pass, see
// tools/_mob.txt. Corrects the /about/services-era description'''
PTS_HEADER_NEW = '''// Landing page shell and body copy shipped MOB v4.317 -- see
// tools/_mob.txt Section 16. Corrects the /about/services-era description'''

TD_HEADER_OLD = '''// Landing page shell (this session). Structure and the sidebar teaser copy
// only -- full body copy is an explicit separate follow-up pass, see
// tools/_mob.txt. Corrects the /about/services-era description (the full'''
TD_HEADER_NEW = '''// Landing page shell and body copy shipped MOB v4.317 -- see
// tools/_mob.txt Section 16. Corrects the /about/services-era description (the full'''

EA_HEADER_OLD = '''// Landing page shell (this session). Structure and the sidebar teaser copy
// only -- full body copy is an explicit separate follow-up pass, see
// tools/_mob.txt. Copy here must not assume a visitor already has a'''
EA_HEADER_NEW = '''// Landing page shell and body copy shipped MOB v4.317 -- see
// tools/_mob.txt Section 16. Copy here must not assume a visitor already has a'''

PTS_BODY_OLD = '''        <p className="font-ui text-sm text-(--slate)">
          Full detail on this page is coming soon.
        </p>'''
PTS_BODY_NEW = '''        <div className="space-y-4">
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            People challenges are rarely a simple, single problem to solve.
            A manager who can&apos;t hold a team together is a web of
            nuanced storylines. By the time it escalates to a
            decision-maker&apos;s desk, each of those storylines is a
            compounding problem for the business. The best-case solution
            requires hours of effort, patience, and expertise. That&apos;s
            where we come in.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            We work inside your organization alongside the people who have
            to live with the outcome, building the structural fix rather
            than handing you a slide deck and a bill. This is embedded
            work, not a report. Engagements are scoped to what&apos;s
            actually in front of you, priced by the work required rather
            than a fixed package, with day rates available when the work
            calls for us on-site.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            If you&apos;re not sure whether what you&apos;re facing is a
            People Tactics &amp; Strategy problem or something else,
            that&apos;s what the diagnostic is for. Fifteen minutes tells
            you which of the four conditions applies before you commit to
            any of them.
          </p>
        </div>
        <Link
          href="/diagnostic"
          className="inline-block mt-8 font-ui text-sm font-medium text-ink underline hover:opacity-90 transition-opacity"
        >
          Take the diagnostic →
        </Link>'''

TD_BODY_OLD = '''        <p className="font-ui text-sm text-(--slate)">
          Full detail on this page is coming soon.
        </p>'''
TD_BODY_NEW = '''        <div className="space-y-4">
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            Most training gets bought off a shelf. A leadership workshop
            that fits every company fits none of them particularly well,
            and everyone in the room knows it. Six months later the binder
            is somewhere in a drawer and nothing about how the team
            actually works has changed.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            We build the training around your people first, and choose the
            format second. Sometimes that&apos;s one person getting
            individual coaching through a specific transition. Sometimes
            it&apos;s a group session built around a pattern we&apos;ve
            actually seen in your organization, not a generic curriculum
            with your logo added. Sometimes the strongest version is
            co-led — your own leaders in the room, building the
            capability to run it themselves next time instead of needing
            us again.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            If you&apos;re not sure whether the gap is a training gap or
            something structural underneath it, that&apos;s what the
            diagnostic is for. Fifteen minutes tells you which of the four
            conditions applies before you commit to any of them.
          </p>
        </div>
        <Link
          href="/diagnostic"
          className="inline-block mt-8 font-ui text-sm font-medium text-ink underline hover:opacity-90 transition-opacity"
        >
          Take the diagnostic →
        </Link>'''

EA_BODY_OLD = '''        <p className="font-ui text-sm text-(--slate)">
          Full detail on this page is coming soon.
        </p>'''
EA_BODY_NEW = '''        <div className="space-y-4">
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            The hardest decisions rarely arrive on schedule. A
            restructuring you didn&apos;t see coming, a leader who
            isn&apos;t working out, a call that has to be made this week
            and lived with for years. What you need in that moment
            isn&apos;t a smart outside opinion. It&apos;s someone who
            knows your organization well enough to tell you the truth, not
            just what sounds reasonable to a stranger hearing it cold.
            That kind of judgment isn&apos;t available on demand. It has
            to be built.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            Executive Advisory is how it gets built: an ongoing
            relationship instead of a one-off engagement, so the credible
            perspective is earned and present when you need it. Some
            months that looks like a standing conversation. Some months it
            means coaching a specific leader through a transition. Either
            way, the advice you&apos;re getting has your actual history
            behind it, not a first impression.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            If you&apos;re not sure whether what you need is a standing
            relationship or a one-time engagement, that&apos;s what the
            diagnostic is for. Fifteen minutes tells you which of the four
            conditions applies before you commit to any of them.
          </p>
        </div>
        <Link
          href="/diagnostic"
          className="inline-block mt-8 font-ui text-sm font-medium text-ink underline hover:opacity-90 transition-opacity"
        >
          Take the diagnostic →
        </Link>'''

FILES = [
    (
        pathlib.Path('web/app/people-tactics-and-strategy/page.tsx'),
        [(PTS_HEADER_OLD, PTS_HEADER_NEW), (IMPORT_OLD, IMPORT_NEW), (PTS_BODY_OLD, PTS_BODY_NEW)],
    ),
    (
        pathlib.Path('web/app/training-and-development/page.tsx'),
        [(TD_HEADER_OLD, TD_HEADER_NEW), (IMPORT_OLD, IMPORT_NEW), (TD_BODY_OLD, TD_BODY_NEW)],
    ),
    (
        pathlib.Path('web/app/executive-advisory/page.tsx'),
        [(EA_HEADER_OLD, EA_HEADER_NEW), (IMPORT_OLD, IMPORT_NEW), (EA_BODY_OLD, EA_BODY_NEW)],
    ),
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
                print(f'Anchor:\n{old[:200]}', file=sys.stderr)
                sys.exit(1)
            new_content = new_content.replace(old, new, 1)
        results.append((path, content, new_content))

    if args.dry_run:
        print('DRY RUN -- all anchors found exactly once in all 3 files, replacements would apply cleanly.')
        for path, old_content, new_content in results:
            print(f'{path}: old length {len(old_content)}, new length {len(new_content)}, delta {len(new_content) - len(old_content)}')
    else:
        for path, old_content, new_content in results:
            path.write_text(new_content, encoding='utf-8')
            print(f'WRITE complete: {path} (delta {len(new_content) - len(old_content)})')


if __name__ == '__main__':
    main()
