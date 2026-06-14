"""
PRV3 MOB patch — v4.7 to v4.8
Session 42: service name rename, open items, registry, session log.

Usage:
  python tools/patch_mob_v48.py --dry-run
  python tools/patch_mob_v48.py --write
"""

import sys
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
DRY_RUN = "--write" not in sys.argv


def run():
    original = MOB_PATH.read_text(encoding="utf-8")
    content = original

    # ── 1. Version bump ────────────────────────────────────────────────────────
    content = content.replace("MOB v4.7", "MOB v4.8")

    # ── 2. Service name replacements ───────────────────────────────────────────
    # Formation → Groundwork (commercial only — no engine ambiguity)
    content = content.replace("Formation", "Groundwork")
    # Practicum → Development (commercial only — no engine ambiguity)
    content = content.replace("Practicum", "Development")
    # Navigation (capital N) → Advisory (lowercase "navigation" in descriptions unaffected)
    content = content.replace("Navigation", "Advisory")
    # Counsel → First Call — protect "Executive Counsel" (engine term) first
    content = content.replace("Executive Counsel", "__EXEC_COUNSEL__")
    content = content.replace("Counsel", "First Call")
    content = content.replace("__EXEC_COUNSEL__", "Executive Counsel")

    # ── 3. Open items additions ────────────────────────────────────────────────
    # Insert two new rows after the ENGINE DEBT row in Section 12.
    ENGINE_DEBT_ANCHOR = "Deferred to Phase 3. ENGINE DEBT. |"
    NEW_OPEN_ITEMS = (
        "\n\n"
        "| Commercial site service descriptions |"
        " Service descriptions on the commercial site (Session 34) still reference"
        " Formation, Practicum, Counsel, Navigation."
        " Update to Groundwork, Development, First Call, Advisory."
        " Not blocking current work. |"
        "\n\n"
        "| Copy rule — human register signals |"
        " Occasional human register signals are permitted and intentional in client-facing copy."
        " A moment of directness or warmth that breaks from the clinical register can signal"
        " human connection when used sparingly. It is not a lapse. Evaluate per instance. |"
    )
    assert ENGINE_DEBT_ANCHOR in content, "OPEN ITEMS anchor not found"
    content = content.replace(ENGINE_DEBT_ANCHOR, ENGINE_DEBT_ANCHOR + NEW_OPEN_ITEMS, 1)

    # ── 4. Document registry additions ────────────────────────────────────────
    # Insert three new entries before the GitHub sync section in Section 15.
    GITHUB_SYNC_ANCHOR = "GitHub sync scope (locked Session 5)"
    assert GITHUB_SYNC_ANCHOR in content, "REGISTRY anchor not found"
    NEW_REGISTRY = (
        r"| \*\*PRV3\_Resolution\_Families\_Copy\_v3.0.docx\*\* |"
        " Static fallback copy for four resolution services keyed by"
        " (commercial name, severity tier). Engine-to-commercial name mapping."
        " Copy standard and standing copy rules. Produced S42."
        " Source for RESOLUTION\\_FALLBACK\\_COPY in engine/resolution\\_families.py. |"
        "\n\n"
        r"| \*\*PRV3\_Output\_Synthesis\_Prompts\_v1.0.docx\*\* |"
        " System prompt and five field-level prompt specifications for"
        " output\\_synthesis.py single LLM call."
        " Context object definition and fallback priority order. Produced S42. |"
        "\n\n"
        r"| \*\*prompts/gemini-s42-synthesis-handoff.md\*\* |"
        " Gemini review request for output\\_synthesis.py 5-field contract migration."
        " Five review questions. Cascade file inventory. S42. |"
        "\n\n"
    )
    content = content.replace(GITHUB_SYNC_ANCHOR, NEW_REGISTRY + GITHUB_SYNC_ANCHOR, 1)

    # ── 5. Session 42 log entry ───────────────────────────────────────────────
    # Append after the Session 41 entry (last line of the file).
    S42_LOG = (
        "\n\n"
        r"| \*\*June 2026 — Session 42\*\* |"
        " Service names renamed (locked Session 42, supersedes Session 32 lock):"
        " Formation→Groundwork, Practicum→Development,"
        " Counsel→First Call, Navigation→Advisory."
        " MOB updated throughout. Copy rule confirmed: occasional human register signals"
        " are intentional, not a lapse, evaluate per instance."
        " engine/resolution\\_families.py: ENGINE\\_TO\\_COMMERCIAL\\_NAME mapping,"
        " translate\\_resolution\\_family() helper,"
        " RESOLUTION\\_FALLBACK\\_COPY dict (12 single-service + 7 compound entries"
        " from PRV3\\_Resolution\\_Families\\_Copy\\_v3.0.docx), get\\_fallback\\_copy() helper."
        " 101/101 resolution family tests. engine/data/states.py:"
        " the\\_exposed resolution\\_family corrected from"
        " \\u201cIntervention + Stability Support\\u201d to"
        " \\u201cIntervention + Executive Counsel\\u201d (PRV2 residue)."
        " PRV3\\_Resolution\\_Families\\_Copy\\_v3.0.docx and"
        " PRV3\\_Output\\_Synthesis\\_Prompts\\_v1.0.docx added to registry."
        " output\\_synthesis.py 5-field contract migration — Gemini review in progress,"
        " deferred to next session. MOB updated to v4.8. |"
    )
    content = content.rstrip() + S42_LOG + "\n"

    # ── Summary ────────────────────────────────────────────────────────────────
    orig_lines = original.count("\n")
    new_lines = content.count("\n")
    print(f"MOB: {orig_lines} lines -> {new_lines} lines ({new_lines - orig_lines:+d})")
    for old, new in [
        ("Formation", "Groundwork"),
        ("Practicum", "Development"),
        ("Navigation", "Advisory"),
    ]:
        n = original.count(old)
        print(f"  {old} -> {new}: {n} replacements")

    if DRY_RUN:
        print("\nDRY RUN — no file written. Run with --write to apply.")
        # Show a snippet of the open items insertion
        idx = content.find("Copy rule — human register")
        if idx >= 0:
            print("\n[Open items sample]")
            print(content[max(0, idx - 100):idx + 200])
    else:
        MOB_PATH.write_text(content, encoding="utf-8")
        print("\nWRITTEN: tools/_mob.txt updated to v4.8.")


if __name__ == "__main__":
    run()
