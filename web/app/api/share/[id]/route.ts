import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";
import type { ShareableOutputPayload } from "@/lib/types";

const redis = Redis.fromEnv();

// ---------------------------------------------------------------------------
// Returns ShareableOutput only.
// PrivateOutput never exists in this response.
// Returns 404 when share key is not found or has expired (KV TTL handles expiry).
//
// No JSON.parse here, deliberately -- @upstash/redis's automaticDeserialization
// defaults to true (confirmed in the installed SDK source), so redis.get()
// already returns the parsed object, not the raw JSON string create/route.ts
// wrote. A prior version of this route called JSON.parse() on that
// already-parsed object anyway, which throws (object -> "[object Object]" ->
// invalid JSON) and surfaced as a permanent "Corrupt record" 500 on every
// share link ever read -- masked as a generic "not found" by the page
// component's own !res.ok check. Root-caused live, 2026-09-16: the record
// was never corrupt, only unreadable by this route's own double-parse.
// ---------------------------------------------------------------------------

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  if (!id || typeof id !== "string" || id.length === 0) {
    return NextResponse.json({ error: "Invalid share key" }, { status: 400 });
  }

  const payload = await redis.get<ShareableOutputPayload>(`share:${id}`);

  if (payload === null || payload === undefined) {
    // Not found or expired — KV TTL removes the key automatically after 30 days
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  // ShareableOutput only. PrivateOutput never exists in this response.
  return NextResponse.json(payload);
}
