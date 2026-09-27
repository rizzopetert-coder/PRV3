"""
House punctuation for AI-generated narrative questions (Pete, 2026-09-27).

Live output on Sonnet 5 included em-dashes in the narrative question ("...
official conversations or reviews -- what's something...", once in
Production), and nothing checked that path: NARRATIVE_PROMPT_GENERATION_
SYSTEM_PROMPT had no punctuation rule and generate_narrative_prompt()
returned the model text as-is.

Two layers:
  1. Prompt rule: no em-dashes, en-dashes used as dashes, double hyphens,
     or semicolons. Written without any dash characters itself (CLAUDE.md:
     avoid em-dashes entirely in LLM system-prompt specs).
  2. Deterministic guard, _enforce_house_punctuation(): rewrites any em-dash,
     spaced en-dash, " -- ", or semicolon that still appears to ", " and
     tidies doubled commas/spaces. A prompt rule lowers the rate, only code
     makes it zero. Hyphenated words ("follow-up", "day-to-day") and
     unspaced en-dash ranges are untouched.

Usage:
    python tools/patch_narrative_question_punctuation.py --dry-run
    python tools/patch_narrative_question_punctuation.py --write
"""
import argparse
import pathlib
import sys

EDITS = [
    ('engine/narrative.py',
     '- Output ONLY the question text. No markdown, no quotation marks, no \\\n'
     'JSON, no surrounding punctuation beyond the question itself.\n'
     '"""\n',
     '- Output ONLY the question text. No markdown, no quotation marks, no \\\n'
     'JSON, no surrounding punctuation beyond the question itself.\n'
     '- Punctuation: never use em dashes, en dashes used as dashes, double \\\n'
     'hyphens, or semicolons. Use a comma, a period, or a separate sentence \\\n'
     'instead.\n'
     '"""\n',
     'prompt punctuation rule'),
    ('engine/narrative.py',
     '_NARRATIVE_PROMPT_FALLBACK: str = (\n',
     'def _enforce_house_punctuation(text: str) -> str:\n'
     '    """\n'
     '    House style for the generated narrative question: no em-dashes, no\n'
     '    dash-style en-dashes or double hyphens, no semicolons. The prompt asks\n'
     '    for this, and this guard guarantees it -- any that slip through become\n'
     '    a comma. Hyphenated words and unspaced en-dash ranges are left alone.\n'
     '    """\n'
     '    import re\n'
     '    text = re.sub(r"\\s*\\u2014\\s*", ", ", text)        # em-dash, spaced or not\n'
     '    text = re.sub(r"\\s+\\u2013\\s+", ", ", text)        # spaced en-dash used as a dash\n'
     '    text = re.sub(r"\\s+--\\s+", ", ", text)            # double-hyphen dash\n'
     '    text = re.sub(r"\\s*;\\s*", ", ", text)             # semicolon\n'
     '    text = re.sub(r",\\s*,", ",", text)\n'
     '    text = re.sub(r",\\s*([?.!])", r"\\1", text)\n'
     '    return re.sub(r"[ \\t]{2,}", " ", text).strip()\n'
     '\n'
     '\n'
     '_NARRATIVE_PROMPT_FALLBACK: str = (\n',
     'guard function'),
    ('engine/narrative.py',
     '    return NarrativePromptResult(prompt=text, is_fallback=False)\n',
     '    return NarrativePromptResult(prompt=_enforce_house_punctuation(text), is_fallback=False)\n',
     'apply guard'),
]

TEST_FILE = pathlib.Path('tools/test_narrative.py')
TEST_ANCHOR = 'check("Engine default model", engine.model == "claude-sonnet-5")\n'
TEST_ADD = '''
# ── House punctuation on the generated narrative question (2026-09-27) ──────
from engine.narrative import _enforce_house_punctuation, NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT
_q1 = "People often know things that never make it into reviews \\u2014 what's something like that on your mind?"
check("guard: em-dash becomes a comma", _enforce_house_punctuation(_q1)
      == "People often know things that never make it into reviews, what's something like that on your mind?")
check("guard: semicolon becomes a comma", ";" not in _enforce_house_punctuation("It shifted; what changed?"))
check("guard: spaced en-dash and double hyphen become commas",
      "\\u2013" not in _enforce_house_punctuation("a \\u2013 b") and " -- " not in _enforce_house_punctuation("a -- b"))
check("guard: hyphenated words and unspaced ranges untouched",
      _enforce_house_punctuation("day-to-day follow-up, 2020\\u20132024?") == "day-to-day follow-up, 2020\\u20132024?")
check("guard: clean text unchanged",
      _enforce_house_punctuation("What stands out to you right now?") == "What stands out to you right now?")
check("prompt: punctuation rule present, prompt itself has no em-dash",
      "never use em dashes" in NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT
      and "\\u2014" not in NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT)
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    edited = {}
    for rel, old, new, label in EDITS:
        p = pathlib.Path(rel)
        t = edited.get(p, p.read_text(encoding='utf-8'))
        if t.count(old) != 1:
            print(f'ERROR: {p} :: {label} anchor found {t.count(old)} times.', file=sys.stderr)
            sys.exit(1)
        edited[p] = t.replace(old, new, 1)
        print(f'[{p} :: {label}] OK')
    tt = TEST_FILE.read_text(encoding='utf-8')
    if tt.count(TEST_ANCHOR) != 1:
        print('ERROR: test anchor not found once.', file=sys.stderr)
        sys.exit(1)
    edited[TEST_FILE] = tt.replace(TEST_ANCHOR, TEST_ANCHOR + TEST_ADD, 1)
    print(f'[{TEST_FILE} :: punctuation tests] OK')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    for p, t in edited.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE (edited): {p}')


if __name__ == '__main__':
    main()
