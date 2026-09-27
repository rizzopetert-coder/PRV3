"""
tools/diagnostic_fast_forward.py rework (Pete, 2026-09-27): make it the
reliable, permanent session driver instead of a tool that needed a scratchpad
wrapper to work at all.

Fixes, all found live 2026-09-26:
  - DEFAULT_INTAKE was missing org_type and significant_events, both now
    required by session/start's validateIntake() -- every run 400'd.
  - The answer loop assumed every non-complete response carries a question;
    status "narrative" (the narrative step) broke it. Now posts the
    narrative answer (--narrative-text, default "" = the route's deliberate
    skip path) and continues, capturing the generated narrative question.
  - Production guard knew only prv-3.vercel.app, not the custom domains.
    Now refuses all known Production hosts unless --allow-production is
    passed -- safe to opt into since test tagging: every request carries
    x-prv3-test-run: 1, so Production records are is_test=true.

Added:
  - --brand {principal_resolution,hr_diagnostic}: on Preview sends
    x-debug-brand (honored only off-Production). In Production, brand comes
    from the host -- use https://hr-dx.com for hr_diagnostic.
  - Results summary (brand, narrative question, resolution_family/routing,
    synthesis fallback flag, headline, resolution_framing_text) and
    --json-out to save the full completion response.
  - The /api/dev/diagnostic-preview link is only requested where that route
    exists (Preview, principal_resolution) and a failure there no longer
    aborts after a completed session.

Usage:
    python tools/patch_fast_forward_rework.py --dry-run
    python tools/patch_fast_forward_rework.py --write
"""
import argparse
import pathlib
import sys

P = pathlib.Path('tools/diagnostic_fast_forward.py')

