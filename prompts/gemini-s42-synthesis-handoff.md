# PRV3 — Gemini Review Request
## Session 42 — output_synthesis.py Contract Migration

**Date:** 2026-06-14
**Requesting:** Architecture review before execution
**Deciding:** Pete
**Executing after confirmation:** Claude Code

---

## Context

`engine/output_synthesis.py` currently generates two synthesis fields: `private_synthesis` and `shareable_synthesis`. These are LLM-authored strings returned in a `SynthesisResult` dataclass.

Session 42 produced `PRV3_Output_Synthesis_Prompts_v1.0.docx`, which specifies a new five-field output contract. This is a data contract migration — not just a prompt update — and it cascades across multiple files.

Claude Code flagged this to Pete before execution. Pete confirmed Gemini review is required.

---

## Current contract (to be replaced)

```python
@dataclass
class SynthesisResult:
    private_synthesis:    str
    shareable_synthesis:  str
    synthesis_confidence: float
    raw_response:         str = ""
    parse_error:          str = ""
    is_fallback:          bool = False
```

Current LLM output JSON:
```json
{
  "private_synthesis": "...",
  "shareable_synthesis": "...",
  "synthesis_confidence": 0.0
}
```

---

## Proposed new contract

```python
@dataclass
class SynthesisResult:
    liability_condition_text:     str
    asset_resolution_anchor_text: str
    framing_text:                 str
    observable_indicators:        list[str]
    resolution_framing_text:      str
    synthesis_confidence:         float
    raw_response:                 str = ""
    parse_error:                  str = ""
    is_fallback:                  bool = False
```

New LLM output JSON (single call, all five fields):
```json
{
  "liability_condition_text": "...",
  "asset_resolution_anchor_text": "...",
  "framing_text": "...",
  "observable_indicators": ["...", "...", "..."],
  "resolution_framing_text": "...",
  "synthesis_confidence": 0.0
}
```

Field routing (from the prompts doc):
- **Private output** (principal only): `liability_condition_text` + `asset_resolution_anchor_text`
- **Shareable output** (external-safe): `framing_text` + `observable_indicators` + `resolution_framing_text`

---

## Cascade files

All five require changes if this migration proceeds:

| File | Change |
|---|---|
| `engine/output_synthesis.py` | SynthesisResult dataclass, system prompt, user prompt structure, fallback behavior |
| `web/lib/types.ts` | `SynthesisResult` type fields (currently `private_synthesis` / `shareable_synthesis`) |
| `web/lib/output-renderer.ts` | `renderPrivateOutput()` and `renderShareableOutput()` draw from new field names |
| `web/components/PrivateOutput.tsx` | Prop rendering updated to new field names |
| `web/components/ShareableOutput.tsx` | Prop rendering updated to new field names |
| `tools/test_output_synthesis.py` | 25 existing tests rewritten; fallback behavior changes |

---

## Proposed implementation approach

### System prompt
Wire the system prompt from `PRV3_Output_Synthesis_Prompts_v1.0.docx` verbatim. It governs all five fields. Voice standard, banned words, format rules, and clinical boundary constraint are all specified there.

### Single LLM call
Generate all five fields in one call. The context object passed to the LLM:

```python
{
    "state_name":         str,   # e.g. "The Founder's Grip"
    "severity_tier":      str,   # Emerging | Entrenched | Endemic
    "resolution_family":  str,   # Commercial name — e.g. "Groundwork"
    "asset_score":        float,
    "liability_score":    float,
    "narrative_response": str,   # principal's free-text from narrative prompt
    "intake":             dict,  # org_size, industry, role, significant events
    "signal_map_context": str,   # for observable_indicators only
}
```

### Fallback behavior
On timeout (5s) or API failure, fall back to `resolution_families.py` static copy via `get_fallback_copy(commercial_name, severity_tier)`. The fallback `SynthesisResult` fields map as:
- `liability_condition_text` ← fallback copy string
- `asset_resolution_anchor_text` ← empty string (not available in static copy)
- `framing_text` ← fallback copy string (same)
- `observable_indicators` ← empty list
- `resolution_framing_text` ← fallback copy string (same)
- `is_fallback` = True

### TypeScript impact
`web/lib/types.ts` exports a synthesis type (currently not explicitly defined — `private_synthesis` and `shareable_synthesis` are used inline in `PrivateOutputPayload` and `ShareableOutputPayload`). The migration adds a `SynthesisFields` interface:

```typescript
export interface SynthesisFields {
  liability_condition_text:     string;
  asset_resolution_anchor_text: string;
  framing_text:                 string;
  observable_indicators:        string[];
  resolution_framing_text:      string;
  synthesis_confidence:         number;
  is_fallback:                  boolean;
}
```

`PrivateOutputPayload` and `ShareableOutputPayload` will reference relevant fields from this interface rather than holding flat strings.

---

## Questions for Gemini

1. **Fallback mapping:** Is the proposed fallback mapping (single string mapped to three output fields) acceptable? Or should `resolution_families.py` provide field-specific fallback strings instead of a single string per (name, tier)?

2. **Observable indicators fallback:** The prompts doc notes that `observable_indicators` "can fall back without significant loss." Should the fallback return an empty list, or should the signal map context be used to produce a static list when the LLM is unavailable?

3. **TypeScript boundary:** The proposed `SynthesisFields` interface in `types.ts` — should `PrivateOutputPayload` and `ShareableOutputPayload` each embed the relevant fields directly (flat), or reference a nested `synthesis` object? The current payload shapes are flat.

4. **Single vs. multi-call:** The prompts doc says "all five fields in one call." Confirm this is the right call structure given the 5-second timeout. If a single call exceeds the timeout, all five fields fall back. An alternative is priority ordering (liability_condition_text first, observable_indicators last) in a multi-call structure. Prompts doc priority order: liability_condition_text, resolution_framing_text, asset_resolution_anchor_text / framing_text (mid), observable_indicators (lowest). Does single-call with 5s timeout hold, or should we structure for graceful partial fallback?

5. **max_tokens:** Current setting is 400. Five fields, especially with observable_indicators as a list, may require more. What is the recommended max_tokens for this call structure?

---

## What Gemini should return

For each question: a specific recommendation, not a list of options.

If any of the cascade files have risks not identified above, flag them.

If the implementation approach has an architectural problem, name it and propose the correction before Claude Code executes.

---

*PRV3 Principal Brief governs. Pete decides. Claude Code executes after confirmation.*
