"""
Patch script: MOB v4.0 -> v4.1
Adds two Session 35 entries to Section 8.
Usage: python tools/patch_mob_s35_sec8.py          # dry run
       python tools/patch_mob_s35_sec8.py --write  # apply
"""
import sys
from pathlib import Path

MOB = Path("tools/_mob.txt")
content = MOB.read_text(encoding="utf-8")
original = content

EM = "—"   # em-dash

# ── SECTION 8: Insert two Session 35 entries before the closing \\--- ─────────
# Anchor: end of LinkedIn BD entry (unique in file)
# End:    the \\--- that closes Section 8

ANCHOR  = "LinkedIn as channel."
# In the file \\--- is two backslashes + three dashes
SEC8_SEP = "\\\\" + "---"

idx_a = content.find(ANCHOR)
if idx_a == -1:
    print("FAIL: Section 8 anchor not found")
    sys.exit(1)
idx_a_end = idx_a + len(ANCHOR)

idx_sep = content.find(SEC8_SEP, idx_a_end)
if idx_sep == -1:
    print("FAIL: Section 8 separator not found")
    sys.exit(1)

NEW_ENTRIES = (
    "\n\n"
    "\\*\\*Self-selection interface"
    f" {EM} Architecture Spec v0.2"
    f" {EM} locked Session 35:\\*\\*"
    " Four-phase architecture confirmed and build-ready."
    f" Phase 1: Signature Recognition {EM} five signature cards,"
    " single instruction (\"Start here. Read each one. Select the ones that sound familiar.\"),"
    " transition trigger copy \"Let's take a closer look.\" fires after first selection."
    f" Phase 2: State Assembly {EM} Option C selection model (signature-level and state-level parallel, shared assembly)."
    " Selected signatures expand on load; unselected signatures collapsed with count affordance (e.g., \"8 conditions inside\")."
    f" Desktop: persistent sidebar. Mobile: collapsible bottom sheet {EM} collapsed state is floating summary bar, expanded reveals full assembly list."
    f" Dimmed states: structural typography {EM} selected states get solid border and bold text, unselected get muted gray and no border."
    " No tap-to-reveal."
    f" Phase 3: Coexistence Interpretation {EM} Option A logic: static interpretation for ≥70% single-signature clean match, dynamic generative fallback for mixed assemblies."
    f" Dynamic fallback input: state names and signature affiliations only {EM} no engine weights injected."
    " Output constraint: condition pattern and organizational cost only, no service language, no severity framing."
    " Transition trigger: \"See what this means.\""
    " Single-state edge case: \"You've identified one condition. The diagnostic can tell you more about what's beneath it.\""
    f" Phase 4: Transition {EM} two equal-weight paths: take the full diagnostic, or start a conversation."
    f" Transition copy: \"Here's what comes next. The diagnostic goes deeper {EM} it sees what self-report can't. Or, if you've seen enough, start a conversation.\""
    " Spec document: PRV3_Self_Selection_Architecture_Spec_v0.2.docx, outputs folder."
    "\n\n"
    "\\*\\*Engagement Agreement Draft v1.0"
    f" {EM} produced Session 35:\\*\\*"
    " Ten sections plus Exhibit A Statement of Work."
    f" Shadow model compliant {EM} no personal name, no affiliated entity reference."
    " Categorical independence language throughout (Section 3)."
    " Six attorney review flags embedded."
    " Five service types described with diagnostic output constraint preserved."
    " Data handling: Option D default, Option B elective with checkbox election block."
    " Governing law: Massachusetts."
    " Load-bearing open item: attorney must read independence representation against non-solicitation agreement before execution."
    f" Draft is working {EM} not execution-ready."
    " Document: PRV3_Engagement_Agreement_Draft_v1.0.docx, outputs folder."
    "\n\n\n\n\n\n\n\n"
)

content = content[:idx_a_end] + NEW_ENTRIES + content[idx_sep:]
print("Section 8 additions: OK")

# ── VERSION BUMP: v4.0 -> v4.1 ────────────────────────────────────────────
VER_FIND    = r"\\\#\\\# MOB v4.0"
VER_REPLACE = r"\\\#\\\# MOB v4.1"

if VER_FIND not in content:
    print("FAIL: version string v4.0 not found")
    sys.exit(1)
content = content.replace(VER_FIND, VER_REPLACE, 1)
print("Version v4.0 -> v4.1: OK")

# ── WRITE / DRY RUN ───────────────────────────────────────────────────────
dry_run = "--write" not in sys.argv
if dry_run:
    old_lines = original.splitlines()
    new_lines = content.splitlines()
    delta = len(new_lines) - len(old_lines)
    sign = "+" if delta >= 0 else ""
    print(f"\nDRY RUN complete. Lines: {len(old_lines)} -> {len(new_lines)} ({sign}{delta})")
    # Show the two new entries
    idx_show = content.find("Self-selection interface")
    if idx_show != -1:
        print("\n--- PREVIEW (first 300 chars of new content) ---")
        print(content[idx_show:idx_show+300])
    print("\nRun with --write to apply.")
else:
    Path("tools/_mob.txt").write_text(content, encoding="utf-8")
    print("\nWRITE complete. MOB v4.1.")
