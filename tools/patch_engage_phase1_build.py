"""
Real Transaction Path -- Phase 1 (e-signature only) build.

Architecture proposed this session, sent to Gemini for review, and
finalized after discussion -- full record in
prompts/real-transaction-path-phase1-gemini-request.md. Three locked
scoping decisions this build implements exactly:

  1. E-signature only. No payment/card collection of any kind (Stripe,
     SetupIntent, or otherwise) -- deferred to a separate future Phase 2.
  2. Provider: Dropbox Sign, hosted (non-embedded) signing -- confirmed
     directly against Dropbox Sign's own API reference that name + email
     is genuinely the minimum the signer object requires.
  3. Signed-document storage: Dropbox Sign's own storage is the source of
     truth. Nothing in this build writes a signed document, or any
     completion-status record, anywhere in this repo or its infrastructure.

Webhook (/api/engage/webhook) is explicitly NOT part of this build. Pete's
first-pass decision was to build it now in a narrowly scoped form (verify/
parse/persist only); Gemini's review argued the opposite (skip it -- no
active consumer exists anywhere in this repo for a "signed" event, and even
the scoped-down version would have produced an invisible Redis record
nothing displays). Reviewed on the merits, Pete's final call was to defer
the webhook entirely to Phase 2, once that phase's real requirements
determine what the persisted record should actually look like. Dropbox
Sign's own dashboard/native completion notifications are the interim way
to check signature status. See the request doc's "Webhook scope -- final
decision" section for the full reasoning.

Five files, two new:

  - web/app/engage/page.tsx (NEW) -- minimal name/email intake, standalone,
    reachable from PrivateOutput's new Engage CTA or directly. Carries no
    diagnostic result data forward -- Dropbox Sign's hosted flow needs
    nothing from it.
  - web/app/api/engage/initiate/route.ts (NEW) -- calls Dropbox Sign's
    POST /signature_request/send_with_template (JSON body, confirmed via
    live API reference fetch this session -- NOT multipart/form-data,
    which is only required for the plain /send endpoint's raw file
    uploads). test_mode is wired to VERCEL_ENV != "production", the same
    convention isPreviewEnvironment() (web/lib/dev-diagnostic-preview.ts)
    already uses, so a Preview/Development send is never treated as
    legally binding by Dropbox Sign.
  - web/components/PrivateOutput.tsx (EDIT) -- new `enableEngage?: boolean`
    prop (default true), mirroring `enableSharing`'s existing suppression
    pattern exactly. New Block 6 CTA, linking to /engage. The old
    "Block 6" trailing comment (which was never an actual rendered block,
    just a note that friction_tax_estimate renders nothing) is renumbered
    to Block 7 so the two aren't both labeled 6.
  - web/app/dev/diagnostic-preview/[id]/page.tsx (EDIT) -- adds
    `enableEngage={false}` alongside the existing `enableSharing={false}`,
    so the dev/test viewer (synthetic, tools/diagnostic_fast_forward.py-
    driven results) can never trigger a real Dropbox Sign request.
  - web/.env.local.example (EDIT) -- documents the two new secrets,
    DROPBOX_SIGN_API_KEY and DROPBOX_SIGN_TEMPLATE_ID. Per the request
    doc's provisioning plan, both get three separate Vercel rows
    (Production/Preview/Development), mirroring ANTHROPIC_API_KEY's
    correct-from-day-one model, not the Redis row's original combined-
    scope mistake (tools/_mob.txt Section 13a).

NOT part of this build (out of scope, confirmed): no Stripe import, no
card field, no pricing UI anywhere -- Phase 1 is e-signature only per
decision 1. No webhook route. No Dropbox Sign Template actually created in
the dashboard -- that is a one-time manual step Pete does separately
(uploading documents/PRV3_Engagement_Agreement_Draft_v1.0.docx, defining
the "Client" signer role, and setting DROPBOX_SIGN_TEMPLATE_ID from the
result). No Vercel env vars provisioned by this script -- also Pete's step.

Usage:
    python tools/patch_engage_phase1_build.py --dry-run
    python tools/patch_engage_phase1_build.py --write
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# ─────────────────────────────────────────────────────────────────────────────
# Edits to existing files
# ─────────────────────────────────────────────────────────────────────────────

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str) -> None:
    EDITS.append((path, old, new))


PRIVATE_OUTPUT = "web/components/PrivateOutput.tsx"
DEV_PREVIEW_PAGE = "web/app/dev/diagnostic-preview/[id]/page.tsx"
ENV_EXAMPLE = "web/.env.local.example"

# PrivateOutput.tsx -- import Link (new, for the Engage CTA below).
edit(
    PRIVATE_OUTPUT,
    '"use client";\n'
    '\n'
    'import type { PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";\n'
    'import type { EnginePayload } from "@/lib/engine-client";\n'
    'import ShareButton from "@/components/ShareButton";\n'
    'import { ConstellationField, severityAccentTokens } from "@/components/ConstellationField";\n'
    'import { stateIdToSlug } from "@/lib/state-slug";\n',
    '"use client";\n'
    '\n'
    'import Link from "next/link";\n'
    'import type { PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";\n'
    'import type { EnginePayload } from "@/lib/engine-client";\n'
    'import ShareButton from "@/components/ShareButton";\n'
    'import { ConstellationField, severityAccentTokens } from "@/components/ConstellationField";\n'
    'import { stateIdToSlug } from "@/lib/state-slug";\n',
)

# PrivateOutput.tsx -- enableEngage prop, mirroring enableSharing exactly.
edit(
    PRIVATE_OUTPUT,
    'interface PrivateOutputProps {\n'
    '  payload: PrivateOutputPayload;\n'
    '  selectedStateIds: string[];\n'
    '  intake: EnginePayload["intake"];\n'
    '  // Path 1 (Session 71, Phase 1): ShareButton re-invokes /api/share/create\n'
    '  // with Path B\'s declared-diagnosis logic (equal weight, selectedStateIds\n'
    '  // as the diagnosis), which would silently recompute — and corrupt — Path\n'
    '  // 1\'s real cosine-similarity-derived weights. ShareableOutput generation\n'
    '  // for Path 1 is explicitly out of scope this phase. Default true —\n'
    '  // existing self-select callers are unaffected.\n'
    '  enableSharing?: boolean;\n'
    '}\n',
    'interface PrivateOutputProps {\n'
    '  payload: PrivateOutputPayload;\n'
    '  selectedStateIds: string[];\n'
    '  intake: EnginePayload["intake"];\n'
    '  // Path 1 (Session 71, Phase 1): ShareButton re-invokes /api/share/create\n'
    '  // with Path B\'s declared-diagnosis logic (equal weight, selectedStateIds\n'
    '  // as the diagnosis), which would silently recompute — and corrupt — Path\n'
    '  // 1\'s real cosine-similarity-derived weights. ShareableOutput generation\n'
    '  // for Path 1 is explicitly out of scope this phase. Default true —\n'
    '  // existing self-select callers are unaffected.\n'
    '  enableSharing?: boolean;\n'
    '  // Real Transaction Path, Phase 1 (e-signature only, this session).\n'
    '  // Suppresses the Engage CTA (Block 6) — identical suppression pattern to\n'
    '  // enableSharing above. Default true; set false on the dev/test preview\n'
    '  // viewer (web/app/dev/diagnostic-preview/[id]/page.tsx) so a synthetic,\n'
    '  // fast-forwarded result can never trigger a real Dropbox Sign request.\n'
    '  enableEngage?: boolean;\n'
    '}\n',
)

# PrivateOutput.tsx -- destructure enableEngage with the same default=true idiom.
edit(
    PRIVATE_OUTPUT,
    'export default function PrivateOutput({\n'
    '  payload,\n'
    '  selectedStateIds,\n'
    '  intake,\n'
    '  enableSharing = true,\n'
    '}: PrivateOutputProps) {\n',
    'export default function PrivateOutput({\n'
    '  payload,\n'
    '  selectedStateIds,\n'
    '  intake,\n'
    '  enableSharing = true,\n'
    '  enableEngage = true,\n'
    '}: PrivateOutputProps) {\n',
)

# PrivateOutput.tsx -- new Block 6 (Engage CTA) after ShareButton. The old
# "Block 6" comment (never an actual rendered block) is renumbered to 7.
edit(
    PRIVATE_OUTPUT,
    '      {/* Block 5 — ShareButton */}\n'
    '      {enableSharing && (\n'
    '        <div className="mt-2 w-full">\n'
    '          <ShareButton selectedStateIds={selectedStateIds} intake={intake} />\n'
    '        </div>\n'
    '      )}\n'
    '\n'
    '      {/* Block 6 — friction_tax_estimate: null in Path B — render nothing */}\n'
    '    </div>\n'
    '  );\n'
    '}\n',
    '      {/* Block 5 — ShareButton */}\n'
    '      {enableSharing && (\n'
    '        <div className="mt-2 w-full">\n'
    '          <ShareButton selectedStateIds={selectedStateIds} intake={intake} />\n'
    '        </div>\n'
    '      )}\n'
    '\n'
    '      {/* Block 6 — Engage CTA (Real Transaction Path, Phase 1). Links out\n'
    '          to the standalone /engage intake (name + email only, per Phase\n'
    '          1\'s e-signature-only scope) rather than carrying any diagnostic\n'
    '          result data forward — Dropbox Sign\'s hosted signing flow needs\n'
    '          nothing from this payload. enableEngage mirrors enableSharing\'s\n'
    '          suppression pattern exactly (see prop doc comment above). */}\n'
    '      {enableEngage && (\n'
    '        <div className="mt-6 pt-6 border-t border-gray-200">\n'
    '          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-3">\n'
    '            Ready to move on this?\n'
    '          </p>\n'
    '          <Link\n'
    '            href="/engage"\n'
    '            className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"\n'
    '          >\n'
    '            Start the engagement →\n'
    '          </Link>\n'
    '        </div>\n'
    '      )}\n'
    '\n'
    '      {/* Block 7 — friction_tax_estimate: null in Path B — render nothing */}\n'
    '    </div>\n'
    '  );\n'
    '}\n',
)

# Dev/test preview viewer -- suppress the new CTA the same way sharing is
# already suppressed there.
edit(
    DEV_PREVIEW_PAGE,
    '          enableSharing={false}\n'
    '        />\n',
    '          enableSharing={false}\n'
    '          enableEngage={false}\n'
    '        />\n',
)

# .env.local.example -- document the two new secrets.
edit(
    ENV_EXAMPLE,
    'ANTHROPIC_API_KEY=your-key-here\n'
    'UPSTASH_REDIS_REST_URL=your-upstash-redis-rest-url\n'
    'UPSTASH_REDIS_REST_TOKEN=your-upstash-redis-rest-token\n'
    '# Shared secret for internal Next.js -> Python engine calls\n'
    '# Must match ENGINE_SECRET in Vercel environment variables\n'
    'ENGINE_SECRET=your-secret-here\n',
    'ANTHROPIC_API_KEY=your-key-here\n'
    'UPSTASH_REDIS_REST_URL=your-upstash-redis-rest-url\n'
    'UPSTASH_REDIS_REST_TOKEN=your-upstash-redis-rest-token\n'
    '# Shared secret for internal Next.js -> Python engine calls\n'
    '# Must match ENGINE_SECRET in Vercel environment variables\n'
    'ENGINE_SECRET=your-secret-here\n'
    '# Real Transaction Path, Phase 1 (e-signature only) -- Dropbox Sign.\n'
    '# DROPBOX_SIGN_API_KEY authenticates outbound calls to\n'
    '# /signature_request/send_with_template. DROPBOX_SIGN_TEMPLATE_ID is the\n'
    '# one-time Dropbox Sign dashboard Template built from\n'
    '# documents/PRV3_Engagement_Agreement_Draft_v1.0.docx (signer role "Client").\n'
    '# No webhook secret needed yet -- /api/engage/webhook is deferred to Phase 2.\n'
    'DROPBOX_SIGN_API_KEY=your-dropbox-sign-api-key\n'
    'DROPBOX_SIGN_TEMPLATE_ID=your-dropbox-sign-template-id\n',
)

# ─────────────────────────────────────────────────────────────────────────────
# New files
# ─────────────────────────────────────────────────────────────────────────────

NEW_FILES: list[tuple[str, str]] = []

ENGAGE_PAGE = "web/app/engage/page.tsx"
ENGAGE_PAGE_CONTENT = '''"use client";

import { useState } from "react";

// ---------------------------------------------------------------------------
// Real Transaction Path — Phase 1 (e-signature only). Architecture proposed,
// Gemini-reviewed, and finalized this session -- see
// prompts/real-transaction-path-phase1-gemini-request.md.
//
// Name and email are genuinely the only fields Dropbox Sign's hosted
// signing flow requires (confirmed directly against Dropbox Sign's API
// reference, not assumed) -- no headcount/industry/jurisdiction carried
// over from the diagnostic. Standalone entry point, reachable from
// PrivateOutput's Engage CTA or directly. On submit, Dropbox Sign emails
// the signer directly (hosted mode) -- this page never sees a signing_url
// or the document itself, and no payment is collected anywhere in this
// flow (decision 1, Phase 1 scope).
// ---------------------------------------------------------------------------

type EngageState =
  | { phase: "form" }
  | { phase: "loading" }
  | { phase: "sent" }
  | { phase: "error"; message: string };

const ERROR_COPY =
  "Something went wrong. Please try again, or reach out directly at pete@principalresolution.com.";

export default function EngagePage() {
  const [state, setState] = useState<EngageState>({ phase: "form" });
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");

  const isComplete = name.trim().length > 0 && email.trim().length > 0;

  async function handleSubmit() {
    if (!isComplete) return;
    setState({ phase: "loading" });
    try {
      const res = await fetch("/api/engage/initiate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, email }),
      });
      if (!res.ok) {
        setState({ phase: "error", message: ERROR_COPY });
        return;
      }
      setState({ phase: "sent" });
    } catch {
      setState({ phase: "error", message: ERROR_COPY });
    }
  }

  if (state.phase === "sent") {
    return (
      <main className="max-w-md mx-auto px-6 py-16 text-center">
        <h1 className="font-display text-2xl text-charcoal mb-4">Check your email.</h1>
        <p className="font-ui text-sm text-gray-500 leading-relaxed">
          The engagement agreement is on its way to {email}. Sign it there —
          there&apos;s nothing further to do on this page.
        </p>
      </main>
    );
  }

  if (state.phase === "error") {
    return (
      <main className="max-w-md mx-auto px-6 py-16 text-center">
        <p className="font-display text-xl text-charcoal mb-6">{state.message}</p>
        <button
          onClick={() => setState({ phase: "form" })}
          className="bg-charcoal text-white font-ui text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-gray-800 transition-colors"
        >
          Try again
        </button>
      </main>
    );
  }

  const isLoading = state.phase === "loading";

  return (
    <main className="max-w-md mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">
        Engagement
      </p>
      <h1 className="font-display text-2xl text-charcoal mb-3">
        Start the engagement.
      </h1>
      <p className="font-ui text-sm text-gray-500 leading-relaxed mb-10">
        We&apos;ll send the engagement agreement to your email for signature.
        No payment is collected here.
      </p>

      <div className="mb-5">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Your name
        </label>
        <input
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>
      <div className="mb-8">
        <label className="block font-ui text-sm font-medium text-charcoal mb-1.5">
          Your email
        </label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={!isComplete || isLoading}
        className="w-full bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {isLoading ? "Sending…" : "Send the agreement"}
      </button>
    </main>
  );
}
'''
NEW_FILES.append((ENGAGE_PAGE, ENGAGE_PAGE_CONTENT))

ENGAGE_INITIATE_ROUTE = "web/app/api/engage/initiate/route.ts"
ENGAGE_INITIATE_ROUTE_CONTENT = '''import { NextRequest, NextResponse } from "next/server";

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
'''
NEW_FILES.append((ENGAGE_INITIATE_ROUTE, ENGAGE_INITIATE_ROUTE_CONTENT))


# ─────────────────────────────────────────────────────────────────────────────

def apply(dry_run: bool) -> int:
    file_texts: dict[str, str] = {}

    for rel_path, old, _new in EDITS:
        if rel_path not in file_texts:
            file_texts[rel_path] = (REPO_ROOT / rel_path).read_text(encoding="utf-8")
        count = file_texts[rel_path].count(old)
        if count != 1:
            print(f"ABORT: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1

    for rel_path, old, new in EDITS:
        file_texts[rel_path] = file_texts[rel_path].replace(old, new, 1)

    for rel_path, _content in NEW_FILES:
        if (REPO_ROOT / rel_path).exists():
            print(f"ABORT: {rel_path} already exists -- refusing to overwrite")
            return 1

    for rel_path, new_text in file_texts.items():
        path = REPO_ROOT / rel_path
        original = path.read_text(encoding="utf-8")
        if dry_run:
            print(f"\\n{'=' * 80}\\nDIFF: {rel_path}\\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{rel_path} (before)",
                tofile=f"{rel_path} (after)",
            )
            print("".join(diff))
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WROTE: {rel_path}")

    for rel_path, content in NEW_FILES:
        path = REPO_ROOT / rel_path
        if dry_run:
            print(f"\\n{'=' * 80}\\nNEW FILE: {rel_path}\\n{'=' * 80}")
            print(content)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print(f"CREATED: {rel_path}")

    if dry_run:
        print("\\nDry run complete. No files written. Re-run with --write to apply.")
    return 0


def main() -> None:
    # Windows console default (cp1252) can't encode the em-dashes/arrows in
    # this script's diffs -- force UTF-8 stdout, matching every file write
    # below which already uses encoding="utf-8" explicitly.
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
