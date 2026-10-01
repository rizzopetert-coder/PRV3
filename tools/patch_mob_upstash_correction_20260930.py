"""
Correction to the v4.330 Upstash lines (2026-09-30, Pete).

web/.env.local has no Upstash credentials, deliberately. The root .env.local held credentials for a database that
is not on Pete's Upstash account, and its PING rate-limit error is unrelated to production. The v4.330 lines
conflated the two files. Edits tools/_mob.txt in place (three exact-match replacements) and regenerates
prompts/session-handoff-v4.330.md from the corrected Section 16 entry.

Usage:
  python tools/patch_mob_upstash_correction_20260930.py --dry-run
  python tools/patch_mob_upstash_correction_20260930.py --write
"""
import importlib.util
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MOB = ROOT / "tools" / "_mob.txt"
HANDOFF = ROOT / "prompts" / "session-handoff-v4.330.md"

OLD_13B_ITEM_START = "- The `.env.local` Upstash database returned a rate-limit error on PING (2026-09-30)."
NEW_13B_ITEM = (
    "- Upstash (checked by Pete 2026-09-30): `web/.env.local` has no Upstash credentials, deliberately "
    "(`vercel env pull` writes [SENSITIVE] placeholders). The root `.env.local` held credentials for a database that is "
    "not on Pete's Upstash account (deleted or foreign). Its PING rate-limit error on 2026-09-30 is unrelated to "
    "production, which was unaffected (tagged session start and answer returned 200, no runtime errors in 24 hours). "
    "Nothing in the repo reads the root `.env.local`'s Upstash entries (grep, 2026-09-30), so they were removed from "
    "it. CORRECTS the v4.330 line \"present in .env.local but rate-limited\", which conflated the two files. The "
    "pre-v4.330 line \"missing\" was right for `web/.env.local`."
)

OLD_INFRA_START = "- Local dev Upstash Redis credentials are present in `.env.local`, not missing"
NEW_INFRA = (
    "- Local dev Upstash Redis credentials are absent from `web/.env.local` by design (`vercel env pull` writes "
    "[SENSITIVE] placeholders), informational only, production has its own. The stale root `.env.local` entries (a "
    "database not on Pete's account) were removed 2026-09-30. See the open item above."
)

OLD_S16_START = "- The `.env.local` Upstash database returned a rate-limit error on PING. Production was unaffected."
NEW_S16 = (
    "- Upstash (checked by Pete 2026-09-30): `web/.env.local` has no Upstash credentials, deliberately. The root "
    "`.env.local` held credentials for a database not on Pete's Upstash account (deleted or foreign), and its PING "
    "rate-limit error is unrelated to production. CORRECTS the v4.330 line \"present in .env.local but rate-limited\", "
    "which conflated the two files. The dead entries were removed from the root file (nothing in the repo reads them)."
)

S16_START = "## SESSION CLOSEOUT (2026-09-30, terminal Claude Code)"


def swap(lines, prefix, new, label):
    hits = [i for i, l in enumerate(lines) if l.startswith(prefix)]
    if not hits and any(l == new for l in lines):  # already applied, idempotent
        return [i for i, l in enumerate(lines) if l == new][0]
    assert len(hits) == 1, f"{label}: expected 1 match, got {len(hits)}"
    lines[hits[0]] = new
    return hits[0]


# Stale phrases left in the 13b "Last updated" line and Section 16 item 6 by the v4.330 closeout.
SUBSTRINGS = [
    ("the Upstash infrastructure line (credentials present, database rate-limited)",
     "the Upstash infrastructure line (credentials absent from `web/.env.local` by design, stale root entries removed)"),
    ("Upstash rate-limit item,", "Upstash env-file item,"),
]


def apply_substrings(text):
    for old, new in SUBSTRINGS:
        if old in text:
            text = text.replace(old, new)
    return text


def main():
    mode = "--write" if "--write" in sys.argv else "--dry-run"
    text = MOB.read_text(encoding="utf-8")
    nl = "\r\n" if "\r\n" in text else "\n"
    lines = text.split(nl)
    a = swap(lines, OLD_13B_ITEM_START, NEW_13B_ITEM, "13b item")
    b = swap(lines, OLD_INFRA_START, NEW_INFRA, "13b infra line")
    c = swap(lines, OLD_S16_START, NEW_S16, "section 16 item 4")
    new_text = apply_substrings(nl.join(lines))
    lines = new_text.split(nl)

    # handoff: regenerate from the corrected Section 16 entry only
    s16_idx = [i for i, l in enumerate(lines) if l.startswith(S16_START)]
    assert len(s16_idx) == 1
    entry = "\n".join(lines[s16_idx[0]:]).rstrip("\n") + "\n"
    spec = importlib.util.spec_from_file_location("closeout", ROOT / "tools" / "patch_mob_session_closeout_20260930.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    handoff = mod.build_handoff(entry)

    new_bits = NEW_13B_ITEM + NEW_INFRA + NEW_S16
    print("semicolons/em-dashes in new text:", [ch for ch in (";", "—") if ch in new_bits] or "none")
    print(f"edited MOB lines {a+1} (13b item), {b+1} (13b infra), {c+1} (Section 16 item 4)")
    print("handoff chars:", len(handoff))
    if mode == "--write":
        MOB.write_text(new_text, encoding="utf-8")
        HANDOFF.write_text(handoff, encoding="utf-8")
        print("written")
    else:
        print("[dry-run] nothing written")


if __name__ == "__main__":
    main()
