# PRV3 Quarterly Step-Back — Part 2, Claude Code Independent Cold Assessment

**Date:** 2026-09-16
**Author:** Claude Code (terminal session, direct source only)
**Process:** Dual-sourced Quarterly Step-Back, locked 2026-08-23 (MOB Section 14). This is
the independent re-verification pass — produced cold, without reading any prior Claude.ai
assessment text, per Pete's explicit instruction. Reconciliation against the Claude.ai
version is a separate, later pass, not performed here.

**Correction carried in from Pete, applied throughout:** Loureiro is a case study
demonstrating the Principal Resolution methodology, not a completed paid engagement. It is
not treated as evidence of closed revenue or a proven price point anywhere below. Direct
repo-wide search (ripgrep, case-insensitive, all file types, `.docx` contents included via
zipfile extraction, full git commit-message history) found **zero references to "Loureiro"
anywhere in this repository** — no prompts/, documents/ (including the two most relevant
`.docx` files), tools/_mob.txt, CLAUDE.md, web/, engine/, or commit message. There is nothing
in-repo to correct; it exists only outside this codebase, presumably in Pete's own
conversation history with Claude.ai. Noted for completeness, not because a correction was
needed here.

---

## Part 1 — Ground-Truth Audit

### 1. Real transaction path — current state, confirmed via direct code/commit read

- `/engage` (`web/app/engage/page.tsx`) and `POST /api/engage/initiate`
  (`web/app/api/engage/initiate/route.ts`) are real, committed, deployed code — commit
  `5b9586f`, 2026-08-25.
- **No payment mechanism exists anywhere in this flow.** Explicit in both the code's own
  header comment and the UI copy itself: *"No payment is collected here."* The flow collects
  name + email only and sends a Dropbox Sign hosted `send_with_template` request.
- **Engagement agreement location:** `documents/PRV3_Engagement_Agreement_Draft_v1.0.docx`,
  committed to the repo 2026-08-26. Per `documents/linkedin-covenant-landscape.md` (read
  directly this session), it is marked in its own text **"working draft, not
  execution-ready,"** with attorney-review flags embedded directly in the document. It has
  not been reviewed by counsel — that review sits on an explicitly indefinite, unforced-hold
  gate (Decision Register, "Attorney review" row: *"No active timeline set with counsel...
  Pete's call — no forced check-in, Pete has explicitly chosen to leave this open-ended"*).
- **Dropbox Sign provisioning status: unconfirmed, not found either way.** The route reads
  `DROPBOX_SIGN_API_KEY` and `DROPBOX_SIGN_TEMPLATE_ID` from environment variables. Unlike
  every other credential in this project's history — `UPSTASH_REDIS_REST_URL/TOKEN`,
  `ANTHROPIC_API_KEY`, `ENGINE_SECRET` — which each have an explicit MOB record of Pete
  confirming provisioning via `vercel env pull`/`vercel env ls`, **no equivalent confirmation
  exists anywhere in ~5,300 lines of MOB history for the Dropbox Sign credentials.** I did not
  attempt to check this via the Vercel MCP (no env-var-listing tool is exposed to me, and I
  will not decrypt or probe live credentials), and I did not hit the live endpoint to test it
  (a real POST would either fail loudly against unprovisioned credentials or, worse, actually
  dispatch a real signature request in Production — `testMode` is hardcoded `false` whenever
  `VERCEL_ENV === "production"`, meaning a live Production send is **not** sandboxed by
  default). This is a genuine unknown, not a confirmed gap — but it is also not confirmed
  working, and nothing in the record shows it was ever live-tested end-to-end.
- **No live production round-trip test exists for this route**, as far as MOB search can
  determine — notable because the project's own standing rule (CLAUDE.md, locked
  2026-08-27, two days *after* this route shipped) now requires exactly that kind of check
  for any route-registration-affecting change, following a prior production outage caused by
  the same gap (the Narrative Modulation `vercel.json` incident). This route predates that
  rule and, on current evidence, was never subjected to it retroactively.

**Bottom line:** the code for a transaction path exists and is deployed, but "shipped" in the
MOB's language means "committed and merged," not "confirmed working against real credentials
in front of a real signer." That distinction matters and the record doesn't resolve it either
way.

### 2. Actual closed-revenue evidence for Principal Resolution — confirmed absent

