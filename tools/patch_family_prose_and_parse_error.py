"""
Three fixes from the 2026-09-26 Sonnet 5 verification round (Pete-approved).

1. hr-dx urgency cue (Option A): hr_diagnostic_synthesis_family() now puts
   the urgency cue directly after the name -- "HR Consulting on an urgent
   basis[, through <refs>]" -- instead of appending ", engaged immediately".
   Sonnet 5 echoes this context string verbatim at the start of
   resolution_framing_text; live output read "HR Consulting, engaged
   immediately, gives this organization...". The new form reads as ordinary
   prose when echoed. Backup-copy lookup keys regenerate from the same
   function, so HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT follows automatically.

2. PR compound joiner: the synthesis prompt line received the raw
   "+"-joined commercial string, and Sonnet 5 echoed it literally ("People
   Tactics & Strategy + First Call is built to help..."). The fix is scoped
   to the prompt line only, in _build_synthesis_prompt(): " + " parts are
   rendered as prose ("A and B", "A, B and C"). The resolution_family value
   synthesize() passes to get_fallback_synthesis() is untouched, so the
   "+"-keyed RESOLUTION_FALLBACK_COPY compound entries still resolve. The
   displayed resolution_family on the results page is not in scope (UI
   label, not AI context). hr-dx strings contain no " + " and are unaffected.

3. parse_error in the /api/complete output: engine/contract.py's
   synthesis_dict listed fields explicitly and omitted parse_error, so the
   web [DIAG] synthesis-fallback log could only say THAT a fallback
   happened ("(no parse_error)"), never why. Additive-only, checked before
   writing: the contract validator and test_main.py check required-field
   PRESENCE, never an exact key set, and every consumer (diagnostic-
   completion.ts, result/route.ts, share/create/route.ts, output-renderer.ts)
   maps named fields into its own object -- parse_error reaches the server
   log, never the browser payload. raw_response deliberately NOT added (can
   carry model text; not needed to diagnose).

Tests: test_hr_diagnostic_brand.py pins the new Intervention string, adds a
urgency+reference combo check, and asserts parse_error is populated on the
real fallback path through assemble_output(). test_output_synthesis.py adds
a compound-prose check on _build_synthesis_prompt().

Usage:
    python tools/patch_family_prose_and_parse_error.py --dry-run
    python tools/patch_family_prose_and_parse_error.py --write
"""
import argparse
import pathlib
import sys

