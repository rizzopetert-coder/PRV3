"""
MOB update: fold the Gemini VII.1 schema review verification pass into the
Visualize Your Data Decision Register row.

Direct file inspection against 014f3f7 corrected the original Gemini
review's citations both ways: 2 of 4 "likely fabricated" flags turned out
to be real (OutputEngine.build(), PrivateOutputBlock), 1 was real but
mischaracterized (tools/test_severity.py), and the actual load-bearing
claim (a strict validate_output() requiring simultaneous whitelist updates)
was false -- the real function is validate_schema(), which only checks
required-field presence and never rejects extra keys. A previously
unidentified real risk was found instead: tools/test_contract.py:178
hardcodes "Exactly 16 top-level fields" (len(output) == 16), which breaks
only if the new field is added top-level rather than nested inside an
existing key.

No code changes. Verification and documentation only.

Version bump: v4.207 -> v4.208 (workstream status materially changed --
the Gemini-review blocker is now framed around verified facts, not the
original review's incorrect claims).

Usage:
    python patch_mob_vyd_gemini_verification.py --dry-run
    python patch_mob_vyd_gemini_verification.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_MD_PATH = Path("CLAUDE.md")

OLD_STATUS = (
    "Verification plan specified: full 172(+3)-profile regression "
    "byte-identical, new engine test coverage against state_severity "
    "directly, tsc/vitest extended, live round trip against real "
    "state_severity output."
)
NEW_STATUS = (
    "Verification plan specified: full 172(+3)-profile regression "
    "byte-identical, new engine test coverage against state_severity "
    "directly, tsc/vitest extended, live round trip against real "
    "state_severity output. **Gemini VII.1 schema review, verification "
    "pass completed 2026-08-20 (direct file inspection against 014f3f7, "
    "not inference):** corrects the initial review's citations in both "
    "directions. CONFIRMED real, not fabricated: `OutputEngine.build()` "
    "(engine/output.py:772, orchestrates `build_private_block()`/"
    "`build_shareable_block()` once per qualified state) and "
    "`PrivateOutputBlock` (Python-side dataclass, engine/output.py:261, "
    "distinct from the TS-side `PrivateOutputPayload`) -- session records "
    "simply hadn't surfaced them before, not a Gemini fabrication. "
    "`tools/test_severity.py` is also real but its actual content "
    "(Section V severity-function tests via a check()/isclose pattern) "
    "carries no VII.1 dict-equality assertions -- the file is real, the "
    "risk attached to it wasn't supported. The cited `validate_output()` "
    "does not exist -- the real function is `validate_schema()` "
    "(engine/contract.py), and reading it in full confirms it only "
    "checks required-field PRESENCE, never rejects extra keys: a purely "
    "additive field passes it with zero whitelist changes needed. "
    "Gemini's \"must update the whitelist simultaneously\" claim is "
    "false. **Real risk found instead, not previously surfaced by "
    "either side:** `tools/test_contract.py:178` hardcodes an exact "
    "top-level field count (`\"Exactly 16 top-level fields\", "
    "len(output) == 16`) -- this breaks (16->17) if Layer 1 adds a new "
    "TOP-LEVEL key, but never triggers if the new field is nested inside "
    "an existing key (e.g. folded into `\"severity\"`) instead. This is "
    "the real open placement question for Gemini's re-review, not the "
    "fictional whitelist-sync risk originally named. Route-path "
    "citations also checked: `web/app/api/dev/diagnostic-preview/route.ts` "
    "and `web/lib/dev-diagnostic-preview.ts` confirmed as two distinct "
    "real objects (a route path and a separate lib file), not a naming "
    "conflict -- both citations were partially right. `ENGINE_VERSION` "
    "confirmed `\"0.2.0\"` at engine/contract.py:50, current HEAD "
    "(014f3f7)."
)

OLD_BLOCKER = (
    "(1) Layer 1 is a locked-contract change and requires its own "
    "Gemini architecture review before execution, per CLAUDE.md's "
    "Architectural Decisions rule -- not yet sent. Open question for "
    "that review: whether a purely additive VII.1 field needs an "
    "ENGINE_VERSION bump (currently 0.2.0) under the section's stated "
    "immutability rule. (2) Audience sequencing -- RESOLVED, Pete "
    "confirmed 2026-08-20: build PrivateOutput.tsx internal-only first; "
    "ShareableOutput.tsx and its P-13 framing deferred to a "
    "separately-gated Phase 2, not bundled into this build."
)
NEW_BLOCKER = (
    "(1) Layer 1 is a locked-contract change and still requires its own "
    "Gemini architecture review before execution, per CLAUDE.md's "
    "Architectural Decisions rule -- not yet sent, now to be framed "
    "around the VERIFIED facts above rather than the original review's "
    "incorrect claims. The original \"whitelist must be updated to avoid "
    "validate_schema() breaking\" concern is retired -- confirmed false "
    "against the real function. Real open question to bring to that "
    "review instead: whether the new field should nest inside an "
    "existing key (e.g. `\"severity\"`) or be added top-level, which "
    "would require updating tools/test_contract.py:178's hardcoded count "
    "from 16 to 17 -- a genuine design fork, not previously identified. "
    "Whether a purely additive VII.1 field needs an ENGINE_VERSION bump "
    "(currently 0.2.0) under the section's stated immutability rule "
    "remains open, not resolved by this verification pass. (2) Audience "
    "sequencing -- RESOLVED, Pete confirmed 2026-08-20: build "
    "PrivateOutput.tsx internal-only first; ShareableOutput.tsx and its "
    "P-13 framing deferred to a separately-gated Phase 2, not bundled "
    "into this build."
)

OLD_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "send Layer 1 for Gemini review -- not time-sensitive, no hard "
    "dependency on other open items. Audience sequencing no longer a "
    "check-in item (resolved above). Still a candidate for the ~August "
    "23 Quarterly Step-Back's forward-planning discussion if Pete wants "
    "to fold it in, but can proceed independently before then. |"
)
NEW_TAIL = (
    " | This session (Claude Code), 2026-08-20 | Pete's call on when to "
    "send the corrected Layer 1 handoff for Gemini review -- not "
    "time-sensitive, no hard dependency on other open items. Audience "
    "sequencing no longer a check-in item (resolved above). Still a "
    "candidate for the ~August 23 Quarterly Step-Back's forward-planning "
    "discussion if Pete wants to fold it in, but can proceed "
    "independently before then. |"
)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    mob_text = MOB_PATH.read_text(encoding="utf-8")

    for label, old, new in [
        ("status column", OLD_STATUS, NEW_STATUS),
        ("blocker column", OLD_BLOCKER, NEW_BLOCKER),
        ("tail (last touched / next check-in)", OLD_TAIL, NEW_TAIL),
    ]:
        count = mob_text.count(old)
        if count != 1:
            raise SystemExit(f"ABORT [{label}]: expected exactly 1 match, found {count}")
        mob_text = mob_text.replace(old, new, 1)

    version_old = "\\\\\\#\\\\\\# MOB v4.207"
    version_new = "\\\\\\#\\\\\\# MOB v4.208"
    count = mob_text.count(version_old)
    if count != 1:
        raise SystemExit(f"ABORT [MOB header version]: expected exactly 1 match, found {count}")
    mob_text = mob_text.replace(version_old, version_new, 1)

    claude_text = CLAUDE_MD_PATH.read_text(encoding="utf-8")
    claude_old = "| MOB version | v4.207 |"
    claude_new = "| MOB version | v4.208 |"
    count = claude_text.count(claude_old)
    if count != 1:
        raise SystemExit(f"ABORT [CLAUDE.md version]: expected exactly 1 match, found {count}")
    claude_text = claude_text.replace(claude_old, claude_new, 1)

    if args.dry_run:
        for path, original, new_text in [
            (MOB_PATH, MOB_PATH.read_text(encoding="utf-8"), mob_text),
            (CLAUDE_MD_PATH, CLAUDE_MD_PATH.read_text(encoding="utf-8"), claude_text),
        ]:
            print(f"\n{'=' * 80}\nDIFF: {path}\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
            )
            print("".join(diff))
        print("\nDry run complete. No files written. Re-run with --write to apply.")
    else:
        MOB_PATH.write_text(mob_text, encoding="utf-8")
        CLAUDE_MD_PATH.write_text(claude_text, encoding="utf-8")
        print(f"WROTE: {MOB_PATH}")
        print(f"WROTE: {CLAUDE_MD_PATH}")


if __name__ == "__main__":
    main()
