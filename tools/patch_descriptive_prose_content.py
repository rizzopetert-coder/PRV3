"""
PRV3 -- Tier 4 content population: descriptive_prose for all 57 states

Part A of the descriptive_prose content-population follow-on task.
Content authored by Pete this session, third-person diagnostic register
(private-report voice, distinct from web/data/taxonomy.ts's second-
person self-recognition voice). Architecture was Gemini-reviewed at the
schema-addition step; the prose itself doesn't need a structural gate,
same convention as the resolution-family copy.

For each state_id, inserts:
    STATE_PROFILES["state_id"].descriptive_prose = "..."
immediately after that state's existing dimensional_vector
post-construction assignment block, preserving the file's existing
per-state grouping and blank-line spacing before the next block.

Placement method: locate the unique
  STATE_PROFILES["state_id"].dimensional_vector = DimensionalVector(
marker for each state (confirmed exactly one occurrence per state_id
via prior grep), then find that block's closing "\n)\n" and insert the
new assignment line immediately after it. This avoids hand-crafting 57
large anchor blocks and is robust to the per-state field-count
differences in each DimensionalVector(...) call.

Verification, pre-write: 57 state_ids cross-checked against the live
STATE_PROFILES registry -- exact match, zero duplicates, zero missing,
zero extra (confirmed via a separate one-off script this session).

Usage:
  python tools/patch_descriptive_prose_content.py --dry-run
  python tools/patch_descriptive_prose_content.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
STATES_PY = REPO_ROOT / "engine" / "data" / "states.py"

DESCRIPTIVE_PROSE: dict[str, str] = {
    # ── APTITUDE ──
    "the_unformed_leader": "A manager occupies the role without having been equipped for it. Direction is inconsistent, feedback arrives late or not at all, and the team absorbs the gap by lowering its own expectations. Turnover concentrates among the people who had other options.",
    "the_overloaded_manager": "A manager who was competent for the original scope of the role is now carrying more than the role was designed to hold. Development conversations have been replaced by status updates, and decisions queue behind everything else competing for the same attention. The organization redesigned the job without redesigning the resources around it.",
    "the_dormant_talent": "The manager can name precisely what each person needs to grow and consistently doesn't act on it. Development stalls while the manager's own visibility and standing continue to rise. The people with the clearest read on the gap are also the ones most able to leave.",
    "built_to_fail": "The role's scope exceeds what any reasonable allocation of resources could support, and each person who holds it is told to make it work rather than given what making it work would require. The organization treats each departure as an individual hiring failure rather than a structural one. The next person inherits the same impossible math.",
    "the_undefined_role": "The role's actual boundaries were never defined, so what lands on the desk, what gets escalated, and what falls through are all matters of local negotiation rather than design. Work duplicates in some places and goes unclaimed in others. The organization is paying for a function that isn't reliably producing what anyone assumes it produces.",
    "the_paper_tiger": "A performance problem has been managed verbally for long enough that the written record no longer matches what everyone privately knows. When the organization finally needs to act on documented cause, it discovers it has been managing one employee on paper and a different one in practice. The gap surfaces in front of the people with the least patience for it.",
    "invisible_performance_management": "A manager's read on an underperforming employee is accurate but was never written down, so it carries no evidentiary weight when a decision needs defending. This isn't concealment. It's an absence of documentation that turns a sound judgment into an exposed one.",
    # ── AUTHORITY ──
    "the_founders_grip": "One person's approval gates nearly every consequential decision, and that person is stretched too thin to make those calls on current information. Work either waits in queue or routes around the bottleneck entirely. The senior people who could tolerate neither option have already left.",
    "the_exposed": "There is no function in the organization whose job it actually is to manage employee-related risk. Concerns have nowhere reliable to land, and obligations accumulate without anyone tracking them. The organization isn't between HR leaders. It's accumulating liability on a clock nobody is watching.",
    "the_uninitiated": "A significant organizational event is underway, and the people leading it have never done this before. They are capable in general and unprepared for this specific kind of decision, which means the costliest mistakes are the ones nobody on the team knows to watch for.",
    "leadership_continuity_risk": "Authority concentrated in a small number of people has no defined path to anyone else if one of them leaves. The organization can name who is critical but not who would replace them or how. That gap becomes a crisis the moment it stops being theoretical.",
    "hr_capture": "The function responsible for protecting the organization and its people has been repurposed to protect specific leaders instead. Complaints against the powerful get managed differently than complaints against everyone else, and the people making that distinction know exactly what they're doing.",
    "decision_paralysis": "Decisions that should move at operational speed are instead stalling in a governance structure that was never built to render verdicts quickly. Nobody is refusing to decide. The structure itself doesn't produce clear ownership of the call.",
    "the_policy_lag": "The organization's written policies describe an operating reality that no longer exists. Practice has moved on without the documentation catching up, so the rules on paper and the rules people actually follow have quietly diverged.",
    "the_unexamined_algorithm": "An automated or algorithmic system is making or materially influencing consequential decisions with no governance layer reviewing what it's actually doing. Nobody owns auditing its outputs for bias, error, or drift. The organization finds out something was wrong only after it's been wrong for a while.",
    "heard_and_ignored": "Concerns are being raised through the organization's own channels and are reliably not acted on. The reporting mechanism exists and functions as a formality, not a corrective one. People stop using it once they've tested it enough times to know what happens when they do.",
    "the_tolerated_violation": "A known violation of policy, law, or basic standard has been allowed to continue long enough that it now reads as normal rather than exceptional. Everyone involved can describe the violation accurately. Nobody with the authority to stop it has been willing to be the one who does.",
    "dueling_narratives": "Different parts of the organization are telling meaningfully different versions of the same set of facts, and nobody has reconciled them into one account. Each version is defensible in isolation. Together they create exposure the moment anyone outside the organization compares notes.",
    "the_unsolved_problem": "A specific problem has been addressed before, more than once, and keeps returning in close to the same form. Each fix treats the most recent symptom rather than whatever keeps regenerating it. The organization is paying repeatedly for a resolution that has never actually resolved anything.",
    "transition_paralysis": "An organizational transition has started and then stalled somewhere in the middle, with the old structure partly dismantled and the new one not yet functional. People are operating in the gap, uncertain which authority actually governs their work day to day.",
    "paper_shield": "Contingency and continuity plans exist in writing and have never been tested against anything real. The organization believes it is prepared because the documentation says so. The gap between documented readiness and actual readiness surfaces exactly once, at the worst time to discover it.",
    "the_lost_map": "Institutional knowledge lives in individual heads rather than in any system the organization actually maintains. When someone leaves, whatever they knew leaves with them, and the organization relearns it the expensive way.",
    "invisible_influence_architecture": "Real influence over decisions runs through informal channels that don't match the org chart anyone would draw. The formally accountable people are not always the ones actually deciding outcomes. New arrivals spend real time discovering who actually has to say yes.",
    "pay_exposure": "Compensation has drifted out of alignment with what the market is currently paying for comparable roles, and the organization is discovering this reactively, through departures, rather than proactively. Each departure it triggers is a preventable one.",
    "the_pay_fog": "Pay decisions across the organization don't follow a consistent, defensible logic, even though each individual decision might have made sense in the moment it was made. That inconsistency is hard to see from inside any one decision and impossible to miss once someone lines them all up.",
    "compression_crisis": "Layers of management have been compressed or eliminated faster than the remaining structure can absorb the load, concentrating decision-making into fewer people than the work actually requires. What looks like efficiency on an org chart is strain everywhere it actually gets executed.",
    "sequential_decision_blindness": "A series of individually defensible decisions, made by different people without coordination, adds up to a pattern that looks like retaliation or targeting when viewed together. No single decision-maker intended that outcome. The exposure exists in the aggregate, not in any one decision anyone can point to.",
    "disparate_impact_architecture": "A policy or practice applies the same rule to everyone and produces meaningfully different outcomes across different groups, in a pattern that would be recognizable to anyone who looked at the aggregate data. Neutral intent doesn't change what the data shows.",
    "planning_authority_gap": "The people responsible for planning don't hold the authority to make the decisions their plans depend on, and the people who hold that authority aren't the ones doing the planning. Plans get built and then wait for approval from someone who wasn't part of building them.",
    # ── ALLIANCE ──
    "the_fracture": "A working relationship between two people, teams, or functions that the organization depends on has broken down past the point of informal repair. Work still moves, but it moves around the fracture rather than through it.",
    "the_second_close": "A relationship or agreement was renegotiated once already, and the same underlying issue that forced the first renegotiation is resurfacing. Whatever the first fix addressed, it wasn't the actual cause. The people involved are less willing to extend trust a second time.",
    "silosolation": "Teams that need each other's information to do their jobs well are operating as if they don't, each optimizing for its own metrics without visibility into how that affects anyone else. The isolation isn't hostile. It's structural, and it produces the same friction hostility would.",
    "the_suppression_filter": "Bad news gets filtered, softened, or dropped entirely as it moves up through the organization's layers, so the people with authority to act on it are consistently the last to hear an accurate version. Each layer believes it's protecting leadership from noise.",
    "the_arbitrary_standard": "The rules that govern who gets what treatment aren't applied consistently, and the pattern of who benefits isn't accidental even if nobody designed it on purpose. People notice the inconsistency well before anyone in leadership does.",
    "decision_blindness": "A single significant decision was made without input from the people who held the information that would have changed it. The decision-maker wasn't negligent. The information simply never reached them, because nobody's job was making sure it did.",
    "distributed_culture_fragmentation": "Teams operating in different locations, functions, or time zones have developed genuinely different norms for how work gets done, and nobody has reconciled them into one coherent culture. The friction shows up exactly at the seams where the teams have to work together.",
    # ── ATTITUDE ──
    "the_untouchable": "One person's results or position have made them functionally exempt from the standards everyone else is held to. Everyone around them can name the exemption specifically. The cost isn't just what that person does. It's what everyone watching learns about what the organization actually values.",
    "what_nobody_says": "There is a specific, known problem that people in the organization can describe accurately in private and will not raise anywhere it might reach someone with the authority to fix it. The silence isn't accidental. It's a rational response to what happened, or is believed to happen, to the last person who spoke up.",
    "leadership_deafness": "Leadership is operating on a version of organizational reality that the people below them stopped believing months or years ago. The gap isn't intentional deception so much as an accumulated pattern of information getting softened on its way up.",
    "the_diversity_ceiling": "The organization's stated commitment to diversity and inclusion is visible in messaging and invisible in outcomes. Representation doesn't advance past a specific point in the hierarchy no matter how the numbers look at entry level. People below that ceiling can see exactly where it sits.",
    "culture_drift": "The organization's stated values and its actual day-to-day behavior have drifted apart gradually enough that no single moment marks the change. Nobody decided to abandon the values. They just stopped being what got rewarded.",
    "identity_erosion": "The organization has lost a clear, shared answer to what it actually is and what makes it different from anywhere else someone could work. That uncertainty shows up first in retention and recruiting, before it shows up anywhere leadership is looking.",
    "the_culture_that_wasnt": "What was described during hiring and what actually exists inside the organization are two different cultures, and new hires discover the gap almost immediately. The mismatch is sharpest and most damaging in the first few months, before anyone has built enough tenure to rationalize it.",
    "the_burned_credibility": "Leadership has announced significant changes before and either didn't follow through or followed through badly enough that people stopped believing the announcements. The next initiative, however well designed, inherits the skepticism earned by the last one.",
    "invisible_burnout": "People are burning out while their output looks fine, which means the organization's usual signals for catching the problem aren't catching it. The cost surfaces later, all at once, as a resignation or a mistake that looks sudden but wasn't.",
    "the_basement_standard": "A standard of performance well below what the organization would say it expects has become the accepted baseline, because nobody has been willing to enforce the standard that's actually on paper. The best performers notice the gap first, and leave.",
    "the_inside_track": "Advancement and opportunity flow disproportionately to a specific, identifiable group through channels that aren't the organization's stated process. Everyone outside that group can name it, usually specifically.",
    "narrative_lock": "The organization keeps telling itself and its people a story about who it is that stopped being accurate some time ago, and it can't update that story even when the facts on the ground contradict it. Anyone who challenges the story is treated as the problem rather than the messenger.",
    "groundhog_day": "The same class of mistake recurs across projects, teams, or cycles, and the organization has no mechanism for capturing what it learned the last time so it doesn't happen again. Each recurrence gets treated as a new problem rather than a repeat of an old one.",
    "the_wrong_reward": "The organization is getting exactly the behavior its incentive structure actually rewards, and that behavior is not the one leadership says it wants. People are responding rationally to the real incentives, not the stated ones.",
    "the_unreported_hazard": "Real safety concerns exist and are not reliably making it into the organization's reporting system, for reasons that have more to do with culture than process. People have learned that reporting doesn't change much and might cost them something personally.",
    "the_unlocked_door": "Security or safety practices that were adequate for an earlier version of the organization haven't kept pace with how the organization actually operates now. Nobody decided to leave the door open. It's simply never been revisited.",
    "the_broken_compass": "The organization can articulate the right strategic direction clearly and consistently fails to actually move in it when the moment requires a hard call. The gap isn't a knowledge problem. It's a courage problem, and it shows up at exactly the moments that matter most.",
    "wellbeing_theater": "The organization has visible wellbeing programming that isn't changing the underlying conditions actually driving people's stress and dissatisfaction. The initiatives address the symptom the organization is comfortable addressing rather than the cause it would rather not name.",
    "human_displacement_anxiety": "People across the organization are anxious about being displaced by automation or AI, and that anxiety is affecting engagement and decision-making whether or not the organization has any actual plans in that direction. Silence from leadership doesn't read as reassurance. It reads as confirmation.",
    "motivational_architecture_failure": "The organization's reward system has stopped functioning as a source of motivation at all, for enough of the workforce that engagement has flattened across the board rather than in any one identifiable group. People haven't misread the incentives. They've stopped believing the incentives connect to anything real.",
    "cultural_overtime": "Extended hours have become an unstated cultural expectation rather than an occasional operational necessity, and the organization is carrying real legal and financial exposure from that norm without having decided, on paper, that it wants to run this way.",
}

# Registration order, for the count/coverage check and deterministic diff order.
_ORDER = list(DESCRIPTIVE_PROSE.keys())


def _find_all(text: str, needle: str) -> list[int]:
    positions = []
    start = 0
    while True:
        idx = text.find(needle, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + 1
    return positions


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    if len(_ORDER) != 57 or len(set(_ORDER)) != 57:
        print(f"ABORT -- expected 57 unique state_ids, got {len(_ORDER)} ({len(set(_ORDER))} unique)", file=sys.stderr)
        sys.exit(1)

    text = STATES_PY.read_text(encoding="utf-8")
    diffs = []

    for state_id in _ORDER:
        marker = f'STATE_PROFILES["{state_id}"].dimensional_vector = DimensionalVector('
        positions = _find_all(text, marker)
        if len(positions) == 0:
            print(f"ABORT -- dimensional_vector marker not found for {state_id!r}", file=sys.stderr)
            sys.exit(1)
        if len(positions) > 1:
            print(f"ABORT -- dimensional_vector marker not unique for {state_id!r} ({len(positions)} matches)", file=sys.stderr)
            sys.exit(1)

        start = positions[0]
        close_idx = text.find("\n)\n", start)
        if close_idx == -1:
            print(f"ABORT -- closing ')' not found for {state_id!r}'s dimensional_vector block", file=sys.stderr)
            sys.exit(1)

        insert_at = close_idx + len("\n)\n")
        prose = DESCRIPTIVE_PROSE[state_id]
        new_line = f'STATE_PROFILES["{state_id}"].descriptive_prose = "{prose}"\n'

        # Guard against having already inserted this state's line (idempotency
        # check, in case this script is re-run after a partial write).
        already_present = f'STATE_PROFILES["{state_id}"].descriptive_prose' in text
        if already_present:
            print(f"ABORT -- {state_id!r} already has a descriptive_prose assignment; refusing to duplicate", file=sys.stderr)
            sys.exit(1)

        diffs.append((state_id, insert_at, new_line))

    # Apply from the END of the file backward so earlier insert_at offsets
    # stay valid as the string grows.
    diffs.sort(key=lambda d: d[1], reverse=True)
    new_text = text
    for state_id, insert_at, new_line in diffs:
        new_text = new_text[:insert_at] + new_line + new_text[insert_at:]

    # Report in registration order, not insertion (reverse) order.
    print(f"Target: {STATES_PY.relative_to(REPO_ROOT)}")
    print(f"States to update: {len(_ORDER)}")
    print("=" * 72)
    for state_id in _ORDER:
        prose = DESCRIPTIVE_PROSE[state_id]
        print(f'+ STATE_PROFILES["{state_id}"].descriptive_prose = "{prose[:70]}..."')
    print("=" * 72)

    if args.dry_run:
        print(f"\nDRY RUN -- {len(_ORDER)} assignments would be inserted, no file written.")
        return

    STATES_PY.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {STATES_PY.relative_to(REPO_ROOT)} -- {len(_ORDER)} assignments inserted.")


if __name__ == "__main__":
    main()
