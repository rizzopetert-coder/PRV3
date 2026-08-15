"""
PRV3 -- /book/toc Phase 1 data confirmation. Three edits, all pure data,
zero behavior change (nothing in the live app consumes taxonomy.ts's new
state entry or book-state-index.ts's new field yet):

(1) web/data/taxonomy.ts -- add the_inner_circle (58th state, confirmed
    missing) as a new state entry, signatureId: "culture_erosion". Pete's
    call, on review of the real 5-signature list: this state shares its
    core mechanism (inconsistent application of standards/accountability
    based on identity or relationship) with the_inside_track,
    the_wrong_reward, the_basement_standard, and the_burned_credibility --
    a real fit, not a forced one. Also added to Culture Erosion's
    stateIds array to keep both membership representations
    (Signature.stateIds and the state's own signatureId field) in sync,
    verified those two representations already matched exactly for all
    57 pre-existing states before this addition.

    NOTE: this state was originally added with signatureId: "" (left
    unassigned pending Pete's review) and reassigned to culture_erosion
    in a follow-up correction, same session. This script reflects the
    final state, not the intermediate one.

(2) web/lib/book-state-index.ts -- new resolutionFamily field on
    BookStateEntry, populated for all 58 states directly from
    engine/data/states.py's STATE_PROFILES (same source, same mirroring
    pattern already used for id/name/dimension/descriptiveProse). Raw
    engine value, not translated -- consumers use resolution-family.ts's
    existing translateResolutionFamily() at display time, same as every
    other real caller, not a second copy of that logic.

Run with --dry-run first (default). Pass --write to apply.
"""
import argparse
import pathlib
import sys

TAXONOMY_PATH = pathlib.Path("web/data/taxonomy.ts")
BOOK_INDEX_PATH = pathlib.Path("web/lib/book-state-index.ts")

# ---------------------------------------------------------------------------
# (1) taxonomy.ts -- the_inner_circle
# ---------------------------------------------------------------------------

OLD_TAXONOMY_ANCHOR = '''  {
    id: "cultural_overtime",
    name: "Cultural Overtime",
    signatureId: "culture_erosion",
    description:
      "Compensable work produced outside paid hours through cultural pressure rather than explicit instruction. The policy is compliant. The culture creates the liability. Distinct from Structural Overload — this is about expected availability, not volume.",
  },
];'''

NEW_TAXONOMY_ANCHOR = '''  {
    id: "cultural_overtime",
    name: "Cultural Overtime",
    signatureId: "culture_erosion",
    description:
      "Compensable work produced outside paid hours through cultural pressure rather than explicit instruction. The policy is compliant. The culture creates the liability. Distinct from Structural Overload — this is about expected availability, not volume.",
  },
  // the_inner_circle -- 58th state (taxonomy expansion, prior session), this
  // session's own data-availability check confirmed it was missing from
  // this file entirely (57 states, not 58) while already present and
  // correct in web/lib/book-state-index.ts. signatureId assigned to
  // culture_erosion -- Pete's call, on review of the real member list: the
  // group shares this state's core mechanism (inconsistent application of
  // standards/accountability based on identity or relationship) with
  // the_inside_track, the_wrong_reward, the_basement_standard, and
  // the_burned_credibility, not just a loose thematic echo. Also added to
  // Culture Erosion's stateIds array below to keep both membership
  // representations in sync, per the pattern already confirmed to matter
  // for this file. description reuses book-state-index.ts's real
  // descriptiveProse verbatim -- already-authored, already-real content,
  // not invented new copy for this addition.
  {
    id: "the_inner_circle",
    name: "The Inner Circle",
    signatureId: "culture_erosion",
    description:
      "There's a group at the top of this organization who look out for each other first. Decisions get made in rooms you're not in, by people who protect each other's mistakes as readily as their own. It isn't about one person getting away with something — it's a whole layer that answers to itself instead of any standard. The people outside the circle have figured out exactly what that means for them.",
  },
];'''

# ---------------------------------------------------------------------------
# (2) book-state-index.ts -- resolutionFamily field
# ---------------------------------------------------------------------------

OLD_INTERFACE = '''export interface BookStateEntry {
  id: string;
  name: string;
  dimension: StateDimension;
  descriptiveProse: string;
}'''

NEW_INTERFACE = '''export interface BookStateEntry {
  id: string;
  name: string;
  dimension: StateDimension;
  // Raw engine/data/states.py STATE_PROFILES resolution_family value
  // (e.g. "Executive Counsel + Intervention"), not translated -- added
  // this session for /book/toc's resolution_family badge (Phase 1 data
  // confirmation, prompts/book-toc-fuller-vision.md). Same mirroring
  // pattern as every other field here, same source. Consumers translate
  // via web/lib/resolution-family.ts's translateResolutionFamily() at
  // display time, same as every other real caller -- not a second copy
  // of that logic.
  resolutionFamily: string;
  descriptiveProse: string;
}'''

