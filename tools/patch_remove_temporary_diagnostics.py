"""
Remove the two TEMPORARY diagnostics before merge (Pete, 2026-09-26). Both
served their investigations and must not ship to Production.

1. web/middleware.ts withDebugHeaders(): set x-debug-mw-host and
   x-debug-mw-brand on every response (raw Host header echoed back), added
   for the Edge-vs-Node host-divergence investigation. The three return
   paths are unwrapped back to their original responses; routing/brand
   logic is unchanged.
2. web/lib/engine-client.ts invokeQuestionCopy(): the "[DIAG] question-copy
   failure" console.error (added by 0f3fd67 for the cross-project bypass
   debugging) is removed, restoring the original throw exactly.

Kept deliberately: web/lib/diagnostic-completion.ts's "[DIAG] synthesis
fallback" log (permanent; surfaces parse_error).

Usage:
    python tools/patch_remove_temporary_diagnostics.py --dry-run
    python tools/patch_remove_temporary_diagnostics.py --write
"""
import argparse
import pathlib
import sys

EDITS = [
    ('web/middleware.ts',
     '// TEMPORARY diagnostic, this session -- remove in the same round as the\n'
     '// real fix, once the raw host divergence (if any) between Edge Middleware\n'
     '// and Node-runtime call sites is identified. Echoes the exact,\n'
     '// unnormalized values back as response headers on every return path, so\n'
     '// the raw string is visible directly rather than inferred from behavior.\n'
     'function withDebugHeaders(response: NextResponse, rawHost: string | null, brand: string): NextResponse {\n'
     '  response.headers.set("x-debug-mw-host", rawHost ?? "(null)");\n'
     '  response.headers.set("x-debug-mw-brand", brand);\n'
     '  return response;\n'
     '}\n'
     '\n',
     '',
     'drop withDebugHeaders'),
    ('web/middleware.ts',
     '  const rawHost = request.headers.get("host");\n',
     '',
     'drop rawHost'),
    ('web/middleware.ts',
     '      return withDebugHeaders(rewritten, rawHost, brand);\n',
     '      return rewritten;\n',
     'unwrap rewrite'),
    ('web/middleware.ts',
     '      return withDebugHeaders(new NextResponse(null, { status: 404 }), rawHost, brand);\n',
     '      return new NextResponse(null, { status: 404 });\n',
     'unwrap 404'),
    ('web/middleware.ts',
     '  return withDebugHeaders(\n'
     '    NextResponse.next({ request: { headers: requestHeaders } }),\n'
     '    rawHost,\n'
     '    brand,\n'
     '  );\n',
     '  return NextResponse.next({ request: { headers: requestHeaders } });\n',
     'unwrap next'),
    ('web/lib/engine-client.ts',
     '  if (!response.ok) {\n'
     '    // TEMPORARY diagnostic, this session -- remove once the cross-project\n'
     '    // bypass issue is resolved. Never logs the actual secret values, only\n'
     '    // presence/length and the raw upstream response body (which contains\n'
     '    // no secrets -- either Vercel\'s own "Protected deployment" JSON or\n'
     '    // api/engine.py\'s own error body).\n'
     '    const bodyText = await response.text().catch(() => "(failed to read body)");\n'
     '    console.error("[DIAG] question-copy failure", {\n'
     '      status: response.status,\n'
     '      bodyText,\n'
     '      bypassSecretPresent: !!VERCEL_PROTECTION_BYPASS,\n'
     '      bypassSecretLength: VERCEL_PROTECTION_BYPASS?.length ?? 0,\n'
     '      engineSecretPresent: !!ENGINE_SECRET,\n'
     '      engineSecretLength: ENGINE_SECRET.length,\n'
     '      resolvedUrl: resolveEnginePath("/api/question-copy"),\n'
     '    });\n'
     '    throw new Error(`Question-copy invocation failed: ${response.status}`);\n'
     '  }\n',
     '  if (!response.ok) {\n'
     '    throw new Error(`Question-copy invocation failed: ${response.status}`);\n'
     '  }\n',
     'drop question-copy DIAG'),
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
        if text.count(old) != 1:
            print(f'ERROR: {path} :: {label} anchor found {text.count(old)} times.', file=sys.stderr)
            sys.exit(1)
        edited[path] = text.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')

    for path, text in edited.items():
        for leftover in ('withDebugHeaders', 'x-debug-mw-', 'rawHost', 'question-copy failure'):
            if leftover in text:
                print(f'ERROR: {path} still contains {leftover!r}.', file=sys.stderr)
                sys.exit(1)
    if 'synthesis fallback' not in pathlib.Path('web/lib/diagnostic-completion.ts').read_text(encoding='utf-8'):
        print('ERROR: permanent [DIAG] synthesis fallback log is missing.', file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print('DRY RUN -- anchors found, no temporary diagnostic left, synthesis-fallback log intact. Nothing written.')
        return
    for path, text in edited.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')


if __name__ == '__main__':
    main()
