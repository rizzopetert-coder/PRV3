"""
Model migration claude-sonnet-4-6 -> claude-sonnet-5 (Pete, 2026-09-26), plus
a permanent diagnostic for swallowed synthesis errors.

Why: every synthesis on the split Preview engine fell back in 0.6-2.8s
(real generation takes several seconds). Pete confirmed the prv3-engine key
works against claude-sonnet-5 via a direct request. The engine, the narrative
engine, the /api/interpret route, and the research refresh script all
hard-coded claude-sonnet-4-6 (8 code sites + 2 tests, no shared constant).

Request-shape changes required by Sonnet 5 (Claude API reference), not
optional tuning:
  - temperature removed: sampling params (temperature/top_p/top_k) return a
    400 on Sonnet 5. Affects synthesize(), extract_signals(),
    generate_narrative_prompt().
  - thinking={"type": "disabled"}: Sonnet 5 runs adaptive thinking when
    `thinking` is omitted. These callers read message.content[0].text and
    budget 150-800 max_tokens under a 15s timeout -- a thinking block in
    content[0] (or thinking spending the token budget) would fail the parse
    and fall back again. Disabled is the closest match to the current
    non-thinking behavior. Applied to the three engine calls and
    /api/interpret (same content[0] read).
  - research/refresh-log/run_refresh.py: model swap only -- it sends no
    temperature and already filters for text blocks, so adaptive thinking is
    compatible there.

Diagnostic: completeDiagnosticSession() logs synthesis.parse_error
(key-like strings redacted) whenever the engine returns is_fallback=true --
this class of error was invisible end to end (engine swallowed it, web
dropped the field). EngineResult.synthesis gains optional parse_error (the
engine already returns it via asdict(SynthesisResult)).

Usage:
    python tools/patch_model_sonnet5_and_synthesis_diag.py --dry-run
    python tools/patch_model_sonnet5_and_synthesis_diag.py --write
"""
import argparse
import pathlib
import sys

OLD, NEW = 'claude-sonnet-4-6', 'claude-sonnet-5'

