"""
Phase 1 (report redesign), commit 4: tactical pre-aggregation and the
three-call synthesis flow (Pete, 2026-09-27, Gemini-reviewed spec).

New modules (created alongside this script): engine/tactical_synthesis.py
(build_tactical_summary, synthesize_tactical = Call 2) and
engine/exec_summary.py (generate_executive_summary = Call 3).

Edits:
  engine/output_synthesis.py  SynthesisResult gains executive_summary: str = ""
                              (defaulted, so every existing constructor and the
                              fallback path are unchanged). Call 1's prompt,
                              inputs, and code path are NOT touched.
  engine/contract.py          assemble_output(tactical_findings=None):
                              private_output["tactical_findings"] (always a
                              list, [] when none), synthesis.executive_summary.
  engine/main.py              run_accumulated_engine():
      Step A (concurrent): Call 2 starts in a worker thread right before the
        existing Call 1 block and is collected right after it. Call 1's code
        is not moved or changed, and it receives no tactical data.
      Step B (sequential): Call 3 runs only when Call 1 succeeded (not a
        fallback) AND Call 2 succeeded, from Call 1's
        liability_condition_text plus the raw tactical counts. Otherwise
        executive_summary is "".
      One [PHASE1] timing line per completion goes to the engine logs.

Threads, not asyncio.gather: run_accumulated_engine() is synchronous (the
FastAPI handler calls it directly), and a worker thread gives the same
overlap without converting the engine to async.

Usage:
    python tools/patch_phase1_three_call.py --dry-run
    python tools/patch_phase1_three_call.py --write
"""
import argparse
import pathlib
import sys

OS = pathlib.Path('engine/output_synthesis.py')
CT = pathlib.Path('engine/contract.py')
MN = pathlib.Path('engine/main.py')

