"""
Call 3 (executive summary) length (Pete, 2026-09-27): the live hr-dx run
returned about 5 sentences against the 2-3 sentence spec. Two layers, same
pattern as the narrative-question punctuation fix: the prompt now says
exactly 2 or 3 sentences and at most 70 words, and a deterministic guard
keeps only the first 3 sentences whatever comes back. max_tokens 300 -> 200.

Usage: python tools/patch_exec_summary_length.py --dry-run | --write
"""
import argparse
import pathlib
import sys

ES = pathlib.Path('engine/exec_summary.py')
T = pathlib.Path('tools/test_phase1_report_data.py')
BS = '\\'  # one literal backslash (prompt line continuations inside the source)

EDITS = [
    ('import os\n', 'import os\nimport re\n', 'import re'),
    ('Write 2 to 3 sentences that connect the two: what the organizational finding ' + BS + '\n',
     'Write exactly 2 or 3 sentences, and no more than 70 words in total, that ' + BS + '\n'
     'connect the two: what the organizational finding ' + BS + '\n',
     'prompt length rule'),
    ('- Output only the summary text. No heading, no quotation marks, no markdown.\n',
     '- Length is strict: 2 or 3 sentences, 70 words at most. Stop after the third ' + BS + '\n'
     'sentence.\n'
     '- Output only the summary text. No heading, no quotation marks, no markdown.\n',
     'prompt strict rule'),
    ('def _build_exec_prompt(',
     '_SENTENCE_END_RE = re.compile(r"(?<=[.!?])' + BS + 's+(?=[A-Z])")\n'
     'MAX_SENTENCES = 3\n'
     '\n'
     '\n'
     'def _limit_sentences(text: str, limit: int = MAX_SENTENCES) -> str:\n'
     '    """Keep at most `limit` sentences. The prompt asks for 2-3, and this guard\n'
     '    guarantees the ceiling (a live run returned about 5). Splits only where a\n'
     '    sentence end is followed by a capitalized word, so decimals and "e.g."\n'
     '    mid-sentence are not treated as boundaries."""\n'
     '    sentences = [s.strip() for s in _SENTENCE_END_RE.split(text.strip()) if s.strip()]\n'
     '    return " ".join(sentences[:limit])\n'
     '\n'
     '\n'
     'def _build_exec_prompt(',
     'guard function'),
    ('            max_tokens=300,\n', '            max_tokens=200,\n', 'max_tokens'),
    ('        text = _enforce_house_punctuation(message.content[0].text.strip())\n',
     '        text = _limit_sentences(_enforce_house_punctuation(message.content[0].text.strip()))\n',
     'apply guard'),
]

TEST = '''
# ── 10. Executive summary length ─────────────────────────────────────────────────
from engine.exec_summary import _limit_sentences, EXEC_SUMMARY_SYSTEM_PROMPT
five = "One thing. Two things here. Three is fine. Four is too many. Five is right out."
check("exec summary guard keeps at most 3 sentences",
      _limit_sentences(five) == "One thing. Two things here. Three is fine.", _limit_sentences(five))
check("exec summary guard leaves 2-3 sentences untouched",
      _limit_sentences("A short one. And a second.") == "A short one. And a second.")
check("exec summary guard does not split on decimals or a lowercase continuation",
      _limit_sentences("Costs rose 2.5 times. Then e.g. more. Three. Four.") == "Costs rose 2.5 times. Then e.g. more. Three.",
      _limit_sentences("Costs rose 2.5 times. Then e.g. more. Three. Four."))
check("exec summary prompt states the strict length",
      "exactly 2 or 3 sentences" in EXEC_SUMMARY_SYSTEM_PROMPT and "70 words" in EXEC_SUMMARY_SYSTEM_PROMPT)
'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    a = ap.parse_args()
    t = ES.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        if t.count(old) != 1:
            print(f'ERROR {label} x{t.count(old)}', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{ES} :: {label}] OK')
    tt = T.read_text(encoding='utf-8')
    i = tt.index('RESULT: {passed} passed')
    ls = tt.rindex('\n', 0, i) + 1
    tt = tt[:ls] + TEST.lstrip('\n') + '\n' + tt[ls:]
    print(f'[{T} :: length tests] OK')
    if a.dry_run:
        print('DRY RUN -- nothing written.')
        return
    ES.write_text(t, encoding='utf-8')
    T.write_text(tt, encoding='utf-8')
    print('WROTE')


if __name__ == '__main__':
    main()
