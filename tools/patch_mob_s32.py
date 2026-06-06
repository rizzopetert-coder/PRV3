"""
Patch tools/_mob.txt for Session 32 closeout.
Usage:
  python tools/patch_mob_s32.py --dry-run
  python tools/patch_mob_s32.py --write
"""

import argparse
import sys
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")

CHANGES = []

# ── 1. Version bump ───────────────────────────────────────────────────────────
CHANGES.append((
    r"\\\#\\\# MOB v3.5",
    r"\\\#\\\# MOB v3.6",
    "Version v3.5 → v3.6",
))

# ── 2. Section 8 — expand Commercial Layer with S32 records ──────────────────
OLD_S8 = "Service offering names, pricing, UX, marketing site, instrument delivery interface — all under review. Not locked. Pete decides."

NEW_S8 = """Service offering names, pricing, UX, marketing site, instrument delivery interface. Core commercial records below.



\\*\\*Practice spine — locked Session 32:\\*\\* Expertise. Resonance. Effectiveness. Internal standard, not a market-facing tagline. Every engagement, every service type, every deliverable is held accountable to all three: Did we bring expertise? Did we produce resonance? Did it result in effectiveness?



\\*\\*Five service names — final, locked Session 32:\\*\\*



| \\*\\*Formation\\*\\* | Group training for developing leaders |

| --- | --- |

| \\*\\*Practicum\\*\\* | Individual coaching for developing leaders, bounded engagement |

| \\*\\*Counsel\\*\\* | Retainer advisory for executives and HR leaders |

| \\*\\*Navigation\\*\\* | Change navigation and emergency response for executives |

| \\*\\*Diagnostic\\*\\* | Organizational assessment leading to recovery consulting if warranted |



\\*\\*Terraforming four-address architecture — Session 32:\\*\\* Terraforming as the practice endgame surfaces differently across four distinct addresses. Shareable output: credibility document. Names the condition with precision. Terraforming premise felt through diagnostic framing — condition language not failure language — concept not introduced explicitly. Private output: where the Principal feels understood. Their language used precisely and sparingly. Consultation: where terraforming is named. The destination the diagnostic was pointing toward. Commercial surface: where the practice speaks about itself. "We don't fix people problems. We change the conditions that produce them." Lives here.



\\*\\*The Work — Session 32:\\*\\* Held. Weight confirmed. Address unknown. Do not assign until Session 33 or later surfaces the right home."""

CHANGES.append((
    OLD_S8,
    NEW_S8,
    "Section 8: expand Commercial Layer with S32 records",
))

# ── 3. Section 13 — update WS3 status line (dynamic — extracted from file) ───
# Not added to CHANGES list; handled separately in apply() to avoid escape issues.

# ── 4. Open items — close Tagline/Spine and Service Names, update Citation Audit ──
OLD_TAGLINE_ITEM = "| Tagline and spine | In progress, not locked. Session 32 opening priority. |"
NEW_TAGLINE_ITEM = "| Tagline and spine | CLOSED Session 32. Practice spine locked as internal standard: Expertise. Resonance. Effectiveness. No separate market-facing tagline pending. |"

CHANGES.append((
    OLD_TAGLINE_ITEM,
    NEW_TAGLINE_ITEM,
    "Open items: close Tagline and spine",
))

OLD_SVC_NAMES = "| Service offering names | Deferred to Session 32. |"
NEW_SVC_NAMES = "| Service offering names | CLOSED Session 32. Final: Formation, Practicum, Counsel, Navigation, Diagnostic. |"

CHANGES.append((
    OLD_SVC_NAMES,
    NEW_SVC_NAMES,
    "Open items: close Service offering names",
))

OLD_CITATION = "| Content library citation audit | Open. |"
NEW_CITATION = "| Content library citation audit | Open. E2, E5, E7 priority. |"

CHANGES.append((
    OLD_CITATION,
    NEW_CITATION,
    "Open items: citation audit — add E2/E5/E7 priority",
))

# Add new open items after the Gemini brief line
OLD_GEMINI_ITEM = "| Gemini commercial brief | Produced Session 31. Pete to engage separately. |"
NEW_GEMINI_ITEM = """| Gemini commercial brief | Produced Session 31. Pete to engage separately. |



| Navigation urgency question | Open. How urgency/emergency positioning is surfaced commercially. Session 33 scope. |



| Diagnostic intrigue question | Open. Whether and how the Diagnostic service name earns more than clinical clarity. Session 33 scope. |



| The Work | Held. Weight confirmed. Address unknown. Do not assign until Session 33 or later surfaces the right home. |"""

CHANGES.append((
    OLD_GEMINI_ITEM,
    NEW_GEMINI_ITEM,
    "Open items: add Navigation urgency, Diagnostic intrigue, The Work",
))

# ── 5. Section 14 — add Session 32 locked decisions entry ────────────────────
OLD_S31_DECISION = ("| \\\\\\*\\\\\\*Session 31\\\\\\*\\\\\\* | Practice values locked: Effectiveness. Candor. Humanity. "
                    "Named as values, demonstrated by the work. Positioning draft confirmed.")

