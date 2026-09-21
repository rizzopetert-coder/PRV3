import { createHash } from "crypto";

// Shared between web/app/api/first-call/admin-login/route.ts (sets the
// cookie on a correct password) and web/app/first-call/admin/page.tsx
// (verifies it on every load) -- kept as one module rather than this
// project's usual duplicated-inline-logic preference (see
// web/app/api/share/create/route.ts's toOrgSize() comment) because a
// security token derivation drifting between its write side and read
// side would silently break or weaken auth, unlike a data-mapping helper.

export const FIRST_CALL_SESSION_COOKIE = "first_call_admin_session";
export const FIRST_CALL_SESSION_MAX_AGE_SECONDS = 60 * 60 * 4; // 4 hours

// Not a security boundary on its own -- anyone who already knows
// FIRST_CALL_ADMIN_SECRET could compute this same value. Its only job is
// to keep the raw secret itself out of the browser's cookie jar. The real
// gate is the timingSafeEqual() password check in admin-login/route.ts.
export function deriveFirstCallSessionToken(secret: string): string {
  return createHash("sha256").update(secret).digest("hex");
}
