"""
tools/sleuth/config.py -- the two exemption lists the build brief called
out as unverified, plus the banned-jargon list extracted live from its
real source rather than hand-copied.

GLOSSARY EXEMPTION: the brief assumed a src/data/glossary.json-rendered
route exists to exempt from the banned-jargon check ("the glossary
literally defines and critiques these words"). Confirmed directly before
writing this file: no such path exists anywhere in this repo (no top-
level src/ directory at all), and the only "glossary" hit in the whole
codebase is an unrelated code comment describing a <dl> markup pattern
on book/toc/page.tsx as "a real glossary structure." There is currently
no page whose purpose is naming/critiquing these specific terms.
GLOSSARY_EXEMPT_ROUTE_PREFIXES is therefore empty today -- a real,
confirmed absence, not a stand-in for something this tool failed to
find. Left as a live, editable list (not deleted) so it activates
immediately if such a page is ever built, without needing to touch the
candidate-tier rule logic again.

SHADOW_MODEL_EXEMPT_STRINGS: the brief assumed a "known shadow-model
exceptions" list exists to check against. Confirmed: CLAUDE.md and
Engage_Protocol_AI_Engineering_Instructions.md both state the rule
("no personal name, no affiliated entity reference in any copy that
will appear on the commercial surface or in client-facing materials")
but neither enumerates exceptions. One real, live exception was found
during this build and confirmed with Pete: pete@principalresolution.com
appears in /first-call's own error-state copy ("reach out directly at
pete@principalresolution.com"), a genuine, necessary contact point, not
an oversight -- seeded here as the one confirmed entry. Anything else
that should be exempt (a footer copyright line, an admin-only page,
etc.) needs the same explicit confirmation before being added -- this
is a deterministic (auto-fail) tier check, so an unconfirmed guess here
risks either hiding a real violation or false-failing legitimate copy.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_SYNTHESIS_PATH = REPO_ROOT / "engine" / "output_synthesis.py"

GLOSSARY_EXEMPT_ROUTE_PREFIXES: tuple[str, ...] = ()

SHADOW_MODEL_EXEMPT_STRINGS: tuple[str, ...] = (
    "pete@principalresolution.com",
)

# Routes that are internal/admin tooling, never commercial-surface or
# client-facing -- the shadow-model rule's own stated scope excludes them
# by definition, not by a separate carve-out. Kept explicit rather than
# relying on the same EXCLUDED_PREFIXES route_manifest.py uses for a
# different purpose (orphan detection), since the two lists answer
# different questions and could diverge legitimately.
SHADOW_MODEL_EXEMPT_ROUTE_PREFIXES: tuple[str, ...] = (
    "/first-call/admin",
)

_BANNED_PHRASE_BLOCK_RE = re.compile(
    r"Banned words and phrases:\s*(.*?)\.\s*\n\s*\n", re.DOTALL
)


def load_banned_jargon() -> tuple[str, ...]:
    """
    Extracted live from engine/output_synthesis.py's
    OUTPUT_SYNTHESIS_SYSTEM_PROMPT rather than duplicated by hand, so this
    list can never silently drift from the real system prompt it's meant
    to mirror. "leverage (as a verb)" is normalized to the bare word
    "leverage" -- true verb-vs-noun part-of-speech detection is out of
    scope for a simple substring scan; every "leverage" hit is flagged
    for review (this is a candidate-tier check, never auto-fail), and a
    human/AI reviewer resolves the noun/verb question the substring match
    can't.
    """
    if not OUTPUT_SYNTHESIS_PATH.exists():
        raise FileNotFoundError(f"{OUTPUT_SYNTHESIS_PATH} not found")
    src = OUTPUT_SYNTHESIS_PATH.read_text(encoding="utf-8")
    match = _BANNED_PHRASE_BLOCK_RE.search(src)
    if not match:
        raise RuntimeError(
            "Could not find the 'Banned words and phrases:' block in "
            f"{OUTPUT_SYNTHESIS_PATH} -- its format changed; update "
            "_BANNED_PHRASE_BLOCK_RE rather than falling back to a "
            "hardcoded list."
        )
    raw = match.group(1).replace("\n", " ")
    raw = raw.replace("(as a verb)", "").strip()
    phrases = [p.strip() for p in raw.split(",") if p.strip()]
    return tuple(phrases)


if __name__ == "__main__":
    jargon = load_banned_jargon()
    print(f"{len(jargon)} banned phrases extracted from {OUTPUT_SYNTHESIS_PATH}:")
    for p in jargon:
        print(" ", p)
