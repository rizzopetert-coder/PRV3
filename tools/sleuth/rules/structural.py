"""
tools/sleuth/rules/structural.py -- 404s, redirect loops, orphans, dead
ends. All DETERMINISTIC tier (auto-fail) per the build brief.

Dead-end detection, a real limitation flagged rather than hidden: a page
counts as reachable-but-not-a-dead-end if it has at least one same-origin
<a href> link OR at least one <button> element anywhere on the page. The
button check is a coarse proxy for "has a CTA" -- it does not confirm the
button actually navigates anywhere (a JS-driven CTA that fetches and stays
on-page, like /first-call's "Send to Pete" submit button, would pass this
check even though it isn't a navigation dead end in the site-structure
sense, which is correct; a genuinely decorative, non-functional button
would also pass, which is a false negative this tier accepts rather than
risk auto-failing real, working interactive pages that just don't happen
to use a plain <a> tag for their CTA).
"""
from __future__ import annotations

from urllib.parse import urlparse

from tools.sleuth.rules.finding import Category, Finding, Tier
from tools.sleuth.route_manifest import RouteManifest

REDIRECT_STATUS_RANGE = range(300, 400)


def _path_of(url: str) -> str:
    p = urlparse(url).path
    if len(p) > 1 and p.endswith("/"):
        p = p[:-1]
    return p or "/"


def check(crawl: dict, route_manifest: RouteManifest, max_pages_hit: bool) -> list[Finding]:
    findings: list[Finding] = []
    pages = crawl.get("pages", [])
    base_origin = urlparse(crawl["baseUrl"]).netloc

    crawled_paths = set()

    for page in pages:
        url = page["url"]
        crawled_paths.add(_path_of(url))
        status = page.get("status")
        nav_error = page.get("navError")

        if nav_error:
            lowered = nav_error.lower()
            if "too_many_redirects" in lowered or "err_too_many_redirects" in lowered:
                findings.append(Finding(
                    tier=Tier.DETERMINISTIC, category=Category.STRUCTURAL,
                    rule_id="redirect-loop",
                    message="Redirect loop detected (browser gave up following redirects).",
                    url=url, detail=nav_error,
                ))
            else:
                findings.append(Finding(
                    tier=Tier.DETERMINISTIC, category=Category.STRUCTURAL,
                    rule_id="navigation-error",
                    message="Navigation failed (timeout, DNS, connection refused, or similar).",
                    url=url, detail=nav_error,
                ))
            continue

        if status is not None and status >= 400:
            findings.append(Finding(
                tier=Tier.DETERMINISTIC, category=Category.STRUCTURAL,
                rule_id="http-error-status",
                message=f"HTTP {status} response.",
                url=url,
            ))

        redirect_chain = page.get("redirectChain") or []
        if redirect_chain and len(set(redirect_chain)) < len(redirect_chain):
            findings.append(Finding(
                tier=Tier.DETERMINISTIC, category=Category.STRUCTURAL,
                rule_id="redirect-loop",
                message="Redirect chain revisits a URL it already passed through.",
                url=url, detail=" -> ".join(redirect_chain),
            ))

        links = page.get("links") or []
        has_internal_link = any(
            not l["href"].strip().startswith(("mailto:", "tel:", "javascript:", "#"))
            and (l["href"].startswith("/") or base_origin in l["href"] or not l["href"].startswith("http"))
            for l in links
        )
        has_button = "button" in {cs.get("tag") for cs in (page.get("computedStyles") or [])}
        if not has_internal_link and not has_button and status and status < 400 and not nav_error:
            findings.append(Finding(
                tier=Tier.DETERMINISTIC, category=Category.STRUCTURAL,
                rule_id="dead-end",
                message="Terminal page: no outbound internal link and no button/CTA found.",
                url=url,
            ))

    if max_pages_hit:
        findings.append(Finding(
            tier=Tier.CANDIDATE, category=Category.STRUCTURAL,
            rule_id="crawl-truncated",
            message=(
                "Crawl hit its max-pages cap before exhausting the BFS frontier -- "
                "orphan detection below may be incomplete (a route could look like "
                "an orphan simply because the crawl stopped before reaching it, not "
                "because nothing links to it). Re-run with a higher --max-pages if "
                "this matters for this run."
            ),
        ))
    else:
        orphans = sorted(
            p for p in route_manifest.static_routes
            if p not in crawled_paths and route_manifest.is_orphan_candidate(p)
        )
        for path in orphans:
            findings.append(Finding(
                tier=Tier.DETERMINISTIC, category=Category.STRUCTURAL,
                rule_id="orphan-route",
                message="Route exists in the build but was never reached by crawling real links from the base URL.",
                url=path,
            ))

    return findings
