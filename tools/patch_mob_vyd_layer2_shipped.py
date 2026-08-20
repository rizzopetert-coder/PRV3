"""
MOB update: Visualize Your Data Layer 2 SHIPPED, commit c4c447d.

Wires severity_by_state through to PrivateOutputPayload: EngineResult.
severity.by_state (engine-client.ts), StateSeverityEntry + new sibling
field PrivateOutputPayload.severity_by_state (types.ts, optional -- see
DevDiagnosticPreviewPayload finding), both real builders wired
(session/answer/route.ts, result/route.ts).

Checkpoint 6's original "4 routes" now fully reconciled: all 10 app
routes checked directly (not just the plausible ones). 2 real
PrivateOutputPayload builders (wired); share/create/route.ts confirmed
(zero PrivateOutputPayload references, builds ShareableOutputPayload
only) correctly excluded; condensed/answer/route.ts (Category D)
confirmed excluded (state_severity always {}); session/resume/route.ts
and dev/diagnostic-preview/route.ts both reference severity but
construct no output payload from live engine output. "4" = 2 Private + 1
Shareable + 1 Condensed across all payload types, not 4 Private routes.

Verified before commit: tsc clean, vitest unchanged from baseline
(39/45, same 6 pre-existing failures), git diff --stat confirmed exactly
4 files touched.

Version bump: v4.210 -> v4.211 (workstream status materially changed --
Layer 2 shipped).

Usage:
    python patch_mob_vyd_layer2_shipped.py --dry-run
    python patch_mob_vyd_layer2_shipped.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "Layer 1 SHIPPED (commit 8f1cd93), Layers 2-3 not started | 3 |"
)
NEW_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "Layers 1-2 SHIPPED (commits 8f1cd93, c4c447d), Layer 3 not started | 3 |"
)

OLD_STATUS_TAIL = (
    "Build spec written: prompts/visualize-your-data-layer1-build-spec.md "
    "-- `by_state` key nested inside `severity_obj` (list of {state_id, "
    "tier, score_0_100} for identified_states members), ENGINE_VERSION "
    "0.2.0 -> 0.2.1, tools/test_contract.py:178 confirmed unaffected (no "
    "count/key-set assertion exists on the severity sub-object; nesting "
    "leaves len(output) at 16)."
)
NEW_STATUS_TAIL = (
    "Build spec written: prompts/visualize-your-data-layer1-build-spec.md "
    "-- `by_state` key nested inside `severity_obj` (list of {state_id, "
    "tier, score_0_100} for identified_states members), ENGINE_VERSION "
    "0.2.0 -> 0.2.1, tools/test_contract.py:178 confirmed unaffected (no "
    "count/key-set assertion exists on the severity sub-object; nesting "
    "leaves len(output) at 16). **Layer 2, SHIPPED (commit c4c447d):** "
    "wires severity_by_state through to the web side. "
    "`EngineResult.severity` (engine-client.ts) gains `by_state` "
    "(type-only, matches `severity_obj.by_state` exactly). "
    "`PrivateOutputPayload` gains a new SIBLING field, "
    "`severity_by_state?: StateSeverityEntry[]` -- deliberately not "
    "nested inside `severity`, which is a bare `SeverityTier` string "
    "read by 9 real call sites (PrivateOutput.tsx x4, "
    "output-renderer.ts x2, ShareableOutput.tsx, CondensedOutput.tsx "
    "x2); nesting would have broken all of them. Optional, not "
    "required: making it required broke two dev-only files "
    "(`app/dev/diagnostic-preview/[id]/page.tsx`, "
    "`DiagnosticFixturePicker.tsx`) that pass `DevDiagnosticPreviewPayload` "
    "into `<PrivateOutput>` by structural typing -- that type omits "
    "`severity_by_state` the same way it already omits "
    "`cascade_risk`/`causation_pattern`/`trajectory`/`urgency_window`, "
    "caught by tsc itself, fixed the same established way. **Checkpoint "
    "6's \"4 routes\" fully reconciled this pass:** all 10 app routes "
    "checked directly, not just the plausible ones. 2 real "
    "`PrivateOutputPayload` builders (session/answer/route.ts, "
    "result/route.ts -- both wired). `share/create/route.ts` confirmed "
    "(zero `PrivateOutputPayload` references, direct grep) builds only "
    "`ShareableOutputPayload` -- correctly excluded, audience decision. "
    "`condensed/answer/route.ts` (Category D) confirmed excluded, same "
    "`state_severity` always `{}` finding as Layer 2's original scope "
    "pass. `session/resume/route.ts` and `dev/diagnostic-preview/route.ts` "
    "both reference severity but construct no output payload from live "
    "engine output (the former is read-only session-state access; the "
    "latter validates/stores an externally pre-built "
    "`DevDiagnosticPreviewPayload` from `tools/diagnostic_fast_forward.py`, "
    "an already-flagged unusable dev tool). \"4\" = 2 Private + 1 "
    "Shareable + 1 Condensed across all payload types, not 4 Private "
    "routes -- the discrepancy fully accounted for, not a search gap. "
    "Verified before commit: tsc clean, vitest unchanged from baseline "
    "(39/45, same 6 pre-existing session-store.test.ts failures), git "
    "diff --stat confirmed exactly 4 files touched "
    "(types.ts/engine-client.ts/session-answer-route.ts/result-route.ts), "
    "ShareableOutput.tsx/CondensedOutput.tsx untouched by construction."
)

OLD_BLOCKER = (
    "(1) Layer 1 -- SHIPPED, commit 8f1cd93, 2026-08-20. Tier 1 "
    "mechanism completed in full: dry-run patch script "
    "(tools/patch_visualize_your_data_layer1.py) -> diff + verification "
    "reviewed by Pete -> commit."
)
NEW_BLOCKER = (
    "(1) Layer 1 -- SHIPPED, commit 8f1cd93, 2026-08-20. Layer 2 -- "
    "SHIPPED, commit c4c447d, 2026-08-20. Both via the same Tier 1 "
    "mechanism: dry-run patch script -> diff + verification reviewed by "
    "Pete -> commit."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "scope and start Layer 2 (wire plumbing) and Layer 3 "
    "(PrivateOutput.tsx UI) -- not time-sensitive, no hard dependency on "
    "other open items. Still a candidate for the ~August 23 Quarterly "
    "Step-Back's forward-planning discussion if Pete wants to fold it "
    "in, but can proceed independently before then. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "scope and start Layer 3 (PrivateOutput.tsx UI) -- not "
    "time-sensitive, no hard dependency on other open items. Still a "
    "candidate for the ~August 23 Quarterly Step-Back's forward-planning "
    "discussion if Pete wants to fold it in, but can proceed "
    "independently before then. |"
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

    version_old = "\\\\\\#\\\\\\# MOB v4.210"
    version_new = "\\\\\\#\\\\\\# MOB v4.211"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.210 |"
    claude_new = "| MOB version | v4.211 |"
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
