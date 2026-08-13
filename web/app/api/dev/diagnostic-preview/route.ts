import { NextRequest, NextResponse } from "next/server";
import {
  createDevPreview,
  isPreviewEnvironment,
  type DevDiagnosticPreviewPayload,
} from "@/lib/dev-diagnostic-preview";

// ---------------------------------------------------------------------------
// DEV / TEST ONLY -- Preview environment exclusively.
//
// Receives a completed diagnostic result from tools/diagnostic_fast_forward.py
// (Mode 1) and stores it under a short-lived, one-off key so Pete can view it
// through the existing <PrivateOutput> component without a live browser
// session of his own. Never reachable in Production: returns 404 immediately,
// before Redis is ever touched, if VERCEL_ENV is "production".
//
// Not the same tool as /dev/diagnostic-fixture (web/app/dev/diagnostic-fixture),
// intentionally: this route's whole purpose is provenance -- the payload it
// stores was computed by the REAL engine via a real driven session, which is
// exactly what makes it worth viewing. /dev/diagnostic-fixture is the
// opposite by design -- hand-picked/arbitrary values for fast rendering/
// interaction iteration, deliberately decoupled from engine correctness, no
// Redis involved since producer and consumer are the same browser tab there.
// Keep both; neither should be merged into or replace the other.
// ---------------------------------------------------------------------------

function validatePayload(body: unknown): body is DevDiagnosticPreviewPayload {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    typeof b.synthesis === "object" && b.synthesis !== null &&
    typeof b.primary_state === "object" && b.primary_state !== null &&
    Array.isArray(b.secondary_states) &&
    typeof b.severity === "string" &&
    typeof b.resolution_family === "string" &&
    typeof b.resolution_routing === "string" &&
    typeof b.intake === "object" && b.intake !== null &&
    typeof b.dimension_summary === "object" && b.dimension_summary !== null &&
    typeof b.primary_asset_domain === "string"
  );
}

export async function POST(request: NextRequest) {
  if (!isPreviewEnvironment()) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!validatePayload(body)) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const id = await createDevPreview(body);
  const origin = request.headers.get("origin") ?? "";

  return NextResponse.json({
    id,
    url: `${origin}/dev/diagnostic-preview/${id}`,
  });
}
