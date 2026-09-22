"""
tools/sleuth/rules/candidate.py -- tighten the appositive-emdash-list
heuristic per Pete's direction this pass: on top of the existing
>=2-comma gate, also require that NONE of the comma-separated segments
inside the dash span contains its own finite verb, to filter out
clause-parallelism rhetoric (three parallel independent/relative
clauses joined by commas) that isn't actually the "(such as X, Y, and
Z)" noun/adjective-phrase list CLAUDE.md's style rule targets.

No POS tagger is available in this environment (no spacy/nltk, no
network egress to install one) -- consistent with this file's existing
approach (banned-jargon, coaching-as-noun are plain regex too), the
finite-verb check is a regex heuristic, not a parser. Three signals,
any one of which in ANY segment is treated as "this segment is a
clause, not a list item":

  1. An auxiliary or modal verb (is/are/was/were/has/have/had/do/does/
     did/will/would/can/could/should/must/etc, plus get/gets/got as a
     common passive-auxiliary substitute -- "gets blamed", "get
     managed"). Unambiguous signal on its own.
  2. A relative/subordinating pronoun (who/that/which/what/where/when/
     why/how) followed by more text in the same segment. Relative
     clauses carry their own verb by construction, so this is a
     reliable proxy even without directly matching the verb itself.
  3. A common personal/demonstrative pronoun subject (it/they/he/she/
     we/this/everything/someone/there/etc) followed within a couple
     words by a word ending in -ed or -s, catching plain declarative
     clauses without an auxiliary ("everything drifted... it
     started").

Verified against the real saved crawl (tools/sleuth/output/sleuth_raw.json,
the same data the 79-hit content-candidate-review-packet.md run used):
BEFORE 79 hits, AFTER 22 hits -- 57 filtered as clause-parallelism.

Flagged honestly, not force-tuned to Pete's "~74 of 79" ballpark: the
remaining 22 include a handful of genuine heuristic misses (e.g. "they
note it, adjust their posture slightly, and move on" -- a real clause
with a bare present-tense verb and no auxiliary, which no regex can
reliably catch without a verb lexicon). Pushing further would mean
either a curated verb wordlist (overfits to this exact corpus, breaks
on the next crawl) or accepting more false positives against genuine
noun-phrase lists. 22 kept, not ~5, is the honest number for this
heuristic -- see this session's report to Pete for the itemized
before/after.

Usage:
    python tools/patch_candidate_finite_verb_filter.py --dry-run
    python tools/patch_candidate_finite_verb_filter.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('tools/sleuth/rules/candidate.py')

OLD = '''_APPOSITIVE_EMDASH_RE = re.compile(r"—([^—.]*,[^—.]*)(—|\\.)")
_MIN_COMMAS_FOR_APPOSITIVE_LIST = 2
_COACHING_NOUN_RE = re.compile('''

NEW = '''_APPOSITIVE_EMDASH_RE = re.compile(r"—([^—.]*,[^—.]*)(—|\\.)")
_MIN_COMMAS_FOR_APPOSITIVE_LIST = 2

# Finite-verb detection for the appositive-list heuristic below: any one
# of these matching within a comma-segment means that segment is its own
# clause, not a noun/adjective-phrase list item. See module docstring for
# the reasoning and the before/after count verified against real crawl data.
_FINITE_AUX_MODAL_RE = re.compile(
    r"\\b(am|is|are|was|were|be|been|being|has|have|had|"
    r"do|does|did|will|would|shall|should|can|could|may|might|must|"
    r"get|gets|got|getting)\\b",
    re.IGNORECASE,
)
_RELATIVE_CLAUSE_RE = re.compile(
    r"\\b(who|whom|whose|which|that|what|where|when|why|how)\\s+\\S",
    re.IGNORECASE,
)
_PRONOUN_VERB_RE = re.compile(
    r"\\b(it|they|he|she|we|i|this|these|those|everything|nothing|something|"
    r"someone|somebody|there)\\s+(?:\\w+\\s+){0,2}?\\w+(?:ed|s)\\b",
    re.IGNORECASE,
)


def _segment_has_finite_verb(segment: str) -> bool:
    return bool(
        _FINITE_AUX_MODAL_RE.search(segment)
        or _RELATIVE_CLAUSE_RE.search(segment)
        or _PRONOUN_VERB_RE.search(segment)
    )


_COACHING_NOUN_RE = re.compile('''

OLD_CHECK_BLOCK = '''        for m in _APPOSITIVE_EMDASH_RE.finditer(text):
            span_text = m.group(1)
            if span_text.count(",") < _MIN_COMMAS_FOR_APPOSITIVE_LIST:
                continue  # a single comma is almost always a two-clause interruption, not a list
            findings.append(Finding('''

NEW_CHECK_BLOCK = '''        for m in _APPOSITIVE_EMDASH_RE.finditer(text):
            span_text = m.group(1)
            if span_text.count(",") < _MIN_COMMAS_FOR_APPOSITIVE_LIST:
                continue  # a single comma is almost always a two-clause interruption, not a list
            if any(_segment_has_finite_verb(seg) for seg in span_text.split(",")):
                continue  # a segment carries its own clause -- parallel-clause rhetoric, not a list
            findings.append(Finding('''

ANCHORS = [(OLD, NEW), (OLD_CHECK_BLOCK, NEW_CHECK_BLOCK)]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    new_content = content
    for old, new in ANCHORS:
        count = new_content.count(old)
        if count != 1:
            print(f'ERROR: anchor found {count} times, expected exactly 1.', file=sys.stderr)
            print(f'Anchor:\\n{old[:200]}', file=sys.stderr)
            sys.exit(1)
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print('DRY RUN -- both anchors found exactly once, replacements would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
