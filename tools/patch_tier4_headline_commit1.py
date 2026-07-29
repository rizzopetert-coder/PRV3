"""
PRV3 -- Tier 4 Headline Field, Commit 1 of 2 (Python core + content-quality
check). Web layer (types.ts, route builders, rendering) is Commit 2,
explicitly NOT touched here.

Four files, exactly as scoped and confirmed:
  1. engine/output_synthesis.py -- system prompt gets the Pete-approved,
     dash-free headline content spec inserted verbatim (superseded a
     first draft that preserved literal "--"; standing PRV3 rule
     confirmed mid-task: no em dashes or "--" anywhere in PRV3 copy,
     including LLM system-prompt content). Also fixes all 5 pre-existing
     em-dash audience labels on the other five field specs
     ("(private — principal only)" x2, "(shareable — professional
     audience)" x2, "(shareable — JSON array of strings)" x1) to comma
     style, matching the new headline label's punctuation -- pure label
     text, confirmed these are structural audience/format annotations,
     not instructions, so the LLM's interpretation is unaffected.
     SynthesisResult dataclass, _parse_synthesis_response().
  2. engine/data/fallback_synthesis.py -- new _FALLBACK_HEADLINE constant
     (Pete-approved verbatim), _make_entry() gains a headline key,
     get_fallback_synthesis()'s docstring corrected (5 keys -> 6).
  3. engine/contract.py -- _SYNTHESIS_FIELDS (the correct constant, per
     this session's own verification pass -- NOT _PRIVATE_OUTPUT_FIELDS
     as Gemini originally claimed) + synthesis_dict construction.
  4. tools/test_output_synthesis.py -- the one SynthesisResult(...)
     construction site (line 77) needs headline= added, since headline
     lands as a REQUIRED field (matching the other five real content
     fields -- no default -- confirmed safe: calibration_runner.py never
     constructs a SynthesisResult at all, so this cannot touch the
     169/172 calibration number). Also folds in the "5-field" -> "6-field"
     label corrections scattered through this file's comments/check
     descriptions (6 occurrences, purely descriptive text, zero
     functional change -- confirmed by reading the check bodies, which
     assert specific field-name substrings, not a field count) since
     this file is already being touched and leaving them stale would be
     a known, avoidable inaccuracy. Flagged explicitly -- not silently
     bundled.

_make_entry()'s four fallback SynthesisResult(**fb, ...) call sites in
output_synthesis.py (lines 168, 188, 282, 323) need ZERO changes -- they
all spread the dict get_fallback_synthesis() returns, which will already
include "headline" once fallback_synthesis.py is updated.

Usage:
  python tools/patch_tier4_headline_commit1.py --dry-run
  python tools/patch_tier4_headline_commit1.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_SYNTHESIS_FILE = REPO_ROOT / "engine" / "output_synthesis.py"
FALLBACK_FILE = REPO_ROOT / "engine" / "data" / "fallback_synthesis.py"
CONTRACT_FILE = REPO_ROOT / "engine" / "contract.py"
TEST_FILE = REPO_ROOT / "tools" / "test_output_synthesis.py"

EDITS: list[tuple[Path, str, str, str]] = []

# --- engine/output_synthesis.py ------------------------------------------------

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: module docstring, five -> six",
    "Generates five synthesis fields from a diagnosed organizational state.",
    "Generates six synthesis fields from a diagnosed organizational state.",
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: system prompt -- headline field spec + JSON example",
    '''resolution_framing_text (shareable — professional audience):
2-3 sentences describing the resolution pathway in organizational benefit language.
No liability framing. Reference the resolution_family name naturally. Forward-facing.
Do not name specific service inclusions or make guarantees.

REQUIRED OUTPUT FORMAT

Return only this JSON structure. No preamble. No explanation. No markdown.

{
  "liability_condition_text": "<2-4 sentences>",
  "asset_resolution_anchor_text": "<1-3 sentences>",
  "framing_text": "<2-3 sentences>",
  "observable_indicators": ["<indicator>", "<indicator>", "<indicator>"],
  "resolution_framing_text": "<2-3 sentences>",
  "synthesis_confidence": <float 0.0-1.0>
}\\
"""''',
    '''resolution_framing_text (shareable — professional audience):
