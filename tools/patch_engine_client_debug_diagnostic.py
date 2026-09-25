"""
TEMPORARY diagnostic: surface the RAW upstream response (status + body
text) that Project A actually receives from prv3-engine on the failing
invokeQuestionCopy() call, instead of letting it collapse into a bare
status code. Also logs (presence/length only, never the value) whether
VERCEL_AUTOMATION_BYPASS_SECRET is truthy at runtime, to distinguish
"env var not populated at request time" from "value populated but wrong
or rejected."

Never logs the actual VERCEL_AUTOMATION_BYPASS_SECRET or ENGINE_SECRET
values -- only presence/length and the upstream response body, which
contains no secrets (Vercel's own "Protected deployment" JSON, or
api/engine.py's own error body, neither of which echo back the secret).

To be removed once the underlying issue is identified, not left standing.

Usage:
    python tools/patch_engine_client_debug_diagnostic.py --dry-run
    python tools/patch_engine_client_debug_diagnostic.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/lib/engine-client.ts')

OLD = '''export async function invokeQuestionCopy(
  questionId: string,
): Promise<QuestionCopy> {
  const response = await engineFetch(resolveEnginePath("/api/question-copy"), {
    question_id: questionId,
  });

  if (!response.ok) {
    throw new Error(`Question-copy invocation failed: ${response.status}`);
  }

  return response.json() as Promise<QuestionCopy>;
}'''

NEW = '''export async function invokeQuestionCopy(
  questionId: string,
): Promise<QuestionCopy> {
  const response = await engineFetch(resolveEnginePath("/api/question-copy"), {
    question_id: questionId,
  });

  if (!response.ok) {
    // TEMPORARY diagnostic, this session -- remove once the cross-project
    // bypass issue is resolved. Never logs the actual secret values, only
    // presence/length and the raw upstream response body (which contains
    // no secrets -- either Vercel's own "Protected deployment" JSON or
    // api/engine.py's own error body).
    const bodyText = await response.text().catch(() => "(failed to read body)");
    console.error("[DIAG] question-copy failure", {
      status: response.status,
      bodyText,
      bypassSecretPresent: !!VERCEL_PROTECTION_BYPASS,
      bypassSecretLength: VERCEL_PROTECTION_BYPASS?.length ?? 0,
      engineSecretPresent: !!ENGINE_SECRET,
      engineSecretLength: ENGINE_SECRET.length,
      resolvedUrl: resolveEnginePath("/api/question-copy"),
    });
    throw new Error(`Question-copy invocation failed: ${response.status}`);
  }

  return response.json() as Promise<QuestionCopy>;
}'''


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')
    count = content.count(OLD)
    if count != 1:
        print(f'ERROR: anchor found {count} times, expected 1.', file=sys.stderr)
        sys.exit(1)

    new_content = content.replace(OLD, NEW, 1)

    if args.dry_run:
        print('DRY RUN -- anchor found, edit would apply cleanly. Nothing written.')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print('WRITE complete.')


if __name__ == '__main__':
    main()
