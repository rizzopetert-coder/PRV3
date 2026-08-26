import { NextRequest, NextResponse } from "next/server";

// ---------------------------------------------------------------------------
// Real Transaction Path — Phase 1 (e-signature only). Architecture proposed,
// Gemini-reviewed, and finalized this session -- see
// prompts/real-transaction-path-phase1-gemini-request.md for the full
// record, including why the webhook (/api/engage/webhook) is deferred to
// Phase 2 rather than built alongside this route.
//
// Calls Dropbox Sign's hosted (non-embedded) signature_request/
// send_with_template endpoint -- confirmed directly against Dropbox Sign's
// live API reference this session: JSON request body (NOT multipart/
// form-data -- that's only required by the plain /send endpoint's raw file
// uploads), template_ids as an array, signers as an array of
// {role, name, email_address} objects. Dropbox Sign emails the signer
// directly; this route never receives or returns a signing_url. No
// webhook exists yet, so Dropbox Sign's own dashboard/native notifications
// are the only way to check completion status until Phase 2.
// ---------------------------------------------------------------------------

const DROPBOX_SIGN_SEND_WITH_TEMPLATE_URL =
  "https://api.hellosign.com/v3/signature_request/send_with_template";

interface EngageRequest {
  name: string;
  email: string;
}

function validateRequest(body: unknown): body is EngageRequest {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    typeof b.name === "string" && b.name.trim().length > 0 &&
    typeof b.email === "string" && b.email.trim().length > 0
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
    return NextResponse.json({ error: "Valid name and email required" }, { status: 400 });
  }

  const { name, email } = body;
  const apiKey = process.env.DROPBOX_SIGN_API_KEY ?? "";
  const templateId = process.env.DROPBOX_SIGN_TEMPLATE_ID ?? "";

  // Same VERCEL_ENV convention as isPreviewEnvironment()
  // (web/lib/dev-diagnostic-preview.ts) -- any non-Production send is
  // marked test_mode so Dropbox Sign never treats it as legally binding.
  const testMode = process.env.VERCEL_ENV !== "production";

  const dropboxSignRes = await fetch(DROPBOX_SIGN_SEND_WITH_TEMPLATE_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Basic ${Buffer.from(`${apiKey}:`).toString("base64")}`,
    },
    body: JSON.stringify({
      template_ids: [templateId],
      signers: [{ role: "Client", name, email_address: email }],
      test_mode: testMode,
    }),
  });

  if (!dropboxSignRes.ok) {
    return NextResponse.json({ error: "Could not send the agreement" }, { status: 502 });
  }

  return NextResponse.json({ success: true });
}
