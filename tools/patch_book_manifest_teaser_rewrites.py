"""
web/lib/book-manifest.ts -- apply Pete's 4 teaser rewrites to the correct
source (the manifest's `teaser` fields, not the /book piece .md bodies --
confirmed via git history + live grep two turns back that the Aug 30
corpus-wide em-dash pass never touched this file, only the .md bodies).

Four targets, exact OLD/NEW pairs as specified:

1. FTA-32 the-unreported-hazard (line ~956): em-dash pair -> two sentences,
   no dash. "this organization" -> "the organization" per Pete's explicit
   note that the change is intentional, not a typo to preserve.
2. FTA-30 the-unsolved-problem (line ~930): em-dash -> colon, otherwise
   unchanged.
3. LIB-052 what-not-to-document (line ~1243): em-dash-set-off list ->
   "(such as X, Y, and Z)" parenthetical, per CLAUDE.md's locked style
   rule. This is the ONE teaser field, rendered in three places (/book,
   /book/memo/what-not-to-document, /book/state/paper-shield via
   relatedSlug) -- confirmed this is a single shared field, not a
   duplicate copy, by direct read of both LIB-052 (line 1243) and
   FTA-45 paper-shield's own teaser (line 1125, "The policies are
   current, the training is documented, the forms are signed. None of
   it describes what actually happens here." -- a completely different,
   shorter teaser with no trace of the target phrase). Only line 1243
   needs editing.
4. FTA-29 the-paper-tiger (line ~917): em-dash-set-off list -> two
   sentences, with a true em-dash character (not "--") before "though
   not on paper" per Pete's explicit instruction.

FTA-?? symptoms-states-and-why-the-distinction-matters: no manifest edit,
Pete rejected that rewrite -- left untouched, not included below.

Usage:
    python tools/patch_book_manifest_teaser_rewrites.py --dry-run
    python tools/patch_book_manifest_teaser_rewrites.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/lib/book-manifest.ts')

ANCHORS = [
    (
        "There's a safety concern in this organization right now — physical, psychological, operational.",
        "There's a safety concern in the organization right now. It could be physical safety, psychological safety, or operational safety.",
    ),
    (
        "It went through the right process — investigated, addressed, formally closed.",
        "It went through the right process: investigated, addressed, formally closed.",
    ),
    (
        "Most organizations document defensively and starve the documentation that actually protects people — the performance conversation, the commitment, the disagreement.",
        "Most organizations document defensively and starve the documentation that actually protects people (such as the performance conversation, the commitment, and the disagreement).",
    ),
    (
        "The conversations have happened more than once — in one-on-ones, in hallway asides, in performance reviews that somehow, every cycle, come out fine.",
        "The conversations have happened more than once. One-on-one conversations, hallway asides, and even performance reviews — though not on paper.",
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
            print(f'Anchor:\n{old[:200]}', file=sys.stderr)
            sys.exit(1)
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print('DRY RUN -- all 4 anchors found exactly once, replacements would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
        print()
        for old, new in ANCHORS:
            print(f'OLD: {old}')
            print(f'NEW: {new}')
            print()
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