# Resolution family values, exact order matching the file's existing
# 58 entries (verified against engine/data/states.py's STATE_PROFILES
# directly, not hand-typed from memory).
RESOLUTION_FAMILIES = {
    "the_unformed_leader": "Development",
    "the_overloaded_manager": "Development + Roadmap",
    "the_dormant_talent": "Executive Counsel + Intervention",
    "built_to_fail": "Roadmap + Intervention",
    "the_undefined_role": "Roadmap",
    "the_paper_tiger": "Development + Roadmap",
    "invisible_performance_management": "Development + Roadmap",
    "the_founders_grip": "Intervention + Executive Counsel",
    "the_exposed": "Intervention + Executive Counsel",
    "the_uninitiated": "Intervention",
    "leadership_continuity_risk": "Roadmap + Development",
    "hr_capture": "Intervention + Executive Counsel",
    "decision_paralysis": "Roadmap + Intervention",
    "the_policy_lag": "Roadmap",
    "the_unexamined_algorithm": "Roadmap + Executive Counsel",
    "heard_and_ignored": "Intervention + Executive Counsel",
    "the_tolerated_violation": "Intervention + Executive Counsel",
    "dueling_narratives": "Executive Counsel + Roadmap",
    "the_unsolved_problem": "Intervention + Roadmap",
    "transition_paralysis": "Intervention + Roadmap",
    "paper_shield": "Roadmap",
    "the_lost_map": "Roadmap + Development",
    "invisible_influence_architecture": "Roadmap + Executive Counsel",
    "pay_exposure": "Roadmap",
    "the_pay_fog": "Roadmap",
    "compression_crisis": "Roadmap",
    "sequential_decision_blindness": "Intervention + Executive Counsel",
    "disparate_impact_architecture": "Intervention + Executive Counsel",
    "planning_authority_gap": "Roadmap + Executive Counsel",
    "the_fracture": "Intervention + Executive Counsel",
    "the_second_close": "Development + Intervention",
    "silosolation": "Development",
    "the_suppression_filter": "Intervention + Executive Counsel",
    "the_arbitrary_standard": "Intervention + Roadmap",
    "decision_blindness": "Intervention + Executive Counsel",
    "distributed_culture_fragmentation": "Development + Intervention",
    "the_untouchable": "Executive Counsel + Intervention",
    "what_nobody_says": "Intervention",
    "leadership_deafness": "Executive Counsel",
    "the_diversity_ceiling": "Intervention",
    "culture_drift": "Intervention",
    "identity_erosion": "Intervention",
    "the_culture_that_wasnt": "Intervention",
    "the_burned_credibility": "Intervention",
    "invisible_burnout": "Development + Intervention",
    "the_basement_standard": "Intervention + Roadmap",
    "the_inside_track": "Intervention + Roadmap",
    "narrative_lock": "Executive Counsel + Intervention",
    "groundhog_day": "Roadmap + Executive Counsel",
    "the_wrong_reward": "Intervention + Roadmap",
    "the_unreported_hazard": "Intervention",
    "the_unlocked_door": "Development + Intervention",
    "the_broken_compass": "Executive Counsel",
    "wellbeing_theater": "Intervention",
    "human_displacement_anxiety": "Development + Intervention",
    "motivational_architecture_failure": "Intervention + Roadmap",
    "cultural_overtime": "Intervention + Roadmap",
    "the_inner_circle": "Intervention + Executive Counsel",
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    # --- taxonomy.ts ---
    taxonomy = TAXONOMY_PATH.read_text(encoding="utf-8")
    taxonomy_orig = taxonomy
    count = taxonomy.count(OLD_TAXONOMY_ANCHOR)
    if count != 1:
        print(f"FAIL (taxonomy.ts): expected 1 match, found {count}")
        sys.exit(1)
    taxonomy = taxonomy.replace(OLD_TAXONOMY_ANCHOR, NEW_TAXONOMY_ANCHOR, 1)

    # --- book-state-index.ts ---
    book_index = BOOK_INDEX_PATH.read_text(encoding="utf-8")
    book_index_orig = book_index
    count = book_index.count(OLD_INTERFACE)
    if count != 1:
        print(f"FAIL (book-state-index.ts interface): expected 1 match, found {count}")
        sys.exit(1)
    book_index = book_index.replace(OLD_INTERFACE, NEW_INTERFACE, 1)

    for state_id, family in RESOLUTION_FAMILIES.items():
        old = f'    id: "{state_id}",\n'
        count = book_index.count(old)
        if count != 1:
            print(f"FAIL (book-state-index.ts, {state_id}): expected 1 match, found {count}")
            sys.exit(1)
        new = old + f'    resolutionFamily: "{family}",\n'
        book_index = book_index.replace(old, new, 1)

    if taxonomy == taxonomy_orig:
        print("FAIL: taxonomy.ts unchanged")
        sys.exit(1)
    if book_index == book_index_orig:
        print("FAIL: book-state-index.ts unchanged")
        sys.exit(1)

    print(f"taxonomy.ts diff: {len(taxonomy) - len(taxonomy_orig):+d} chars")
    print(f"book-state-index.ts diff: {len(book_index) - len(book_index_orig):+d} chars")
    print(f"book-state-index.ts: {len(RESOLUTION_FAMILIES)} resolutionFamily fields inserted")

    if args.write:
        TAXONOMY_PATH.write_text(taxonomy, encoding="utf-8")
        BOOK_INDEX_PATH.write_text(book_index, encoding="utf-8")
        print("WRITTEN.")
    else:
        print("DRY RUN -- no files written. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
