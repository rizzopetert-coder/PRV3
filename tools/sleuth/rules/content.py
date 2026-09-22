"""
tools/sleuth/rules/content.py -- semicolons, "--" em-dash placeholders,
literal "PCD"/"Presenting Complaint Displacement", and shadow-model
name/entity leaks. All DETERMINISTIC tier per the build brief and
CLAUDE.md's own standing rules (no semicolons, no "--" placeholder, no
coined terms/jargon needing a glossary).

Scans `page.textContent` (document.body.innerText, rendered/visible text
only -- not raw HTML, so hidden metadata, comments, or script content
never trip these checks).

SHADOW-MODEL CHECK: searches for \\brizzo\\b and \\bonedigital\\b
(word-boundary, case-insensitive) -- not a bare "pete" substring, which
would false-positive on ordinary words containing that substring (e.g.
"competed", "repeated"). Confirmed exemptions (tools/sleuth/config.py)
are applied first: any exempted string is stripped from the text before
the forbidden-name scan runs, and exempted routes are skipped entirely.
"""
from __future__ import annotations

import re

from tools.sleuth.config import (
    SHADOW_MODEL_EXEMPT_ROUTE_PREFIXES,
    SHADOW_MODEL_EXEMPT_STRINGS,
)
from tools.sleuth.rules.finding import Category, Finding, Tier

_SEMICOLON_RE = re.compile(r"[^\n]{0,40};[^\n]{0,40}")
_DASH_PLACEHOLDER_RE = re.compile(r".{0,40}\s--\s.{0,40}")
_PCD_RE = re.compile(r"\bPCD\b|Presenting Complaint Displacement", re.IGNORECASE)
_FORBIDDEN_NAME_RE = re.compile(r"\brizzo\b|\bonedigital\b", re.IGNORECASE)


def _is_exempt_route(url: str) -> bool:
    return any(prefix in url for prefix in SHADOW_MODEL_EXEMPT_ROUTE_PREFIXES)


def _strip_exemptions(text: str) -> str:
    for exempt in SHADOW_MODEL_EXEMPT_STRINGS:
        text = text.replace(exempt, "")
    return text


def check(crawl: dict) -> list[Finding]:
    findings: list[Finding] = []

    for page in crawl.get("pages", []):
        url = page["url"]
        if page.get("navError"):
            continue
        text = page.get("textContent") or ""
        if not text:
            continue

        for m in _SEMICOLON_RE.finditer(text):
            findings.append(Finding(
                tier=Tier.DETERMINISTIC, category=Category.CONTENT,
                rule_id="semicolon-in-copy",
                message="Semicolon found in rendered copy (standing rule: no semicolons in any string or copy).",
                url=url, detail=f"...{m.group(0).strip()}...",
            ))

        for m in _DASH_PLACEHOLDER_RE.finditer(text):
            findings.append(Finding(
                tier=Tier.DETERMINISTIC, category=Category.CONTENT,
                rule_id="dash-placeholder",
                message='Literal "--" found where a real em-dash (or a comma/colon/rephrase) belongs (standing rule: never a "--" placeholder).',
                url=url, detail=f"...{m.group(0).strip()}...",
            ))

        for m in _PCD_RE.finditer(text):
            findings.append(Finding(
                tier=Tier.DETERMINISTIC, category=Category.CONTENT,
                rule_id="internal-acronym-leak",
                message='Internal acronym "PCD"/"Presenting Complaint Displacement" found in client-facing copy.',
                url=url, detail=m.group(0),
            ))

        if not _is_exempt_route(url):
            scrubbed = _strip_exemptions(text)
            for m in _FORBIDDEN_NAME_RE.finditer(scrubbed):
                start = max(0, m.start() - 40)
                end = min(len(scrubbed), m.end() + 40)
                findings.append(Finding(
                    tier=Tier.DETERMINISTIC, category=Category.CONTENT,
                    rule_id="shadow-model-name-leak",
                    message="Personal name or affiliated-entity reference found on a commercial-surface/client-facing page (shadow-model rule).",
                    url=url, detail=f"...{scrubbed[start:end].strip()}...",
                ))

    return findings
