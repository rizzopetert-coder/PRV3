import { NextRequest, NextResponse } from "next/server";
import { kv } from "@vercel/kv";
import { nanoid } from "nanoid";
import type { ShareableOutputPayload } from "@/lib/output-renderer";

// ---------------------------------------------------------------------------
// Payload separation contract:
//   PrivateOutput is NEVER written to KV.
//   KV stores ShareableOutput only.
// ---------------------------------------------------------------------------

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

  // TODO(S39): Retrieve the session's ShareableOutput from server-side session
  // store using body.sessionId. The session store holds engine output keyed by
  // sessionId, populated when /api/result was called.
  // Only extract the shareable_output section — never touch private_output.

  const expiresAt = new Date(
    Date.now() + KV_TTL_SECONDS * 1000
  ).toISOString();

  const shareKey = nanoid(21);

  // Shareable payload — PrivateOutput fields are NEVER included here.
  const shareablePayload: ShareableOutputPayload = {
    sessionId: body.sessionId,
    shareKey,
    expiresAt,
    outputType: "multi_state", // TODO(S39): from session store
    identifiedStates: [],      // TODO(S39): from session store shareable_output
    severity: {
      tier: "Entrenched",      // TODO(S39): from session store
      anchor_text: "COPY PENDING",
    },
    shareableOutput: {
      framing_text: "COPY PENDING",      // TODO(S39): from engine shareable_output
      observable_indicators: [],         // TODO(S39): from engine shareable_output
      resolution_framing: "COPY PENDING",
      attribution_text:
        "Identified using the PRV3 diagnostic instrument.",
    },
    // synthesis.shareableSynthesis populated separately — not included in KV record
    // synthesis.privateSynthesis is NEVER written here
  };

  // Write to KV — ShareableOutput only. PrivateOutput never written to KV.
  await kv.set(`share:${shareKey}`, JSON.stringify(shareablePayload), {
    ex: KV_TTL_SECONDS,
  });

  const origin = request.headers.get("origin") ?? "";

  return NextResponse.json({
    shareKey,
    shareUrl: `${origin}/share/${shareKey}`,
    expiresAt,
  });
}
