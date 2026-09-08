"""
tools/_mob.txt: add a 5th Priority Queue item to this session's just-
appended Section 16 entry -- pre-existing untracked scratch files
(_salience_pilot_*, gemini_prompts/, gemini_responses/, qsm_extracted.txt,
qualitative_review.py) flagged during closeout but predating this
session and explicitly not CC's to bundle in or decide on unilaterally
(Pete's call, 2026-09-08). Open cleanup question for next session, not
a decided disposition.

Usage:
    python tools/patch_mob_untracked_cleanup_item.py --dry-run
    python tools/patch_mob_untracked_cleanup_item.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

OLD = "4. v2 token migration for the homepage -- unchanged, architectural only.\n"

NEW = (
    "4. v2 token migration for the homepage -- unchanged, architectural only.\n"
    "5. **New: pre-existing untracked scratch files, disposition undecided.**\n"
    "   `git status` at this session's closeout showed a pile of untracked\n"
    "   files predating this session's work -- `tools/_salience_pilot_*`,\n"
    "   `tools/gemini_prompts/`, `tools/gemini_responses/`,\n"
    "   `tools/qsm_extracted.txt`, `tools/qualitative_review.py`. Flagged,\n"
    "   not bundled into this session's commits -- not CC's work to decide\n"
    "   on unilaterally. Open question for next session: track, or clean up.\n"
)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')
    count = content.count(OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
