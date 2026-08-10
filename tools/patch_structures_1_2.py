"""
PRV3 -- Structures 1 and 2 from Gemini's architecture review (this
session), verified before implementation, not treated as ready-to-use
per standing protocol.

Structure 1 (position 34, engine Q41, built_to_fail): Q41 fully
replaced with a yes/no gate. New SEVER-30 (fires on "Yes") asks
whether the gap was raised; its mandatory "have not raised it" option
fires new SEVER-31 (deepest level, asking why not). 3-deep chain,
exercises Part 1's ancestry-labeling fix directly.

Structure 2 (position 36, engine Q43, the_founders_grip): Q43 fully
replaced with a yes/no gate. New SEVER-32 (fires on "Yes") asks why
senior leaders departed, with a mandatory neutral "I don't know"
option. 2-deep chain.

Final content (Pete-approved, 2026-08-09) -- no placeholders remain.
SEVER-31's D option carries severity_trigger=True (no follow_on_id --
matches the Q40-51 batch's own precedent of flagging the worst-case
option for future extensibility without an active further splice, not
an oversight).

Scoring design, verified against precedent, not invented:
  - Base gate questions (Q41, Q43): both options all-zero
    (dict(_z)) -- the real signal moves entirely into the follow-on
    chain. "Yes" carries severity_trigger=True + the real
    severity_follow_on_id; "No" carries neither.
  - New follow-on questions given real _opt_contrib entries (escalating
    0/.25/.5/.75 on the parent's existing dimension -- aptitude_liability
    for built_to_fail, authority_liability for the_founders_grip),
    NOT left to the flat-0.25-uniform fallback that SEVER-14 through
    SEVER-29 all use today. Precedent for a "SEVER-" ID carrying a real
    _opt_contrib entry: SEVER-05 already does this (confirmed via
    direct read) -- not unprecedented.
  - severity_input_mapping (duration_band-style content feeding the
    separate SeverityEngine/severity_tier, unrelated to state ranking)
    deliberately NOT added to SEVER-30/31/32 -- Pete's design brief
    describes state-ranking-style content ("did you raise it", "why
    not"), not duration/population-band content, and no such content
    was drafted. Flagged explicitly: this makes these three questions
    functionally like the Q40-51 batch's own pattern (dimensional_
    contributions only), not like most other SEVER-## questions (which
    all carry severity_input_mapping, 29/29 confirmed) -- Pete's call
    whether that's fine or whether severity_input_mapping content
    should be authored later.
  - SEVER-30's D option ("have not raised it") and SEVER-32's D option
    ("I don't know") sit at opposite ends structurally: D on SEVER-30
    carries the HIGHEST liability value (0.75) since total silence is
    the worst finding for built_to_fail, consistent with this file's
    "D = worst" convention throughout. D on SEVER-32 is neutral
    (dict(_z)) per Pete's explicit instruction ("mandatory 'I don't
    know' option with zero/neutral dimensional weight").

Structure 3 (positions 37/38/39) deliberately NOT touched -- parked
alongside A5, same MC_CENTROID_39/core-count landmine, logged
separately in tools/_mob.txt.

Usage:
  python tools/patch_structures_1_2.py --dry-run
  python tools/patch_structures_1_2.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


Q = "engine/data/questions.py"

# ---------------------------------------------------------------------
# 1. Q41 -- fully replaced with a yes/no gate (Structure 1 base).
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q41",\n'
    '        "When you\'ve raised the gap between what this role is responsible"\n'
    '        " for and the resources you actually have to do it, what\'s happened?",\n'
    '        "forced_choice", 41, "late",\n'
    "        [\n"
    '            ("A", "It got acknowledged and something changed.", False, None),\n'
    '            ("B", "It got acknowledged, but nothing\'s changed yet.", False, None),\n'
    '            ("C", "I was told to figure it out — the responsibility landed on me, not the structure.", False, None),\n'
    '            ("D", "I\'ve been told that directly — and it\'s clearly the standard response to this role, not advice specific to my situation.", True, None),\n'
    "        ],\n"
    '        ["built_to_fail"],\n'
    "        True,\n"
    "    ),",
    '        "Q41",\n'
    '        "Is there a gap between what this role is responsible for and the"\n'
    '        " resources you actually have to do it?",\n'
    '        "forced_choice", 41, "late",\n'
    "        [\n"
    '            ("A", "No.", False, None),\n'
    '            ("B", "Yes.", True, "SEVER-30"),\n'
    "        ],\n"
    '        ["built_to_fail"],\n'
    "        True,\n"
    "    ),",
)

# ---------------------------------------------------------------------
# 2. Q43 -- fully replaced with a yes/no gate (Structure 2 base).
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q43",\n'
    '        "Have senior people left specifically because of how concentrated"\n'
    '        " decision-making is here?",\n'
    '        "forced_choice", 43, "late",\n'
    "        [\n"
    '            ("A", "Not that I\'m aware of.", False, None),\n'
    '            ("B", "Maybe — it\'s come up, but I\'m not certain it was the deciding factor.", False, None),\n'
    '            ("C", "Yes, at least one departure, and the reason was fairly clear.", False, None),\n'
    '            ("D", "Yes, more than one, and it\'s become something people acknowledge openly as why they left or are thinking about leaving.", True, None),\n'
    "        ],\n"
    '        ["the_founders_grip"],\n'
    "        True,\n"
    "    ),",
    '        "Q43",\n'
    '        "Have more than 1 senior leader left in the last 18 months?",\n'
    '        "forced_choice", 43, "late",\n'
    "        [\n"
    '            ("A", "No.", False, None),\n'
    '            ("B", "Yes.", True, "SEVER-32"),\n'
    "        ],\n"
    '        ["the_founders_grip"],\n'
    "        True,\n"
    "    ),",
)

# ---------------------------------------------------------------------
# 3. New SEVER-30/31/32 _QDATA tuples -- inserted after SEVER-29, before
#    Q35, matching the file's existing chronological SEVER-## ordering.
# ---------------------------------------------------------------------

edit(
    Q,
    '        ["the_untouchable"],\n'
    "        False,\n"
    "    ),\n"
    "    (\n"
    '        "Q35",',
    '        ["the_untouchable"],\n'
    "        False,\n"
    "    ),\n"
    "    # -- Structure 1/2 conditional follow-up chains (this session) -- Gemini\n"
    "    # architecture review, Structures 1 and 2 (Structure 3 parked with A5,\n"
    "    # see Decision Register). Content Pete-approved, final.\n"
    "    (\n"
    '        "SEVER-30",\n'
    '        "Have you brought attention to the gap(s), and if so, what\'s happened?",\n'
    '        "forced_choice", None, "conditional",\n'
    "        [\n"
    '            ("A", "It got acknowledged and something changed.", False, None),\n'
    '            ("B", "It got acknowledged, but nothing\'s changed yet.", False, None),\n'
    '            ("C", "I was told to figure it out — the responsibility landed on me, not the structure.", False, None),\n'
    '            ("D", "I have not brought attention to the gap.", True, "SEVER-31"),\n'
    "        ],\n"
    '        ["built_to_fail"],\n'
    "        True,\n"
    "    ),\n"
    "    (\n"
    '        "SEVER-31",\n'
    '        "What\'s kept you from raising it?",\n'
    '        "forced_choice", None, "conditional",\n'
    "        [\n"
    '            ("A", "I\'ve been planning to, but haven\'t yet — no specific reason it\'s been delayed.", False, None),\n'
    '            ("B", "It didn\'t seem like it would lead anywhere, based on how similar things have gone before.", False, None),\n'
    '            ("C", "I wasn\'t sure it was my place to raise, or who the right person to raise it with even is.", False, None),\n'
    '            ("D", "Raising it has felt genuinely risky — like it could reflect on me rather than get the actual problem addressed.", True, None),\n'
    "        ],\n"
    '        ["built_to_fail"],\n'
    "        True,\n"
    "    ),\n"
    "    (\n"
    '        "SEVER-32",\n'
    '        "Why did they depart?",\n'
    '        "forced_choice", None, "conditional",\n'
    "        [\n"
    '            ("A", "For reasons clearly unrelated to this — retirement, relocation, an outside opportunity.", False, None),\n'
    '            ("B", "It\'s unclear whether this played a role.", False, None),\n'
    '            ("C", "This was at least part of the reason, alongside other factors.", False, None),\n'
    '            ("D", "I don\'t know.", False, None),\n'
    "        ],\n"
    '        ["the_founders_grip"],\n'
    "        False,\n"
    "    ),\n"
    "    (\n"
    '        "Q35",',
)

# ---------------------------------------------------------------------
# 4. _opt_contrib -- Q41/Q43 reduced to all-zero gates; new SEVER-30/31/32
#    given real escalating entries (not the flat-0.25 fallback).
# ---------------------------------------------------------------------

edit(
    Q,
    '        "Q41": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "aptitude_liability":  0.25},\n'
    '            "C": {**_z, "aptitude_liability":  0.50},\n'
    '            "D": {**_z, "aptitude_liability":  0.75},\n'
    "        },",
    '        "Q41": {\n'
    "            \"A\": dict(_z),\n"
    "            \"B\": dict(_z),\n"
    "        },\n"
    '        "SEVER-30": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "aptitude_liability":  0.25},\n'
    '            "C": {**_z, "aptitude_liability":  0.50},\n'
    '            "D": {**_z, "aptitude_liability":  0.75},\n'
    "        },\n"
    '        "SEVER-31": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "aptitude_liability":  0.25},\n'
    '            "C": {**_z, "aptitude_liability":  0.50},\n'
    '            "D": {**_z, "aptitude_liability":  0.75},\n'
    "        },",
)

edit(
    Q,
    '        "Q43": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "authority_liability":  0.25},\n'
    '            "C": {**_z, "authority_liability":  0.50},\n'
    '            "D": {**_z, "authority_liability":  0.75},\n'
    "        },",
    '        "Q43": {\n'
    "            \"A\": dict(_z),\n"
    "            \"B\": dict(_z),\n"
    "        },\n"
    '        "SEVER-32": {\n'
    "            \"A\": dict(_z),\n"
    '            "B": {**_z, "authority_liability":  0.25},\n'
    '            "C": {**_z, "authority_liability":  0.50},\n'
    '            "D": dict(_z),\n'
    "        },",
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 200 chars): {old[:200]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