NEW_S31_AND_S32 = (OLD_S31_DECISION[: OLD_S31_DECISION.rfind("|") + 1] +
                   "\n\n  \n\n| \\\\\\*\\\\\\*Session 32\\\\\\*\\\\\\* | "
                   "Practice spine locked: Expertise. Resonance. Effectiveness. (internal standard, not tagline). "
                   "Five service names final: Formation, Practicum, Counsel, Navigation, Diagnostic. "
                   "Terraforming four-address architecture recorded. The Work held — address deferred. |")

CHANGES.append((
    OLD_S31_DECISION,
    NEW_S31_AND_S32,
    "Section 14: add Session 32 locked decisions entry",
))

# ── 6. Section 16 — add Session 32 session log entry ─────────────────────────
OLD_S31_LOG = ("| \\\\\\*\\\\\\*June 2026 — Session 31\\\\\\*\\\\\\* | Commercial Layer (WS3) Session 1. "
               "Practice values locked: Effectiveness, Candor, Humanity.")

NEW_S31_AND_S32_LOG = (OLD_S31_LOG +
                       " Positioning draft confirmed. Two load-bearing statements confirmed. "
                       "Terraforming as practice endgame confirmed. Bilateral understanding arc confirmed. "
                       "PRV3 as primary SEO entry point confirmed. Service menu retained — hard silos rejected, "
                       "lines may blur in practice. Service offering names deferred Session 32. "
                       "Tagline and spine in progress — not locked. Gemini commercial brief produced "
                       "(Pete to engage separately). Path B migration closed as infrastructure item. "
                       "405 tests, 0 failures (no engine changes this session). MOB updated to v3.5. |"
                       "\n\n  \n\n| \\\\\\*\\\\\\*June 2026 — Session 32\\\\\\*\\\\\\* | "
                       "Commercial Layer (WS3) Session 2. No engine work. No code touched. "
                       "Practice spine locked: Expertise. Resonance. Effectiveness. (internal standard). "
                       "Five service names final: Formation, Practicum, Counsel, Navigation, Diagnostic. "
                       "Terraforming four-address architecture recorded. The Work held. "
                       "MOB updated to v3.6. |")

CHANGES.append((
    OLD_S31_LOG,
    NEW_S31_AND_S32_LOG,
    "Section 16: add Session 32 session log entry",
))


def _ws3_old(content: str) -> str:
    idx = content.find("Commercial layer")
    start = content.rfind("\n", 0, idx) + 1
    end = content.find("\n", idx)
    return content[start:end]

def _ws3_new(old: str) -> str:
    return (old
        .replace("ACTIVE — Session 31.", "ACTIVE — Session 32.")
        .replace(
            "Positioning draft confirmed. Practice values locked: Effectiveness, Candor, Humanity. "
            "Service menu retained — hard silos rejected, lines may blur in practice. "
            "Service offering names deferred Session 32. Tagline and spine in progress — not locked.",
            "Practice spine locked (internal standard: Expertise. Resonance. Effectiveness.). "
            "Five service names final and locked (Formation, Practicum, Counsel, Navigation, Diagnostic). "
            "Terraforming four-address architecture recorded. The Work held — address deferred. "
            "Session 33 priority: service menu structure, Navigation urgency question, Diagnostic intrigue question."
        ))

def apply(content: str, dry_run: bool) -> tuple[str, list[str]]:
    log = []

    # Dynamic WS3 change
    old_ws3 = _ws3_old(content)
    new_ws3 = _ws3_new(old_ws3)
    if old_ws3 == new_ws3:
        log.append("  MISS  [Section 13: update WS3 status to Session 32] — transformation produced no change")
    elif old_ws3 not in content:
        log.append("  MISS  [Section 13: update WS3 status to Session 32] — extracted line not found in content")
    else:
        log.append("  HIT   [Section 13: update WS3 status to Session 32]")
        if not dry_run:
            content = content.replace(old_ws3, new_ws3)

    for old, new, label in CHANGES:
        if old not in content:
            log.append(f"  MISS  [{label}] — string not found")
        else:
            count = content.count(old)
            if count > 1:
                log.append(f"  WARN  [{label}] — {count} occurrences found, replacing all")
            else:
                log.append(f"  HIT   [{label}]")
            if not dry_run:
                content = content.replace(old, new)
    return content, log


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        print("Specify --dry-run or --write")
        sys.exit(1)

    content = MOB_PATH.read_text(encoding="utf-8")
    updated, log = apply(content, dry_run=True)

    out = sys.stdout.buffer
    def p(s): out.write((s + "\n").encode("utf-8"))

    p(f"Patch report -- tools/_mob.txt ({len(CHANGES)} changes)\n")
    for line in log:
        p(line)

    misses = [l for l in log if "MISS" in l]
    if misses:
        p(f"\n{len(misses)} miss(es) -- stopping. Fix before write.")
        sys.exit(1)

    if args.write:
        final, _ = apply(content, dry_run=False)
        MOB_PATH.write_text(final, encoding="utf-8")
        p(f"\nWritten: {MOB_PATH}")
    else:
        p("\nDry-run complete. Run with --write to apply.")


if __name__ == "__main__":
    main()
