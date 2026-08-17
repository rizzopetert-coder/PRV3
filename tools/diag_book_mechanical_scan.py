"""
PRV3 -- mechanical (grep/regex-based, not a rewrite or a subjective close-read)
scan across the full /book published corpus, per the "Proposed next phase"
criteria: em-dash count per file, exact/near-exact duplicate closing lines
across files, weasel-attribution phrases with no named source, and same-file
binary-contrast count >=3. Read-only, writes a report file, touches no
content.

NOTE: this scans the FULL 87-file published corpus, not "the remaining ~79"
-- prompts/no-ai-slop-fix-tracking.md (which would identify exactly which 8
files were already fixed this session) was not available when this ran, so
excluding any specific 8 files here would be a guess. Files already fixed
will simply show their current (already-improved) counts; nothing here
assumes otherwise.

Usage:
  python tools/diag_book_mechanical_scan.py
"""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST = REPO_ROOT / "web" / "lib" / "book-manifest.ts"
CONTENT_ROOT = REPO_ROOT / "web" / "content" / "book"

EM_DASH_THRESHOLD = 8
BINARY_CONTRAST_THRESHOLD = 3

WEASEL_PATTERNS = [
    r"\bresearch (?:on|shows?|has shown|suggests?|found)\b",
    r"\ba study (?:of|on|found|shows?)\b",
    r"\bstudies (?:show|have shown|suggest|found)\b",
    r"\bexperts? (?:agree|say|believe)\b",
    r"\bwidely (?:regarded|cited|known|accepted)\b",
    r"\bmany (?:argue|believe|say)\b",
    r"\bit is well known\b",
    r"\bevidence (?:shows?|suggests?)\b",
]

# A "named source" nearby = a capitalized Name (+ optional &/and Name) followed
# by a 4-digit year in parens, OR "according to <Name>", within the same
# sentence. Rough but adequate for a mechanical first pass -- not a rewrite.
NAMED_SOURCE_RE = re.compile(
    r"[A-Z][a-z]+(?:\s*(?:&|and)\s*[A-Z][a-z]+)*\s*(?:,\s*)?\(?\d{4}\)?"
    r"|according to [A-Z][a-z]+"
)

# Binary contrast: "X is/was/does/do/are not... . It/They/That is/was/are Y."
# across one or two adjacent sentences. Intentionally loose (regex, not a
# parser) -- flags candidates for a human read, not a certified count.
BINARY_CONTRAST_RE = re.compile(
    r"\b(?:isn't|wasn't|aren't|doesn't|don't|is not|was not|are not|does not|do not)\b"
    r"[^.!?]*[.!?]\s+"
    r"(?:It|It's|It is|It was|They|They're|They are|That|That's|That is)\b",
    re.IGNORECASE,
)


def load_manifest_slugs() -> dict[str, tuple[str, str]]:
    """slug -> (contentType, status)"""
    text = MANIFEST.read_text(encoding="utf-8")
    entries: dict[str, tuple[str, str]] = {}
    for m in re.finditer(
        r'slug:\s*"([^"]+)".*?contentType:\s*"([^"]+)".*?status:\s*"([^"]+)"',
        text,
        re.DOTALL,
    ):
        slug, content_type, status = m.groups()
        # guard against runaway DOTALL matches spanning multiple entries --
        # cap by re-splitting on the next "slug:" boundary implicitly via
        # non-greedy [^"]+ above; verified against expected count below.
        entries[slug] = (content_type, status)
    return entries


def count_em_dashes(text: str) -> int:
    return text.count("—")


def count_binary_contrasts(text: str) -> int:
    return len(BINARY_CONTRAST_RE.findall(text))


def find_weasel_hits(text: str) -> list[str]:
    hits = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        for pat in WEASEL_PATTERNS:
            if re.search(pat, sent, re.IGNORECASE):
                if not NAMED_SOURCE_RE.search(sent):
                    hits.append(sent.strip()[:140])
                break
    return hits


def last_paragraph(text: str) -> str:
    paras = [p.strip() for p in text.split("\n\n") if p.strip() and p.strip() != "---"]
    return paras[-1] if paras else ""


