# PRV3 Quarterly Step-Back #4 — Claude Code Independent Cold Assessment

**Date:** 2026-09-19
**Author:** Claude Code (terminal session, direct source only)
**Process:** Dual-sourced Quarterly Step-Back, locked 2026-08-23 (MOB Section 14). This is
the independent re-verification pass — produced cold, without reading any prior Claude.ai
assessment text, per Pete's explicit instruction. Reconciliation against the Claude.ai
version is a separate, later pass, not performed here (Part 5, below).

---

## Part 1 — Ground-Truth Audit

### 1. Calibration baseline — 171/175 confirmed, live, this pass

`python tools/calibration_runner.py` → `RESULT: 171/175 passed (4 failed)`,
`SEVERITY: 175/175 applicable profiles match expected per-state tier`. Run fresh for this
step-back, not carried forward from this session's own earlier work on the friction tax
ledger (though it matches those runs too, as expected — every change since the last
step-back was additive/display-layer, none touched calibration inputs). No drift from the
171/175 figure Step-Back #3 (2026-09-16) confirmed and traced to source.

### 2. Commit history since the last step-back (2026-09-16) — 26 commits, all accounted for

`git log --since="2026-09-16" --oneline` returns 26 commits. All fall into three groups,
all already logged in Section 16 at the time they landed (no undocumented work found):

- **Display/contract bug fixes, each root-caused before any code change:** the
  `legal_tail_risk_exposure` low===high display bug (`37047dc`, `1c65bdf`), the
  `signal_map_context`/Trajectory `option_ids` silent-failure bug (`ce4c67f`, `7ca6006`).
- **The friction tax ledger build plus its org_type prerequisite fix** (`76c0690` through
  `0c68722`, 11 commits) — per-condition risk/dollar/top-contributing-answers ledger,
  Gemini-cleared across two rounds, plus the org_type threading fix that made
  `dollar_exposure` non-null for real Path 1 sessions for the first time.
