"""
PRV3 -- Report Depth Initiative Tier 1, follow-up fix.

tsc caught a third PrivateOutputPayload-shaped type after the main Tier 1
patch landed: DevDiagnosticPreviewPayload (web/lib/dev-diagnostic-preview.ts),
the diagnostic fast-forward tool's dev-only viewer type -- deliberately a
SEPARATE interface from PrivateOutputPayload (not a re-export), with "the
same field shapes" by design so it renders through the same <PrivateOutput>
component (confirmed: app/dev/diagnostic-preview/[id]/page.tsx passes it
directly as the `payload` prop, which is typed PrivateOutputPayload --
that's the actual compile error). My earlier grep for the literal string
"PrivateOutputPayload" as a builder search didn't surface this, since it's
a structurally-similar but separately-named type.

Traced the data flow before writing anything: tools/diagnostic_fast_forward.py
POSTs `result = answer_resp["result"]` verbatim to /api/dev/diagnostic-preview
-- the raw JSON body already returned by the live session/answer route at
completion (i.e. the real, already-updated PrivateOutputPayload with
primary_asset_domain included). Zero field whitelisting on the Python side,
confirmed by direct read -- so no Python change is needed; the field will
already be present in what gets POSTed once answer/route.ts's response
includes it (already true from the main Tier 1 commit).

Two files, matching the new field's required (non-optional) status:
  1. web/lib/dev-diagnostic-preview.ts -- DevDiagnosticPreviewPayload gains
     primary_asset_domain: string (required, matching PrivateOutputPayload).
  2. web/app/api/dev/diagnostic-preview/route.ts -- validatePayload() gains
     the corresponding runtime check, matching its existing per-field
     validation convention.

Usage:
  python tools/patch_report_depth_tier1_devpreview_fix.py --dry-run
  python tools/patch_report_depth_tier1_devpreview_fix.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
DEV_PREVIEW_LIB_FILE = REPO_ROOT / "web" / "lib" / "dev-diagnostic-preview.ts"
DEV_PREVIEW_ROUTE_FILE = REPO_ROOT / "web" / "app" / "api" / "dev" / "diagnostic-preview" / "route.ts"

EDITS: list[tuple[Path, str, str, str]] = []

EDITS.append((
    DEV_PREVIEW_LIB_FILE,
    "dev-diagnostic-preview.ts: DevDiagnosticPreviewPayload.primary_asset_domain",
    '''  intake: IntakeEcho;
  dimension_summary: DimensionSummary;
}''',
    '''  intake: IntakeEcho;
  dimension_summary: DimensionSummary;
  primary_asset_domain: string;
}''',
))

EDITS.append((
    DEV_PREVIEW_ROUTE_FILE,
    "dev/diagnostic-preview/route.ts: validatePayload() checks primary_asset_domain",
    '''    typeof b.intake === "object" && b.intake !== null &&
    typeof b.dimension_summary === "object" && b.dimension_summary !== null
  );''',
    '''    typeof b.intake === "object" && b.intake !== null &&
    typeof b.dimension_summary === "object" && b.dimension_summary !== null &&
    typeof b.primary_asset_domain === "string"
  );''',
))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts: dict[Path, str] = {}
    for path in {e[0] for e in EDITS}:
        file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in EDITS:
        count = file_texts[path].count(old)
        if count != 1:
            print(f"ABORT -- anchor for '{label}' matched {count} times in {path.relative_to(REPO_ROOT)}, need exactly 1", file=sys.stderr)
            sys.exit(1)

    print("=" * 100)
    for path, label, old, new in EDITS:
        print(f"\n--- {label} ({path.relative_to(REPO_ROOT)}) ---")
        print("BEFORE:")
        print(old)
        print("AFTER:")
        print(new)
    print("\n" + "=" * 100)

    new_texts: dict[Path, str] = dict(file_texts)
    for path, label, old, new in EDITS:
        new_texts[path] = new_texts[path].replace(old, new, 1)

    print("Files touched:")
    for path in file_texts:
        delta = len(new_texts[path]) - len(file_texts[path])
        print(f"  {path.relative_to(REPO_ROOT)}: {delta:+d} chars")

    print("\ntools/diagnostic_fast_forward.py confirmed NOT touched -- pure passthrough,")
    print("already forwards whatever answer/route.ts returns, verified by direct read.")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    for path, text in new_texts.items():
        path.write_text(text, encoding="utf-8")
        print(f"\nWROTE {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
