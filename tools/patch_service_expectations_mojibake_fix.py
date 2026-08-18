"""
Fix mojibake in prompts/service-expectations-page-draft.md (tracked, committed
d925079, cited in Section 13a as the real Service Expectations draft copy).

Found during the untracked-file-pile inventory: this tracked file's em-dashes
were corrupted to the "â" mojibake pattern (the exact chat-paste corruption
already documented in the 2026-08-17 no-ai-slop session), while its untracked
twin, prompts/service-expectations-draft.md, carries the same content with
clean real em-dashes (U+2014). Byte-verified before writing this script:
normalizing both files' em-dash representations to a common placeholder makes
them byte-for-byte identical -- the mojibake fix is the ONLY difference,
nothing else changed. Same standard as the 2026-08-17 remediation: pure
punctuation correction, zero wording/meaning change.

Usage:
    python tools/patch_service_expectations_mojibake_fix.py --dry-run
    python tools/patch_service_expectations_mojibake_fix.py --write
"""
import argparse
import difflib
from pathlib import Path

CLEAN_SOURCE = Path("prompts/service-expectations-draft.md")
CORRUPTED_TARGET = Path("prompts/service-expectations-page-draft.md")


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    clean_text = CLEAN_SOURCE.read_text(encoding="utf-8")
    corrupted_text = CORRUPTED_TARGET.read_text(encoding="utf-8")

    # Safety check: confirm the two texts are identical once em-dash/mojibake
    # representations are normalized -- abort if anything else differs.
    normalized_clean = clean_text.replace("—", "@@")
    normalized_corrupted = corrupted_text.replace("â", "@@")
    if normalized_clean != normalized_corrupted:
        raise SystemExit(
            "ABORT: files differ beyond em-dash/mojibake -- do not proceed blind."
        )

    mojibake_count = corrupted_text.count("â")
    emdash_count = clean_text.count("—")
    if mojibake_count != emdash_count or mojibake_count == 0:
        raise SystemExit(
            f"ABORT: mojibake count ({mojibake_count}) != em-dash count "
            f"({emdash_count}), or zero -- unexpected state."
        )

    if args.dry_run:
        print(f"Mojibake instances in target today: {mojibake_count}")
        print(f"Real em-dash instances in clean source: {emdash_count}")
        print(f"\n{'=' * 80}\nDIFF: {CORRUPTED_TARGET}\n{'=' * 80}")
        diff = difflib.unified_diff(
            corrupted_text.splitlines(keepends=True),
            clean_text.splitlines(keepends=True),
            fromfile=f"{CORRUPTED_TARGET} (before)",
            tofile=f"{CORRUPTED_TARGET} (after)",
        )
        print("".join(diff))
        print("\nDry run complete. No files written. Re-run with --write to apply.")
    else:
        CORRUPTED_TARGET.write_text(clean_text, encoding="utf-8")
        print(f"WROTE: {CORRUPTED_TARGET}")
        post_text = CORRUPTED_TARGET.read_text(encoding="utf-8")
        post_mojibake = post_text.count("â")
        post_emdash = post_text.count("—")
        print(f"Post-write verification: mojibake={post_mojibake}, em-dash={post_emdash}")
        if post_mojibake != 0 or post_emdash != emdash_count:
            raise SystemExit("POST-WRITE VERIFICATION FAILED -- investigate before proceeding.")


if __name__ == "__main__":
    main()
