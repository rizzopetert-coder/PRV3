"""
PRV3 -- MOB update: Category E Direction 3 (editorial/typographic hero:
cluster display) shipped. Records both corrected Gemini findings from
this build's verification pass, and the percentage-drop content decision,
as further confirmed instances of the standing Gemini-verification-
catches-real-errors pattern.

Version bump v4.147 -> v4.148: a Direction 3 build closes, touching
shipped presentation code on the real results page.

Usage:
  python tools/patch_mob_direction3_shipped.py --dry-run
  python tools/patch_mob_direction3_shipped.py --write
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

ANCHOR = (
    "| Primary-state / intended-target match rate -- FLAGGED, standalone investigation candidate | 3 | **Flagged, not investigated further -- Pete's call on if/when to open this thread** | N/A -- not scheduled | prompts/primary-state-target-match-finding.md written -- a durable planning artifact, no code changes. Surfaced as a side effect of the same Direction 3 data pull, not sought out deliberately: across the 58 real high_confidence profiles, the displayed primary_state (actual #1-by-score from rank_states()) matched the profile's own intended target state in only 1 of 58 cases -- the other 57 landed anywhere from rank 2 to rank 58 (dead last) among all states, usually surfacing inside the tied secondary cluster instead. Real but contextualized, not presented as a bare alarming number: this project's calibration suite has a long-locked cluster/top_3/prominence pass criterion, not rank-1 (Session 7 precedent, reconfirmed at Session 69 -- only built_to_fail was found to reliably achieve rank-1 anywhere in the taxonomy), and the calibration suite's own pass bar (SCD_WCS_CLUSTER_WINDOW = 0.35) is confirmed far more permissive than the live display's actual qualification gate (SCD_WCS_MARGIN_GATE = 0.05) -- so this is not a hidden calibration-suite failure, it's a distinct property of the live margin gate specifically, sitting underneath a pass bar already designed with wide tolerance in mind. Open question, explicitly not resolved: is 1/58 still inside what \"cluster, not rank-1\" was always expected to produce, or does it indicate more dimensional overlap between states than originally intended. Methodology caveat logged honestly: pulled via generate_answers()'s systematic answer-selection heuristic, not organic human answers -- real respondent answers could spread scores less evenly, though the structural cause (states sharing closely related dimensional_vector profiles) is a taxonomy property, not a test-answer artifact, so some clustering would likely persist regardless. Not blocking Direction 3 -- the report should represent real multiplicity honestly either way. | This session (Claude Code) | Pete's call -- not scheduled, no forced check-in. Reopen only if Pete decides the 1/58 figure warrants its own dedicated investigation |"
)

NEW_ROW = (
    '\n'
    '| Category E Direction 3 (editorial/typographic hero: cluster display) -- SHIPPED | 3 | **Closed -- built, verified, live before/after check via Pete\'s claude-in-chrome, not a manual walkthrough** | N/A | Gemini architecture review cleared the design direction (delta-weight bucket at 0.08, core cluster capped at 5, "+N" overflow affordance, typographic hierarchy per the token table) -- two of five verification-gate claims corrected before any code was written, both further confirmed instances of the standing Gemini-verification-catches-real-errors pattern already logged multiple times this project. **Correction 1 (component path):** Gemini claimed web/app/diagnostic/components/PrivateOutput.tsx -- confirmed via direct filesystem check that this path does not exist; the real component is web/components/PrivateOutput.tsx, the same path used throughout Direction 1\'s work this session. **Correction 2 (output-renderer.ts):** Gemini\'s Phase 1 plan targeted renderPrivateOutput() in web/lib/output-renderer.ts -- the file and function are real, exactly as named, but confirmed via repo-wide grep to have zero callers anywhere; PrivateOutput.tsx reads the raw PrivateOutputPayload directly, never through that view-model layer. Patching it would have compiled clean and changed nothing about what a respondent actually sees. All bucketing logic built inline in PrivateOutput.tsx instead; output-renderer.ts left completely untouched per Pete\'s explicit instruction (not modified, not deleted, not "cleaned up" -- that\'s a separate future decision). Two smaller items also confirmed accurate before use: --font-display (Lora) and --font-ui (Inter) are the real tokens (--font-sans exists but maps to Geist Sans, a different typeface, deliberately not used anywhere in this build); secondary_states confirmed the correct, fully unfiltered source on both Path A and Path B construction sites, zero backend/route changes needed. BUILD: buildCoreCluster() helper (module-level, alongside the existing firstSentence() pattern) -- filters secondary_states to those within CORE_CLUSTER_DELTA=0.08 of the primary state\'s normalized weight, caps at CORE_CLUSTER_CAP=5, returns overflowCount for the rest. Block 1 hero treatment: primary condition name at font-display/text-3xl (Lora), replacing the prior text-[13px] treatment; eyebrow softened from "Condition identified" to "Most prominent pattern". Block 4b: "Also present" flat bulleted list replaced with a "Co-occurring conditions" section -- core cluster members at font-display/text-lg (Lora, uniform "secondary" weight, not graduated per member), plus a "+N co-occurring conditions" overflow affordance (font-ui) when the cluster exceeds the cap. **Content decision, Pete-confirmed:** the literal per-state percentage ("(N%)") is dropped entirely from the core cluster display -- showing that number repeated up to 5 times was the exact visual symptom motivating this redesign (near-identical percentages undermining the "co-occurring" framing, confirmed via the real distribution data behind this Direction); typographic presence carries the signal instead. Reversible if it doesn\'t read well live -- not a locked decision, just the shipped default. VERIFICATION: tsc --noEmit clean. output-renderer.ts confirmed untouched via diff. Full vitest run: same 6 pre-existing, unrelated session-store.test.ts failures as Direction 1 (confirmed same file, same stale sequence-length assertions), nothing new. Edge-case logic verification (Gemini\'s own Phase 3 recommendation) pulled three REAL high_confidence calibration profiles through the actual engine pipeline, not invented weight arrays -- APT-OM-01 (n=2): core=1, overflow=0; EXP-IC-01 (n=25): core=5 (cap), overflow=19; ATT-BC-01 (n=32, the real max in the 58-profile sample, closest available to "~30+"): core=5 (cap), overflow=26 -- then re-ran the exact buildCoreCluster() code (not a re-derivation) in Node against the same three real weight arrays, confirming an exact match with zero transcription error and no crashes at either extreme. Logic-level only -- cannot confirm visual layout without a browser, held for Pete\'s live check. One observation flagged, not acted on: in all three real cases the 0.08 delta threshold never excluded anything the 5-cap wouldn\'t have anyway -- normalized weight gaps shrink as the qualified count grows, so the cap does most of the real bounding work in practice; the 0.08 threshold stays as specified. Diff reviewed and approved by Pete before commit. | This session (Claude Code) | Pete\'s call -- reopen if the live before/after check surfaces a rendering issue, or if the dropped-percentage decision doesn\'t read well live and needs reverting. Category E\'s three-direction sequencing is now fully explored (Directions 1 and 3 shipped, Direction 2 -- the four-dial instrument-panel reframe -- remains concept-level, Pete\'s call whenever he wants to pick it up) |\n'
)


def apply(dry_run: bool) -> int:
    changed = 0
    path = REPO_ROOT / MOB
    text = path.read_text(encoding="utf-8")
    count = text.count(ANCHOR)
    if count != 1:
        print(f"ERROR: {MOB} -- expected 1 match for anchor, found {count}")
        return 1
    new_text = text.replace(ANCHOR, ANCHOR + NEW_ROW, 1)
    if dry_run:
        print(f"OK (dry-run): {MOB} -- anchor found, would insert 1 new row")
    else:
        path.write_text(new_text, encoding="utf-8")
        print(f"WRITTEN: {MOB} -- 1 new row inserted")
    changed += 1

    version_edits = [
        (MOB, "\\\\\\#\\\\\\# MOB v4.147", "\\\\\\#\\\\\\# MOB v4.148"),
        ("CLAUDE.md", "| MOB version | v4.147 |", "| MOB version | v4.148 |"),
    ]
    for rel_path, old, new in version_edits:
        p = REPO_ROOT / rel_path
        t = p.read_text(encoding="utf-8")
        c = t.count(old)
        if c != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {c}")
            return 1
        nt = t.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            p.write_text(nt, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1

    print(f"\n{changed}/3 edits {'validated' if dry_run else 'applied'}.")
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
