# PRV3 Quarterly Step-Back — 2026-09-05

Second run under the dual-sourced format locked 2026-08-23 (`prompts/prv3-quarterly-step-back-2026-08-23.md` defines the process; not re-defined here). Process followed as specified: Claude.ai produced an initial assessment first; Claude Code then independently re-verified cold, from live source only, without reading Claude.ai's version until after its own assessment was complete.

**Trigger:** this Quarterly Step-Back was due "on or near September 6, 2026" per the standing cadence note. It had not run on its own — Pete had to explicitly request it after the fact, one day before the due date, following a long same-day execution stretch (STATE_CAUSATION_OVERRIDES closure, the silosolation fix, the coverage-threshold gate build, the Vercel infrastructure cleanup). This is itself a finding, not just process trivia — see Reconciliation below.

---

## Round 1 — Claude.ai's Initial Assessment (provisional, verbatim)

> **Strengths**
> - Verification discipline is now systemic, not incidental — three separate Gemini fabrications caught this session alone (silosolation's dimensional vector, plus two more in the earlier recede/resolve thread per the other chat), all before they shipped.
> - Taxonomy/engine work is genuinely rigorous: `STATE_CAUSATION_OVERRIDES` closed with real per-state reasoning, not pattern-stamped; the coverage-threshold gate was built on primary-statute verification, not aggregator convenience.
> - 25 years of real judgment sits behind this — the product's actual differentiator was never the software.
>
> **Weaknesses**
> - The diagnostic has still never been run against a real external organization — the production Redis aggregate list is entirely your own test sessions. This was true in August and is still true now; nothing this session changed it.
> - No custom domain, no live transaction path, no public-facing identity tied to your name (shadow-model constraint via the OneDigital covenant).
> - Legal/Compliance module — the highest-stakes accuracy surface in the product — still has ~30 states at PARTIAL confidence, by design excluded from dollar output, but that's still a large unfinished surface on a credibility-critical feature.
>
> **Opportunities**
> - The coverage-threshold work done today is a genuine differentiator if finished properly — most competitors in this space almost certainly still use the federal-only framing.
> - The attorney-review question remains the single highest-leverage unresolved decision on the board, cheap relative to what it unblocks.
>
> **Threats**
> - Time cost: an enormous amount of session time continues to go into engine/taxonomy refinement work that, however well-executed, doesn't touch the demand-validation gap.
> - The parked attorney-review decision has now been raised and reaffirmed as parked twice (once via the Fable exchange, implicitly again by continued build-focus) — worth naming plainly rather than letting inertia decide it by default.
>
> **Honest viability read:** the product keeps getting more defensible technically. The business case hasn't moved. Both things can be true, and only you can decide if that's the right allocation of time right now.

---

## Round 2 — Claude Code's Independent Cold Assessment (verbatim, produced without reading Round 1)

### 5 required verified items

1. **Production diagnostic-aggregate data — could not independently verify.** Production's `UPSTASH_REDIS_REST_URL`/`TOKEN` are Sensitive-flagged; `vercel env pull --environment=production` returns literal `"[SENSITIVE]"`, confirmed live. Preview-scoped credentials pulled in plaintext, but Preview is a deliberately separate Redis instance (split from Production during a Session 71 fix) and wouldn't answer the production question even if queried. Attempted a read-only query against it anyway for context — blocked by Claude Code's own safety classifier (sending a bearer token to an external host); did not attempt to route around this. **What I could confirm directly:** a full search of tracked MOB history found zero mentions of any real signed client or external organization anywhere. That absence is the verified fact. The specific "11 entries, all test sessions" figure is a carried-forward claim from a separate, older exercise — I could not re-verify the count or its interpretation this session.
2. **Legal/Compliance coverage-threshold module — verified exactly as designed, stress-tested not just read.** Live count from `engine/friction_tax.py`: 7 CONFIRMED, 44 PARTIAL, 51 total (matches the commit message). Called `resolve_coverage_gate(headcount=1, jurisdictions=["CO"])` directly — Colorado is PARTIAL with threshold=1, meaning if trusted, headcount=1 would read as "covered." Result: `confidence='FEDERAL_FALLBACK'`, `applies=False` — the federal 15-employee floor was used instead. Confirmed through the real dollar-output path too (`compute_legal_compliance_exposure`): `low`/`high` both `None`. The gate is genuinely wired end to end.
3. **Production accessibility — mostly unchanged, one live discrepancy.** `prv-3.vercel.app` returns HTTP 200 live. `vercel domains ls` shows exactly one registered domain on the account, `principalresolution.com`, bound exclusively to `prv-2` — PRV3 itself has never had a branded domain. Discrepancy: live config shows `ssoProtection: {"deploymentType": "all_except_custom_domains"}` — a real, non-null setting — yet the live curl returns a clean, unauthenticated 200 with no auth challenge. Could not reconcile from this environment (possibly a Hobby-tier plan limitation makes the setting inert); flagging rather than guessing.
4. **Test suite — fully clean, run fresh.** All 11 Python engine scripts pass (775+ assertions, 0 failures). `test_friction_tax.py`: 121/121. Calibration suite re-run fresh, not carried forward: 166/175 (9 failed), identical to the last logged 2026-08-29 figure — genuinely re-verified, not stale. Severity: 175/175. One weak spot: `extreme_high_confidence` tier is 0/1 — the entire tier fails its one test profile.
5. **Other structural findings:** 783 commits since 2026-05-03 (~4 months), a sustained ~6-7 commits/day velocity. The MOB's own Priority Queue contains an internal contradiction — items 1 and 3 still say "no automated tests," flatly false today, sitting uncorrected right next to item 2's own accurate correction ("45/45 passing... most of the web layer remains untested"). 87 `/book` pieces published (matches standing record). 16 untracked files, the known deferred pile, not growing. No dedicated Redis-inspection tooling exists in `tools/`, confirmed by direct search. **The Legal/Compliance module as a whole — coverage gate included — is still not wired into `compute_friction_tax()`'s return dict, `contract.py`'s output, or `web/lib/types.ts`**, confirmed by the function's own header comment and by tracing that it isn't called anywhere in the output pipeline. A fully-built, empirically-tested subsystem with zero client-facing surface today.

### SWOT (independently derived)

**Strengths**
- Engine test discipline is real and enforced: 775+ assertions across 11 scripts, re-verified today at zero failures; today's own coverage-threshold gate was empirically stress-tested (not just documented) before being trusted.
- Sustained, high-velocity, self-correcting engineering process — 783 commits in 4 months, with a visible, repeated pattern of catching and fixing its own stale claims rather than letting them calcify.
- A working, live, calibration-tested diagnostic engine (166/175) with a genuinely sophisticated taxonomy and a real, if incomplete, legal/compliance exposure model now state-aware.

**Weaknesses**
- Zero verifiable external usage — the one usage data point that exists is unverifiable from this environment and over a week old regardless.
- No branded domain for the actual product; unauthenticated, unbranded `.vercel.app` URL; no Preview-environment safety net.
- The Legal/Compliance subsystem has no path to the client at all yet — complete, tested, and unused.
- `extreme_high_confidence` calibration tier at 0/1.
- Real credential-hygiene inconsistency: Preview's Redis token is unmasked/plaintext-retrievable while Production's is properly Sensitive-masked.
- The MOB's own open-items tracking has internal contradictions.

**Opportunities**
- The coverage-threshold gate's PARTIAL-state design (44 of 51) is a ready-made, code-risk-free roadmap for incremental legal-research investment — each state upgrades independently, gated by design.
- A real external pilot would immediately convert the single biggest unknown into a known.

**Threats**
- Continued Tier-1-only engineering (this session flagged itself as Tier-1-heavy, triggering the project's own Soft Governor tripwire) risks indefinitely deferring the attorney review and real external validation.
- The Quarterly Step-Back itself was due 2026-09-06 and had to be manually triggered rather than firing on its own cadence — a structural process built specifically to prevent extended engineering-only stretches from continuing unchecked did, in fact, need a manual nudge.

**Honest viability read (Round 2, before comparison):** the engineering is real and rigorous — that's not in question. What's genuinely unverified, from live source, independent of any prior framing: whether anyone outside this project has ever used it. That is the load-bearing uncertainty this whole assessment turns on, and it could not be resolved from this environment either way.

---

## Reconciliation

**Where Round 1 overstated confidence, corrected against live source:** Claude.ai's Weaknesses section states as settled, current fact that "the production Redis aggregate list is entirely your own test sessions... This was true in August and is still true now; nothing this session changed it." **This claim was not independently re-verified this session by either assessment.** Production's Redis credentials are properly Sensitive-masked and could not be queried live — by design, this is correct security posture, not a gap to fix. The specific "11 entries" figure traces to a separate, older strategic-evaluation exercise, carried forward without re-verification since. **What Round 2 could independently confirm, and what the reconciled record should actually rely on:** a direct search of all tracked MOB history found zero mentions of any real signed client, paying customer, or external organization anywhere. That absence — not the specific session count — is the verified fact. The practical conclusion is the same either way (no evidence of external usage), but the two claims have different evidentiary weight, and the record should reflect the one that's actually checkable.

**Three genuinely new findings, surfaced only by the cold pass (Round 1 had no way to catch these — they required live infrastructure/code inspection, not conversation history):**

1. **Today's entire coverage-threshold gate build has zero live effect.** Complete, empirically stress-tested, correctly gated end to end — and structurally disconnected from every client-facing output path. `engine/friction_tax.py`'s Legal/Compliance module is not wired into `compute_friction_tax()`'s return dict, `engine/contract.py`, or `web/lib/types.ts`. Round 1's Weaknesses section correctly flagged the ~30 PARTIAL states as an unfinished surface, but did not know (couldn't know, from conversation history) that the entire module — CONFIRMED states included — currently reaches no client at all.
2. **A real credential-hygiene asymmetry.** Preview's `UPSTASH_REDIS_REST_URL`/`TOKEN` pull in plaintext via `vercel env pull`; Production's are properly Sensitive-flagged and masked. Not necessarily a live exploit (Preview is a separate, non-production instance), but an inconsistency in how the two environments are protected that's worth a deliberate look rather than an accident of which environment happened to get flagged first.
3. **An unresolved discrepancy between prv-3's stated and observed access-protection state.** Live config: `ssoProtection.deploymentType = "all_except_custom_domains"` (a real, active-looking setting). Live behavior: a clean, unauthenticated HTTP 200 on `prv-3.vercel.app`, no auth challenge. Neither the config nor the observed behavior should be assumed to reflect the true state of production access control until this is reconciled — flagged, not resolved, since guessing here (e.g., "probably a Hobby-tier limitation") isn't the same as confirming it.

**Smaller findings worth preserving alongside the above:**
- `extreme_high_confidence` calibration tier at 0/1 — the one tier that should be easiest to get right is failing entirely.
- A real internal contradiction in the MOB's own Priority Queue: items 1 and 3 still claim "no automated tests," sitting uncorrected next to item 2's already-accurate correction of the same claim.

**Points both assessments agreed on, independently:**
- No branded domain for `prv-3` — only `prv-2` holds `principalresolution.com`.
- No verifiable external usage anywhere in tracked history.
- The Step-Back process itself had to be manually triggered rather than firing on its own cadence — worth naming plainly, since this is exactly the kind of drift the process exists to catch, and it happened to the process's own cadence check.

**Reconciled viability read:** the engineering is verifiably rigorous and continuing to improve — both assessments agree, and Round 2's direct testing (the coverage-threshold gate's empirical stress test, the fresh calibration run) reinforces rather than merely repeats that conclusion. Whether the product works for anyone besides Pete remains genuinely, honestly unanswered — not because it's being avoided, but because nothing has yet forced an answer either way. That is the single fact this whole reconciliation converges on, from two independent directions.

---

## Decision items surfaced but explicitly NOT acted on this session

Logged as open, not parked, not resolved — tracked structurally in Section 13a/13b (`tools/_mob.txt`), not only here:

1. **Fix the Preview Redis credential exposure** (plaintext-retrievable via `vercel env pull`, unlike Production's Sensitive-masked equivalent).
2. **Resolve the `ssoProtection` discrepancy** before assuming production access behaves as either the live config or the observed live behavior alone suggests.
3. **Decide whether to wire the built-but-unused Legal/Compliance module into live output now or later** — a real product decision, not an engineering one; the code is ready either way.

## Cadence

This run: 2026-09-05. Logged in `CLAUDE.md`'s Quarterly Step-Back section as the new "Last step-back" date; next due recalculated biweekly from this date, per the standing cadence rule (unchanged by this run).
