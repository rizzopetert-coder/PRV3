"""
web/components/ServiceSidebar.tsx: move the persistent desktop sidebar
from right to left, give the four service boxes a real visible gap
instead of a hairline, and flip the /diagnostic collapsed trigger to
match the new side.

1. Non-diagnostic <aside> branch: reordered so <aside> renders before
   {children} (was children-then-aside). border-l -> border-r on the
   aside, since it now divides sidebar-from-content on its right edge.

2. Box separator: border-b border-line (an effective 1px hairline) ->
   border-b-8 border-field. Token checked first, not assumed: this
   component already backgrounds the aside itself with bg-field, the
   v2 token that's redefined per-theme in :root/[data-theme="dark"]/
   [data-theme="neutral"] (app/globals.css). --color-paper, the other
   candidate, is a fixed non-theme-reactive value (#F6F3ED) used by
   older-token pages like ServicesPageContent.tsx -- wrong here, it
   would not track Dark/Neutral. border-field matches the aside's own
   background exactly, so the 8px border reads as a real background-
   colored gap, not a highlighted rule. last:border-b-0 kept unchanged.
   Added py-6 (was px-6 only) since the boxes read cramped once the
   gap ate into the flex-1 justify-center vertical rhythm -- first
   pass, Pete may adjust.

3. /diagnostic's collapsed trigger: justify-end -> justify-start,
   absolute right-6 -> absolute left-6, matching the sidebar's new
   side. Purely the alignment/position classes -- the in-flow-not-fixed
   architecture (and the comment block explaining why, referencing the
   AssemblyPanel collision this was built to avoid) is unchanged.

No other changes. Header comment block (lines 7-42) not touched --
its content (suppression rationale, in-flow-trigger rationale, bg-rust
exception) remains accurate regardless of which side the sidebar is on.

Usage:
    python tools/patch_service_sidebar_left_gap.py --dry-run
    python tools/patch_service_sidebar_left_gap.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/components/ServiceSidebar.tsx')

DESKTOP_OLD = '''  return (
    <div className="flex flex-1">
      <div className="flex-1 min-w-0">{children}</div>
      <aside className="hidden md:flex md:flex-col w-72 shrink-0 border-l border-line bg-field sticky top-0 h-screen">
        {SERVICES.map((s) => (
          <Link
            key={s.id}
            href={s.href}
            className={`flex-1 flex flex-col justify-center px-6 border-b border-line last:border-b-0 transition-colors ${
              s.rust ? "bg-rust text-white hover:opacity-90" : "text-(--slate) hover:bg-field-raise hover:text-ink"
            }`}
          >
            <h2 className="font-display text-lg font-semibold mb-2">{s.name}</h2>
            <p className={`font-ui text-sm leading-relaxed mb-3 ${s.rust ? "" : "opacity-80"}`}>
              {s.teaser}
            </p>
            <span className="font-ui text-sm font-medium">{s.cta}</span>
          </Link>
        ))}
      </aside>
    </div>
  );'''

DESKTOP_NEW = '''  return (
    <div className="flex flex-1">
      <aside className="hidden md:flex md:flex-col w-72 shrink-0 border-r border-line bg-field sticky top-0 h-screen">
        {SERVICES.map((s) => (
          <Link
            key={s.id}
            href={s.href}
            className={`flex-1 flex flex-col justify-center px-6 py-6 border-b-8 border-field last:border-b-0 transition-colors ${
              s.rust ? "bg-rust text-white hover:opacity-90" : "text-(--slate) hover:bg-field-raise hover:text-ink"
            }`}
          >
            <h2 className="font-display text-lg font-semibold mb-2">{s.name}</h2>
            <p className={`font-ui text-sm leading-relaxed mb-3 ${s.rust ? "" : "opacity-80"}`}>
              {s.teaser}
            </p>
            <span className="font-ui text-sm font-medium">{s.cta}</span>
          </Link>
        ))}
      </aside>
      <div className="flex-1 min-w-0">{children}</div>
    </div>
  );'''

TRIGGER_ALIGN_OLD = '''          <div className="flex justify-end px-6 py-1.5">'''
TRIGGER_ALIGN_NEW = '''          <div className="flex justify-start px-6 py-1.5">'''

DROPDOWN_POS_OLD = '''            <div className="absolute right-6 top-full bg-field border border-line py-1 min-w-[200px] shadow-sm z-50">'''
DROPDOWN_POS_NEW = '''            <div className="absolute left-6 top-full bg-field border border-line py-1 min-w-[200px] shadow-sm z-50">'''

ANCHORS = [
    (DESKTOP_OLD, DESKTOP_NEW),
    (TRIGGER_ALIGN_OLD, TRIGGER_ALIGN_NEW),
    (DROPDOWN_POS_OLD, DROPDOWN_POS_NEW),
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
            print(f'Anchor:\n{old[:200]}', file=sys.stderr)
            sys.exit(1)
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print('DRY RUN -- all 3 anchors found exactly once, replacements would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