EDITS = [
    # ── engine/output_synthesis.py ────────────────────────────────────────────
    ('engine/output_synthesis.py', f'    model: str = "{OLD}",\n    client=None,\n    timeout: float = 15.0,\n',
     f'    model: str = "{NEW}",\n    client=None,\n    timeout: float = 15.0,\n', 'synthesize default model'),
    ('engine/output_synthesis.py', f'    def __init__(self, model: str = "{OLD}", client=None):\n',
     f'    def __init__(self, model: str = "{NEW}", client=None):\n', 'OutputSynthesisEngine default model'),
    ('engine/output_synthesis.py',
     '            max_tokens=800,\n            temperature=0.3,\n            system=OUTPUT_SYNTHESIS_SYSTEM_PROMPT,\n',
     '            max_tokens=800,\n'
     '            # Sonnet 5: sampling params (temperature) return a 400, and\n'
     '            # omitting `thinking` runs adaptive thinking -- content[0]\n'
     '            # below must be the text block, within 800 tokens / 15s.\n'
     '            thinking={"type": "disabled"},\n'
     '            system=OUTPUT_SYNTHESIS_SYSTEM_PROMPT,\n', 'synthesis call shape'),

    # ── engine/narrative.py ───────────────────────────────────────────────────
    ('engine/narrative.py', f'    narrative_text: str,\n    model: str = "{OLD}",\n',
     f'    narrative_text: str,\n    model: str = "{NEW}",\n', 'extract_signals default model'),
    ('engine/narrative.py', f'    context: dict,\n    model: str = "{OLD}",\n',
     f'    context: dict,\n    model: str = "{NEW}",\n', 'generate_narrative_prompt default model'),
    ('engine/narrative.py', f'        engine = NarrativeModulationEngine(model="{OLD}")\n',
     f'        engine = NarrativeModulationEngine(model="{NEW}")\n', 'narrative engine instantiation'),
    ('engine/narrative.py', f'    def __init__(self, model: str = "{OLD}", client=None):\n',
     f'    def __init__(self, model: str = "{NEW}", client=None):\n', 'NarrativeModulationEngine default'),
    ('engine/narrative.py',
     '            max_tokens=500,\n            temperature=0.2,\n            system=NARRATIVE_SYSTEM_PROMPT,\n',
     '            max_tokens=500,\n'
     '            # Sonnet 5: no temperature (400), thinking off so content[0]\n'
     '            # is the text block.\n'
     '            thinking={"type": "disabled"},\n'
     '            system=NARRATIVE_SYSTEM_PROMPT,\n', 'extract_signals call shape'),
    ('engine/narrative.py',
     '            max_tokens=150,\n            temperature=0.6,\n            system=NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT,\n',
     '            max_tokens=150,\n'
     '            # Sonnet 5: no temperature (400), thinking off so content[0]\n'
     '            # is the text block within 150 tokens.\n'
     '            thinking={"type": "disabled"},\n'
     '            system=NARRATIVE_PROMPT_GENERATION_SYSTEM_PROMPT,\n', 'narrative prompt call shape'),

    # ── web/app/api/interpret/route.ts ────────────────────────────────────────
    ('web/app/api/interpret/route.ts',
     f'    model: "{OLD}",\n    max_tokens: 200,\n',
     f'    model: "{NEW}",\n    max_tokens: 200,\n'
     '    // Sonnet 5 runs adaptive thinking unless disabled; content[0] below\n'
     '    // must be the text block.\n'
     '    thinking: { type: "disabled" },\n', 'interpret route'),

    # ── research/refresh-log/run_refresh.py ───────────────────────────────────
    ('research/refresh-log/run_refresh.py', f'            model="{OLD}",\n',
     f'            model="{NEW}",\n', 'research refresh model'),

    # ── tests ─────────────────────────────────────────────────────────────────
    ('tools/test_narrative.py', f'engine = NarrativeModulationEngine(model="{OLD}")\n',
     f'engine = NarrativeModulationEngine(model="{NEW}")\n', 'test_narrative instantiation'),
    ('tools/test_narrative.py', f'check("Engine default model", engine.model == "{OLD}")\n',
     f'check("Engine default model", engine.model == "{NEW}")\n', 'test_narrative assertion'),
    ('tools/test_output_synthesis.py', f'engine = OutputSynthesisEngine(model="{OLD}")\n',
     f'engine = OutputSynthesisEngine(model="{NEW}")\n', 'test_output_synthesis instantiation'),

    # ── diagnostic: web/lib/engine-client.ts + diagnostic-completion.ts ──────
    ('web/lib/engine-client.ts',
     '    synthesis_confidence:         number;\n    is_fallback:                  boolean;\n  } | null;\n  engine_version: string;\n',
     '    synthesis_confidence:         number;\n    is_fallback:                  boolean;\n'
     '    // Present when is_fallback -- the swallowed error detail (API error,\n'
     '    // parse failure). Logged, never forwarded to the client payload.\n'
     '    parse_error?:                 string | null;\n  } | null;\n  engine_version: string;\n',
     'EngineResult.synthesis.parse_error'),
    ('web/lib/diagnostic-completion.ts',
     '  const engSynthesis = engineResult.synthesis;\n',
     '  const engSynthesis = engineResult.synthesis;\n'
     '  // Synthesis failures are swallowed engine-side (static backup copy) and\n'
     '  // the error detail never reached the client -- log it here so a silent\n'
     '  // fallback is diagnosable from runtime logs. Key-like strings redacted.\n'
     '  if (engSynthesis?.is_fallback) {\n'
     '    const detail = (engSynthesis.parse_error ?? "(no parse_error)")\n'
     '      .replace(/sk-ant-[A-Za-z0-9_-]+/g, "[redacted-key]")\n'
     '      .slice(0, 500);\n'
     '    console.warn("[DIAG] synthesis fallback", { brand: session.brand, detail });\n'
     '  }\n',
     'fallback diagnostic log'),
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

    leftovers = {str(p): t.count(OLD) for p, t in edited.items() if OLD in t}
    if leftovers:
        print(f'ERROR: {OLD} still present after edits: {leftovers}', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print('DRY RUN -- all anchors found, no old model ID left in edited files. Nothing written.')
        return
    for path, text in edited.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
