# PRV3 Output Layer — Gemini Route Handler Payload Separation Review

## Context

PRV3 is an organizational diagnostic platform. The output layer (WS2) has just been scaffolded. Three route handlers were created in Session 38 implementing two payload types: PrivateOutput (for the principal) and ShareableOutput (for external sharing).

The locked architectural constraint is:
> "Payload separation is a server boundary, not a rendering hide. Enforce at serialization, not at the component level."

This constraint comes from a locked S34 decision: the diagnostic output must never expose private organizational data through the shareable endpoint, regardless of what the component tree renders.

## What was built

Three route handlers in `web/app/api/`:

### `/api/result` (POST)
Accepts: `{ sessionId, selectedStateIds, intake }`
Returns: `PrivateOutputPayload` — principal-facing only.
Constraint: ShareableOutput is **never** serialized into this response.

### `/api/share/create` (POST)
Accepts: `{ sessionId }`
Writes to Vercel KV: `ShareableOutputPayload` only.
Constraint: PrivateOutput fields are **never** written to KV.
Returns: `{ shareKey, shareUrl, expiresAt }`

### `/api/share/[id]` (GET)
Reads from KV by share key.
Returns: `ShareableOutputPayload` only.
Constraint: PrivateOutput **never exists** in this response. Returns 404 if not found or expired (KV TTL handles expiry).

## The PrivateOutputPayload type

```typescript
interface PrivateOutputPayload {
  sessionId: string;
  outputType: "single_state" | "multi_state" | "no_signal";
  identifiedStates: Array<{
    state_id: string;
    state_name: string;
    score: number;
    distinguishing_language?: string | null;
  }>;
  severity: {
    tier: string;
    score: number;        // 0-100
    anchor_text: string;
  };
  privateOutput: {
    opening_text: string;
    liability_block: string;
    asset_anchor_text: string;
    resolution_routing: string;
    friction_tax_estimate: {
      low: number | null;
      high: number | null;
      currency: string;
      org_size_label: string;
      severity_scalar: number;
      calibration_complete: boolean;
    } | null;
  };
  synthesis?: {
    privateSynthesis: string;  // LLM-generated, private
    synthesisConfidence: number;
    isFallback: boolean;
  };
}
```

## The ShareableOutputPayload type

```typescript
interface ShareableOutputPayload {
  sessionId: string;
  shareKey: string;
  expiresAt: string;
  outputType: "single_state" | "multi_state" | "no_signal";
  identifiedStates: Array<{
    state_id: string;
    state_name: string;
    score: number;
  }>;
  severity: {
    tier: string;
    anchor_text: string;       // NOTE: no score field — severity score not shared
  };
  shareableOutput: {
    framing_text: string;
    observable_indicators: string[];
    resolution_framing: string;
    attribution_text: string;
  };
  synthesis?: {
    shareableSynthesis: string;  // LLM-generated, third-party safe
    synthesisConfidence: number;
    isFallback: boolean;
    // NOTE: privateSynthesis never appears here
  };
}
```

## What I need reviewed

1. **Separation audit**: Is the PrivateOutputPayload type designed in a way that makes accidental leakage into ShareableOutput easy or hard? Is there any field in PrivateOutputPayload that should not exist in PrivateOutputPayload or should be restructured?

2. **KV write boundary**: The `/api/share/create` route is responsible for fetching the session's engine output server-side and extracting only the shareable portion before writing to KV. Currently a TODO — it hasn't been wired to the actual engine session store yet. What is the recommended pattern for server-side session management in Next.js App Router (App Dir) that ensures PrivateOutput never touches the KV write path?

3. **`synthesis` optional field risk**: Both payload types have an optional `synthesis` field. On `PrivateOutputPayload`, it contains `privateSynthesis`. On `ShareableOutputPayload`, it contains `shareableSynthesis`. Is there a structural risk that a developer could accidentally use the wrong synthesis key? Should these be separate required types rather than optionals?

4. **Score exposure in ShareableOutput**: The `ShareableOutputPayload.severity` type intentionally omits `score` (only `tier` and `anchor_text`). The `PrivateOutputPayload.severity` includes `score` (0-100 numeric). Is this the right separation point for severity data? Should `state_id` scores in `identifiedStates` also be omitted from the shareable payload?

5. **Route handler shell vs. full implementation risk**: The `/api/result` handler currently returns placeholder data. When the real engine call is wired in (S39), what is the most robust pattern to ensure the serialization boundary holds — explicitly pick fields rather than spreading the full engine output object?

## Decision needed

For item 2: recommend a session storage pattern (in-memory Map keyed by sessionId, Redis, encrypted cookie, other) given Next.js App Router constraints and the requirement that PrivateOutput never persists in any form accessible from the shareable path.

For item 5: confirm or reject the approach of explicit field selection at the `/api/result` handler boundary vs. defining a serialization allow-list type.

## What I am NOT asking

- Do not recommend UI/component-level separation — payload separation is a server boundary, not a rendering concern.
- Do not recommend session IDs be exposed to the client in a way that allows re-fetching private data via the shareable endpoint.
- Do not suggest sharing more than `shareKey` with the client after `/api/share/create` resolves.
