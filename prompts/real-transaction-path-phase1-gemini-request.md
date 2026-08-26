# Real Transaction Path — Phase 1 (E-Signature Only) — Gemini Architecture Review Request

Durable request file. Priority Queue item 1 (diagnostic → signed engagement) is a structural/scope decision (Tier 3) affecting new API routes, a new page, and new secret management — per standing discipline, routes through Gemini architecture review before any build. **No code has been written.** This document, plus the three locked scoping decisions it's built on, is the only artifact produced this session.

---

## Context

**What's locked already (Pete, Claude.ai, this session):**
1. Phase 1 = e-signature only. No payment or card collection of any kind, including a Stripe SetupIntent card-on-file — email alone is sufficient for now. Payment is explicitly deferred to a separate future Phase 2, scoped once pricing is locked.
2. E-signature provider: **Dropbox Sign** (formerly HelloSign) — chosen over DocuSign (too enterprise-heavy for this volume/cost) and PandaDoc (bundles payment, unneeded complexity given decision 1).
3. Signed-document storage: **Dropbox Sign's own storage is the source of truth.** The signed agreement must NOT be committed to this git repo — unlike the unsigned template (`documents/PRV3_Engagement_Agreement_Draft_v1.0.docx`), which correctly lives in the repo since it carries no client-specific data, a signed doc carries a specific client's name, business details, and signature, and committing that would put personal data in git history permanently.

**What exists today, confirmed by direct read this session:**

- **No "Engage" CTA exists anywhere yet.** `PrivateOutput.tsx` (the shared results component rendered by both the live Path 1 diagnostic and the self-select Path B flow) ends at Block 5, a `ShareButton`. There is nothing to "wire" — this is new UI, not activating a dormant button. `/ask` (`web/app/ask/page.tsx`) is a static `mailto:` link, unrelated to this flow. The natural spot is a new block after `ShareButton` in `PrivateOutput.tsx`, since that component is the single shared exit point for every path that produces a result — but see the dev-preview note below.
- **`PrivateOutput` already has a precedent for suppressing a block per caller**: `enableSharing?: boolean` (default `true`), explicitly set `false` by `web/app/dev/diagnostic-preview/[id]/page.tsx` (the `tools/diagnostic_fast_forward.py`-driven dev/test viewer) and by `DiagnosticFlow.tsx`'s own complete phase. Any new Engage CTA should follow the identical pattern (`enableEngage`, default `true`, set `false` on the dev-preview route) rather than introduce a new suppression mechanism — the dev/test viewer must not offer a real signature flow.
- **Existing API route convention** (`web/app/api/diagnostic/session/start/route.ts`, `web/app/api/share/create/route.ts`): Next.js App Router `route.ts` files, `export async function POST(request: NextRequest)`, manual hand-written request-shape validation (no schema library in use — `zod` is not a dependency), `NextResponse.json(...)` responses, errors returned as `{ error: string }` with a 4xx/5xx status.
- **Existing secret-management convention**: `web/.env.local.example` documents every required var; `web/lib/session-store.ts` and `web/app/api/share/create/route.ts` both call `Redis.fromEnv()` (reads `UPSTASH_REDIS_REST_URL`/`UPSTASH_REDIS_REST_TOKEN` implicitly); `engine-client.ts` reads `ENGINE_SECRET` via `process.env`. Per `tools/_mob.txt` Section 13a ("Production and Preview shared the same Redis instance"), this project has a documented incident from provisioning one Vercel env var as a single combined Production+Preview row instead of two separate per-environment rows — `ANTHROPIC_API_KEY` was provisioned correctly (three separate rows: Production/Preview/Development) from day one and is the model to copy, not the Redis row's original mistake.
- **No email-sending infrastructure exists anywhere in this repo.** No SendGrid/Resend/Nodemailer dependency, no server-side email code. `/ask`'s `mailto:` link is client-side only. This was part of why the webhook was ultimately deferred — see "Webhook scope — final decision" below.

**Dropbox Sign API facts, verified directly against current developer documentation this session (not from training-data recall — see Sources):**

