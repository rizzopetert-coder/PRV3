"""
Phase 3 Pass 2 — Aptitude additive questions Q35–Q39 (Session 14)

Adds five QuestionDefinition entries to engine/data/questions.py and wires
full per-option dimensional_contributions for each via a new _opt_contrib dict.

Three changes applied in order:
  Step 1 — Append Q35–Q39 tuples to _QDATA.
  Step 2 — Insert _opt_contrib dict in _build_library() before the for-loop.
  Step 3 — Update dimensional_contributions assignment to dispatch to
            _opt_contrib for questions whose options need full control,
            falling back to the existing _uniform + _seed + _opt_apt path.

Q35–Q39 bypass _uniform / _seed entirely — each option carries explicit
per-field contributions. All unspecified fields are 0.0.

Usage:
  python tools/patch_q35_q39.py          # dry-run (default)
  python tools/patch_q35_q39.py --write  # apply
"""

import sys
import argparse
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"


# ── Step 1 anchor — end of _QDATA ────────────────────────────────────────────

_QDATA_ANCHOR = '''\
        ["narrative_lock", "the_broken_compass"],
        False,
    ),
]'''

_QDATA_NEW_ENTRIES = '''    (
        "Q35",
        "When someone in a key role isn't performing,"
        " what does the conversation usually sound like?",
        "forced_choice", 35, "mid",
        [
            ("A", "We talk about what the person needs to do differently.", False, None),
            ("B", "We talk about whether the role itself is set up to let them succeed.", False, None),
            ("C", "We talk about whether this is the right role for this person.", False, None),
            ("D", "We don't usually have that conversation until something forces it.", False, None),
        ],
        ["built_to_fail", "the_undefined_role", "the_overloaded_manager"],
        False,
    ),
    (
        "Q36",
        "When someone is underperforming, how does it usually come to a resolution?",
        "forced_choice", 36, "mid",
        [
            ("A", "A direct conversation happens early. Most situations resolve from there.", False, None),
            ("B", "There are conversations, but they tend to drag."
             " The situation usually outlasts the patience for it.", False, None),
            ("C", "The person eventually leaves — resignation, transfer, or mutual agreement"
             " — without a formal process.", False, None),
            ("D", "It depends on who the person is. Some situations get addressed. Others don't.", False, None),
            ("E", "The manager flags it but isn't sure what they're authorized to do about it.", False, None),
        ],
        ["the_paper_tiger", "built_to_fail", "the_undefined_role"],
        False,
    ),
    (
        "Q37",
        "When a policy, process, or tool is no longer working the way it should,"
        " how does that typically surface?",
        "forced_choice", 37, "mid",
        [
            ("A", "Someone with ownership over it flags it and brings a recommendation.", False, None),
            ("B", "People working around it start talking about it"
             " and it eventually reaches leadership.", False, None),
            ("C", "Something breaks — a complaint, a miss, an incident"
             " — and that's when it gets attention.", False, None),
            ("D", "It doesn't always surface. Some things just quietly stop being followed.", False, None),
        ],
        ["the_unexamined_algorithm", "the_policy_lag", "the_undefined_role"],
        False,
    ),
    (
        "Q38",
        "If a senior leader — someone who runs a function or a team — left unexpectedly,"
        " what would happen to what they were carrying?",
        "forced_choice", 38, "mid",
        [
            ("A", "We have someone ready. Coverage would be managed.", False, None),
            ("B", "We'd cover it, but there would be a real gap"
             " while we figured out the transition.", False, None),
            ("C", "A significant amount of what they know and who they know"
             " leaves with them.", False, None),
            ("D", "We'd be in a difficult position."
             " That role holds more than most people realize.", False, None),
        ],
        ["leadership_continuity_risk", "the_unformed_leader", "the_overloaded_manager"],
        False,
    ),
    (
        "Q39",
        "How does your organization typically handle a situation"
        " where someone is clearly not right for a role?",
        "forced_choice", 39, "mid",
        [
            ("A", "We address it directly. The conversation happens and the decision follows.", False, None),
            ("B", "We try to move them into a better fit somewhere else"
             " before making a harder call.", False, None),
            ("C", "We give it more time. Most situations work themselves out.", False, None),
            ("D", "It usually becomes clear the role wasn't set up correctly,"
             " not that the person was wrong for it.", False, None),
        ],
        ["the_paper_tiger", "the_unformed_leader", "built_to_fail"],
        False,
    ),
]'''

_QDATA_REPLACEMENT = (
    "        [\"narrative_lock\", \"the_broken_compass\"],\n"
    "        False,\n"
    "    ),\n"
    + _QDATA_NEW_ENTRIES
)


# ── Step 2 anchor — before the for-loop in _build_library() ──────────────────

_FOR_LOOP_ANCHOR = "    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:"

