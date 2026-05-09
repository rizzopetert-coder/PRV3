"""
tools/patch_verify_probes.py
Session 14: Add 12 VERIFY verification probes to engine/data/questions.py.
Also adds seeding vocabulary note (0.50 intermediate value) and flags
VERIFY-Q25 for copy review.

Usage:
    python tools/patch_verify_probes.py          # dry-run (default)
    python tools/patch_verify_probes.py --write  # write file
"""
import sys
import argparse
from pathlib import Path

TARGET = Path(__file__).parents[1] / "engine" / "data" / "questions.py"

# ── Vocabulary note ────────────────────────────────────────────────────────────
# Inserted between _z closing } and _opt_contrib = {

_VOCAB_NOTE = """\
    # Contribution vocabulary for _opt_contrib:
    #   0.60 = HIGH           primary liability or asset — maximum signal confidence
    #   0.50 = INTERMEDIATE   between MEDIUM and HIGH; verification probe answers
    #                         that fall between ambiguous and clearly problem-indicating
    #   0.40 = MEDIUM         secondary or partial signal
    #   0.25 = LOW/baseline   minimal or cluster-level signal
    #   0.0  = absent         field not relevant to this option
"""

_VOCAB_ANCHOR = (
    '        "attitude_liability":  0.0, "attitude_asset":  0.0,\n'
    "    }\n"
    "    _opt_contrib = {"
)
_VOCAB_REPLACEMENT = (
    '        "attitude_liability":  0.0, "attitude_asset":  0.0,\n'
    "    }\n"
    + _VOCAB_NOTE
    + "    _opt_contrib = {"
)

# ── _opt_contrib entries ───────────────────────────────────────────────────────
# Inserted inside _opt_contrib dict, after Q39 entry, before closing }

