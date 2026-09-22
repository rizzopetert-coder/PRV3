# sleuth report

- Base URL: `http://localhost:3000`
- Theme: `warm`
- Pages crawled: 107
- Generated: 2026-09-22T15:10:16.991321+00:00
- **Deterministic (auto-fail) findings: 216**
- Candidate (review) findings: 247

## Known gaps in this run

- No coined-term (P-10) scan: the build brief asked for "possible coined-term hits," but P-10 is the rule ("no coined terms"), not an enumerated term list -- no such list exists anywhere in this repo to check against. Not implemented with a fake heuristic; see tools/sleuth/rules/candidate.py's module docstring.
- Brand-color check uses a flat union of every locked color across all themes and scopes (not strict per-theme cascade resolution) -- see tools/sleuth/tokens.py's module docstring for why, and the tradeoff this accepts.
- Glossary-exemption list (tools/sleuth/config.py) is currently empty -- confirmed no src/data/glossary.json or equivalent page exists in this repo. Will activate automatically if such a page is ever built.
- Shadow-model exemption list has exactly one confirmed entry (pete@principalresolution.com) -- anything else that should be exempt needs the same explicit confirmation before being added.

## Structural breaks

### Deterministic (11) -- exit code non-zero

- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/dimension/alliance`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/dimension/aptitude`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/dimension/attitude`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/dimension/authority`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/pillar/case-composited`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/pillar/foundation`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/pillar/pattern-named`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/pillar/reframe`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/book/pillar/underneath`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/diagnostic/condensed`
- **[orphan-route]** Route exists in the build but was never reached by crawling real links from the base URL.
  - URL: `/engage`

## Brand violations

### Deterministic (200) -- exit code non-zero

- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (27 node(s), impact: serious).
  - URL: `http://localhost:3000/`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['.text-\\(--slate\\).hover\\:text-ink[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (191 node(s), impact: serious).
  - URL: `http://localhost:3000/book`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold.font-display']; ['a[href="/people-tactics-and-strategy"] > .leading-relaxed.mb-3']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (18 node(s), impact: serious).
  - URL: `http://localhost:3000/ask`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .leading-relaxed.mb-3']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (22 node(s), impact: serious).
  - URL: `http://localhost:3000/about`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (19 node(s), impact: serious).
  - URL: `http://localhost:3000/people-tactics-and-strategy`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (19 node(s), impact: serious).
  - URL: `http://localhost:3000/training-and-development`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (23 node(s), impact: serious).
  - URL: `http://localhost:3000/first-call`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed']
- **[axe-label]** Form elements must have labels (5 node(s), impact: critical).
  - URL: `http://localhost:3000/first-call`
  - Detail: ['.mb-5:nth-child(4) > .border-gray-200[type="text"][value=""]']; ['.mb-5:nth-child(5) > .border-gray-200[type="text"][value=""]']; ['input[type="email"]']; ['input[type="tel"]']; ['textarea']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (19 node(s), impact: serious).
  - URL: `http://localhost:3000/executive-advisory`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/symptoms-states-and-why-the-distinction-matters`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/symptoms-states-and-why-the-distinction-matters`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (4 node(s), impact: serious).
  - URL: `http://localhost:3000/diagnostic`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['.text-xs']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (403 node(s), impact: serious).
  - URL: `http://localhost:3000/book/toc`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed.text-sm']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (5 node(s), impact: serious).
  - URL: `http://localhost:3000/book/toc`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']; ['.text-gray-500']; ['div:nth-child(1) > .text-\\[11px\\].text-gray-400.mb-2']; ['div:nth-child(2) > .text-\\[11px\\].text-gray-400.mb-2']; ['.mb-6']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (28 node(s), impact: serious).
  - URL: `http://localhost:3000/services`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['.hover\\:bg-field-raise.justify-center[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['.hover\\:bg-field-raise.justify-center[href="/people-tactics-and-strategy"] > .mb-3']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/services`
  - Detail: ['.text-gray-400']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (51 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/candor-as-an-organizational-variable`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/candor-as-an-organizational-variable`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (44 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/when-the-data-points-at-the-person-who-hired-you`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/when-the-data-points-at-the-person-who-hired-you`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (44 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-problem-they-brought-you-is-not-always-the-problem`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-problem-they-brought-you-is-not-always-the-problem`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (49 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/how-to-tell-if-the-organization-will-actually-change`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/how-to-tell-if-the-organization-will-actually-change`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (51 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/what-their-resistance-is-actually-telling-you`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/what-their-resistance-is-actually-telling-you`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (47 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness-conversation-framework`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness-conversation-framework`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (57 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (55 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/anchor`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/anchor`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (25 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/anchor-problem`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/anchor-problem`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (26 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/exit-calculation`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/exit-calculation`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (56 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/feedback-nobody-wants-to-say`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/feedback-nobody-wants-to-say`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (64 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/psychological-safety-walked-into-a-meeting`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/psychological-safety-walked-into-a-meeting`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (59 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/hr-is-the-table`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/hr-is-the-table`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (21 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/organizational-assessment`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/organizational-assessment`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (32 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/organizational-assessment-methodology`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/organizational-assessment-methodology`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (63 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/succession-planning`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/succession-planning`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (56 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/business-case`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/business-case`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (64 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/accountability`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/accountability`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (63 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/matrix-organization`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/matrix-organization`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (56 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/toxic-culture`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/toxic-culture`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (57 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (53 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/leadership-deafness`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/leadership-deafness`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (60 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/no-margin-for-error`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/no-margin-for-error`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (66 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/exit-pattern`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/exit-pattern`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (62 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-basement-standard`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-basement-standard`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (63 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/silosolation`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/silosolation`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (64 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (50 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/decision-paralysis`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/decision-paralysis`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (57 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-undefined-role`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-undefined-role`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (55 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-policy-lag`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-policy-lag`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (52 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-lost-map`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-lost-map`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (35 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/everyone-is-defensive-and-no-one-knows-why`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/everyone-is-defensive-and-no-one-knows-why`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (35 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/the-room-that-never-pushes-back`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/the-room-that-never-pushes-back`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (61 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/what-the-organization-decided-he-was-worth`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/what-the-organization-decided-he-was-worth`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (49 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/the-first-one-out-the-door`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/the-first-one-out-the-door`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (32 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/why-your-team-stopped-disagreeing-with-you`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/why-your-team-stopped-disagreeing-with-you`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (50 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/the-resignation-that-ended-a-department`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/the-resignation-that-ended-a-department`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (45 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/what-ready-didnt-include`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/what-ready-didnt-include`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (47 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/one-exception-at-a-time`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/one-exception-at-a-time`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (54 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/built-for-comfort`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/case_pattern/built-for-comfort`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (33 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/anatomy-of-resentment`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/anatomy-of-resentment`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (30 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/effectiveness-dies-in-darkness`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/effectiveness-dies-in-darkness`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (28 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/cost-of-flying-blind`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/cost-of-flying-blind`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (28 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/risk-of-family-friction`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/risk-of-family-friction`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (31 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/velocity-of-truth`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/velocity-of-truth`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (30 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/politeness-tax`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/politeness-tax`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (32 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/intellectual-bottleneck`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/intellectual-bottleneck`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (37 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/crisis-as-catalyst-for-clarity`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/crisis-as-catalyst-for-clarity`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (37 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (52 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-overloaded-manager`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-overloaded-manager`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (45 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unformed-leader`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unformed-leader`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (44 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-dormant-talent`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-dormant-talent`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/decision-blindness`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/decision-blindness`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (44 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/what-nobody-says`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/what-nobody-says`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (45 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/heard-and-ignored`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/heard-and-ignored`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-suppression-filter`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-suppression-filter`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/culture-drift`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/culture-drift`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (40 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-burned-credibility`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-burned-credibility`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (42 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/pay-exposure`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/pay-exposure`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (41 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/built-to-fail`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/built-to-fail`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (47 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-paper-tiger`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-paper-tiger`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (44 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unsolved-problem`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unsolved-problem`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-tolerated-violation`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-tolerated-violation`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unreported-hazard`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unreported-hazard`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unlocked-door`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unlocked-door`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (42 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/dueling-narratives`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/dueling-narratives`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/narrative-lock`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/narrative-lock`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (41 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-wrong-reward`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-wrong-reward`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/groundhog-day`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/groundhog-day`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (36 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-founders-grip`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-founders-grip`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (37 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/invisible-influence-architecture`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/invisible-influence-architecture`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (36 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-fracture`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-fracture`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (40 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/hr-capture`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/hr-capture`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (35 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/transition-paralysis`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/transition-paralysis`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (40 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-exposed`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-exposed`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (35 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-uninitiated`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-uninitiated`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (39 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/paper-shield`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/paper-shield`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (39 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-pay-fog`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-pay-fog`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (34 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-arbitrary-standard`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-arbitrary-standard`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (41 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unexamined-algorithm`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-unexamined-algorithm`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (38 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-second-close`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-second-close`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (34 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/invisible-burnout`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/invisible-burnout`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (34 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-culture-that-wasnt`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-culture-that-wasnt`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (39 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-inside-track`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-inside-track`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (40 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-diversity-ceiling`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > h2']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/methodology/the-diversity-ceiling`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (54 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/what-not-to-document`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/book/memo/what-not-to-document`
  - Detail: ['.md\\:inline-flex > .align-middle:nth-child(2)']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (43 node(s), impact: serious).
  - URL: `http://localhost:3000/about/story`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.text-sm.leading-relaxed']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (5 node(s), impact: serious).
  - URL: `http://localhost:3000/about/story`
  - Detail: ['.pb-16 > .text-xs.tracking-widest.uppercase']; ['.py-16:nth-child(2) > .text-xs.tracking-widest.uppercase']; ['.py-16:nth-child(3) > .text-xs.tracking-widest.uppercase']; ['.py-16:nth-child(4) > .text-xs.tracking-widest.uppercase']; ['.pt-16 > .text-xs.tracking-widest.uppercase']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (24 node(s), impact: serious).
  - URL: `http://localhost:3000/about/method`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .mb-3.leading-relaxed.text-sm']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (2 node(s), impact: serious).
  - URL: `http://localhost:3000/about/method`
  - Detail: ['.pb-16 > .text-xs.tracking-widest.uppercase']; ['.pt-16 > .text-xs.tracking-widest.uppercase']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (28 node(s), impact: serious).
  - URL: `http://localhost:3000/about/services`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['.hover\\:bg-field-raise.justify-center[href="/people-tactics-and-strategy"] > .text-lg.mb-2.font-semibold']; ['.hover\\:bg-field-raise.justify-center[href="/people-tactics-and-strategy"] > .mb-3']
- **[axe-color-contrast]** Elements must meet minimum color contrast ratio thresholds (1 node(s), impact: serious).
  - URL: `http://localhost:3000/about/services`
  - Detail: ['.text-gray-400']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (20 node(s), impact: serious).
  - URL: `http://localhost:3000/book/state/the-overloaded-manager`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .leading-relaxed.mb-3']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (20 node(s), impact: serious).
  - URL: `http://localhost:3000/book/state/the-founders-grip`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .leading-relaxed.mb-3']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (20 node(s), impact: serious).
  - URL: `http://localhost:3000/book/state/decision-paralysis`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .leading-relaxed.mb-3']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (20 node(s), impact: serious).
  - URL: `http://localhost:3000/book/state/paper-shield`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .leading-relaxed.mb-3']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (20 node(s), impact: serious).
  - URL: `http://localhost:3000/book/state/silosolation`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .leading-relaxed.mb-3']
- **[axe-color-contrast-enhanced]** Elements must meet enhanced color contrast ratio thresholds (20 node(s), impact: serious).
  - URL: `http://localhost:3000/book/state/the-broken-compass`
  - Detail: ['a[href$="book"]']; ['a[href$="ask"]']; ['a[href$="about"]']; ['a[href="/people-tactics-and-strategy"] > .text-lg.font-semibold']; ['a[href="/people-tactics-and-strategy"] > .leading-relaxed.mb-3']

## Content/principle violations

### Deterministic (5) -- exit code non-zero

- **[semicolon-in-copy]** Semicolon found in rendered copy (standing rule: no semicolons in any string or copy).
  - URL: `http://localhost:3000/book/methodology/candor-as-an-organizational-variable`
  - Detail: ...some legitimate methodological critique; the study was internal research rather...
- **[semicolon-in-copy]** Semicolon found in rendered copy (standing rule: no semicolons in any string or copy).
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness`
  - Detail: ...ed. If it doesn't, you weren't listening; you were waiting....
- **[semicolon-in-copy]** Semicolon found in rendered copy (standing rule: no semicolons in any string or copy).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...ocus now. Your skip-level said one thing; your direct manager said something diff...
- **[semicolon-in-copy]** Semicolon found in rendered copy (standing rule: no semicolons in any string or copy).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...erent; the all-hands said something vague enou...
- **[semicolon-in-copy]** Semicolon found in rendered copy (standing rule: no semicolons in any string or copy).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...adership support. One VP is enthusiastic; another is skeptical. The initiative be...

## Style nits (candidate tier -- review, not auto-fail)

### Candidate -- flagged for review (247)

- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book`
  - Detail: — not because anyone decided that, but through small, accumulated signals that added up to something legible: raising difficult things here costs more than stay
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book`
  - Detail: — and acting on it without checking first produces a specific kind of waste that organizations pay for, on a delay, in the next hire.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book`
  - Detail: — in one-on-ones, in hallway asides, in performance reviews that somehow, every cycle, come out fine.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book`
  - Detail: — investigated, addressed, formally closed.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book`
  - Detail: — physical, psychological, operational.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book`
  - Detail: — known, named, and sitting there unaddressed.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book`
  - Detail: — and then, without any single dramatic reversal, everything drifted back to almost exactly where it started.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book`
  - Detail: — the performance conversation, the commitment, the disagreement.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/ask`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/about`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/people-tactics-and-strategy`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/training-and-development`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/training-and-development`
  - Detail: ...MENT

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Mos...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/training-and-development`
  - Detail: ...oose the format second. Sometimes that's one person getting individual coaching through a specific transition. Sometimes it's a group sessi...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/first-call`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/executive-advisory`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/symptoms-states-and-why-the-distinction-matters`
  - Detail: — in the same place, with the same characteristics, often with the same people involved —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/symptoms-states-and-why-the-distinction-matters`
  - Detail: — it is real, it is painful, it matters —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/symptoms-states-and-why-the-distinction-matters`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (10, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/methodology/symptoms-states-and-why-the-distinction-matters`
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/toc`
  - Detail: ...posure

Compensation has drifted out of alignment with what the market is currently payin...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/toc`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/services`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/services`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/candor-as-an-organizational-variable`
  - Detail: — they are paying for it in measurable ways, through turnover, through lost productivity, through slower decisions made on worse information.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/candor-as-an-organizational-variable`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/when-the-data-points-at-the-person-who-hired-you`
  - Detail: — a behavior that has become load-bearing, a structural decision that served a different organization, a blind spot that has gone unnamed long enough to calcify
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/when-the-data-points-at-the-person-who-hired-you`
  - Detail: — a reframe that repositions the data, a silence that goes half a beat too long, an agreement that arrives too quickly to be real —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/when-the-data-points-at-the-person-who-hired-you`
  - Detail: — not colluding with them, not softening the data, but invested in what happens next —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/when-the-data-points-at-the-person-who-hired-you`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-problem-they-brought-you-is-not-always-the-problem`
  - Detail: ...become load-bearing. The problem is not alignment. It is architecture.

A department with...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/the-problem-they-brought-you-is-not-always-the-problem`
  - Detail: — the tension that has been building on the senior team, the turnover that keeps happening in the same department, the initiative that has stalled for the third
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/the-problem-they-brought-you-is-not-always-the-problem`
  - Detail: — who has already told the board it is a communication issue, or has already restructured the team around a theory about role clarity, or has already let someon
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/the-problem-they-brought-you-is-not-always-the-problem`
  - Detail: — and decide, with your help, what to do about what they are actually looking at.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-problem-they-brought-you-is-not-always-the-problem`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (10, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/methodology/the-problem-they-brought-you-is-not-always-the-problem`
- **[banned-jargon]** Banned/jargon term "actionable" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/how-to-tell-if-the-organization-will-actually-change`
  - Detail: ...ation. It will be useful to someone and actionable by no one.

The organization has named...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/how-to-tell-if-the-organization-will-actually-change`
  - Detail: — a senior leader, a longtime employee, occasionally the person who made the call —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/how-to-tell-if-the-organization-will-actually-change`
  - Detail: — honest, warm, clear-eyed about what the work requires —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/how-to-tell-if-the-organization-will-actually-change`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (10, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/methodology/how-to-tell-if-the-organization-will-actually-change`
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/what-their-resistance-is-actually-telling-you`
  - Detail: — who can say, in effect, "I think you know this is right, and I think what you are carrying right now is what comes next" —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/what-their-resistance-is-actually-telling-you`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness-conversation-framework`
  - Detail: — consistently, under pressure, when the other person is not making it easy —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness-conversation-framework`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness-conversation-framework`
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/methodology/earned-effectiveness`
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/anchor`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/anchor-problem`
  - Detail: — measured in decision velocity, in the initiatives that stall before they start, in the energy spent navigating around something that should not require naviga
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/anchor-problem`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/exit-calculation`
  - Detail: — a person, a structure, a decision, a cultural norm —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/exit-calculation`
  - Detail: — not manage the symptom, not accelerate hiring, not improve the offboarding experience.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/exit-calculation`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "robust" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/memo/feedback-nobody-wants-to-say`
  - Detail: ...Something about how organizations with robust feedback cultures outperform their peer...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/feedback-nobody-wants-to-say`
  - Detail: — for the giver, primarily, and for the receiver secondarily.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/feedback-nobody-wants-to-say`
  - Detail: — about a decision, a behavior, a pattern —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/feedback-nobody-wants-to-say`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/memo/feedback-nobody-wants-to-say`
- **[banned-jargon]** Banned/jargon term "stakeholder" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/memo/psychological-safety-walked-into-a-meeting`
  - Detail: ...ecause the roadmap is being driven by a stakeholder relationship rather than user evidence,...
- **[banned-jargon]** Banned/jargon term "stakeholder" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/memo/psychological-safety-walked-into-a-meeting`
  - Detail: ...the last person who pushed back on that stakeholder got quietly moved off the team.

The re...
- **[banned-jargon]** Banned/jargon term "robust" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/memo/psychological-safety-walked-into-a-meeting`
  - Detail: ...e for its impact on team performance is robust and consistent. This is an argument aga...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/psychological-safety-walked-into-a-meeting`
  - Detail: — highly regarded, technically excellent, genuinely difficult —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/psychological-safety-walked-into-a-meeting`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/memo/psychological-safety-walked-into-a-meeting`
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/hr-is-the-table`
  - Detail: — how clear they are, how honestly they are maintained, how well they match the actual capabilities and motivations of the people involved —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/hr-is-the-table`
  - Detail: — how leaders give feedback, how teams are structured, what behaviors are rewarded in practice rather than on paper, whether the organization actually believes 
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/hr-is-the-table`
  - Detail: — not rhetorically, but structurally, with real authority and real accountability —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/hr-is-the-table`
  - Detail: — of their agreements, their relationships, their capabilities, their motivations, and their willingness to work toward a shared purpose.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/hr-is-the-table`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/organizational-assessment`
  - Detail: — where the friction actually is, how it originates, what sustains it —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/organizational-assessment`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/organizational-assessment-methodology`
  - Detail: — not because the consultants are dishonest, but because the hypothesis shapes what gets looked at, who gets talked to, and what counts as a finding.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/organizational-assessment-methodology`
  - Detail: — specific enough that the organization can return to it, act on it, and hold itself accountable to it.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/organizational-assessment-methodology`
  - Detail: — clearly, without hedging, and without manufacturing significance to justify the engagement.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/organizational-assessment-methodology`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/succession-planning`
  - Detail: ...nt is the only thing that matters.

The Leverage Problem

Here's the part that connects...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/succession-planning`
  - Detail: ...tical role, the person in that role has leverage. Maybe they don't use it. Maybe they're...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/succession-planning`
  - Detail: ...ritory. And it's often preventable. The leverage that makes someone untouchable usually...
- **[banned-jargon]** Banned/jargon term "actionable" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/succession-planning`
  - Detail: ...l the team?

If the answer is clear and actionable, you're in better shape than most. If t...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/succession-planning`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/business-case`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/accountability`
  - Detail: ...rotected. Maybe it's tenure. Maybe it's leverage. Maybe it's a relationship with someone...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/accountability`
  - Detail: ...is ready to change that. Sometimes it's leverage that can be addressed. Sometimes it's a...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/accountability`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/matrix-organization`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/toxic-culture`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ...ier than addressing them.

The specific leverage varies: institutional history, technica...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ...by the person.

It usually starts with leverage. Real leverage, at first: they knew the...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ...It usually starts with leverage. Real leverage, at first: they knew the system, they h...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ...ver facing consequences.

Sometimes the leverage is technical. They're the only person w...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ...dge, and now it's stuck.

Sometimes the leverage is relational. They're close to the CEO...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ...cided it's not worth it.

Sometimes the leverage is just... vibes. They've been here for...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-untouchable`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/leadership-deafness`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/no-margin-for-error`
  - Detail: ..., you can do assessments. You can build alignment. You can roll out initiatives and measu...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/no-margin-for-error`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/exit-pattern`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-basement-standard`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/silosolation`
  - Detail: ...y has resolved. The calendar fills with alignment meetings. The actual work waits.

Dupli...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/silosolation`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...yone's a little burned out on the whole alignment thing. Let's just focus on execution an...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...se it failed but because it ran into an alignment problem that existed before it started....
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...n latency. Every decision that requires alignment across leadership takes forever. The de...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...disagreement. The calendar fills with "alignment" meetings. The actual alignment never a...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...s with "alignment" meetings. The actual alignment never arrives.

What Actually Resolves...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-broken-compass`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/decision-paralysis`
  - Detail: ...ifferent framing and a request for more alignment that never quite arrives.

It doesn't f...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/decision-paralysis`
  - Detail: ...d also nothing ever changes, that's not alignment. That's Decision Paralysis.

The same d...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/decision-paralysis`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-undefined-role`
  - Detail: ...ligned because the systems don't create alignment automatically. The time people spend fi...
- **[banned-jargon]** Banned/jargon term "bandwidth" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-undefined-role`
  - Detail: ...d everyone knows it, and nobody has the bandwidth to fix it.

The People Who Absorb It

T...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-undefined-role`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-policy-lag`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-lost-map`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/everyone-is-defensive-and-no-one-knows-why`
  - Detail: — not because anyone decided that, but through small, accumulated signals that added up to something legible: raising difficult things here costs more than stay
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/everyone-is-defensive-and-no-one-knows-why`
  - Detail: — through small, accumulated signals, each one individually defensible, that added up to something legible: raising difficult things here costs more than stayin
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/everyone-is-defensive-and-no-one-knows-why`
  - Detail: — carefully, over time, by people who learned that showing leadership what it actually looks like was not worth the risk.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/everyone-is-defensive-and-no-one-knows-why`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/memo/everyone-is-defensive-and-no-one-knows-why`
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/the-room-that-never-pushes-back`
  - Detail: — not dramatically, not with any obvious consequence, but in a way that the person who raised it felt.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/the-room-that-never-pushes-back`
  - Detail: — a decision revisited, an assumption named and abandoned, a direction adjusted in real time because someone in the room said something true that you hadn't con
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/the-room-that-never-pushes-back`
  - Detail: — no hard conversations, no real resistance, nothing that genuinely surprised you —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/the-room-that-never-pushes-back`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/memo/the-room-that-never-pushes-back`
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/case_pattern/what-the-organization-decided-he-was-worth`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/case_pattern/the-first-one-out-the-door`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/case_pattern/the-first-one-out-the-door`
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/why-your-team-stopped-disagreeing-with-you`
  - Detail: — through the small signals that leadership sends, consistently, over time, about what kind of input is actually welcome.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/why-your-team-stopped-disagreeing-with-you`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (10, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/memo/why-your-team-stopped-disagreeing-with-you`
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/the-resignation-that-ended-a-department`
  - Detail: — got a call from someone new, someone who did not know the history, someone who treated the arrangement as a transaction rather than a relationship.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/the-resignation-that-ended-a-department`
  - Detail: — the judgment calls, the relationship management, the load-bearing informality that kept things moving —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/case_pattern/the-resignation-that-ended-a-department`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/what-ready-didnt-include`
  - Detail: — an all-hands announcement, slides prepared in advance, a Q&A that had the careful energy of a conversation where the important decisions have already been mad
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/what-ready-didnt-include`
  - Detail: — accurate information, correctly identified, traveling through a channel that slowed it to the point of irrelevance —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/case_pattern/what-ready-didnt-include`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/one-exception-at-a-time`
  - Detail: — they still produced them, still presented them, still filed them in the places plans get filed.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/one-exception-at-a-time`
  - Detail: — through accumulated evidence, over time, one decision at a time.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/one-exception-at-a-time`
  - Detail: — compelling, adjacent, lucrative —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/one-exception-at-a-time`
  - Detail: — and so the leader has already built the structures that make hearing it survivable, and acting on it possible, before the resignation letter arrives.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/case_pattern/one-exception-at-a-time`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/built-for-comfort`
  - Detail: — and that they cannot tell the difference, from inside the room, between a team that agrees and a team that has learned to agree.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/case_pattern/built-for-comfort`
  - Detail: — and who built, without intending to, a room that stopped offering it.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/case_pattern/built-for-comfort`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/anatomy-of-resentment`
  - Detail: — teams that function well argue about strategy, push back on decisions, and navigate competing priorities without the underlying relationships deteriorating.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/anatomy-of-resentment`
  - Detail: — they note it, adjust their posture slightly, and move on.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/anatomy-of-resentment`
  - Detail: — careful, pleasant, emptied of anything that matters.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/anatomy-of-resentment`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/effectiveness-dies-in-darkness`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/memo/cost-of-flying-blind`
  - Detail: ...ds as consensus. But consensus is about alignment on what was decided — what specifically...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/memo/cost-of-flying-blind`
  - Detail: ...-making process produced the feeling of alignment without the substance of it, and the or...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/cost-of-flying-blind`
  - Detail: — what specifically, what it means for each person to act on it, what it would look like if they were doing it wrong.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/cost-of-flying-blind`
  - Detail: — the market shifted, the timeline was unrealistic, the team didn't execute —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/cost-of-flying-blind`
  - Detail: — stalling execution, failing cross-functional coordination, contradictory direction reaching the mid-level teams —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/cost-of-flying-blind`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "alignment" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/memo/risk-of-family-friction`
  - Detail: ...rity structure are almost always out of alignment, and everyone in the organization knows...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/risk-of-family-friction`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/velocity-of-truth`
  - Detail: — known but not acted on, surfaced but not escalated, visible but not named —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/velocity-of-truth`
  - Detail: — is that the messenger gets blamed, that being the bearer of bad news creates association with the news itself, that raising something that implicates a senior
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/velocity-of-truth`
  - Detail: — that the messenger is not blamed, that the truth doesn't create association with the problem, that early signals are rewarded rather than punished —
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/velocity-of-truth`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/politeness-tax`
  - Detail: — which requires naming who it isn't working for, and why, and what specifically needs to change.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/politeness-tax`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/intellectual-bottleneck`
  - Detail: — they see patterns others miss, make decisions quickly and accurately, and have a track record that justifies the confidence they carry.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/intellectual-bottleneck`
  - Detail: — because thinking at that level and bringing it to the leader has a documented outcome: the leader already has a view, the leader's view prevails, and the thin
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/intellectual-bottleneck`
  - Detail: — these functions, which are essential to leadership, degrade under conditions of sustained power.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/intellectual-bottleneck`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "bandwidth" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/crisis-as-catalyst-for-clarity`
  - Detail: ...anization cannot afford while consuming bandwidth the leadership team needs for something...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/crisis-as-catalyst-for-clarity`
  - Detail: — executives departing, client relationships in question, board patience exhausted, revenue dropping in ways that can no longer be explained away —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/crisis-as-catalyst-for-clarity`
  - Detail: — the professional courtesy, the careful language, the way difficult truths get managed rather than named —
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/crisis-as-catalyst-for-clarity`
  - Detail: — specific leaders whose behavior is blocking the path forward, specific relationships that have broken in ways that cannot be repaired within the current struc
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/crisis-as-catalyst-for-clarity`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/methodology/crisis-as-catalyst-for-clarity`
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem`
  - Detail: — and acting on it without checking first produces a specific kind of waste that organizations pay for, on a delay, in the next hire.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem`
  - Detail: — the pilot, the surgeon, the operator.
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem`
  - Detail: — draws a hard line between two different things: the visible action that happened right before the failure, and the conditions, built years earlier by people w
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem`
  - Detail: — this really was about them," that's a real finding, and it should lead somewhere.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[emdash-cap-exceeded]** Em-dash count (9, signature line excluded) exceeds the /book editorial cap of 8 per piece.
  - URL: `http://localhost:3000/book/methodology/why-blaming-the-person-almost-never-fixes-the-problem`
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-overloaded-manager`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "move the needle" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-unformed-leader`
  - Detail: ....

Development was attempted and didn't move the needle. This is what separates Unformed Leader...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-unformed-leader`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-dormant-talent`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/decision-blindness`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/what-nobody-says`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/heard-and-ignored`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-suppression-filter`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/culture-drift`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "move the needle" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-burned-credibility`
  - Detail: ...s might even be accurate. They will not move the needle, because the workforce isn't actually d...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-burned-credibility`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/pay-exposure`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/built-to-fail`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "going forward" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-paper-tiger`
  - Detail: ...write what's actually true. That helps going forward, but it doesn't retroactively repair th...
- **[banned-jargon]** Banned/jargon term "going forward" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-paper-tiger`
  - Detail: ...s.

Step two: create a real-time record going forward. From this point, every conversation ab...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/the-paper-tiger`
  - Detail: — in one-on-ones, in hallway asides, in performance reviews that somehow, every cycle, come out fine.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-paper-tiger`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/the-unsolved-problem`
  - Detail: — investigated, addressed, formally closed.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-unsolved-problem`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-tolerated-violation`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/the-unreported-hazard`
  - Detail: — physical, psychological, operational.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-unreported-hazard`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/the-unlocked-door`
  - Detail: — known, named, and sitting there unaddressed.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-unlocked-door`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/dueling-narratives`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "stakeholder" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/narrative-lock`
  - Detail: ...the story can no longer explain away, a stakeholder the story stops working on, a consequen...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/narrative-lock`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-wrong-reward`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/methodology/groundhog-day`
  - Detail: — and then, without any single dramatic reversal, everything drifted back to almost exactly where it started.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/groundhog-day`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-founders-grip`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/invisible-influence-architecture`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-fracture`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/hr-capture`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/transition-paralysis`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-exposed`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-uninitiated`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/paper-shield`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-pay-fog`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "going forward" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-arbitrary-standard`
  - Detail: ...hat it will actually be enforced evenly going forward, and a restated policy statement offers...
- **[banned-jargon]** Banned/jargon term "going forward" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-arbitrary-standard`
  - Detail: ...equires visible, consistent enforcement going forward, including, and especially and specific...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-arbitrary-standard`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-unexamined-algorithm`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "leverage" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-second-close`
  - Detail: ...vor whichever side had more negotiating leverage during the original deal, rather than f...
- **[banned-jargon]** Banned/jargon term "going forward" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-second-close`
  - Detail: ...ly better for the combined organization going forward.

Two Companies, One Name

Two entirely...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-second-close`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/invisible-burnout`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "going forward" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-culture-that-wasnt`
  - Detail: ...se the organization claims about itself going forward....
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-culture-that-wasnt`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[banned-jargon]** Banned/jargon term "going forward" found (source: engine/output_synthesis.py system prompt).
  - URL: `http://localhost:3000/book/methodology/the-inside-track`
  - Detail: ...ard actually being able to enforce them going forward.

Second, audit recent actual promotion...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-inside-track`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/methodology/the-diversity-ceiling`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/memo/what-not-to-document`
  - Detail: — the performance conversation, the commitment, the disagreement.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/memo/what-not-to-document`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/about/story`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/about/method`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/about/services`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/about/services`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/state/the-overloaded-manager`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/state/the-founders-grip`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/state/decision-paralysis`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[appositive-emdash-list]** Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.
  - URL: `http://localhost:3000/book/state/paper-shield`
  - Detail: — the performance conversation, the commitment, the disagreement.
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/state/paper-shield`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/state/silosolation`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
- **[coaching-as-noun]** "Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.
  - URL: `http://localhost:3000/book/state/the-broken-compass`
  - Detail: ...ment

Training built around what your people actually need: individual coaching, group sessions, or work co-led with your own leaders.

Lea...
