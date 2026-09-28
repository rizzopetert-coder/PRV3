"""
Pin maxDuration = 60 on the two prv-3 web routes that can run the full
completion path (session/answer at the last question, session/narrative when
the narrative fires at Q34). Neither set a maxDuration, so both ran on the
unverified platform default. Engine worst case is 45s (Call 1 || Call 2 at
30s, then Call 3 at 15s). prv3-engine's own 300s (root vercel.json) is left
unchanged, per Pete.

Usage:
    python tools/patch_session_routes_maxduration.py --dry-run
    python tools/patch_session_routes_maxduration.py --write
"""
import argparse
import pathlib
import sys

ANCHOR = "export async function POST(request: NextRequest) {"

EDITS = {
    pathlib.Path("web/app/api/diagnostic/session/answer/route.ts"): (
        "// Completion runs Call 1 || Call 2 (30s) then Call 3 (15s), worst case 45s\n"
        "// engine-side, plus the TC question-copy fetches. Pinned, not left to the default.\n"
        "export const maxDuration = 60;\n\n"
    ),
    pathlib.Path("web/app/api/diagnostic/session/narrative/route.ts"): (
        "// Can run the full completion path when the narrative fires at Q34.\n"
        "export const maxDuration = 60;\n\n"
    ),
}


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    args = ap.parse_args()

    ok = True
    staged = {}
    for path, block in EDITS.items():
        text = path.read_text(encoding="utf-8")
        if "export const maxDuration" in text:
            print(f"[SKIP] {path}: maxDuration already present")
            ok = False
            continue
        if text.count(ANCHOR) != 1:
            print(f"[FAIL] {path}: anchor found {text.count(ANCHOR)} times, expected 1")
            ok = False
            continue
        staged[path] = text.replace(ANCHOR, block + ANCHOR, 1)
        print(f"[OK]   {path}: insert before POST handler")
        print("       + " + block.rstrip("\n").replace("\n", "\n       + "))

    if not ok:
        print("Aborting, nothing written.")
        return 1
    if args.write:
        for path, new in staged.items():
            path.write_text(new, encoding="utf-8")
            print(f"[WROTE] {path}")
    else:
        print("Dry run only, nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