- Two request modes: **hosted** (Dropbox Sign emails the signer directly; they sign on Dropbox Sign's own platform) and **embedded** (signing happens in an iframe on your own site, requires a registered API App and its `client_id`). [Signature Request | Dropbox Sign Developer Documentation](https://developers.hellosign.com/api/signature-request)
- For the plain (non-embedded) `POST /signature_request/send` endpoint: **`client_id` is optional, not required.** The only hard requirements are (a) `files` or `file_urls` (or a `template_id` via the `/send_with_template` variant), and (b) `signers` — where each signer object requires exactly `name` and `email_address`, nothing else. [Create Embedded Signature Request | Dropbox Sign for Developers](https://developers.hellosign.com/api/reference/operation/signatureRequestCreateEmbedded/)
- This confirms Pete's decision 1 assumption exactly: **name + email is genuinely the minimum the API requires**, for the hosted flow specifically. Embedded would additionally require a registered API App (`client_id`) purely for iframe authentication — no additional signer data — but adds real integration weight (client-side embedded-signing JS SDK, an iframe-hosting page) for a project with zero existing precedent for embedding third-party signing UI.
- Webhooks: configured via an `event_callback_url`; Dropbox Sign POSTs `multipart/form-data` with event details in a `json` field. The completion event is `signature_request_all_signed` (distinct from `signature_request_signed`, which fires per-signer and from `signature_request_downloadable`, which can lag completion while the final file renders). **Your endpoint must respond with HTTP 200 and a body containing the literal text `Hello API Event Received`** — not JSON — or Dropbox Sign will treat the callback as failed and retry. [Events and Callbacks | Dropbox Sign Developer Documentation](https://developers.hellosign.com/docs/guides/events-and-callbacks)
- Authenticity verification: every event payload carries an `event_hash`, computed as `HMAC-SHA256(event_time + event_type)` keyed by your account's API key. Verify by recomputing the same HMAC server-side and comparing. [Walkthrough | Dropbox Sign Developer Documentation](https://developers.hellosign.com/docs/events/walkthrough/)
- **A live account detail search could not verify from documentation alone, flagged rather than assumed**: Dropbox Sign's dashboard/account-level email notifications on request completion (i.e., whether Pete's own account already gets emailed when a request he sent gets fully signed, independent of any webhook). This is standard behavior for e-signature platforms generally but wasn't confirmed against Dropbox Sign's own docs specifically this session — worth Pete confirming directly in the Dropbox Sign account settings now, since (per "Webhook scope — final decision" below) this native notification is the only completion signal Phase 1 will have.

---

## Proposed architecture (for review, not yet built)

1. **New page**: `web/app/engage/page.tsx` — minimal client component, two fields (name, email), same visual/form idiom as `IntakeForm` in `DiagnosticFlow.tsx` (labeled inputs, disabled-until-complete submit button). No headcount/industry/jurisdiction fields — Dropbox Sign needs nothing else, and Phase 1 has no payment step to gate behind more intake.
2. **New CTA**: a Block 6 in `PrivateOutput.tsx`, after `ShareButton`, linking to `/engage` (or, if Pete wants zero extra navigation, a collapsed inline form triggered from that block — a UI-polish call, not an architecture one). Gated by a new `enableEngage?: boolean` prop (default `true`), set `false` in `web/app/dev/diagnostic-preview/[id]/page.tsx` alongside the existing `enableSharing={false}`.
3. **New API route — `POST /api/engage/initiate`**: validates `{ name: string, email: string }` (same manual-validation style as every existing route), then calls Dropbox Sign's `POST /signature_request/send_with_template` with a pre-created Dropbox Sign **Template** (a one-time manual dashboard step: Pete uploads `documents/PRV3_Engagement_Agreement_Draft_v1.0.docx` to Dropbox Sign once and defines a single signer role, e.g. "Client") — `template_id` stored as an env var, not re-uploaded per request. Returns a plain confirmation (`{ success: true }`) to the client; the page then shows "Check your email" copy. No `signing_url` needs to reach the client — hosted mode means Dropbox Sign emails the signer directly.
4. **`POST /api/engage/webhook` — DEFERRED, not built in Phase 1.** See "Webhook scope — final decision" below for the full reasoning. Phase 1 ships with no inbound completion handling of any kind; Dropbox Sign's own dashboard is the sole way to check signature status until Phase 2 defines a real consumer.
5. **New secrets**, following the `ANTHROPIC_API_KEY` per-environment provisioning model (three separate Vercel rows: Production/Preview/Development), not the Redis row's original combined-row mistake: `DROPBOX_SIGN_API_KEY` (outbound API auth for `/api/engage/initiate` — no inbound webhook use in Phase 1) and `DROPBOX_SIGN_TEMPLATE_ID`. Both added to `web/.env.local.example` alongside the existing four.
6. **No payment-adjacent code anywhere** — no Stripe import, no card field, no pricing display on `/engage`. Out of scope per decision 1.

---

## Webhook scope — final decision

This went through two rounds. First, Pete decided to build `/api/engage/webhook` now in a narrowly scoped form (verify → parse → persist a Redis record, no completion-triggered action). That draft was sent to Gemini for architecture review. Gemini's response recommended the opposite — skip the webhook for Phase 1 entirely — arguing (a) no active consumer exists anywhere in this repo for a "signed" event, (b) decision 3's Dropbox-Sign-as-source-of-truth framing extends naturally to status as well as documents, and (c) skipping it avoids real production surface (a public retry-prone URL, HMAC verification, a non-JSON response contract) for a project this early.

Reviewed on the merits, not deferred to either side by default: (b) doesn't fully hold up — decision 3 was specifically about not committing signed *documents* to git, and a status-only Redis mirror wouldn't have compromised Dropbox Sign's authority any more than `ShareableOutput` already caches computed engine results in Redis while the engine stays authoritative. (c) is real but modest — the actual code delta is small, not the "eliminates HMAC maintenance" framing Gemini used. **Point (a) is what actually decided it**: even in the narrowly scoped version, the resulting Redis record would have been invisible day-to-day — nothing in this proposal builds a way to view it, so building it now would not have given Pete any usable visibility, only a data shape seeded for a consumer that doesn't exist yet.

**Final call (Pete, after discussion): defer the webhook entirely.** Phase 1 ships `/engage` and `/api/engage/initiate` only. Dropbox Sign's own dashboard/native notifications are the interim way to check signature status. The webhook gets built in Phase 2, once that phase's actual requirements (payment reconciliation, or whatever else needs to react to a signature programmatically) determine what the persisted record should actually look like — designing it now, before there's a real consumer, risked designing it wrong.

---

## Verification requirement

Same standard as every prior architecture review on this project. Any claim about Dropbox Sign's actual API behavior, this repo's existing patterns, or Next.js App Router conventions must cite the specific source it's grounded in (a fetched doc URL, or a repo file and line) — not a restatement of what the API "should" or "typically" does. This project's Gemini-review history has a documented pattern of fabricated or stale technical claims slipping through on exactly this class of question (see `tools/_mob.txt` Section 13a's several "Gemini claim independently verified, found wrong" rows) — narrow, cite-or-flag answers are what has worked, open-ended confident prose has not.

---

## Not asked here

No code written, no page created, no route created, no `.env.local.example` edit, no Vercel env var provisioned, no Dropbox Sign account/template created. Per "Webhook scope — final decision" above, `/api/engage/webhook` itself — not just its completion-handling behavior — is out of scope for the Phase 1 build entirely, deferred to Phase 2. This document now reflects Pete's final, Gemini-reviewed decision; the next step is building items 1, 2, 3, 5, and 6 above.

**Sources cited above:**
- [Signature Request | Dropbox Sign Developer Documentation](https://developers.hellosign.com/api/signature-request)
- [Create Embedded Signature Request | Dropbox Sign for Developers](https://developers.hellosign.com/api/reference/operation/signatureRequestCreateEmbedded/)
- [Events and Callbacks | Dropbox Sign Developer Documentation](https://developers.hellosign.com/docs/guides/events-and-callbacks)
- [Walkthrough | Dropbox Sign Developer Documentation](https://developers.hellosign.com/docs/events/walkthrough/)
