"""
PRV3 -- /book Content Architecture Phase 2, Step 2
primaryDimension population -- match/no-match report + gated write.

Per the handoff, this step:
  (a) parses web/data/taxonomy.ts's state list, capturing each state's
      dimension from its section comment (APTITUDE/AUTHORITY/ALLIANCE/
      ATTITUDE), building a name -> (id, dimension) lookup
  (b) for each book-manifest.ts entry, attempts an exact-or-near-exact
      title match against that lookup
  (c) for matched entries (--write only), sets primaryDimension to the
      matched state's dimension and stateIds to [matched state id]
  (d) for unmatched entries, lists them -- no dimension is guessed

Matching is deliberately conservative: normalized equality only (case,
whitespace, apostrophe style, "&"/"and", and a symmetric "the " strip).
No substring/containment matching -- the taxonomy has near-duplicate
names by design (e.g. "Decision Blindness" vs. "Sequential Decision
Blindness" are two different states in two different dimensions), and
a containment match would silently cross-wire them.

--dry-run prints the full match/no-match report and writes nothing.
--write requires --dry-run to have been reviewed first (this script
does not enforce that mechanically -- Pete's review gate is procedural,
per the handoff: do not proceed past the dry-run without it) and only
ever touches MATCHED entries. Unmatched entries are never written with
a guessed value, in either mode.

Usage:
  python tools/report_book_dimension_match_s2.py --dry-run
  python tools/report_book_dimension_match_s2.py --write
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TAXONOMY_FILE = REPO_ROOT / "web" / "data" / "taxonomy.ts"
MANIFEST_FILE = REPO_ROOT / "web" / "lib" / "book-manifest.ts"

DIMENSION_MARKERS = {
    "APTITUDE": "aptitude",
    "AUTHORITY": "authority",
    "ALLIANCE": "alliance",
    "ATTITUDE": "attitude",
}


def normalize(s: str) -> str:
    s = s.lower()
    s = s.replace("’", "'").replace("‘", "'")
    s = s.replace("&", " and ")
    s = re.sub(r"[^a-z0-9' ]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    if s.startswith("the "):
        s = s[4:]
    return s


def parse_taxonomy_states(text: str) -> list[tuple[str, str, str]]:
    """Returns list of (id, name, dimension) bounded to the states array."""
    start_marker = "export const states: State[] = ["
    start = text.index(start_marker)
    # states array closes at the first top-level "];" after start
    end = text.index("\n];", start)
    body = text[start:end]

    results: list[tuple[str, str, str]] = []
    current_dim: str | None = None
    pending_id: str | None = None

    for line in body.splitlines():
        stripped = line.strip()
        marker_match = re.match(r"//\s*(APTITUDE|AUTHORITY|ALLIANCE|ATTITUDE)\b", stripped)
        if marker_match:
            current_dim = DIMENSION_MARKERS[marker_match.group(1)]
            continue
        id_match = re.match(r'id:\s*"([^"]+)"', stripped)
        if id_match:
            pending_id = id_match.group(1)
            continue
        name_match = re.match(r'name:\s*"([^"]+)"', stripped)
        if name_match and pending_id is not None:
            if current_dim is None:
                print(f"ERROR: state {pending_id} has no dimension context", file=sys.stderr)
                sys.exit(1)
            results.append((pending_id, name_match.group(1), current_dim))
            pending_id = None

    return results


def parse_manifest_entries(text: str) -> list[tuple[str, str]]:
    """Returns list of (id, title) for every book-manifest entry, in order."""
    blocks = re.findall(r'\{\s*id: "[^"]+".*?\n  \},', text, re.DOTALL)
    results = []
    for b in blocks:
        idm = re.search(r'id: "([^"]+)"', b)
        titlem = re.search(r'title: "((?:[^"\\]|\\.)*)"', b)
        if not idm or not titlem:
            print(f"ERROR: could not extract id/title from block starting {b[:60]!r}", file=sys.stderr)
            sys.exit(1)
        results.append((idm.group(1), titlem.group(1)))
    return results


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    taxonomy_text = TAXONOMY_FILE.read_text(encoding="utf-8")
    manifest_text = MANIFEST_FILE.read_text(encoding="utf-8")

    states = parse_taxonomy_states(taxonomy_text)
    print(f"Parsed {len(states)} states from taxonomy.ts (expect 57)")

    name_lookup: dict[str, tuple[str, str, str]] = {}  # normalized -> (id, name, dim)
    dupe_normalized = set()
    for state_id, name, dim in states:
        norm = normalize(name)
        if norm in name_lookup:
            dupe_normalized.add(norm)
        name_lookup[norm] = (state_id, name, dim)
    if dupe_normalized:
        print(f"WARNING: {len(dupe_normalized)} normalized name collisions among states: {dupe_normalized}", file=sys.stderr)

    entries = parse_manifest_entries(manifest_text)
    print(f"Parsed {len(entries)} entries from book-manifest.ts (expect 88)")
    print("=" * 100)

    matched: list[tuple[str, str, str, str, str]] = []  # piece_id, title, state_id, state_name, dim
    unmatched: list[tuple[str, str]] = []

    for piece_id, title in entries:
        norm = normalize(title)
        hit = name_lookup.get(norm)
        if hit:
            state_id, state_name, dim = hit
            matched.append((piece_id, title, state_id, state_name, dim))
        else:
            unmatched.append((piece_id, title))

    print(f"\nMATCHED ({len(matched)}):")
    print(f"{'piece_id':<10} {'title':<55} {'state_id':<35} {'dimension'}")
    print("-" * 100)
    for piece_id, title, state_id, state_name, dim in matched:
        print(f"{piece_id:<10} {title:<55} {state_id:<35} {dim}")

    print(f"\nUNMATCHED ({len(unmatched)}) -- no dimension guessed, Pete review required:")
    print(f"{'piece_id':<10} {'title'}")
    print("-" * 100)
    for piece_id, title in unmatched:
        print(f"{piece_id:<10} {title}")

    print("\n" + "=" * 100)
    print(f"SUMMARY: {len(matched)} matched, {len(unmatched)} unmatched, {len(entries)} total")

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    print("\n--write: applying primaryDimension + stateIds to MATCHED entries only.")
    new_text = manifest_text
    applied = 0
    for piece_id, title, state_id, state_name, dim in matched:
        block_pattern = re.compile(r'(\{\s*id: "' + re.escape(piece_id) + r'".*?\n  \},)', re.DOTALL)
        m = block_pattern.search(new_text)
        if not m:
            print(f"ERROR: could not locate block for {piece_id} during write", file=sys.stderr)
            sys.exit(1)
        block = m.group(1)
        if "primaryDimension" in block:
            print(f"SKIP: {piece_id} already has primaryDimension, not overwriting", file=sys.stderr)
            continue
        # Insert before the closing "  },": add primaryDimension + stateIds as the last fields.
        insert = f'    primaryDimension: "{dim}",\n    stateIds: ["{state_id}"],\n  }},'
        new_block = block[: -len("\n  },")] + "\n" + insert
        new_text = new_text.replace(block, new_block, 1)
        applied += 1

    MANIFEST_FILE.write_text(new_text, encoding="utf-8")
    print(f"WROTE {MANIFEST_FILE.relative_to(REPO_ROOT)} -- {applied} entries updated, {len(unmatched)} left untouched (unmatched).")


if __name__ == "__main__":
    main()
