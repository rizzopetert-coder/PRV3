import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import type { ShareableOutputPayload } from "@/lib/output-renderer";

// ---------------------------------------------------------------------------
// Payload separation contract:
//   PrivateOutput is NEVER written to KV.
//   KV stores ShareableOutput only.
//
// Engine call is independent of /api/result — engine runs twice if user shares.
// That is correct and intentional. Option D baseline preserved:
//   no KV write occurs until the user explicitly requests a share link.
// ---------------------------------------------------------------------------

const redis = Redis.fromEnv();
const KV_TTL_SECONDS = 30 * 24 * 60 * 60; // 30 days

interface CreateShareRequest {
  sessionId: string;
}

function validateRequest(body: unknown): body is CreateShareRequest {
  if (typeof body !== "object" || body === null) return false;
  return typeof (body as Record<string, unknown>).sessionId === "string";
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!validateRequest(body)) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  // TODO(S40): Call Python engine afresh with session payload.
  // This is an independent engine call — does not depend on /api/result having run.
  // Extract shareable_output section only. Never touch private_output.
  // synthesis.shareable_synthesis arrives from engine as an opaque string.

  const shareKey = nanoid(21);
  const expiresAt = new Date(
    Date.now() + KV_TTL_SECONDS * 1000
  ).toISOString();

  // Shareable payload — PrivateOutput fields are NEVER included here.
  const shareablePayload: ShareableOutputPayload = {
    sessionId: body.sessionId,
    shareKey,
    expiresAt,
    outputType: "multi_state",   // TODO(S40): from engine output
    identifiedStates: [],        // TODO(S40): from engine shareable_output
    severity: {
      tier: "Entrenched",        // TODO(S40): from engine severity_result
      anchor_text: "COPY PENDING",
    },
    shareableOutput: {
      framing_text: "COPY PENDING",      // TODO(S40): from engine shareable_output
      observable_indicators: [],         // TODO(S40): from engine shareable_output
      resolution_framing: "COPY PENDING",
      attribution_text:
        "Identified using the PRV3 diagnostic instrument.",
    },
    // synthesis.shareableSynthesis from engine (S40) — opaque string, never generated here
    // synthesis.privateSynthesis is NEVER written here
  };

  // Write to KV — ShareableOutput only. PrivateOutput never written to KV.
  await redis.set(`share:${shareKey}`, JSON.stringify(shareablePayload), {
    ex: KV_TTL_SECONDS,
  });

  const origin = request.headers.get("origin") ?? "";

  return NextResponse.json({
    shareKey,
    shareUrl: `${origin}/share/${shareKey}`,
    expiresAt,
  });
}
