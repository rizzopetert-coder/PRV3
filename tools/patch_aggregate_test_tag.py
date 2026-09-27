"""
Test-run tag on diagnostic-aggregate records (Pete, 2026-09-26/27), plus the
MOB fold-in for the aggregate cleanup it follows.

Why: Preview and Production write to the SAME Upstash database (confirmed
2026-09-26 -- Pete's LRANGE showed this session's Preview test completions
in the Production list). AnonymizedCompletion carried nothing marking a test
run, so test data was indistinguishable from real completions except by
timestamp and the session driver's fixed intake fingerprint. Pete cleared
the list (DEL diagnostic-aggregate, LLEN 0 confirmed) and chose tag-not-skip.

Design (Pete-approved, no Gemini gate per Pete):
  - Decided once at session start, stored on the session: test when
    VERCEL_ENV !== "production" (every Preview session -- Preview shares the
    Production DB), or when a Production request carries
    `x-prv3-test-run: 1` (deliberate Production smoke tests). Spoofing the
    header only removes the sender's own record from analytics.
  - AnonymizedCompletion gains `is_test: boolean`, always present (false for
    real users). DiagnosticSession gets optional `is_test?` -- sessions
    already in flight in Redis at deploy time lack it and complete as
    is_test=false, and hand-built test sessions need no edits.
  - createSession(intake, brand, isTest=false): default keeps all 9
    existing call sites unchanged, same convention as `brand`.
  - No reader of diagnostic-aggregate exists in code today (write-only),
    and the list is empty, so every record from here on has the new shape.
  - tools/diagnostic_fast_forward.py sends the header on every request.

Usage:
    python tools/patch_aggregate_test_tag.py --dry-run
    python tools/patch_aggregate_test_tag.py --write
"""
import argparse
import pathlib
import sys

NEW_FILES = {
    pathlib.Path('web/lib/test-run.ts'): '''// Whether a diagnostic session is a test run -- decided once at session
// start and carried through to the anonymized aggregate record, so test
// completions can be excluded when diagnostic-aggregate is analyzed.
//
// Preview deployments write to the same Upstash database as Production
// (confirmed 2026-09-26), so every non-Production session is a test run by
// definition. In Production, a deliberate smoke test opts in with the
// x-prv3-test-run header. The header is an honest-client flag: spoofing it
// only removes the sender's own record from analytics.
export const TEST_RUN_HEADER = "x-prv3-test-run";

export function isTestRun(
  headers: Headers,
  vercelEnv: string | undefined = process.env.VERCEL_ENV,
): boolean {
  if (vercelEnv !== "production") return true;
  return headers.get(TEST_RUN_HEADER) === "1";
}
''',
    pathlib.Path('web/lib/test-run.test.ts'): '''import { describe, it, expect, vi } from "vitest";

// Test-run tagging (2026-09-26). isTestRun() decides; completeSession()
// must carry the decision into the anonymized aggregate record.

const rpushed: string[] = [];

vi.mock("@upstash/redis", () => {
  class FakeRedis {
    static fromEnv() {
      return new FakeRedis();
    }
    async get() {
      return null;
    }
    async set() {
      return "OK";
    }
    async del() {
      return 1;
    }
    async rpush(_key: string, value: string) {
      rpushed.push(value);
      return rpushed.length;
    }
  }
  return { Redis: FakeRedis };
});

const { isTestRun, TEST_RUN_HEADER } = await import("@/lib/test-run");
const { createSession, completeSession } = await import("@/lib/session-store");

const FAKE_INTAKE = { industry: "Technology", organization_size: 175 } as Parameters<typeof createSession>[0];

describe("isTestRun", () => {
  it("tags every non-production session (Preview shares the Production DB)", () => {
    expect(isTestRun(new Headers(), "preview")).toBe(true);
    expect(isTestRun(new Headers(), undefined)).toBe(true);
  });

  it("tags a production session only when the test-run header is 1", () => {
    expect(isTestRun(new Headers(), "production")).toBe(false);
    expect(isTestRun(new Headers({ [TEST_RUN_HEADER]: "1" }), "production")).toBe(true);
    expect(isTestRun(new Headers({ [TEST_RUN_HEADER]: "true" }), "production")).toBe(false);
  });
});

describe("completeSession is_test", () => {
  it("writes is_test: true for a session created as a test run", async () => {
    rpushed.length = 0;
    const session = await createSession(FAKE_INTAKE, "hr_diagnostic", true);
    await completeSession(session, [{ id: "built_to_fail", name: "Built to Fail", weight: 1 }]);
    expect(JSON.parse(rpushed[0]).is_test).toBe(true);
  });

  it("writes is_test: false for a real session (default)", async () => {
    rpushed.length = 0;
    const session = await createSession(FAKE_INTAKE);
    await completeSession(session, []);
    expect(JSON.parse(rpushed[0]).is_test).toBe(false);
  });

  it("writes is_test: false for an in-flight session that predates the field", async () => {
    rpushed.length = 0;
    const session = await createSession(FAKE_INTAKE);
    delete session.is_test;
    await completeSession(session, []);
    expect(JSON.parse(rpushed[0]).is_test).toBe(false);
  });
});
''',
}