_OPT_CONTRIB_BLOCK = '''\
    # Session 14: per-option full contribution overrides for Aptitude additive questions.
    # Q35-Q39 bypass _uniform / _seed — each option carries explicit per-field values.
    # "all others: 0.0" means every unspecified field is 0.0.
    _z = {
        "aptitude_liability":  0.0, "aptitude_asset":  0.0,
        "authority_liability": 0.0, "authority_asset": 0.0,
        "alliance_liability":  0.0, "alliance_asset":  0.0,
        "attitude_liability":  0.0, "attitude_asset":  0.0,
    }
    _opt_contrib = {
        "Q35": {
            "A": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.25},
            "B": {**_z, "aptitude_liability": 0.25, "authority_liability": 0.60},
            "C": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40},
        },
        "Q36": {
            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},
            "B": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40},
            "C": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40,
                        "attitude_liability": 0.40},
            "E": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.60},
        },
        "Q37": {
            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},
            "B": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.25},
            "C": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40},
        },
        "Q38": {
            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.40},
            "B": {**_z, "aptitude_liability": 0.25, "authority_liability": 0.40},
            "C": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.60},
            "D": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.60},
        },
        "Q39": {
            "A": {**_z, "aptitude_asset":    0.40, "authority_asset":    0.25},
            "B": {**_z, "aptitude_liability": 0.25, "authority_liability": 0.25},
            "C": {**_z, "aptitude_liability": 0.60, "authority_liability": 0.40},
            "D": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.60},
        },
    }
    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:'''


# ── Step 3 anchors — dimensional_contributions dispatch ──────────────────────

_OLD_DIM_CONTRIB = """\
                    dimensional_contributions={
                        **base,
                        \"aptitude_liability\": _opt_apt.get(qid, {}).get(
                            o[0], base[\"aptitude_liability\"]
                        ),
                    },"""

_NEW_DIM_CONTRIB = """\
                    dimensional_contributions=(
                        dict(_opt_contrib[qid][o[0]])
                        if qid in _opt_contrib
                        else {
                            **base,
                            \"aptitude_liability\": _opt_apt.get(qid, {}).get(
                                o[0], base[\"aptitude_liability\"]
                            ),
                        }
                    ),"""


# ── Patch logic ───────────────────────────────────────────────────────────────

def load_source() -> str:
    return TARGET.read_text(encoding="utf-8")


def patch(source: str) -> str:
    # Step 1 — Append Q35–Q39 to _QDATA
    if '"Q35"' in source:
        print("  INFO: Q35 already present in _QDATA — skipping Step 1.")
        patched = source
    else:
        if _QDATA_ANCHOR not in source:
            raise ValueError("Step 1: _QDATA end anchor not found.")
        patched = source.replace(_QDATA_ANCHOR, _QDATA_REPLACEMENT)
        print("  Step 1: Q35–Q39 _QDATA entries — will insert.")

    # Step 2 — Insert _opt_contrib before the for-loop
    if "_opt_contrib" in patched:
        print("  INFO: _opt_contrib already present — skipping Step 2.")
    else:
        if _FOR_LOOP_ANCHOR not in patched:
            raise ValueError("Step 2: for-loop anchor not found.")
        patched = patched.replace(_FOR_LOOP_ANCHOR, _OPT_CONTRIB_BLOCK)
        print("  Step 2: _opt_contrib dict — will insert.")

    # Step 3 — Update dimensional_contributions dispatch
    if _OLD_DIM_CONTRIB not in patched:
        if "if qid in _opt_contrib" in patched:
            print("  INFO: dimensional_contributions dispatch already present — skipping Step 3.")
        else:
            raise ValueError("Step 3: old dimensional_contributions pattern not found.")
    else:
        patched = patched.replace(_OLD_DIM_CONTRIB, _NEW_DIM_CONTRIB)
        print("  Step 3: dimensional_contributions dispatch — will update.")

    return patched


def diff_summary(original: str, updated: str) -> None:
    orig_lines = original.splitlines()
    upd_lines = updated.splitlines()
    added = [l for l in upd_lines if l not in orig_lines]
    removed = [l for l in orig_lines if l not in upd_lines]
    print(f"\n  Lines removed ({len(removed)}):")
    for l in removed[:20]:
        print(f"    - {l}")
    if len(removed) > 20:
        print(f"    ... and {len(removed) - 20} more")
    print(f"\n  Lines added ({len(added)}):")
    for l in added[:60]:
        print(f"    + {l}")
    if len(added) > 60:
        print(f"    ... and {len(added) - 60} more")


def dry_run() -> None:
    source = load_source()
    updated = patch(source)
    if source == updated:
        print("DRY-RUN: No changes would be made.")
        return
    print("\nDRY-RUN: Changes that would be applied to engine/data/questions.py:")
    diff_summary(source, updated)
    print("\nDRY-RUN complete. Run with --write to apply.")


def write() -> None:
    source = load_source()
    updated = patch(source)
    if source == updated:
        print("WRITE: No changes needed.")
        return
    TARGET.write_text(updated, encoding="utf-8")
    print("WRITE: engine/data/questions.py patched.")
    diff_summary(source, updated)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Phase 3 Pass 2 — Aptitude additive questions Q35–Q39"
    )
    parser.add_argument("--write", action="store_true", help="Apply changes (default: dry-run)")
    args = parser.parse_args()
    if args.write:
        write()
    else:
        dry_run()
