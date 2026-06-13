import { NextRequest, NextResponse } from "next/server";
import Anthropic from "@anthropic-ai/sdk";
import { buildInterpretationPrompt } from "@/lib/prompts";

const PERMITTED_FIELDS = new Set(["name", "signatureId"]);

function validatePayload(
  states: unknown
): states is { name: string; signatureId: string }[] {
  if (!Array.isArray(states)) return false;
  for (const item of states) {
    if (typeof item !== "object" || item === null) return false;
    for (const key of Object.keys(item)) {
      if (!PERMITTED_FIELDS.has(key)) return false;
    }
    if (
      typeof (item as Record<string, unknown>).name !== "string" ||
      typeof (item as Record<string, unknown>).signatureId !== "string"
    ) {
      return false;
    }
  }
  return true;
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const { states } = body;

  if (!validatePayload(states)) {
    return NextResponse.json({ error: "Invalid payload" }, { status: 400 });
  }

  const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

  const response = await client.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 200,
    messages: [{ role: "user", content: buildInterpretationPrompt(states) }],
  });

  return NextResponse.json({
    interpretation: (response.content[0] as { text: string }).text,
  });
}
