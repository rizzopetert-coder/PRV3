"""MOB patch script — S41 closeout. Bump v4.6 → v4.7, add Session 41 entries."""
import sys
from pathlib import Path

DRY_RUN = "--write" not in sys.argv

mob_path = Path("tools/_mob.txt")
content = mob_path.read_text(encoding="utf-8")
original = content

# ---------------------------------------------------------------------------
# Change 1: Version bump
# ---------------------------------------------------------------------------
OLD_VERSION = "MOB v4.6"
NEW_VERSION = "MOB v4.7"
assert content.count(OLD_VERSION) >= 1, f"Version string not found"
content = content.replace(OLD_VERSION, NEW_VERSION, 1)

# ---------------------------------------------------------------------------
# Change 2: WS2 description — replace S41 scope placeholder with S41 completion
# ---------------------------------------------------------------------------
OLD_S41_SCOPE = (
    "S41 scope: output component copy and styling"
    " — PrivateOutput.tsx, ShareableOutput.tsx, ShareButton.tsx."
)
NEW_S41_BLOCK = (
    "S41 complete: web/lib/types.ts created — authoritative type contract"
    " (PrivateOutputPayload, ShareableOutputPayload, StateRef, IntakeEcho,"
    " FrictionTaxEstimate, SeverityTier, ResolutionFamily)."
    " output-renderer.ts — types removed, imported from types.ts;"
    " render functions updated for new payload shapes."
    " /api/result — PrivateOutputPayload with normalized weights;"
    " resolution_family sourced from TypeScript STATE_RESOLUTION_FAMILY map (not engine field)."
    " /api/share/create — ShareableOutputPayload with secondary filter (weight >= 0.20, max 2);"
    " IntakeEcho included."
    " /api/share/[id] — import path updated."
    " page.tsx — Phase 5 added; diagnostic CTA wired:"
    " POST /api/result sets resultPayload, transitions to Phase 5;"
    " AssemblyPanel hidden at Phase 5."
    " PrivateOutput.tsx — prop updated to PrivateOutputPayload direct."
    " ResolutionFamily casing verified lowercase against engine/resolution_families.py."
    " ENGINE DEBT FLAGGED (deferred Phase 3):"
    " private_output.resolution_routing in states.py serializes pre-S32 service names"
    " (e.g. Development, Roadmap + Intervention) — bypassed by TypeScript STATE_RESOLUTION_FAMILY map;"
    " requires Python-side cleanup in engine/data/states.py + engine/output.py before output layer is clean."
    " TypeScript: 0 errors."
    " S42 scope: PrivateOutput.tsx, ShareableOutput.tsx, ShareButton.tsx — copy and styling."
)
assert OLD_S41_SCOPE in content, "S41 scope placeholder not found"
content = content.replace(OLD_S41_SCOPE, NEW_S41_BLOCK, 1)

# ---------------------------------------------------------------------------
# Change 3: Open items — add engine debt row before the closing separator
# The open items table ends with the LinkedIn BD row, then blank lines, then \\---
# ---------------------------------------------------------------------------
OLD_OPEN_ITEMS_END = (
    "LinkedIn BD legal read | Required before personal account amplification."
    " Non-solicitation agreement with OneDigital governs."
    " Attorney to advise on: passive content sharing,"
    " definition of solicitation under agreement, LinkedIn as channel. |\n"
)
ENGINE_DEBT_ROW = (
    "| private_output.resolution_routing stale values"
    " | engine/data/states.py serializes pre-S32 service names"
    " (Development, Roadmap + Intervention, Executive Counsel + Intervention, etc.)"
    " in the resolution_routing field."
    " TypeScript layer bypasses this via STATE_RESOLUTION_FAMILY map in /api/result and /api/share/create."
    " Python-side cleanup required in engine/data/states.py and engine/output.py"
    " before output layer is fully clean. Deferred to Phase 3. ENGINE DEBT. |\n"
)
NEW_OPEN_ITEMS_END = OLD_OPEN_ITEMS_END + ENGINE_DEBT_ROW
assert OLD_OPEN_ITEMS_END in content, "LinkedIn BD open items anchor not found"
content = content.replace(OLD_OPEN_ITEMS_END, NEW_OPEN_ITEMS_END, 1)

