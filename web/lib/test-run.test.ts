import { describe, it, expect, vi } from "vitest";

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
