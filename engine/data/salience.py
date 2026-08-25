"""
PRV3 Scoring Engine — Section II.4 Supplemental
Per-State Salience Weight Profiles

SALIENCE_PROFILES: dict mapping state_id -> {field: weight}

Seeding rule — three-tier architecture (v18, Session 23):
  HIGH/MEDIUM states: primary fields 2.5; all others 0.4
  LOW/CLUSTER states: primary fields 2.5; secondary fields 1.0; all others 0.4
  (Session 21 original: binary seeding — primary 2.5, secondary 2.5, others 0.4)

Used by rank_states() when salience_weights is passed explicitly.
Import: from engine.data.salience import SALIENCE_PROFILES
"""

SALIENCE_PROFILES = {

    # ── APTITUDE — HIGH tier (primary only) ───────────────────────────────────
    "built_to_fail": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    # SCD-WCS remediation pilot (2026-08-20, rank-8): previously shared
    # this exact tuple with built_to_fail -- combined with an identical
    # dimensional_vector, a guaranteed exact-tie score for any session
    # vector (confirmed: 175/175 calibration profiles tied before this
    # change). built_to_fail's own read stays unchanged (approved as-is,
    # aptitude-dominant, clean). the_paper_tiger differentiated per the
    # real descriptive_prose: aptitude reduced (not a skill/resourcing
    # story), authority raised (structural gap -- no one held
    # responsible for keeping documentation current, precedent for this
    # exact magnitude class in the_suppression_filter's own Authority
    # secondary), attitude raised (operational avoidance behavior --
    # managed verbally, record doesn't match reality). alliance
    # untouched -- no textual basis to move it. dimensional_vector
    # deliberately untouched -- salience-only, by design.
    #
    # Magnitude: 4 candidates searched against the real calibration
    # pipeline (tools/_salience_pilot_search_rank8.py), all passed
    # identically clean -- landed on the best worst-case gap floor
    # (min gap 0.0195 across all 175 profiles) among candidates tested.
    #
    # SIGNIFICANT FINDING, not fixed by this change: built_to_fail wins
    # a false rank-1 in 49/175 calibration profiles (28%) -- confirmed
    # structurally incapable of improving via this differentiation at
    # ANY tested magnitude, because built_to_fail and the_paper_tiger
    # share an identical dimensional_vector and built_to_fail's own
    # aptitude weight stays fixed at 2.5 (its only real vector signal).
    # Only 4 of the 49 are the_paper_tiger's own profiles; the other 45
    # are unrelated states entirely -- a taxonomy-wide dominance
    # pattern, not a tie artifact. See
    # prompts/scd-wcs-cluster-map-findings.md for the full writeup.
    # Phase 5 (2026-08-25) -- dual-elevated, matched to the new vector
    # (Authority primary, Attitude secondary). Supersedes the prior
    # shape, which compensated for the old, wrong Aptitude-primary
    # vector inherited from built_to_fail -- that compensation no
    # longer applies now that the vector itself is corrected.
    "the_paper_tiger": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.0, "attitude_asset": 2.0,
    },

    # ── APTITUDE — MEDIUM tier (primary only) ─────────────────────────────────
    "the_undefined_role": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── APTITUDE — LOW/CLUSTER (primary=Aptitude, secondary=Attitude) ─────────
    # SCD-WCS remediation pilot (2026-08-20, revised magnitude --
    # second pass): the_unformed_leader and the_dormant_talent
    # previously shared this exact tuple (Tier 2 v18 comment above,
    # kept for history, superseded by this revision) -- combined with
    # an identical dimensional_vector, this produced a guaranteed
    # exact-tie score for any session vector (confirmed: 175/175
    # calibration profiles tied before this change). Differentiated
    # per the real descriptive_prose (engine/data/states.py), not the
    # TS-facing description copy: the_unformed_leader is a capability
    # gap ("without having been equipped for it") -- aptitude stays
    # dominant, unchanged. the_dormant_talent is retained capability
    # plus a willingness failure ("can name precisely... consistently
    # doesn't act on it"). A larger swing (aptitude 1.5, attitude 2.0,
    # making attitude fully dominant) broke the tie but regressed
    # APT-DT-02 below its moderate-tier prominence threshold --
    # searched smaller deltas against the real calibration pipeline
    # (tools/_salience_pilot_search.py) rather than re-tuning by hand.
    # Every candidate preserving full attitude dominance failed
    # APT-DT-02 (its session vector carries strong aptitude signal);
    # every candidate keeping aptitude dominant passed with real
    # margin. Landed on aptitude=2.0/attitude=1.3 -- best margin
    # (+0.064) and best worst-case gap floor (0.000633) among
    # candidates tested. Aptitude remains the larger weight on both
    # states -- this does NOT make attitude dominant for
    # the_dormant_talent, a real deviation from the original
    # narrative-driven direction, flagged not silently adapted around.
    # authority/alliance untouched on both -- the text gives no basis
    # to move them. dimensional_vector deliberately untouched this
    # pilot -- salience-only, by design.
    "the_unformed_leader": {  # Tier 2 v18: attitude secondary 2.5->1.0
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.6, "attitude_asset": 0.6,
    },
    "the_dormant_talent": {  # Tier 2 v18: attitude secondary 2.5->1.0
        "aptitude_liability": 2.0, "aptitude_asset": 2.0,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 1.3, "attitude_asset": 1.3,
    },

    # ── APTITUDE — LOW/CLUSTER (primary=Aptitude, secondary=Authority) ────────
    "the_overloaded_manager": {  # Tier 2 v18: authority secondary 2.5->1.0
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 1.0, "authority_asset": 1.0,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── AUTHORITY — HIGH tier (primary only) ──────────────────────────────────
    "the_founders_grip": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_exposed": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "hr_capture": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "heard_and_ignored": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_tolerated_violation": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    # SCD-WCS re-clustering (this session, Program Phase 4):
    # the_unsolved_problem moved from the rank-3 Authority-dominant
    # template to a standard flat-aptitude-primary template,
    # matching invisible_performance_management's own entry. Vector-
    # only change was sufficient -- confirmed by the search holding
    # this exact salience constant across all 9 tested vector
    # candidates. See prompts/scd-wcs-remediation-tracker.md for
    # full detail.
    "the_unsolved_problem": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── AUTHORITY — MEDIUM tier (primary only) ────────────────────────────────
    "the_uninitiated": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "leadership_continuity_risk": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "decision_paralysis": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_policy_lag": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "dueling_narratives": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "transition_paralysis": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_lost_map": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "pay_exposure": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "the_pay_fog": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── AUTHORITY — LOW/CLUSTER (primary=Authority, secondary=Aptitude) ───────
    "the_unexamined_algorithm": {  # Tier 2 v18: aptitude secondary 2.5->1.0
        "aptitude_liability": 1.0, "aptitude_asset": 1.0,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── AUTHORITY — LOW/CLUSTER (primary=Authority, secondary=Alliance) ───────
    # SCD-WCS re-clustering (this session): paper_shield moved from
    # the rank-5 Authority-dominant template (Tier 2 v18 comment, kept
    # for history) to a standard flat-aptitude-primary template,
    # matching invisible_performance_management's own entry ("medium
    # tier, primary only"). Vector-only change was sufficient --
    # confirmed by the search holding this exact salience constant
    # across all 12 tested vector candidates. See
    # prompts/scd-wcs-remediation-tracker.md for full detail.
    # SCD-WCS Phase 8 mitigation: previously the bare standard
    # template (aptitude=2.5/2.5, else flat 0.4/0.4), which
    # manufactured a 9/175 false-rank-1 footprint that measured
    # 0/175 before this session's Aptitude re-clustering (see
    # prompts/scd-wcs-remediation-tracker.md). Attitude secondary
    # raised per the real text -- "the organization believes it
    # is prepared because the documentation says so" -- a real
    # false-confidence/complacency mechanism, never tested in the
    # original re-clustering search. Aptitude (2.5/2.5) unchanged,
    # still dominant, dimensional_vector untouched. Margin-searched
    # (0.7-2.0, full 175-profile suite): false-rank-1 reaches
    # 0/175 at every tested magnitude; landed on 2.0, the best
    # available margin in the tested range (0.0100 vs. 0.7's
    # razor-thin 0.0034), zero regression cost, zero collision.
    # Still loses all 3 of its own dedicated profiles to
    # built_to_fail -- separate, already-known Track 2 problem,
    # unaffected by and not solved by this fix.
    "paper_shield": {
        "aptitude_liability": 2.5, "aptitude_asset": 2.5,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.0, "attitude_asset": 2.0,
    },
    # SCD-WCS remediation pilot (rank-5 cluster): previously shared
    # this exact tuple with paper_shield and planning_authority_gap
    # (Tier 2 v18 comment above, kept for history) -- combined with an
    # identical dimensional_vector, all three states tied exactly on
    # every calibration profile (confirmed 175/175 via
    # tools/_salience_pilot_search_rank5.py before this change).
    # Differentiated per the real descriptive_prose
    # (engine/data/states.py): informal, relationship-based influence
    # ("channels that don't match the org chart... who actually has
    # to say yes") is the substance of the narrative -- alliance
    # secondary raised. Authority stays dominant, unchanged --
    # confirmed Authority-correct against the real text. paper_shield
    # deliberately left untouched -- flagged possible mis-clustering,
    # a separate open question, not a same-cluster question.
    # dimensional_vector untouched -- salience-only, by design.
    "invisible_influence_architecture": {  # Tier 2 v18: alliance secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 1.8, "alliance_asset": 1.8,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── ALLIANCE — HIGH tier (primary only) ───────────────────────────────────
    "the_fracture": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "decision_blindness": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── ALLIANCE — MEDIUM tier (primary only) ─────────────────────────────────
    # Phase 5 (2026-08-25) -- Aptitude secondary elevated to match the
    # new vector's real (non-floor) Aptitude value. Alliance unchanged,
    # still dominant.
    "the_second_close": {
        "aptitude_liability": 2.0, "aptitude_asset": 2.0,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    # SCD-WCS remediation pilot (rank-6 cluster, silosolation-only
    # partial fix): previously shared this exact tuple with
    # the_second_close and the_arbitrary_standard -- all three tied
    # exactly on every calibration profile (confirmed 175/175 via
    # tools/_scdwcs_decomposition_rank6.py and
    # tools/_salience_pilot_search_rank6.py before this change).
    # Differentiated per the real descriptive_prose
    # (engine/data/states.py): cross-team structural/decision-
    # visibility gap ("not hostile... structural") -- Authority
    # secondary raised. Alliance (2.5/2.5) unchanged, still
    # dominant -- confirmed Alliance-correct against the real text.
    # HONEST PARTIAL FIX, not a full fix: breaks the exact
    # mathematical tie against both the_second_close and
    # the_arbitrary_standard (0/175 tied on both pairings, verified),
    # but does NOT make silosolation win its own dedicated profiles
    # outright -- the_second_close (left untouched) still outranks
    # it there, confirmed unmovable even at extreme magnitude (tested
    # to 12.0). Vector-shape ceiling: silosolation's authored
    # authority_liability/authority_asset are only 0.15 each
    # (dimensional_vector deliberately untouched, salience-only by
    # design), too small for a salience weight alone to efficiently
    # overcome the_second_close's larger, untouched Alliance anchor.
    # Accepted as-is, same category as built_to_fail's residual after
    # rank-8. the_second_close and the_arbitrary_standard
    # deliberately left untouched -- the_arbitrary_standard's
    # originally-proposed Attitude secondary failed scrutiny (not
    # text-grounded, and mechanically counterproductive -- see
    # prompts/scd-wcs-remediation-tracker.md), no replacement axis
    # identified yet.
    "silosolation": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.0, "authority_asset": 2.0,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    # SCD-WCS remediation pilot (Phase 7, leftover from rank-6):
    # previously shared this exact tuple with the_second_close --
    # tied exactly on every calibration profile (confirmed 175/175,
    # rank-6). Differentiated per the real descriptive_prose
    # (engine/data/states.py): rule-application/documentation
    # language runs through all three dedicated profiles ("documented
    # criteria", "documentation" x2, "rules apply differently") --
    # Authority secondary raised. Alliance (2.5/2.5) unchanged, still
    # dominant. dimensional_vector UNCHANGED -- salience-only
    # confirmed sufficient (tools/_scdwcs_phase7_arbitrary_standard.py).
    # Magnitude 2.0 landed via proper margin search across 1.0-3.0
    # (tools/_salience_pilot_search_arbitrary_standard.py): smallest
    # candidate clearing the thin-margin zone on ALL-AS-02/03
    # (+0.0115, vs. a razor-thin +0.0039 at 1.0), matches
    # silosolation's own shipped score exactly on ALL-AS-01
    # (0.710304). Zero regression, zero reverse-direction ripple onto
    # the_second_close's own profiles, at every magnitude tested.
    # Phase 5 (2026-08-25) -- weights flip to match the vector's own
    # axis flip (Authority now primary, Alliance now secondary).
    "the_arbitrary_standard": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 2.0, "alliance_asset": 2.0,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── ALLIANCE — LOW/CLUSTER (primary=Alliance, secondary=Authority) ────────
    "the_suppression_filter": {  # v23: revert to Three-Tier -- alliance primary 2.5, authority secondary 1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 1.0, "authority_asset": 1.0,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },

    # ── ATTITUDE — HIGH tier (primary only) ───────────────────────────────────
    "the_untouchable": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },

    # ── ATTITUDE — MEDIUM tier (primary only) ─────────────────────────────────
    "the_diversity_ceiling": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_burned_credibility": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "invisible_burnout": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_basement_standard": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_inside_track": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "groundhog_day": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_wrong_reward": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_broken_compass": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },

    # ── ATTITUDE — LOW/CLUSTER (primary=Attitude, secondary=Alliance) ─────────
    "narrative_lock": {  # Tier 2 v18: alliance secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 1.0, "alliance_asset": 1.0,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "what_nobody_says": {  # Tier 2 v18: primary=Alliance(2.5), attitude secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 1.0, "attitude_asset": 1.0,
    },
    "leadership_deafness": {  # v23: revert to Three-Tier -- attitude primary 2.5, authority secondary 1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 1.0, "authority_asset": 1.0,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "identity_erosion": {  # Tier 2 v18: alliance secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 1.0, "alliance_asset": 1.0,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_culture_that_wasnt": {  # Tier 2 v18: alliance secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 1.0, "alliance_asset": 1.0,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_unreported_hazard": {  # Tier 2 v18: alliance secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 1.0, "alliance_asset": 1.0,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "the_unlocked_door": {  # Tier 2 v18: alliance secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 1.0, "alliance_asset": 1.0,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },

    # ── ATTITUDE — LOW/CLUSTER (primary=Attitude, secondary=Authority) ────────
    "culture_drift": {  # Tier 2 v18: authority secondary 2.5->1.0; v19 revert: attitude primary 1.85->2.5
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 1.0, "authority_asset": 1.0,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },

    # ── TAXONOMY EXPANSION (Session 67) — DRAFT, pending Gemini review ──────────
    # Seeded per the three-tier rule above from each state's draft signal_weight in
    # engine/data/states.py; secondary bumps mirror that state's dimensional_vector
    # secondary-field elevation.
    # Phase 5 (2026-08-25) -- standard flat template, moved to the new
    # vector's own axis (Authority). See engine/data/states.py.
    "invisible_performance_management": {
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "compression_crisis": {  # medium tier, primary only
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "sequential_decision_blindness": {  # high tier, primary only
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "disparate_impact_architecture": {  # high tier, primary only
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    # SCD-WCS remediation pilot (rank-5 cluster): previously shared
    # this exact tuple with paper_shield and
    # invisible_influence_architecture (Tier 2 v18 comment above, kept
    # for history) -- see invisible_influence_architecture's comment
    # above for the full tie finding. Differentiated per the real
    # descriptive_prose (engine/data/states.py): a pure structural/
    # procedural authority-execution gap ("plans get built and then
    # wait for approval from someone who wasn't part of building
    # them") -- zero relational content in the text, alliance
    # secondary lowered. Authority stays dominant, unchanged --
    # confirmed Authority-correct against the real text.
    # dimensional_vector untouched -- salience-only, by design.
    "planning_authority_gap": {  # low tier, alliance secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 2.5, "authority_asset": 2.5,
        "alliance_liability": 0.5, "alliance_asset": 0.5,
        "attitude_liability": 0.4, "attitude_asset": 0.4,
    },
    "distributed_culture_fragmentation": {  # medium tier, attitude secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 2.5, "alliance_asset": 2.5,
        "attitude_liability": 1.0, "attitude_asset": 1.0,
    },
    "wellbeing_theater": {  # cluster tier (C-Culture), authority secondary 2.5->1.0
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 1.0, "authority_asset": 1.0,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "human_displacement_anxiety": {  # medium tier, primary only
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "motivational_architecture_failure": {  # medium tier, primary only
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
    "cultural_overtime": {  # medium tier, primary only
        "aptitude_liability": 0.4, "aptitude_asset": 0.4,
        "authority_liability": 0.4, "authority_asset": 0.4,
        "alliance_liability": 0.4, "alliance_asset": 0.4,
        "attitude_liability": 2.5, "attitude_asset": 2.5,
    },
}
