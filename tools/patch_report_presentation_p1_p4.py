r'''
Part P -- report presentation fixes (Pete-approved 2026-09-28).

  P1  Drop the "Primary asset domain: X" line (screen and Copy results). The
      payload field stays: it is part of the engine contract's asset_score
      block (contract.py _ASSET_SCORE_FIELDS, tools/test_contract.py) and is
      read by Path B, the dev preview and the fixture picker.
  P2  Friction tax ledger: rows citing an identical evidence set are grouped
      into one row that names every condition, shows the highest standalone
      estimate in the group (stated as such), and the shared evidence once.
      Rows with no evidence are never grouped. A new ledger note says rows
      are standalone and do not add up to the total. Screen and copy share
      groupLedgerRows() and the note constant.
  P3  Receipt evidence ranks problem/neutral answers on *_liability
      contributions only, and quotes an answer only when its weight reaches
      _RECEIPT_EVIDENCE_MIN_WEIGHT (0.20). When no unused answer clears it,
      the "Based on your answers" line is omitted (no more reuse fallback).
  P4  Legal "Total" receipt wording is accurate for any number of conditions.
  A1  Every dollar figure shown to the nearest $1,000 (display only).
  A2  Grouped ledger rows on screen: 3 names, then "and N more".
  A3  Ledger evidence ranks on *_liability only, zero-weight answers out.
  (A1-A3 live in patch_report_presentation_p1_p4_edits_3.py.)

Usage (from repo root):
    python tools/patch_report_presentation_p1_p4.py --dry-run
    python tools/patch_report_presentation_p1_p4.py --write
    --root <dir>  apply against another checkout (verification worktree)
'''
import argparse
import difflib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
LEDGER_NOTE = (
    "Each row estimates what that condition would cost on its own. Conditions "
    "that rest on the same answers share a row, which shows the highest of their "
    "individual estimates. The rows do not add up to the friction tax total, "
    "because the total counts overlapping conditions at decreasing weight rather "
    "than adding them in full."
)
LEGAL_TOTAL_NEW_TEXT = (
    "Within a category, the largest exposure counts in full and each additional "
    "one counts at half the weight of the one before it. Categories are then "
    "added together."
)
BANNED = {"em-dash": "—", "en-dash": "–", "double hyphen": "--", "semicolon": ";"}


def split_words(text: str, width: int = 76) -> list:
    parts, cur = [], ""
    for word in text.split(" "):
        piece = word if not cur else " " + word
        if cur and len(cur) + len(piece) > width:
            parts.append(cur + " ")
            cur = word
        else:
            cur += piece
    parts.append(cur)
    assert "".join(parts) == text
    return parts


def ts_concat(text: str) -> str:
    return " +\n".join(f'  "{p}"' for p in split_words(text))


def py_concat(text: str, indent: str) -> str:
    return "\n".join(f'{indent}"{p}"' for p in split_words(text))


def load_edits() -> dict:
    """The anchor/replacement pairs live in two data files next to this script
    (engine + copy text, then screen + tests), executed into one namespace."""
    ns = {"ts_concat": ts_concat, "py_concat": py_concat,
          "LEDGER_NOTE": LEDGER_NOTE, "LEGAL_TOTAL_NEW_TEXT": LEGAL_TOTAL_NEW_TEXT}
    for name in ("patch_report_presentation_p1_p4_edits.py", "patch_report_presentation_p1_p4_edits_2.py",
                 "patch_report_presentation_p1_p4_edits_3.py"):
        exec((HERE / name).read_text(encoding="utf-8"), ns)
    return ns["EDITS"]


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    ap.add_argument("--root", default=".")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    root = pathlib.Path(args.root)

    for label, text in (("ledger note", LEDGER_NOTE), ("legal Total", LEGAL_TOTAL_NEW_TEXT)):
        hits = [n for n, ch in BANNED.items() if ch in text]
        print(f"[CHECK] {label} punctuation: {hits or 'clean'}")
        if hits:
            return 1

    out = {}
    for rel, edits in load_edits().items():
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
