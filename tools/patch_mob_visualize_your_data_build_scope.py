"""
MOB update: Visualize Your Data (per-state severity comparison) Decision
Register row progressed from "raw concept, not scoped" to "fully scoped,
not yet Gemini-reviewed, not yet built" -- full build scope now exists
(3 layers) in the new durable doc prompts/visualize-your-data-build-scope.md,
companion to the earlier prompts/visualize-your-data-severity-comparison-concept.md.

Two open blockers carried into the updated row, neither resolved this pass:
(1) Layer 1 (VII.1 schema addition) is a locked-contract change requiring
its own Gemini architecture review before execution, per CLAUDE.md's
Architectural Decisions rule -- not yet sent. (2) Audience sequencing
(internal-only first vs. both PrivateOutput.tsx and ShareableOutput.tsx
together) is an open decision for Pete, with a stated recommendation not
yet confirmed.

Version bump: v4.205 -> v4.206 (workstream status change, not a session-log-only entry).

Usage:
    python patch_mob_visualize_your_data_build_scope.py --dry-run
    python patch_mob_visualize_your_data_build_scope.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_ROW = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "RAW CONCEPT, not scoped, not approved for build | 3 | RAW CONCEPT, "
    "no urgency assigned. Not scoped, not approved for build. Durable "
    "record only: prompts/visualize-your-data-severity-comparison-concept.md. "
    "| N/A -- captured for continuity, not yet a scoping conversation | "
    "New report section showing every qualifying state's own severity "
    "(tier + score_0_100 magnitude) side by side, no state visually "
    "privileged over another -- deliberately NOT lead-state-anchored, a "
    "departure from Checkpoint 3's pattern for the existing single-scalar "
    "VII.1 fields. Audience: both client-facing and internal. Design "
    "settled this session (Claude.ai): row-based layout, one row per "
    "state already in identified_states (not all 58 taxonomy states); "
    "each row = state name, color-coded tier badge, continuous bar "
    "reflecting the state's own score_0_100 within its tier (so two "
    "states sharing a tier stay visually distinguishable); no "
    "sorting/ranking implied by row position. Confirmed with Pete: "
    "Emerging is the real floor of the severity scale (zero-input state "
    "classifies as Emerging via the real math, not a placeholder "
    "default) -- worth an explanatory note in the eventual UI so a short "
    "bar reads as a real finding, not as borderline. Underlying data "
    "need: engine/severity.py's state_severity dict (tier + "
    "score_0_100, computed since Checkpoint 1) has never crossed the "
    "VII.1 wire contract -- confirmed via Checkpoint 6's full trace this "
    "session that web/lib/types.ts, engine-client.ts, all 4 routes, and "
    "every component only ever see the single top-level severity "
    "scalar; zero `state_severity` matches anywhere under web/. Rough "
    "build shape, not yet scoped: (1) VII.1 schema addition exposing "
    "per-state severity across the wire -- locked-contract change, "
    "needs its own Gemini architecture review, same treatment as "
    "Checkpoint 3; (2) wire-contract plumbing (engine-client.ts, "
    "types.ts, relevant routes) -- mechanical, similar shape to "
    "Checkpoint 2; (3) the UI component in PrivateOutput.tsx, plus an "
    "open decision on ShareableOutput.tsx given the dual audience. | "
    "This session (Claude Code), 2026-08-19 | Pete's call -- not "
    "scheduled, no forced check-in. Needs its own scoping conversation "
    "before any build begins. |"
)

NEW_ROW = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "SCOPED, not yet Gemini-reviewed, not yet built | 3 | **Full build "
    "scope now exists across 3 layers -- durable record: "
    "prompts/visualize-your-data-build-scope.md, companion to the "
    "earlier concept doc (prompts/visualize-your-data-severity-comparison-concept.md, "
    "design unchanged from that pass).** Layer 1: VII.1 schema addition "
    "exposing a list of {state_id, tier, score_0_100} entries for every "
    "identified_states member, pure exposure of the existing "
    "state_severity dict, no new computation. Layer 2: wire-contract "
    "plumbing (types.ts, engine-client.ts, routes -- re-traced fresh, "
    "not assumed to match Checkpoint 6's route list; Category D's "
    "run_condensed_engine() likely excluded, needs confirming against "
    "real code before excluding). Layer 3: PrivateOutput.tsx UI section "
    "per the settled design; ShareableOutput.tsx explicitly deferred, "
    "see audience-sequencing blocker. Explicit non-dependency confirmed: "
    "does not need triggering_option_id / split-by-option attribution -- "
    "that belongs to a separate, unrelated prerequisite. Verification "
    "plan specified: full 172(+3)-profile regression byte-identical, new "
    "engine test coverage against state_severity directly, tsc/vitest "
    "extended, live round trip against real state_severity output. | "
    "(1) Layer 1 is a locked-contract change and requires its own "
    "Gemini architecture review before execution, per CLAUDE.md's "
    "Architectural Decisions rule -- not yet sent. Open question for "
    "that review: whether a purely additive VII.1 field needs an "
    "ENGINE_VERSION bump (currently 0.2.0) under the section's stated "
    "immutability rule. (2) Audience sequencing is an open decision for "
    "Pete: build PrivateOutput.tsx internal-only first and gate "
    "ShareableOutput.tsx as a separate Phase 2, versus building both "
    "together now. A recommendation (internal-only first, per P-13's "
    "reading-affordance cost for a Principal-facing multi-state "
    "comparison) has been stated but not confirmed. | This session "
    "(Claude Code), 2026-08-20 | Pete's call -- not time-sensitive, no "
    "hard dependency on other open items. Candidate item for the "
    "~August 23 Quarterly Step-Back's forward-planning discussion, but "
    "the audience-sequencing decision and the Gemini-review go-ahead can "
    "each move independently of the Step-Back if Pete wants to proceed "
    "sooner. |"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    mob_text = MOB_PATH.read_text(encoding="utf-8")

    count = mob_text.count(OLD_ROW)
    if count != 1:
        raise SystemExit(f"ABORT [Decision Register row]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(OLD_ROW, NEW_ROW, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.205"
    version_new = "\\\\\\#\\\\\\# MOB v4.206"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.205 |"
    claude_new = "| MOB version | v4.206 |"
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
