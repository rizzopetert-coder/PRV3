"""
MOB update: Visualize Your Data Layer 1 field-placement claims verified
clean (4/4, direct file inspection against fd80709/HEAD), and a build spec
now exists: prompts/visualize-your-data-layer1-build-spec.md.

Confirmed this round: assemble_output()'s severity_obj (engine/contract.py,
~line 434) has real keys tier/score/anchor_text/inputs, exact match;
PrivateOutputBlock's real fields (state_name, severity_tier,
severity_anchor_text, resolution_family) exact match; _TOP_LEVEL_SCHEMA
types only top-level keys, no nested severity shape; call chain traced
consistent (OutputEngine.build() -> session.output_package.private,
consumed later by assemble_output() alongside a separately-built
severity_obj -- no contradiction between the two verification rounds).
tools/test_contract.py:178 confirmed unaffected by nesting inside severity.

Row title updated to reflect the build spec now exists; blocker column
updated -- the "Gemini review not yet sent" blocker retires (this Q&A
round served that function and verified clean); remaining gate is the
standard Tier 1 mechanism (dry-run patch script -> Pete confirms ->
commit), not yet actioned.

Version bump: v4.208 -> v4.209 (workstream status materially changed).

Usage:
    python patch_mob_vyd_layer1_spec.py --dry-run
    python patch_mob_vyd_layer1_spec.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "SCOPED, not yet Gemini-reviewed, not yet built | 3 |"
)
NEW_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "Layer 1 build spec verified and drafted, not yet built | 3 |"
)

OLD_STATUS_TAIL = (
    "Route-path citations also checked: "
    "`web/app/api/dev/diagnostic-preview/route.ts` and "
    "`web/lib/dev-diagnostic-preview.ts` confirmed as two distinct real "
    "objects (a route path and a separate lib file), not a naming "
    "conflict -- both citations were partially right. `ENGINE_VERSION` "
    "confirmed `\"0.2.0\"` at engine/contract.py:50, current HEAD "
    "(014f3f7)."
)
NEW_STATUS_TAIL = (
    "Route-path citations also checked: "
    "`web/app/api/dev/diagnostic-preview/route.ts` and "
    "`web/lib/dev-diagnostic-preview.ts` confirmed as two distinct real "
    "objects (a route path and a separate lib file), not a naming "
    "conflict -- both citations were partially right. `ENGINE_VERSION` "
    "confirmed `\"0.2.0\"` at engine/contract.py:50, current HEAD "
    "(014f3f7). **Layer 1 field-placement verification, second round, "
    "completed 2026-08-20 (direct file inspection against fd80709):** "
    "all 4 claims checked out clean, no errors this round. "
    "`assemble_output()`'s `severity_obj` (engine/contract.py, ~line 434) "
    "confirmed with exact real keys `tier`/`score`/`anchor_text`/`inputs`, "
    "matching `_SEVERITY_FIELDS`. `PrivateOutputBlock`'s real fields "
    "(`state_name`, `severity_tier`, `severity_anchor_text`, "
    "`resolution_family`) confirmed exact. `_TOP_LEVEL_SCHEMA` confirmed "
    "to type only the 15 top-level keys, no nested shape for "
    "`\"severity\"`. Call chain traced end to end, no contradiction "
    "with the first round's confirmed OutputEngine.build() chain: "
    "`session.output_package.private` (built via `OutputEngine.build()` "
    "-> `build_private_block()`) is consumed by `assemble_output()` to "
    "build `private_output`, while `severity_obj` is built separately in "
    "the same function from `session.severity_result` -- two different "
    "fields, same pipeline, sequential, not conflicting. Incidental "
    "finding: `private_output` (contract.py line 558) only reads "
    "`priv.state_name` today -- `priv.severity_tier`/`severity_anchor_text` "
    "are computed but never surface in the wire contract, concretely "
    "confirming the feature's original problem statement. Build spec "
    "written: prompts/visualize-your-data-layer1-build-spec.md -- "
    "`by_state` key nested inside `severity_obj` (list of "
    "{state_id, tier, score_0_100} for identified_states members), "
    "ENGINE_VERSION 0.2.0 -> 0.2.1, tools/test_contract.py:178 confirmed "
    "unaffected (no count/key-set assertion exists on the severity "
    "sub-object; nesting leaves len(output) at 16)."
)

OLD_BLOCKER = (
    "(1) Layer 1 is a locked-contract change and still requires its own "
    "Gemini architecture review before execution, per CLAUDE.md's "
    "Architectural Decisions rule -- not yet sent, now to be framed "
    "around the VERIFIED facts above rather than the original review's "
    "incorrect claims. The original \"whitelist must be updated to avoid "
    "validate_schema() breaking\" concern is retired -- confirmed false "
    "against the real function. Real open question to bring to that "
    "review instead: whether the new field should nest inside an "
    "existing key (e.g. `\"severity\"`) or be added top-level, which "
    "would require updating tools/test_contract.py:178's hardcoded count "
    "from 16 to 17 -- a genuine design fork, not previously identified. "
    "Whether a purely additive VII.1 field needs an ENGINE_VERSION bump "
    "(currently 0.2.0) under the section's stated immutability rule "
    "remains open, not resolved by this verification pass. (2) Audience "
    "sequencing -- RESOLVED, Pete confirmed 2026-08-20: build "
    "PrivateOutput.tsx internal-only first; ShareableOutput.tsx and its "
    "P-13 framing deferred to a separately-gated Phase 2, not bundled "
    "into this build."
)
NEW_BLOCKER = (
    "(1) Gemini architecture review -- RESOLVED via this session's "
    "two-round verified Q&A (placement question answered: nest inside "
    "`severity`, not top-level; ENGINE_VERSION bump to 0.2.1 confirmed "
    "reasonable). No further Gemini round scheduled. Remaining gate is "
    "the standard Tier 1 mechanism (CLAUDE.md, Workflow Governance): "
    "dry-run patch script -> Pete confirms -> commit -- not yet actioned, "
    "build spec exists (prompts/visualize-your-data-layer1-build-spec.md) "
    "but no implementation code written. (2) Audience sequencing -- "
    "RESOLVED, Pete confirmed 2026-08-20: build PrivateOutput.tsx "
    "internal-only first; ShareableOutput.tsx and its P-13 framing "
    "deferred to a separately-gated Phase 2, not bundled into this "
    "build."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "send the corrected Layer 1 handoff for Gemini review -- not "
    "time-sensitive, no hard dependency on other open items. Audience "
    "sequencing no longer a check-in item (resolved above). Still a "
    "candidate for the ~August 23 Quarterly Step-Back's forward-planning "
    "discussion if Pete wants to fold it in, but can proceed "
    "independently before then. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "greenlight the Layer 1 dry-run build -- not time-sensitive, no hard "
    "dependency on other open items. Neither audience sequencing nor "
    "the Gemini review are check-in items any longer (both resolved "
    "above). Still a candidate for the ~August 23 Quarterly Step-Back's "
    "forward-planning discussion if Pete wants to fold it in, but can "
    "proceed independently before then. |"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    mob_text = MOB_PATH.read_text(encoding="utf-8")

    for label, old, new in [
        ("title", OLD_TITLE, NEW_TITLE),
        ("status tail", OLD_STATUS_TAIL, NEW_STATUS_TAIL),
        ("blocker column", OLD_BLOCKER, NEW_BLOCKER),
        ("tail (last touched / next check-in)", OLD_TAIL, NEW_TAIL),
    ]:
        count = mob_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        mob_text = mob_text.replace(old, new, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.208"
    version_new = "\\\\\\#\\\\\\# MOB v4.209"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.208 |"
    claude_new = "| MOB version | v4.209 |"
    count = claude_text.count(claude_old)
    if count != 1:
        raise SystemExit(f"ABORT [CLAUDE.md version]: expected exactly 1 match, found {count}")
    claude_text = claude_text.replace(claude_old, claude_new, 1)

    if args.dry_run:
        for path, original, new_text in [
            (MOB_PATH, MOB_PATH.read_text(encoding="utf-8"), mob_text),
            (CLAUDE_MD_PATH, CLAUDE_MD_PATH.read_text(encoding="utf-8"), claude_text),
        ]:
            print(f"\n{'=' * 80}\nDIFF: {path}\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
            )
            print("".join(diff))
        print("\nDry run complete. No files written. Re-run with --write to apply.")
    else:
        MOB_PATH.write_text(mob_text, encoding="utf-8")
        CLAUDE_MD_PATH.write_text(claude_text, encoding="utf-8")
        print(f"WROTE: {MOB_PATH}")
        print(f"WROTE: {CLAUDE_MD_PATH}")


if __name__ == "__main__":
    main()
