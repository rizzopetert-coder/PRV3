# PRV3 Quarterly Step-Back — Reconciliation

**Date:** 2026-09-16
**Process:** Final step of the dual-sourced Quarterly Step-Back, locked 2026-08-23 (MOB
Section 14). Reconciles (1) Claude.ai's initial project evaluation against (2) Claude Code's
independent, cold, source-verified pass
(`prompts/prv3-quarterly-step-back-2026-09-16-cc-independent.md`), per the standing format:
discrepancies resolved against live source, root cause named, reconciled picture — not either
assessment alone — drives the work plan.

---

## Where the two assessments agreed

Both passes landed on the same core technical read: the engine and taxonomy are mature and
not the project's bottleneck. 58 locked states, a live-verified 171/175 calibration baseline,
full test coverage, and the newly-researched legal/compliance pricing layer (Ohio R.C.
2315.21, this session) all point the same direction — this is a technically sound instrument,
and neither assessment found reason to treat the engine side as an open risk. Both also
converged on the broader shape of the gap: substantial published content and research
groundwork exist (87 `/book` pieces, the seven-experiments corpus), but the commercial path
from that groundwork to an actual paying engagement remains unproven. That convergence is
what drives the reconciled bottom line below.

---

## The corrected finding: Loureiro and Principal Resolution revenue

**Claude.ai's initial draft incorrectly treated Loureiro as a completed, paid Principal
Resolution engagement and cited a $22–25K figure from it as a proven PR pricing data point.**
This was wrong. Per Pete's direct correction, carried into Claude Code's independent pass as
an explicit instruction, and independently confirmed by that pass's own source search:
Loureiro is a case study demonstrating the Principal Resolution methodology, not a closed
client engagement. It does not appear anywhere in this repository at all — not in prompts/,
documents/ (including a direct `.docx`-content search of the two most relevant files), the
MOB, CLAUDE.md, or git commit history — meaning it exists entirely outside this codebase, most
likely only in Pete's own prior conversation history with Claude.ai. That conversational
origin is almost certainly how the error entered the Claude.ai draft: a conversation-history-
based assessment repeating a framing it was never source-checked against, the same failure
mode the dual-sourced process was created to catch (see the 2026-08-23 precedent named in
CLAUDE.md's own Quarterly Step-Back section).

**Stated plainly, for the record: zero closed Principal Resolution revenue exists.** Not
"unconfirmed" — a direct search of the full MOB session log (Sessions 3 through v4.308), the
complete git commit-message history, and documents/ for any invoice, signed client agreement,
paid engagement, or delivered-and-paid deliverable found nothing. The only "signed agreement"
artifact in the repo is the engagement-agreement template itself, explicitly marked in its own
text as a working draft, not execution-ready, with no counterparty named.

**The $22–25K figure should not be used as a Principal Resolution pricing anchor going
forward.** It is a number associated with a demonstration case study, not a transaction this
practice has ever actually closed. Any future pricing discussion should treat PR's real price
point as genuinely unestablished, not "known but unconfirmed."

---

## Two net-new findings the Claude.ai draft missed entirely

Both surfaced only in Claude Code's direct-source pass, since they require reading actual code
and cross-referencing it against the MOB's own credential-provisioning history — not something
a conversation-history-based draft would have reason to check.

1. **The `/engage` transaction path's Dropbox Sign provisioning is unconfirmed, and
   `testMode` defaults to live-fire in Production.** `web/app/api/engage/initiate/route.ts`
   reads `DROPBOX_SIGN_API_KEY`/`DROPBOX_SIGN_TEMPLATE_ID` from environment variables with no
   MOB record anywhere confirming those were ever provisioned in Vercel — a real gap, since
   every other credential this project uses (Redis, Anthropic, the engine secret) has an
   explicit provisioning-confirmation entry in the MOB and this one does not. Compounding it:
   `testMode = process.env.VERCEL_ENV !== "production"` means a real Production request is
   **not** sandboxed by default — if the credentials are provisioned but this route was never
   live-tested (no evidence of a live round-trip test exists either), the first real signer to
   use it would be the first real-world test of the whole path.
2. **CLAUDE.md's own Key References table was stale**, listing `MOB version | v4.303` against
   an actual current version of v4.308 at the time of the independent pass — a live
   cross-reference drift, not a historical one, sitting in the governing document itself.

Both are fixed as part of this reconciliation's closeout (see MOB Section 16 entry for
specifics); the Dropbox Sign provisioning question itself is **not** resolved here — it's
carried forward as an open recommendation below, Pete's call to check.

---

## Reconciled bottom line

**The engine and content are mature. Commercial viability is entirely unproven.** Two of the
highest-leverage levers available to close that gap — the LinkedIn campaign (19 weeks, 57
posts, ready to go) and the engagement agreement (drafted, ready for review) — are both gated
on a single open-ended attorney review that has no forced check-in. That review sits directly
on top of a currently-active OneDigital covenant situation: Sections 2 (confidential
information), 8 (fiduciary duty), and 9 (IP assignment) are all live obligations right now,
not future contingencies, for as long as Pete remains employed there, confirmed by direct read
of `documents/linkedin-covenant-landscape.md`. This is not a technology problem and closing it
does not require more engine work — it requires a legal-review decision and, separately, a
real test of whether anyone will pay.

---

## Leading near-term recommendation

**Use the Tier 4 pilot mechanism (share with 2-3 trusted people) before the attorney-review
gate opens, not after.** This is the single highest-leverage next move available: it tests
real willingness-to-pay and public reception at near-zero exposure, using a channel this
project's own governance model already defines but has never actually used, and it doesn't
require the LinkedIn-scale legal clearance the campaign itself needs. It can start closing the
"zero proven commercial viability" gap immediately, independent of when the attorney review
resolves.

The remaining four recommendations from Claude Code's independent pass stand as secondary,
in this order: (2) resolve the Dropbox Sign provisioning question directly (a one-time,
low-risk `vercel env ls` check, no value decryption needed) before treating the transaction
path as real; (3) treat the attorney-review gate as the actual critical path given the
covenant situation's active status, not a background item Pete can leave open-ended
indefinitely without cost; (4) the two staleness fixes, now closed as part of this
reconciliation's own closeout; (5) do not read the revenue gap as a technical failure — it
isn't one.

None of the above — the attorney-review gate, the Dropbox Sign check, or the pilot-mechanism
share itself — is acted on in this reconciliation. All three remain open, Pete's calls, logged
here as recommendations only.
