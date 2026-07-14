"""
Verify Gemini's Filter A/B/C consolidation-mapping output against the actual
PRV3 source corpus — mechanically, before a human re-reads paragraphs by hand.

Catches two failure classes:
  1. Fabricated or paraphrased "verbatim quotes" — text Gemini claims comes
     word-for-word from a named source (a taxonomy.ts state, FTA-17/LIB-014,
     or one of the E2/E3/E6/E7 experiment files) but that doesn't actually
     appear there.
  2. Invalid COLLAPSE targets — a disposition that names a target state which
     isn't one of the 47 locked taxonomy.ts states (e.g. collapsing into
     another still-unresolved candidate rather than an actual state).

Two modes:
  --build-corpus         Read the repo's source files fresh and write
                          tools/consolidation_source_corpus.json. Re-run this
                          whenever taxonomy.ts, the anchor pieces, or the
                          experiment files change.
  --check RESPONSE.txt    Check a pasted-in Gemini response against the
                          corpus. Requires the corpus to already exist.

Stdlib only. No repo files are modified by either mode — --build-corpus only
writes the corpus JSON cache; --check only prints a report to stdout.
"""
import argparse
import difflib
import html
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS_PATH = Path(__file__).resolve().parent / "consolidation_source_corpus.json"

TAXONOMY_PATH = REPO_ROOT / "web" / "data" / "taxonomy.ts"
FTA17_PATH = REPO_ROOT / "web" / "content" / "book" / "methodology" / "anchor.md"
LIB014_PATH = REPO_ROOT / "web" / "content" / "book" / "memo" / "anchor-problem.md"
EXPERIMENT_PATHS = {
    "E2": REPO_ROOT / "research" / "seven-experiments" / "experiment-2-employment-litigation-taxonomy.html",
    "E3": REPO_ROOT / "research" / "seven-experiments" / "experiment-3-glassdoor-indeed-review-clustering.html",
    "E6": REPO_ROOT / "research" / "seven-experiments" / "experiment-6-hr-conference-theme-analysis.html",
    "E7": REPO_ROOT / "research" / "seven-experiments" / "experiment-7-organizational-psychology-literature-review.html",
}

DISPOSITION_WORDS = ("COLLAPSE", "STATE", "ROOT", "ELIMINATE")


# ---------------------------------------------------------------------------
# Corpus building
# ---------------------------------------------------------------------------

def _unescape_ts_string(raw: str) -> str:
    """Unescape a captured TS double-quoted string body via JSON's escaping rules."""
    try:
        return json.loads('"' + raw + '"')
    except (json.JSONDecodeError, ValueError):
        return raw


def parse_taxonomy_states(text: str) -> dict:
    start = text.index("export const states: State[] = [")
    end = text.index("export const signatures: Signature[] = [")
    block = text[start:end]

    pattern = re.compile(
        r'\{\s*id:\s*"([a-z_0-9]+)",\s*name:\s*"([^"]+)",'
        r'.*?description:\s*\n?\s*"((?:[^"\\]|\\.)*)",\s*\}',
        re.DOTALL,
    )
    states = {}
    for match in pattern.finditer(block):
        state_id, name, desc_raw = match.groups()
        states[state_id] = {
            "name": name,
            "description": _unescape_ts_string(desc_raw),
        }
    return states


