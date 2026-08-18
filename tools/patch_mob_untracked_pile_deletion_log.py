"""
MOB update -- log the irreversible deletion of 76 untracked historical-pile
files as a Decision Register row (Section 13a), per the Tier 4
irreversible-action standard (Workflow Governance Four-Tier Model): no git
history exists to recover deleted untracked files, so this gets its own
record even though it's cleanup, not a public-facing change.

Also commits Tasks 1/2 from this same session to the record: the
service-expectations-page-draft.md mojibake fix and the .gitignore addition
(.mcp.json/entities.json/mempalace.yaml), both already committed and pushed
(e9dd69b, b44181c) ahead of this MOB write.

Re-verified fresh before writing: MOB header confirmed v4.184 (line 9),
CLAUDE.md cross-reference confirmed v4.184 (line 183), Section 13a's last row
confirmed as the Section 16 logging-gap row added last session (line 1389).

Usage:
    python patch_mob_untracked_pile_deletion_log.py --dry-run
    python patch_mob_untracked_pile_deletion_log.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_PATH = Path("CLAUDE.md")

DELETION_LOG_ROW = (
    '| Untracked historical-pile deletion, 76 files -- CLOSED, irreversible action logged | 4 '
    '(irreversible -- no git history exists for untracked files, so this cannot be undone by '
    'revert) | **Executed, this session, on Pete\'s explicit two-round-reviewed confirmation.** '
    '| N/A -- action complete | Full inventory ran across two prior sessions before any deletion: '
    'a 165-file untracked pile was bucketed into scratch/patch-script residue (verified landed via '
    'an AST-based content-match checker plus manual spot-checks, all confirmed applied except the '
    'one known exception, tools/patch_severity_follow_on_state_scoping.py, deliberately preserved '
    'investigation scaffolding for the still-open severity follow-on gate item), 6 specifically '
    'flagged files (resolved individually -- see the mojibake and .gitignore rows/commits this '
    'session), and a 94-file cluster sharing one exact mtime (2026-07-22 21:33), confirmed via '
    'forensic re-derivation to be a single bulk filesystem event (not per-session authorship -- '
    'file content spans Session pre-1 through Session 69) matching the "~94-entry pre-existing '
    'untracked file pile" first logged 2026-07-23. Cluster count dropped to 91 once .mcp.json/'
    'entities.json/mempalace.yaml were gitignored (no longer untracked). Before deletion, cross-'
    'referenced all 91 against tracked source for citations by name -- found 15 cited as historical-'
    'provenance comments in live engine/research files (not runtime dependencies, confirmed no code '
    'actually reads these docx/prompt files): documents/PRV3-Principal-Brief.docx, PRV3_Frameworks.'
    'docx, PRV3_Output_Synthesis_Prompts_v1.0.docx, PRV3_Question_Signal_Map.docx, PRV3_Resolution_'
    'Families_Copy_v3.0.docx, PRV3_Scoring_Architecture_Spec_v1.docx, PRV3_Signal_Map.docx, PRV3_'
    'State_Taxonomy_Profiles.docx, prompts/state_count_resolved.md, state_removal_final.md, state_'
    'removal_v3.md, tools/gemini_prompts/, tools/gemini_responses/, tools/qsm_extracted.txt, tools/'
    'qualitative_review.py -- all 15 held back, untouched, pending a future deliberate pass to '
    'update their citing comments before any removal. **Deleted: the remaining 76** (91 minus the '
    '15 held back) -- superseded pre-project-history briefs (.claude/claude_code_brief.md and its '
    'prompts/ duplicate, referencing "45 states" and MOB v1_2, predating the current 58-state/'
    'v4.184-era project entirely), old MOB version snapshots (documents/PRV3_MOB_v1.3/1.8/2.8.md, '
    'all superseded by tools/_mob.txt), stale documents/*.xlsx/*.html, and ~65 one-off patch/diag/'
    'trace/phase2 scripts and their output reports, all independently confirmed landed before '
    'deletion. Verified post-deletion via git status: zero tracked files touched, all 76 confirmed '
    'gone, all 15 held-back files confirmed still present. Untracked pile reconciled at 86 remaining '
    '(71-file living pile, unchanged and out of scope this pass, plus the 15 held-back files, zero '
    'overlap between the two sets) -- corrects an informal "roughly 74" estimate floated before the '
    'count was actually re-derived. | This session (Claude Code), 2026-08-18 | Closed, no further '
    'check-in needed on the 76 deleted. The 15 held-back files are their own future consideration -- '
    'not scheduled, Pete\'s call on when to update their citing comments and revisit removal. |\n'
)

REPLACEMENTS = [
    (
        CLAUDE_PATH,
        "CLAUDE.md MOB version cross-reference",
        "| MOB version | v4.184 |",
        "| MOB version | v4.185 |",
    ),
    (
        MOB_PATH,
        "append deletion-log row at end of Section 13a",
        "Pete's call whether a fuller Section 16 backfill is worth the effort versus leaving it as a "
        "known, bounded gap -- no forcing deadline, re-raise if a future session needs the missing "
        "narrative context. |\n",
        "Pete's call whether a fuller Section 16 backfill is worth the effort versus leaving it as a "
        "known, bounded gap -- no forcing deadline, re-raise if a future session needs the missing "
        "narrative context. |\n" + DELETION_LOG_ROW,
    ),
]


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts = {}
    for path, _label, _old, _new in REPLACEMENTS:
        if path not in file_texts:
            file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in REPLACEMENTS:
        text = file_texts[path]
        count = text.count(old)
        if count != 1:
            raise SystemExit(
                f"ABORT [{label}] in {path}: expected exactly 1 match, found {count}"
            )
        file_texts[path] = text.replace(old, new, 1)

    mob_text = file_texts[MOB_PATH]
    mob_lines = mob_text.split("\n")
    header_idx = 8
    assert mob_lines[header_idx].endswith("MOB v4.184"), (
        f"ABORT [header bump]: line 9 does not end with 'MOB v4.184': {mob_lines[header_idx]!r}"
    )
    mob_lines[header_idx] = mob_lines[header_idx].replace("v4.184", "v4.185")
    file_texts[MOB_PATH] = "\n".join(mob_lines)

    for path, new_text in file_texts.items():
        original = path.read_text(encoding="utf-8")
        if args.dry_run:
            print(f"\n{'=' * 80}\nDIFF: {path}\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
            )
            print("".join(diff))
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WROTE: {path}")

    if args.dry_run:
        print("\nDry run complete. No files written. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