Direct search across the full MOB session log (Sessions 3 through the current v4.308, roughly
5,300 lines), git commit-message history (`git log --all -i --grep`), and the documents/
directory for "invoice," "paid engagement," "signed client," "first client," "closed deal,"
or "revenue" in a transactional sense: **no hits describing an actual closed, paid Principal
Resolution engagement.** The only "signed agreement" artifact in the repo is the
engagement-agreement *template*, explicitly marked not execution-ready, with no named
counterparty. No invoice exists anywhere in this repo. **There is no evidence of any closed
Principal Resolution revenue, full stop — not "not yet found," genuinely absent from every
source checked.**

### 3. Calibration baseline — 171/175 confirmed, staleness traced

- **Live run, this session, this exact investigation:** `python tools/calibration_runner.py`
  → `RESULT: 171/175 passed (4 failed)`. Confirmed fresh, not carried forward from earlier in
  this session's other work (though it also matched those runs).
- **The `166/175` figure's staleness traced to source, not assumed:** `tools/_mob.txt:1506`,
  dated language from the 2026-08-24 rewrite of Section 13b (*"Calibration status as of
  session close: unchanged since the 2026-08-24 rewrite... 166/175"*) — never refreshed after
  three subsequent, individually-documented calibration improvements: `the_paper_tiger`
  `primary_dimension` fix (166→169, `session-handoff-v4.297.md`), a second batch fix
  (169→170, same file), and the IPM/`the_founders_grip` vector-differentiation fix, commit
  `09ed822`, 2026-09-14 (170→171, explicitly logged as "EXP-IPM-02 fix" in
  `session-handoff-v4.298.md`). **171/175 was already the correct documented baseline before
  this session's rename and pricing work began** — the 166 figure is a live, currently-stale
  line still sitting in the MOB today (Section 13b), a genuine open correction, not a
  hypothetical one.

### 4. Legal/covenant risk material — confirmed via direct read of `linkedin-covenant-landscape.md`

Read the full document directly this session (not summarized secondhand). Confirms, in the
document's own words:
- **Restricted Period is currently active, not a future contingency:** *"Pete is currently
  employed at OneDigital (Digital Insurance LLC)... every restrictive covenant in the
  agreement (Sections 2–6, 12, 13) is currently active."*
- **Sections 2, 8, 9 are live during employment specifically**, not deferred to
  post-employment: Section 2 (confidential information) — *"a current, active restriction...
  during employment"*; Section 8 (fiduciary duty) — *"a live obligation that exists
  independent of how 'solicit' gets defined"*; Section 9 (IP assignment) — *"also live now,
  not deferred."*
- **LinkedIn campaign structure confirmed: 19 weeks, 57 posts**, drawing from the existing
  `/book` content library plus, per the document, *"a handful of the seven-experiments essays
  as 'Foundation' pillar teaser/launch pairs."*
- **No end date confirmed, explicitly flagged as the higher-stakes reading:** *"No termination
  date planned, confirmed... there's no natural endpoint... the fiduciary-duty question shifts
  from 'is a LinkedIn post a problem' to 'is running a sustained, long-term BD campaign for a
  second practice, indefinitely, while actively employed in an HR consulting role, a
  duty-of-loyalty question.'"*
- The document itself is explicit that it is **not legal advice** and that a full Section 7
  (non-disparagement) clearance would require reading all 57 posts' actual text, not just
  titles — that full-text pass has not happened.

### 5. The seven experiment files — confirmed internal-only, not yet client-facing

`research/seven-experiments/README.md` states its own status plainly: *"Raw research inputs —
not finished public-facing content"* and *"upstream of the Hammer Index citations and the
47-state taxonomy, not downstream of them."* Cross-checked against
`research/seven-experiments/consolidation-mapping-trace.md` (a large, detailed internal
document): all seven experiments' findings were consumed as taxonomy-validation input — used
to confirm, rename, collapse, or root-classify roughly 80 candidate organizational patterns
against the locked 47→58-state taxonomy. This is real, substantive internal work, not idle
research. **No direct grep hit for the seven-experiments filenames or "experiment-N" pattern
anywhere in `web/content/book/`** — their content has not been directly published as
client-facing pieces. The only place they are slated for *any* external use is the LinkedIn
campaign's "Foundation" pillar teaser/launch pairs (per item 4 above) — a planned, not-yet-live
use, gated behind the same indefinitely-parked attorney review.

### 6. Other stale claims surfaced on this cold read

- **`tools/_mob.txt:1506`** — the `166/175` calibration figure (see item 3). Live and stale
  right now, not historical.
- **`CLAUDE.md`'s own Key References table** — lists `MOB version | v4.303`. The actual
  current MOB version, confirmed by reading the file's own header, is **v4.308**. This is a
  second, independent instance of the same failure mode as item 3: a cross-reference number
  that stopped being updated at some point in the last several sessions. Worth naming as a
  pattern, not a one-off — two live staleness gaps found in one cold read, both in the
  "small cross-reference number nobody re-checks" category, is a signal the closeout
  protocol's cross-reference-update step is not catching everything it's meant to.
- No other new staleness surfaced beyond what this session's own earlier work already caught
  and corrected (the OH `legal_tail_risk_exposure` test assertions, the
  `_oh_is_small_employer()` docstring) — those are process, not fresh findings for this
  step-back.

---

## Part 2 — Viability Assessment (project health, business viability, path to market)

**Engine and taxonomy: genuinely mature, no real technical blocker to diagnosis quality.**
58 locked states, 171/175 calibration (a real, live-measured number as of tonight, not a
carried-forward claim), full test coverage across 11 Python suites plus a 99-test frontend
suite, all green. Legal/compliance pricing (item 9 this session, OH R.C. 2315.21) shows the
engine can absorb genuinely researched, jurisdiction-specific financial modeling without
destabilizing the rest of the system — the calibration suite was untouched by that entire
body of work, confirmed empirically via git-stash A/B testing earlier this session. This is a
technically sound instrument. That is not the bottleneck.

**The bottleneck is commercial, not technical, and it is a wide gap.** Zero closed revenue
(item 2). A transaction path that exists in code but has no confirmed working payment-adjacent
integration and no confirmed live test (item 1). A legal review gate for both the LinkedIn
campaign and the engagement agreement that has sat open-ended for an extended period by Pete's
own explicit choice, not because it's blocked externally — meaning the delay is a standing
decision, not a stalled process, but its effect on time-to-market is the same either way. The
project has built a diagnostic instrument and a body of substantive content (87 published
`/book` pieces, per the MOB's own go-live record) with no confirmed mechanism yet proven to
turn any of it into a paying engagement.

**Progress on the path to market is real but entirely pre-revenue.** The sequence that would
need to close — public content live (done), a way for a prospect to reach out (done, `/ask`
mailto and the diagnostic itself), a transaction mechanism to formalize an engagement (built,
unconfirmed-working), a reviewed and executable engagement agreement (drafted,
attorney-review-gated, no forced timeline), a legally cleared promotional channel to drive
prospects at scale (drafted at 19 weeks/57 posts, blocked on the same attorney-review gate,
now compounded by the fact that gate sits inside a currently-active non-compete/fiduciary-duty
situation) — has a real, working link at nearly every stage except the two gated on outside
counsel, and those two gates are exactly the ones standing between "instrument exists" and
"instrument can be sold."

**Project health, structurally:** the session-log discipline here is unusually strong —
staleness gets caught and corrected repeatedly, not just once (this step-back itself is the
fourth or fifth documented instance of a stale-claim sweep in this project's history). That
is a real strength for a solo-operator project without a second reviewer in the loop day to
day. But it also means the *same kind of small cross-reference drift* keeps recurring (item 6
above is not the first instance) — the pattern is caught reliably, not prevented.

---

## Part 3 — SWOT (incorporating opportunities, blind spots, risk profile)

### Strengths
- Technically mature, well-tested diagnostic engine (58 states, 171/175 calibration, full
  test coverage, verified this session via live re-run, not carried forward).
- Genuinely researched legal/compliance pricing layer (item 9) — real statutory citations,
  Gemini-reviewed twice, independently re-verified, not templated boilerplate.
- Strong internal verification discipline — this project catches its own stale claims
  repeatedly and has a standing process (the Quarterly Step-Back itself) built specifically
  to keep doing so.
- Substantial published content (87 `/book` pieces) and a well-sourced internal research base
  (the seven experiments) available to draw from for future public content.

### Weaknesses
- **Zero closed revenue, confirmed absent, not just unconfirmed** — the project has no proof
  point yet that anyone will pay for this instrument at any price.
- Transaction path exists in code only; genuinely unknown whether it works end-to-end against
  real credentials, and it predates the project's own rule requiring that kind of check.
- Two of the highest-leverage go-to-market levers (the LinkedIn campaign, the engagement
  agreement) are both gated behind the same open-ended attorney review, with no forced
  check-in — a real, chosen delay, but one with compounding cost the longer it sits, given the
  time-value of the covenant situation below.
- Solo-operator structure: the "Outside Human Gap" the project's own CLAUDE.md already names
  (no second human reviewing public-reception judgment before irreversible actions) remains
  entirely unaddressed as of this pass.

### Opportunities
- The seven-experiments corpus and 87 published pieces are a real, underused asset — genuine
  research grounding that most solo-practitioner diagnostic tools won't have, not yet
  leveraged into the LinkedIn campaign or any paid-acquisition channel.
- The legal/compliance pricing work (item 9) suggests a path to a defensible, jurisdiction-
  specific "dollar exposure" angle that's differentiated from generic organizational-health
  tools — this is real, hard-to-replicate work, not generic content.
- A pilot mechanism already exists in the governance model (Tier 4's "share with 2-3 trusted
  people before public commitment") and has not yet been used — a low-cost way to get real
  signal on willingness-to-pay before the attorney-review gate even needs to open, since a
  private pilot with people Pete already knows doesn't obviously require the same LinkedIn-
  scale covenant analysis.

### Threats / risk profile
- **The OneDigital covenant situation is the single highest-stakes open item in the project,**
  confirmed directly this session, not inferred: fiduciary duty, confidential-information, and
  IP-assignment obligations are all live *right now*, not future contingencies, for as long as
  Pete remains employed there. Every week the LinkedIn campaign and public BD activity continue
  to build without a resolved legal read is a week of exposure under Section 8 specifically,
  which the document itself notes doesn't depend on how "solicit" gets defined — it's a duty-
  of-loyalty question independent of any specific covenant technicality.
- Reputational risk if the transaction path is ever used in its current, never-live-tested
  state and fails at the exact moment a real prospect is trying to sign — this is the kind of
  gap the project's own standing rule exists to prevent, and this route may have slipped
  through before that rule existed.
- No named second human reviewing public-facing judgment calls before irreversible actions
  (the already-documented Outside Human Gap) — compounds both risks above, since the same
  person deciding legal-exposure tradeoffs is also the person whose income depends on the
  outcome.

---

## Part 4 — Forward Recommendations (Claude Code's own, not imported from any prior framing)

1. **Resolve the Dropbox Sign provisioning question before treating the transaction path as
   real.** A one-time, low-risk check (confirm `DROPBOX_SIGN_API_KEY`/`DROPBOX_SIGN_TEMPLATE_ID`
   exist in Vercel via `vercel env ls`, no value decryption needed) closes a genuine unknown
   cheaply. If they're not provisioned, this project's headline claim of "shipped, live" for
   Real Transaction Path Phase 1 is materially overstated.
2. **Treat the attorney-review gate as the actual critical path, not a background item.** Two
   of the highest-leverage levers in this whole project are both blocked on it, and the
   covenant situation makes the cost of leaving it open-ended asymmetric — it doesn't just
   delay revenue, it extends a live legal-exposure window every week it stays open. This
   doesn't mean rushing counsel; it means Pete deciding consciously whether "no forced
   check-in" is still the right call given what this pass confirmed about Sections 2/8/9's
   current, active status.
3. **Use the pilot mechanism before the attorney-review gate opens**, not after. A private
   share with 2-3 trusted people tests willingness-to-pay and public reception without needing
   the LinkedIn-scale legal clearance — genuine signal, near-zero exposure, already defined in
   this project's own governance model and unused so far.
4. **Fix the two live staleness items found this pass** at the next closeout: the `166/175`
   line in Section 13b, and CLAUDE.md's `v4.303` cross-reference. Small, but both are exactly
   the kind of small-number drift this project has been burned by before.
5. **Do not read the absence of closed revenue as a technical failure** — the engine and
   content are genuinely ready. The gap is entirely in the commercial/legal sequencing above,
   and closing it doesn't require more engine work.

---

## Part 5 — Comparison Note

Not performed in this pass, per Pete's explicit instruction. This document is the independent,
cold, source-verified half of the dual-sourced process. Reconciliation against the Claude.ai
assessment — where the two agree, where they diverge, and the root cause of any divergence —
is a separate step to be run after both assessments exist, per the standing 2026-08-23 format.
