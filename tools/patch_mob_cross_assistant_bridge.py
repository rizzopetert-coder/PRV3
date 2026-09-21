"""
tools/_mob.txt: add a new subsection documenting the cross-assistant
operational bridge established 2026-09-21 (Gemini now maintains two
Google Docs journals -- the Practice Journal and the Home Journal --
and monitors inbound prospect leads, beyond its existing audit/propose
role on structural decisions).

Placement: end of Section 12 (Session Continuity -- Mem0), as its own
"## Cross-assistant operational bridge" subsection, inserted after the
existing "## Former MemPalace configuration" subsection and before
Section 12's closing rule / Section 13's "Current Workstream" heading.
Chosen over Section 13a (Decision Register) or a new top-level section
because this is operational/tooling infrastructure (what Gemini has
access to and maintains), the same category as Section 12's existing
content (what Mem0 is, what MemPalace was), not a scoped decision with
a status/blocker/check-in shape.

Anchor found by substring position, not a hand-typed literal spanning
the boundary -- the surrounding lines in this file carry inconsistent
backslash-escaping artifacts from past automated patches (a lone
backslash before a rule or heading marker), so locating by known-clean
substrings on either side and slicing between them avoids silently
mismatching or reproducing that escaping.

Wording change from Pete's first draft of the bullet text: the one
`--` placeholder (first bullet) became a colon, per the standing
no-em-dash-placeholder rule (CLAUDE.md Standing Rules) -- this is
internal MOB documentation prose, not externally-authored locked copy,
so the standing style rule applies rather than being flagged-and-
preserved the way locked marketing copy was in an earlier session.

Fourth bullet (Practice Journal taxonomy error) revised a second time
per Pete's correction: the original draft framed the fix as
"correction in progress," which went stale after Pete independently
verified the live document directly and confirmed the fix, the
source-of-truth rule, and the MOB/Journal demarcation were already
live -- not pending. Replaced with Pete's supplied "corrected, verified
directly" framing verbatim, including the newly-noted residual (the
Journal's Intake Protocols line still says "five engagement tiers").
No `--` placeholders in this replacement text -- used as supplied.

Usage:
    python tools/patch_mob_cross_assistant_bridge.py --dry-run
    python tools/patch_mob_cross_assistant_bridge.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/_mob.txt')

ANCHOR_A = '| **Diary** | Session diary: write at close, read at open. Agent name: claude-code. |\n'
ANCHOR_B_SUBSTRING = '# 13. Current Workstream'

NEW_SUBSECTION = '''
---

## Cross-assistant operational bridge (2026-09-21)

- **Principal Resolution — Practice Journal** (Google Docs, Gemini-maintained): day-to-day practice pulse, client pipeline status, inbound triage state. NOT a technical source of truth: service names, pricing, and architecture are defined in the MOB/engine and referenced there, never redefined there.
- **The Home Journal** (Google Docs, Gemini-maintained): household/family operational log, out of PRV3 scope entirely, noted here only because Gemini now holds both.
- **Gemini's role expanded 2026-09-21, Pete's explicit authorization**: beyond audit/propose on structural decisions, Gemini now monitors inbound prospect leads and maintains both journals as a persistent operational assistant.
- **Practice Journal taxonomy error, corrected**: initially pulled a stale/incorrect 5-tier service taxonomy on creation (Stability Support, Executive Counsel, The Intervention, The Roadmap, Development) that did not match the confirmed 4-service set (People Tactics & Strategy, Training & Development, First Call, Executive Advisory). Corrected same-day on the Gemini side; verified directly against the live document, not just reported. One residual noted separately for cleanup: the Journal's Intake Protocols line still referenced "five engagement tiers" as of the fix.
'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    count_a = content.count(ANCHOR_A)
    if count_a != 1:
        print(f'ERROR: ANCHOR_A found {count_a} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    count_b = content.count(ANCHOR_B_SUBSTRING)
    if count_b != 1:
        print(f'ERROR: ANCHOR_B_SUBSTRING found {count_b} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    idx_after_a = content.index(ANCHOR_A) + len(ANCHOR_A)
    idx_b_substring = content.index(ANCHOR_B_SUBSTRING)
    idx_b_line_start = content.rfind('\n', 0, idx_b_substring) + 1

    if idx_b_line_start <= idx_after_a:
        print('ERROR: ANCHOR_B line start is not after ANCHOR_A -- unexpected file layout.', file=sys.stderr)
        sys.exit(1)

    new_content = content[:idx_after_a] + NEW_SUBSECTION + content[idx_after_a:idx_b_line_start] + content[idx_b_line_start:]

    if args.dry_run:
        print('DRY RUN -- both anchors found exactly once, insertion would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