_OPT_CONTRIB_INSERT = """\
        # -- Verification probes (Session 14) ----------------------------------------
        "VERIFY-Q16": {
            "A": {**_z, "attitude_asset":     0.40, "authority_asset":     0.40},
            "B": {**_z, "attitude_liability":  0.40, "authority_liability":  0.25},
            "C": {**_z, "attitude_liability":  0.40, "authority_liability":  0.25},
            "D": {**_z, "attitude_liability":  0.25},
        },
        "VERIFY-Q20": {
            "A": {**_z, "aptitude_asset":     0.40, "authority_asset":     0.40},
            "B": {**_z, "aptitude_liability":  0.25, "authority_liability":  0.25},
            "C": {**_z, "aptitude_liability":  0.40, "authority_liability":  0.40},
            "D": {**_z, "aptitude_asset":     0.25, "authority_asset":     0.40},
        },
        "VERIFY-Q21": {
            "A": {**_z, "authority_asset":     0.40},
            "B": {**_z, "authority_liability":  0.25},
            "C": {**_z, "authority_liability":  0.50},
            "D": {**_z, "authority_liability":  0.40, "aptitude_liability":  0.25},
        },
        "VERIFY-Q22": {
            "A": {**_z, "aptitude_asset":     0.40, "authority_asset":     0.40},
            "B": {**_z, "aptitude_liability":  0.25, "authority_liability":  0.25},
            "C": {**_z, "aptitude_liability":  0.50, "authority_liability":  0.40},
            "D": {**_z, "aptitude_liability":  0.60, "authority_liability":  0.60},
        },
        "VERIFY-Q24": {
            "A": {**_z, "attitude_asset":     0.40},
            "B": {**_z, "attitude_liability":  0.40},
            "C": {**_z, "attitude_liability":  0.60},
            "D": {**_z, "attitude_liability":  0.40},
        },
        "VERIFY-Q25": {
            "A": {**_z, "aptitude_asset":     0.40, "authority_asset":     0.40},
            "B": {**_z, "aptitude_liability":  0.25, "authority_liability":  0.25},
            "C": {**_z, "aptitude_liability":  0.50, "authority_liability":  0.40},
            "D": {**_z, "aptitude_liability":  0.60, "authority_liability":  0.40},
        },
        "VERIFY-Q26": {
            "A": {**_z, "alliance_asset":     0.40},
            "B": {**_z, "alliance_liability":  0.40},
            "C": {**_z, "alliance_liability":  0.50},
            "D": {**_z, "alliance_liability":  0.60},
        },
        "VERIFY-Q27A": {
            "A": {**_z, "alliance_asset":     0.40, "attitude_asset":     0.40},
            "B": {**_z, "alliance_liability":  0.25, "attitude_liability":  0.25},
            "C": {**_z, "alliance_liability":  0.50, "attitude_liability":  0.50},
            "D": {**_z, "alliance_liability":  0.60, "attitude_liability":  0.60},
        },
        "VERIFY-Q27B": {
            "A": {**_z, "attitude_asset":     0.40},
            "B": {**_z, "attitude_liability":  0.25},
            "C": {**_z, "attitude_liability":  0.50, "alliance_liability":  0.25},
            "D": {**_z, "attitude_liability":  0.60, "alliance_liability":  0.25},
        },
        "VERIFY-Q28": {
            "A": {**_z, "authority_asset":    0.40, "aptitude_asset":     0.40},
            "B": {**_z, "authority_liability": 0.40, "aptitude_liability":  0.25},
            "C": {**_z, "authority_liability": 0.50, "aptitude_liability":  0.40},
            "D": {**_z, "authority_liability": 0.60, "aptitude_liability":  0.60},
        },
        "VERIFY-Q31": {
            "A": {**_z, "authority_asset":    0.40},
            "B": {**_z, "authority_liability": 0.25},
            "C": {**_z, "authority_liability": 0.60, "alliance_liability":  0.40},
            "D": {**_z, "authority_liability": 0.60, "alliance_liability":  0.50},
        },
        "VERIFY-Q32": {
            "A": {**_z, "attitude_asset":     0.40, "authority_asset":     0.25},
            "B": {**_z, "attitude_liability":  0.25, "authority_liability":  0.25},
            "C": {**_z, "attitude_liability":  0.50, "authority_liability":  0.40},
            "D": {**_z, "attitude_liability":  0.60, "authority_liability":  0.40},
        },
"""

# The Q39 _opt_contrib block closes with this exact sequence; we insert before the }
_OPT_CONTRIB_ANCHOR = (
    '            "D": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.60},\n'
    "        },\n"
    "    }\n"
    "    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:"
)
_OPT_CONTRIB_REPLACEMENT = (
    '            "D": {**_z, "aptitude_liability": 0.40, "authority_liability": 0.60},\n'
    "        },\n"
    + _OPT_CONTRIB_INSERT
    + "    }\n"
    "    for (qid, text, fmt, pos, seg, opts, targets, sev) in _QDATA:"
)

# ── _QDATA entries ─────────────────────────────────────────────────────────────
# Inserted at the end of _QDATA, before the closing ]

