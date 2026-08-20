"""
MOB update: Visualize Your Data Layer 1 SHIPPED, commit 8f1cd93.

severity_obj gains "by_state" (engine/contract.py's assemble_output()),
ENGINE_VERSION 0.2.0 -> 0.2.1. Dry-run patch script
(tools/patch_visualize_your_data_layer1.py) applied and verified before
commit: full 172(+3)-profile calibration regression byte-identical
(171/175, same 4 pre-existing failures), tools/test_contract.py's
"Exactly 16 top-level fields" assertion re-verified passing, tsc clean,
diff scoped to engine/contract.py only (git diff --stat confirmed).

Pre-commit housekeeping check, also folded in: two unrelated working-tree
items Pete flagged before allowing the commit turned out to be non-issues.
web/content/book/methodology/hr-capture.md's "M" status is pure CRLF/LF
line-ending drift (core.autocrlf, git ls-files --eol confirmed i/lf w/crlf,
git diff byte count 0) predating this session, not a real content change.
The untracked .docx files are NOT outside the repo -- they sit at
PRV3/documents/ (8 files, not 3, all timestamped identically 2026-07-22,
predating this session by a month); the earlier "../documents/" framing
was an artifact of running git status from within web/, not anything
unusual about the files themselves. Neither item touched by this commit.

Version bump: v4.209 -> v4.210 (workstream status materially changed --
Layer 1 shipped).

Usage:
    python patch_mob_vyd_layer1_shipped.py --dry-run
    python patch_mob_vyd_layer1_shipped.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "Layer 1 build spec verified and drafted, not yet built | 3 |"
)
NEW_TITLE = (
    "| \"Visualize your data\" per-state severity comparison section -- "
    "Layer 1 SHIPPED (commit 8f1cd93), Layers 2-3 not started | 3 |"
)

OLD_BLOCKER = (
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
NEW_BLOCKER = (
    "(1) Layer 1 -- SHIPPED, commit 8f1cd93, 2026-08-20. Tier 1 "
    "mechanism completed in full: dry-run patch script "
    "(tools/patch_visualize_your_data_layer1.py) -> diff + verification "
    "reviewed by Pete -> commit. Verification, real not assumed: full "
    "172(+3)-profile calibration regression byte-identical (171/175, "
    "same 4 pre-existing moderate-tier failures: identity_erosion, "
    "invisible_burnout, leadership_deafness, the_untouchable), "
    "SEVERITY 175/175 unchanged; tools/test_contract.py's \"Exactly 16 "
    "top-level fields\" assertion (line 178) re-run and confirmed still "
    "passing (140/140, 0 failed); tsc clean; git diff --stat confirmed "
    "engine/contract.py the only file touched, zero TypeScript. Pre-commit, "
    "Pete flagged two unrelated working-tree items for a check before "
    "allowing the commit -- both resolved as non-issues, neither touched: "
    "web/content/book/methodology/hr-capture.md's \"M\" status is pure "
    "CRLF/LF line-ending drift (core.autocrlf, git diff byte count 0), "
    "predating this session; the untracked .docx files are not outside "
    "the repo (they sit at PRV3/documents/, 8 files not 3, apparent "
    "single-batch export timestamped 2026-07-22) -- the \"outside the "
    "repo\" appearance was an artifact of running git status from "
    "within web/, not anything unusual. Committed with `git add "
    "engine/contract.py` explicitly, not a broad add. (2) Audience "
    "sequencing -- RESOLVED, Pete confirmed 2026-08-20: build "
    "PrivateOutput.tsx internal-only first; ShareableOutput.tsx and its "
    "P-13 framing deferred to a separately-gated Phase 2, not bundled "
    "into this build."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "greenlight the Layer 1 dry-run build -- not time-sensitive, no hard "
    "dependency on other open items. Neither audience sequencing nor "
    "the Gemini review are check-in items any longer (both resolved "
    "above). Still a candidate for the ~August 23 Quarterly Step-Back's "
    "forward-planning discussion if Pete wants to fold it in, but can "
    "proceed independently before then. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "scope and start Layer 2 (wire plumbing) and Layer 3 (PrivateOutput.tsx "
    "UI) -- not time-sensitive, no hard dependency on other open items. "
    "Still a candidate for the ~August 23 Quarterly Step-Back's "
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
        ("blocker column", OLD_BLOCKER, NEW_BLOCKER),
        ("tail (last touched / next check-in)", OLD_TAIL, NEW_TAIL),
    ]:
        count = mob_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        mob_text = mob_text.replace(old, new, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.209"
    version_new = "\\\\\\#\\\\\\# MOB v4.210"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.209 |"
    claude_new = "| MOB version | v4.210 |"
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
