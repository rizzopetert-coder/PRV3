"""
MOB update: log Pete's Phase 2 (ShareableOutput.tsx) design decisions for
Visualize Your Data into the EXISTING Decision Register row -- not a new
row, this is the same feature's Phase 2 status changing from "not
started, audience deferred" to "design direction decided, still not
started, no urgency." Decision-logging pass only, no code changes, no
scope doc yet.

Also folds in confirmation of the real Playwright/Chromium screenshot
verification (Pete-approved, same session) as a closing note on the
Layer 3 build's own visual-verification trail.

Version bump: v4.218 -> v4.219 (workstream status materially changed --
new locked design decisions for a deferred phase).

Usage:
    python patch_mob_vyd_phase2_design_decision.py --dry-run
    python patch_mob_vyd_phase2_design_decision.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "CLOSED, all 3 layers SHIPPED (commits 8f1cd93, c4c447d, 4e42aea), "
    "internal-only; ShareableOutput.tsx phase not started | 3 |"
)
NEW_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "CLOSED internal-only (all 3 layers SHIPPED, commits 8f1cd93, c4c447d, "
    "4e42aea); Phase 2 (ShareableOutput.tsx) DESIGN DIRECTION DECIDED, "
    "still not started, no urgency | 3 |"
)

OLD_BLOCKER_TAIL = (
    "(2) Audience sequencing -- RESOLVED, Pete confirmed 2026-08-20: "
    "build PrivateOutput.tsx internal-only first; ShareableOutput.tsx "
    "and its P-13 framing deferred to a separately-gated Phase 2, not "
    "bundled into this build."
)
NEW_BLOCKER_TAIL = (
    "(2) Audience sequencing -- RESOLVED, Pete confirmed 2026-08-20: "
    "build PrivateOutput.tsx internal-only first; ShareableOutput.tsx "
    "and its P-13 framing deferred to a separately-gated Phase 2, not "
    "bundled into this build. (3) Phase 2 design direction -- DECIDED, "
    "not built, Pete confirmed 2026-08-20: three decisions. First, "
    "per-state severity comparison is understood as an internal/"
    "advisory-conversation artifact, not a passive unmediated reveal -- "
    "the shareable version is something a Principal encounters WITH "
    "guidance (an advisor walking them through it), not a cold read "
    "alone. Second, the shareable surface gets a stripped-down version: "
    "tier only, no score_0_100 magnitude bar -- but it must still carry "
    "real value, not be a token gesture. Open design question for later, "
    "explicitly not resolved now: what makes a tier-only comparison "
    "genuinely still valuable without the magnitude signal -- does row "
    "order still carry information, does the Emerging-floor "
    "explanatory note still apply, does it need its own P-13 \"how to "
    "read this\" framing given the reduced-context audience. Third, the "
    "feature is closed for now at this decision -- no build urgency, "
    "this was a scoping/logging pass only. No scope doc written yet; "
    "this MOB entry is the durable record for a future session to pick "
    "up from, not starting from scratch. **Real Playwright/Chromium "
    "screenshot verification, Pete-approved, this session:** closes the "
    "visual-verification gap flagged at Layer 3's original commit (SSR-"
    "HTML-fetch proof used then in lieu of a screenshot, no browser "
    "tooling available). Installed Playwright + Chromium as a web/ dev "
    "dependency, rendered PrivateOutput against a 5-state payload "
    "covering all three severity tiers in one shot (Emerging, "
    "Entrenched, Endemic all visible, including a near-floor Emerging "
    "bar), captured a full-page PNG showing Block 1 hero through Block "
    "4c in context, zero console errors. Scratch route, driver script, "
    "and screenshot all deleted after, confirmed via git status clean. "
    "Playwright/Chromium dependency itself (web/package.json, "
    "web/package-lock.json) left uncommitted pending Pete's call on "
    "whether to keep it as a standing dev dependency."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Closed, no forced "
    "check-in on the internal-only build. ShareableOutput.tsx phase is "
    "its own future consideration whenever Pete wants to open it -- not "
    "scheduled, not a candidate for the ~August 23 Quarterly Step-Back "
    "unless Pete chooses to raise it there. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Closed, no forced "
    "check-in on the internal-only build or on Phase 2's design "
    "direction. Phase 2 build itself is its own future consideration "
    "whenever Pete wants to open it -- not scheduled, no urgency, not a "
    "candidate for the ~August 23 Quarterly Step-Back unless Pete "
    "chooses to raise it there. Separately: Pete's call on whether to "
    "keep Playwright/Chromium as a standing web/ dev dependency or "
    "revert the package.json/package-lock.json change. |"
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
        ("blocker tail", OLD_BLOCKER_TAIL, NEW_BLOCKER_TAIL),
        ("tail (last touched / next check-in)", OLD_TAIL, NEW_TAIL),
    ]:
        count = mob_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        mob_text = mob_text.replace(old, new, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.218"
    version_new = "\\\\\\#\\\\\\# MOB v4.219"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.218 |"
    claude_new = "| MOB version | v4.219 |"
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
