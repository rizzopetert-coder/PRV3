"""
Patch tools/_mob.txt for Session 33 closeout.
Usage:
  python tools/patch_mob_s33.py --dry-run
  python tools/patch_mob_s33.py --write
"""

import argparse
import sys
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")


def out(s):
    sys.stdout.buffer.write((s + "\n").encode("utf-8"))


# ── helpers ───────────────────────────────────────────────────────────────────

def _apply(content, old, new, label, log):
    if old not in content:
        log.append(f"  MISS  [{label}]")
        return content
    count = content.count(old)
    tag = "WARN (multiple)" if count > 1 else "HIT "
    log.append(f"  {tag}  [{label}]")
    return content.replace(old, new)


# ── change 1: Section 1 service offerings sentence ────────────────────────────

SEC1_OLD = ("The five service offerings the diagnostic routes to: "
            "Roadmap, Stability Support, Development, Intervention, Executive Counsel. "
            "Names and pricing under review — not locked.")

SEC1_NEW = ("The diagnostic is the primary entry point. "
            "Four resolution services sit beneath it: Formation, Practicum, Counsel, Navigation. "
            "Service names locked Session 32. Two-tier structure locked Session 33. Pricing not locked.")


# ── change 2: Section 8 — add Session 33 locked records ──────────────────────

# Insertion anchor: end of The Work entry
S8_ANCHOR = ("The Work — Session 32:\\\\\\* Held. Weight confirmed. Address unknown. "
             "Do not assign until Session 33 or later surfaces the right home.")

# Dynamically extract — the exact S8 The Work line from file
def _s8_anchor(content):
    idx = content.find("The Work")
    while idx != -1:
        chunk = content[idx:idx+120]
        if "Weight confirmed" in chunk:
            start = content.rfind("\n", 0, idx) + 1
            end = content.find("\n", idx)
            return content[start:end]
        idx = content.find("The Work", idx + 1)
    return None

S8_ADDITION = """


\\*\\*Site architecture — locked Session 33:\\*\\* Three parallel entry points: diagnostic path, direct inquiry path, service-specific path. All converge to a conversation. Diagnostic is intellectual center of gravity, not sole entry point.



\\*\\*Two-tier service structure — locked Session 33:\\*\\* Diagnostic sits above the four resolution services (Formation, Practicum, Counsel, Navigation). Diagnostic is the entry point layer. The four are the resolution layer.



\\*\\*Content principles — locked Session 33:\\*\\* Site is short. Three content types: condition language, short-form proof, clear next steps (one per path). Methodology, instrument architecture, 47-state taxonomy, and pricing stay off the site. Content library lives adjacent to the commercial surface, not on it. Two-minute test governs: visitor understands the practice, confirms relevance, finds next step in under two minutes.



\\*\\*Navigation subtitle — locked Session 33:\\*\\* Primary name confirmed. Subtitle carries urgency for the acute entry point. Executives in crisis need to know the practice recognizes the emergency before they register the capability.



\\*\\*Diagnostic name — locked Session 33:\\*\\* Clarity confirmed over intrigue. Clinical register is the differentiator. Name sets the standard of Expertise before the client engages."""


# ── change 3: Section 13 WS3 — update S33 priority line ─────────────────────

SEC13_OLD = ("Session 33 priority: service menu structure, "
             "Navigation urgency question, Diagnostic intrigue question.")

SEC13_NEW = ("Session 33 complete. Navigation and Diagnostic names confirmed. "
             "Two-tier service structure locked. Site architecture locked. Content principles locked. "
             "Session 34 priority: service-specific path design and execution-level menu layout.")


# ── change 4: Open items — close Navigation urgency ──────────────────────────

NAV_OLD = ("| Navigation urgency question | Open. "
           "How urgency/emergency positioning is surfaced commercially. Session 33 scope. |")

NAV_NEW = "| Navigation urgency question | CLOSED Session 33. Name confirmed. Subtitle carries urgency. |"


