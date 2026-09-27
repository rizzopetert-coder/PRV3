"""
Compound resolution_family grammar (Pete, 2026-09-27): live Production output
read "People Tactics & Strategy and First Call is built for exactly this
moment..." -- Sonnet 5 echoes the synthesis prompt's resolution_family
verbatim as a sentence subject, and "A and B" is a plural subject taking a
singular verb.

Fix, prompt line only (same scope as 95a4491): _family_as_prose() joins the
parts with "with" -- "A with B" (three parts: "A with B and C"). The
head noun stays singular, so the echo reads grammatically with "is":
"People Tactics & Strategy with First Call is built for...". The "+" form is
still what get_fallback_synthesis() receives, so compound backup-copy keys
keep resolving. hr-dx context strings have no " + " and are unaffected.

Usage:
    python tools/patch_compound_family_singular_subject.py --dry-run
    python tools/patch_compound_family_singular_subject.py --write
"""
import argparse
import pathlib
import sys

EDITS = [
    ('engine/output_synthesis.py',
     '    Render a "+"-joined commercial compound as prose for the synthesis\n'
     '    prompt ("A + B" -> "A and B", "A + B + C" -> "A, B and C"). The\n'
     '    model echoes resolution_family verbatim, and a literal "+" read as\n'
     '    prose ("People Tactics & Strategy + First Call is built to...").\n'
     '    Prompt-only: the "+" form is still what get_fallback_synthesis()\n'
     '    receives, so the compound backup-copy keys keep resolving.\n'
     '    """\n'
     '    parts = [p.strip() for p in resolution_family.split(" + ") if p.strip()]\n'
     '    if len(parts) <= 1:\n'
     '        return resolution_family\n'
     '    return ", ".join(parts[:-1]) + " and " + parts[-1]\n',
     '    Render a "+"-joined commercial compound as prose for the synthesis\n'
     '    prompt ("A + B" -> "A with B", "A + B + C" -> "A with B and C").\n'
     '    The model echoes resolution_family verbatim as a sentence subject:\n'
     '    a literal "+" read as prose, and "A and B" is a plural subject the\n'
     '    model pairs with a singular verb ("...and First Call is built").\n'
     '    "with" keeps the head noun singular, so the echo stays grammatical.\n'
     '    Prompt-only: the "+" form is still what get_fallback_synthesis()\n'
     '    receives, so the compound backup-copy keys keep resolving.\n'
     '    """\n'
     '    parts = [p.strip() for p in resolution_family.split(" + ") if p.strip()]\n'
     '    if len(parts) <= 1:\n'
     '        return resolution_family\n'
     '    if len(parts) == 2:\n'
     '        return f"{parts[0]} with {parts[1]}"\n'
     '    return f"{parts[0]} with " + ", ".join(parts[1:-1]) + " and " + parts[-1]\n',
     'singular-subject join'),
    ('tools/test_output_synthesis.py',
     '    "_build_synthesis_prompt: compound family rendered as prose, no literal \'+\'",\n'
     '    "resolution_family: People Tactics & Strategy and First Call" in _compound_prompt\n',
     '    "_build_synthesis_prompt: compound family rendered as singular-subject prose, no literal \'+\'",\n'
     '    "resolution_family: People Tactics & Strategy with First Call" in _compound_prompt\n',
     'test pin'),
    ('tools/test_output_synthesis.py',
     '    _compound_prompt.split("resolution_family:")[1].splitlines()[0],\n'
     ')\n',
     '    _compound_prompt.split("resolution_family:")[1].splitlines()[0],\n'
     ')\n'
     'from engine.output_synthesis import _family_as_prose\n'
     'check(\n'
     '    "_family_as_prose: three-part compound keeps a singular head noun",\n'
     '    _family_as_prose("A + B + C") == "A with B and C",\n'
     '    _family_as_prose("A + B + C"),\n'
     ')\n'
     'check(\n'
     '    "_family_as_prose: single family unchanged",\n'
     '    _family_as_prose("First Call") == "First Call",\n'
     '    _family_as_prose("First Call"),\n'
     ')\n',
     'three-part + single tests'),
]


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
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    for p, t in edited.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE (edited): {p}')


if __name__ == '__main__':
    main()
