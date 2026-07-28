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