EDITS = [
    # ── 1. hr-dx urgency cue ──────────────────────────────────────────────────
    ('engine/resolution_families.py',
     '    synthesis prompt receives -- "HR Consulting", plus ", through <refs>"\n'
     '    for Development / Executive Counsel and ", engaged immediately" when\n'
     '    Intervention is present. Empty or wholly-unknown input returns "" (same\n'
     '    as the PR path\'s empty-routing case).\n',
     '    synthesis prompt receives -- "HR Consulting", plus " on an urgent\n'
     '    basis" directly after the name when Intervention is present, then\n'
     '    ", through <refs>" for Development / Executive Counsel. The model\n'
     '    tends to echo this string verbatim, so it is worded to read as\n'
     '    ordinary prose when it does. Empty or wholly-unknown input returns ""\n'
     '    (same as the PR path\'s empty-routing case).\n',
     'hr docstring'),
    ('engine/resolution_families.py',
     '    text = HR_DIAGNOSTIC_FAMILY_NAME\n'
     '    if refs:\n'
     '        text += ", through " + " and ".join(refs)\n'
     '    if _HR_DIAGNOSTIC_URGENT_FAMILY in parts:\n'
     '        text += ", engaged immediately"\n'
     '    return text\n',
     '    text = HR_DIAGNOSTIC_FAMILY_NAME\n'
     '    if _HR_DIAGNOSTIC_URGENT_FAMILY in parts:\n'
     '        text += " on an urgent basis"\n'
     '    if refs:\n'
     '        text += ", through " + " and ".join(refs)\n'
     '    return text\n',
     'hr urgency cue'),

    # ── 2. PR compound joiner (prompt line only) ──────────────────────────────
    ('engine/output_synthesis.py',
     'def _build_synthesis_prompt(\n',
     'def _family_as_prose(resolution_family: str) -> str:\n'
     '    """\n'
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
     '    return ", ".join(parts[:-1]) + " and " + parts[-1]\n'
     '\n'
     '\n'
     'def _build_synthesis_prompt(\n',
     'prose helper'),
    ('engine/output_synthesis.py',
     '        f"resolution_family: {resolution_family}",\n',
     '        f"resolution_family: {_family_as_prose(resolution_family)}",\n',
     'prompt line uses prose'),

    # ── 3. parse_error in /api/complete synthesis output ──────────────────────
    ('engine/contract.py',
     '            "is_fallback":                  synthesis_result.is_fallback,\n',
     '            "is_fallback":                  synthesis_result.is_fallback,\n'
     '            # Why a fallback happened (API error, parse failure); None on\n'
     '            # success. Additive -- consumers map named fields only. Read\n'
     '            # by web/lib/diagnostic-completion.ts\'s [DIAG] log, never\n'
     '            # forwarded to the client payload.\n'
     '            "parse_error":                  synthesis_result.parse_error,\n',
     'contract parse_error'),

    # ── tests ─────────────────────────────────────────────────────────────────
    ('tools/test_hr_diagnostic_brand.py',
     '    "Intervention": "HR Consulting, engaged immediately",\n',
     '    "Intervention": "HR Consulting on an urgent basis",\n',
     'pin new Intervention string'),
    ('tools/test_hr_diagnostic_brand.py',
     'check("empty -> empty", hr_diagnostic_synthesis_family("") == "")\n',
     'check("empty -> empty", hr_diagnostic_synthesis_family("") == "")\n'
     'check("urgency + reference combo reads as prose",\n'
     '      hr_diagnostic_synthesis_family("Executive Counsel + Intervention")\n'
     '      == "HR Consulting on an urgent basis, through Employee Development, Coaching & Performance Management")\n'
     'check("old \'engaged immediately\' cue gone from every context string",\n'
     '      all("engaged immediately" not in c for c in HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT))\n',
     'combo + old-cue checks'),
    ('tools/test_hr_diagnostic_brand.py',
     '        check(f"[{routing}] hr synthesis is fallback", hs["is_fallback"] is True)\n',
     '        check(f"[{routing}] hr synthesis is fallback", hs["is_fallback"] is True)\n'
     '        check(f"[{routing}] parse_error surfaced in /api/complete output",\n'
     '              bool(hs.get("parse_error")), repr(hs.get("parse_error")))\n',
     'parse_error surfaced check'),
    ('tools/test_output_synthesis.py',
     'check(\n'
     '    "_build_synthesis_prompt: includes resolution_family",\n'
     '    "Groundwork" in prompt_text,\n'
     '    "resolution_family not found",\n'
     ')\n',
     'check(\n'
     '    "_build_synthesis_prompt: includes resolution_family",\n'
     '    "Groundwork" in prompt_text,\n'
     '    "resolution_family not found",\n'
     ')\n'
     '_compound_prompt = _build_synthesis_prompt(\n'
     '    state_name="Built to Fail", severity_tier="Emerging",\n'
     '    resolution_family="People Tactics & Strategy + First Call",\n'
     '    asset_score=0.1, liability_score=0.5, narrative_response="", intake={},\n'
     ')\n'
     'check(\n'
     '    "_build_synthesis_prompt: compound family rendered as prose, no literal \'+\'",\n'
     '    "resolution_family: People Tactics & Strategy and First Call" in _compound_prompt\n'
     '    and " + " not in _compound_prompt.split("resolution_family:")[1].splitlines()[0],\n'
     '    _compound_prompt.split("resolution_family:")[1].splitlines()[0],\n'
     ')\n',
     'compound prose check'),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    edited = {}
    for rel, old, new, label in EDITS:
        path = pathlib.Path(rel)
        text = edited.get(path, path.read_text(encoding='utf-8'))
        count = text.count(old)
        if count != 1:
            print(f'ERROR: {path} :: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
            sys.exit(1)
        edited[path] = text.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')

    if args.dry_run:
        print('DRY RUN -- all anchors found. Nothing written.')
        return
    for path, text in edited.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