# ── change 5: Open items — close Diagnostic intrigue ─────────────────────────

DIAG_OLD = ("| Diagnostic intrigue question | Open. "
            "Whether and how the Diagnostic service name earns more than clinical clarity. Session 33 scope. |")

DIAG_NEW = "| Diagnostic intrigue question | CLOSED Session 33. Clarity confirmed over intrigue. |"


# ── change 6: Open items — add three new items after The Work item ────────────

THEWORK_ITEM = ("| The Work | Held. Weight confirmed. "
                "Address unknown. Do not assign until Session 33 or later surfaces the right home. |")

THEWORK_ITEM_NEW = (
    "| The Work | Held. Weight confirmed. "
    "Address unknown. Do not assign until Session 33 or later surfaces the right home. |"
    "\n\n\n\n| Service-specific path design | Open. "
    "How each of the four resolution services presents on the site. "
    "What a practitioner-directed arrival finds. Session 34 scope. |"
    "\n\n\n\n| Menu execution layout | Open. "
    "How the two-tier structure looks on the page. "
    "Weight and position of Diagnostic relative to the four. Session 34 scope. |"
    "\n\n\n\n| Placement of two load-bearing positioning statements | Open. "
    "Both confirmed for commercial surface. Specific location not yet decided. |"
)


# ── change 7: Section 16 — correct Session 32 log entry ─────────────────────
# The S32 row has pasted S31 content starting after "The Work held."
# Anchor: unique substring spanning the S32/S31 paste boundary

def _s32_log_old(content):
    """Extract the pasted-S31 tail from the S32 log row."""
    marker = "The Work held."
    idx = content.find(marker)
    # There may be multiple — find the one in the log section
    log_idx = content.find("# 16. Session Log")
    idx = content.find(marker, log_idx)
    if idx == -1:
        return None
    # From marker to end of row (next \n that is followed by | or \n)
    search = idx + len(marker)
    row_end = None
    pos = search
    while pos < len(content):
        nl = content.find("\n", pos)
        if nl == -1:
            row_end = len(content)
            break
        after = content[nl + 1: nl + 3]
        if after.startswith("|") or after == "\n":
            row_end = nl
            break
        pos = nl + 1
    if row_end is None:
        return None
    return content[idx:row_end]


S32_LOG_TAIL_NEW = (
    "The Work held. "
    "Load-bearing statements confirmed: “We don’t arrive with a methodology and fit you into it. "
    "We start with you.” and “We don’t fix people problems. "
    "We change the conditions that produce them.” "
    "Terraforming as practice endgame confirmed. "
    "Bilateral understanding arc confirmed as value delivery sequence. "
    "PRV3 diagnostic confirmed as primary SEO entry point. "
    "Service menu retained — hard silos rejected. MOB updated to v3.6. |"
)


# ── change 8: Section 16 — add Session 33 log entry ─────────────────────────

S33_LOG_ANCHOR = "MOB updated to v3.6. |"  # end of corrected S32 entry (after change 7)

S33_LOG_ENTRY = (
    "\n\n  \n\n| \\\\\\*\\\\\\*June 2026 — Session 33\\\\\\*\\\\\\* | "
    "Commercial Layer (WS3) Session 3. "
    "Navigation name confirmed — subtitle carries urgency. "
    "Diagnostic name confirmed — clarity over intrigue. "
    "Two-tier service structure locked: Diagnostic above, four resolution services beneath. "
    "Site architecture locked: three entry points (diagnostic, direct inquiry, service-specific), "
    "all converge to conversation. "
    "Content principles locked: condition language, short-form proof, clear next steps. "
    "Two-minute test adopted as governing standard. "
    "Content library confirmed as adjacent to commercial surface, not on it. "
    "No engine changes. MOB updated to v3.7. |"
)

# ── change 9: version bump ────────────────────────────────────────────────────

