"""
Patch tools/_mob.txt: append the Section 16 session closeout entry for
2026-09-07 (end of file, matching the established | Title | Narrative |
Session/date | Next-note | row format), and bump MOB version.

Usage:
    python tools/patch_mob_section16_closeout_20260907.py --dry-run
    python tools/patch_mob_section16_closeout_20260907.py --write
"""
import argparse
import pathlib
import sys

MOB_PATH = pathlib.Path('tools/_mob.txt')

TITLE = (
    "**SESSION CLOSEOUT (2026-09-07, terminal Claude Code) -- three "
    "Quarterly Step-Back items closed (Redis Sensitive-masking, "
    "ssoProtection root-cause, domain reassignment), a net-new homepage "
    "dark/neutral theme bug found and fixed, Redis token rotation "
    "confirmed, Priority Queue resequenced -- MOB v4.280 -> v4.286**"
)

BODY = (
    "Four closed items plus one resequencing action, all live-verified, "
    "not just source-reviewed. (1) Preview Redis credential exposure: "
    "Pete ran `vercel env update UPSTASH_REDIS_REST_URL/TOKEN preview "
    "--sensitive` himself after this session's sandbox correctly refused "
    "to handle the plaintext value directly -- both vars confirmed "
    "`[SENSITIVE]` via a redacted `vercel env pull`, matching Production. "
    "A plaintext token value that landed in the session transcript during "
    "troubleshooting was flagged immediately; Pete separately regenerated "
    "it at Upstash and confirmed app reconnection -- fully closed, not "
    "just the masking fix (Section 13a Redis row updated to reflect "
    "this). (2) `ssoProtection` discrepancy resolved via direct "
    "unauthenticated `curl` A/B testing (production vs. an actual preview "
    "deployment URL, which correctly returned a real `302` to "
    "`vercel.com/sso-api`) plus Vercel's own live docs: root cause is "
    "Hobby-plan Standard Protection scope, which by design exempts the "
    "production domain -- not a misconfiguration. Corrects an earlier "
    "MOB entry (~2026-08-27) that had this exactly backwards. (3) "
    "`principalresolution.com` (+ `www`) reassigned from `prv-2` to "
    "`prv-3` via `vercel domains add --force`, after confirming real "
    "dependencies first (live Google Workspace email via MX/SPF/TXT; "
    "prv-2's own genuinely distinct, if 4-months-stale, marketing site) "
    "-- live-verified post-cutover on the real domain, email confirmed "
    "untouched via fresh `nslookup`. (4) Net-new, not part of the "
    "original Step-Back scope: investigating Pete's own report of a "
    "homepage dark-theme bug found two independent, pre-existing issues. "
    "`.home-scope`'s `--home-paper`/`--home-field-raise`/`--home-slate` "
    "tokens (introduced during the ~2026-08-29 homepage restructure) "
    "never got `[data-theme=\"dark\"]`/`[data-theme=\"neutral\"]` "
    "variants at all -- confirmed live via browser instrumentation "
    "(`body`'s background genuinely switched, `<main>`'s never did). "
    "Fixing that exposed a second bug: `page.tsx`/`WayfindingGrid.tsx`'s "
    "hardcoded `text-charcoal` computed at 1.18:1 contrast once the "
    "background actually went dark -- invisible until the first fix made "
    "it live. Both fixed (`--home-slate` a new, computed-and-verified "
    "value; `--home-ink` mirroring the existing global `--ink` Dark value "
    "exactly, zero new color judgment there). Two Gemini review rounds, "
    "both independently verified rather than trusted: round 1 cited a "
    "fabricated \"v3 Palette Infrastructure\" (a claimed uniform 21-color "
    "grid; the real palette is 16 tokens in an inconsistent 6/5/5 split) "
    "and misquoted P-12's actual text; round 2's underlying facts "
    "(`--ink`/`--color-charcoal` are genuinely distinct tokens) checked "
    "out but mischaracterized what had actually been proposed -- a "
    "one-line misreading, not a fabrication, corrected for the record. "
    "Live-verified on production `principalresolution.com` across all "
    "three themes via `getComputedStyle`, not just screenshots: Warm "
    "unchanged (`#F1F3F1`/`#26241F`), Dark fixed (`#171512`/`#EDEAE3`/"
    "`#5B9BD9`), Neutral unaffected (`#FFFFFF`/`#26241F`). A real "
    "architectural question the fix surfaced but did not act on -- a "
    "`globals.css` comment implying the homepage was meant to be the "
    "first route to fully adopt v2 tokens -- logged as its own parked "
    "Section 13a row, not resolved. (5) Section 13b Priority Queue "
    "rewritten wholesale per Pete's explicit 4-item order (Legal/"
    "Compliance friction-tax wiring, ~30 remaining PARTIAL "
    "coverage-threshold states, `extreme_high_confidence` at 0/1, v2 "
    "token migration) -- previously-tracked items not in that list "
    "(Service Expectations page, SEVER-09, `diagnostic_fast_forward.py`, "
    "OSHA backfill, ADA/FMLA/OSHA gating) explicitly carried forward, not "
    "dropped. A recurring dev-server file-watcher/build-cache staleness "
    "issue surfaced twice mid-session (Turbopack not picking up edits to "
    "an already-running server even after a plain restart, confirmed via "
    "raw network fetch of the served CSS both times, not assumed from a "
    "process restart alone) -- the reliable fix each time was kill "
    "process + clear `.next/` + restart fresh. Files changed: "
    "`CLAUDE.md`, `tools/_mob.txt` (updated at every version step, "
    "v4.280 through v4.286); `web/app/globals.css`, `web/app/page.tsx`, "
    "`web/components/home/WayfindingGrid.tsx` (the two-part homepage "
    "fix); six new `tools/patch_mob_*.py`/`tools/patch_home_scope_*.py` "
    "scripts (dry-run-then-write throughout, zero blind writes); "
    "`.claude/launch.json` (new, genuinely reusable dev-server launch "
    "config). Two separate pushes to production: `b527004` (infra/docs "
    "only) and `3a87611` (the homepage fix, real production-facing "
    "change, live-verified post-deploy both times). Diary write "
    "confirmed successful this session (topic "
    "`session-2026-09-07-homepage-dark-theme-fix-redis-rotation-vercel-infra`)."
)

NEXT_NOTE = (
    "Next Quarterly Step-Back due on or near September 19, 2026, "
    "unchanged. Next session should open per the resequenced Section 13b "
    "Priority Queue: (1) Legal/Compliance friction-tax module wiring -- "
    "Pete's call, code ready either way; (2) PARTIAL coverage-threshold "
    "state verification; (3) `extreme_high_confidence` calibration "
    "investigation; (4) v2 token migration for the homepage, architectural "
    "only, no urgency. `session-handoff-v4.287.md` has the full "
    "files-to-attach breakdown by likely next task."
)


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = MOB_PATH.read_text(encoding='utf-8')

    old_version = "\\\\\\#\\\\\\# MOB v4.286"
    new_version = "\\\\\\#\\\\\\# MOB v4.287"
    if content.count(old_version) != 1:
        print(f'ERROR: version header found {content.count(old_version)} times, expected 1.', file=sys.stderr)
        sys.exit(1)

    new_row = f"\n| {TITLE} | {BODY} | This session (Claude Code), 2026-09-07 | {NEXT_NOTE} |\n"
    new_content = content + new_row
    new_content = new_content.replace(old_version, new_version, 1)

    if args.dry_run:
        print('DRY RUN -- version header found exactly once, append would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        MOB_PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
