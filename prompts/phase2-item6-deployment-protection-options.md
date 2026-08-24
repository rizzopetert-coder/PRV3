# Deployment Protection — Options Brief

Date: 2026-08-24. Decision prep only — no setting changed. For Pete's call.

## Current state, confirmed

Deployment Protection is **off** on Production (`prv-3.vercel.app`). No custom domain is wired (Porkbun purchase/DNS work not started). Web-layer test coverage, corrected this session (see `prompts/phase1-item4-web-test-coverage-correction.md`): not zero — 45 real tests exist, 39 pass, 6 known failures, covering 4 files (`ConstellationField`, `engine-client`, `resolution-family`, `session-store`) out of the full web layer. No Preview environment exists — every push deploys straight to this same public Production URL.

## What turning it on vs. leaving it off actually means, practically

**Leaving it off (current state):** the live site is reachable by anyone with the URL, unauthenticated, right now. Given there's no custom domain yet, `prv-3.vercel.app` is not a URL anyone would find by accident or by guessing a brand name — practical exposure today is closer to "reachable if someone has the link" than "publicly discoverable." Every push (including anything not yet fully verified) goes live at this same URL immediately.

**Turning it on:** Vercel's Deployment Protection gates access behind an SSO/auth check — anyone without a Vercel-authenticated session (or a bypass token) would be blocked, including Pete's own casual browser checks and any live-verification workflow that currently relies on directly opening the URL (several sessions this arc have used exactly this — Pete's own claude-in-chrome live checks against Production). Turning it on would require either provisioning a bypass mechanism for those checks or switching verification back to local/dev-server-only, which is a real workflow change, not just a settings toggle.

## Is there a reason to act before domain wiring happens?

**No clear urgency found.** The two real risks this posture creates — an unverified push reaching a real visitor, and no test/Preview safety net catching a regression before it's live — are both already true today regardless of whether Deployment Protection is on or off, since the actual gap is "no Preview environment + partial test coverage," not specifically "no auth gate." Turning Deployment Protection on would reduce exposure marginally (fewer people who could stumble onto the URL) but wouldn't address the underlying verification-gap risk at all, and would cost real workflow friction (breaking the established live-check pattern) for a marginal exposure reduction on a URL that isn't the eventual public-facing domain anyway.

## Options for Pete

1. **Leave it off, unchanged, until custom-domain wiring happens** — matches the sequencing already recommended elsewhere this session (domain wiring after a real transaction path exists). Deployment Protection would then naturally become a real decision at the same time as domain wiring, not a separate one now.
2. **Turn it on now anyway**, accepting the live-verification workflow change, as a precautionary step independent of domain timing — worth it only if Pete weighs "reduce exposure now" above "keep the current fast live-check workflow."
3. **Leave it off, but treat the underlying gap (test coverage + no Preview environment) as the thing actually worth acting on** — since that's what would catch a real regression before a visitor sees it, which Deployment Protection alone doesn't address either way.

No recommendation forced — the practical stakes here are genuinely low either direction (a low-traffic, unbranded URL, with the real risk sitting in test/Preview coverage rather than the auth gate specifically), so this is presented as a real choice rather than a close call to be decided unilaterally.