def strip_html(raw_html: str) -> str:
    text = re.sub(r"<style.*?</style>", " ", raw_html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


NAME_DESC_RE = re.compile(
    r'class="[^"]*-name"[^>]*>([^<]+)</div>\s*<div class="[^"]*-desc"[^>]*>([^<]+)</div>',
    re.DOTALL,
)
NCT_TABLE_RE = re.compile(
    r'<table class="[^"]*\bnct\b[^"]*">.*?</table>', re.DOTALL
)
NCT_ROW_RE = re.compile(
    r"<tr>\s*<td>([^<]+)</td>\s*<td>([^<]+)</td>\s*<td>[^<]*</td>\s*<td>[^<]*</td>\s*</tr>",
    re.DOTALL,
)
# "Condition Underneath"-style blocks: a *-label div whose text mentions
# "condition" (any casing — files use "Organizational Condition Underneath",
# "Underlying Condition", "Condition Underneath" etc.), immediately followed
# by a *-text/-desc div formatted as "Candidate Name — description...". This
# is where the richest definition of many inline/sub-candidates actually
# lives — the numbered summary tables and cond-name/cond-desc pairs elsewhere
# in the same file often only carry a short cross-reference blurb for the
# same name, not this fuller text.
CONDITION_LABEL_RE = re.compile(
    r'class="[^"]*-label"[^>]*>[^<]*condition[^<]*</div>\s*'
    r'<div class="[^"]*-(?:text|desc)"[^>]*>([^<]+)</div>',
    re.DOTALL | re.IGNORECASE,
)
NAME_DASH_SPLIT_RE = re.compile(
    r"^([A-Z][A-Za-z0-9'’ ,&]{2,60}?)\s*[—–-]\s*(.+)$", re.DOTALL
)

# Names known to exist ONLY as a fragment embedded mid-sentence inside a
# DIFFERENT finding's verdict-text prose — no dedicated name-div or
# "Name — description" block anywhere. E3's own summary card classifies all
# three as "Partial Matches / Extensions" of an existing state, not
# standalone new candidates, but the fragment text is real and worth keeping
# so a verbatim check has something genuine to work from. Unlike the general
# patterns above, this can't be found by structure alone — there's no marker
# distinguishing "this verdict-text happens to name a second condition" from
# any other verdict-text — so the names are named explicitly here rather
# than guessed at from markup shape.
FRAGMENT_ONLY_NAMES = ("Sustainability Theater", "Trust Deficit", "Compensation Indifference")
VERDICT_TEXT_RE = re.compile(r'<div class="verdict-text">([^<]+)</div>', re.DOTALL)


def extract_fragment_candidates(raw_html: str) -> dict:
    candidates: dict = {}
    for m in VERDICT_TEXT_RE.finditer(raw_html):
        text = html.unescape(re.sub(r"\s+", " ", m.group(1))).strip()
        for name in FRAGMENT_ONLY_NAMES:
            if name in text:
                bucket = candidates.setdefault(name, [])
                if text not in bucket:
                    bucket.append(text)
    return candidates


def extract_html_candidates(raw_html: str) -> dict:
    """name -> list of distinct description texts found under that name.
    A single name frequently has more than one genuinely different text in
    the same file (e.g. a short "confirms existing" cross-reference AND a
    fuller "Condition Underneath" definition) — keep both rather than letting
    one silently overwrite the other, so a verbatim-quote check can try every
    text actually attributed to that name, not just whichever was extracted
    last.
    """
    candidates: dict = {}

    def add(name: str, desc: str):
        name = html.unescape(re.sub(r"\s+", " ", name)).strip()
        desc = html.unescape(re.sub(r"\s+", " ", desc)).strip()
        if not name or not desc:
            return
        bucket = candidates.setdefault(name, [])
        if desc not in bucket:
            bucket.append(desc)

    for name, desc in NAME_DESC_RE.findall(raw_html):
        add(name, desc)

    for table_block in NCT_TABLE_RE.findall(raw_html):
        for name, desc in NCT_ROW_RE.findall(table_block):
            add(name, desc)

    for block_text in CONDITION_LABEL_RE.findall(raw_html):
        block_text = html.unescape(re.sub(r"\s+", " ", block_text)).strip()
        m = NAME_DASH_SPLIT_RE.match(block_text)
        if m:
            add(m.group(1).strip(), m.group(2).strip())

    for name, texts in extract_fragment_candidates(raw_html).items():
        for text in texts:
            add(name, text)

    return candidates


def build_corpus() -> dict:
    if not TAXONOMY_PATH.exists():
        raise SystemExit(f"ABORT: taxonomy file not found: {TAXONOMY_PATH}")
    taxonomy_text = TAXONOMY_PATH.read_text(encoding="utf-8")
    states = parse_taxonomy_states(taxonomy_text)

    corpus = {
        "taxonomy_states": states,
        "taxonomy_state_names": sorted(s["name"] for s in states.values()),
        "book_pieces": {},
        "experiments": {},
    }

    if FTA17_PATH.exists():
        corpus["book_pieces"]["FTA-17"] = {
            "path": str(FTA17_PATH.relative_to(REPO_ROOT)),
            "text": FTA17_PATH.read_text(encoding="utf-8"),
        }
    if LIB014_PATH.exists():
        corpus["book_pieces"]["LIB-014"] = {
            "path": str(LIB014_PATH.relative_to(REPO_ROOT)),
            "text": LIB014_PATH.read_text(encoding="utf-8"),
        }

    for tag, path in EXPERIMENT_PATHS.items():
        if not path.exists():
            continue
        raw_html = path.read_text(encoding="utf-8")
        corpus["experiments"][tag] = {
            "path": str(path.relative_to(REPO_ROOT)),
            "raw_text": strip_html(raw_html),
            "candidates": extract_html_candidates(raw_html),
        }

    return corpus


def cmd_build_corpus():
    corpus = build_corpus()

    n_states = len(corpus["taxonomy_states"])
    print(f"taxonomy.ts states extracted: {n_states}" + ("" if n_states == 47 else "  <-- EXPECTED 47, CHECK PARSER"))

    for key in ("FTA-17", "LIB-014"):
        piece = corpus["book_pieces"].get(key)
        if piece:
            print(f"{key} ({piece['path']}): {len(piece['text'])} chars")
        else:
            print(f"{key}: NOT FOUND")

    for tag in EXPERIMENT_PATHS:
        exp = corpus["experiments"].get(tag)
        if exp:
            n_names = len(exp["candidates"])
            n_texts = sum(len(v) for v in exp["candidates"].values())
            print(
                f"{tag} ({exp['path']}): {len(exp['raw_text'])} chars raw text, "
                f"{n_names} candidate names, {n_texts} distinct description texts "
                f"({n_texts - n_names} name(s) with more than one text)"
            )
        else:
            print(f"{tag}: NOT FOUND")

    CORPUS_PATH.write_text(json.dumps(corpus, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote corpus: {CORPUS_PATH}")


# ---------------------------------------------------------------------------
# Normalization + fuzzy matching
# ---------------------------------------------------------------------------

def normalize(text: str) -> str:
    text = text.replace("‘", "'").replace("’", "'")
    text = text.replace("“", '"').replace("”", '"')
    text = text.replace("–", "-").replace("—", "-").replace("−", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_name(s: str) -> str:
    """Normalize a source NAME for lookup purposes — case and &/and folded,
    separate from normalize() above (which handles quote CONTENT and
    deliberately doesn't touch & since that's meaningful inside a quote).
    """
    s = s.lower().replace(" & ", " and ")
    return re.sub(r"\s+", " ", s).strip()


def closest_match(quote: str, text: str, context: int = 40):
    if not text:
        return None
    sm = difflib.SequenceMatcher(None, quote, text, autojunk=False)
    m = sm.find_longest_match(0, len(quote), 0, len(text))
    if m.size == 0:
        return None
    start = max(0, m.b - context)
    end = min(len(text), m.b + m.size + context)
    snippet = text[start:end]
    return {"matched_chars": m.size, "quote_chars": len(quote), "context": snippet}


# ---------------------------------------------------------------------------
# Corpus lookup — build a flat set of (label, text) sources to search
# ---------------------------------------------------------------------------

def flatten_sources(corpus: dict) -> list:
    """Every named, individually-addressable source, as (label, text)."""
    sources = []
    for state_id, state in corpus["taxonomy_states"].items():
        sources.append((state["name"], state["description"]))
        sources.append((state_id, state["description"]))
    for key, piece in corpus["book_pieces"].items():
        sources.append((key, piece["text"]))
    for tag, exp in corpus["experiments"].items():
        sources.append((tag, exp["raw_text"]))
        for cand_name, cand_descs in exp["candidates"].items():
            for cand_desc in cand_descs:
                sources.append((f"{tag}:{cand_name}", cand_desc))
                sources.append((cand_name, cand_desc))
    return sources


def guess_sources(block_text: str, corpus: dict, sources: list) -> list:
    """Which known source labels does this block of Gemini's text mention?
    Returns a list of (label, text) to try the quote against, most specific
    first. Broad fallback — matches anywhere in the whole block, which is
    exactly what makes it prone to coincidental substring collisions (e.g. a
    fabricated quote that happens to contain the word "fracture" wrongly
    matching the state "The Fracture"). Callers should prefer
    nearest_label_before() when a quote's exact position is known, and use
    this only as a secondary/fallback source list.
    """
    hits = []

    explicit = re.search(r"source:\s*([^\n]+)", block_text, re.IGNORECASE)
    explicit_label = explicit.group(1).strip() if explicit else ""

    block_norm = normalize_name(block_text)
    for label, text in sources:
        if len(label) < 3:
            continue
        label_norm = normalize_name(label)
        if label_norm in block_norm or (explicit_label and label_norm in normalize_name(explicit_label)):
            hits.append((label, text))

    # de-dup on (label, text) — not label alone. Candidate names frequently
    # collide with taxonomy state names (that's the whole point of this
    # check), and those are DIFFERENT texts that both need to be tried.
    seen = set()
    ordered = []
    for label, text in sorted(hits, key=lambda h: (":" not in h[0], len(h[0]))):
        key = (label, text)
        if key not in seen:
            seen.add(key)
            ordered.append((label, text))
    return ordered


def nearest_label_before(block_text: str, pos: int, sources: list, window: int = 200) -> tuple:
    """Find the source label whose mention in block_text ends closest to (and
    strictly before) position `pos`, searching only the `window` characters
    immediately preceding it. This ties a quote to the specific name written
    right before it — e.g. "Check vs. Dueling Narratives: '...quote...'" —
    instead of any name mentioned anywhere in the surrounding paragraph. That
    broader search is exactly what previously mislabeled a fabricated
    Dueling Narratives quote as "The Fracture" (the fabricated text itself
    happened to contain the phrase "along the fracture line"), since that
    coincidental match lives inside/after the quote, not before it — this
    function only ever looks backward from the quote's start.
    Returns (label, text) or None.
    """
    start = max(0, pos - window)
    context_norm = normalize_name(block_text[start:pos])
    best = None  # (label, text, end_pos_in_context)
    for label, text in sources:
        if len(label) < 3:
            continue
        needle = normalize_name(label)
        idx = context_norm.rfind(needle)
        if idx == -1:
            continue
        end = idx + len(needle)
        if best is None or end > best[2]:
            best = (label, text, end)
    return (best[0], best[1]) if best else None


# ---------------------------------------------------------------------------
# Extraction from Gemini's response
# ---------------------------------------------------------------------------

QUOTE_LABEL_RE = re.compile(r"verbatim[\w \-]*(?:quote|text|target)?s?", re.IGNORECASE)
QUOTED_SPAN_RES = [
    re.compile(r'"([^"]{15,})"'),
    re.compile(r"“([^”]{15,})”"),
    re.compile(r"`([^`]{15,})`"),
]

# Requires the literal word "disposition" as a label immediately before the
# keyword (allowing markdown bold/colon) — bare "Collapse."/"Pass." verdicts
# inside Filter A/B/C sub-analysis use the same vocabulary and must NOT be
# picked up here, only the canonical "**Disposition:** **COLLAPSE**" line.
DISPOSITION_LINE_RE = re.compile(
    r"disposition\**:?\**\s*\**\s*(COLLAPSE|STATE|ROOT|ELIMINATE)\b[^\n|]{0,250}",
    re.IGNORECASE,
)
DISPOSITION_TABLE_ROW_RE = re.compile(
    r"^\s*\|\s*\**([^|*]+?)\**\s*\|\s*\**(COLLAPSE|STATE|ROOT|ELIMINATE)\**\s*\|\s*\**([^|]+?)\**\s*\|",
    re.IGNORECASE | re.MULTILINE,
)
TARGET_PHRASE_RE = re.compile(
    r"(?:into|as|maps? to|folds? into|collapses? into|absorbed(?: bidirectionally)? by|target)"
    r"\s*[:\-→]?\s*"
    r"[`*]*([A-Z][A-Za-z0-9'’ ,&\-]{2,60}?)[`*]*(?:[.,;)\n]|$)",
    re.IGNORECASE,
)


HEADING_RE = re.compile(r"^#{1,6}\s+.+")
CANDIDATE_LINE_RE = re.compile(r"^\s*[\*\-]*\s*\*{0,2}candidate\*{0,2}\s*:", re.IGNORECASE)


def _extract_line_quote(line: str):
    for pattern in QUOTED_SPAN_RES:
        m = pattern.search(line)
        if m:
            return m.group(1).strip().strip('"“”').strip()
    return None


def split_blocks(response_text: str) -> list:
    """Split into blank-line-delimited paragraph chunks for source attribution,
    each prefixed with the most recent markdown heading. Two real formatting
    patterns in Gemini's responses otherwise break naive splitting: (1) a
    "Verbatim Quote:" label and the quote(s) beneath it are frequently on
    separate lines within the same paragraph with no blank line between them
    — splitting per-bullet would separate the label from what it's labeling;
    (2) the candidate name is often only in a "#### 2c. Candidate Name"
    heading, separated from its content by a blank line — without carrying
    that heading forward, source attribution for everything under it fails.
    Worst case of staying coarse is guess_sources() tries an extra wrong
    candidate source, which is harmless (see instruction to be liberal /
    prefer false positives over silently missing a fabrication).

    Also tracks the current item's own "Candidate:" quote as it's seen line
    by line, and attaches it to every block returned — this is what lets
    check_quote() recognize a quote as the candidate's own words repeated
    mid-comparison (misattributed to whatever state name is nearby) rather
    than a real FAIL against the comparison state.

    Returns a list of {"text": block_text, "candidate": current_candidate_text}.
    """
    lines = response_text.split("\n")
    blocks = []
    current_heading = ""
    current_candidate = None
    current_lines = []

    def flush():
        body = "\n".join(current_lines).strip()
        if body:
            text = (current_heading + "\n" + body).strip() if current_heading else body
            blocks.append({"text": text, "candidate": current_candidate})
        current_lines.clear()

    for line in lines:
        if HEADING_RE.match(line):
            flush()
            current_heading = line.strip()
            continue
        if CANDIDATE_LINE_RE.match(line):
            q = _extract_line_quote(line)
            if q:
                current_candidate = q
        if line.strip() == "":
            flush()
            continue
        current_lines.append(line)
    flush()
    return blocks or [{"text": response_text, "candidate": None}]


def extract_quote_claims(response_text: str) -> list:
    """Return list of dicts: {block, quote}.
    Deliberately liberal: extract every quoted span >= 15 chars from every
    block, full stop — no "must be labeled 'verbatim' or mention 'source'"
    gate. Gemini's labeling convention is not stable across responses (seen
    so far: backtick-wrapped quotes under "Verbatim Quote:" labels, and
    plain straight-quotes under "Check vs. X:" / "Candidate:" labels with no
    "verbatim"/"source" word anywhere in the document). A spurious extraction
    just costs a cheap SOURCE NOT FOUND for a human to glance past; a missed
    one costs an unchecked fabrication, which is the worse failure mode.
    """
    claims = []
    blocks = split_blocks(response_text)
    for block in blocks:
        block_text = block["text"]
        seen_in_block = set()
        for pattern in QUOTED_SPAN_RES:
            for m in pattern.finditer(block_text):
                # Strip any straight/smart quote chars left over from
                # backtick-wrapped-AND-quote-marked text like `"..."` —
                # otherwise the backtick pattern and the straight-quote
                # pattern both match the same quote (one clean, one with
                # stray leading/trailing " chars) and it gets checked twice,
                # with the dirty copy spuriously failing.
                quote = m.group(1).strip().strip('"“”').strip()
                if len(quote) < 15:
                    continue
                if quote in seen_in_block:
                    continue
                seen_in_block.add(quote)
                claims.append({
                    "block": block_text,
                    "quote": quote,
                    "pos": m.start(1),
                    "candidate_text": block["candidate"],
                })
    return claims


def extract_disposition_claims(response_text: str) -> list:
    claims = []
    seen_spans = set()

    for m in DISPOSITION_TABLE_ROW_RE.finditer(response_text):
        candidate, disposition, detail = m.groups()
        claims.append({
            "candidate": candidate.strip(),
            "disposition": disposition.upper(),
            "detail": detail.strip(),
            "line": m.group(0).strip(),
        })
        seen_spans.add(m.span())

    for m in DISPOSITION_LINE_RE.finditer(response_text):
        if any(m.start() >= s and m.end() <= e for s, e in seen_spans):
            continue
        disposition = m.group(1).upper()
        tail = m.group(0)
        target_match = TARGET_PHRASE_RE.search(tail)
        claims.append({
            "candidate": None,
            "disposition": disposition,
            "detail": target_match.group(1).strip() if target_match else None,
            "line": m.group(0).strip(),
        })
    return claims


# ---------------------------------------------------------------------------
# Check mode
# ---------------------------------------------------------------------------

ELLIPSIS_RE = re.compile(r"\.{3}|…")


def split_quote_segments(quote: str) -> list:
    """Split a claimed quote on ellipses into the pieces that must each be
    found, in order, in the source. A quote with no ellipsis degenerates to
    the original single-segment whole-string check.
    """
    segments = [normalize(p) for p in ELLIPSIS_RE.split(quote)]
    return [s for s in segments if s]


def match_segments(segments: list, source_text: str):
    """Each segment is checked independently for presence in source_text,
    then positions are checked for non-decreasing order. A segment matched
    out of order still counts as "found" (so a human can see it's present,
    just spliced from the wrong place) but fails the overall pass.
    """
    norm_source = normalize(source_text)
    norm_source_lower = norm_source.lower()
    details = []
    for seg in segments:
        idx = norm_source.find(seg)
        case_insensitive = False
        if idx == -1:
            idx_ci = norm_source_lower.find(seg.lower())
            if idx_ci != -1:
                idx = idx_ci
                case_insensitive = True
        details.append({
            "segment": seg,
            "found": idx != -1,
            "position": idx if idx != -1 else None,
            "case_insensitive": case_insensitive,
        })

    all_found = all(d["found"] for d in details)
    in_order = True
    last_pos = -1
    for d in details:
        if not d["found"] or d["position"] <= last_pos:
            in_order = False
        if d["found"]:
            last_pos = d["position"]
    return (all_found and in_order), details


BARE_NAME_SUFFIX_RE = re.compile(r"\s*\([^)]*\)\s*$")


def is_bare_name_reference(quote: str, sources: list) -> bool:
    """True if the extracted "quote" is just a source name in backticks/quotes
    used as a markdown code-reference (e.g. "...mirrors `Heard & Ignored` where
    the report...") rather than a content excerpt. Checking a name against its
    own description is nonsensical and was drowning out real findings — this
    only filters an EXACT normalized match against a known label (after
    stripping one trailing parenthetical, e.g. "Human Displacement Anxiety
    (E6 #2)" — Gemini sometimes quotes its own item header, tag and all,
    instead of real descriptive text when labeling a self-reference), so it
    can't accidentally suppress a genuine short quote that happens to overlap
    a name.
    """
    q_norm = normalize_name(quote)
    q_norm_stripped = normalize_name(BARE_NAME_SUFFIX_RE.sub("", quote))
    for label, _ in sources:
        label_norm = normalize_name(label)
        if q_norm == label_norm or q_norm_stripped == label_norm:
            return True
    return False


def check_quote(claim: dict, corpus: dict, sources: list) -> dict:
    quote = claim["quote"]
    segments = split_quote_segments(quote)
    candidates = guess_sources(claim["block"], corpus, sources)

    # Prefer the label written immediately before this specific quote (e.g.
    # "Check vs. Dueling Narratives: '...'") over the broader whole-block
    # guess — tried first, so it wins both PASS attribution and the label
    # shown on FAIL when it ties with (or beats) the fallback candidates.
    pos = claim.get("pos")
    if pos is not None:
        nearest = nearest_label_before(claim["block"], pos, sources)
        if nearest is not None:
            candidates = [nearest] + [c for c in candidates if c != nearest]

    best = None  # (label, text, details, n_found)
    for label, text in candidates:
        all_pass, details = match_segments(segments, text)
        n_found = sum(1 for d in details if d["found"])
        any_ci = any(d["found"] and d["case_insensitive"] for d in details)
        if all_pass:
            return {
                "quote": quote,
                "claimed_source": label,
                "result": "PASS (case-insensitive segment)" if any_ci else "PASS",
                "segments": details,
                "detail": None,
            }
        if best is None or n_found > best[3]:
            best = (label, text, details, n_found)

    # Third case: not a real claim about the comparison state at all — it's
    # the CURRENT ITEM's own "Candidate:" text, quoted again mid-comparison
    # and misattributed by the heuristics above to whichever state name is
    # nearby. Checked last, after every real candidate source has already
    # had its shot at a PASS, so a quote that's genuinely accurate against
    # BOTH the claimed source and the candidate text still reports PASS
    # against the claimed source, not SELF-QUOTE.
    candidate_text = claim.get("candidate_text")
    if candidate_text:
        # Try every known variant of this same candidate name, not just the
        # one that happened to appear in this response's own "Candidate:"
        # line — the corpus (and the prompt) offer multiple text variants
        # for many names, and Gemini is explicitly told it may quote
        # whichever one it's actually referencing, not only the first one.
        norm_candidate = normalize(candidate_text)
        matched_bases = {
            (label.split(":", 1)[1] if ":" in label else label)
            for label, text in sources
            if normalize(text) == norm_candidate
        }
        self_quote_texts = [candidate_text]
        if matched_bases:
            seen = {candidate_text}
            for label, text in sources:
                base = label.split(":", 1)[1] if ":" in label else label
                if base in matched_bases and text not in seen:
                    seen.add(text)
                    self_quote_texts.append(text)

        for text in self_quote_texts:
            self_pass, self_details = match_segments(segments, text)
            if self_pass:
                return {
                    "quote": quote,
                    "claimed_source": "(this item's own Candidate text)",
                    "result": "SELF-QUOTE",
                    "segments": self_details,
                    "detail": None,
                }

    if not candidates:
        return {
            "quote": quote,
            "claimed_source": None,
            "result": "SOURCE NOT FOUND",
            "segments": None,
            "detail": "No known corpus source (taxonomy state, FTA-17/LIB-014, or "
                      "E2/E3/E6/E7 file/candidate) mentioned in the surrounding text.",
        }

    label, text, details, _ = best
    for d in details:
        if not d["found"]:
            d["closest"] = closest_match(d["segment"], normalize(text))
    return {
        "quote": quote,
        "claimed_source": label,
        "result": "FAIL",
        "segments": details,
        "detail": None,
        "sources_tried": [l for l, _ in candidates],
    }


def check_disposition(claim: dict, corpus: dict) -> dict:
    disposition = claim["disposition"]
    target = claim["detail"]

    if disposition != "COLLAPSE":
        return {**claim, "result": f"{disposition} (no target validation needed)"}

    if not target:
        return {**claim, "result": "COLLAPSE — NO TARGET PARSED", "detail": None}

    norm_target = normalize(target).lower().lstrip("the ").strip()
    state_names = corpus["taxonomy_state_names"]
    for name in state_names:
        norm_name = normalize(name).lower().lstrip("the ").strip()
        if norm_target == norm_name or normalize(target).lower() == normalize(name).lower():
            return {**claim, "result": "VALID TARGET", "resolved_state": name}

    # not one of the 47 — is it a known unresolved candidate instead?
    all_candidate_names = set()
    for exp in corpus["experiments"].values():
        all_candidate_names.update(exp["candidates"].keys())
    close_candidate = difflib.get_close_matches(target, all_candidate_names, n=1, cutoff=0.6)
    close_state = difflib.get_close_matches(target, state_names, n=1, cutoff=0.6)

    if close_candidate:
        note = f"another unresolved candidate, not a taxonomy state: '{close_candidate[0]}'"
    elif close_state:
        note = f"possible typo of taxonomy state '{close_state[0]}'"
    else:
        note = "no close match in taxonomy states or known experiment candidates"

    return {**claim, "result": "INVALID TARGET", "note": note}


def cmd_check(response_path: Path):
    if not CORPUS_PATH.exists():
        raise SystemExit(f"ABORT: corpus not found at {CORPUS_PATH}. Run --build-corpus first.")
    corpus = json.loads(CORPUS_PATH.read_text(encoding="utf-8"))
    sources = flatten_sources(corpus)

    response_text = response_path.read_text(encoding="utf-8")

    quote_claims = [
        c for c in extract_quote_claims(response_text)
        if not is_bare_name_reference(c["quote"], sources)
    ]
    quote_results = [check_quote(c, corpus, sources) for c in quote_claims]

    disposition_claims = extract_disposition_claims(response_text)
    disposition_results = [check_disposition(c, corpus) for c in disposition_claims]

    n_quotes = len(quote_results)
    n_pass = sum(1 for r in quote_results if r["result"].startswith("PASS"))
    n_fail = sum(1 for r in quote_results if r["result"] == "FAIL")
    n_self_quote = sum(1 for r in quote_results if r["result"] == "SELF-QUOTE")
    n_no_source = sum(1 for r in quote_results if r["result"] == "SOURCE NOT FOUND")

    n_collapse = sum(1 for r in disposition_results if r["disposition"] == "COLLAPSE")
    n_valid = sum(1 for r in disposition_results if r["result"] == "VALID TARGET")
    n_invalid = sum(1 for r in disposition_results if r["result"] == "INVALID TARGET")

    print("=" * 72)
    print(f"QUOTE VERIFICATION — {response_path}")
    print("=" * 72)
    print(f"Total quote claims checked: {n_quotes}")
    print(f"  PASS:              {n_pass}")
    print(f"  FAIL:              {n_fail}")
    print(f"  SELF-QUOTE:        {n_self_quote}  (candidate's own words, misattributed — not a real finding)")
    print(f"  SOURCE NOT FOUND:  {n_no_source}")
    print()
    print(f"Total COLLAPSE disposition targets checked: {n_collapse}")
    print(f"  VALID TARGET:      {n_valid}")
    print(f"  INVALID TARGET:    {n_invalid}")
    print()

    if n_fail or n_no_source:
        print("-" * 72)
        print("QUOTE FAILURES / MISSING SOURCES")
        print("-" * 72)
        for r in quote_results:
            if r["result"] in ("FAIL", "SOURCE NOT FOUND"):
                print(f"\n[{r['result']}] claimed source: {r['claimed_source']}")
                print(f"  Quote: {r['quote'][:300]}")
                if r["result"] == "FAIL" and r["segments"]:
                    n_seg = len(r["segments"])
                    if n_seg > 1:
                        print(f"  Ellipsis quote split into {n_seg} segments:")
                    for i, seg in enumerate(r["segments"], 1):
                        prefix = f"    segment {i}/{n_seg}:" if n_seg > 1 else "    segment:"
                        if seg["found"]:
                            note = " (case-insensitive)" if seg["case_insensitive"] else ""
                            print(f"{prefix} FOUND at position {seg['position']}{note} — \"{seg['segment'][:80]}\"")
                        else:
                            print(f"{prefix} NOT FOUND — \"{seg['segment'][:80]}\"")
                            if seg.get("closest"):
                                c = seg["closest"]
                                print(f"      closest match ({c['matched_chars']}/{c['quote_chars']} chars): ...{c['context']}...")
                    if "sources_tried" in r and len(r["sources_tried"]) > 1:
                        print(f"  (also tried: {', '.join(r['sources_tried'][1:])})")

    if n_self_quote:
        print("-" * 72)
        print("SELF-QUOTES (noise — candidate's own words, not a finding)")
        print("-" * 72)
        for r in quote_results:
            if r["result"] == "SELF-QUOTE":
                print(f"  - {r['quote'][:150]}")

    if n_invalid:
        print("-" * 72)
        print("INVALID COLLAPSE TARGETS")
        print("-" * 72)
        for r in disposition_results:
            if r["result"] == "INVALID TARGET":
                cand = r["candidate"] or "(candidate name not parsed)"
                print(f"\n[INVALID TARGET] {cand} -> \"{r['detail']}\"")
                print(f"  {r['note']}")
                print(f"  Source line: {r['line']}")

    print("\nDone. Nothing written to disk.")


# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--build-corpus", action="store_true",
                        help="Read repo source files and write consolidation_source_corpus.json")
    group.add_argument("--check", metavar="RESPONSE.txt",
                        help="Check a Gemini response file against the corpus")
    args = parser.parse_args()

    if args.build_corpus:
        cmd_build_corpus()
    else:
        path = Path(args.check)
        if not path.exists():
            raise SystemExit(f"ABORT: response file not found: {path}")
        cmd_check(path)


if __name__ == "__main__":
    main()
