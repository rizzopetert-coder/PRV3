r'''
Option (C), Pete 2026-09-28: hide friction-tax dollar figures on both brands
until the friction methodology is rebuilt. Legal exposure is unchanged.

One reversible switch, web layer: FRICTION_DOLLARS_VISIBLE in
web/lib/output-text.ts (false). The engine keeps computing and the payload is
unchanged. With the switch true, today's full dollar ledger returns.

While the switch is off, on screen and in Copy results:
  - the ledger heading reads "The answers behind these conditions"
  - each row (evidence grouping, 3 names + "and N more" unchanged) names its
    conditions, then the evidence lines. No figure.
  - the note "Conditions that rest on the same answers share a row." replaces
    both ledger footnotes (the methodology footnote is hidden)
  - the friction calculation steps are hidden
  - the cost comparison drops the friction line (the whole block is omitted
    when there is no priced legal exposure)

Engine, both brands: Call 1 and Call 2 system prompts gain the rule "Do not
state dollar figures or percentages of payroll." Call 3 is untouched (its hr-dx
prompt stays byte-identical, pinned in tools/test_phase1_report_data.py).

Usage (from repo root):
    python tools/patch_friction_dollars_hidden.py --dry-run
    python tools/patch_friction_dollars_hidden.py --write
    --root <dir>  apply against another checkout (verification worktree)
'''
import argparse
import difflib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
HEADING = "The answers behind these conditions"
NOTE = "Conditions that rest on the same answers share a row."
RULE = "Do not state dollar figures or percentages of payroll."
BANNED = {"em-dash": "—", "en-dash": "–", "double hyphen": "--", "semicolon": ";"}


def load_edits() -> tuple:
    ns = {"HEADING": HEADING, "NOTE": NOTE, "RULE": RULE}
    exec((HERE / "patch_friction_dollars_hidden_edits.py").read_text(encoding="utf-8"), ns)
    return ns["EDITS"], ns.get("NEW_FILES", {})


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = pathlib.Path(args.root).resolve()

    for label, text in (("heading", HEADING), ("note", NOTE), ("prompt rule", RULE)):
        hits = [n for n, ch in BANNED.items() if ch in text]
        print(f"[CHECK] {label} punctuation: {hits or 'clean'}")
        if hits:
            return 1

    out = {}
    edits_by_file, new_files = load_edits()
    for new_file, content in new_files.items():
        if (root / new_file).exists():
            print(f"[FAIL] {new_file} already exists")
            return 1
        out[new_file] = ("", content)
    for rel, edits in edits_by_file.items():
        src = (root / rel).read_text(encoding="utf-8")
        new = src
        for old, rep in edits:
            if new.count(old) != 1:
                print(f"[FAIL] {rel}: anchor found {new.count(old)} times: {old[:70]!r}")
                return 1
            new = new.replace(old, rep, 1)
        out[rel] = (src, new)
    for rel, (src, new) in out.items():
        if args.dry_run:
            sys.stdout.writelines(difflib.unified_diff(
                src.splitlines(True), new.splitlines(True), f"a/{rel}", f"b/{rel}"))
        else:
            (root / rel).write_text(new, encoding="utf-8")
            print(f"[WROTE] {rel}")
    if args.dry_run:
        print("\nDry run only, nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
