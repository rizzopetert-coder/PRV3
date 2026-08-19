"""
MOB update -- Section 13a's "Severity follow-on state scoping" row rewritten
to reflect Gemini's architecture review round: 6 specific technical claims
independently verified (none fabricated, 3 real consumer-list gaps found and
folded into the scoping doc's Section 3, 12 -> 14 real consumers). Doc
corrections committed. Documentation only, no engine code touched.

Re-verified fresh before writing: MOB header confirmed v4.189 (line 9),
CLAUDE.md cross-reference confirmed v4.189 (line 183), the row's current
exact text confirmed via direct read immediately before this script was
written.

Usage:
    python patch_mob_severity_gemini_verified.py --dry-run
    python patch_mob_severity_gemini_verified.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_PATH = Path("CLAUDE.md")

OLD_ROW = Path(
    "C:/Users/rizzo/AppData/Local/Temp/claude/c--Users-rizzo-PRV3/"
    "9354bfe3-2f47-478f-ac95-6d59ebb8dbc1/scratchpad/sever_row_v189.txt"
).read_text(encoding="utf-8")

NEW_ROW = (
    '| Severity follow-on state scoping -- Gemini architecture review round complete, '
    'specific claims independently verified, doc corrected | 3 | **Gemini reviewed the '
    'scoping doc, confirmed Items A-E, and returned 6 additional specific technical '
    'claims. All 6 independently verified against real source before being trusted -- '
    'none fabricated, but 3 exposed genuine gaps in the doc\'s original consumer list, '
    'now corrected and committed.** Whether this corrected version goes back to Gemini '
    'for a confirming second pass or moves straight to build authorization is Pete\'s '
    'call, not decided here. | None remaining for scoping or verification. Pete\'s call '
    'on next step (re-review vs. build authorization) is the only thing outstanding. | '
    'Full record: prompts/severity-result-per-state-redesign-scope.md, corrected this '
    'session (commit df83122). Gemini\'s 6 claims and their verification: (1) '
    '_build_synthesis_prompt() (engine/output_synthesis.py:264-313) -- CONFIRMED REAL, a '
    'genuine gap. Takes severity_tier directly, writes it into the LLM-facing synthesis '
    'prompt (line 303), called from engine/main.py:107 and :640 with '
    'severity_result.tier -- the narrative text a user reads is severity-driven too, not '
    'just the output JSON\'s numeric fields. Added to Section 3. (2) '
    '_assemble_monitoring_metadata() (engine/contract.py:242-313) -- CONFIRMED REAL, '
    'already covered under the existing Decision Blindness flag entry, just not named by '
    'function; named explicitly for clarity, not a new consumer. (3) PrivateOutput.tsx -- '
    'CONFIRMED REAL and exposed a real error: web/lib/output-renderer.ts (previously '
    'listed as the live web render consumer) is confirmed dead code, zero imports '
    'anywhere in the repo (matches an earlier separate finding, Category E Direction 3 '
    'session). The real live consumers are web/components/PrivateOutput.tsx (reads '
    'payload.severity directly, lines 98/129/138/163) and ShareableOutput.tsx (line 70) '
    '-- both added to Section 3 in output-renderer.ts\'s place. (4) StateRef and '
    'IdentifiedStateBlock -- both CONFIRMED REAL. StateRef (web/lib/types.ts:47-52) is '
    'real and relevant, the type a web-side state_severity lookup should key against via '
    '.id -- noted in Section 3. IdentifiedStateBlock is real but exists only inside the '
    'now-removed dead output-renderer.ts, not relevant. (5) _TOP_LEVEL_SCHEMA / '
    'validate_schema() (engine/contract.py:572-588, 647-728) -- CONFIRMED REAL and '
    'mechanically sound: the validator checks required fields are present and correctly '
    'typed, never rejects unexpected extra fields, confirming Gemini\'s backward-'
    'compatibility reasoning holds for adding state_severity. (6) The "0.6x scalar" -- '
    'CONFIRMED REAL, precisely traced: engine/friction_tax.py:73-77, SEVERITY_SCALAR = '
    '{"Emerging": 0.6, "Entrenched": 1.0, "Endemic": 1.4}, explicitly marked LOCKED, '
    'applied at friction_tax.py:1908 inside compute_friction_tax() -- the real multiplier '
    'driving the friction-tax dollar estimate off session-wide tier, now cited precisely '
    'under Section 3\'s existing compute_friction_tax() entry. **Net result: Section 3\'s '
    'consumer count corrected from 12 to 14** (-1 dead-code removal, +3 real additions). '
    'No engine code touched, no build work, across any session in this thread. | This '
    'session (Claude Code), 2026-08-19 | Pete\'s call: submit the corrected doc back to '
    'Gemini for a confirming pass, or treat this verification round as sufficient and '
    'move to build authorization. No forced check-in either way. |\n'
)

REPLACEMENTS = [
    (
        CLAUDE_PATH,
        "CLAUDE.md MOB version cross-reference",
        "| MOB version | v4.189 |",
        "| MOB version | v4.190 |",
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
    assert mob_lines[header_idx].endswith("MOB v4.189"), (
        f"ABORT [header bump]: line 9 does not end with 'MOB v4.189': {mob_lines[header_idx]!r}"
    )
    mob_lines[header_idx] = mob_lines[header_idx].replace("v4.189", "v4.190")
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
