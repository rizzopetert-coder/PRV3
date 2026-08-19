"""
MOB update -- log the "decision-authority ambiguity" taxonomy gap as its own
Section 13a Decision Register row. Documentation only, no engine code touched.

Surfaced while locking SEVER-03's content mapping
(prompts/severity-result-per-state-redesign-scope.md, Section 8): Q21's option
E doesn't cleanly fit either of Q21's two real state_targets
(decision_paralysis, the_lost_map) -- mapped to the_lost_map as the
best-available fit, explicitly flagged as not confident. This gets its own
Decision Register row so it isn't lost inside a scoping document footnote,
per Pete's explicit instruction this session.

Re-verified fresh before writing: MOB header confirmed v4.187 (line 9),
CLAUDE.md cross-reference confirmed v4.187 (line 183), Section 13a's true
last row confirmed as the stale-git-worktree row (line 1391).

Usage:
    python patch_mob_taxonomy_gap_decision_authority.py --dry-run
    python patch_mob_taxonomy_gap_decision_authority.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_PATH = Path("CLAUDE.md")

TAXONOMY_GAP_ROW = (
    '| Taxonomy gap: "decision-authority ambiguity" has no clean home in the current '
    '58-state taxonomy -- OPEN, flagged for a future taxonomy conversation | 3 | **OPEN. '
    'Not scoped for resolution now. Logged for a future taxonomy conversation, not '
    'actioned this session.** | No existing state cleanly captures decision-authority '
    'ambiguity as distinct from decision speed (`decision_paralysis`) or information-'
    'findability (`the_lost_map`) -- needs either a taxonomy addition or a deliberate call '
    'that one of the two existing states should absorb this case | Surfaced while locking '
    'SEVER-03\'s content mapping (`prompts/severity-result-per-state-redesign-scope.md`, '
    'Section 8). Q21\'s option E ("It\'s unclear who has the authority to decide -- '
    'decisions happen but nobody can say with confidence who was supposed to make them") '
    'was mapped to `the_lost_map` as the best-available fit among Q21\'s only two real '
    '`state_targets` (`decision_paralysis`, `the_lost_map`), but flagged explicitly as not '
    'a confident match. `the_lost_map`\'s own definition (institutional knowledge living in '
    'individual heads, lost when someone leaves) is adjacent to but not the same mechanism '
    'as option E\'s actual content (ambiguity about who currently holds decision authority '
    '-- a live governance-clarity gap, not specifically a knowledge-loss-on-departure '
    'problem). `decision_paralysis` (a speed problem) doesn\'t fit either. Not attempted to '
    'fix here, per explicit scope at the time this was found -- recorded so the SEVER-03/E '
    'mapping isn\'t mistaken for a settled, confident match later, and so this can be picked '
    'up as its own taxonomy conversation whenever Pete wants to open it. | This session '
    '(Claude Code), 2026-08-19 | No forced check-in. Pete\'s call on when to open a taxonomy '
    'conversation -- cross-reference `prompts/severity-result-per-state-redesign-scope.md` '
    'Section 8 (SEVER-03) for the full context. |\n'
)

REPLACEMENTS = [
    (
        CLAUDE_PATH,
        "CLAUDE.md MOB version cross-reference",
        "| MOB version | v4.187 |",
        "| MOB version | v4.188 |",
    ),
    (
        MOB_PATH,
        "append taxonomy-gap row at end of Section 13a",
        "This session (Claude Code), 2026-08-18 | No forced check-in, low priority. Worth a "
        "look next time someone is doing git housekeeping, not urgent. |\n",
        "This session (Claude Code), 2026-08-18 | No forced check-in, low priority. Worth a "
        "look next time someone is doing git housekeeping, not urgent. |\n" + TAXONOMY_GAP_ROW,
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
    assert mob_lines[header_idx].endswith("MOB v4.187"), (
        f"ABORT [header bump]: line 9 does not end with 'MOB v4.187': {mob_lines[header_idx]!r}"
    )
    mob_lines[header_idx] = mob_lines[header_idx].replace("v4.187", "v4.188")
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
