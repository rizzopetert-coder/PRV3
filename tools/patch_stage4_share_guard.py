"""
Friction tax rebuild, Stage 4, R6: the share-payload name guard.

web/lib/share-store.ts: the read-time strip now removes all four names
(friction_tax_estimate, legal_tail_risk_band, friction_receipts, channels) instead
of two, so a record carrying any of them at read can never reach a share reader.
Adds web/lib/share-payload-guard.test.ts, which fails if a share payload at write
(POST /api/share/create) or at read (getShareRecord) carries any of the four, at any
depth.

Usage: python tools/patch_stage4_share_guard.py --dry-run | --write
"""
import sys
from pathlib import Path

W = Path(__file__).resolve().parents[1] / "web"
STORE = W / "lib/share-store.ts"
TEST = W / "lib/share-payload-guard.test.ts"

OLD = """type LegacyShareRecord = ShareableOutputPayload & {
  friction_tax_estimate?: unknown;
  legal_tail_risk_band?: unknown;
};

function stripRetiredFields(record: LegacyShareRecord): ShareableOutputPayload {
  const { friction_tax_estimate: _friction, legal_tail_risk_band: _legal, ...rest } = record;
  return rest;
}
"""
NEW = """//
// Stage 4 (R6, friction tax rebuild): the strip also names friction_receipts
// and channels, the two fields the rebuild adds to the private output. They are
// never written to a share (the write is a whitelist), this makes sure a record
// that somehow carried one still cannot reach a reader.
type LegacyShareRecord = ShareableOutputPayload & {
  friction_tax_estimate?: unknown;
  legal_tail_risk_band?: unknown;
  friction_receipts?: unknown;
  channels?: unknown;
};

function stripRetiredFields(record: LegacyShareRecord): ShareableOutputPayload {
  const {
    friction_tax_estimate: _friction,
    legal_tail_risk_band: _legal,
    friction_receipts: _receipts,
    channels: _channels,
    ...rest
  } = record;
  return rest;
}
"""