EDITS = [
    ('Constraints:\n'
     '  - Preview only. --base-url must be an explicit Preview deployment URL;\n'
     '    the known stable Production alias (prv-3.vercel.app) is refused\n'
     '    outright, before any network call is made.\n',
     'Constraints:\n'
     '  - Preview by default. Every known Production host (prv-3.vercel.app,\n'
     '    principalresolution.com, hr-dx.com, and their www. forms) is refused\n'
     '    before any network call unless --allow-production is passed. Every\n'
     '    request carries x-prv3-test-run: 1, so Production runs are recorded\n'
     '    with is_test=true in diagnostic-aggregate (web/lib/test-run.ts).\n'
     '  - Handles the narrative step (status "narrative") by posting\n'
     '    --narrative-text (default "": the route\'s deliberate skip).\n'
     '  - --brand hr_diagnostic sends x-debug-brand on Preview. In Production\n'
     '    brand comes from the host: use https://hr-dx.com.\n',
     'docstring constraints'),
    ('PRODUCTION_HOST = "prv-3.vercel.app"\n',
     '# Every host that serves Production -- refused unless --allow-production.\n'
     'PRODUCTION_HOSTS = {\n'
     '    "prv-3.vercel.app",\n'
     '    "principalresolution.com",\n'
     '    "www.principalresolution.com",\n'
     '    "hr-dx.com",\n'
     '    "www.hr-dx.com",\n'
     '}\n',
     'production hosts'),
    ('    "jurisdiction": "CA",\n}\n',
     '    "jurisdiction": "CA",\n'
     '    # Both required by session/start\'s validateIntake() (the tool 400\'d on\n'
     '    # every run without them). org_type must be one of engine/data/\n'
     '    # intake.py\'s INTAKE_FIELDS["org_type"] values.\n'
     '    "org_type": "Privately held professional leadership",\n'
     '    "significant_events": ["none"],\n'
     '}\n',
     'intake fields'),
    ('    def __init__(self, base_url: str, bypass_secret: str | None):\n'
     '        self.base_url = base_url.rstrip("/")\n'
     '        self.bypass_secret = bypass_secret\n',
     '    def __init__(\n'
     '        self,\n'
     '        base_url: str,\n'
     '        bypass_secret: str | None,\n'
     '        extra_headers: dict | None = None,\n'
     '    ):\n'
     '        self.base_url = base_url.rstrip("/")\n'
     '        self.bypass_secret = bypass_secret\n'
     '        self.extra_headers = extra_headers or {}\n',
     'client extra headers'),
    ('        if self.bypass_secret:\n'
     '            headers["x-vercel-protection-bypass"] = self.bypass_secret\n'
     '        req = urllib.request.Request(url, data=data, headers=headers, method="POST")\n'
     '        try:\n'
     '            with urllib.request.urlopen(req, timeout=30) as resp:\n',
     '        headers.update(self.extra_headers)\n'
     '        if self.bypass_secret:\n'
     '            headers["x-vercel-protection-bypass"] = self.bypass_secret\n'
     '        req = urllib.request.Request(url, data=data, headers=headers, method="POST")\n'
     '        try:\n'
     '            # 60s: the completing answer runs synthesis (~10s) plus engine work.\n'
     '            with urllib.request.urlopen(req, timeout=60) as resp:\n',
     'client post headers + timeout'),
    ('def _guard_not_production(base_url: str) -> None:\n'
     '    host = urlparse(base_url).netloc\n'
     '    if host == PRODUCTION_HOST:\n'
     '        raise SystemExit(\n'
     '            f"REFUSED: {base_url!r} is the known Production alias ({PRODUCTION_HOST}). "\n'
     '            "This tool is Preview-only -- pass an actual Preview deployment URL, "\n'
     '            "e.g. https://prv-3-xxxxx-peter-rizzos-projects.vercel.app"\n'
     '        )\n',
     'def _guard_not_production(base_url: str, allow_production: bool = False) -> bool:\n'
     '    """Returns True if base_url is a Production host (only when allowed)."""\n'
     '    host = urlparse(base_url).netloc.lower()\n'
     '    if host in PRODUCTION_HOSTS:\n'
     '        if not allow_production:\n'
     '            raise SystemExit(\n'
     '                f"REFUSED: {base_url!r} is a Production host. Pass --allow-production "\n'
     '                "for a deliberate Production smoke test (recorded as is_test=true), or "\n'
     '                "use a Preview deployment URL, e.g. "\n'
     '                "https://prv-3-xxxxx-peter-rizzos-projects.vercel.app"\n'
     '            )\n'
     '        return True\n'
     '    return False\n',
     'production guard'),
    ('    intake: dict,\n'
     '    stop_before_question: int | None = None,\n',
     '    intake: dict,\n'
     '    stop_before_question: int | None = None,\n'
     '    narrative_text: str = "",\n',
     'drive_session narrative param'),
    ('        if answer_resp["status"] == "complete":\n'
     '            return {"mode": "complete", "session_id": session_id, "result": answer_resp["result"]}\n'
     '\n'
     '        question = answer_resp["question"]\n'
     '        label = answer_resp["label"]\n',
     '        # Narrative step: the route returns {status: "narrative", prompt}\n'
     '        # instead of a question. Answer it via the narrative route, which\n'
     '        # returns either the next question or the completed result.\n'
     '        if answer_resp["status"] == "narrative":\n'
     '            narrative_prompt = answer_resp.get("prompt")\n'
     '            answer_resp = client.post(\n'
     '                "/api/diagnostic/session/narrative",\n'
     '                {"session_id": session_id, "narrative_text": narrative_text},\n'
     '            )\n'
     '\n'
     '        if answer_resp["status"] == "complete":\n'
     '            return {\n'
     '                "mode": "complete",\n'
     '                "session_id": session_id,\n'
     '                "result": answer_resp["result"],\n'
     '                "narrative_prompt": narrative_prompt,\n'
     '                "raw": answer_resp,\n'
     '            }\n'
     '\n'
     '        question = answer_resp["question"]\n'
     '        label = answer_resp["label"]\n',
     'narrative handling'),
    ('    start_resp = client.post("/api/diagnostic/session/start", intake)\n',
     '    narrative_prompt = None\n'
     '    start_resp = client.post("/api/diagnostic/session/start", intake)\n',
     'narrative_prompt init'),
    ('        description="PRV3 diagnostic fast-forward tool -- Preview only, dev/test.",\n',
     '        description="PRV3 diagnostic fast-forward tool -- Preview by default, dev/test.",\n',
     'description'),
    ('    args = parser.parse_args()\n'
     '\n'
     '    _guard_not_production(args.base_url)\n',
     '    parser.add_argument(\n'
     '        "--brand", choices=["principal_resolution", "hr_diagnostic"], default="principal_resolution",\n'
     '        help="Preview: sends x-debug-brand for hr_diagnostic. Production: brand comes from the host.",\n'
     '    )\n'
     '    parser.add_argument(\n'
     '        "--narrative-text", default="",\n'
     '        help="Answer to the narrative step, if it fires (default empty: deliberate skip)",\n'
     '    )\n'
     '    parser.add_argument(\n'
     '        "--allow-production", action="store_true",\n'
     '        help="Permit a Production host (smoke test; recorded with is_test=true)",\n'
     '    )\n'
     '    parser.add_argument("--json-out", default=None, help="Write the full completion response to this file")\n'
     '    args = parser.parse_args()\n'
     '\n'
     '    is_production = _guard_not_production(args.base_url, args.allow_production)\n'
     '    if is_production and args.brand == "hr_diagnostic" and "hr-dx.com" not in args.base_url:\n'
     '        raise SystemExit("In Production, hr_diagnostic comes from the host -- use https://hr-dx.com.")\n',
     'new args + guard call'),
    ('    if not args.bypass_secret:\n',
     '    if not args.bypass_secret and not is_production:\n',
     'bypass warning preview-only'),
    ('    client = PreviewClient(args.base_url, args.bypass_secret)\n',
     '    extra_headers = {"x-debug-brand": "hr_diagnostic"} if args.brand == "hr_diagnostic" else {}\n'
     '    client = PreviewClient(\n'
     '        args.base_url, None if is_production else args.bypass_secret, extra_headers,\n'
     '    )\n',
     'client construction'),
    ('        stop_before_question=args.question if args.mode == "jump" else None,\n'
     '    )\n',
     '        stop_before_question=args.question if args.mode == "jump" else None,\n'
     '        narrative_text=args.narrative_text,\n'
     '    )\n',
     'pass narrative_text'),
    ('    preview_resp = client.post("/api/dev/diagnostic-preview", result)\n'
     '    print(f"\\nView the completed report: {preview_resp[\'url\']}")\n',
     '    synthesis = result.get("synthesis") or {}\n'
     '    print(f"session_id: {outcome[\'session_id\']}  |  brand: {args.brand}  |  production: {is_production}")\n'
     '    print(f"Narrative question: {outcome.get(\'narrative_prompt\') or \'(narrative did not fire)\'}")\n'
     '    print(f"resolution_family: {result.get(\'resolution_family\')!r}")\n'
     '    print(f"resolution_routing: {result.get(\'resolution_routing\')!r}")\n'
     '    print(f"synthesis.is_fallback: {synthesis.get(\'is_fallback\')}")\n'
     '    print(f"headline: {synthesis.get(\'headline\')}")\n'
     '    print(f"resolution_framing_text: {synthesis.get(\'resolution_framing_text\')}")\n'
     '\n'
     '    if args.json_out:\n'
     '        Path(args.json_out).write_text(json.dumps(outcome["raw"], indent=2), encoding="utf-8")\n'
     '        print(f"Full response written to {args.json_out}")\n'
     '\n'
     '    # The dev-preview route exists only on Preview, and is walled off on\n'
     '    # hr_diagnostic -- request the viewable link only where it can work.\n'
     '    if not is_production and args.brand == "principal_resolution":\n'
     '        try:\n'
     '            preview_resp = client.post("/api/dev/diagnostic-preview", result)\n'
     '            print(f"\\nView the completed report: {preview_resp[\'url\']}")\n'
     '        except RuntimeError as e:\n'
     '            print(f"\\n(dev preview link unavailable: {e})", file=sys.stderr)\n',
     'output summary + conditional dev link'),
]


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
        print(f'[{label}] OK')
    if 'PRODUCTION_HOST ' in t or 'PRODUCTION_HOST)' in t or '{PRODUCTION_HOST}' in t:
        print('ERROR: stale PRODUCTION_HOST reference left.', file=sys.stderr)
        sys.exit(1)
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    P.write_text(t, encoding='utf-8')
    print(f'WROTE (edited): {P}')


if __name__ == '__main__':
    main()
