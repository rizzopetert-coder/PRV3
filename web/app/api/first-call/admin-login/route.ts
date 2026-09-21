import { NextRequest, NextResponse } from "next/server";
import { timingSafeEqual } from "crypto";
import {
  FIRST_CALL_SESSION_COOKIE,
  FIRST_CALL_SESSION_MAX_AGE_SECONDS,
  deriveFirstCallSessionToken,
} from "@/lib/first-call-admin-session";

// ---------------------------------------------------------------------------
// First Call admin viewer login. Single shared secret, no accounts -- see
// web/lib/first-call-admin-session.ts. timingSafeEqual() avoids leaking the
// secret's length or a partial match via response-time differences; the
// length check before it is required, not optional -- timingSafeEqual()
// throws on unequal-length inputs rather than returning false.
// ---------------------------------------------------------------------------

function validateRequest(body: unknown): body is { password: string } {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return typeof b.password === "string";
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!validateRequest(body)) {
    return NextResponse.json({ error: "Incorrect password" }, { status: 401 });
  }

  const adminSecret = process.env.FIRST_CALL_ADMIN_SECRET ?? "";
  const providedBuf = Buffer.from(body.password);
  const expectedBuf = Buffer.from(adminSecret);

  // adminSecret.length > 0 guards against an unset secret making an empty
  // submitted password "match" (two zero-length buffers are trivially
  // timingSafeEqual).
  const isMatch =
    adminSecret.length > 0 &&
    providedBuf.length === expectedBuf.length &&
    timingSafeEqual(providedBuf, expectedBuf);

  if (!isMatch) {
    return NextResponse.json({ error: "Incorrect password" }, { status: 401 });
  }

  const response = NextResponse.json({ success: true });
  response.cookies.set(FIRST_CALL_SESSION_COOKIE, deriveFirstCallSessionToken(adminSecret), {
    httpOnly: true,
    secure: true,
    sameSite: "lax",
    path: "/first-call",
    maxAge: FIRST_CALL_SESSION_MAX_AGE_SECONDS,
  });
  return response;
}
