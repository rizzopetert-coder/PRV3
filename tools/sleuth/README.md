# sleuth

Site-integrity crawler for principalresolution.com. Crawls a single base
URL (dev or prod -- same tool, `--base-url` flag), surfaces structural,
brand, and content/editorial problems, split into a **deterministic**
tier (auto-fail, non-zero exit code) and a **candidate** tier (flagged
in the report for human/AI review, never auto-failed).

## Usage

```bash
python tools/sleuth/cli.py --base-url https://principalresolution.com --theme warm
python tools/sleuth/cli.py --base-url http://localhost:3000 --theme dark --skip-build
python tools/sleuth/cli.py --base-url https://<preview>.vercel.app --theme neutral \
    --bypass-secret VERCEL_AUTOMATION_BYPASS_SECRET
```

One theme per invocation -- run it three times (warm/dark/neutral) for full
coverage, not once with all three bundled.

`--bypass-secret` takes the **name** of an environment variable holding the
real Vercel Protection Bypass for Automation secret, not the secret itself
(so it never appears in shell history or a process listing). Mechanics
verified against Vercel's current docs during this build: header
`x-vercel-protection-bypass: <secret>` plus `x-vercel-set-bypass-cookie: true`
(Vercel's own documented pattern for multi-page/in-browser automation, which
a BFS crawl is).

Other flags: `--skip-build` (reuse the existing `web/.next` build instead of
running `npm run build` first), `--concurrency` (default 3), `--max-pages`
(default 400), `--per-page-timeout-ms` (default 20000).

### `--skip-build` and stale builds

Without `--skip-build`, sleuth always runs `npm run build` before crawling
(`route_manifest.build_route_manifest`), so the crawl can never be stale --
this is the default for exactly that reason.

`--skip-build` exists to save the build step on repeat runs, but it opens a
real gap: if source changed after the existing build was produced, sleuth
would crawl and report on content that no longer exists, with nothing
distinguishing that from a real live finding. This happened for real: a
`--skip-build` crawl reported 110 "coaching used as a noun" hits against a
build that was about 16 hours older than three commits that had already
reworded the exact sentence being flagged. Every one of those 110 findings
was against text that no longer existed in source. Nothing caught it until
a human noticed the findings didn't match the live repo.

`cli.py` now checks this whenever `--skip-build` is passed: it compares
`web/.next/BUILD_ID`'s mtime against the latest commit touching
`web/app`, `web/components`, `web/lib`, or `web/content`, and **fails fast**
(non-zero exit, no crawl attempted) if the build predates that commit.

Fail-fast rather than sleuth silently running `npm run build` itself on your
behalf: `--skip-build` is an explicit request to skip the build step, and
sleuth has stayed read-only/non-invasive everywhere else in its design (it
crawls and reports on the site under test, it never modifies it or the
process running it). Quietly overriding that flag would replace an explicit
choice with a guess, and `next build` can take long enough that surprising
the caller with one mid-command is worse than a clear, actionable error.
The error message tells you to either run `npm run build` yourself or drop
`--skip-build`.

Known limitation, matching the scope this check was asked to cover: it
compares against the latest **commit**, not the working tree, so uncommitted
edits to a watched path aren't caught. A stricter working-tree check would
need a different mechanism (e.g. hashing watched files), not implemented
here.

### Outputs

Written to `tools/sleuth/output/`:

- `sleuth_raw.json` -- full crawl extract (every page's rendered text,
  computed styles on real text-bearing elements, full link graph, HTTP
  status/redirect chain, axe-core violations). Gitignored -- large,
  fully-regeneratable raw data, never worth tracking. Re-running the rule
  engines against a saved `sleuth_raw.json` without re-crawling is possible
  by importing `tools.sleuth.rules.*` directly against loaded JSON.
- `sleuth_report.md` -- findings grouped structural -> brand ->
  content/principle -> style, deterministic findings first within each
  group, candidate findings clearly marked as review-only. **Tracked and
  committed deliberately, not gitignored** -- Pete's explicit call,
  2026-09-22 (commit `47aca05`): a regenerated report is committed as
  evidence of a specific fix, not automatically on every run.

Exit code: non-zero if any deterministic-tier finding exists anywhere in
the crawl, zero otherwise (candidate-tier findings never affect it,
however many there are).

## Architecture

- `route_manifest.py` -- the "expected" route set, read from a real
  `next build`'s `.next/prerender-manifest.json` rather than hand-parsed
  from `web/app/**/page.tsx`. Confirmed during this build that `/book/*`
  alone has four separate dynamic-route generators (`[type]/[slug]`,
  `dimension`, `pillar`, `state`), each pulling from a different data
  source -- reading Next's own resolved output avoids re-implementing all
  four in Python and risking drift every time one of them changes.
- `crawler/crawl.mjs` -- the actual BFS crawler. **Node, not Python** --
  the project's only installed Playwright is the Node one already in
  `web/node_modules` (with Chromium binaries already downloaded), so this
  reuses it via `createRequire` anchored at `web/package.json` rather than
  installing a second, redundant Playwright+Chromium under Python.
  `cli.py` invokes it as a subprocess with `cwd=web/`.
- `tokens.py` -- the locked color/font allowlists, read from
  `web/app/globals.css` and `web/app/layout.tsx` directly (see below for
  why this diverges from the original build brief's stated 4-color/
  JetBrains-Mono assumption).
