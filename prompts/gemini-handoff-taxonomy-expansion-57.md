# PRV3 Taxonomy Expansion 47 -> 57 — Gemini Architecture Review Request (Session 67)

## Context

Session 65 locked the taxonomy expansion decision via Gemini architecture review: 10 new
states added (47 -> 57), across Authority (+4), Attitude (+4), Aptitude (+1), Alliance (+1).
That review approved state names, dimension assignment, and disposition (why each is a
genuine new STATE and not a COLLAPSE into an existing one). It did not assign the
finer-grained per-state fields the engine actually requires to route and score these
states. This session (67) implemented the expansion end-to-end and authored those fields
as a first-pass draft, grounded in `research/seven-experiments/consolidation-mapping-trace.md`'s
own disposition rationale and analogy to the closest existing state in each dimension.

**This is a request for architecture review of that draft, not a report of a locked
decision.** Nothing described below has been treated as final. The code has been written
and the test suite runs against it (see Current Status), but Pete has not confirmed any of
it and no commit reflecting it should be treated as locked until this review returns.

## What was authored, and why it needed a decision

Three files require classification fields with no source-document basis for the 10 new
states (the original 47 states drew these from `PRV3_Question_Signal_Map.docx` and
`PRV3_State_Taxonomy_Profiles.docx` — no equivalent exists for the new 10):

1. **`engine/data/states.py`** — `signal_weight`, `cluster_id`, `liability_axes`,
   `asset_axes`, `severity_range`, `resolution_family` (legacy free-text field), and a
   hand-set 8-field `dimensional_vector` per state.
2. **`engine/resolution_families.py`** — which of the 4 live resolution families
   (developmental / structural / investigative / directional) each state routes to. This
   is the field that actually drives output routing today (TypeScript mirrors it).
3. **`web/data/taxonomy.ts`** — `signatureId`, clustering each state into one of the 5
   existing Signature groups (each with its own user-facing coexistence-interpretation
   copy).

A fourth file was found to need the same kind of entry during implementation, not
anticipated in the original file list:

4. **`engine/data/salience.py`** — every one of the 47 existing states has a
   `SALIENCE_PROFILES` weighted-cosine entry (100% coverage); leaving the new 10 without
   one would silently degrade them to unweighted cosine scoring, inconsistent with every
   other state.

## Naming collisions found during implementation

Two collisions surfaced that were not in Session 65's required-mitigation list (which
covered only Sequential Decision Blindness vs. Decision Blindness). Both are handled the
same way Session 65 handled that one — inline documentation cross-reference at the point
of definition — but neither has been independently reviewed:

- **Motivational Architecture Failure** — this exact name is the profiles-doc
  inferred-mapping source for the *existing locked state* `the_wrong_reward` (see
  `engine/data/states.py`'s own `# Inferred from profiles doc: Motivational Architecture
  Failure` comment on that entry). The trace file already argues the two are
  mechanistically distinct (Wrong Reward = rational optimization for the real, unstated
  incentive system; the new state = a clinical controlled/amotivated psychological
  condition). Please confirm that distinction holds and that reusing the name is
  acceptable.
- **Invisible Performance Management** — more serious: this is a **retired `state_id`**,
  not just a name echo. `states.py`'s header records `Rename applied:
  invisible_performance_management -> the_paper_tiger`, and `the_paper_tiger`'s own entry
  says `Renamed from clinical name: Invisible Performance Management (profiles doc #33)`.
  This was resolved years ago (`state_removal_final.md`, `state_removal_v3.md` — a
  45-vs-47 count question, settled at 47) — there is no live dict collision, since the old
  entry was fully removed. But it means the identifier is being reused for a genuinely
  different mechanism (documentation-failure vs. The Paper Tiger's active-concealment).
  Please confirm this is acceptable or recommend an alternate `state_id`.

## Draft classification table

| State | Dim | signal_weight | cluster_id | sev range | resolution_family (4-bucket) | signatureId |
|---|---|---|---|---|---|---|
| Compression Crisis | Authority | medium | — | Emerging-Entrenched | investigative | compounding_risks |
| Sequential Decision Blindness | Authority | high | — | Emerging-Entrenched | investigative | compounding_risks |
| Disparate Impact Architecture | Authority | high | — | Entrenched-Endemic | investigative | compounding_risks |
| Planning Authority Gap | Authority | low | — | Emerging-Entrenched | structural | leadership_bottleneck |
| Wellbeing Theater | Attitude | cluster | C-Culture (draft) | Emerging-Entrenched | directional | culture_erosion |
| Human Displacement Anxiety | Attitude | medium | — | Emerging-Entrenched | directional | stunted_growth |
| Motivational Architecture Failure | Attitude | medium | — | Entrenched-Endemic | directional | culture_erosion |
| Cultural Overtime | Attitude | medium | — | Emerging-Entrenched | investigative | culture_erosion |
| Invisible Performance Management | Aptitude | medium | — | Emerging-Entrenched | structural | compounding_risks |
| Distributed Culture Fragmentation | Alliance | medium | — | Emerging-Entrenched | directional | culture_erosion |

Full rationale (dimensional vectors, liability/asset axes, and the specific existing state
each was mirrored against) is in `engine/data/states.py`'s inline comments per entry —
every new entry is marked `# DRAFT — pending Gemini review`.

## Specific judgment calls worth a second look

1. **Wellbeing Theater's `cluster_id="C-Culture"`** — drafted because the source text
   self-describes as "a specific variant of Culture Drift." This adds a 4th member to a
   cluster mechanism (`CLUSTERS["C-Culture"]`) that drives `checkpoint.py`'s stress-test
   routing. Confirm or reject the cluster membership specifically, not just the
   `signatureId`.
2. **Distributed Culture Fragmentation's `signatureId="culture_erosion"`** — this is the
   first Alliance-dimension member of a signature whose other 8 members are all Attitude
   states. Signatures already cross dimensions elsewhere (Leadership Bottleneck mixes
   Aptitude/Authority/Alliance), so this isn't unprecedented, but it's a judgment call
   worth confirming rather than assuming.
3. **`states.py`'s legacy `resolution_family` field** (e.g. `"Roadmap"`, `"Intervention +
   Executive Counsel"`) — this field is known engine debt per the MOB (serializes
   pre-S32 service names, bypassed by the TypeScript output layer's own mapping). Draft
   values here follow the historical naming loosely for consistency but are lower-stakes
   than the resolution_families.py 4-bucket assignment, since nothing live reads this
   field today.

## Signature copy not touched

`stateIds` arrays in `web/data/taxonomy.ts` were updated to include the new states in
their assigned signatures, but the signature-level `description` and
`coexistenceInterpretation` prose (the user-facing copy describing what the cluster means)
was **not** rewritten to account for the new members. That's a copywriting pass, out of
scope for this session. Flagging in case a composition change (e.g., item 2 above) is
significant enough to warrant one.

## Current status (informational — test suite runs, not fully calibrated)

30 new test profiles were authored (3 per state) and wired into `calibration_runner.py`.
Current run: 152/172 passed. 3 of the 10 new states pass all 3 profiles outright
(Distributed Culture Fragmentation, Invisible Performance Management, Wellbeing Theater);
1 passes 2/3 (Compression Crisis); the remaining 6 fail on `cluster` (high_confidence) or
`prominence` (moderate/weak) criteria — the same category of gap the original 47 states
took roughly 13 sessions (S16-S29) of Monte Carlo calibration to close. No attempt was made
to force a pass by hand-tuning against un-reviewed classification choices — that would
waste effort if this review changes the underlying signal_weight/severity/axis
assignments first. Full calibration is appropriately a follow-up workstream once this
review lands.

## What's being asked of this review

1. Confirm or revise the classification table above (dimension is locked from Session 65;
   everything else here is open).
2. Confirm or reject the two naming-collision handling decisions.
3. Confirm or reject Wellbeing Theater's C-Culture cluster membership specifically.
4. Confirm or flag the Distributed Culture Fragmentation / culture_erosion cross-dimension
   signature assignment.
5. Anything else structurally unsound that a fresh read catches — this was authored by one
   party (Claude Code) without the second-look Gemini gave the original 47.
