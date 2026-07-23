"""
PRV3 MOB Update -- Path 1 genuinely live-verified (real Preview round trip),
Decision Register Path 1 row resolved, bypass-secret exposure/rotation logged

Updates tools/_mob.txt:
  - Section 13a (Decision Register): Path 1 row status updated from
    "Phase 1 built, unverified end-to-end" to RESOLVED, closing the row
    opened at Session 71
  - Section 14 (Locked Decisions Log): new entry appended after the prior
    "code-level complete, live verification blocked" entry (ascending
    order, this section's newest tail)
  - Section 16 (Session Log): new one-line entry prepended before the
    prior entry's log line (descending order, this section's newest head)
  - Version bump v4.58 -> v4.59 (material workstream status change --
    Path 1 is now genuinely live-verified, not just code-correct; a
    long-standing Decision Register row closes)

Updates CLAUDE.md:
  - MOB version cross-reference v4.58 -> v4.59

Documentation-only change -- no product code touched by this script.

Usage:
  python tools/patch_mob_path1_live_verified.py --dry-run
  python tools/patch_mob_path1_live_verified.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


# ═══════════════════════════════════════════════════════════════════════════
# tools/_mob.txt
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.58",
    "\\\\\\#\\\\\\# MOB v4.59",
)

# --- Section 13a (Decision Register): resolve the Path 1 row ---

PATH1_ROW_OLD = (
    "| Path 1 (full diagnostic instrument) scope | 3 | Phase 1 built, "
    "unverified end-to-end | Credentials exist in Vercel Production/Preview "
    "(ENGINE_URL, ENGINE_SECRET, UPSTASH_REDIS_REST_URL, "
    "UPSTASH_REDIS_REST_TOKEN, ANTHROPIC_API_KEY — provisioned 2026-06-14, "
    "confirmed S71) but are not present in the Claude Code coding sandbox "
    "where this build happened. `vercel env pull` requires an authenticated "
    "Vercel CLI session — this sandbox has network access to Vercel's API "
    "(confirmed: a live token-validation round trip returned a real 401, "
    "not a connection failure) but no valid token, and completing "
    "`vercel login` requires an interactive step (browser or email) this "
    "non-interactive environment can't perform | Session 71 (Claude Code) | "
    "Whenever the credential-access path is resolved — Pete pulls "
    "`.env.local` locally and transfers it into the coding environment "
    "some other way, or authenticates the CLI in-session some other way "
    "— and the live round trip can actually run. Not a session-number "
    "check-in |"
)

PATH1_ROW_NEW = (
    "| Path 1 (full diagnostic instrument) scope | 3 | **RESOLVED — "
    "genuinely live-verified** | Credential-access path resolved by Pete "
    "directly (`vercel login` completed, `vercel link` + `vercel env pull "
    "--environment=preview` run clean from the coding sandbox). Real "
    "Preview round trip executed and independently confirmed: real HTTP → "
    "real Next.js route → real Python engine → real Redis write/delete, "
    "verified against Upstash directly (not just the app's own API "
    "response) — `LRANGE diagnostic-aggregate` showed the matching "
    "completion record, `KEYS diagnostic-session:*` returned empty, "
    "confirming the Transition Rule's delete-on-completion fired for real. "
    "Two severity follow-ons fired live (SEVER-04 deliberate, SEVER-05 "
    "incidental) and Phase 2 checkpoint distinguishers (DIST-CM-01/02) "
    "fired in the same session — tier=Entrenched, score=50.0, hand-verified "
    "against the raw contribution math. | Session 71 → resolved this "
    "session (Claude Code) | Closed — no further check-in needed. Separate "
    "investigation opened this same session into a splice-numbering "
    "display bug and a leaked dev annotation/template placeholder "
    "surfaced during Pete's own live session, tracked independently, not "
    "part of this row. |"
)

edit("tools/_mob.txt", PATH1_ROW_OLD, PATH1_ROW_NEW)

# --- Section 14 (Locked Decisions Log, ascending -- append after newest tail) ---

CODE_COMPLETE_ENTRY_TAIL = (
    "The live round trip is the explicit remaining step before Path 1 can "
    "be called genuinely live, and requires Pete's action on the "
    "credential-access path (or Pete running the check directly against a "
    "real Preview deployment), not further Claude Code work from this "
    "sandbox. MOB v4.58. |"
)

LIVE_VERIFIED_ENTRY = (
    "| **July 2026 — Path 1 genuinely live-verified (real Preview round "
    "trip)** | Closes the credential-access gap open since Session 71. "
    "Pete completed `vercel login` directly; from the coding sandbox: "
    "`vercel link` → linked to peter-rizzos-projects/prv-3; `vercel env "
    "pull --environment=preview` → confirmed ENGINE_SECRET present "
    "non-empty, ANTHROPIC_API_KEY/UPSTASH_REDIS_REST_URL/"
    "UPSTASH_REDIS_REST_TOKEN all present. **ENGINE_URL confirmed absent "
    "from Preview entirely** (Production only, 38d old) — logged as its "
    "own separate, non-blocking infrastructure item since "
    "resolveEnginePath() (Path 1's actual code path, verified via direct "
    "quote before proceeding) never consults ENGINE_URL at all, only "
    "resolveEngineUrl() (Path B's /api/engine) does. **Fresh Preview "
    "deployment built** via `vercel deploy` from the exact committed HEAD "
    "— uncommitted local changes (the paused /diagnostic reskin, "
    "already-known-uncommitted tools/test_main.py additions) stashed "
    "before deploying and restored immediately after, so the deployment "
    "matched origin/main exactly, not a mix of committed and in-progress "
    "work. **Deployment Protection (SSO gate) blocked external access** — "
    "resolved via Protection Bypass for Automation, a System Environment "
    "Variable Pete confirmed exists dashboard-side (added Jul 17) but "
    "which never surfaces via `vercel env ls`/`env pull` regardless of "
    "system-var exposure settings (other system vars like VERCEL_URL, "
    "VERCEL_GIT_* did come through, ruling out that theory) — likely "
    "deliberate on Vercel's part for a bypass-category secret, not "
    "confirmed beyond that. Pete added it directly to web/.env.local. "
    "**Real round trip executed** (scripted HTTP client, not the browser "
    "UI, but hitting the actual deployed API with real Redis behind it): "
    "session/start → 34+ answers → completion, forcing Q22 option D "
    "deliberately (triggers SEVER-04) and defaulting elsewhere to option "
    "A. Q11's checkpoint fired for real (DIST-CM-01/DIST-CM-02 spliced "
    "live). Q23's own option A (the 'healthy' default) independently "
    "triggered SEVER-05, unplanned — a second, incidental confirmation of "
    "the live splice mechanism beyond the one deliberately engineered. "
    "**Result: tier=Entrenched, score=50.0** — hand-verified against the "
    "raw contribution math (SEVER-04 duration_band=18mo_plus contributes "
    "raw 2.0; SEVER-05 sets only named_condition=False with no "
    "duration_band, defaulting to raw 1.0; total 3.0/6.0×100=50.0, "
    "correctly inside the Entrenched band). **Independently confirmed "
    "outside the app's own API**, querying Upstash directly: "
    "`LRANGE diagnostic-aggregate -3 -1`'s newest entry matched the test "
    "session's completion time, industry, org size, and primary state "
    "exactly; `KEYS diagnostic-session:*` returned empty, confirming the "
    "Transition Rule's delete-on-completion genuinely fired, not assumed "
    "from the HTTP response alone. **Security incident, caught and "
    "contained mid-run:** the first request's Set-Cookie header (a JWT "
    "encoding the bypass secret in its payload) was printed in full "
    "during diagnostic output before redaction was added — the secret "
    "value briefly appeared in this session's tool output. Caught "
    "immediately, script fixed to redact Set-Cookie/Cookie/Authorization/"
    "the bypass header from all subsequent output, no further exposure. "
    "**VERCEL_AUTOMATION_BYPASS_SECRET has been rotated by Pete directly "
    "in the Vercel dashboard and the new value updated in local "
    "web/.env.local — confirmed done.** **Decision Register (Section 13a) "
    "Path 1 row closed** — RESOLVED, no further check-in needed. This is "
    "the first time in this project's history that a live session, "
    "through the real deployed API and real Redis, has produced a "
    "severity tier other than the 'Emerging' constant. MOB v4.59. |"
)

edit("tools/_mob.txt", CODE_COMPLETE_ENTRY_TAIL, CODE_COMPLETE_ENTRY_TAIL + "\n" + LIVE_VERIFIED_ENTRY)

# --- Section 16 (Session Log, descending -- prepend before newest head) ---

CODE_COMPLETE_LOG_HEAD = (
    "| **July 2026 — Path 1 severity wiring complete at the code level, "
    "live verification blocked** | api/engine.py + web/lib/session-store.ts "
    "+ session/answer/route.ts wired to splice SEVER-## follow-ons into a "
    "live sequence and thread collected severity_inputs into completion, "
    "commit c82c67a. tools/test_main.py 36/0, vitest 27/27, tsc clean, "
    "172-profile v23 suite unchanged at 169/172. Hand-verified the real "
    "trigger-out/input-in contract (Q22-D -> SEVER-04 -> tier=Entrenched) "
    "through the actual modified functions. NOT live-verified -- blocked on "
    "the Session 71 credential-access gap (no ENGINE_URL/ENGINE_SECRET, no "
    "authenticated Vercel token in this sandbox), not a new blocker. Live "
    "browser/Redis round trip against Preview is the explicit remaining "
    "step, requires Pete's action. Full detail in Section 14. MOB v4.58. |"
)

LIVE_VERIFIED_LOG_LINE = (
    "| **July 2026 — Path 1 genuinely live-verified (real Preview round "
    "trip)** | Credential-access gap closed by Pete (vercel login/link/env "
    "pull). Deployment Protection bypass resolved via Pete-provisioned "
    "VERCEL_AUTOMATION_BYPASS_SECRET. Real HTTP round trip against a fresh "
    "Preview deployment (exact committed HEAD): session/start -> 38 "
    "answers -> completion, SEVER-04 deliberate + SEVER-05 incidental "
    "follow-ons both fired live, Q11 checkpoint distinguishers fired live, "
    "tier=Entrenched score=50.0, hand-verified against raw math. "
    "Independently confirmed via direct Upstash query (aggregate write "
    "matched, session key deleted per Transition Rule) -- not just trusted "
    "from the app's own response. Bypass secret briefly exposed in tool "
    "output mid-run (JWT in a Set-Cookie header), caught and redacted "
    "immediately, rotated by Pete, confirmed done. Decision Register Path "
    "1 row (open since Session 71) closed RESOLVED. Full detail in "
    "Section 14. MOB v4.59. |"
)

edit("tools/_mob.txt", CODE_COMPLETE_LOG_HEAD, LIVE_VERIFIED_LOG_LINE + "\n" + CODE_COMPLETE_LOG_HEAD)


# ═══════════════════════════════════════════════════════════════════════════
# CLAUDE.md
# ═══════════════════════════════════════════════════════════════════════════

edit(
    "CLAUDE.md",
    "| MOB version | v4.58 |",
    "| MOB version | v4.59 |",
)


# ---------------------------------------------------------------------------

def apply(dry_run: bool):
    changed_files: dict[str, str] = {}
    errors = []

    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = changed_files.get(rel_path)
        if text is None:
            if not path.exists():
                errors.append(f"MISSING FILE: {rel_path}")
                continue
            text = path.read_text(encoding="utf-8")

        count = text.count(old)
        if count != 1:
            errors.append(
                f"{rel_path}: expected 1 match, found {count}\n"
                f"  --- anchor (first 160 chars) ---\n  {old[:160]!r}"
            )
            continue

        changed_files[rel_path] = text.replace(old, new, 1)

    print("=" * 72)
    print(f"MOB PATH1-LIVE-VERIFIED PATCH — {'DRY RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"Files touched: {len(changed_files)}")
    for rel_path in changed_files:
        print(f"  - {rel_path}")

    if errors:
        print("\nERRORS:" if dry_run else "\nERRORS — nothing written:")
        for e in errors:
            print(f"\n[ERROR] {e}")
        if not dry_run:
            sys.exit(1)
        return

    if dry_run:
        print("\nDry run OK — all anchors matched exactly once. No files written.")
        return

    for rel_path, text in changed_files.items():
        (REPO_ROOT / rel_path).write_text(text, encoding="utf-8")
    print("\nAll files written.")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    apply(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