VER_OLD = r"\\\#\\\# MOB v3.6"
VER_NEW = r"\\\#\\\# MOB v3.7"


# ── apply all changes ─────────────────────────────────────────────────────────

def apply_all(content: str, dry_run: bool) -> tuple[str, list[str]]:
    log = []

    # 1. Section 1
    content = _apply(content, SEC1_OLD, SEC1_NEW, "Section 1: service offerings sentence", log)

    # 2. Section 8 addition — dynamic anchor
    s8_old = _s8_anchor(content)
    if s8_old is None:
        log.append("  MISS  [Section 8: add S33 records] — The Work anchor not found")
    else:
        s8_new = s8_old + S8_ADDITION
        if s8_old == s8_new:
            log.append("  MISS  [Section 8: add S33 records] — S8 addition produced no change")
        else:
            log.append("  HIT   [Section 8: add S33 records]")
            if not dry_run:
                content = content.replace(s8_old, s8_new, 1)

    # 3. Section 13 WS3
    content = _apply(content, SEC13_OLD, SEC13_NEW,
                     "Section 13: WS3 S33 priority → complete", log)

    # 4. Nav urgency close
    content = _apply(content, NAV_OLD, NAV_NEW, "Open items: close Navigation urgency", log)

    # 5. Diagnostic intrigue close
    content = _apply(content, DIAG_OLD, DIAG_NEW, "Open items: close Diagnostic intrigue", log)

    # 6. Add three new open items
    content = _apply(content, THEWORK_ITEM, THEWORK_ITEM_NEW,
                     "Open items: add Service-specific path, Menu layout, Load-bearing placement", log)

    # 7. Correct S32 log entry — dynamic extraction
    s32_tail_old = _s32_log_old(content)
    if s32_tail_old is None:
        log.append("  MISS  [Section 16: correct S32 log] — tail not found")
    elif s32_tail_old == S32_LOG_TAIL_NEW:
        log.append("  SKIP  [Section 16: correct S32 log] — already correct")
    else:
        log.append("  HIT   [Section 16: correct S32 log]")
        if not dry_run:
            content = content.replace(s32_tail_old, S32_LOG_TAIL_NEW, 1)

    # 8. Add S33 log entry — after the corrected S32 tail
    # Anchor is the last occurrence of "MOB updated to v3.6. |" (the corrected S32 end)
    anchor_idx = content.rfind(S33_LOG_ANCHOR)
    if anchor_idx == -1:
        log.append("  MISS  [Section 16: add S33 log entry] — S32 end anchor not found")
    else:
        after_anchor = anchor_idx + len(S33_LOG_ANCHOR)
        # Check if S33 entry already present
        if "Session 33" in content[after_anchor:after_anchor + 200]:
            log.append("  SKIP  [Section 16: add S33 log entry] — already present")
        else:
            log.append("  HIT   [Section 16: add S33 log entry]")
            if not dry_run:
                content = content[:after_anchor] + S33_LOG_ENTRY + content[after_anchor:]

    # 9. Version bump — applied last so anchors above still match v3.6
    content = _apply(content, VER_OLD, VER_NEW, "Version v3.6 → v3.7", log)

    return content, log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        out("Specify --dry-run or --write")
        sys.exit(1)

    content = MOB_PATH.read_text(encoding="utf-8")
    _, log = apply_all(content, dry_run=True)

    out(f"Patch report -- tools/_mob.txt (9 changes)\n")
    for line in log:
        out(line)

    misses = [l for l in log if "MISS" in l]
    if misses:
        out(f"\n{len(misses)} miss(es) -- stopping. Fix before write.")
        sys.exit(1)

    if args.write:
        final, _ = apply_all(content, dry_run=False)
        MOB_PATH.write_text(final, encoding="utf-8")
        out(f"\nWritten: {MOB_PATH}")
    else:
        out("\nDry-run complete. Run with --write to apply.")


if __name__ == "__main__":
    main()