EDITS = [
    ('web/lib/session-store.ts',
     '  brand: Brand;\n  intake: PrivateIntakeEcho;\n',
     '  brand: Brand;\n'
     '  // Test run (web/lib/test-run.ts), decided once at createSession() and\n'
     '  // carried into the anonymized aggregate record. Optional: sessions\n'
     '  // already in Redis before this field existed complete as false.\n'
     '  is_test?: boolean;\n'
     '  intake: PrivateIntakeEcho;\n',
     'DiagnosticSession.is_test'),
    ('web/lib/session-store.ts',
     '  final_state_rankings: Array<{ id: string; name: string; weight: number }>;\n'
     '  completed_at: string; // ISO 8601\n'
     '}\n',
     '  final_state_rankings: Array<{ id: string; name: string; weight: number }>;\n'
     '  completed_at: string; // ISO 8601\n'
     '  // true for Preview sessions and flagged Production smoke tests --\n'
     '  // exclude these when analyzing diagnostic-aggregate. Always present.\n'
     '  is_test: boolean;\n'
     '}\n',
     'AnonymizedCompletion.is_test'),
    ('web/lib/session-store.ts',
     '  brand: Brand = "principal_resolution",\n): Promise<DiagnosticSession> {\n',
     '  brand: Brand = "principal_resolution",\n'
     '  // Same default-not-required convention as `brand`: the real caller\n'
     '  // (session/start/route.ts) passes isTestRun(request.headers).\n'
     '  isTest: boolean = false,\n'
     '): Promise<DiagnosticSession> {\n',
     'createSession param'),
    ('web/lib/session-store.ts',
     '    session_id: nanoid(),\n    brand,\n    intake,\n',
     '    session_id: nanoid(),\n    brand,\n    is_test: isTest,\n    intake,\n',
     'createSession sets is_test'),
    ('web/lib/session-store.ts',
     '    completed_at: new Date().toISOString(),\n  };\n\n  await redis.rpush(AGGREGATE_KEY',
     '    completed_at: new Date().toISOString(),\n'
     '    is_test: session.is_test === true,\n'
     '  };\n\n  await redis.rpush(AGGREGATE_KEY',
     'completeSession writes is_test'),
    ('web/app/api/diagnostic/session/start/route.ts',
     'import { resolveBrandForRequest } from "@/lib/brand";\n',
     'import { resolveBrandForRequest } from "@/lib/brand";\n'
     'import { isTestRun } from "@/lib/test-run";\n',
     'import isTestRun'),
    ('web/app/api/diagnostic/session/start/route.ts',
     '  const session = await createSession(body, brand);\n',
     '  const session = await createSession(body, brand, isTestRun(request.headers));\n',
     'pass isTestRun'),
    ('tools/diagnostic_fast_forward.py',
     '        headers = {"Content-Type": "application/json", "Origin": self.base_url}\n',
     '        # x-prv3-test-run: tags this session\'s aggregate record as a test\n'
     '        # run (web/lib/test-run.ts) -- required for any Production run;\n'
     '        # Preview sessions are tagged regardless.\n'
     '        headers = {"Content-Type": "application/json", "Origin": self.base_url, "x-prv3-test-run": "1"}\n',
     'driver sends header'),
]

