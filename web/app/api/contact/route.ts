import { NextRequest, NextResponse } from "next/server";
import { Resend } from "resend";

interface ContactBody {
  name: string;
  email: string;
  organization?: string;
  message: string;
  website?: string;
}

function isValidBody(body: unknown): body is ContactBody {
  if (typeof body !== "object" || body === null) return false;
  const b = body as Record<string, unknown>;
  return (
    typeof b.name === "string" &&
    typeof b.email === "string" &&
    typeof b.message === "string"
  );
}

function isValidEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "Invalid JSON" }, { status: 400 });
  }

  if (!isValidBody(body)) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const { name, email, organization, message, website } = body;

  const trimmedName = name.trim();
  const trimmedEmail = email.trim();
  const trimmedMessage = message.trim();

  if (!trimmedName || !trimmedEmail || !trimmedMessage) {
    return NextResponse.json({ error: "Missing required fields" }, { status: 400 });
  }

  if (!isValidEmail(trimmedEmail)) {
    return NextResponse.json({ error: "Invalid email address" }, { status: 400 });
  }

  // Honeypot — silently succeed without sending
  if (website && website.trim().length > 0) {
    return NextResponse.json({ ok: true });
  }

  const apiKey = process.env.RESEND_API_KEY;
  const toEmail = process.env.CONTACT_TO_EMAIL;

  if (!apiKey || !toEmail) {
    return NextResponse.json({ error: "Service unavailable" }, { status: 500 });
  }

  const resend = new Resend(apiKey);

  const orgLine = organization?.trim()
    ? `Organization: ${organization.trim()}\n`
    : "";

  const emailBody = `Name: ${trimmedName}
Email: ${trimmedEmail}
${orgLine}
Message:
${trimmedMessage}`;

  try {
    await resend.emails.send({
      from: "onboarding@resend.dev",
      to: toEmail,
      subject: `New inquiry via Just Ask — ${trimmedName}`,
      text: emailBody,
    });
  } catch {
    return NextResponse.json({ error: "Service unavailable" }, { status: 500 });
  }

  return NextResponse.json({ ok: true });
}
