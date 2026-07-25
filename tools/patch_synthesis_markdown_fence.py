#!/usr/bin/env python
"""
PRV3 -- patch_synthesis_markdown_fence.py
Fixes the markdown-fence JSON parsing gap in _parse_synthesis_response()
(engine/output_synthesis.py), confirmed live on prv-3 Production this
session: 100% of successful Anthropic API calls in a 30s-diagnostic test
returned complete, well-formed synthesis content, but every one failed
json.loads() because the model wraps its response in a ```json ... ```
markdown code fence, despite the system prompt explicitly instructing "no
markdown, return only this JSON structure." Independent of, and not fixed
by, the separate 5s-timeout-value question.

Two layers of defensiveness, both small:
  1. _strip_markdown_fence() -- strips a leading ```json / ``` fence and
     trailing ``` if present. Returns text unchanged if no fence is found,
     so the already-working bare-JSON case (what the system prompt asks
     for and sometimes gets) is untouched.
  2. If the cleaned text still doesn't parse (e.g. the model added prose
     around the JSON rather than a clean fence), _parse_synthesis_response()
     falls back to extracting the outermost {...} block via regex before
     giving up. This is the one additional layer proposed, not more --
     kept small and targeted per Pete's explicit instruction not to
     over-engineer this.

The original JSONDecodeError message (from the first parse attempt) is
preserved in parse_error in both failure branches, so diagnostic output
doesn't regress if both layers fail.

Changes:
  engine/output_synthesis.py
    - import re added
    - _strip_markdown_fence() helper added before _parse_synthesis_response()
    - _parse_synthesis_response()'s parse step gains the fence-strip +
      regex-extraction fallback; the missing-required-field and success
      paths are unchanged
  tools/test_output_synthesis.py
    - 5 new tests (26-30) covering: ```json-fenced response parses
      successfully; bare ```-fenced (no "json" label) response parses
      successfully; already-working bare JSON still works post-fix
      (regression guard); JSON embedded in surrounding prose (no clean
      fence) recovered via the regex-extraction fallback; a genuinely
      broken fenced response still falls back correctly (parse_error
      populated, is_fallback True) -- the fix doesn't silently swallow
      real parse failures

Usage:
  python tools/patch_synthesis_markdown_fence.py --dry-run
  python tools/patch_synthesis_markdown_fence.py --write
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
SYNTHESIS_TARGET = ROOT / "engine" / "output_synthesis.py"
TEST_TARGET = ROOT / "tools" / "test_output_synthesis.py"

CHANGES = []  # list of (path, label, old, new)


def edit(path, label, old, new):
    CHANGES.append((path, label, old, new))


# ── 1. engine/output_synthesis.py: add `import re` ────────────────────────────
edit(
    SYNTHESIS_TARGET,
    "add import re",
    '''from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Optional

from engine.data.fallback_synthesis import get_fallback_synthesis''',
    '''from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Optional

from engine.data.fallback_synthesis import get_fallback_synthesis''',
)

# ── 2. engine/output_synthesis.py: fence-stripping + regex fallback ───────────
OLD_PARSE = '''def _parse_synthesis_response(
    response_text: str,
    commercial_name: str = "",
    severity_tier: str | None = None,
) -> SynthesisResult:
    """Parse LLM JSON response. Full fallback from static dict on any failure."""
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        fb = get_fallback_synthesis(commercial_name, severity_tier)
        return SynthesisResult(
            **fb,
            synthesis_confidence=0.0,
            raw_response=response_text,
            parse_error=str(e),
            is_fallback=True,
        )'''

NEW_PARSE = '''_MARKDOWN_FENCE_RE = re.compile(r"^```(?:json)?\\s*\\n?(.*?)\\n?```\\s*$", re.DOTALL)
_JSON_OBJECT_RE = re.compile(r"\\{.*\\}", re.DOTALL)


def _strip_markdown_fence(text: str) -> str:
    """Strip a ```json / ``` code fence wrapping the response, if present.

    Models sometimes wrap their JSON in a markdown code fence despite the
    system prompt explicitly instructing otherwise (confirmed live on
    prv-3 Production, Session 72). Returns text unchanged if no fence
    is found, so the already-working bare-JSON case is untouched.
    """
    match = _MARKDOWN_FENCE_RE.match(text.strip())
    return match.group(1).strip() if match else text


def _parse_synthesis_response(
    response_text: str,
    commercial_name: str = "",
    severity_tier: str | None = None,
) -> SynthesisResult:
    """Parse LLM JSON response. Full fallback from static dict on any failure."""
    cleaned = _strip_markdown_fence(response_text)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as e:
        # Second layer: the model may have added prose around the JSON
        # rather than a clean fence -- extract the outermost {...} block
        # before giving up. Original error preserved in parse_error either way.
        match = _JSON_OBJECT_RE.search(cleaned)
        try:
            if match is None:
                raise e
            data = json.loads(match.group(0))
        except json.JSONDecodeError:
            fb = get_fallback_synthesis(commercial_name, severity_tier)
            return SynthesisResult(
                **fb,
                synthesis_confidence=0.0,
                raw_response=response_text,
                parse_error=str(e),
                is_fallback=True,
            )'''

edit(SYNTHESIS_TARGET, "fence-stripping + regex-extraction fallback", OLD_PARSE, NEW_PARSE)

# ── 3. tools/test_output_synthesis.py: docstring additions ────────────────────
edit(
    TEST_TARGET,
    "docstring: add items 26-30",
    '''  24. OutputSynthesisEngine: result is None before first call
  25. OutputSynthesisEngine: result stored after synthesize() call
"""''',
    '''  24. OutputSynthesisEngine: result is None before first call
  25. OutputSynthesisEngine: result stored after synthesize() call
  26. _parse_synthesis_response: ```json-fenced response parses successfully
  27. _parse_synthesis_response: bare ```-fenced (no "json" label) response parses
  28. _parse_synthesis_response: bare JSON still works post-fix (regression guard)
  29. _parse_synthesis_response: JSON embedded in surrounding prose recovered via regex fallback
  30. _parse_synthesis_response: genuinely broken fenced response still falls back correctly
