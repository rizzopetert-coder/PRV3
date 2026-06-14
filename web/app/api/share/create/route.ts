import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import type { ShareableOutputPayload } from "@/lib/output-renderer";
import { invokeEngine } from "@/lib/engine-client";

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
  selectedStateIds: string[];
  intake: {
    headcount: string;
    industry: string;
    orgType: string;
    jurisdictions: string[];
    significantEvents: string[];
    principalRole: string;
  };
}

function validateRequest(body: unknown): body is CreateShareRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    Array.isArray(b.selectedStateIds) &&
    b.selectedStateIds.every((id) => typeof id === "string") &&
    typeof b.intake === "object" &&
    b.intake !== null
  );
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

  const { selectedStateIds, intake } = body;

  const engineResult = await invokeEngine({ selectedStateIds, intake });

  const shareKey = nanoid(21);
  const expiresAt = new Date(
    Date.now() + KV_TTL_SECONDS * 1000
  ).toISOString();

  // Shareable payload — PrivateOutput fields are NEVER included here.
  const shareablePayload: ShareableOutputPayload = {
    sessionId: engineResult.session_id,
    shareKey,
    expiresAt,
    outputType: engineResult.output_type,
    identifiedStates: engineResult.identified_states.map((s) => ({
      state_id: s.state_id,
      state_name: s.state_name,
      score: s.score,
    })),
    severity: {
      tier: engineResult.severity.tier,
      anchor_text: engineResult.severity.anchor_text,
    },
    shareableOutput: {
      framing_text: engineResult.shareable_output.framing_text,
      observable_indicators: engineResult.shareable_output.observable_indicators,
      resolution_framing: engineResult.shareable_output.resolution_framing,
      attribution_text: engineResult.shareable_output.attribution_text,
    },
    // synthesis: opaque string from engine — not present in Path B (no output_synthesis call)
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
