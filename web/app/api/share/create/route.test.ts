import { describe, it, expect, vi, beforeEach } from "vitest";

// ---------------------------------------------------------------------------
// Route-level test, share/create: the stored share payload must carry no
// friction dollars and no legal band. Friction dollars are hidden in the
// display (FRICTION_DOLLARS_VISIBLE) and the share page serializes the whole
// stored payload to the browser, so the stored copy is the exposure.
//
// Mocks @upstash/redis (captures the write) and @/lib/engine-client (the
// engine call). Everything else in the route runs for real.
// ---------------------------------------------------------------------------

const written = new Map<string, string>();

vi.mock("@upstash/redis", () => {
  class FakeRedis {
    static fromEnv() {
      return new FakeRedis();
    }
    async set(key: string, value: string) {
      written.set(key, value);
      return "OK";
    }
  }
  return { Redis: FakeRedis };
});

const mockInvokeEngine = vi.fn();
vi.mock("@/lib/engine-client", () => ({
  invokeEngine: (...args: unknown[]) => mockInvokeEngine(...args),
}));

const { POST } = await import("./route");

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
      low: 123456, high: 172838, currency: "USD",
      driving_factors: [{ label: "Payroll baseline", text: "Estimated annual payroll: $1,000,000." }],
    },
    legal_tail_risk_exposure: { band: "Moderate", low: 1, high: 2 },
  },
  intake: { org_size: 150, industry: "Technology", org_type: "Founder-led", principal_role: "CEO", jurisdictions: ["California"] },
};

function fakeRequest(body: unknown) {
  return { json: async () => body, headers: new Headers() } as unknown as Parameters<typeof POST>[0];
}

describe("POST /api/share/create stored payload", () => {
  beforeEach(() => {
    written.clear();
    mockInvokeEngine.mockReset();
    mockInvokeEngine.mockResolvedValue(ENGINE_RESULT);
  });

  it("stores neither friction_tax_estimate nor legal_tail_risk_band, and no low/high/driving_factors anywhere", async () => {
    const res = await POST(fakeRequest({
      selectedStateIds: ["built_to_fail"],
      intake: { headcount: 150, industry: "Technology", orgType: "Founder-led", jurisdictions: ["California"], significantEvents: ["none"], principalRole: "CEO" },
    }));
    expect(res.status).toBe(200);
    expect(written.size).toBe(1);
    const stored = [...written.values()][0];
    const payload = JSON.parse(stored);
    expect(payload).not.toHaveProperty("friction_tax_estimate");
    expect(payload).not.toHaveProperty("legal_tail_risk_band");
    expect(stored).not.toMatch(/"low"|"high"|"driving_factors"/);
    expect(stored).not.toContain("123456");
  });
});
