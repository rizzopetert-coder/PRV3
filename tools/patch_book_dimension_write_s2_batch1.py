"""
PRV3 -- /book Content Architecture Phase 2, Step 2, confident batch 1
Applies Pete's manually-reviewed primaryDimension (+ stateIds where
noted) assignments to 28 previously-unmatched entries, plus a partial
write (stateIds only, no primaryDimension) to LIB-014.

Every value below was supplied directly by Pete in this session, not
guessed or inferred by this script. This script's job is mechanical
application plus pre-flight verification:
  1. WRITE_IDS | PARTIAL_IDS | HOLD_IDS must exactly partition the 42
     entries Step 2's dry-run found unmatched -- no gaps, no overlaps,
     no entries outside that set.
  2. None of the WRITE/PARTIAL entries may already carry primaryDimension
     or stateIds (they should still be untouched from Step 2's dry run).
  3. Every stateIds value must exist as a real id in web/data/taxonomy.ts.
  4. LIB-052's relatedSlug must still be "paper-shield" (the basis Pete
     cited for its stateIds assignment) -- abort if it has changed.

HOLD entries are never touched by this script, in either mode.

Usage:
  python tools/patch_book_dimension_write_s2_batch1.py --dry-run
  python tools/patch_book_dimension_write_s2_batch1.py --write
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_FILE = REPO_ROOT / "web" / "data" / "taxonomy.ts"
MANIFEST_FILE = REPO_ROOT / "web" / "lib" / "book-manifest.ts"

# piece_id -> (dimension, stateIds-or-None)
WRITE: dict[str, tuple[str, list[str] | None]] = {
    "FTA-03": ("authority", None),
    "FTA-06": ("authority", None),
    "FTA-10": ("authority", None),
    "FTA-11": ("authority", None),
    "FTA-04": ("aptitude", None),
    "FTA-12": ("attitude", None),
    "LIB-013": ("attitude", None),
    "LIB-015": ("attitude", None),
    "LIB-016": ("attitude", None),
    "LIB-018": ("attitude", None),
    "LIB-019": ("attitude", None),
    "LIB-020": ("attitude", None),
    "LIB-024": ("attitude", None),
    "LIB-043": ("attitude", None),
    "LIB-048": ("attitude", None),
    "LIB-017": ("authority", None),
    "LIB-022": ("authority", None),
    "LIB-032": ("authority", None),
    "LIB-033": ("authority", None),
    "LIB-046": ("authority", None),
    "LIB-049": ("authority", None),
    "LIB-023": ("aptitude", None),
    "LIB-029": ("aptitude", None),
    "LIB-031": ("alliance", None),
    "LIB-044": ("alliance", ["silosolation"]),
    "LIB-045": ("attitude", ["the_broken_compass"]),
    "LIB-047": ("authority", ["decision_paralysis"]),
    "LIB-052": ("authority", ["paper_shield"]),
}

# piece_id -> stateIds only, no primaryDimension
PARTIAL: dict[str, list[str]] = {
    "LIB-014": ["the_overloaded_manager", "the_founders_grip"],
}

HOLD = {
    "FTA-17", "LIB-037",
    "LIB-021", "LIB-025", "LIB-026", "LIB-027", "LIB-028", "LIB-030",
    "LIB-034", "LIB-035", "LIB-036", "LIB-050", "LIB-051",
}

DIMENSION_MARKERS = {
    "APTITUDE": "aptitude", "AUTHORITY": "authority",
    "ALLIANCE": "alliance", "ATTITUDE": "attitude",
}


def normalize(s: str) -> str:
    s = s.lower().replace("’", "'").replace("‘", "'").replace("&", " and ")
    s = re.sub(r"[^a-z0-9' ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if s.startswith("the "):
        s = s[4:]
    return s


def parse_taxonomy_state_ids(text: str) -> set[str]:
    start = text.index("export const states: State[] = [")
    end = text.index("\n];", start)
    body = text[start:end]
    ids = set()
    for line in body.splitlines():
        m = re.match(r'\s*id:\s*"([^"]+)"', line)
        if m:
            ids.add(m.group(1))
    return ids


def parse_taxonomy_name_lookup(text: str) -> dict[str, str]:
    start = text.index("export const states: State[] = [")
    end = text.index("\n];", start)
    body = text[start:end]
    lookup = {}
    cur = None
    pend = None
    for line in body.splitlines():
        s = line.strip()
        mm = re.match(r"//\s*(APTITUDE|AUTHORITY|ALLIANCE|ATTITUDE)\b", s)
        if mm:
            cur = DIMENSION_MARKERS[mm.group(1)]
            continue
        im = re.match(r'id:\s*"([^"]+)"', s)
        if im:
            pend = im.group(1)
            continue
        nm = re.match(r'name:\s*"([^"]+)"', s)
        if nm and pend:
            lookup[normalize(nm.group(1))] = pend
            pend = None
    return lookup


def get_manifest_blocks(text: str) -> list[str]:
    return re.findall(r'\{\s*id: "[^"]+".*?\n  \},', text, re.DOTALL)


def get_entry(text: str, piece_id: str) -> tuple[str, str]:
    """Returns (block, title)."""
    for b in get_manifest_blocks(text):
        idm = re.search(r'id: "([^"]+)"', b)
        if idm.group(1) == piece_id:
            tm = re.search(r'title: "((?:[^"\\]|\\.)*)"', b)
            return b, (tm.group(1) if tm else "")
    raise SystemExit(f"ERROR: entry {piece_id} not found in manifest")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    taxonomy_text = TAXONOMY_FILE.read_text(encoding="utf-8")
    manifest_text = MANIFEST_FILE.read_text(encoding="utf-8")

    # --- Pre-flight check 1: recompute Step 2's unmatched set fresh, confirm partition ---
    name_lookup = parse_taxonomy_name_lookup(taxonomy_text)
    blocks = get_manifest_blocks(manifest_text)
    unmatched_now = set()
    for b in blocks:
        idm = re.search(r'id: "([^"]+)"', b)
        tm = re.search(r'title: "((?:[^"\\]|\\.)*)"', b)
        piece_id, title = idm.group(1), (tm.group(1) if tm else "")
        if normalize(title) not in name_lookup:
            unmatched_now.add(piece_id)

    write_ids = set(WRITE.keys())
    partial_ids = set(PARTIAL.keys())
    combined = write_ids | partial_ids | HOLD

    print(f"Unmatched entries recomputed fresh: {len(unmatched_now)} (expect 42)")
    print(f"WRITE={len(write_ids)} PARTIAL={len(partial_ids)} HOLD={len(HOLD)} combined={len(combined)}")

    missing_from_combined = unmatched_now - combined
    extra_in_combined = combined - unmatched_now
    overlap_write_partial = write_ids & partial_ids
    overlap_write_hold = write_ids & HOLD
    overlap_partial_hold = partial_ids & HOLD

    problems = []
    if unmatched_now != combined:
        problems.append(f"Partition mismatch. In unmatched but not covered: {missing_from_combined}. Covered but not unmatched: {extra_in_combined}")
    if overlap_write_partial:
        problems.append(f"IDs in both WRITE and PARTIAL: {overlap_write_partial}")
    if overlap_write_hold:
        problems.append(f"IDs in both WRITE and HOLD: {overlap_write_hold}")
    if overlap_partial_hold:
        problems.append(f"IDs in both PARTIAL and HOLD: {overlap_partial_hold}")
    if len(write_ids) != 28:
        problems.append(f"Expected 28 WRITE entries, got {len(write_ids)}")
    if len(partial_ids) != 1:
        problems.append(f"Expected 1 PARTIAL entry, got {len(partial_ids)}")

    if problems:
        print("ABORT -- pre-flight partition check failed:", file=sys.stderr)
        for p in problems:
            print("  - " + p, file=sys.stderr)
        sys.exit(1)
    print("Partition check PASSED -- WRITE+PARTIAL+HOLD exactly cover the 42 unmatched entries, no overlaps.")

    # --- Pre-flight check 2: none of WRITE/PARTIAL already carry primaryDimension/stateIds ---
    for piece_id in write_ids | partial_ids:
        block, _ = get_entry(manifest_text, piece_id)
        if "primaryDimension" in block or "stateIds" in block:
            print(f"ABORT -- {piece_id} already has primaryDimension or stateIds set", file=sys.stderr)
            sys.exit(1)
    print("Pre-existing-field check PASSED -- none of the 29 target entries already carry primaryDimension/stateIds.")

    # --- Pre-flight check 3: every referenced stateIds value is a real taxonomy id ---
    taxonomy_ids = parse_taxonomy_state_ids(taxonomy_text)
    referenced_ids = set()
    for dim, sids in WRITE.values():
        if sids:
            referenced_ids.update(sids)
    for sids in PARTIAL.values():
        referenced_ids.update(sids)
    unknown_ids = referenced_ids - taxonomy_ids
    if unknown_ids:
        print(f"ABORT -- these stateIds are not real taxonomy.ts ids: {unknown_ids}", file=sys.stderr)
        sys.exit(1)
    print(f"Taxonomy id check PASSED -- all {len(referenced_ids)} referenced stateIds exist in taxonomy.ts.")

    # --- Pre-flight check 4: LIB-052 relatedSlug unchanged ---
    lib052_block, _ = get_entry(manifest_text, "LIB-052")
    if 'relatedSlug: "paper-shield"' not in lib052_block:
        print("ABORT -- LIB-052's relatedSlug is not \"paper-shield\" as expected", file=sys.stderr)
        sys.exit(1)
    print("LIB-052 relatedSlug check PASSED -- still \"paper-shield\".")

    print("=" * 100)

    # --- Build edits ---
    new_text = manifest_text
    rows = 0

    def apply_edit(piece_id: str, insert_lines: list[str]) -> None:
        nonlocal new_text, rows
        block, title = get_entry(new_text, piece_id)
        insert = "\n".join(insert_lines)
        new_block = block[: -len("\n  },")] + "\n" + insert + "\n  },"
        print(f"\n--- {piece_id} ({title[:60]}) ---")
        for line in insert_lines:
            print("  + " + line)
        new_text = new_text.replace(block, new_block, 1)
        rows += 1

    for piece_id in sorted(WRITE.keys()):
        dim, sids = WRITE[piece_id]
        lines = [f'    primaryDimension: "{dim}",']
        if sids:
            sid_list = ", ".join(f'"{s}"' for s in sids)
            lines.append(f"    stateIds: [{sid_list}],")
        apply_edit(piece_id, lines)

    for piece_id in sorted(PARTIAL.keys()):
        sids = PARTIAL[piece_id]
        sid_list = ", ".join(f'"{s}"' for s in sids)
        apply_edit(piece_id, [f"    stateIds: [{sid_list}],"])

    print("\n" + "=" * 100)
    print(f"Rows touched: {rows} (expect 29 = 28 full writes + 1 partial)")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    MANIFEST_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {MANIFEST_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