_QDATA_INSERT = """\
    # -- Verification probes (Session 14) ----------------------------------------
    (
        "VERIFY-Q16",
        "What's that assessment based on?",
        "forced_choice", None, "conditional",
        [
            ("A", "We've looked at the data. Advancement rates by demographic group"
             " are tracked and reviewed.", False, None),
            ("B", "We don't have formal data on this"
             " — it's my read of how things are going.", False, None),
            ("C", "We've had the conversation but haven't pulled the numbers.", False, None),
            ("D", "We're a small enough organization that I can see it directly.",
             False, None),
        ],
        ["the_diversity_ceiling"],
        True,
    ),
    (
        "VERIFY-Q20",
        "When there's a disagreement about who owns a decision,"
        " how does it get resolved?",
        "forced_choice", None, "conditional",
        [
            ("A", "There's a clear escalation path."
             " It gets to the right person and resolves.", False, None),
            ("B", "It usually works out but the path isn't always obvious.", False, None),
            ("C", "It depends on the people involved — some figure it out,"
             " others escalate unnecessarily.", False, None),
            ("D", "That doesn't come up — ownership is clear enough"
             " that it doesn't create conflict.", False, None),
        ],
        ["built_to_fail", "the_undefined_role", "decision_paralysis"],
        True,
    ),
    (
        "VERIFY-Q21",
        "Think of a significant decision made in the last six months."
        " How long did it take from the moment it needed to be made"
        " to the moment it was made?",
        "forced_choice", None, "conditional",
        [
            ("A", "About as long as it should have."
             " The timeline matched the complexity.", False, None),
            ("B", "Longer than it needed to be, but the outcome was right.", False, None),
            ("C", "Longer than it needed to be, and the delay created real costs.",
             False, None),
            ("D", "I'm not sure I can think of a clear example"
             " — decisions tend to happen gradually.", False, None),
        ],
        ["decision_paralysis", "the_lost_map"],
        True,
    ),
    (
        "VERIFY-Q22",
        "When did your policies last get a meaningful review,"
        " and what changed as a result?",
        "forced_choice", None, "conditional",
        [
            ("A", "Within the past year. Specific updates were made,"
             " reviewed by counsel or HR leadership.", False, None),
            ("B", "Within the past year, but mostly incremental"
             " — format updates more than substantive changes.", False, None),
            ("C", "A few years ago. I can't point to a specific recent review.",
             False, None),
            ("D", "I'm not sure — I'd have to check who's responsible for that.",
             False, None),
        ],
        ["the_policy_lag", "the_unexamined_algorithm"],
        True,
    ),
    (
        "VERIFY-Q24",
        "How do you know?",
        "forced_choice", None, "conditional",
        [
            ("A", "We measure it. Engagement data, pulse surveys, or direct feedback"
             " with real follow-through.", False, None),
            ("B", "My read of the people I interact with most directly.", False, None),
            ("C", "They're performing, so I assume they're okay.", False, None),
            ("D", "I check in regularly and people tell me things are fine.", False, None),
        ],
        ["invisible_burnout"],
        True,
    ),
    (
        "VERIFY-Q25",
        # COPY REVIEW: two-part question — "who" + "what did the path look like"
        # Options address path quality only. Review in voice pass before deployment.
        "Who was the last person you promoted into a leadership role from within,"
        " and what did the development path look like?",
        "forced_choice", None, "conditional",
        [
            ("A", "I can name them. There was a deliberate path"
             " — coaching, expanded scope, clear criteria.", False, None),
            ("B", "I can name them but the path was more organic than structured.",
             False, None),
            ("C", "It's been a while since we've promoted from within"
             " into a leadership role.", False, None),
            ("D", "We promoted someone but it hasn't gone as well as we hoped.",
             False, None),
        ],
        ["leadership_continuity_risk", "the_dormant_talent", "the_unformed_leader"],
        True,
    ),
    (
        "VERIFY-Q26",
        "What was the last significant cross-functional initiative,"
        " and what made it work?",
        "forced_choice", None, "conditional",
        [
            ("A", "I can name it. Clear ownership, right people, produced the outcome.",
             False, None),
            ("B", "I can name it but it worked because specific people made it work"
             " — not because of the system.", False, None),
            ("C", "Cross-functional work tends to happen within clusters"
             " — some functions collaborate well, others don't.", False, None),
            ("D", "It's hard to name a specific example"
             " — most work stays within functions.", False, None),
        ],
        ["silosolation", "the_fracture"],
        True,
    ),
    (
        "VERIFY-Q27A",
        "What specifically has been done to integrate the people and culture side"
        " — not the systems and processes?",
        "forced_choice", None, "conditional",
        [
            ("A", "A specific plan with owners, milestones,"
             " and progress we're tracking.", False, None),
            ("B", "Some deliberate effort but it's been more reactive than planned.",
             False, None),
            ("C", "We've focused on the structural side"
             " — people and culture integration hasn't had the same attention.",
             False, None),
            ("D", "We haven't treated people and culture as a separate workstream.",
             False, None),
        ],
        ["the_second_close"],
        True,
    ),
    (
        "VERIFY-Q27B",
        "If you asked a new hire six months in what surprised them about the culture,"
        " what would they say?",
        "forced_choice", None, "conditional",
        [
            ("A", "Nothing significant"
             " — what they experienced matched what they were told.", False, None),
            ("B", "Mostly matched, but some things were different than they expected.",
             False, None),
            ("C", "I'm not sure"
             " — we don't have good visibility into the new hire experience.",
             False, None),
            ("D", "There are things people mention that suggest a gap"
             " between what we say and what they find.", False, None),
        ],
        ["culture_drift", "identity_erosion", "the_culture_that_wasnt"],
        True,
    ),
    (
        "VERIFY-Q28",
        "What specifically changed,"
        " and how do you know it addressed the root cause?",
        "forced_choice", None, "conditional",
        [
            ("A", "I can describe it. Named changes, traceable to the condition,"
             " confirmed by follow-up.", False, None),
            ("B", "We made changes but I couldn't say with confidence"
             " we got to the root.", False, None),
            ("C", "Process updates and policy changes"
             " — more procedural than structural.", False, None),
            ("D", "Honestly, the situation resolved and we moved forward."
             " I'm not sure what specifically changed.", False, None),
        ],
        ["the_unsolved_problem"],
        True,
    ),
    (
        "VERIFY-Q31",
        "What makes you confident they're unrelated?",
        "forced_choice", None, "conditional",
        [
            ("A", "We looked at them together."
             " No common thread in circumstances, people, or outcomes.", False, None),
            ("B", "They happened at different times,"
             " in different parts of the organization.", False, None),
            ("C", "I haven't looked at them together"
             " — that's my read but I haven't verified it.", False, None),
            ("D", "I'm not sure anyone has looked at them as a set.", False, None),
        ],
        ["the_unsolved_problem", "decision_blindness"],
        True,
    ),
    (
        "VERIFY-Q32",
        "What's an example of something your organization examined,"
        " concluded needed to change, and actually changed?",
        "forced_choice", None, "conditional",
        [
            ("A", "I can name it. Specific situation, clear conclusion,"
             " observable change that held.", False, None),
            ("B", "I can name it but the change was partial"
             " — we moved in the right direction but didn't complete it.", False, None),
            ("C", "It's hard to name a specific example"
             " where the full cycle completed.", False, None),
            ("D", "We're good at the examining and concluding part."
             " The changing part is harder.", False, None),
        ],
        ["narrative_lock", "groundhog_day", "the_broken_compass"],
        True,
    ),
"""

