r'''
Session closeout 2026-09-28/29 -- MOB v4.328 -> v4.329.

  tools/_mob.txt
    - header version
    - Section 13b rewritten wholesale (numbered priorities 1-5 unchanged,
      unchanged open items and the infrastructure / parked / closed-since
      blocks carried verbatim from the current text, prior-session CLOSED
      lines dropped since Section 16 records them)
    - Section 14: 7 locked rows added after the effective_resolution_family
      row, and the Session 38 severity-scalar lock marked REOPENED (not deleted)
    - Section 16: closeout entry appended
  CLAUDE.md: MOB version cross-reference
  prompts/session-handoff-v4.329.md: new, derived from the Section 16 entry

Usage (from repo root):
    python tools/patch_mob_session_closeout_20260929.py --dry-run
    python tools/patch_mob_session_closeout_20260929.py --write
'''
import argparse
import difflib
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
MOB = pathlib.Path("tools/_mob.txt")
CLAUDE = pathlib.Path("CLAUDE.md")
HANDOFF = pathlib.Path("prompts/session-handoff-v4.329.md")


def main() -> int:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--write", action="store_true")
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    ns = {}
    for part in ("text", "s16", "handoff"):  # split for size: 13b + Section 14, Section 16, handoff
        exec((HERE / f"patch_mob_session_closeout_20260929_{part}.py").read_text(encoding="utf-8"), ns)

    mob = MOB.read_text(encoding="utf-8")
    lines = mob.split("\n")

    def find(prefix, start=0):
        hits = [i for i in range(start, len(lines)) if lines[i].startswith(prefix)]
        if len(hits) != 1:
            raise SystemExit(f"[FAIL] {len(hits)} lines start with {prefix[:60]!r}")
        return hits[0]

    # ── 13b ──
    i_start = find("Priority order for next session, in sequence.")
    i_open = find("Open, not sequenced -- real items")
    i_infra = find("Infrastructure carry-forwards, tracked only in Section 16")
    i_parked = find("Explicitly parked, do not resurface unless Pete reopens:")
    i_closed = find("Closed since the 2026-09-07 rewrite")
    i_files = find("Files to attach next session, categorized by likely next task:")
    i_last = find("Last updated: This session (Claude Code), 2026-09-27/28")
    assert i_start < i_open < i_infra < i_parked < i_closed < i_files < i_last

    numbered = [l for l in lines[i_start + 1:i_open] if l.strip()]
    assert [l[:3] for l in numbered] == ["1. ", "2. ", "3. ", "4. ", "5. "], numbered
    old_open = lines[i_open + 1:i_infra]
    old_files = lines[i_files + 1:i_last]

    def old_item(prefix, pool):
        hits = [l for l in pool if l.startswith(prefix)]
        if len(hits) != 1:
            raise SystemExit(f"[FAIL] {len(hits)} old 13b lines start with {prefix!r}")
        return hits[0]

    kept_open = [old_item(p, old_open) for p in ns["KEEP_OPEN_PREFIXES"]]
    kept_open.append("- " + old_item("  - `web/lib/diagnostic-completion.ts` `[DIAG] synthesis fallback` log", old_open).lstrip(" -"))
    infra = [l for l in lines[i_infra:i_parked] if not l.startswith("- CLOSED")]
    parked = lines[i_parked:i_closed]
    closed_since = lines[i_closed:i_files]
    kept_files = [old_item(p, old_files) for p in ns["KEEP_FILE_PREFIXES"]]

    new_13b = (
        [ns["NUMBERED_HEADER"], ""] + numbered + [""]
        + [lines[i_open]] + ns["NEW_OPEN"] + kept_open + ns["CLOSED_IN_PLACE"] + [""]
        + infra + parked + closed_since
        + [lines[i_files]] + ns["NEW_FILES_TO_ATTACH"] + kept_files + [""]
        + [ns["LAST_UPDATED"]]
    )
    lines[i_start:i_last + 1] = new_13b

    # ── Section 14: new rows after the effective_resolution_family row ──
    i_row = find("| **Pathway, Call 1 and backup copy all read effective_resolution_family**")
    rows = []
    for r in ns["SECTION_14_ROWS"]:
        rows += ["", r]
    lines[i_row + 1:i_row + 1] = rows

    new_mob = "\n".join(lines)

    # Session 38 severity-scalar lock: REOPENED marker, row kept
    anchor = "high=low*1.4 range spread LOCKED."
    if new_mob.count(anchor) != 1:
        raise SystemExit(f"[FAIL] severity-scalar anchor found {new_mob.count(anchor)} times")
    new_mob = new_mob.replace(anchor, anchor + " " + ns["REOPENED_MARKER"], 1)

    # header version
    hdr = "\\\\\\#\\\\\\# MOB v4.328"
    if new_mob.count(hdr) != 1:
        raise SystemExit(f"[FAIL] header anchor found {new_mob.count(hdr)} times")
    new_mob = new_mob.replace(hdr, "\\\\\\#\\\\\\# MOB v4.329", 1)

    # Section 16 entry
    if not new_mob.rstrip("\n").endswith("MOB v4.328."):
        raise SystemExit("[FAIL] MOB does not end with the v4.328 closeout line")
    new_mob = new_mob.rstrip("\n") + "\n\n" + ns["SECTION_16"].rstrip("\n") + "\n"

    claude = CLAUDE.read_text(encoding="utf-8")
    old_v = "| MOB version | v4.328 |"
    if claude.count(old_v) != 1:
        raise SystemExit("[FAIL] CLAUDE.md version anchor")
    new_claude = claude.replace(old_v, "| MOB version | v4.329 |", 1)

    if HANDOFF.exists():
        raise SystemExit(f"[FAIL] {HANDOFF} already exists")

    out = {MOB: (mob, new_mob), CLAUDE: (claude, new_claude), HANDOFF: ("", ns["HANDOFF"])}
    for path, (a, b) in out.items():
        if args.dry_run:
            sys.stdout.writelines(difflib.unified_diff(
                a.splitlines(True), b.splitlines(True), f"a/{path.as_posix()}", f"b/{path.as_posix()}", n=1))
        else:
            path.write_text(b, encoding="utf-8")
            print(f"[WROTE] {path.as_posix()}")
    if args.dry_run:
        print("\nDry run only, nothing written.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