- **Documentation-only commits:** two new planning docs (`ee0c3d7` — the "ALL DATA IS
  USEFUL" candidate principle and the asset-integration-into-resolution scope file), and
  five MOB-version-cross-reference bump commits riding alongside the above.

No commit in this range touches `vercel.json`, calibration targets, or taxonomy data —
consistent with the fresh 171/175 result above.

### 3. `tools/_mob.txt` / `CLAUDE.md` cross-reference — **no drift found this pass**

`tools/_mob.txt`'s own header: `MOB v4.314`. `CLAUDE.md`'s Key References table: `MOB
version | v4.314`. **These match exactly.** This is a genuine change from the pattern the
last two step-backs both found (Step-Back #3 found `CLAUDE.md` three versions stale at
`v4.303` against an actual `v4.308`; the session immediately after that found it stale
again at `v4.310` against `v4.311`, within the same day). The discipline of bumping both
files in the same commit — which this session did consistently across all five version
bumps in the range above — appears to be holding right now. Worth naming as a positive
finding, not just an absence of a negative one: this is the first of the (at least) three
dual-sourced step-backs run so far to find this specific cross-reference clean.

### 4. Commercial viability — zero closed revenue, independently re-confirmed, not assumed

Fresh repo-wide search this pass (`grep -rli` for "invoice," "paid engagement," "signed
client," "closed deal," "first client" across `.md`/`.py`/`.ts`/`.tsx`), not a re-read of
the prior step-back's conclusion:

- Every hit found is a **prior assessment document stating the absence of revenue**, not
  evidence of any — `session-handoff-v4.309.md` ("Loureiro is a case study, not a closed
  deal"), `session-handoff-v4.280.md` ("zero mentions of any real signed client anywhere in
  tracked MOB history"), `prv3-comprehensive-assessment-cc.md` ("No automated path from
  diagnostic completion to a signed, paid engagement").
- `documents/` directory contents checked directly (`ls`): the engagement agreement is
  still `PRV3_Engagement_Agreement_Draft_v1.0.docx` — still a draft, no executed version,
  no new document added since the last check.
- **Zero closed Principal Resolution revenue still holds, confirmed fresh, not carried
  forward from Step-Back #3's finding.**

**Dropbox Sign provisioning — still unconfirmed, and now confirmed unconfirmable from
this session specifically, not just "not attempted."** Step-Back #3 noted no env-var-listing
tool was exposed to that session. This session has live Vercel MCP access and attempted
`filter_project_envs` (name/metadata only, no `decrypt` flag — consistent with this
project's standing rule against handling credential values) against `prj_j8f7V51...`
(`prv-3`) directly. **Result: `403 Forbidden — "You don't have permission to list the
project environment variable."`** This is a real, informative negative: the connected
credential is scoped without env-var-list permission. The open question from Step-Back #3
(is `DROPBOX_SIGN_API_KEY`/`DROPBOX_SIGN_TEMPLATE_ID` actually provisioned) remains exactly
as open as it was, now for a confirmed permissions reason rather than an absent capability.

**No change to the transaction path or attorney-review-gate status** since Step-Back #3 —
`tools/_mob.txt` search confirms no new Section 13a/16 entries touching Real Transaction
Path Phase 2, pricing/checkout display, or the attorney-review gate in the intervening
window. Both remain exactly where Step-Back #3 left them: Phase 1 shipped and functioning,
everything else indefinitely parked, Pete's explicit and unchanged decision.

### 5. The Vercel "10GB storage" notification — investigated directly, partially resolved

**No record of the originating notification found anywhere in `tools/_mob.txt`, and no
"10GB" figure appears anywhere in this repository.** This is a real gap, not a non-finding:
per this project's own standing rule ("decisions don't stay in conversational context"),
a real infrastructure alert should have been logged the way the 2026-09-05 storage incident
was (a full, detailed Section 16 entry) — this one apparently wasn't, so I cannot confirm
from written record what resource it named, when it fired, or what its exact wording was.

**What I could and did check directly, live, this pass, via the Vercel MCP:**

- **Projects:** exactly two — `prv-3` and `prv-2`. `principal-resolution` remains
  permanently deleted (confirmed via `list_projects`), consistent with the 2026-09-05
  cleanup record. No new or unexpected project exists that could be silently consuming
  storage outside what this MOB already tracks.
- **Deployment counts — the specific problem from 2026-09-05, checked fresh:** `prv-3`: 11
  deployments. `prv-2`: 11 deployments. Both are far below the 324/33 counts that triggered
  the original storage-limit incident, and consistent with the 15/11 counts that cleanup
  left behind — **the September 5 retention-policy fix is holding, and deployment-history
  storage is not, on this evidence, the cause of a new alert.**
- **Billing plan:** `list_billing_charges` (FOCUS-format usage billing) returned
  `404 Plan not found` for this team — this account is not on a metered/usage-billed plan,
  consistent with the Hobby (free) tier already established in this project's history.
  Vercel's own Hobby-tier storage notifications are typically a fixed free-allowance
  warning, not a billing-driven one, which is consistent with a "10GB" figure appearing
  with no corresponding charge.
- **Native Vercel storage (Blob/KV/Postgres):** no store ID is recorded anywhere in this
  repo or MOB, and I have no "list stores for this project" capability in my current
  toolset (only a get-by-ID lookup) — I could not find any Vercel-native storage product
  connected to `prv-3`. This project's only confirmed persistent storage is **Upstash
  Redis**, a separate third-party marketplace integration (session storage,
  `UPSTASH_REDIS_REST_URL`/`TOKEN`) with its own, independently-billed free-tier cap — not
  a Vercel-native "storage" resource, and not something a generic Vercel-branded "10GB"
  notification would typically be measuring.
- **`get_project` on `prv-3` surfaced one incidental, unexplained data point, flagged but
  not investigated further this pass** (out of scope for a storage question, noted so it
  isn't lost): the project's own `framework` field reports `"fastapi"`, not a Next.js
  preset — plausibly reflects the co-deployed Python FastAPI engine backend
  (`api/engine.py`) rather than a misconfiguration, but not confirmed either way here.

**Characterization, not a resolution:** based on what's actually checkable from this
session, the "10GB" notification is unlikely to be about deployment-history storage (fixed,
holding, verified fresh above) or Vercel-native Blob/KV/Postgres (none found attached).
The two most plausible remaining explanations are (a) a generic Hobby-plan account-level
storage summary that doesn't reflect an active problem, or (b) something scoped to a part
of Pete's Vercel account this session's credentials don't have visibility into. **This is
not fully resolved** — the fastest actual close is Pete pasting the notification's exact
text/screenshot, which would let a future session confirm the named resource directly
rather than continuing to triangulate around it.

### 6. Loose end from earlier this session, status unchanged

`gh` CLI remains not installed on this machine (`gh: command not found`, checked fresh this
pass) — flagged twice already this session (Startup Status Report, and the Step 0 bug-fix
report). Pete has not yet run the suggested `winget install --id GitHub.cli -e`. No new
information, just confirming the loose end is still open, not silently dropped.

---

## Part 2 — Viability Assessment

**Engine and taxonomy: still genuinely mature, and now with a real, shipped example of
absorbing a second major feature (the friction tax ledger) without calibration drift.**
58 locked states, 171/175 calibration (confirmed fresh this pass, not carried forward),
full test coverage across 11 Python suites (all green) plus a passing frontend suite. Since
Step-Back #3, this project shipped a genuinely new, Gemini-gated engine feature (the
per-condition friction tax ledger) and fixed two real silent-failure bugs (the legal
exposure display bug, the `signal_map_context`/Trajectory `option_ids` bug) — all three
verified with fresh calibration re-runs at each step, all confirmed 171/175 exact, zero
drift. This is direct, repeated evidence the engine can take on real new work without
destabilizing, not just a claim.

**The commercial bottleneck is unchanged, not narrowed, since Step-Back #3.** Zero closed
revenue (re-confirmed fresh, item 4 above). The Dropbox Sign provisioning question is
exactly as open as it was three days ago, now confirmed unconfirmable from this session's
own credentials rather than simply unattempted. The attorney-review gate has had zero
movement. **Nothing in the last three days of work — real and substantial as it was —
touched the commercial path at all.** All of it was engine/UI quality work (the ledger,
two bug fixes) plus process documentation (the two new planning docs). That is not a
criticism of the work itself, which was well-executed and independently verified at each
stage — it is a direct observation that the gap Step-Back #3 named as the actual
bottleneck has had zero net movement in either direction this cycle.

**One new, real process win this cycle: the MOB/CLAUDE.md cross-reference drift that
recurred across the two prior step-backs did not recur this time** (item 3 above). Small,
but it's the specific failure mode Step-Back #3 called out as a pattern, not a one-off —
worth tracking whether it holds across the next cycle too before calling it fixed for good.

**The newly-surfaced silent-failure bugs (legal exposure display, `signal_map_context`/
Trajectory) are worth naming as a pattern in their own right, independent of the "ALL DATA
IS USEFUL" candidate principle this session also produced** (see that file for the full
argument): both bugs were real, live, affecting every relevant production session, and
both were caught only because someone was building something new that happened to expose
them — not by any standing check. That is a real, repeated shape (also true of the
org_type gap), not a coincidence, and it's the strongest evidence yet for whatever
verification discipline the candidate principle's Provisional Hold question ultimately
resolves to.

---

## Part 3 — SWOT

### Strengths
- Technically mature engine, now with three consecutive successful feature/fix cycles
  since the last step-back, each independently verified (calibration re-run, full suite,
  `tsc`) rather than assumed clean.
- Strong, improving self-correction discipline: the cross-reference drift pattern named in
  Step-Back #3 did not recur this cycle (item 3).
- A now-explicit, named governing principle under consideration ("ALL DATA IS USEFUL")
  that directly targets the exact failure mode (silent degradation of computed values)
  this cycle's two bug fixes both were.

### Weaknesses
- Zero closed revenue, still confirmed absent, unchanged from Step-Back #3 — three days
  of real engineering work, zero movement on the actual named bottleneck.
- Dropbox Sign provisioning remains an open, unconfirmed question, and is now confirmed
  unconfirmable from this session's own Vercel credentials (403 on env-var listing) —
  narrower uncertainty than before (we know *why* it can't be checked from here), but not
  resolved.
- A real infrastructure alert (the "10GB storage" notification) went unlogged somewhere in
  this project's own recent history, a gap in the same "decisions don't stay in
  conversational context" discipline this project otherwise holds itself to.

### Opportunities
- The friction tax ledger's per-condition dollar figures are a real, differentiated
  content asset once the UI-shape/footnote decisions (both resolved this session) are
  live — a concrete, specific artifact to show in a pilot share, not just a description of
  capability.
- The pilot mechanism (Tier 4, "share with 2-3 trusted people") remains unused, per
  Step-Back #3's own recommendation — still available, still low-cost, still untried.

### Threats / risk profile
- Unchanged from Step-Back #3: the OneDigital covenant situation remains the single
  highest-stakes open item, live during current employment, not a future contingency —
  nothing in this pass found any change to that status.
- A live, unresolved infrastructure notification (storage) sitting open for at least one
  full session cycle without a clear owner or next step is a small but real version of the
  same "open thread that could compound" pattern the covenant situation represents at much
  higher stakes — worth closing quickly precisely because it's cheap to close.

---

## Part 4 — Forward Recommendations

1. **Get the actual "10GB" notification text/screenshot from Pete next session.** This
   step-back narrowed the space considerably (not deployment storage, not a billing-plan
   issue, no native Vercel store found) but could not close it without the source text —
   this is now the cheapest possible next step, not a re-investigation.
2. **Log infrastructure alerts the moment they're seen, before they age into an
   unrecoverable "which session mentioned this" question** — the 2026-09-05 storage
   incident got a full, excellent Section 16 entry; whatever generated the "10GB" mention
   this time didn't get one anywhere findable. Small process gap, cheap to close by just
   doing it consistently.
3. **The Dropbox Sign provisioning question deserves a direct owner action, not further
   indirect investigation** — Pete checking `vercel env ls` (or the dashboard) himself
   resolves in one look what two consecutive step-backs have now been unable to confirm
   from the AI side (no tool access the first time, a permissions wall the second).
4. **Watch whether the MOB/CLAUDE.md cross-reference discipline holds for one more cycle**
   before treating it as fixed — one clean pass after two dirty ones is a good sign, not
   yet a trend.
5. **Unchanged from Step-Back #3, repeated because nothing has moved it:** use the pilot
   mechanism before the attorney-review gate opens. The friction tax ledger now gives this
   pilot a more concrete, specific artifact to show than existed three days ago.

---

## Part 5 — Comparison Note

Not performed in this pass, per the standing dual-sourced format and Pete's explicit
instruction for this step-back. This document is the independent, cold, source-verified
half of the process. Reconciliation against the Claude.ai assessment — where the two
agree, where they diverge, and the root cause of any divergence — is a separate step to be
run after both assessments exist.