EDITS = {
    OS: [
        ('    raw_response:                 str  = ""\n'
         '    parse_error:                  str  = ""\n'
         '    is_fallback:                  bool = False\n',
         '    raw_response:                 str  = ""\n'
         '    parse_error:                  str  = ""\n'
         '    is_fallback:                  bool = False\n'
         '    # Phase 1 Call 3 (engine/exec_summary.py), set by\n'
         '    # run_accumulated_engine() after this call returns. Never produced\n'
         '    # by this module\'s own LLM call or its fallback.\n'
         '    executive_summary:            str  = ""\n',
         'SynthesisResult.executive_summary'),
    ],
    CT: [
        ('    session: SessionData, synthesis_result=None, trajectory_result=None, answers_log=None,\n'
         '    brand: str = "principal_resolution",\n'
         ') -> dict:\n',
         '    session: SessionData, synthesis_result=None, trajectory_result=None, answers_log=None,\n'
         '    brand: str = "principal_resolution", tactical_findings=None,\n'
         ') -> dict:\n',
         'tactical_findings param'),
        ('    if service_cost_comparison is not None:\n'
         '        private_output["service_cost_comparison"] = service_cost_comparison\n',
         '    if service_cost_comparison is not None:\n'
         '        private_output["service_cost_comparison"] = service_cost_comparison\n'
         '    # Phase 1 Call 2 output: always a list, [] when the session has no\n'
         '    # TC-* answers or the tactical call failed.\n'
         '    private_output["tactical_findings"] = list(tactical_findings or [])\n',
         'attach tactical_findings'),
        ('            "parse_error":                  synthesis_result.parse_error,\n'
         '        }\n',
         '            "parse_error":                  synthesis_result.parse_error,\n'
         '            # Phase 1 Call 3, "" when skipped or failed.\n'
         '            "executive_summary":            getattr(synthesis_result, "executive_summary", ""),\n'
         '        }\n',
         'synthesis.executive_summary'),
    ],
    MN: [
        ('from engine.output_synthesis import OutputSynthesisEngine, SynthesisResult\n',
         'from engine.output_synthesis import OutputSynthesisEngine, SynthesisResult\n'
         'from engine.tactical_synthesis import build_tactical_summary, synthesize_tactical, tactical_totals\n'
         'from engine.exec_summary import generate_executive_summary\n'
         'from concurrent.futures import ThreadPoolExecutor\n'
         'import time\n',
         'imports'),
        ('    output_package = output_engine.build(final_rankings, severity_result)\n'
         '\n'
         '    synthesis_result = None\n'
         '    if final_rankings:\n'
         '        lead_id = final_rankings[0].state_id\n'
         '        lead_name = (\n',
         '    output_package = output_engine.build(final_rankings, severity_result)\n'
         '\n'
         '    # Phase 1 Step A: Call 2 (tactical synthesis) runs in a worker thread\n'
         '    # concurrently with Call 1 below. It gets ONLY the deterministic\n'
         '    # TC-* pre-aggregation, and Call 1 gets no tactical data at all.\n'
         '    tactical_summary = build_tactical_summary(answers_log or [])\n'
         '    _phase1_t0 = time.monotonic()\n'
         '\n'
         '    def _timed_call_2():\n'
         '        _t = time.monotonic()\n'
         '        _findings, _ok, _err = synthesize_tactical(tactical_summary)\n'
         '        return _findings, _ok, _err, time.monotonic() - _t\n'
         '\n'
         '    _call_2_pool = ThreadPoolExecutor(max_workers=1)\n'
         '    _call_2_future = _call_2_pool.submit(_timed_call_2) if tactical_summary else None\n'
         '\n'
         '    synthesis_result = None\n'
         '    if final_rankings:\n'
         '        lead_id = final_rankings[0].state_id\n'
         '        lead_name = (\n',
         'Step A: start Call 2'),
        ('        )\n'
         '\n'
         '    duration_band = next(\n',
         '        )\n'
         '    _call_1_s = time.monotonic() - _phase1_t0\n'
         '\n'
         '    tactical_findings, tactical_ok, tactical_err, _call_2_s = [], False, "not run", 0.0\n'
         '    if _call_2_future is not None:\n'
         '        tactical_findings, tactical_ok, tactical_err, _call_2_s = _call_2_future.result()\n'
         '    _call_2_pool.shutdown(wait=False)\n'
         '\n'
         '    # Phase 1 Step B: Call 3 (executive summary), sequential, only when\n'
         '    # Call 1 produced real synthesis and Call 2 succeeded.\n'
         '    executive_summary, exec_ok, exec_err, _call_3_s = "", False, "skipped", 0.0\n'
         '    if synthesis_result is not None and not synthesis_result.is_fallback and tactical_ok:\n'
         '        _t = time.monotonic()\n'
         '        executive_summary, exec_ok, exec_err = generate_executive_summary(\n'
         '            synthesis_result.liability_condition_text, tactical_totals(tactical_summary),\n'
         '        )\n'
         '        _call_3_s = time.monotonic() - _t\n'
         '    if synthesis_result is not None:\n'
         '        synthesis_result.executive_summary = executive_summary\n'
         '    print(\n'
         '        f"[PHASE1] brand={brand} call1={_call_1_s:.1f}s "\n'
         '        f"call1_fallback={synthesis_result.is_fallback if synthesis_result else None} "\n'
         '        f"call2={_call_2_s:.1f}s ok={tactical_ok} ({tactical_err or \'-\'}) "\n'
         '        f"call3={_call_3_s:.1f}s ok={exec_ok} ({exec_err or \'-\'})",\n'
         '        flush=True,\n'
         '    )\n'
         '\n'
         '    duration_band = next(\n',
         'collect Call 2, Step B'),
        ('        answers_log=answers_log, brand=brand,\n'
         '    )\n',
         '        answers_log=answers_log, brand=brand, tactical_findings=tactical_findings,\n'
         '    )\n',
         'pass tactical_findings'),
    ],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    for f in ('engine/tactical_synthesis.py', 'engine/exec_summary.py'):
        if not pathlib.Path(f).exists():
            print(f'ERROR: {f} missing.', file=sys.stderr)
            sys.exit(1)
    out = {}
    for path, edits in EDITS.items():
        t = path.read_text(encoding='utf-8')
        for old, new, label in edits:
            n = t.count(old)
            if n != 1:
                print(f'ERROR: {path} :: {label} anchor found {n} times.', file=sys.stderr)
                sys.exit(1)
            t = t.replace(old, new, 1)
            print(f'[{path} :: {label}] OK')
        out[path] = t
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    for path, t in out.items():
        path.write_text(t, encoding='utf-8')
        print(f'WROTE: {path}')


if __name__ == '__main__':
    main()
