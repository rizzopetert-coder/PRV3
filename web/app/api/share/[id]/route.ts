import { NextRequest, NextResponse } from "next/server";
import { getShareRecord } from "@/lib/share-store";

// ---------------------------------------------------------------------------
// Returns ShareableOutput only.
// PrivateOutput never exists in this response.
// Returns 404 when share key is not found or has expired (KV TTL handles expiry).
//
// Read logic (the automaticDeserialization-aware Redis get, root-caused live
// 2026-09-16 after a prior double-JSON.parse bug here produced a permanent
// "Corrupt record" 500 on every share link ever read) now lives in
// web/lib/share-store.ts, shared with web/app/share/[id]/page.tsx -- that
// page previously round-tripped through this exact route via
// resolveBaseUrl()/process.env.VERCEL_URL, which this project's
// ssoProtection setting blocks unconditionally (confirmed live: a 302 to
// Vercel's own auth wall). The page now reads Redis directly instead.
//
// This route itself has no other caller left after that change (confirmed
// by search -- ShareButton.tsx only ever POSTs /api/share/create) but is
// kept as a standalone public JSON endpoint for the share data, not removed
// speculatively.
// ---------------------------------------------------------------------------

export async function GET(
  _request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  if (!id || typeof id !== "string" || id.length === 0) {
    return NextResponse.json({ error: "Invalid share key" }, { status: 400 });
  }

  const payload = await getShareRecord(id);

  if (payload === null) {
    // Not found or expired — KV TTL removes the key automatically after 30 days
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  // ShareableOutput only. PrivateOutput never exists in this response.
  return NextResponse.json(payload);
}
