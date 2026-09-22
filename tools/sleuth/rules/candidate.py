"""
tools/sleuth/rules/candidate.py -- CANDIDATE tier only (logged in
sleuth_report.md, never auto-fail, never affects exit code): banned
jargon, the appositive em-dash construction, "coaching" as a noun/
adjective, and the /book em-dash-per-piece cap.

KNOWN GAP, flagged rather than faked: the build brief also asked for
"possible coined-term hits (P-10)". P-10 (tools/_mob.txt / the
Principal Brief) is the *rule* ("no coined terms") -- it is not itself
a list of specific coined terms to search for, and no such list exists
anywhere in this repo. A keyword search needs keywords; inventing a
plausible-looking heuristic (e.g. flagging Title Case or hyphenated
compounds) would mostly generate noise, not real signal, and would
misrepresent this as a working check when it isn't grounded in
anything real. This function does not implement a coined-term scan --
it's a genuine gap, not a silent one, and the report/README both say so
explicitly rather than shipping a fake heuristic under a real-looking
label.
"""
from __future__ import annotations

import re

from tools.sleuth.config import GLOSSARY_EXEMPT_ROUTE_PREFIXES, load_banned_jargon
from tools.sleuth.rules.finding import Category, Finding, Tier

# Matches ANY em-dash-to-terminator span containing a comma -- deliberately
# loose at the regex stage. The real filter is the comma-count check in
# check() below: a genuine appositive list ("your policies -- handbook,
# documentation, compliance obligations", CLAUDE.md's own example) has at
# least 2 commas (3+ items). A single comma inside a dash span is far more
# often an ordinary two-clause interruption ("-- not because X, but because
# Y", a permitted CLAUDE.md em-dash use), which the original version of this
# regex couldn't tell apart -- confirmed directly against the last real test
# run, where 15 of 17 hits were exactly that pattern, not appositive lists.
_APPOSITIVE_EMDASH_RE = re.compile(r"—([^—.]*,[^—.]*)(—|\.)")
_MIN_COMMAS_FOR_APPOSITIVE_LIST = 2
_COACHING_NOUN_RE = re.compile(
    r"\b(a|the|some|individual|group|executive|one-on-one)\s+coaching\b"
    r"|\bcoaching\s+(session|program|call|engagement|package)\b",
    re.IGNORECASE,
)
_BOOK_PIECE_PATH_RE = re.compile(r"/book/(memo|methodology|case_pattern)/")
_EMDASH_CAP = 8
_SIGNATURE_LINE_RE = re.compile(r"—\s*Principal Resolution\s*$")


def _is_glossary_exempt(url: str) -> bool:
    return any(url.startswith(prefix) or prefix in url for prefix in GLOSSARY_EXEMPT_ROUTE_PREFIXES)


def check(crawl: dict) -> list[Finding]:
    findings: list[Finding] = []
    banned_jargon = load_banned_jargon()
    jargon_patterns = [(term, re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)) for term in banned_jargon]

    for page in crawl.get("pages", []):
        url = page["url"]
        if page.get("navError"):
            continue
        text = page.get("textContent") or ""
        if not text:
            continue

        if not _is_glossary_exempt(url):
            for term, pattern in jargon_patterns:
                for m in pattern.finditer(text):
                    start = max(0, m.start() - 40)
                    end = min(len(text), m.end() + 40)
                    findings.append(Finding(
                        tier=Tier.CANDIDATE, category=Category.STYLE,
                        rule_id="banned-jargon",
                        message=f'Banned/jargon term "{term}" found (source: engine/output_synthesis.py system prompt).',
                        url=url, detail=f"...{text[start:end].strip()}...",
                    ))

        for m in _APPOSITIVE_EMDASH_RE.finditer(text):
            span_text = m.group(1)
            if span_text.count(",") < _MIN_COMMAS_FOR_APPOSITIVE_LIST:
                continue  # a single comma is almost always a two-clause interruption, not a list
            findings.append(Finding(
                tier=Tier.CANDIDATE, category=Category.STYLE,
                rule_id="appositive-emdash-list",
                message='Possible em-dash-set-off list construction -- CLAUDE.md prefers "(such as X, Y, and Z)" for multi-item appositive lists. Heuristic match, needs human/AI review, not auto-fail.',
                url=url, detail=m.group(0).strip()[:160],
            ))

        for m in _COACHING_NOUN_RE.finditer(text):
            start = max(0, m.start() - 60)
            end = min(len(text), m.end() + 60)
            findings.append(Finding(
                tier=Tier.CANDIDATE, category=Category.STYLE,
                rule_id="coaching-as-noun",
                message='"Coaching" used as a noun/adjective rather than a verb -- flagged for review per brand voice guidance.',
                url=url, detail=f"...{text[start:end].strip()}...",
            ))

        if _BOOK_PIECE_PATH_RE.search(url):
            emdash_count = text.count("—")
            if _SIGNATURE_LINE_RE.search(text.strip()):
                emdash_count -= 1
            if emdash_count > _EMDASH_CAP:
                findings.append(Finding(
                    tier=Tier.CANDIDATE, category=Category.STYLE,
                    rule_id="emdash-cap-exceeded",
                    message=f"Em-dash count ({emdash_count}, signature line excluded) exceeds the /book editorial cap of {_EMDASH_CAP} per piece.",
                    url=url,
                ))

    return findings
