"""
MOB update: Visualize Your Data build arc CLOSED. Layer 3 SHIPPED, commit
4e42aea -- all three layers (1: 8f1cd93, 2: c4c447d, 3: 4e42aea) now
shipped, verified, committed. Feature complete internal-only
(PrivateOutput.tsx); ShareableOutput.tsx phase not started, deferred per
the standing audience decision (Pete confirmed 2026-08-20).

Layer 3: new Block 4c in PrivateOutput.tsx, one row per state in
severity_by_state -- name via primary_state/secondary_states lookup
(confirmed zero-gap), tier badge reusing severityAccentTokens() as-is
(rust/Endemic-only, matching locked visual identity), tier rendered as
literal text alongside its accent color (Pete's resolution -- mirrors the
primary-state badge, since color alone can't distinguish 3 tiers), fill
bar reflecting score_0_100's position within its tier band. Renders for
single-state results too (deliberate, real information not shown
elsewhere for a single-state result). Omitted entirely when
severity_by_state is absent/empty, same idiom as every other optional
block in this component.

Verified before commit: tsc clean, vitest unchanged from baseline (39/45,
same 6 pre-existing failures), git diff --stat confirmed
PrivateOutput.tsx the only file touched. Visually verified via two
temporary scratch routes (SSR HTML fetched directly, both deleted after,
zero trace in git status): first pass confirmed 4 states across all 3
tiers with bar-fill percentages hand-checked exact against the tier-band
formula; a follow-up pass specifically exercised the near-zero Emerging
case (score_0_100=0) after being asked to confirm rather than infer it --
renders a genuine 0% bar cleanly, explanatory note directly beneath it,
no errors.

Version bump: v4.211 -> v4.212 (workstream status materially changed --
feature build arc closed).

Usage:
    python patch_mob_vyd_layer3_closeout.py --dry-run
    python patch_mob_vyd_layer3_closeout.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "Layers 1-2 SHIPPED (commits 8f1cd93, c4c447d), Layer 3 not started | 3 |"
)
NEW_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "CLOSED, all 3 layers SHIPPED (commits 8f1cd93, c4c447d, 4e42aea), "
    "internal-only; ShareableOutput.tsx phase not started | 3 |"
)

OLD_STATUS_TAIL = (
    "session/resume/route.ts` and `dev/diagnostic-preview/route.ts` "
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
NEW_STATUS_TAIL = (
    "session/resume/route.ts` and `dev/diagnostic-preview/route.ts` "
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
    "ShareableOutput.tsx/CondensedOutput.tsx untouched by construction. "
    "**Layer 3, SHIPPED (commit 4e42aea) -- CLOSES THE BUILD ARC:** new "
    "Block 4c in PrivateOutput.tsx, one row per state in "
    "`severity_by_state`. Design confirmed against the real shipped "
    "shape before writing (Pete's three verification items): (1) name "
    "via a lookup built from `primary_state`/`secondary_states` -- "
    "confirmed zero-gap, both real builders derive them from the exact "
    "same `identified_states` array `severity_by_state` comes from; (2) "
    "omit-entirely idiom for the absent/empty case, matching `headline`/"
    "`observableIndicators`/`secondary_states` elsewhere in the same "
    "file; (3) tier badge reuses `severityAccentTokens()` as-is -- rust "
    "only for Endemic, slate for Emerging/Entrenched, matching locked "
    "visual identity rather than inventing a third color. Pete's own "
    "resolution on (3): tier renders as literal text inside the badge "
    "alongside its accent color (confirmed the primary-state badge one "
    "section above already does exactly this, mirrored exactly) -- "
    "color alone can't distinguish 3 tiers, text does. Fill bar reflects "
    "`score_0_100`'s position within its tier's band, mirroring "
    "`engine/severity.py`'s `classify_severity()` CALIBRATION TARGET "
    "default boundaries (0-33-66-100; confirmed live/unset at HEAD, not "
    "stale). Renders for single-state results too (one row), not gated "
    "to >=2 -- deliberate: score magnitude within tier is real "
    "information not shown elsewhere in the component for a single-state "
    "result, not literal spec adherence for its own sake. Verified "
    "before commit: tsc clean, vitest unchanged from baseline (39/45, "
    "same 6 pre-existing failures), git diff --stat confirmed "
    "PrivateOutput.tsx the only file touched. Visually verified via two "
    "temporary scratch routes (`web/app/dev/scratch-severity-check`, "
    "`...-check2` -- real SSR HTML fetched via curl, both deleted after, "
    "zero trace in git status; no chromium-cli/Playwright available in "
    "this environment, flagged rather than installing a browser stack "
    "unprompted): first pass, 4 states across all 3 tiers, every "
    "bar-fill percentage hand-checked exact against the tier-band "
    "formula, rust fired only on the Endemic row. Pete caught that this "
    "pass's lowest Emerging score (36.36%) wasn't actually a short bar "
    "-- follow-up pass specifically exercised score_0_100=0 (genuine "
    "floor) after being asked to confirm rather than infer it, rendering "
    "a clean 0% bar with the explanatory note directly beneath it, no "
    "errors. **Feature complete, internal-only.** ShareableOutput.tsx "
    "phase not started, deferred per the standing audience decision "
    "(Pete confirmed 2026-08-20)."
)

OLD_BLOCKER = (
    "(1) Layer 1 -- SHIPPED, commit 8f1cd93, 2026-08-20. Layer 2 -- "
    "SHIPPED, commit c4c447d, 2026-08-20. Both via the same Tier 1 "
    "mechanism: dry-run patch script -> diff + verification reviewed by "
    "Pete -> commit."
)
NEW_BLOCKER = (
    "(1) Layer 1 -- SHIPPED, commit 8f1cd93, 2026-08-20. Layer 2 -- "
    "SHIPPED, commit c4c447d, 2026-08-20. Layer 3 -- SHIPPED, commit "
    "4e42aea, 2026-08-20. All three via the same Tier 1 mechanism: "
    "dry-run patch script -> diff + verification reviewed by Pete -> "
    "commit. No blocker remaining on the internal-only build -- CLOSED."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "scope and start Layer 3 (PrivateOutput.tsx UI) -- not "
    "time-sensitive, no hard dependency on other open items. Still a "
    "candidate for the ~August 23 Quarterly Step-Back's forward-planning "
    "discussion if Pete wants to fold it in, but can proceed "
    "independently before then. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Closed, no forced "
    "check-in on the internal-only build. ShareableOutput.tsx phase is "
    "its own future consideration whenever Pete wants to open it -- not "
    "scheduled, not a candidate for the ~August 23 Quarterly Step-Back "
    "unless Pete chooses to raise it there. |"
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

    version_old = "\\\\\\#\\\\\\# MOB v4.211"
    version_new = "\\\\\\#\\\\\\# MOB v4.212"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.211 |"
    claude_new = "| MOB version | v4.212 |"
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