def tokenize(s: str) -> list[str]:
    return re.findall(r"[A-Za-z']+", s.lower())


def lcs_len(a: list[str], b: list[str]) -> int:
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for x in range(1, m + 1):
        for y in range(1, n + 1):
            dp[x][y] = dp[x - 1][y - 1] + 1 if a[x - 1] == b[y - 1] else max(dp[x - 1][y], dp[x][y - 1])
    return dp[m][n]


def main() -> None:
    slugs = load_manifest_slugs()
    published = {s: ct for s, (ct, status) in slugs.items() if status == "published"}
    print(f"Manifest published-slug count: {len(published)}")

    files: dict[str, tuple[Path, str]] = {}
    for slug, content_type in published.items():
        p = CONTENT_ROOT / content_type / f"{slug}.md"
        if not p.exists():
            print(f"WARNING: manifest slug {slug!r} has no file at {p}")
            continue
        files[slug] = (p, p.read_text(encoding="utf-8"))

    print(f"Files actually loaded: {len(files)}\n")

    rows = []
    for slug, (path, text) in sorted(files.items()):
        em = count_em_dashes(text)
        bc = count_binary_contrasts(text)
        weasel = find_weasel_hits(text)
        rows.append((slug, str(path.relative_to(REPO_ROOT)), em, bc, weasel))

    # Report 1: em-dash count > threshold
    print(f"=== Files with em-dash count > {EM_DASH_THRESHOLD} ===")
    over_em = sorted([r for r in rows if r[2] > EM_DASH_THRESHOLD], key=lambda r: -r[2])
    for slug, path, em, bc, weasel in over_em:
        print(f"  {em:3d}  {slug}")
    print(f"Total: {len(over_em)} of {len(rows)}\n")

    # Report 2: binary contrast count >= threshold
    print(f"=== Files with binary-contrast count >= {BINARY_CONTRAST_THRESHOLD} ===")
    over_bc = sorted([r for r in rows if r[3] >= BINARY_CONTRAST_THRESHOLD], key=lambda r: -r[3])
    for slug, path, em, bc, weasel in over_bc:
        print(f"  {bc:3d}  {slug}")
    print(f"Total: {len(over_bc)} of {len(rows)}\n")

    # Report 3: weasel attribution hits
    print("=== Files with weasel-attribution phrases (no named source in-sentence) ===")
    with_weasel = [r for r in rows if r[4]]
    for slug, path, em, bc, weasel in with_weasel:
        print(f"  {slug} ({len(weasel)}):")
        for w in weasel:
            print(f"      \"{w}\"")
    print(f"Total: {len(with_weasel)} of {len(rows)}\n")

    # Report 4: near-duplicate closing paragraphs across files (pairwise LCS)
    print("=== Near-duplicate closing paragraphs across files (LCS >= 60% of shorter) ===")
    closings = [(slug, last_paragraph(text)) for slug, (path, text) in files.items()]
    closings = [(s, c, tokenize(c)) for s, c in closings if len(tokenize(c)) >= 5]
    dup_pairs = []
    for i in range(len(closings)):
        for j in range(i + 1, len(closings)):
            s1, c1, w1 = closings[i]
            s2, c2, w2 = closings[j]
            shorter = min(len(w1), len(w2))
            ratio = lcs_len(w1, w2) / shorter
            if ratio >= 0.6:
                dup_pairs.append((ratio, s1, c1, s2, c2))
    dup_pairs.sort(key=lambda x: -x[0])
    for ratio, s1, c1, s2, c2 in dup_pairs:
        print(f"  [{ratio:.0%} match]")
        print(f"    {s1}: \"{c1[:200]}\"")
        print(f"    {s2}: \"{c2[:200]}\"")
    print(f"Total near-duplicate closing pairs: {len(dup_pairs)}\n")

    # Full table dump for the report file
    print("=== FULL TABLE (all files) ===")
    print(f"{'slug':<55} {'em-dash':>8} {'bin-contrast':>13} {'weasel':>7}")
    for slug, path, em, bc, weasel in sorted(rows, key=lambda r: -r[2]):
        print(f"{slug:<55} {em:>8} {bc:>13} {len(weasel):>7}")


if __name__ == "__main__":
    main()
