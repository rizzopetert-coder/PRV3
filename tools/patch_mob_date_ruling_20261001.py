"""
Date ruling (Pete, 2026-10-01): PRV3 dates by the local clock (ET), consistent with the v4.330
closeout stamp. Every AMBIGUOUS item in the v4.332 correction note is correct as 2026-09-30 and
stays unchanged. MOB v4.332 -> v4.333.

  1. tools/_mob.txt: version header, the ruling line appended to the CORRECTION (MOB v4.331 ->
     v4.332) note in Section 16, the closing marker, and a Section 14 row for the standing date rule.
     v4.332 put no "pending ruling" line in the MOB (it is only in the untouched v4.332 handoff),
     so there is nothing to remove there.
  2. CLAUDE.md: MOB version cross-reference and the standing date rule in the Closeout Protocol.
  3. prompts/session-handoff-v4.333.md: new, extract of the v4.331 entry, the correction note and
     this ruling. Earlier handoffs are untouched.

Usage:
  python tools/patch_mob_date_ruling_20261001.py --dry-run
  python tools/patch_mob_date_ruling_20261001.py --write
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOB = ROOT / "tools" / "_mob.txt"
CLAUDE = ROOT / "CLAUDE.md"
HANDOFF = ROOT / "prompts" / "session-handoff-v4.333.md"

OLD_V, NEW_V = "v4.332", "v4.333"

RULING = (
    "Ruling (Pete, 2026-10-01): local clock (ET). The items listed as ambiguous are correct as 2026-09-30 and stay "
    "unchanged. Only the six re-dated items moved."
)

RULE_TEXT = (
    "Dates in MOB, spec and handoff entries come from git commit timestamps and the local clock (ET), stamped by Claude "
    "Code. Dates in Claude.ai prompts are not authoritative and are not copied into records."
)

SEC14_ROW = (
    "| **Dates in records come from git and the local clock (ET)** | LOCKED 2026-10-01, Pete. " + RULE_TEXT +
    " PRV3 dates by local clock, consistent with the v4.330 closeout stamp (22:23 EDT, 2026-09-30). Reason: Claude.ai "
    "stamped this session's rulings 2026-09-30 from the prior handoff's close date, see the Section 16 correction note. "
    "Also in CLAUDE.md, Closeout Protocol. | This session (Claude Code), 2026-10-01 | MOB v4.333 |"
)

CLAUDE_ANCHOR = (
    "When Pete says \"close session\", \"wrap up\", \"end session\", or similar, execute all steps in sequence without "
    "being prompted for each.\n"
)
CLAUDE_RULE = "\n**Date rule (Pete, 2026-10-01).** " + RULE_TEXT + "\n"

HANDOFF_FILES = """## Files to attach next session

- Quarterly Step-Back (due 2026-10-03): tools/_mob.txt, PRV3-Principal-Brief.docx. Input: the Output Precision question (Brief Section 10) against the 2026-09-28 Copy results lock.
- Severity follow-on gate (priority 1): engine/data/questions.py, engine/severity.py, engine/main.py, web/app/api/diagnostic/session/answer/route.ts, tools/diagnostic_question_audit.py, tools/_mob.txt.
- Pete's friction copy-register review: prompts/friction-tax-rebuild-build-spec.md (addendum section "Copy requiring Pete's review before any flag flip"), engine/contract.py, engine/friction_tax.py, web/lib/output-text.ts, web/components/ReportDetails.tsx, web/components/CondensedOutput.tsx.
- HR-DX overview doc update: Google Drive HR-DX-Overview and HR-DX-Methodology-Detail, prompts/friction-tax-rebuild-build-spec.md, prompts/friction-tax-rebuild-source-verification.md, engine/friction_tax.py.

## Time-anchored

- Quarterly Step-Back due 2026-10-03.
"""


def main():
    mode = "--write" if "--write" in sys.argv else "--dry-run"
    text = MOB.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)

    hv = [i for i, l in enumerate(lines) if l.strip() == r"\\\#\\\# MOB " + OLD_V]
    assert len(hv) == 1
    lines[hv[0]] = r"\\\#\\\# MOB " + NEW_V

    # Section 14 row after the expand/contract row
    ie = [i for i, l in enumerate(lines) if l.startswith("| **Cross-project payload changes use expand/contract**")]
    assert len(ie) == 1
    lines[ie[0] + 1:ie[0] + 1] = ["", SEC14_ROW]

    # ruling appended to the correction note, closing marker moved to v4.333
    while lines and lines[-1].strip() == "":
        lines.pop()
    assert lines[-1].strip() == f"MOB {OLD_V}.", lines[-1]
    ic = [i for i, l in enumerate(lines) if l.startswith("## CORRECTION (MOB v4.331 -> v4.332)")]
    assert len(ic) == 1
    lines[-1] = RULING
    lines.append("")
    lines.append(f"MOB {NEW_V}.")
    lines.append("")
    start = [i for i, l in enumerate(lines) if l.startswith("## SESSION CLOSEOUT (2026-09-30/10-01")]
    assert len(start) == 1
    new_text = nl.join(lines)
    entry_plus = "\n".join(lines[start[0]:]).rstrip("\n")

    ctext = CLAUDE.read_text(encoding="utf-8")
    assert f"| MOB version | {OLD_V} |" in ctext
    new_ctext = ctext.replace(f"| MOB version | {OLD_V} |", f"| MOB version | {NEW_V} |", 1)
    assert new_ctext.count(CLAUDE_ANCHOR) == 1, "closeout anchor"
    new_ctext = new_ctext.replace(CLAUDE_ANCHOR, CLAUDE_ANCHOR + CLAUDE_RULE, 1)

    handoff = (
        "# Session handoff, MOB v4.333 (extract of Section 16: the v4.331 entry, its correction note and the date ruling)\n\n"
        "Source: tools/_mob.txt Section 16, entry `SESSION CLOSEOUT (2026-09-30/10-01`, the `CORRECTION (MOB v4.331 -> v4.332)` "
        "note and its appended ruling. If this file and Section 16 ever differ, Section 16 is authoritative. Earlier handoffs "
        "(v4.331, v4.332) are unchanged, this file is complete on its own.\n\n"
        + entry_plus + "\n\n" + HANDOFF_FILES
    )

    new_texts = RULING + SEC14_ROW + CLAUDE_RULE
    print("semicolons in new text:", new_texts.count(";"), "| em-dashes:", new_texts.count("—"))
    print(f"MOB lines {len(text.splitlines())} -> {len(new_text.splitlines())}; handoff chars {len(handoff)}")
    if mode == "--write":
        MOB.write_text(new_text, encoding="utf-8")
        CLAUDE.write_text(new_ctext, encoding="utf-8")
        HANDOFF.write_text(handoff, encoding="utf-8")
        print("written")
    else:
        print("[dry-run] nothing written")


if __name__ == "__main__":
    main()