TEST_SRC = """import { describe, it, expect, vi, beforeEach } from "vitest";

// ---------------------------------------------------------------------------
// R6 (friction tax rebuild): a share payload must never carry friction_tax_estimate,
// legal_tail_risk_band, friction_receipts or channels, at write (POST
// /api/share/create) or at read (getShareRecord). The guard scans the whole payload
// at any depth, so a nested channels list (the friction ledger rows carry one) fails
// it too.
// ---------------------------------------------------------------------------

const store = new Map<string, string>();

vi.mock("@upstash/redis", () => {
  class FakeRedis {
    static fromEnv() {
      return new FakeRedis();
    }
    async set(key: string, value: string) {
      store.set(key, value);
      return "OK";
    }
    async get(key: string) {
      return store.get(key) ?? null;
    }
  }
  return { Redis: FakeRedis };
});

const mockInvokeEngine = vi.fn();
vi.mock("@/lib/engine-client", () => ({
  invokeEngine: (...args: unknown[]) => mockInvokeEngine(...args),
}));

const { POST } = await import("@/app/api/share/create/route");
const { getShareRecord } = await import("./share-store");

const FORBIDDEN = ["friction_tax_estimate", "legal_tail_risk_band", "friction_receipts", "channels"];

function forbiddenKeysIn(value: unknown, path = "$"): string[] {
  if (Array.isArray(value)) return value.flatMap((v, i) => forbiddenKeysIn(v, `${path}[${i}]`));
  if (value && typeof value === "object") {
    return Object.entries(value as Record<string, unknown>).flatMap(([k, v]) => [
      ...(FORBIDDEN.includes(k) ? [`${path}.${k}`] : []),
      ...forbiddenKeysIn(v, `${path}.${k}`),
    ]);
  }
  return [];
}

const ENGINE_RESULT = {
  identified_states: [
    { state_id: "built_to_fail", state_name: "Built to Fail", score: 0.8, descriptive_prose: "x" },
  ],
  synthesis: {
    framing_text: "f", observable_indicators: ["i"], resolution_framing_text: "r",
    headline: "h", synthesis_confidence: 0.9, is_fallback: false,
  },
  severity: { tier: "Entrenched" },
  private_output: {
    resolution_routing: "Structural",
    friction_tax_estimate: {
      currency: "USD",
      typical_baseline: {
        total: { amount: 63923.24, percent_of_payroll: 12.6759 },
        channels: [{ channel: "engagement", amount: 35401.02, percent_of_payroll: 7.02, inputs: [] }],
      },
      excess: null,
    },
    friction_receipts: [{ category: "Total", rationale: "Together, what organizations like yours typically lose is 12.68% of payroll." }],
    friction_tax_ledger: [{ state_id: "built_to_fail", state_name: "Built to Fail", risk_label: "Entrenched", channels: ["engagement"], top_contributing_answers: [] }],
    legal_tail_risk_exposure: { band: "Moderate", low: 1, high: 2 },
  },
  intake: { org_size: 150, industry: "Technology", org_type: "Founder-led", principal_role: "CEO", jurisdictions: ["California"] },
};

function fakeRequest(body: unknown) {
  return { json: async () => body, headers: new Headers() } as unknown as Parameters<typeof POST>[0];
}

describe("the guard itself", () => {
  it("finds a forbidden name at any depth", () => {
    expect(forbiddenKeysIn({ a: [{ b: { channels: [] } }] })).toEqual(["$.a[0].b.channels"]);
    expect(forbiddenKeysIn({ friction_receipts: [], x: { legal_tail_risk_band: 1 } })).toHaveLength(2);
    expect(forbiddenKeysIn({ fine: { engagement: 1 } })).toEqual([]);
  });
});

describe("share payload at write (POST /api/share/create)", () => {
  beforeEach(() => {
    store.clear();
    mockInvokeEngine.mockReset();
    mockInvokeEngine.mockResolvedValue(ENGINE_RESULT);
  });

  it("stores none of friction_tax_estimate, legal_tail_risk_band, friction_receipts or channels, at any depth", async () => {
    const res = await POST(fakeRequest({
      selectedStateIds: ["built_to_fail"],
      intake: { headcount: 150, industry: "Technology", orgType: "Founder-led", jurisdictions: ["California"], significantEvents: ["none"], principalRole: "CEO" },
    }));
    expect(res.status).toBe(200);
    expect(store.size).toBe(1);
    const stored = [...store.values()][0];
    expect(forbiddenKeysIn(JSON.parse(stored))).toEqual([]);
    expect(stored).not.toContain("63923");
    expect(stored).not.toContain("typically lose");
  });
});

describe("share payload at read (getShareRecord)", () => {
  beforeEach(() => store.clear());

  const HOSTILE = {
    synthesis: { framing_text: "f", observable_indicators: [], resolution_framing_text: "r", headline: "h", synthesis_confidence: 0.9, is_fallback: false },
    primary_state: { id: "built_to_fail", name: "Built to Fail", weight: 1 },
    secondary_states: [],
    severity: "Entrenched",
    resolution_family: "Structural",
    friction_tax_estimate: ENGINE_RESULT.private_output.friction_tax_estimate,
    legal_tail_risk_band: "Moderate",
    friction_receipts: ENGINE_RESULT.private_output.friction_receipts,
    channels: ["engagement"],
    intake: { organization_size: 150, industry: "Technology" },
    share_id: "abc", expires_at: "2026-10-30T00:00:00.000Z", created_at: "2026-10-01T00:00:00.000Z",
  };

  it("returns a record without any of the four names, stored as a raw string", async () => {
    store.set("share:abc", JSON.stringify(HOSTILE));
    const rec = await getShareRecord("abc");
    expect(rec).not.toBeNull();
    expect(forbiddenKeysIn(rec)).toEqual([]);
    expect(rec?.share_id).toBe("abc");
    expect(rec?.severity).toBe("Entrenched");
  });
});
"""


def main():
    write = "--write" in sys.argv
    raw = STORE.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    assert t.count(OLD) == 1, t.count(OLD)
    t = t.replace(OLD, NEW)
    print("share-store.ts: 1 edit ok", "CRLF" if crlf else "LF")
    print("share-payload-guard.test.ts:", "exists, would not overwrite" if TEST.exists() else "new")
    if write:
        STORE.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
        if not TEST.exists():
            TEST.write_bytes(TEST_SRC.encode("utf-8"))
        print("WROTE")
    else:
        print("DRY RUN")


main()