# Q39 closes _QDATA; anchor is the last three lines of the list
_QDATA_ANCHOR = (
    '        ["the_paper_tiger", "the_unformed_leader", "built_to_fail"],\n'
    "        False,\n"
    "    ),\n"
    "]\n"
)
_QDATA_REPLACEMENT = (
    '        ["the_paper_tiger", "the_unformed_leader", "built_to_fail"],\n'
    "        False,\n"
    "    ),\n"
    + _QDATA_INSERT
    + "]\n"
)


# ── Patch logic ────────────────────────────────────────────────────────────────

def apply_patches(text: str) -> tuple[str, list[str]]:
    """
    Apply all three patches and return (patched_text, list_of_applied_patches).
    Raises ValueError if any anchor is not found or is not unique.
    """
    applied = []

    def replace_once(src: str, old: str, new: str, label: str) -> str:
        count = src.count(old)
        if count == 0:
            raise ValueError(f"Anchor not found: {label!r}")
        if count > 1:
            raise ValueError(f"Anchor not unique ({count} matches): {label!r}")
        applied.append(label)
        return src.replace(old, new, 1)

    text = replace_once(text, _VOCAB_ANCHOR,       _VOCAB_REPLACEMENT,       "vocab_note")
    text = replace_once(text, _OPT_CONTRIB_ANCHOR, _OPT_CONTRIB_REPLACEMENT, "_opt_contrib entries")
    text = replace_once(text, _QDATA_ANCHOR,       _QDATA_REPLACEMENT,       "_QDATA entries")

    return text, applied


