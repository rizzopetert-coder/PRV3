// PRV3 — Shareable Output Store
// web/lib/share-store.ts
//
// Read-side access to a share record in Upstash Redis, shared between
// web/app/api/share/[id]/route.ts (the public JSON endpoint) and
// web/app/share/[id]/page.tsx (the rendered page). Previously each of
// those two call sites had its own inline Redis read; the page's own
// version was a server-to-server fetch() of the API route via
// process.env.VERCEL_URL, which this project's ssoProtection setting
// (deploymentType: "all_except_custom_domains") blocks unconditionally --
// that internal fetch never reaches the route at all, confirmed live via
// a 302 to Vercel's own auth wall. Reading Redis directly here removes
// that self-fetch, and the SSO failure mode, entirely rather than
// routing around it.
//
// The write side (JSON.stringify() before redis.set()) stays in
// web/app/api/share/create/route.ts, unchanged -- this module is read-only,
// matching what both call sites actually need.

import { Redis } from "@upstash/redis";
import type { ShareableOutputPayload } from "@/lib/types";

const redis = Redis.fromEnv();

function shareKey(id: string): string {
  return `share:${id}`;
}

// Same defensive shape as session-store.ts's getSession() and
// dev-diagnostic-preview.ts's getDevPreview(): @upstash/redis's
// automaticDeserialization defaults to true, so redis.get() normally
// returns the already-parsed object create/route.ts wrote via
// JSON.stringify() -- not the raw string the generic type parameter
// might suggest. A prior version of web/app/api/share/[id]/route.ts
// called JSON.parse() on that already-parsed object unconditionally,
// which throws (object -> "[object Object]" -> invalid JSON) and
// produced a permanent 500 on every share link ever read, confirmed
// live 2026-09-16. Typing the read as `string | ShareableOutputPayload`
// and branching on typeof handles both the normal (already-parsed)
// case and the degenerate case where the SDK's own parseResponse()
// falls back to returning the raw string unchanged.
export async function getShareRecord(id: string): Promise<ShareableOutputPayload | null> {
  const raw = await redis.get<string | ShareableOutputPayload>(shareKey(id));
  if (raw === null || raw === undefined) return null;
  return typeof raw === "string" ? (JSON.parse(raw) as ShareableOutputPayload) : raw;
}
