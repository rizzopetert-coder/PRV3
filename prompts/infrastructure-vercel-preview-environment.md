# Infrastructure — Vercel Preview Environment ("Option A"): Full Scope Document

Status: DRAFT, concept-level, deliberately deferred. Not started, not scoped for build, no
Gemini review. Captured for future reference at Pete's explicit request — this is a save-for-
later document, not a current priority.

## Origin

Surfaced this session while looking for a fast way to jump to the diagnostic's output for UI
testing, without walking all 42 questions each time. That immediate need has a smaller, faster
fix (a dev-only fixture route rendering PrivateOutput directly — tracked separately, not this
document). But the smaller fix sits on top of a real, already-logged infrastructure gap that's
worth its own scoping pass, captured here.

## Current state, confirmed

- No Vercel Preview environment exists for this project. Every push to `main` deploys straight
  to Production (`prv-3.vercel.app`). Confirmed in an infrastructure-findings session, logged as
  a Decision Register row.
- No custom domain yet either (Porkbun wiring pending, separate open item) — Vercel's
  Deployment Protection (SSO gate) currently blocks public access, which is expected behavior
  given the missing domain, not a bug.
- `tools/diagnostic_fast_forward.py` already exists in the repo, built for jump-to-question
  testing. It's currently confirmed structurally unusable: its own `_guard_not_production()`
  correctly refuses to run against the Production host, and there is nowhere else to point it —
  no Preview environment to target instead. This has sat as an open, undated Priority Queue item
  ("rework or retire, not urgent") since it was found.
- The project's default workflow — stage/commit/push together, hold only for unretested
  production-facing surfaces or structural decisions not yet through Gemini — exists specifically
  *because* there's no Preview environment to test against first. "Push, then Claude.ai verifies
  live" is the actual current normal, not a fallback.

## What Vercel Preview actually is

A standard Vercel feature: every branch or pull request can get its own live, fully-functional
deployed instance on a unique URL, separate from the domain serving Production. It runs real
infrastructure — not a mock, not a local dev server — just not the public-facing domain. Once
configured, most Vercel projects get this automatically on every push to a non-main branch or
open PR, no per-deploy setup required.

## Real scope, not a toggle

This is a genuine infrastructure decision, not a quick setting change:

- **Environment variables and secrets** need a non-Production configuration. Whatever the app
  currently reads from Production env vars (API keys, service credentials, anything
  environment-specific) needs Preview-safe equivalents, or Preview becomes a preview of a broken
  app rather than a working one. Exact inventory of what needs duplicating isn't done — needs a
  real audit of the codebase's env var usage before scoping further.
- **Upstash Redis (session storage)** — needs its own consideration. Does Preview point at a
  separate Redis instance/keyspace, or share Production's with some isolation mechanism? Sharing
  risks Preview test sessions polluting Production data or vice versa; a fully separate instance
  is cleaner but is itself a new piece of infrastructure to provision and maintain.
- **Any external service connections** the engine or web layer touches — not fully enumerated
  here, needs its own pass. Nothing found yet that's a hard blocker, but nothing's been ruled out
  either.
- **Domain/access implications** — Preview URLs are typically also gated behind Vercel's own
  auth by default, separate from whatever the eventual custom-domain SSO gate ends up being.
  Worth confirming this doesn't create a second, redundant access-control system to maintain.

None of this is confirmed infeasible or high-risk — it's confirmed *unscoped*. A real estimate
needs an actual audit pass, not a guess.

## What this unblocks

**Directly:**
- `tools/diagnostic_fast_forward.py` — no new code needed, it already correctly refuses
  Production; pointing it at a real Preview URL un-blocks it as-is.

**More broadly, concrete cases surfaced in discussion this session:**

1. **UI/interaction verification before it's real.** Today's live-verification pass for Category
   E Direction 1 Refinement involved uncertain hover-coordinate fumbling directly against
   Production, unable to fully distinguish "this is broken" from "I clicked the wrong pixel."
   Preview lets that verification happen, and fail safely, somewhere nobody but the team can see.
2. **Catching what real users catch, before real users catch it.** The two live production bugs
   found via Pete's wife's actual use of the diagnostic (headcount-stepper escape-character
   render, flaky remount) were found in Production because there was nowhere else for a real
   person to click through first.
3. **All future Category E visual/interaction work.** Direction 2 (shelved for now but not
   permanently), any future motion or interactivity passes — currently each one means build,
   push to Production, then verify live. Preview extends the same safe-iteration workflow this
   project already uses for content into visual/interactive work.
4. **Structural engine changes.** Recalibrations, new conditional-follow-up structures (the
   Structure 1/2/3 pattern), future severity-trigger work — currently verified via the 172-
   profile regression suite plus live browser walkthroughs post-push. Preview adds a private,
   real environment to click through new question flows before they're live for a real
   respondent.
5. **Gemini reviews that make behavioral claims, not just factual ones.** Gemini's confirmed
   failure pattern (this project's own record: fabricated pass criteria, wrong file paths,
   fabricated CSS values, wrong rollback characterizations) includes claims about how the app
   *behaves*, not just what's in a file. Some of those can only really be checked by clicking the
   actual running app — Preview gives a safe place to do that.
6. **The Pilot Mechanism, already named in the project's own governance model.** The Session 71
   Four-Tier Workflow Governance Model calls for a "2-3 trusted people before site publication"
   pilot step ahead of any Tier 4 public/irreversible action. There is currently no environment
   for that pilot to run in except Production itself — Preview is the infrastructure that
   mechanism already assumes exists.
7. **Tier 4 irreversible decisions generally.** Domain wiring, SSO configuration changes, a
   locked pricing/tier structure — anything in the project's own irreversible-action category
   currently gets tested, if at all, live. Preview means testing nowhere near real.

## Relationship to other open items

- Does not block or depend on Category D, `/book/toc`'s fuller vision, or any current Category E
  work — fully independent, can be picked up whenever.
- Directly related to, but distinct from, the smaller near-term fix (a dev-only fixture route
  for fast output-only testing) — that fix doesn't require this infrastructure and can ship
  first without it. This document is the "do it properly, later" path; the fixture route is the
  "unblock today's specific need" path. They're not mutually exclusive.
- `diagnostic_fast_forward.py`'s rework-or-retire decision (existing Priority Queue item) is
  effectively resolved by this: if Preview ships, "rework" means "point it at Preview," not a
  rebuild. If Preview never ships, "retire" becomes the more honest call.

## Open questions, not yet resolved

- Full environment-variable/secrets audit — not started.
- Redis/session-storage isolation approach for Preview vs. Production — not decided.
- Whether Preview's own access gating creates a second auth system alongside the eventual
  custom-domain SSO gate — not checked.
- Rough effort estimate — genuinely unknown until the audit above happens. Not a "quick setting,"
  not confirmed to be a major undertaking either — currently unscoped in both directions.

## Next steps, if and when this gets picked up

1. Real audit of environment variable / secrets usage across the web and engine layers —
   Claude Code work, needs repo access.
2. Decision on Redis isolation approach — Pete's call once the audit shows what's actually at
   stake.
3. Gemini architecture review before any actual configuration change, per standing protocol —
   this is a structural/infrastructure decision, not a content or copy change.
4. Once live: revisit `diagnostic_fast_forward.py`'s guard and point it at the new Preview URL
   rather than rebuilding it.

Not started. No urgency assigned. Revisit when Pete reopens it.
