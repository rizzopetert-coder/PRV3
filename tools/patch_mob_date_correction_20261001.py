"""
Date correction for the v4.331 closeout (MOB v4.331 -> v4.332).

Claude.ai stamped this session's rulings "2026-09-30", carrying the prior close date. Git commit
timestamps (local EDT) show the work spans the local midnight: baseline, R1-R6 addendum, Stage 1
and Stage 2 were committed 22:40-22:51 EDT on 2026-09-30 (02:40-02:51 UTC on 2026-10-01), and
Stage 3a onward on 2026-10-01 (08:34 EDT onward). Only occurrences that are unambiguously
2026-10-01 are re-dated here, each annotated in place. Occurrences in the ambiguous window are
left for Pete. The body of the v4.331 Section 16 entry is not edited, a correction note is
appended after it.

  1. tools/_mob.txt: version header, six in-place re-dates, the Copy results item (Step-Back
     routing), correction note appended after the v4.331 entry.
  2. CLAUDE.md: MOB version cross-reference, one in-place re-date.
  3. prompts/friction-tax-rebuild-build-spec.md: one in-place re-date.
  4. prompts/session-handoff-v4.332.md: new, extract of the v4.331 entry plus the correction note.
     prompts/session-handoff-v4.331.md is left untouched (handoffs are additive).

Usage:
  python tools/patch_mob_date_correction_20261001.py --dry-run
  python tools/patch_mob_date_correction_20261001.py --write
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOB = ROOT / "tools" / "_mob.txt"
CLAUDE = ROOT / "CLAUDE.md"
SPEC = ROOT / "prompts" / "friction-tax-rebuild-build-spec.md"
HANDOFF = ROOT / "prompts" / "session-handoff-v4.332.md"

OLD_V, NEW_V = "v4.331", "v4.332"
NOTE = "(date corrected from 2026-09-30, see Section 16)"
NOTE_MOB_RANGE = "(date corrected from 2026-09-30/10-01, see Section 16)"

# (file, line prefix, old substring, new substring), exactly one line and one occurrence each
MOB_REDATES = [
    ("- RESOLVED 2026-09-30/10-01 by the rebuild (R5)", "RESOLVED 2026-09-30/10-01 by the rebuild (R5)",
     f"RESOLVED 2026-10-01 {NOTE_MOB_RANGE} by the rebuild (R5)"),
    ("- RESOLVED 2026-09-30/10-01: the `PAYROLL_BASELINE_GRID` docstring", "RESOLVED 2026-09-30/10-01: the `PAYROLL",
     f"RESOLVED 2026-10-01 {NOTE_MOB_RANGE}: the `PAYROLL"),
    ("- RESOLVED 2026-09-30/10-01: `web/lib/output-renderer.ts` deleted", "RESOLVED 2026-09-30/10-01: `web/lib/output-r",
     f"RESOLVED 2026-10-01 {NOTE_MOB_RANGE}: `web/lib/output-r"),
    ("| \\\\\\*\\\\\\*Session 38\\\\\\*\\\\\\*", "**SUPERSEDED 2026-09-30 by the friction rebuild:",
     f"**SUPERSEDED 2026-10-01 {NOTE} by the friction rebuild:"),
    ("| **Cross-project payload changes use expand/contract**", "LOCKED 2026-09-30, Pete. prv-3 and prv3-engine deploy",
     f"LOCKED 2026-10-01 {NOTE}, Pete. prv-3 and prv3-engine deploy"),
]

COPY_PREFIX = "- Copy results carries 36 conditions with full prose"
COPY_OLD = (
    "Open question for Pete and Claude.ai: whether that length sits against the Brief's output-precision principle (the Brief "
    "was not available to Claude Code in this session, so that comparison was not made)."
)
COPY_NEW = (
    "Brief comparison answered 2026-10-01 (Claude.ai, from the Principal Brief, Section 10, Output Precision): PRV2's output "
    "was comprehensive, PRV3's output is precise, length is not depth, and a verdict naming one true thing beats a report "
    "naming nothing new. The 36-condition full-prose on-screen output, mirrored by the 2026-09-28 Copy results lock, is in "
    "tension with that principle. This is a principle-versus-lock question for Pete, routed to the 2026-10-03 Quarterly "
    "Step-Back as an input. Not a defect, and the item stays open."
)

CLAUDE_REDATE = (
    "  reads only the new one. Locked 2026-09-30, Pete, after the Stage 5 deploy race",
    "  reads only the new one. Locked 2026-10-01 (date corrected from 2026-09-30, see `tools/_mob.txt` Section 16), Pete, "
    "after the Stage 5 deploy race",
)
SPEC_REDATE = (
    "**Sequencing change (Pete, 2026-09-30): Stage 3a.**",
    "**Sequencing change (Pete, 2026-10-01, date corrected from 2026-09-30, see MOB Section 16): Stage 3a.**",
)

CORRECTION_NOTE = r"""## CORRECTION (MOB v4.331 -> v4.332), dated 2026-10-01

