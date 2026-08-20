# Visualize Your Data — Layer 1 Build Spec (VII.1 schema addition)

Status: build spec, verified against real code, not yet implemented.
Precedes: Layers 2 (wire plumbing) and 3 (UI), see
prompts/visualize-your-data-build-scope.md.
Verification lineage: prompts/visualize-your-data-build-scope.md's original
Gemini review had 4 fabricated/mischaracterized citations, corrected in
tools/_mob.txt Section 13a (commit fd80709). This round's placement review
(4 further claims) verified clean against real files — see chat record,
commit history for this session.

## Change

`severity_obj` (engine/contract.py, built inside `assemble_output()`,
line ~434) gains one new key, `by_state`:

```python
severity_obj = {
    "tier":        lead_severity_tier,
    "score":       round(lead_severity_score_0_100, 2),
    "anchor_text": SEVERITY_TIER_DESCRIPTIONS.get(lead_severity_tier, ""),
    "inputs": { ... },  # unchanged
    "by_state": [
        {
            "state_id":     state_id,
            "tier":         entry.tier,
            "score_0_100":  entry.score_0_100,
        }
        for state_id, entry in sev.state_severity.items()
        if state_id in {s["state_id"] for s in identified_states}
    ],
}
```

Pure exposure of `sev.state_severity` (already correct, computed since
Checkpoint 1, verified end-to-end since Checkpoint 4/5), filtered to the
states already in `identified_states` — no new computation, matches the
row-based/qualifying-states-only design already settled in the concept doc.

## Why nested inside `severity`, not top-level

Confirmed this round: `_TOP_LEVEL_SCHEMA` (engine/contract.py) types only
the 15 top-level keys and declares no nested shape for `"severity"` — that's
governed separately by `_SEVERITY_FIELDS`. `validate_schema()` (previously
misnamed `validate_output()` in the first review round) only checks
required-field presence in both cases, never rejects extra keys, so this
placement needs no schema-constant changes to pass validation.

The concrete reason to nest rather than add a new top-level key:
`tools/test_contract.py:178` hardcodes `"Exactly 16 top-level fields"`
(`len(output) == 16`). Nesting inside `severity_obj` leaves `len(output)`
at 16 — confirmed via direct search, no count or key-set assertion exists
on the `severity` sub-object specifically in `tools/test_contract.py`.
Adding `by_state` top-level instead would require bumping that assertion
to 17; nesting avoids the need entirely.

## ENGINE_VERSION

Bump `engine/contract.py:50` from `"0.2.0"` to `"0.2.1"` — confirmed
current value at HEAD (fd80709) before this spec was written. A minor
version bump for a purely additive field, consistent with Section VII's
immutability rule protecting existing field semantics, not forbidding new
ones (the reasoning already assessed as sound in the first Gemini review
round, Q1).

## Verified unaffected

- `tools/test_contract.py:178` (`len(output) == 16`) — confirmed
  unaffected, see above.
- `_TOP_LEVEL_SCHEMA`, `_PRIVATE_OUTPUT_FIELDS` — untouched; `by_state`
  lives inside `_SEVERITY_FIELDS`'s dict, not a new top-level or
  private_output key.
- `PrivateOutputBlock` (engine/output.py:261) — untouched. Its
  `severity_tier`/`severity_anchor_text` fields are a separate, existing
  mechanism (per-state, used for `build_private_block()`'s own per-state
  block) and are not surfaced in `private_output`'s wire dict today
  (confirmed: `private_output` only reads `priv.state_name`, for
  `opening_text`) — this change doesn't touch that path at all.

## Not yet done

- Full 172(+3)-profile calibration regression re-run against this change
  (must stay byte-identical — purely additive field, no ranking logic
  touched).
- New engine test coverage confirming `by_state` values match
  `state_severity` exactly, single-state and multi-state profiles.
- Layers 2 (wire plumbing) and 3 (PrivateOutput.tsx UI) — separate spec,
  not started.

## Sequencing

This is a locked-contract (Section VII.1) change. Per CLAUDE.md's Tier 1
mechanism: dry-run patch script -> Pete confirms -> commit. Not yet built.
