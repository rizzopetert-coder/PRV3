"""
Compile-only (no rewording): regenerates content-candidate-review-packet.md
from a saved sleuth crawl, using the newly-tightened candidate.py heuristic
(finite-verb filter, 79 -> 22 appositive-emdash-list hits). Same extraction
approach as the prior packet -- full paragraph context, grouped by page,
appositive-emdash-list + coaching-as-noun only. Review only, does not touch
any content file.

Usage:
    python tools/generate_candidate_review_packet.py
"""
import json
import pathlib
import sys

sys.path.insert(0, '.')
from tools.sleuth.rules import candidate

RAW_PATH = pathlib.Path('tools/sleuth/output/sleuth_raw.json')
OUT_PATH = pathlib.Path('content-candidate-review-packet.md')


def paragraph_containing(text: str, snippet: str) -> str:
    # finding.detail is pre-truncated with leading/trailing "..." markers and
    # collapsed whitespace -- strip those and use the longest contiguous
    # word-run as the actual search key, since the raw ellipsis-wrapped
    # string never matches verbatim against page_text.
    core = snippet.strip()
    for marker in ("...", "…"):
        if core.startswith(marker):
            core = core[len(marker):]
        if core.endswith(marker):
            core = core[:-len(marker)]
    core = core.strip()
    # collapse whitespace the same way the page text likely isn't collapsed --
    # search for the longest slice that still finds a hit.
    idx = -1
    probe = core
    while probe and idx == -1:
        idx = text.find(probe)
        if idx == -1:
            # shrink from both ends toward the middle to survive whitespace
            # differences at the truncation boundary
            probe = probe[1:] if len(probe) > 20 else ''
    if idx == -1:
        return '[paragraph not located verbatim in page text -- see snippet above]'
    start = text.rfind("\n", 0, idx)
    start = 0 if start == -1 else start + 1
    end = text.find("\n", idx + len(probe))
    end = len(text) if end == -1 else end
    para = text[start:end].strip()
    return para if para else '[paragraph not located verbatim in page text -- see snippet above]'


def main():
    crawl = json.loads(RAW_PATH.read_text(encoding='utf-8'))
    findings = candidate.check(crawl)

    theme = crawl.get('theme')
    page_count = crawl.get('pageCount')
    if theme and page_count is not None:
        source_desc = f'fresh full-site crawl, {theme.capitalize()} theme, {page_count} pages'
    elif theme:
        source_desc = f'fresh full-site crawl, {theme.capitalize()} theme'
    elif page_count is not None:
        source_desc = f'fresh full-site crawl, {page_count} pages'
    else:
        source_desc = 'fresh full-site crawl'

    relevant = [f for f in findings if f.rule_id in ('appositive-emdash-list', 'coaching-as-noun')]

    by_page: dict[str, dict[str, list]] = {}
    page_text_by_url = {p['url']: (p.get('textContent') or '') for p in crawl.get('pages', [])}

    for f in relevant:
        by_page.setdefault(f.url, {'appositive-emdash-list': [], 'coaching-as-noun': []})
        by_page[f.url][f.rule_id].append(f)

    appositive_total = sum(1 for f in relevant if f.rule_id == 'appositive-emdash-list')
    coaching_total = sum(1 for f in relevant if f.rule_id == 'coaching-as-noun')

    lines = []
    lines.append('# Content Candidate Review Packet (regenerated)')
    lines.append('')
    lines.append(f'Source: {source_desc}, post finite-verb-filter '
                  'heuristic tightening (tools/sleuth/rules/candidate.py).')
    lines.append('')
    lines.append(f'- appositive-emdash-list: {appositive_total} hits (was 79 before this pass '
                  '-- 57 filtered as clause-parallelism, not genuine lists)')
    lines.append(f'- coaching-as-noun: {coaching_total} hits')
    lines.append(f'- Pages with at least one hit: {len(by_page)}')
    lines.append('')
    lines.append('Review only. Nothing reworded. Grouped by page, full paragraph context per hit. '
                  'Duplicate hits (same exact snippet repeated on the same page, e.g. a teaser '
                  'reused via related-content) are shown once per page with a repeat count noted.')
    lines.append('')
    lines.append('---')
    lines.append('')

    for url in sorted(by_page.keys()):
        hits = by_page[url]
        page_text = page_text_by_url.get(url, '')
        total_hits = len(hits['appositive-emdash-list']) + len(hits['coaching-as-noun'])
        if total_hits == 0:
            continue
        lines.append(f'## {url}')
        lines.append('')

        if hits['appositive-emdash-list']:
            lines.append(f'### appositive-emdash-list ({len(hits["appositive-emdash-list"])})')
            lines.append('')
            seen_snippets: dict[str, int] = {}
            order: list[str] = []
            for f in hits['appositive-emdash-list']:
                snippet = f.detail or ''
                if snippet not in seen_snippets:
                    seen_snippets[snippet] = 0
                    order.append(snippet)
                seen_snippets[snippet] += 1
            for snippet in order:
                count = seen_snippets[snippet]
                para = paragraph_containing(page_text, snippet)
                suffix = f' (repeated {count}x on this page)' if count > 1 else ''
                lines.append(f'**Snippet:** {snippet}{suffix}')
                lines.append('')
                lines.append(f'**Paragraph:** {para}')
                lines.append('')

        if hits['coaching-as-noun']:
            lines.append(f'### coaching-as-noun ({len(hits["coaching-as-noun"])})')
            lines.append('')
            seen_snippets = {}
            order = []
            for f in hits['coaching-as-noun']:
                snippet = f.detail or ''
                if snippet not in seen_snippets:
                    seen_snippets[snippet] = 0
                    order.append(snippet)
                seen_snippets[snippet] += 1
            for snippet in order:
                count = seen_snippets[snippet]
                para = paragraph_containing(page_text, snippet)
                suffix = f' (repeated {count}x on this page)' if count > 1 else ''
                lines.append(f'**Snippet:** {snippet}{suffix}')
                lines.append('')
                lines.append(f'**Paragraph:** {para}')
                lines.append('')

        lines.append('---')
        lines.append('')

    OUT_PATH.write_text('\n'.join(lines), encoding='utf-8')
    print(f'Wrote {OUT_PATH} -- {appositive_total} appositive-emdash-list, {coaching_total} coaching-as-noun, {len(by_page)} pages.')


if __name__ == '__main__':
    main()
