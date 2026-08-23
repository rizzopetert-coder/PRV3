# PRV3 Comprehensive Project Assessment — Claude Code, Independent Verification

Date: 2026-08-23
Method: every claim below was checked directly against live source (running the real test suite, executing real engine calls, reading current file contents, grepping for real call sites) in this session. No claim is carried over from a prior document, a prior session's summary, or this conversation's own earlier work without being re-verified fresh. Where a stale document or comment is itself part of the finding, that is stated explicitly and separately from the verified behavior.

---

## Part 1 — Ground-Truth Audit

| # | Item | Status | Evidence |
|---|---|---|---|
| 1 | Diagnostic engine / calibration | **DONE** | Ran `python tools/calibration_runner.py` fresh: 171/175 profiles passed. Breakdown: `high_confidence` OK, `extreme_high_confidence` OK, `moderate` 54/58 (4 failures), `weak` OK. Taxonomy confirmed at 58 states two independent ways (`STATE_PROFILES` dict length and a source-level count). The 4 moderate-tier failures are real and unresolved, not hidden — this is a working, calibrated engine with a small, known residual gap, not a fully closed suite. |
| 2 | Path 1 — full diagnostic instrument | **DONE, contradicted by a stale Decision Register row** | Read `web/app/diagnostic/page.tsx` directly (lines 336-339): choosing the "diagnostic" path mounts `<DiagnosticFlow />` for real, not a placeholder. `tools/_mob.txt` Section 13a still carries a Decision Register row reading *"Path 1 — full diagnostic instrument \| FullInstrumentPlaceholder holds the space... Full instrument not built. Scope TBD."* — this row is stale; a separate Section-14-style row in the same file correctly documents `DiagnosticFlow` replacing `FullInstrumentPlaceholder` as of Session 71. The two rows disagree with each other; only one matches the live code. |
| 3 | Friction tax engine, with real-number rendering confirmed | **DONE — fully calibrated, confirmed with live calls** | `engine/friction_tax.py`: `STATE_MULTIPLIERS` (58/58 populated, 0 `None`), `PAYROLL_BASELINE_GRID` (66/66 cells populated, 0 `None`), `ORG_TYPE_SCALARS` (6/6 populated, 0 `None`). Ran `compute_friction_tax()` live with two different real state/org combinations: `built_to_fail` + Healthcare, 100-249 headcount → `low=$1,870,183 / high=$2,618,257`; `built_to_fail`+`the_unexamined_algorithm` + Technology, 250-499 headcount, Endemic severity → `low=$15,448,829 / high=$21,628,360`. Both returned `calibration_complete=True` with real dollar figures, not `None`. A `tools/_mob.txt` entry from July 2026 claims *"every STATE_MULTIPLIERS entry (57/57)... is None"* — that was true then and is stale now; git log on `engine/friction_tax.py` shows multiple calibration-completion commits since. |
| 4 | Resolution-family + per-state content authenticity | **DONE (content); stale comments confirmed as a separate, narrower issue** | All 58 states' `descriptive_prose` checked programmatically: 0 empty, 0 under 100 characters — real authored prose throughout. `engine/resolution_families.py`'s four `RESOLUTION_FAMILY_DESCRIPTIONS` entries: the actual `"description"` string values are real, specific, authored copy (confirmed by direct read) — but each line still carries a literal trailing `# COPY PENDING — ...` comment, and the module docstring still says *"All family description copy is flagged COPY PENDING."* `git log` shows commit `95fc404` ("content: resolution family descriptions — replace COPY PENDING placeholders") replaced the four description **values** with Pete-supplied final copy, while the patch script's own docstring states the inline comments and module note were **deliberately left as-is**, out of that task's scope. Separately: `get_family()`/`STATE_RESOLUTION_FAMILY` in `engine/resolution_families.py` is confirmed dead Python (zero real callers, per `web/lib/resolution-family.ts`'s own header comment) — the live commercial-facing translation path is `web/lib/resolution-family.ts`'s `translateResolutionFamily()`, not the Python module. |
| 5 | Web commercial surface (domain / Deployment Protection / route reachability) | **PARTIAL** | Live production is `prv-3.vercel.app` — a bare Vercel subdomain, no custom domain yet (Porkbun purchase/DNS wiring confirmed still pending, per `prompts/infrastructure-vercel-preview-environment.md`, dated this session, status: "DRAFT, deliberately deferred, not started"). `web/lib/engine-client.ts` confirms Deployment Protection (Vercel's SSO gate) is currently **absent on Production** — the site is publicly reachable without a bypass secret. No Preview/branch-deployment environment exists at all; every push to `main` goes straight to Production, confirmed as the project's actual current normal, not an oversight. Zero automated test coverage anywhere in the web (TypeScript) layer — confirmed via `tools/_mob.txt`'s own audit note (no `test` script in `web/package.json`, no `.test.*`/`.spec.*` files under `web/`) and independently by direct `find`. |
| 6 | Visual-identity v3 rollout state | **DONE (partial rollout by design, one real nuance found)** | `useTheme()` is live in 9 files: `/about/services`, `/about/story`, `/about/method` (via `MethodPageContent`), `/about` hub, `/ask`, `/book` index + piece + taxonomy-list content. `<ThemeSwitcher>` itself is mounted in exactly one place — `web/app/about/layout.tsx` — scoping the switcher **control** to `/about/*`. But `ThemeSwitcher.tsx` sets `data-theme` on `document.documentElement`, i.e. globally on `<html>`, not scoped to a subtree. Practical effect: a visitor who sets Dark or Neutral on any `/about/*` page and then navigates to `/ask` or `/book/*` carries that theme with them, even though those routes have no switcher of their own — this is real, working behavior, not a bug, but it means "scoped to /about/*" describes where the control lives, not where the theme state applies. Homepage (`/`), `/diagnostic`, and global `NavBar` background remain unmigrated (NavBar's `<nav>` is hardcoded `bg-white`, confirmed non-theme-reactive on any route). |
| 7 | `/book` real published count | **DONE** | Fresh count against `web/lib/book-manifest.ts` today: `published: 87`, `draft: 1`, `parked: 1`. |
| 8 | Engagement Agreement staleness | **STALE / UNVERIFIABLE IN-REPO** | `tools/_mob.txt`'s Session 35 log entry (June 2026) states an "Engagement Agreement Draft v1.0" was produced — ten sections plus Exhibit A, shadow-model compliant, six attorney-review flags, not execution-ready. A repo-wide search (`documents/`, `prompts/`, root, all `.docx` files) found **no file matching this document anywhere in the current repository.** This does not mean it doesn't exist — it may live outside the repo (e.g., a Google Doc) — but it cannot be verified from source the way the other nine items can, and no file path for it appears logged anywhere in the MOB. Legal review of it (Section 3 specifically) is confirmed explicitly parked in the MOB's own "do not resurface" list — reported here factually per the task's constraint, not treated as an open gap and not recommended for reopening. |
| 9 | Real end-to-end transaction path (diagnostic → signature → engagement start) | **NOT BUILT** | Repo-wide search for `stripe`, `docusign`, `hellosign`, `pandadoc`, `checkout`, `payment` across `web/app`, `web/lib`, `web/components` returned zero matches. `web/app/ask/page.tsx` is confirmed (both by direct read intent and by the MOB's own architecture note) to be a single server component with one `mailto:pete@principalresolution.com` link — no client state, no third-party integration. There is no automated path from a completed diagnostic session to a signed engagement or payment anywhere in the codebase; the only mechanism is a human emailing Pete. |
| 10 | Anything else discovered | Two additional real findings | **(a)** Item 2 above is itself evidence of a process gap, not just a one-off stale line: two rows in the same MOB file, both plausibly load-bearing, directly contradict each other on whether Path 1 is built, and neither is flagged as superseding the other. **(b)** `tools/diagnostic_fast_forward.py` exists and is confirmed structurally unusable against current infrastructure — its own production guard correctly refuses to run against `prv-3.vercel.app`, and there is no Preview environment to point it at instead. Logged as an open "rework or retire" item, not urgent, not actioned here. |

---

## Part 2 — Business Viability Gap Assessment

Ranked by how directly each gap blocks a real transaction from happening, most severe first. Technical gaps, gaps that are Pete's decision to make, and gaps that depend on someone outside PRV3 are kept distinct. Legal review of the Engagement Agreement is a fixed, deliberately parked constraint — noted where relevant, never counted as an actionable gap and never recommended for reopening here.

**Transaction-blocking (technical, no path exists today):**
- No automated flow from a completed diagnostic to a signed engagement or payment (Item 9). Every real transaction today requires a human email exchange starting from a bare `mailto:` link. This is the single largest gap between "the diagnostic works and produces a real, calibrated dollar figure" (Items 1, 3 — genuinely true) and "a prospect can become a client without a person manually carrying every step."
- The Engagement Agreement Draft itself — the actual contract a prospect would sign — cannot currently be located in the repository (Item 8). Whether this is a missing-artifact problem or a document-lives-elsewhere problem is not something source-reading can resolve; either way, nobody executing a transaction today has a locatable, current draft to work from inside this project's own record.

**Transaction-blocking (external, not Pete's or PRV3's to fix alone):**
- Legal review of the Engagement Agreement (six attorney-review flags noted at drafting, per the MOB) is outstanding and explicitly parked. This is a real precondition for the contract being execution-ready, factually reported here, not reopened or recommended for action.
- No custom domain yet (Porkbun wiring pending) — a `prv-3.vercel.app` URL is a real, reachable, working site, but is a materially weaker signal to send a prospect than a branded domain, and this is outside PRV3's codebase to resolve on its own.

**Not transaction-blocking, but load-bearing for how safely the project can move (Pete's call, technical in nature):**
- No Preview/branch-deployment environment exists — every change tests live on the same URL a prospect could be looking at, with no automated test suite as a second line of defense (Item 5). This is a process-risk gap, not a missing-feature gap: the diagnostic and friction tax outputs verified in Part 1 are real and correct today, but the mechanism for catching a future regression before it's public is weaker than it could be.
- The stale/contradictory Decision Register rows found in Item 2/10(a) are a documentation-integrity gap, not a functional one — the engine and web layer are ahead of what the project's own status record says about them in at least one place.

**Not gaps — confirmed working, contrary to what a document-only read might conclude:**
- Diagnostic engine, Path 1 full instrument, friction tax calibration, resolution-family and per-state copy, and the `/book` library (87 published pieces) are all real, live, and functioning as of this session's direct verification.

---

## Part 3 — SWOT

Grounded specifically in Part 1's findings. Items marked *(judgment)* are category-level or contextual assessments rather than direct source verification, and are labeled as such.

**Strengths**
- A genuinely working, calibrated diagnostic engine (171/175, 58 states) with a fully populated, live friction-tax pricing layer that renders real, non-trivial dollar figures today (Items 1, 3) — this is the hardest, most technically substantive part of the product, and it is done.
- A large, real content library: 87 published `/book` pieces plus authored (not placeholder) prose across all 58 states and all four resolution families (Items 4, 7).
- Consistent engineering discipline evident in the source itself — dry-run/write patch scripts, exact-match guards, docstrings that record *why* a change was made and what was deliberately left out of scope. *(judgment: this reads as a genuine practice, not just a one-off; it's what made several of Part 1's findings independently checkable in the first place.)*

**Weaknesses**
- No automated path from diagnostic completion to a signed, paid engagement (Item 9) — the product's technical core is ahead of its commercial mechanics.
- Zero automated test coverage in the web layer and no Preview environment (Item 5) — *(judgment)* a real, if not currently urgent, fragility given the project's stated preference for testing live.
- Internal documentation (the MOB's own Decision Register) contains at least one direct self-contradiction on a load-bearing fact (Item 2/10a) — a real risk to anyone, human or AI, relying on that document alone.

**Opportunities**
- Because the engine and content are further along than the project's own most pessimistic internal notes suggest, the practical next investment is concentrated and known: the transaction path (Item 9) and locating/finalizing the Engagement Agreement (Item 8), not further engine or content work. *(judgment: this is a comparatively narrow, well-defined gap to close relative to what's already built.)*
- A Preview environment (already scoped in detail in `prompts/infrastructure-vercel-preview-environment.md`, deliberately deferred) would directly de-risk future Tier 4 work and is explicitly named there as the missing infrastructure the project's own Pilot Mechanism already assumes exists.

**Threats**
- Every push currently deploys straight to a publicly reachable Production URL with no Deployment Protection and no automated tests (Item 5) — *(judgment)* the realized risk so far has been two production bugs caught by a real user (Pete's wife) rather than by verification infrastructure, which is a pattern that could repeat with more consequence once real prospects are using the site.
- The absence of a locatable Engagement Agreement draft (Item 8) creates a risk that isn't purely technical: if a transaction opportunity arose today, the contracting step would have no ready starting document inside this project's own record.

---

## Part 4 — Forward Recommendations

Grounded in Part 1's specific gaps. Does not recommend reopening legal review of the Engagement Agreement — that stays exactly where Pete parked it.

1. **Locate or reconstitute the Engagement Agreement Draft v1.0** (Item 8) before any other transaction-path work — there is no point building automation toward a document that currently doesn't have a confirmed location. This is a Pete-decision item (where does it live, does it need to be re-drafted) more than a technical one.
2. **Scope the transaction path** (Item 9) as its own explicit workstream once #1 resolves — even a minimal version (e.g., a structured intake-to-Pete handoff richer than a bare `mailto:`) would close the largest gap found in this audit.
3. **Reconcile the Path 1 Decision Register contradiction** (Item 2/10a) — a five-minute fix (correct or retire the stale row) that removes a real risk of anyone, including a future AI assessment, citing the wrong one.
4. **Preview environment** (Item 5) — already fully scoped in `prompts/infrastructure-vercel-preview-environment.md` at "not started, no urgency assigned, revisit when Pete reopens it." This assessment doesn't change that status, but notes it directly supports #1-#3 in reducing risk once picked up.
5. Custom domain / Porkbun wiring — outside this audit's technical scope to recommend a timeline for, but worth sequencing consciously against #1/#2 rather than treating as independent, since a domain change is a more credible signal to send once there's a real transaction path behind it.

---

## Part 5 — Comparison Note

Two specific claims from the earlier, conversation-history-based assessment were named by Pete as materially wrong. Both are directly addressed by Part 1's fresh verification:

- **"Friction tax pricing engine wasn't built."** Confirmed false as of today: `compute_friction_tax()` is fully calibrated across all three axes (58/58 states, 66/66 grid cells, 6/6 org types, 0 `None` entries anywhere) and returns real dollar figures on live test calls (Item 3). The likely source of the error: `tools/_mob.txt` itself still contains a July-2026-dated entry stating the opposite — a conversation-history search that surfaced that older entry, without checking it against a fresh calibration-table read or a live function call, would reproduce exactly this mistake. This is the general risk this whole assessment was built to avoid: a document can be accurate when written and stale by the time it's cited.
- **"Resolution-family copy was still COPY PENDING."** Partially right, partially wrong, in a way worth stating precisely rather than just overturning: the actual `"description"` field values are real, specific, Pete-supplied copy (confirmed via direct read and via the `95fc404` commit that put them there) — so "copy pending" as a claim about the *content* is false. But the literal string `"COPY PENDING"` genuinely does still appear in `engine/resolution_families.py` today, in five places (the module docstring plus four trailing comments) — so an assessment built on a text search for that exact phrase, without checking whether it appeared in a comment versus a live value, would find real matches and draw the wrong conclusion from them. The correction isn't "there was nothing to find" — it's "what was found was a stale label on finished work, not evidence the work wasn't finished."

Both errors share a shape: real historical or in-code text (an old MOB entry, a leftover comment) was treated as current truth about behavior, rather than checked against what the code actually does when run. That's the specific failure mode this document's method — running the calibration suite, calling `compute_friction_tax()` live, counting non-empty `descriptive_prose` fields — was built to avoid.

---

## Addendum — 2026-08-23 (same day): Engagement Agreement status definitively resolved

Item 8 above flagged the Engagement Agreement Draft v1.0 as "stale / unverifiable in-repo" — present in the MOB's Session 35 narrative but not locatable anywhere in the repository via a filesystem search. This addendum records a follow-on, deeper check: full git history, not just the current working tree.

**Method:** `git log --all --full-history --diff-filter=A` for the exact filename and reasonable variants (v1, draft, docx), across every branch including the two stale agent worktrees — not just `main`. Cross-checked two independent ways: a content pickaxe (`git log --all -S"Engagement Agreement"`, searching for the literal string ever being added to or removed from any tracked file's content) and a full-history filename scan for every `.docx` file ever committed to this repository (`git log --all --name-only -- "*.docx"`).

**Finding:** zero commits, on any branch, ever added a file matching this document. The `.docx` scan returned zero results for *any* `.docx` file, ever — not just this one. The commit that logged the draft's creation (`faec1f9`, Session 35 closeout, 2026-06-08) itself names the document's location as `PRV3_Engagement_Agreement_Draft_v1.0.docx, outputs folder` — Claude.ai's own session-output storage, external to this git repository by construction, not a repo-relative path.

**Conclusion, stated precisely:** this is not a case of a file existing and later being deleted — it was never checked into this repository at all. It is also not currently sitting untracked in the working tree, unlike 8 sibling `.docx` documents from the same era (`PRV3_Frameworks.docx`, `PRV3_Scoring_Architecture_Spec_v1.docx`, etc.) that do sit untracked in `documents/` today. Whether a copy exists somewhere outside git (a local download, a Google Doc) is unknown and outside what git history can answer — that determination, and any decision to locate or rebuild the document, is Pete's call, not resolved here.

Full detail and Decision Register entry: `tools/_mob.txt` Section 13a.
