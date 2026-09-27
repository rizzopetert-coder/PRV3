"""
Narrative question referenced "your school" for a Professional Services /
privately held intake (Pete, 2026-09-27 bug report 1). Reproduced on
Preview: 1 of 24 sampled narrative questions said "your school".

Root cause: no few-shot example or placeholder exists, and intake is not
interpolated into this call at all -- generate_narrative_prompt() receives
only the top states' descriptive_prose (none of which mention schools) and
the entropy. The only organizational cue the model gets is the system
prompt's own first line, "a question for a principal completing an
organizational diagnostic". With no other context, "principal" reads as a
school principal, and the model occasionally writes "your school".

Fix (engine prompt text only, no data-contract change):
  - The respondent is described as the leader of an organization (owner,
    executive, or senior manager). "principal" no longer appears anywhere
    in the model-facing text (system prompt or user content).
  - New rule: the model is not told what kind of organization this is, so
    it refers to it only as "your organization" and never names or implies
    a type or sector.
Passing real intake (industry, org type, size) into this call would ground
it further but changes the web -> engine payload, a data-contract change
that routes through Gemini per CLAUDE.md. Not done here.

Usage:
    python tools/patch_narrative_prompt_org_type.py --dry-run
    python tools/patch_narrative_prompt_org_type.py --write
"""
import argparse
import pathlib
import sys

P = pathlib.Path('engine/narrative.py')
T = pathlib.Path('tools/test_narrative.py')

EDITS = [
    ('You write ONE open-ended question for a principal completing an \\\n'
     'organizational diagnostic. Your question invites them to describe, in \\\n',
     'You write ONE open-ended question for the leader of an organization \\\n'
     '(an owner, executive, or senior manager) who is completing an \\\n'
     'organizational diagnostic. Your question invites them to describe, in \\\n',
     'opening line'),
    ('You are given internal signal only -- never repeat it back, never name \\\n'
     'it, never let the principal infer it from your phrasing. Use it only to \\\n',
     'You are given internal signal only. Never repeat it back, never name \\\n'
     'it, never let the respondent infer it from your phrasing. Use it only to \\\n',
     'internal-signal line'),
    ('- Never presuppose an answer or imply a problem exists. The principal \\\n',
     '- Never presuppose an answer or imply a problem exists. The respondent \\\n',
     'presuppose rule'),
    ('- Plain, direct language. No jargon. Second person ("you," "your \\\n'
     'organization").\n',
     '- Plain, direct language. No jargon. Second person ("you," "your \\\n'
     'organization").\n'
     '- You are not told what kind of organization this is. Refer to it only \\\n'
     'as "your organization" (or its people, teams, or leadership). Never name \\\n'
     'or imply a specific type of institution or sector, such as a school, \\\n'
     'hospital, church, or government agency.\n',
     'org-type rule'),
    ('            "general, open-ended question inviting the principal to add "\n',
     '            "general, open-ended question inviting the respondent to add "\n',
     'fallback input'),
    ('    lines = ["Internal signal (never reveal these details to the principal):"]\n',
     '    lines = ["Internal signal (never reveal these details to the respondent):"]\n',
     'signal header'),
]

TEST_ANCHOR = ('check("prompt: punctuation rule present, prompt itself has no em-dash",\n'
               '      "never use em dashes" in NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT\n'
               '      and "\\u2014" not in NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT)\n')
TEST_ADD = '''
# ── Organization-type grounding (2026-09-27): "principal" read as a school
# principal and produced "your school" for a business intake ─────────────────
from engine.narrative import _build_prompt_generation_input
check("prompt: never calls the respondent a principal",
      "principal" not in NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT.lower())
check("prompt: tells the model it is not told the organization type",
      "not told what kind of organization" in NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT
      and '"your organization"' in NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT)
check("prompt input: no 'principal' in either the empty or ranked user content",
      "principal" not in _build_prompt_generation_input({}).lower()
      and "principal" not in _build_prompt_generation_input(
          {"top_states": [{"state_id": "built_to_fail", "rank": 1}], "entropy": 4, "max_entropy": 5.83}).lower())
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    t = P.read_text(encoding='utf-8')
    for old, new, label in EDITS:
        if t.count(old) != 1:
            print(f'ERROR: {label} anchor found {t.count(old)} times.', file=sys.stderr)
            sys.exit(1)
        t = t.replace(old, new, 1)
        print(f'[{P} :: {label}] OK')
    tt = T.read_text(encoding='utf-8')
    if tt.count(TEST_ANCHOR) != 1:
        print('ERROR: test anchor not found once.', file=sys.stderr)
        sys.exit(1)
    tt = tt.replace(TEST_ANCHOR, TEST_ANCHOR + TEST_ADD, 1)
    print(f'[{T} :: org-type tests] OK')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    P.write_text(t, encoding='utf-8')
    T.write_text(tt, encoding='utf-8')
    print(f'WROTE: {P}, {T}')


if __name__ == '__main__':
    main()
