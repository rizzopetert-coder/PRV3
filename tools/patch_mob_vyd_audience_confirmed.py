"""
MOB update: Visualize Your Data audience-sequencing decision CONFIRMED by
Pete -- internal-only first (PrivateOutput.tsx), ShareableOutput.tsx
deferred to a separately-gated Phase 2. Resolves one of the two blockers
on the Decision Register row updated last pass (patch_mob_visualize_your_data_build_scope.py);
the remaining blocker is Layer 1's required Gemini architecture review,
not yet sent.

Version bump: v4.206 -> v4.207 (locked decision added).

Usage:
    python patch_mob_vyd_audience_confirmed.py --dry-run
    python patch_mob_vyd_audience_confirmed.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_BLOCKER = (
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
    "comparison) has been stated but not confirmed."
)

NEW_BLOCKER = (
    "(1) Layer 1 is a locked-contract change and requires its own "
    "Gemini architecture review before execution, per CLAUDE.md's "
    "Architectural Decisions rule -- not yet sent. Open question for "
    "that review: whether a purely additive VII.1 field needs an "
    "ENGINE_VERSION bump (currently 0.2.0) under the section's stated "
    "immutability rule. (2) Audience sequencing -- RESOLVED, Pete "
    "confirmed 2026-08-20: build PrivateOutput.tsx internal-only first; "
    "ShareableOutput.tsx and its P-13 framing deferred to a "
    "separately-gated Phase 2, not bundled into this build."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call -- not "
    "time-sensitive, no hard dependency on other open items. Candidate "
    "item for the ~August 23 Quarterly Step-Back's forward-planning "
    "discussion, but the audience-sequencing decision and the "
    "Gemini-review go-ahead can each move independently of the "
    "Step-Back if Pete wants to proceed sooner. |"
)

NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "send Layer 1 for Gemini review -- not time-sensitive, no hard "
    "dependency on other open items. Audience sequencing no longer a "
    "check-in item (resolved above). Still a candidate for the ~August "
    "23 Quarterly Step-Back's forward-planning discussion if Pete wants "
    "to fold it in, but can proceed independently before then. |"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    mob_text = MOB_PATH.read_text(encoding="utf-8")

    for label, old, new in [
        ("blocker column", OLD_BLOCKER, NEW_BLOCKER),
        ("tail (last touched / next check-in)", OLD_TAIL, NEW_TAIL),
    ]:
        count = mob_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        mob_text = mob_text.replace(old, new, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.206"
    version_new = "\\\\\\#\\\\\\# MOB v4.207"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.206 |"
    claude_new = "| MOB version | v4.207 |"
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