def verify_library(patched_text: str) -> int:
    """
    Execute the patched source in an isolated namespace and return library size.
    """
    ns: dict = {}
    exec(compile(patched_text, str(TARGET), "exec"), ns)
    return len(ns["QUESTION_LIBRARY"])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true",
                        help="Write patched file (default: dry-run)")
    args = parser.parse_args()
    dry_run = not args.write

    original = TARGET.read_text(encoding="utf-8")
    original_lines = original.count("\n")

    try:
        patched, applied = apply_patches(original)
    except ValueError as exc:
        print(f"PATCH FAILED: {exc}")
        sys.exit(1)

    patched_lines = patched.count("\n")

    # Verify the patched source parses and the library loads
    try:
        original_lib_size = verify_library(original)
        patched_lib_size  = verify_library(patched)
    except Exception as exc:
        print(f"LIBRARY LOAD FAILED: {exc}")
        sys.exit(1)

    # ── Report ─────────────────────────────────────────────────────────────────
    print("=" * 72)
    print(f"patch_verify_probes.py  {'DRY-RUN' if dry_run else 'WRITE'}")
    print("=" * 72)
    print(f"\nTarget:          {TARGET}")
    print(f"Patches applied: {', '.join(applied)}")
    print(f"Lines:           {original_lines} -> {patched_lines} (+{patched_lines - original_lines})")
    print(f"Library size:    {original_lib_size} -> {patched_lib_size} entries "
          f"(+{patched_lib_size - original_lib_size})")

    # Show the new question IDs
    ns: dict = {}
    exec(compile(patched, str(TARGET), "exec"), ns)
    lib = ns["QUESTION_LIBRARY"]
    new_ids = [qid for qid in lib if qid.startswith("VERIFY-")]
    print(f"\nNew VERIFY entries ({len(new_ids)}):")
    for qid in sorted(new_ids):
        q = lib[qid]
        n_opts = len(q.answer_options)
        targets = q.state_targets
        print(f"  {qid:<16}  {n_opts} options  targets={targets}")

    # Spot-check VERIFY-Q28-D aptitude_liability (confirmed adjustment: 0.50 → 0.60)
    q28d = next(o for o in lib["VERIFY-Q28"].answer_options if o.option_id == "D")
    apt_d = q28d.dimensional_contributions.get("aptitude_liability", 0)
    check = "OK" if apt_d == 0.60 else f"FAIL (got {apt_d})"
    print(f"\nVERIFY-Q28-D aptitude_liability = {apt_d}  [{check}]")

    # Spot-check 0.50 values present
    probe_50 = []
    for qid in new_ids:
        for opt in lib[qid].answer_options:
            for field, val in opt.dimensional_contributions.items():
                if val == 0.50:
                    probe_50.append(f"{qid}-{opt.option_id}.{field}")
    print(f"0.50 intermediate values ({len(probe_50)}): {probe_50}")

    # Spot-check VERIFY-Q25 copy review comment survives (in source text)
    copy_flag = "COPY REVIEW" in patched
    print(f"VERIFY-Q25 copy review flag present: {'YES' if copy_flag else 'MISSING'}")

    print(f"\n{'DRY-RUN complete — no file written.' if dry_run else ''}", end="")

    if not dry_run:
        TARGET.write_text(patched, encoding="utf-8")
        print(f"Written: {TARGET}")

    print("\n" + "=" * 72)
    sys.exit(0)


if __name__ == "__main__":
    main()
