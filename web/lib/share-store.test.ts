import { describe, it, expect, vi, beforeEach } from "vitest";

// ---------------------------------------------------------------------------
// getShareRecord read-time projection: shares written before 2026-09-30 still
// hold friction_tax_estimate (with dollars) and legal_tail_risk_band in Redis
// until their 30-day TTL ends. Every reader goes through getShareRecord, so it
// must return them without those two fields.
// ---------------------------------------------------------------------------

const store = new Map<string, unknown>();

vi.mock("@upstash/redis", () => {
  class FakeRedis {
    static fromEnv() {
      return new FakeRedis();
    }
    async get(key: string) {
      return store.get(key) ?? null;
    }
  }
  return { Redis: FakeRedis };
});

const { getShareRecord } = await import("./share-store");

const LEGACY = {
  synthesis: { framing_text: "f", observable_indicators: [], resolution_framing_text: "r", headline: "h", synthesis_confidence: 0.9, is_fallback: false },
  primary_state: { id: "built_to_fail", name: "Built to Fail", weight: 1 },
  secondary_states: [],
  severity: "Entrenched",
  resolution_family: "Structural",
  friction_tax_estimate: { low: 123456, high: 172838, currency: "USD", driving_factors: [] },
  legal_tail_risk_band: "Moderate",
  intake: { organization_size: 150, industry: "Technology" },
  share_id: "abc", expires_at: "2026-10-30T00:00:00.000Z", created_at: "2026-09-30T00:00:00.000Z",
};

describe("getShareRecord", () => {
  beforeEach(() => store.clear());

  it("returns a legacy record (already parsed) without the two retired fields", async () => {
    store.set("share:abc", LEGACY);
    const rec = await getShareRecord("abc");
    expect(rec).not.toBeNull();
    expect(rec).not.toHaveProperty("friction_tax_estimate");
    expect(rec).not.toHaveProperty("legal_tail_risk_band");
    expect(rec?.share_id).toBe("abc");
    expect(rec?.severity).toBe("Entrenched");
  });

  it("returns a legacy record stored as a raw string without the two retired fields", async () => {
    store.set("share:abc", JSON.stringify(LEGACY));
    const rec = await getShareRecord("abc");
    expect(rec).not.toHaveProperty("friction_tax_estimate");
    expect(rec).not.toHaveProperty("legal_tail_risk_band");
    expect(rec?.primary_state.id).toBe("built_to_fail");
  });

  it("returns null for a missing record", async () => {
    expect(await getShareRecord("nope")).toBeNull();
  });
});