- `config.py` -- the banned-jargon list (extracted live from
  `engine/output_synthesis.py`'s system prompt, not hand-duplicated) and
  the two exemption lists the brief assumed existed (see below).
- `rules/{structural,brand,content,candidate}.py` -- the four rule
  engines, each a `check(crawl, ...) -> list[Finding]`.
- `report.py` -- renders `sleuth_report.md`.

## What changed from the original build brief, and why

Confirmed with Pete before writing any code (this section is the record
of that, not a changelog of afterthoughts):

1. **Brand palette is far richer than 4 colors.** The real system is
   fully theme-reactive (v2 base tokens redefined per `[data-theme]`)
   plus a five-color v3 expansion per theme with usage-tier rules
   (TEXT-SAFE / LARGE-DECORATIVE-ONLY / BACKGROUND-FILL-ONLY /
   CTA-EXCLUSIVE), on top of the v1 static palette the brief described.
   `tokens.py` reads every locked color from `globals.css` as a flat
   union (all themes, all scopes) rather than the stated 4 hex values --
   correct per-theme cascade resolution and tier enforcement are known,
   accepted v1 simplifications (see `tokens.py`'s module docstring).
2. **JetBrains Mono is stale.** `web/app/layout.tsx` shows it was already
   replaced by IBM Plex Mono. Real locked set: Lora, Inter, IBM Plex
   Mono, Source Serif 4 (optional). Geist/Geist Mono accepted as the
   framework's own base-layer fallback, not flagged as foreign.
3. **No `src/data/glossary.json` exists.** No `src/` directory at all in
   this repo, and no page whose purpose is naming/critiquing the
   banned-jargon terms. `GLOSSARY_EXEMPT_ROUTE_PREFIXES` in `config.py`
   is empty -- a confirmed absence, not an oversight -- and will activate
   automatically if such a page is ever built.
4. **No enumerated shadow-model exception list exists**, only the general
   rule. One real, live exception was found and confirmed during this
   build: `pete@principalresolution.com` in `/first-call`'s own
   error-state copy -- seeded in `config.py` as the one confirmed entry.
   `/first-call/admin` is also exempt (internal-only, never
   commercial-surface).
5. **Route manifest sourced from `next build` output**, not hand-parsed
   TSX -- see Architecture above.

## Known gaps (also printed in every `sleuth_report.md`)

- **No coined-term (P-10) scan.** P-10 (the Principal Brief / CLAUDE.md
  standing rule) is "no coined terms" -- a rule, not an enumerated list of
  specific coined terms. No such list exists anywhere in this repo to
  check against, so this isn't implemented. A heuristic (e.g. flagging
  Title Case or hyphenated compounds) would mostly generate noise, not
  real signal -- not shipped under a real-looking label.
- **Rust-reservation check is class-name-based, not color-based.**
  Caught mid-build via a real false-positive flood in this session's own
  test crawl: `--oxide-text` (unrestricted general accent) and
  `--urgency`/`--urgency-text` (reserved for genuine Endemic-severity
  signaling) are numerically **identical** hex values in both Warm and
  Dark themes (confirmed in `globals.css`'s own comment). A computed-color
  check cannot distinguish them in those two themes. Redesigned to key
  off the literal `bg-rust`/`text-rust`/etc. Tailwind class instead, with
  the one confirmed exception (`ServiceSidebar.tsx`'s First Call section)
  matched narrowly by its `<a href="/first-call">` context, not by class
  name alone.
- **Dead-end detection** treats "has at least one `<button>` anywhere on
  the page" as a CTA proxy -- doesn't confirm the button actually
  navigates. Accepted to avoid false-failing real, working
  JavaScript-driven CTAs (e.g. `/first-call`'s submit button).
- **Appositive em-dash heuristic** flags any em-dash-delimited span
  containing a comma, which also catches ordinary rhetorical
  interruptions that aren't really appositive lists (confirmed in this
  build's own test run). Candidate tier only, by design, for exactly
  this reason -- needs human/AI judgment, not treated as precise.

## Verification performed during this build

Ran end-to-end against `http://localhost:3000` (5-page smoke test,
15-page capped run, full 107-of-121-page run, plus a dedicated
dark-theme run). Caught and fixed four real bugs before calling it
done:

1. An ESM module-resolution failure (Node's `import` doesn't follow
   `cwd`; fixed via `createRequire` anchored at `web/package.json`).
2. The oxide/urgency color collision (see the rust-reservation gap
   above) -- caught because the first real test crawl immediately
   flooded the report with false positives, not caught by inspection.
3. Orphan detection wasn't applying its own exclusion list -- `/dev/*`
   and `/favicon.ico` were showing up as false orphans in the first
   full-crawl test.
4. **`--theme` had no actual effect on rendering** -- the flag only
   changed which colors sleuth treated as valid; the crawled pages
   still rendered in Warm (the site's default) regardless, because
   nothing was seeding the site's real theme-persistence mechanism
   (`localStorage["prv3-theme"]`, read by `ThemeSwitcher.tsx`). Fixed
   via `context.addInitScript()` seeding that same key before every
   navigation -- the same mechanism a real returning visitor's
   persisted preference uses, not a synthetic bypass. Verified by
   inspecting raw computed styles from a `--theme dark` run:
   `rgb(237, 234, 227)` and `rgb(143, 163, 156)` are Dark's exact
   `--ink` (#EDEAE3) and `--slate` (#8FA39C) values, not Warm's.

The full run surfaced real findings, including a genuine semicolon in
a published `/book` piece and a real missing-form-label accessibility
gap on `/first-call`. All three themes confirmed via raw computed-style inspection after the
fix (Warm/Dark/Neutral `--ink` all resolved correctly: `rgb(20,23,26)`
/ `rgb(237,234,227)` / `rgb(52,56,60)`). Not exercised during this
build: a live Vercel deployment with `--bypass-secret` -- the
header-injection code path is verified against Vercel's current docs,
but not against a real protected deployment.
