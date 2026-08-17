"""
PRV3 -- diagnostic, read-only. Mines recurring n-grams (3-8 word phrases)
and near-exact duplicate sentences/clauses across every shipped taxonomy
description/definition source, as raw material for a future /book/toc
plainspoken-filter-category redesign (replacing filtering by dimension/
signature). Investigation only -- writes findings to a report file, does
not touch any /book or /book/toc source.

Sources mined (live/current versions, confirmed via direct file read,
not assumed from memory):
  1. web/data/taxonomy.ts        -- states[].description (58)
  2. web/data/taxonomy.ts        -- signatures[].description (5)
  3. web/data/taxonomy.ts        -- signatures[].coexistenceInterpretation (5)
  4. engine/resolution_families.py -- RESOLUTION_FALLBACK_COPY values (~18)
  5. web/lib/book-state-index.ts -- BOOK_STATE_INDEX[].descriptiveProse (58)
     -- CONFIRMED DISTINCT from source 1: mirrors engine/data/states.py's
     descriptive_prose, a genuinely different body of copy for the same
     58 states, not a duplicate of taxonomy.ts's description field.
  6. web/lib/book-taxonomy-labels.ts -- PUBLIC_DIMENSION_LABELS (4, title+description)
  7. web/app/book/toc/page.tsx   -- SIGNATURE_DEFINITIONS (5)
     -- CONFIRMED DISTINCT from source 2/3: a third, shorter body of
     signature-level copy, authored for the Gestalt Pass Terminology Guide.
  8. web/components/ConstellationField.tsx -- GESTALT_INFO (title + 3 points)

Method: extract every string via source-specific regex (verified against
expected counts -- 58 states, 5 signatures, etc. -- before trusting any
extraction), split into sentences, generate word n-grams (3-8 words) per
sentence so a phrase never spans a sentence boundary, count frequency
across the whole corpus, and separately flag sentence-level near-exact
duplicates via a normalized-token Jaccard/subsequence check.

Usage:
  python tools/diag_book_toc_glossary_intersection.py
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

STOP_SINGLE = set()  # single-word noise filtering handled by n>=3 requirement instead

# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

Entry = tuple[str, str, str]  # (source_label, entry_id, text)


def _unescape(s: str) -> str:
    return s.replace('\\"', '"').replace("\\'", "'").replace("\\n", " ")


def extract_taxonomy_states() -> list[Entry]:
    path = REPO_ROOT / "web" / "data" / "taxonomy.ts"
    text = path.read_text(encoding="utf-8")
    block_start = text.index("export const states: State[]")
    block_end = text.index("export const signatures: Signature[]")
    block = text[block_start:block_end]
    entries = []
    for m in re.finditer(
        r'id:\s*"([^"]+)".*?description:\s*\n?\s*"((?:[^"\\]|\\.)*)"',
        block,
        re.DOTALL,
    ):
        sid, desc = m.group(1), _unescape(m.group(2))
        entries.append(("taxonomy.ts state description", sid, desc))
    return entries


def extract_taxonomy_signatures() -> list[Entry]:
    path = REPO_ROOT / "web" / "data" / "taxonomy.ts"
    text = path.read_text(encoding="utf-8")
    block_start = text.index("export const signatures: Signature[]")
    block = text[block_start:]
    entries = []
    # split into per-signature chunks on "id:" boundaries
    chunks = re.split(r"\n  \{\n\s*id:", block)[1:]
    for chunk in chunks:
        id_m = re.match(r'\s*"([^"]+)"', chunk)
        sid = id_m.group(1) if id_m else "?"
        desc_m = re.search(r'description:\s*\n?\s*"((?:[^"\\]|\\.)*)"', chunk)
        coex_m = re.search(r'coexistenceInterpretation:\s*\n?\s*"((?:[^"\\]|\\.)*)"', chunk)
        if desc_m:
            entries.append(("taxonomy.ts signature description", sid, _unescape(desc_m.group(1))))
        if coex_m:
            entries.append(("taxonomy.ts signature coexistenceInterpretation", sid, _unescape(coex_m.group(1))))
    return entries


def extract_resolution_fallback_copy() -> list[Entry]:
    path = REPO_ROOT / "engine" / "resolution_families.py"
    text = path.read_text(encoding="utf-8")
    block_start = text.index("RESOLUTION_FALLBACK_COPY")
    block_end = text.index("\n}", block_start)
    # find the real closing brace of the dict literal, not the first "\n}"
    # (dict spans to a top-level "}\n" at column 0) -- locate precisely
    depth = 0
    i = text.index("{", block_start)
    j = i
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    block = text[block_start:j]
    entries = []
    for m in re.finditer(
        r'\("([^"]+)",\s*"?([A-Za-z]+)"?\):\s*\(\s*((?:"(?:[^"\\]|\\.)*"\s*)+)\)',
        block,
    ):
        family, tier = m.group(1), m.group(2)
        raw_strings = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(3))
        joined = " ".join(_unescape(s) for s in raw_strings)
        entries.append(("resolution_families.py RESOLUTION_FALLBACK_COPY", f"{family} / {tier}", joined))
    return entries


def extract_book_state_index() -> list[Entry]:
    path = REPO_ROOT / "web" / "lib" / "book-state-index.ts"
    text = path.read_text(encoding="utf-8")
    entries = []
    for m in re.finditer(
        r'id:\s*"([^"]+)".*?descriptiveProse:\s*"((?:[^"\\]|\\.)*)"',
        text,
        re.DOTALL,
    ):
        sid, desc = m.group(1), _unescape(m.group(2))
        entries.append(("book-state-index.ts descriptiveProse", sid, desc))
    return entries


def extract_dimension_labels() -> list[Entry]:
    path = REPO_ROOT / "web" / "lib" / "book-taxonomy-labels.ts"
    text = path.read_text(encoding="utf-8")
    entries = []
    for m in re.finditer(
        r'(\w+):\s*\{\s*title:\s*"([^"]+)",\s*description:\s*"([^"]+)"',
        text,
    ):
        dim, title, desc = m.group(1), m.group(2), m.group(3)
        entries.append(("book-taxonomy-labels.ts PUBLIC_DIMENSION_LABELS", f"{dim} (title)", title))
        entries.append(("book-taxonomy-labels.ts PUBLIC_DIMENSION_LABELS", f"{dim} (description)", desc))
    return entries


def extract_signature_definitions() -> list[Entry]:
    path = REPO_ROOT / "web" / "app" / "book" / "toc" / "page.tsx"
    text = path.read_text(encoding="utf-8")
    block_start = text.index("SIGNATURE_DEFINITIONS")
    block_end = text.index("\n};", block_start)
    block = text[block_start:block_end]
    entries = []
    for m in re.finditer(r'(\w+):\s*\n?\s*"((?:[^"\\]|\\.)*)"', block):
        sid, desc = m.group(1), _unescape(m.group(2))
        entries.append(("page.tsx SIGNATURE_DEFINITIONS (Gestalt Pass)", sid, desc))
    return entries


def extract_gestalt_info() -> list[Entry]:
    path = REPO_ROOT / "web" / "components" / "ConstellationField.tsx"
    text = path.read_text(encoding="utf-8")
    block_start = text.index("GESTALT_INFO")
    block_end = text.index("};", block_start)
    block = text[block_start:block_end]
    entries = []
    title_m = re.search(r'title:\s*"([^"]+)"', block)
    if title_m:
        entries.append(("ConstellationField.tsx GESTALT_INFO", "title", title_m.group(1)))
    for i, pt in enumerate(re.findall(r'"((?:[^"\\]|\\.)*)"', block)[1:], 1):
        entries.append(("ConstellationField.tsx GESTALT_INFO", f"point {i}", _unescape(pt)))
    return entries


# ---------------------------------------------------------------------------
# N-gram mining
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    # Simple sentence splitter -- good enough for this corpus's plain prose
    # (no abbreviations/decimals that would confuse a period split).
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def tokenize(sentence: str) -> list[str]:
    # Lowercase, strip surrounding punctuation per token, keep internal
    # apostrophes (don't -> don't, not do -> n t).
    words = re.findall(r"[A-Za-z']+", sentence.lower())
    return words


def ngrams(words: list[str], n: int) -> list[str]:
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]


def main() -> None:
    all_entries: list[Entry] = []
    all_entries += extract_taxonomy_states()
    all_entries += extract_taxonomy_signatures()
    all_entries += extract_resolution_fallback_copy()
    all_entries += extract_book_state_index()
    all_entries += extract_dimension_labels()
    all_entries += extract_signature_definitions()
    all_entries += extract_gestalt_info()

    # Sanity counts, printed for verification before trusting anything downstream
    counts_by_source: dict[str, int] = defaultdict(int)
    for src, _id, _text in all_entries:
        counts_by_source[src] += 1
    print("=== Extraction sanity counts ===")
    for src, c in counts_by_source.items():
        print(f"  {src}: {c}")
    print()

    # Build sentence-level corpus with provenance
    sentence_records: list[tuple[str, str, str]] = []  # (source, entry_id, sentence)
    for src, entry_id, text in all_entries:
        for sent in split_sentences(text):
            sentence_records.append((src, entry_id, sent))

    # N-gram frequency (3-8 words), phrase -> set of (source, entry_id)
    phrase_occurrences: dict[str, set[tuple[str, str]]] = defaultdict(set)
    for src, entry_id, sent in sentence_records:
        words = tokenize(sent)
        for n in range(3, 9):
            for gram in ngrams(words, n):
                phrase_occurrences[gram].add((src, entry_id))

    # Only phrases appearing across >=2 DISTINCT entries count as "recurring"
    # (same phrase appearing twice within one entry's own text is not cross-
    # taxonomy recurrence). Rank by distinct-entry count, then phrase length
    # (longer phrase = stronger signal) as tiebreak.
    recurring = [
        (phrase, occ) for phrase, occ in phrase_occurrences.items()
        if len(occ) >= 2
    ]
    recurring.sort(key=lambda x: (-len(x[1]), -len(x[0].split())))

    print(f"=== {len(recurring)} recurring phrases (3-8 words, appear in >=2 distinct entries) ===\n")
    for phrase, occ in recurring[:200]:
        entries_str = "; ".join(f"{src} :: {eid}" for src, eid in sorted(occ))
        print(f"[{len(occ)}x, {len(phrase.split())}w] \"{phrase}\"")
        print(f"    -> {entries_str}")
    print()

    # Near-exact sentence duplicates: for every pair of sentences from
    # DIFFERENT entries, compute similarity via longest common SUBSEQUENCE
    # (order-preserving, gaps allowed) as % of the shorter sentence's word
    # count. A pure longest-CONTIGUOUS-run metric under-counts the exact
    # "same template, one clause swapped" pattern this task is looking for
    # -- e.g. "...couldn't live with EITHER OPTION have already left" vs
    # "...couldn't live with THAT have already left" shares two separate
    # contiguous runs (a 7-word prefix, a 3-word suffix) that a contiguous-
    # only measure scores far lower than the sentences actually are. LCS
    # correctly credits both runs as one shared skeleton with a swapped
    # middle clause, matching how a human reader would judge these as the
    # same class of duplicate.
    def lcs_len(a: list[str], b: list[str]) -> int:
        m, n = len(a), len(b)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        for x in range(1, m + 1):
            for y in range(1, n + 1):
                if a[x - 1] == b[y - 1]:
                    dp[x][y] = dp[x - 1][y - 1] + 1
                else:
                    dp[x][y] = max(dp[x - 1][y], dp[x][y - 1])
        return dp[m][n]

    print("=== Near-exact duplicate sentences/clauses (LCS >=65% of shorter sentence's words) ===\n")
    seen_pairs = set()
    found: list[tuple[float, int, int, str, str, str, str, str, str]] = []
    for i in range(len(sentence_records)):
        src_i, id_i, sent_i = sentence_records[i]
        words_i = tokenize(sent_i)
        if len(words_i) < 5:
            continue
        for j in range(i + 1, len(sentence_records)):
            src_j, id_j, sent_j = sentence_records[j]
            if src_i == src_j and id_i == id_j:
                continue
            words_j = tokenize(sent_j)
            if len(words_j) < 5:
                continue
            shorter_len = min(len(words_i), len(words_j))
            best = lcs_len(words_i, words_j)
            ratio = best / shorter_len
            if ratio >= 0.65:
                key = tuple(sorted([sent_i, sent_j]))
                if key in seen_pairs:
                    continue
                seen_pairs.add(key)
                found.append((ratio, best, shorter_len, src_i, id_i, sent_i, src_j, id_j, sent_j))

    found.sort(key=lambda x: -x[0])
    for ratio, best, shorter_len, src_i, id_i, sent_i, src_j, id_j, sent_j in found:
        print(f"[{ratio:.0%} match, LCS {best}/{shorter_len} words]")
        print(f"  {src_i} :: {id_i}: \"{sent_i}\"")
        print(f"  {src_j} :: {id_j}: \"{sent_j}\"")
        print()
    print(f"Total near-exact duplicate pairs found: {len(found)}")


if __name__ == "__main__":
    main()
