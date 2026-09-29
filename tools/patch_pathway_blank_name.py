"""
Part X (NOT approved, review only) -- the "Resolution pathway" block renders
an empty service-name line when the engine found no routing
(resolution_family "" on both brands, diagnostic-completion.ts:189-193).
Minimal fix: render the name line only when there is a name. The heading
and Call 1's resolution_framing_text still render (Call 1 runs with an
empty family and still writes framing text). The orientation fallback copy
("The recommended next step is below...") is not reused here, since it
points "below" and this block IS the next step.

If Part C lands first, the copied text mirrors the same rule.

Usage (from repo root):
    python tools/patch_pathway_blank_name.py --dry-run [--with-copy-text]
    python tools/patch_pathway_blank_name.py --write   [--with-copy-text]
"""
import argparse
import difflib
import pathlib
import sys

PO = "web/components/PrivateOutput.tsx"
PO_OLD = (
    "        <p className=\"text-[13px] font-medium text-charcoal\">\n"
    "          {payload.resolution_family}\n"
    "        </p>\n"
)
PO_NEW = (
    "        {payload.resolution_family && (\n"
    "          <p className=\"text-[13px] font-medium text-charcoal\">\n"
    "            {payload.resolution_family}\n"
    "          </p>\n"
    "        )}\n"
)

OT = "web/lib/output-text.ts"
OT_OLD = "  const pathway = [`Resolution pathway: ${payload.resolution_family}`];\n"
OT_NEW = (
    "  const pathway = [\n"
    "    payload.resolution_family ? `Resolution pathway: ${payload.resolution_family}` : \"Resolution pathway:\",\n"
    "  ];\n"
)


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    ap.add_argument("--with-copy-text", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    root = pathlib.Path(args.root)
    edits = [(PO, PO_OLD, PO_NEW)]
    if args.with_copy_text:
        edits.append((OT, OT_OLD, OT_NEW))
    for rel, old, new in edits:
        src = (root / rel).read_text(encoding="utf-8")
        if src.count(old) != 1:
            print(f"[FAIL] {rel}: anchor found {src.count(old)} times"); return 1
        out = src.replace(old, new, 1)
        if args.dry_run:
            sys.stdout.writelines(difflib.unified_diff(
                src.splitlines(True), out.splitlines(True), f"a/{rel}", f"b/{rel}"))
        else:
            (root / rel).write_text(out, encoding="utf-8")
            print(f"[WROTE] {rel}")
    if args.dry_run:
        print("\nDry run only, nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
