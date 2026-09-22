"""
tools/_mob.txt: document the Cross-Assistant Sync mechanism that
resolved the MOB/Google-Drive mirroring question, and correct a
process discrepancy caught before writing anything else.

CONTEXT, verified fresh this session before writing anything (Cross-
Environment Verification Discipline): the prompt characterized Task 1
(patch-script clarification), Task 2 (Section 13 open-items commit),
and Task 3 (full session closeout -- Section 16 entry, Section 8
JetBrains-Mono correction, MOB v4.320->v4.322, diary write, handoff
file) as still pending, "interrupted" before being reported back on.
Checked directly: all of it is already committed and pushed to
origin/main (commits d75edbf, 91648a8, 19509d7, 6f84dfb), the diary
entry exists (read back directly, topic
"session-closeout-2026-09-22-sleuth-build-contrast-coaching-fixes"),
and prompts/session-handoff-v4.322.md exists on disk. None of that is
redone here -- redoing it would create duplicate/conflicting Section 16
entries. This script only adds the one genuinely new thing: the sync
mechanism itself, which was resolved after that closeout.

Sync mechanism, verified directly, not taken on report alone:
- C:\\Users\\rizzo\\PRV3-MOB-sync.ps1 exists (read directly) -- a plain
  unconditional Copy-Item from tools/_mob.txt to the Drive path on
  every run (no change-detection; the previous git-hook approach's
  "only copy when tools/_mob.txt was touched" logic isn't replicated
  here -- this is simpler by necessity, since it runs fully outside any
  git context).
- A Windows Scheduled Task named "PRV3 MOB sync" is registered and
  Ready (checked via Get-ScheduledTask directly) -- LastResult 0
  (success), NextRunTime exactly 15 minutes after LastRunTime,
  confirming the 15-minute cadence.
- C:\\Users\\rizzo\\My Drive\\Principal Resolution\\PRV3-MOB.md exists
  and matches tools/_mob.txt line-for-line (6665 lines each) with an
  identical tail at the time of this check.
- NOT independently verified: "confirmed by Gemini Spark on the
  receiving end" -- relayed from Pete, not something checkable from
  this environment. Documented as Pete's report, not asserted as this
  session's own confirmation.

Two writes:
1. Section 12's existing "Cross-assistant operational bridge
   (2026-09-21)" subsection -- the closest existing equivalent to a
   "System Role/Architecture" section (checked headings directly
   before choosing this, same discipline as the earlier "Flagged for
   later" non-existent-section check) -- gains a new "Cross-Assistant
   Sync mechanism" bullet block.
2. Section 16 gains a short DATED NOTE (not a second full SESSION
   CLOSEOUT entry, since the real closeout already happened and a
   second one would misrepresent this as new session-level work)
   recording that the git-hook approach was blocked twice (execution,
   then authoring) by Claude Code's own data-exfiltration classifier,
   and the OS-level Scheduled Task is what actually resolved it.

Version bump: v4.322 -> v4.323 (+1) -- the sync mechanism question was
a real, standing open item; this locks in how it actually works, not
just a session-log note.

Usage:
    python tools/patch_mob_cross_assistant_sync_mechanism.py --dry-run
    python tools/patch_mob_cross_assistant_sync_mechanism.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')
CLAUDE_PATH = pathlib.Path('CLAUDE.md')

SECTION12_ANCHOR = 'One residual noted separately for cleanup: the Journal\'s Intake Protocols line still referenced "five engagement tiers" as of the fix.\n'

SECTION12_ADDITION = '''
**Cross-Assistant Sync mechanism (2026-09-22):**
- **Claude (Claude Code / local):** authoritative maintainer of the codebase and of `tools/_mob.txt` itself.
- **Sync mechanism:** an OS-level Windows Scheduled Task ("PRV3 MOB sync"), not a git hook -- a git `post-commit` hook was tried and blocked twice by Claude Code's own data-exfiltration safety classifier (once when attempting the actual copy, once when merely authoring a hook script containing that copy logic -- confirmed both times this was the harness's own guardrail, not a missing path or a technical failure, and per standing instruction no workaround was attempted). The Scheduled Task runs `C:\\Users\\rizzo\\PRV3-MOB-sync.ps1` every 15 minutes, fully outside Claude Code's own execution, copying `tools/_mob.txt` to `C:\\Users\\rizzo\\My Drive\\Principal Resolution\\PRV3-MOB.md` unconditionally (no change-detection -- it overwrites every run, not only on real changes). Verified directly this session: the script's content, the registered task (state Ready, last result 0/success, next run exactly 15 minutes after last), and the destination file (line-for-line identical to `tools/_mob.txt` at time of check).
- **Gemini Spark (cloud):** reads the mirrored MOB from Drive to ground practice operations; distills business-relevant deltas into the Practice Journal with Pete's approval before writing, per the existing protocol above. (Confirmed working on the receiving end per Pete's report -- not independently checkable from this environment.)
- **Pete:** decides.
'''

TAIL_ANCHOR = 'MOB v4.322.\n'

NEW_DATED_NOTE = '''---

## DATED NOTE (2026-09-22) -- Cross-Assistant Sync mechanism resolved,
## git-hook approach confirmed closed

Follow-up to this same date's earlier closeout entry (MOB v4.320 ->
v4.322): the MOB-to-Google-Drive mirror question (open since the prior
session, when direct execution of the copy was blocked by Claude
Code's own data-exfiltration classifier) is now resolved. A
`post-commit` git hook was attempted as the fix -- blocked a second
time, this time at the authoring step (writing a hook script whose
*content* described the copy operation was itself refused, before any
commit or execution). Per standing instruction, no workaround was
attempted at either block -- the intent of the classifier was treated
as the actual boundary, not an obstacle to route around.

Resolved instead via a mechanism fully outside Claude Code's own
execution, as flagged as the necessary fallback when the hook path
closed: a Windows Scheduled Task ("PRV3 MOB sync") running
`C:\\Users\\rizzo\\PRV3-MOB-sync.ps1` on a 15-minute timer, copying
`tools/_mob.txt` to `C:\\Users\\rizzo\\My Drive\\Principal
Resolution\\PRV3-MOB.md` unconditionally. Verified directly this
session -- script content, live Scheduled Task registration and last-
run result, and destination-file content match -- not taken on report
alone. Full mechanism documented in Section 12's "Cross-assistant
operational bridge" subsection, new "Cross-Assistant Sync mechanism"
block.

**Process note, not a criticism, logged for the record:** this
session's opening prompt characterized Section 16's prior closeout
entry (same date, MOB v4.322) as never having been reported back on,
prompting a request to redo Task 1-3. Checked directly before acting:
all three were already committed and pushed (commits d75edbf, 91648a8,
19509d7, 6f84dfb), diary entry present, handoff file present. Not
redone -- would have created duplicate Section 16 entries. Flagged to
Pete directly rather than silently complying with the redo request or
silently ignoring it.

MOB v4.323.
'''

CLAUDE_OLD = '| MOB version | v4.322 |'
CLAUDE_NEW = '| MOB version | v4.323 |'


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    mob_content = MOB_PATH.read_text(encoding='utf-8')

    count_s12 = mob_content.count(SECTION12_ANCHOR)
    if count_s12 != 1:
        print(f'ERROR: SECTION12_ANCHOR found {count_s12} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)

    count_tail = mob_content.count(TAIL_ANCHOR)
    if count_tail != 1:
        print(f'ERROR: TAIL_ANCHOR found {count_tail} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)
    if not mob_content.endswith(TAIL_ANCHOR):
        print('ERROR: TAIL_ANCHOR is not at the true end of the file -- refusing to guess.', file=sys.stderr)
        sys.exit(1)

    new_mob_content = mob_content.replace(SECTION12_ANCHOR, SECTION12_ANCHOR + SECTION12_ADDITION, 1)
    new_mob_content = new_mob_content + '\n' + NEW_DATED_NOTE

    claude_content = CLAUDE_PATH.read_text(encoding='utf-8')
    count_claude = claude_content.count(CLAUDE_OLD)
    if count_claude != 1:
        print(f'ERROR: CLAUDE_OLD found {count_claude} times, expected exactly 1.', file=sys.stderr)
        sys.exit(1)
    new_claude_content = claude_content.replace(CLAUDE_OLD, CLAUDE_NEW, 1)

    if args.dry_run:
        print('DRY RUN -- all anchors found exactly once, both files would write cleanly.')
        print(f'_mob.txt: old length {len(mob_content)}, new length {len(new_mob_content)}, delta {len(new_mob_content) - len(mob_content)}')
        print(f'CLAUDE.md: old length {len(claude_content)}, new length {len(new_claude_content)}, delta {len(new_claude_content) - len(claude_content)}')
    else:
        MOB_PATH.write_text(new_mob_content, encoding='utf-8')
        CLAUDE_PATH.write_text(new_claude_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'_mob.txt: old length {len(mob_content)}, new length {len(new_mob_content)}, delta {len(new_mob_content) - len(mob_content)}')
        print(f'CLAUDE.md: old length {len(claude_content)}, new length {len(new_claude_content)}, delta {len(new_claude_content) - len(claude_content)}')


if __name__ == '__main__':
    main()