# ---------------------------------------------------------------------------
# Change 4: Locked Decisions Log (Section 14) — add Session 41 before closing ---
# Anchor: the end of the Session 39 entry (known commit hash 2d2da5d)
# ---------------------------------------------------------------------------
SESSION_40_COMMIT_ANCHOR = "Commit: 2d2da5d. |"
SESSION_41_LOCKED = (
    "\n\n  \n\n"
    "| \\\\\\*\\\\\\*Session 41\\\\\\*\\\\\\* |"
    " web/lib/types.ts created as authoritative type contract."
    " PrivateOutputPayload, ShareableOutputPayload, StateRef, IntakeEcho,"
    " FrictionTaxEstimate, SeverityTier, ResolutionFamily locked."
    " ResolutionFamily lowercase confirmed against engine/resolution_families.py."
    " Secondary state filter locked: weight >= 0.20 max 2 (shareable payload)."
    " Result routing locked: client-side Phase 5 transition, zero KV write for private output."
    " IntakeEcho added to ShareableOutputPayload (Gemini Q5 correction)."
    " ENGINE DEBT logged: private_output.resolution_routing carries pre-S32 service names;"
    " deferred to Phase 3 Python-side fix."
    " TypeScript: 0 errors. Commit: this session. |"
)
assert SESSION_40_COMMIT_ANCHOR in content, f"Session 40 commit anchor not found: {SESSION_40_COMMIT_ANCHOR}"
content = content.replace(SESSION_40_COMMIT_ANCHOR, SESSION_40_COMMIT_ANCHOR + SESSION_41_LOCKED, 1)

# ---------------------------------------------------------------------------
# Change 5: Document Registry (Section 15) — add types.ts entry
# Anchor: after output-renderer.ts entry
# ---------------------------------------------------------------------------
OLD_RENDERER_ENTRY = "| \\\\\\*\\\\\\*web/lib/output-renderer.ts\\\\\\*\\\\\\*"
TYPES_TS_ENTRY = (
    "| \\\\\\*\\\\\\*web/lib/types.ts\\\\\\*\\\\\\* |"
    " Authoritative TypeScript type contract for output layer."
    " Exports: PrivateOutputPayload, ShareableOutputPayload, StateRef, IntakeEcho,"
    " FrictionTaxEstimate, SeverityTier, ResolutionFamily."
    " Source of truth for /api/result, /api/share/create, /api/share/[id],"
    " output-renderer.ts, PrivateOutput.tsx. Created S41. |\n"
    "| \\\\\\*\\\\\\*web/lib/output-renderer.ts\\\\\\*\\\\\\*"
)
assert OLD_RENDERER_ENTRY in content, "output-renderer.ts registry entry not found"
content = content.replace(OLD_RENDERER_ENTRY, TYPES_TS_ENTRY, 1)

# ---------------------------------------------------------------------------
# Change 6: Session Log (Section 16) — add Session 41 after Session 40
# Session 40 entry is the final line of the file (no trailing newline).
# ---------------------------------------------------------------------------
SESSION_40_LOG_END = "MOB updated to v4.6. |"
assert SESSION_40_LOG_END in content, "Session 40 log end anchor not found"
SESSION_41_LOG = (
    "\n\n  \n\n"
    "| \\\\\\*\\\\\\*June 2026 — Session 41\\\\\\*\\\\\\* |"
    " S41 output layer data contract complete."
    " web/lib/types.ts created — authoritative type contract."
    " output-renderer.ts updated — types imported from types.ts."
    " /api/result, /api/share/create, /api/share/[id] updated."
    " page.tsx Phase 5 wired."
    " PrivateOutput.tsx updated to PrivateOutputPayload direct."
    " ENGINE DEBT flagged: private_output.resolution_routing stale field in states.py,"
    " deferred to Phase 3."
    " TypeScript: 0 errors. MOB updated to v4.7. |"
)
content = content.replace(SESSION_40_LOG_END, SESSION_40_LOG_END + SESSION_41_LOG, 1)

# ---------------------------------------------------------------------------
# Dry-run report
# ---------------------------------------------------------------------------
changes = [
    ("Version", OLD_VERSION, NEW_VERSION),
    ("WS2 S41 scope", OLD_S41_SCOPE[:60], NEW_S41_BLOCK[:60]),
    ("Open items engine debt", "ADDED engine debt row after LinkedIn BD", ""),
    ("Section 14 Session 41", "ADDED Session 41 locked decisions entry", ""),
    ("Section 15 types.ts", "ADDED web/lib/types.ts registry entry", ""),
    ("Section 16 Session 41", "ADDED Session 41 session log entry", ""),
]

print(f"DRY RUN: {DRY_RUN}")
print(f"Original length: {len(original)} chars")
print(f"New length:      {len(content)} chars")
print(f"Delta:           +{len(content) - len(original)} chars")
print()
for label, old, new in changes:
    print(f"  [{label}]")
    if new:
        print(f"    OLD: {old}")
        print(f"    NEW: {new}")
    else:
        print(f"    {old}")
    print()

if DRY_RUN:
    print("Pass --write to apply.")
else:
    Path("tools/_mob.txt").write_text(content, encoding="utf-8")
    print("Written to tools/_mob.txt")
