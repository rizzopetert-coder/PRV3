"""
PRV3 -- MOB update: A1 (free-text "Other" elaboration) Decision Register
row, Open/pending-Gemini -> CLOSED. Full build shipped this session
(tools/patch_a1_free_text_other_phase1/2/3.py), tsc clean, full
172(+3)-profile regression held at 170/175 (moderate 53/58) -- zero
movement, confirming Gemini's claim that elaboration text never touches
accumulation.py. engine/data/validate.py's one failure is the pre-existing,
already-logged cluster_id gap (same 5 states), confirmed unrelated.

Version bump v4.136 -> v4.137: new Decision Register row closes a Tier 3
item with real implementation, not a session-log-only change.

Usage:
  python tools/patch_mob_a1_closed.py --dry-run
  python tools/patch_mob_a1_closed.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


MOB = "tools/_mob.txt"
CLAUDE_MD = "CLAUDE.md"

edit(
    MOB,
    '| A1 (diagnostic usability, free-text "Other" option) -- sent to Gemini for architecture review, awaiting response | 3 | Open -- pending Gemini | Response not yet received | Category A item A1 (adding a free-text "Other" option to the relevant intake/diagnostic question) was sent to Gemini for architecture review this session, scoped to the P-03 clinical-boundary implications of accepting free-text input in a diagnostic context -- a different concern than the schema-collision reviews used for prior content batches. Not implemented -- no code changes made pending Gemini\'s response. | This session (Claude Code) | Reopen once Gemini\'s review returns -- not a scheduled check-in |',
    '| A1 (diagnostic usability, free-text "Other" option) -- CLOSED, shipped | 3 | **Closed -- built, verified, zero regression** | N/A | Gemini architecture review returned: CLEARED TO BUILD WITH STRUCTURAL AIRGAP -- significant_event_elaboration is free-text, isolated from vector scoring entirely (engine/accumulation.py never parses it), feeds only synthesis-prompt construction, and is kept off ShareableOutputPayload at the type level (a new PrivateIntakeEcho extends ShareableIntakeEcho; ShareableIntakeEcho has none) rather than a runtime flag. Two of Gemini\'s specific technical claims were independently verified before writing any diff, per this project\'s standing verification discipline -- both caught real problems: (1) Gemini cited a lookup constant "EVENT_LABEL_LOOKUP" in engine/output_synthesis.py -- confirmed via repo-wide grep to not exist anywhere; the real, already-wired mechanism is PRIOR_ADJUSTER_INDEX (engine/data/intake.py), already imported and used in output_synthesis.py exactly as the Mechanism-1-deprecation Phase 3 record describes. The new format_event_for_synthesis() keys off PRIOR_ADJUSTER_INDEX, not the fabricated name, special-casing "other" (which has no PRIOR_ADJUSTER_INDEX counterpart, since it never existed as a Mechanism-1 event type) with the respondent\'s own elaboration text. (2) Gemini\'s proposed _INTAKE_FIELDS addition (engine/contract.py) listed both "headcount" and "org_size" as separate keys -- confirmed via direct read that both already exist there; nothing to correct, only significant_event_elaboration needed adding. Three further corrections found while tracing the actual data path, not in Gemini\'s condensed summary: web/app/api/diagnostic/session/answer/route.ts has no mapIntake() function at all (passes session.intake straight through -- Gemini\'s phase list named a file with nothing to edit); web/app/api/share/create/route.ts\'s mapIntake() needed no destructure-strip step, since it already builds the shareable object field-by-field, explicitly, never spreading the engine\'s raw intake dict (only its return-type annotation changed, IntakeEcho -> ShareableIntakeEcho); and none of Gemini\'s 3 named phases touched the actual UI -- the checkbox + free-text box a respondent types into (web/components/DiagnosticFlow.tsx\'s SignificantEventsField) wasn\'t in the phase list at all. Two product decisions confirmed with Pete before writing: elaboration is REQUIRED when "other" is checked (mirrors the existing none/other-events mutual-exclusivity pattern already in that component -- an incomplete submission, gated by isComplete, not a separate error state; re-enforced server-side in validateIntake(), the real trust boundary); textarea, 500-char cap. BUILD, 3 phases (tools/patch_a1_free_text_other_phase1/2/3.py, all dry-run validated before write, 30/30 edits matched exactly once): Phase 1 (web/lib/types.ts split IntakeEcho -> ShareableIntakeEcho/PrivateIntakeEcho, "other" added to SIGNIFICANT_EVENT_OPTIONS; DiagnosticFlow.tsx UI; PrivateIntakeEcho threaded through web/lib/session-store.ts, web/lib/engine-client.ts, web/lib/dev-diagnostic-preview.ts so the type carries end-to-end from browser to Redis to the engine POST body, not just at the two payload boundaries). Phase 2 (engine/accumulation.py: IntakeData gains significant_event_elaboration, defaulted so every pre-existing constructor call keeps working; engine/main.py: both IntakeData construction sites populate it, Path B via .get() with a safe default since that path\'s UI never collects it; engine/contract.py: _INTAKE_FIELDS + intake_obj; engine/output_synthesis.py: format_event_for_synthesis() + _build_synthesis_prompt() wiring). Phase 3 (session/start/route.ts: validateIntake() enforces the required-when-"other" rule server-side; result/route.ts: mapIntake() threads the field through from the engine\'s intake echo; share/create/route.ts: return-type change only). VERIFICATION: tsc --noEmit clean. tools/test_main.py 36/36. Full 172(+3)-profile calibration regression: 170/175 passed, moderate 53/58 -- byte-identical to the pre-change baseline, zero movement, confirming the airgap claim empirically (elaboration text genuinely never reaches scoring). engine/data/validate.py: 40/41 -- the one failure (cluster_id gap, 5 named states) is the pre-existing, already-logged Decision Register item, confirmed unrelated by exact state-list match. | This session (Claude Code) | Closed -- no further check-in. If a comparable free-text intake field is ever added elsewhere, this row is the reusable precedent for the airgap pattern (type-level split, not a runtime flag) |',
)

edit(
    MOB,
    "\\\\\\#\\\\\\# MOB v4.136",
    "\\\\\\#\\\\\\# MOB v4.137",
)

edit(
    CLAUDE_MD,
    "| MOB version | v4.136 |",
    "| MOB version | v4.137 |",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