MOB = pathlib.Path('tools/_mob.txt')
MOB_BULLET_PREFIX = '  - Two Production test records to delete from Redis list `diagnostic-aggregate`'
MOB_BULLET_NEW = ('  - CLOSED 2026-09-26/27 -- `diagnostic-aggregate` cleared entirely by Pete (`DEL`, `LLEN` 0 '
                  'confirmed), clean slate for Production. Answered the open question: Preview and Production '
                  'DO share one Upstash database -- the list held this session\'s ~20 Preview test completions '
                  'alongside the 2 Production ones, plus older likely-test entries (2026-09-24, August, '
                  '2026-09-13) that Pete chose to clear too. Records now carry `is_test` (Preview sessions '
                  'always, Production only with `x-prv3-test-run: 1`) -- see `web/lib/test-run.ts`. Exclude '
                  '`is_test: true` when analyzing the list. A separate Upstash database for Preview remains an '
                  'option, not pursued.')
MOB_ADDENDUM = '''

**Addendum (2026-09-27, same session, post-closeout):** Production aggregate cleanup and test-run tagging. Pete cleared `diagnostic-aggregate` entirely (was 38 records: 20 of this session's Preview tests, 2 Production smoke tests, 16 older likely-test entries), `LLEN` 0 confirmed. This confirmed Preview writes to the Production Upstash database. Records now carry `is_test` (`web/lib/test-run.ts`, `completeSession()`), set for every non-Production session and for Production requests with `x-prv3-test-run: 1`, which `tools/diagnostic_fast_forward.py` now sends. 13b's "delete two test records" item closed in place. MOB version unchanged (v4.326).'''


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    for p in NEW_FILES:
        if p.exists():
            print(f'ERROR: {p} already exists.', file=sys.stderr)
            sys.exit(1)

    edited = {}
    for rel, old, new, label in EDITS:
        path = pathlib.Path(rel)
        text = edited.get(path, path.read_text(encoding='utf-8'))
        if text.count(old) != 1:
            print(f'ERROR: {path} :: {label} anchor found {text.count(old)} times.', file=sys.stderr)
            sys.exit(1)
        edited[path] = text.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')

    mob = MOB.read_bytes().decode('utf-8')
    if mob.count(MOB_BULLET_PREFIX) != 1:
        print('ERROR: 13b test-records bullet not found exactly once.', file=sys.stderr)
        sys.exit(1)
    start = mob.index(MOB_BULLET_PREFIX)
    end = mob.index('\r\n', start)
    mob = mob[:start] + MOB_BULLET_NEW + mob[end:]
    print('[MOB :: 13b bullet closed] OK')
    if not mob.rstrip().endswith('MOB v4.326.'):
        print('ERROR: MOB does not end with the v4.326 closeout line.', file=sys.stderr)
        sys.exit(1)
    mob = mob.rstrip('\r\n') + MOB_ADDENDUM.replace('\n', '\r\n') + '\r\n'
    print('[MOB :: Section 16 addendum] OK')

    if args.dry_run:
        print('DRY RUN -- all anchors found. Nothing written.')
        return
    for p, content in NEW_FILES.items():
        p.write_text(content, encoding='utf-8')
        print(f'WROTE: {p}')
    for p, text in edited.items():
        p.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {p}')
    MOB.write_text(mob, encoding='utf-8', newline='')
    print(f'WROTE: {MOB}')


if __name__ == '__main__':
    main()
