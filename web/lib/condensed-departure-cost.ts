// The condensed report's cost of one departure, a single value (friction tax
// rebuild, Stage 5): the industry wage (OEWS May 2025) x 0.333, computed by the
// engine as condensed_departure_cost. Replaces the 0.50 to 0.75 range
// (condensed_financial_range). Shown only behind FRICTION_DOLLARS_VISIBLE.
//
// The web and engine deploy separately from one push, so every read of the figure
// tolerates the new single value, the old { low, high } range (the engine of the
// previous deploy) and a missing value. The old range is a different basis, so it
// is read as no figure rather than converted. Nothing here throws.

export interface DepartureCost {
  amount: number | null;
  currency: "USD";
}

function finiteAmount(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

// The engine's /api/condensed-complete result, in either shape.
export function departureCostFromEngine(result: unknown): DepartureCost {
  const r = result && typeof result === "object" ? (result as Record<string, unknown>) : {};
  const cost = r.condensed_departure_cost;
  const amount = cost && typeof cost === "object" ? finiteAmount((cost as Record<string, unknown>).amount) : null;
  return { amount, currency: "USD" };
}

// The CondensedOutputPayload the component renders, in the new shape or the old
// one (financial_range, from a payload built by the previous deploy's route).
export function departureCostAmount(payload: unknown): number | null {
  const p = payload && typeof payload === "object" ? (payload as Record<string, unknown>) : {};
  const cost = p.departure_cost;
  return cost && typeof cost === "object" ? finiteAmount((cost as Record<string, unknown>).amount) : null;
}