**What was wrong.** Pete flagged that Claude.ai stamped this session's rulings and decisions "2026-09-30" throughout its prompts, carrying over the prior session's close date. Claude.ai's error, anchoring on the prior handoff's date. The v4.331 entry and the records written from those prompts inherited it.

**What git shows (local EDT, the project's date convention: the v4.330 closeout was stamped 2026-09-30 for a 22:23 EDT commit).** The v4.330 closeout is 2026-09-30 22:23 EDT. This session's Legal baseline (`6c067fd`..`fc87f9a`), the spec addendum with rulings R1-R6 (`fb3323f`), Stage 1 (`7f31c4e`..`fdbc957`) and Stage 2 (`92b40b5`..`8330dac`) were committed 22:40 to 22:51 EDT on 2026-09-30, which is 02:40 to 02:51 UTC on 2026-10-01. Stage 3a onward (`060603b`, 08:34 EDT) and the v4.331 closeout (`92ea1a8`, 09:54 EDT) are 2026-10-01. So the session spans the local midnight, and the date depends on whether the local clock or UTC is used.

**Re-dated to 2026-10-01, each annotated in place "(date corrected from 2026-09-30, see Section 16)":**
- Section 14: the Session 38 row's SUPERSEDED annotation (Stage 4 commits are 09:11 EDT on 2026-10-01), and the expand/contract row (stated in the 2026-10-01 closeout prompt).
- Section 13b: the three RESOLVED items (`inaction_cost_*`, the `PAYROLL_BASELINE_GRID` docstring, `output-renderer.ts`), whose resolving commits are 2026-10-01. Their original "2026-09-30/10-01" range is also corrected.
- CLAUDE.md Engine Rules: the expand/contract rule.
- Spec addendum: the Stage 3a sequencing change (Pete's go came 2026-10-01).

**Read as 2026-10-01 in the v4.331 entry (body left unedited):** the Stage 3a resequencing, Stage 6 pulled ahead of Stage 5, the condensed intro copy approval, the accepted interpretation calls, the expand/contract rule, the ship dates of Stages 3a, 3, 4, 5 and 6, and the two UI-driven production sessions (already recorded as 2026-10-01 UTC).

**AMBIGUOUS, left unchanged for Pete to rule** (committed or given 22:40 to 22:51 EDT on 2026-09-30, 02:40 to 02:51 UTC on 2026-10-01): the spec addendum heading "Phase 0 corrections and rulings (Pete, 2026-09-30)" and the sentences that cite it (spec line 3, and the baseline "pushed 2026-09-30" line), the "W and q primary-source check (Claude Code, 2026-09-30)" heading and the sentence in Section 3 that says W and q were verified on 2026-09-30, and the Section 14 rows for the friction model (decisions 1-18 plus R3), the frozen Legal wage table (R1), the condensed single value (R2), plus the share row's "EXTENDED 2026-09-30 (R6)" annotation and the 13b pointer to "Section 14 rows dated 2026-09-30". If the project dates by local clock these are correct as written. If Pete rules UTC, they become 2026-10-01 and the same annotation applies. Rulings R1-R6 themselves were given about 22:45 EDT on 2026-09-30.

**Kept as 2026-09-30 (genuinely the prior session):** the verification doc and decisions 1-18, the build spec and Gemini clearance, the share fix `2e56044` and `8680886` and its original Section 14 row, the `4445210` deploy error, the Upstash check, the Geist check, and everything else dated by the v4.330 closeout.

**Step-Back input (2026-10-03).** The Principal Brief, Section 10, Output Precision: PRV2's output was comprehensive, PRV3's output is precise, length is not depth, and a verdict naming one true thing beats a report naming nothing new. The 36-condition full-prose on-screen output, mirrored by the 2026-09-28 Copy results lock (Section 14), is in tension with that principle. Principle versus lock, a question for Pete, not a defect. This answers the v4.331 note that the Brief was unavailable to Claude Code. Recorded in the 13b Copy results item.

MOB v4.332.
"""

HANDOFF_FILES = """## Files to attach next session

- Quarterly Step-Back (due 2026-10-03): tools/_mob.txt, PRV3-Principal-Brief.docx. Input: the Output Precision question (Brief Section 10) against the 2026-09-28 Copy results lock.
- Severity follow-on gate (priority 1): engine/data/questions.py, engine/severity.py, engine/main.py, web/app/api/diagnostic/session/answer/route.ts, tools/diagnostic_question_audit.py, tools/_mob.txt.
- Pete's friction copy-register review: prompts/friction-tax-rebuild-build-spec.md (addendum section "Copy requiring Pete's review before any flag flip"), engine/contract.py, engine/friction_tax.py, web/lib/output-text.ts, web/components/ReportDetails.tsx, web/components/CondensedOutput.tsx.
- HR-DX overview doc update: Google Drive HR-DX-Overview and HR-DX-Methodology-Detail, prompts/friction-tax-rebuild-build-spec.md, prompts/friction-tax-rebuild-source-verification.md, engine/friction_tax.py.

## Time-anchored

- Quarterly Step-Back due 2026-10-03.
- Pete to rule on the AMBIGUOUS date items in the correction note (local clock or UTC for 22:40 to 22:51 EDT on 2026-09-30).
"""


def line_edit(lines, prefix, old, new, label):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    assert len(hits) == 1, f"{label}: expected 1 line for prefix, got {len(hits)}"
    assert lines[hits[0]].count(old) == 1, f"{label}: substring count {lines[hits[0]].count(old)}"
    lines[hits[0]] = lines[hits[0]].replace(old, new)


def main():
    mode = "--write" if "--write" in sys.argv else "--dry-run"
    text = MOB.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)

    hv = [i for i, l in enumerate(lines) if l.strip() == r"\\\#\\\# MOB " + OLD_V]
    assert len(hv) == 1
    lines[hv[0]] = r"\\\#\\\# MOB " + NEW_V

    for prefix, old, new in MOB_REDATES:
        line_edit(lines, prefix, old, new, prefix[:40])
    line_edit(lines, COPY_PREFIX, COPY_OLD, COPY_NEW, "copy results")

    # the v4.331 entry's last line is "MOB v4.331." at the end of the file
    while lines and lines[-1].strip() == "":
        lines.pop()
    assert lines[-1].strip() == f"MOB {OLD_V}.", lines[-1]
    # slice start of the v4.331 entry for the handoff
    start = [i for i, l in enumerate(lines) if l.startswith("## SESSION CLOSEOUT (2026-09-30/10-01")]
    assert len(start) == 1
    lines.append("")
    lines.extend(CORRECTION_NOTE.rstrip("\n").split("\n"))
    lines.append("")
    new_text = nl.join(lines)
    entry_plus_note = "\n".join(lines[start[0]:])

    ctext = CLAUDE.read_text(encoding="utf-8")
    assert f"| MOB version | {OLD_V} |" in ctext
    new_ctext = ctext.replace(f"| MOB version | {OLD_V} |", f"| MOB version | {NEW_V} |", 1)
    assert new_ctext.count(CLAUDE_REDATE[0]) == 1
    new_ctext = new_ctext.replace(CLAUDE_REDATE[0], CLAUDE_REDATE[1], 1)

    stext = SPEC.read_text(encoding="utf-8")
    assert stext.count(SPEC_REDATE[0]) == 1
    new_stext = stext.replace(SPEC_REDATE[0], SPEC_REDATE[1], 1)

    handoff = (
        "# Session handoff, MOB v4.332 (extract of Section 16: the v4.331 entry plus its correction note)\n\n"
        "Source: tools/_mob.txt Section 16, entry `SESSION CLOSEOUT (2026-09-30/10-01` and the `CORRECTION (MOB v4.331 -> v4.332)` "
        "note directly after it. If this file and Section 16 ever differ, Section 16 is authoritative. "
        "prompts/session-handoff-v4.331.md is unchanged (handoffs are additive), this file is complete on its own.\n\n"
        + entry_plus_note.rstrip("\n") + "\n\n" + HANDOFF_FILES
    )

    new_texts = CORRECTION_NOTE + COPY_NEW + "".join(n for _, _, n in MOB_REDATES) + CLAUDE_REDATE[1] + SPEC_REDATE[1]
    print("semicolons in new text:", new_texts.count(";"), "| em-dashes:", new_texts.count("—"))
    print(f"MOB lines {len(text.splitlines())} -> {len(new_text.splitlines())}; handoff chars {len(handoff)}")
    if mode == "--write":
        MOB.write_text(new_text, encoding="utf-8")
        CLAUDE.write_text(new_ctext, encoding="utf-8")
        SPEC.write_text(new_stext, encoding="utf-8")
        HANDOFF.write_text(handoff, encoding="utf-8")
        print("written")
    else:
        print("[dry-run] nothing written")


if __name__ == "__main__":
    main()