"""''',
)

# ── 4. tools/test_output_synthesis.py: new test block ──────────────────────────
OLD_TEST_TAIL = '''# ── 10–11. get_fallback_synthesis: structure and content ──────────────────────'''

NEW_TEST_BLOCK = '''# ── 26–30. _parse_synthesis_response: markdown-fence handling (Session 72) ────

fenced_json = json.dumps({
    "liability_condition_text":     "The decision-making pattern is structural.",
    "asset_resolution_anchor_text": "Governance discipline is intact.",
    "framing_text":                 "An organizational pattern is affecting decision-making.",
    "observable_indicators":        ["Decisions escalate to senior leadership."],
    "resolution_framing_text":      "Groundwork at this stage produces a clear structural account.",
    "synthesis_confidence":         0.82,
})

fenced_with_label = f"```json\\n{fenced_json}\\n```"
fenced_parsed = _parse_synthesis_response(fenced_with_label, "Groundwork", "Entrenched")

check(
    "```json-fenced response: is_fallback False",
    fenced_parsed.is_fallback is False,
    f"got {fenced_parsed.is_fallback}, parse_error={fenced_parsed.parse_error!r}",
)
check(
    "```json-fenced response: liability_condition_text populated",
    fenced_parsed.liability_condition_text == "The decision-making pattern is structural.",
    f"got {fenced_parsed.liability_condition_text!r}",
)

fenced_bare = f"```\\n{fenced_json}\\n```"
fenced_bare_parsed = _parse_synthesis_response(fenced_bare, "Groundwork", "Entrenched")

check(
    "bare ```-fenced (no json label) response: is_fallback False",
    fenced_bare_parsed.is_fallback is False,
    f"got {fenced_bare_parsed.is_fallback}, parse_error={fenced_bare_parsed.parse_error!r}",
)
check(
    "bare ```-fenced response: framing_text populated",
    fenced_bare_parsed.framing_text == "An organizational pattern is affecting decision-making.",
    f"got {fenced_bare_parsed.framing_text!r}",
)

unfenced_parsed = _parse_synthesis_response(fenced_json, "Groundwork", "Entrenched")

check(
    "unfenced JSON still works post-fix (regression guard): is_fallback False",
    unfenced_parsed.is_fallback is False,
    f"got {unfenced_parsed.is_fallback}, parse_error={unfenced_parsed.parse_error!r}",
)
check(
    "unfenced JSON still works post-fix: resolution_framing_text populated",
    unfenced_parsed.resolution_framing_text == "Groundwork at this stage produces a clear structural account.",
    f"got {unfenced_parsed.resolution_framing_text!r}",
)

embedded_in_prose = f"Here is the result:\\n\\n{fenced_json}\\n\\nHope this helps!"
prose_parsed = _parse_synthesis_response(embedded_in_prose, "Groundwork", "Entrenched")

check(
    "JSON embedded in prose (no fence): recovered via regex fallback, is_fallback False",
    prose_parsed.is_fallback is False,
    f"got {prose_parsed.is_fallback}, parse_error={prose_parsed.parse_error!r}",
)
check(
    "JSON embedded in prose: observable_indicators populated",
    prose_parsed.observable_indicators == ["Decisions escalate to senior leadership."],
    f"got {prose_parsed.observable_indicators!r}",
)

broken_fenced = "```json\\nnot actually valid json {{{{\\n```"
broken_parsed = _parse_synthesis_response(broken_fenced, "Groundwork", "Entrenched")

check(
    "genuinely broken fenced response: is_fallback True (not silently swallowed)",
    broken_parsed.is_fallback is True,
    f"got {broken_parsed.is_fallback}",
)
check(
    "genuinely broken fenced response: parse_error populated",
    len(broken_parsed.parse_error) > 0,
    "parse_error empty",
)


# ── 10–11. get_fallback_synthesis: structure and content ──────────────────────'''

edit(TEST_TARGET, "new test block (26-30)", OLD_TEST_TAIL, NEW_TEST_BLOCK)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if not args.dry_run and not args.write:
        parser.print_help()
        sys.exit(1)

    texts = {}
    for path, label, old, new in CHANGES:
        if path not in texts:
            if not path.exists():
                print(f"ERROR: target not found: {path}")
                sys.exit(1)
            texts[path] = path.read_text(encoding="utf-8")

    if args.dry_run:
        print("DRY RUN")
        all_ok = True
        for path, label, old, new in CHANGES:
            count = texts[path].count(old)
            status = f"OK ({count}x)" if count == 1 else ("MISS" if count == 0 else f"AMBIGUOUS ({count}x)")
            if count != 1:
                all_ok = False
            print(f"  [{status}] {path.name}: {label}")
        if not all_ok:
            print("\n  ERROR: one or more OLD strings not found exactly once in target.")
            sys.exit(1)
        print("\n  All anchors matched exactly once. Ready for --write.")
        return

    for path, label, old, new in CHANGES:
        count = texts[path].count(old)
        if count != 1:
            print(f"ERROR: OLD string for '{label}' in {path.name} matched {count} times (expected 1) -- aborting.")
            sys.exit(1)

    new_texts = dict(texts)
    for path, label, old, new in CHANGES:
        new_texts[path] = new_texts[path].replace(old, new, 1)

    for path, text in new_texts.items():
        if text == texts[path]:
            print(f"ERROR: no changes produced for {path.name}.")
            sys.exit(1)
        path.write_text(text, encoding="utf-8")
        print(f"WRITTEN: {path}")

    print(f"  {len(CHANGES)} change(s) applied across {len(new_texts)} file(s)")


if __name__ == "__main__":
    main()
