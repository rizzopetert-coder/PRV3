"""
MOB update -- Section 13a's "Severity follow-on state scoping" row rewritten
to reflect current state: scoping complete, doc committed across two
commits this session, ready for Gemini submission (not yet submitted).
Documentation only, no engine code touched.

Re-verified fresh before writing: MOB header confirmed v4.188 (line 9),
CLAUDE.md cross-reference confirmed v4.188 (line 183), the row's current
exact text confirmed via direct read immediately before this script was
written.

Usage:
    python patch_mob_severity_scoping_complete.py --dry-run
    python patch_mob_severity_scoping_complete.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_PATH = Path("CLAUDE.md")

OLD_ROW = Path(
    "C:/Users/rizzo/AppData/Local/Temp/claude/c--Users-rizzo-PRV3/"
    "9354bfe3-2f47-478f-ac95-6d59ebb8dbc1/scratchpad/sever_row_current.txt"
).read_text(encoding="utf-8")

NEW_ROW = (
    '| Severity follow-on state scoping -- SCOPING COMPLETE, doc committed, ready for '
    'Gemini submission (not yet submitted) | 3 | **SCOPING COMPLETE.** Full architecture '
    'reframe, 19/32 SEVER-ID mapping, recalibration-scope estimate, and recalibration '
    'sequencing (LOCKED: Bundle) all done and committed. Ready for Gemini architecture '
    'review -- submission itself is a separate, explicit action, not yet taken. | None '
    'remaining for scoping. Gemini submission and Pete\'s go-ahead on the actual build are '
    'the only steps left before code changes begin. | Full record: '
    'prompts/severity-result-per-state-redesign-scope.md (533 lines), committed across '
    'two commits this session (a57b5be: doc added as-is; 942a998: recalibration '
    'sequencing locked to Bundle, status marked unconditionally Gemini-ready), building '
    'on the reframe/taxonomy-gap work committed last session (362aaaf, 7d90b57, 095a2d2). '
    'Condensed summary of what the doc contains, not a substitute for reading it: (1) the '
    'architecture problem -- SeverityResult has no per-state dimension, confirmed via the '
    'ATT-UT-01 reproduction (severity credited to a rank-58/58 state never promoted it '
    'into output, but the 7 states that did qualify all received the same inflated tier '
    'the input was never about); (2) proposed fix -- SeverityResult gains state_severity: '
    'dict[state_id, tier], Emerging fallback for unmapped states; (3) confirmed hard '
    'prerequisite -- split-by-option attribution (SEVER-03, SEVER-07 both need it), '
    'requiring a new triggering_option_id field on SeverityInput plus real wire-contract '
    'plumbing through the web layer, since AccumulatePayload doesn\'t even carry '
    'trigger_question_id today (confirmed this does NOT affect the 19 locked single-key '
    'mappings, which key purely on severity_follow_on_id); (4) 19 of 32 live '
    'severity_trigger IDs locked to intended states (Pete-confirmed directly, not just '
    'proposed), 11 unmapped (harmless per the Emerging fallback, not a blocker), 2 '
    'explicitly excluded (SEVER-05, SEVER-13); (5) recalibration-scope estimate -- 14/175 '
    'profiles (8%) would see a real tier change, all decreases, no new escalations; (6) '
    'recalibration sequencing LOCKED: Bundle, not a separate follow-on, given the small '
    'fully-characterized scope, unlike the MC_CENTROID_39 precedent\'s unpredictable blast '
    'radius; (7) one taxonomy gap (decision-authority ambiguity, SEVER-03/E) flagged '
    'separately in its own Decision Register row rather than left buried in the doc. No '
    'engine code touched by any session that produced this scoping work. | This session '
    '(Claude Code), 2026-08-19 | No forced check-in. Next real step is Gemini submission '
    '(Pete\'s call on timing) -- once Gemini clears the architecture, this becomes a real '
    'build session, still gated by standing Tier 3 protocol. |\n'
)

REPLACEMENTS = [
    (
        CLAUDE_PATH,
        "CLAUDE.md MOB version cross-reference",
        "| MOB version | v4.188 |",
        "| MOB version | v4.189 |",
    ),
    (
        MOB_PATH,
        "rewrite severity follow-on state scoping row",
        OLD_ROW,
        NEW_ROW.rstrip("\n"),
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
    assert mob_lines[header_idx].endswith("MOB v4.188"), (
        f"ABORT [header bump]: line 9 does not end with 'MOB v4.188': {mob_lines[header_idx]!r}"
    )
    mob_lines[header_idx] = mob_lines[header_idx].replace("v4.188", "v4.189")
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