2-3 sentences describing the resolution pathway in organizational benefit language.
No liability framing. Reference the resolution_family name naturally. Forward-facing.
Do not name specific service inclusions or make guarantees.

headline (private and shareable, board-safe):
One sentence, 8-14 words. Non-confrontational, behavioral, and
operational. Not a verdict, not accusatory, and no liability language.
Uses the same "conditions for a conversation, not a verdict" register as
framing_text. Draw from the identified state's primary dimension and
current severity tier, without naming the state directly or using
liability-specific terms. Should read as the sentence a principal or
board member remembers after closing the report. Not a teaser, not a
question, and not marketing copy.
No exclamation points. No loosely-used superlatives, such as "worst,"
"biggest," or "critical."
Severity calibration (behavioral framing only):
  Emerging: name the pattern as visible.
  Entrenched: name the pattern as settled.
  Endemic: name the pattern as structural to how the organization runs.

REQUIRED OUTPUT FORMAT

Return only this JSON structure. No preamble. No explanation. No markdown.

{
  "liability_condition_text": "<2-4 sentences>",
  "asset_resolution_anchor_text": "<1-3 sentences>",
  "framing_text": "<2-3 sentences>",
  "observable_indicators": ["<indicator>", "<indicator>", "<indicator>"],
  "resolution_framing_text": "<2-3 sentences>",
  "headline": "<8-14 words>",
  "synthesis_confidence": <float 0.0-1.0>
}\\
"""''',
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: label fix, liability_condition_text audience label",
    "liability_condition_text (private — principal only):",
    "liability_condition_text (private, principal only):",
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: label fix, asset_resolution_anchor_text audience label",
    "asset_resolution_anchor_text (private — principal only):",
    "asset_resolution_anchor_text (private, principal only):",
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: label fix, framing_text audience label",
    "framing_text (shareable — professional audience):\nProfessional framing for a board member or senior leader.",
    "framing_text (shareable, professional audience):\nProfessional framing for a board member or senior leader.",
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: label fix, observable_indicators audience label",
    "observable_indicators (shareable — JSON array of strings):",
    "observable_indicators (shareable, JSON array of strings):",
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: label fix, resolution_framing_text audience label",
    "resolution_framing_text (shareable — professional audience):",
    "resolution_framing_text (shareable, professional audience):",
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: SynthesisResult dataclass -- add headline field",
    '''@dataclass
class SynthesisResult:
    """
    Output of one synthesis call. Five content fields plus metadata.
    All string fields are empty string on failure. observable_indicators is
    empty list on failure. is_fallback=True when LLM call failed or response
    was unparseable.
    """
    liability_condition_text:     str
    asset_resolution_anchor_text: str
    framing_text:                 str
    observable_indicators:        list
    resolution_framing_text:      str
    synthesis_confidence:         float''',
    '''@dataclass
class SynthesisResult:
    """
    Output of one synthesis call. Six content fields plus metadata.
    All string fields are empty string on failure. observable_indicators is
    empty list on failure. is_fallback=True when LLM call failed or response
    was unparseable.
    """
    liability_condition_text:     str
    asset_resolution_anchor_text: str
    framing_text:                 str
    observable_indicators:        list
    resolution_framing_text:      str
    headline:                     str
    synthesis_confidence:         float''',
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: _parse_synthesis_response() -- extract + require + return headline",
    '''    resolution = str(data.get("resolution_framing_text", "")).strip()
    confidence = float(data.get("synthesis_confidence", 0.0))

    if not liability or not framing or not resolution:
        fb = get_fallback_synthesis(commercial_name, severity_tier)
        return SynthesisResult(
            **fb,
            synthesis_confidence=0.0,
            raw_response=response_text,
            parse_error="missing required fields",
            is_fallback=True,
        )

    return SynthesisResult(
        liability_condition_text=liability,
        asset_resolution_anchor_text=asset,
        framing_text=framing,
        observable_indicators=indicators,
        resolution_framing_text=resolution,
        synthesis_confidence=confidence,
        raw_response=response_text,
    )''',
    '''    resolution = str(data.get("resolution_framing_text", "")).strip()
    headline   = str(data.get("headline", "")).strip()
    confidence = float(data.get("synthesis_confidence", 0.0))

    if not liability or not framing or not resolution or not headline:
        fb = get_fallback_synthesis(commercial_name, severity_tier)
        return SynthesisResult(
            **fb,
            synthesis_confidence=0.0,
            raw_response=response_text,
            parse_error="missing required fields",
            is_fallback=True,
        )

    return SynthesisResult(
        liability_condition_text=liability,
        asset_resolution_anchor_text=asset,
        framing_text=framing,
        observable_indicators=indicators,
        resolution_framing_text=resolution,
        headline=headline,
        synthesis_confidence=confidence,
        raw_response=response_text,
    )''',
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: prompt trailing instruction, five -> six",
    '    parts.append("\\nGenerate all five synthesis fields for this diagnostic result.")',
    '    parts.append("\\nGenerate all six synthesis fields for this diagnostic result.")',
))

EDITS.append((
    OUTPUT_SYNTHESIS_FILE,
    "output_synthesis.py: synthesize() docstring, five -> six",
    "    Call the LLM to generate five synthesis fields for a diagnostic result.",
    "    Call the LLM to generate six synthesis fields for a diagnostic result.",
))

# --- engine/data/fallback_synthesis.py -----------------------------------------

EDITS.append((
    FALLBACK_FILE,
    "fallback_synthesis.py: new _FALLBACK_HEADLINE constant + _make_entry() gains headline",
    '''def _make_entry(copy_text: str) -> dict:
    """Build a 5-field synthesis entry from a single copy string."""
    return {
        "liability_condition_text":     copy_text,
        "asset_resolution_anchor_text": "",
        "framing_text":                 copy_text,
        "observable_indicators":        [],
        "resolution_framing_text":      copy_text,
    }''',
    '''# Generic, state/severity-agnostic fallback headline. The fallback path
# has no real session signal to draw the per-state/per-tier calibration
# from, so this is the single safe default used everywhere, not a
# per-tier variant set.
_FALLBACK_HEADLINE: str = "A pattern in how this organization operates is shaping outcomes internally."


def _make_entry(copy_text: str) -> dict:
    """Build a synthesis entry from a single copy string, plus the fixed
    generic headline fallback. Headline is not derived from copy_text."""
    return {
        "liability_condition_text":     copy_text,
        "asset_resolution_anchor_text": "",
        "framing_text":                 copy_text,
        "observable_indicators":        [],
        "resolution_framing_text":      copy_text,
        "headline":                     _FALLBACK_HEADLINE,
    }''',
))

EDITS.append((
    FALLBACK_FILE,
    "fallback_synthesis.py: get_fallback_synthesis() docstring, 5 keys -> 6",
    '''    Returned dict has exactly 5 keys matching SynthesisResult fields:
        liability_condition_text, asset_resolution_anchor_text, framing_text,
        observable_indicators, resolution_framing_text.''',
    '''    Returned dict has exactly 6 keys matching SynthesisResult fields:
        liability_condition_text, asset_resolution_anchor_text, framing_text,
        observable_indicators, resolution_framing_text, headline.''',
))

# --- engine/contract.py ---------------------------------------------------------

EDITS.append((
    CONTRACT_FILE,
    "contract.py: _SYNTHESIS_FIELDS gains headline",
    '''_SYNTHESIS_FIELDS = {
    "liability_condition_text", "asset_resolution_anchor_text",
    "framing_text", "observable_indicators", "resolution_framing_text",
    "synthesis_confidence", "is_fallback",
}''',
    '''_SYNTHESIS_FIELDS = {
    "liability_condition_text", "asset_resolution_anchor_text",
    "framing_text", "observable_indicators", "resolution_framing_text",
    "headline", "synthesis_confidence", "is_fallback",
}''',
))

EDITS.append((
    CONTRACT_FILE,
    "contract.py: synthesis_dict construction gains headline",
    '''            "resolution_framing_text":      synthesis_result.resolution_framing_text,
            "synthesis_confidence":         synthesis_result.synthesis_confidence,
            "is_fallback":                  synthesis_result.is_fallback,
        }
        if synthesis_result is not None
        else None
    )''',
    '''            "resolution_framing_text":      synthesis_result.resolution_framing_text,
            "headline":                     synthesis_result.headline,
            "synthesis_confidence":         synthesis_result.synthesis_confidence,
            "is_fallback":                  synthesis_result.is_fallback,
        }
        if synthesis_result is not None
        else None
    )''',
))

# --- tools/test_output_synthesis.py ---------------------------------------------

EDITS.append((
    TEST_FILE,
    "test_output_synthesis.py: fixture construction gains headline",
    '''result = SynthesisResult(
    liability_condition_text="test liability",
    asset_resolution_anchor_text="test asset",
    framing_text="test framing",
    observable_indicators=["one", "two"],
    resolution_framing_text="test resolution",
    synthesis_confidence=0.75,
)''',
    '''result = SynthesisResult(
    liability_condition_text="test liability",
    asset_resolution_anchor_text="test asset",
    framing_text="test framing",
    observable_indicators=["one", "two"],
    resolution_framing_text="test resolution",
    headline="test headline",
    synthesis_confidence=0.75,
)''',
))

EDITS.append((
    TEST_FILE,
    "test_output_synthesis.py: label corrections, 5-field -> 6-field (flagged, zero functional change)",
    "Verifies the 5-field contract migration (S42):",
    "Verifies the 5-field contract migration (S42), now 6 fields (Tier 4 headline):",
))

EDITS.append((
    TEST_FILE,
    "test_output_synthesis.py: label correction, check 4 description",
    "  4.  _parse_synthesis_response: valid 5-field JSON → correct SynthesisResult",
    "  4.  _parse_synthesis_response: valid 6-field JSON → correct SynthesisResult",
))

EDITS.append((
    TEST_FILE,
    "test_output_synthesis.py: label correction, check 17 description",
    "  17. OUTPUT_SYNTHESIS_SYSTEM_PROMPT: 5-field JSON output format required",
    "  17. OUTPUT_SYNTHESIS_SYSTEM_PROMPT: 6-field JSON output format required",
))

EDITS.append((
    TEST_FILE,
    "test_output_synthesis.py: banner label correction",
    'print("PRV3 Output Synthesis — Unit Tests (5-field contract, S42)")',
    'print("PRV3 Output Synthesis — Unit Tests (6-field contract, S42 + Tier 4 headline)")',
))

EDITS.append((
    TEST_FILE,
    "test_output_synthesis.py: check label correction, liability_condition_text",
    '"System prompt: 5-field JSON output format — liability_condition_text",',
    '"System prompt: 6-field JSON output format — liability_condition_text",',
))

EDITS.append((
    TEST_FILE,
    "test_output_synthesis.py: check label correction, synthesis_confidence",
    '"System prompt: 5-field JSON output format — synthesis_confidence",',
    '"System prompt: 6-field JSON output format — synthesis_confidence",',
))


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts: dict[Path, str] = {}
    for path in {e[0] for e in EDITS}:
        file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in EDITS:
        count = file_texts[path].count(old)
        if count != 1:
            print(f"ABORT -- anchor for '{label}' matched {count} times in {path.relative_to(REPO_ROOT)}, need exactly 1", file=sys.stderr)
            sys.exit(1)

    print("=" * 100)
    for path, label, old, new in EDITS:
        print(f"\n--- {label} ({path.relative_to(REPO_ROOT)}) ---")
        print("BEFORE:")
        print(old)
        print("AFTER:")
        print(new)
    print("\n" + "=" * 100)

    new_texts: dict[Path, str] = dict(file_texts)
    for path, label, old, new in EDITS:
        new_texts[path] = new_texts[path].replace(old, new, 1)

    print("Files touched:")
    for path in file_texts:
        delta = len(new_texts[path]) - len(file_texts[path])
        print(f"  {path.relative_to(REPO_ROOT)}: {delta:+d} chars")

    print("\nCommit 2 scope (types.ts, both private route builders, share/create/route.ts,")
    print("PrivateOutput.tsx, ShareableOutput.tsx) confirmed NOT touched by this script.")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    for path, text in new_texts.items():
        path.write_text(text, encoding="utf-8")
        print(f"\nWROTE {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
