import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";
import type { ShareableOutputPayload } from "@/lib/output-renderer";

const redis = Redis.fromEnv();

// ---------------------------------------------------------------------------
// Returns ShareableOutput only.
// PrivateOutput never exists in this response.
// Returns 404 when share key is not found or has expired (KV TTL handles expiry).
// ---------------------------------------------------------------------------

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  if (!id || typeof id !== "string" || id.length === 0) {
    return NextResponse.json({ error: "Invalid share key" }, { status: 400 });
  }

  const raw = await redis.get<string>(`share:${id}`);

  if (raw === null || raw === undefined) {
    // Not found or expired — KV TTL removes the key automatically after 30 days
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  let payload: ShareableOutputPayload;
  try {
    payload = JSON.parse(raw) as ShareableOutputPayload;
  } catch {
    return NextResponse.json({ error: "Corrupt record" }, { status: 500 });
  }

  // ShareableOutput only. PrivateOutput never exists in this response.
  return NextResponse.json(payload);
}
