import { NextRequest, NextResponse } from "next/server";
import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";

// ---------------------------------------------------------------------------
// First Call Crisis Intake -- Redis-only build, this session. Email
// notification is an explicit, separate fast-follow: Resend's
// principalresolution.com domain is added but still Pending DNS
// verification as of this session, so no email call is made here. Once it
// clears, add an independent fetch() POST to https://api.resend.com/emails
// (RESEND_API_KEY, from/to pete@principalresolution.com) directly below the
// Redis write, in its own try/catch -- it must never gate the Redis write,
// and the Redis write must never gate on it. Durability shouldn't depend on
// email deliverability. See tools/_mob.txt for the tracked decision.
// ---------------------------------------------------------------------------

const redis = Redis.fromEnv();

const VALID_CRISIS_CATEGORIES = ["safety", "financial", "personnel"] as const;

interface FirstCallRequest {
  organizationName: string;
  contactName: string;
  contactEmail: string;
  contactPhone?: string;
  crisisCategories: string[];
  description?: string;
}

function validateRequest(body: unknown): body is FirstCallRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    typeof b.organizationName === "string" && b.organizationName.trim().length > 0 &&
    typeof b.contactName === "string" && b.contactName.trim().length > 0 &&
    typeof b.contactEmail === "string" && b.contactEmail.trim().length > 0 &&
    (b.contactPhone === undefined || typeof b.contactPhone === "string") &&
    Array.isArray(b.crisisCategories) &&
    b.crisisCategories.length > 0 &&
    b.crisisCategories.every(
      (c) => typeof c === "string" && (VALID_CRISIS_CATEGORIES as readonly string[]).includes(c)
    ) &&
    (b.description === undefined || typeof b.description === "string")
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
    return NextResponse.json(
      { error: "Valid organization, contact, and at least one crisis category required" },
      { status: 400 }
    );
  }

  const { organizationName, contactName, contactEmail, contactPhone, crisisCategories, description } = body;

  const intakeId = nanoid(21);
  const record = {
    id: intakeId,
    organization_name: organizationName,
    contact_name: contactName,
    contact_email: contactEmail,
    contact_phone: contactPhone ?? null,
    crisis_categories: crisisCategories,
    description: description ?? null,
    submitted_at: new Date().toISOString(),
  };

  // Durable record -- no ex/TTL. This is a permanent record, not an expiring
  // share link (contrast web/app/api/share/create/route.ts's KV_TTL_SECONDS).
  await redis.set(`crisis-intake:${intakeId}`, JSON.stringify(record));

  // FAST-FOLLOW (not built yet): independent, non-blocking Resend fetch()
  // call goes here once principalresolution.com verifies -- see comment above.

  return NextResponse.json({ success: true });
}
