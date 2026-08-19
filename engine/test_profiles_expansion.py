"""
PRV3 Scoring Engine — Phase 1 Test Profiles
Taxonomy Expansion (Session 67) — 30 profiles across the 10 new states.

DRAFT — pending Gemini review, same status as the classification fields these
profiles are built against (engine/data/states.py signal_weight/severity_range/
dimensional_vector for these 10 states). See
prompts/gemini-handoff-taxonomy-expansion-57.md.

Authored at the same rigor and narrative convention as the original Phase 1/2
batches (engine/test_profiles*.py): one high_confidence + one moderate + one
weak profile per state. No extreme_high_confidence profiles — none of these
10 states carry a Fixed severity tier.

answers: empty at this stage — populated by calibration_runner.py's
signal-driven generate_answers(), same as every other Phase 1 profile.
intake: representative values derived from each state's profile description
and research/seven-experiments/consolidation-mapping-trace.md disposition notes.
"""

from engine.test_suite import TestCase, ExpectedOutput


# -- Authority: Compression Crisis ---------------------------------------------

EXP_CC_01 = TestCase(
    test_id="EXP-CC-01",
    description=(
        "300-person tech company in a pay-transparency state. Recruiting posted "
        "salary bands that meet or exceed what several 3+ year employees currently "
        "earn in the same roles. Three resignations in the past quarter cited pay "
        "discovery specifically. Principal has not adjusted existing pay."
    ),
    profile_type="high_confidence",
    target_state="compression_crisis",
    intake={
        "headcount":          328,
        "industry":           "Technology",
        "org_type":           "PE or VC-backed",
        "jurisdictions":      ["CA"],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["compression_crisis"],
        severity_tier="Entrenched",
    ),
)

EXP_CC_02 = TestCase(
    test_id="EXP-CC-02",
    description=(
        "120-person healthcare services firm. HR has noticed new-hire offers "
        "trending close to tenured pay in a couple of roles but hasn't run a "
        "full comparison. One exit interview mentioned pay as a factor among others."
    ),
    profile_type="moderate",
    target_state="compression_crisis",
    intake={
        "headcount":          152,
        "industry":           "Healthcare & Life Sciences",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      ["CA"],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["compression_crisis", "the_pay_fog"],
        severity_tier="Emerging",
    ),
)

EXP_CC_03 = TestCase(
    test_id="EXP-CC-03",
    description=(
        "60-person retail chain. Principal mentions new hires cost more than they "
        "used to but hasn't compared it to existing staff pay. No departures "
        "attributed to compensation yet."
    ),
    profile_type="weak",
    target_state="compression_crisis",
    intake={
        "headcount":          45,
        "industry":           "Retail & Hospitality",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["compression_crisis", "pay_exposure", "the_pay_fog"],
        severity_tier="Emerging",
    ),
)


# -- Authority: Sequential Decision Blindness -----------------------------------

EXP_SDB_01 = TestCase(
    test_id="EXP-SDB-01",
    description=(
        "400-person financial services firm. Employee filed an internal complaint "
        "about a manager. Two months later a different manager passed them over "
        "for promotion, unaware of the complaint. A subsequent RIF selection "
        "process, run by a third manager who had never heard of either event, "
        "included the same employee. No single decision-maker coordinated with "
        "another, and outside counsel has flagged the sequence as a retaliation "
        "exposure regardless of intent."
    ),
    profile_type="high_confidence",
    target_state="sequential_decision_blindness",
    intake={
        "headcount":          328,
        "industry":           "Financial Services",
        "org_type":           "Publicly traded",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim", "restructuring_or_layoff"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["sequential_decision_blindness"],
        severity_tier="Emerging",
    ),
)

EXP_SDB_02 = TestCase(
    test_id="EXP-SDB-02",
    description=(
        "150-person logistics company. A complaint was filed, and the employee "
        "later missed a promotion and had a rating dip, each decided by a "
        "different manager with no apparent knowledge of the complaint. No legal "
        "claim filed yet, but HR has noticed the pattern internally."
    ),
    profile_type="moderate",
    target_state="sequential_decision_blindness",
    intake={
        "headcount":          152,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["sequential_decision_blindness", "decision_blindness"],
        severity_tier="Emerging",
    ),
)

EXP_SDB_03 = TestCase(
    test_id="EXP-SDB-03",
    description=(
        "50-person nonprofit. An employee who raised a concern months ago has "
        "since had a couple of unrelated-seeming setbacks in scheduling and "
        "assignments. No complaint has been made about it and no one has "
        "connected the events yet."
    ),
    profile_type="weak",
    target_state="sequential_decision_blindness",
    intake={
        "headcount":          45,
        "industry":           "Nonprofit & Education",
        "org_type":           "Nonprofit",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Other",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["sequential_decision_blindness", "decision_blindness", "the_arbitrary_standard"],
        severity_tier="Emerging",
    ),
)


# -- Authority: Disparate Impact Architecture -----------------------------------

EXP_DIA_01 = TestCase(
    test_id="EXP-DIA-01",
    description=(
        "800-person manufacturing company. Promotion criteria and a RIF selection "
        "matrix were both built years ago around tenure and shift-availability "
        "factors, never reviewed for disparate impact. A demographic analysis run "
        "by outside counsel after an EEOC inquiry shows a statistically "
        "significant skew in outcomes with no individual decision-maker intending it."
    ),
    profile_type="high_confidence",
    target_state="disparate_impact_architecture",
    intake={
        "headcount":          692,
        "industry":           "Manufacturing & Industrial",
        "org_type":           "Publicly traded",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["disparate_impact_architecture"],
        severity_tier="Entrenched",
    ),
)

EXP_DIA_02 = TestCase(
    test_id="EXP-DIA-02",
    description=(
        "300-person insurance company. HR has noticed promotion rates differ "
        "meaningfully by demographic group but hasn't formally analyzed why, and "
        "no one has reviewed whether the criteria themselves are the cause."
    ),
    profile_type="moderate",
    target_state="disparate_impact_architecture",
    intake={
        "headcount":          328,
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["disparate_impact_architecture", "the_diversity_ceiling"],
        severity_tier="Entrenched",
    ),
)

EXP_DIA_03 = TestCase(
    test_id="EXP-DIA-03",
    description=(
        "90-person professional services firm. Someone mentioned the performance "
        "rating criteria have never been reviewed for fairness across groups. No "
        "data has been pulled and no pattern is confirmed."
    ),
    profile_type="weak",
    target_state="disparate_impact_architecture",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Other",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["disparate_impact_architecture", "the_arbitrary_standard"],
        severity_tier="Entrenched",
    ),
)


# -- Authority: Planning Authority Gap -------------------------------------------

EXP_PAG_01 = TestCase(
    test_id="EXP-PAG-01",
    description=(
        "600-person retail company. HR built a full strategic workforce plan "
        "with headcount, succession, and skills-gap modeling a year ago. "
        "Leadership decisions on hiring, restructuring, and location strategy "
        "have all been made since without referencing it. HR's standing to "
        "have the analysis acted on has never been established."
    ),
    profile_type="high_confidence",
    target_state="planning_authority_gap",
    intake={
        "headcount":          692,
        "industry":           "Retail & Hospitality",
        "org_type":           "Publicly traded",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["planning_authority_gap"],
        severity_tier="Emerging",
    ),
)

EXP_PAG_02 = TestCase(
    test_id="EXP-PAG-02",
    description=(
        "200-person technology company. HR has workforce data and has raised it "
        "in a couple of planning meetings, with mixed uptake — sometimes it "
        "informs decisions, sometimes it's set aside."
    ),
    profile_type="moderate",
    target_state="planning_authority_gap",
    intake={
        "headcount":          152,
        "industry":           "Technology",
        "org_type":           "PE or VC-backed",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["planning_authority_gap", "invisible_influence_architecture"],
        severity_tier="Emerging",
    ),
)

EXP_PAG_03 = TestCase(
    test_id="EXP-PAG-03",
    description=(
        "70-person nonprofit. HR mentions having some workforce data but isn't "
        "sure leadership finds it useful. No specific decision has been "
        "identified where the analysis was overridden."
    ),
    profile_type="weak",
    target_state="planning_authority_gap",
    intake={
        "headcount":          45,
        "industry":           "Nonprofit & Education",
        "org_type":           "Nonprofit",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["planning_authority_gap", "the_lost_map"],
        severity_tier="Emerging",
    ),
)


# -- Attitude: Wellbeing Theater --------------------------------------------------

EXP_WT_01 = TestCase(
    test_id="EXP-WT-01",
    description=(
        "350-person consulting firm. Leadership rolled out a mental health app "
        "subscription and a wellness stipend last year. Chronic understaffing "
        "and manager overload — the conditions employees say actually cause "
        "their stress — are unchanged. Survey comments describe the programs "
        "as beside the point."
    ),
    profile_type="high_confidence",
    target_state="wellbeing_theater",
    intake={
        "headcount":          328,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["wellbeing_theater"],
        severity_tier="Entrenched",
    ),
)

EXP_WT_02 = TestCase(
    test_id="EXP-WT-02",
    description=(
        "140-person healthcare organization. A wellness program launched "
        "recently; some employees find it useful, others say it doesn't touch "
        "the real workload problem. Culture Drift more broadly is also visible."
    ),
    profile_type="moderate",
    target_state="wellbeing_theater",
    intake={
        "headcount":          152,
        "industry":           "Healthcare & Life Sciences",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["wellbeing_theater", "culture_drift"],
        severity_tier="Emerging",
    ),
)

EXP_WT_03 = TestCase(
    test_id="EXP-WT-03",
    description=(
        "45-person marketing agency. Leadership mentioned adding a wellness "
        "benefit next quarter. No program exists yet and no employee feedback "
        "has been gathered."
    ),
    profile_type="weak",
    target_state="wellbeing_theater",
    intake={
        "headcount":          45,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["wellbeing_theater", "invisible_burnout"],
        severity_tier="Emerging",
    ),
)


# -- Attitude: Human Displacement Anxiety -----------------------------------------

EXP_HDA_01 = TestCase(
    test_id="EXP-HDA-01",
    description=(
        "280-person software company. AI tools were rolled into daily workflows "
        "quickly with no communication about what it means for roles. Several "
        "of the strongest engineers — the ones best positioned to work well "
        "alongside the new tools — have left citing uncertainty about where "
        "they fit."
    ),
    profile_type="high_confidence",
    target_state="human_displacement_anxiety",
    intake={
        "headcount":          328,
        "industry":           "Technology",
        "org_type":           "PE or VC-backed",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["human_displacement_anxiety"],
        severity_tier="Emerging",
    ),
)

EXP_HDA_02 = TestCase(
    test_id="EXP-HDA-02",
    description=(
        "130-person insurance company. AI tools were introduced in a couple of "
        "departments. Some staff have asked what it means for their jobs; no "
        "departures yet, but engagement in the affected teams has softened."
    ),
    profile_type="moderate",
    target_state="human_displacement_anxiety",
    intake={
        "headcount":          152,
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["human_displacement_anxiety", "invisible_burnout"],
        severity_tier="Emerging",
    ),
)

EXP_HDA_03 = TestCase(
    test_id="EXP-HDA-03",
    description=(
        "40-person design studio. Leadership is evaluating AI tools but hasn't "
        "deployed anything yet. A couple of informal comments about job "
        "security have come up in passing."
    ),
    profile_type="weak",
    target_state="human_displacement_anxiety",
    intake={
        "headcount":          45,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["human_displacement_anxiety", "the_unexamined_algorithm"],
        severity_tier="Emerging",
    ),
)


# -- Attitude: Motivational Architecture Failure ----------------------------------

EXP_MAF_01 = TestCase(
    test_id="EXP-MAF-01",
    description=(
        "500-person call center operation. Performance management is built "
        "entirely around metrics and corrective action for missing them. Most "
        "of the floor staff describe their goal as simply avoiding a write-up, "
        "not doing good work. Turnover and quiet quitting are both elevated and "
        "the pattern has held for over a year despite manager changes."
    ),
    profile_type="high_confidence",
    target_state="motivational_architecture_failure",
    intake={
        "headcount":          328,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "VP or senior director",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["motivational_architecture_failure"],
        severity_tier="Entrenched",
    ),
)

EXP_MAF_02 = TestCase(
    test_id="EXP-MAF-02",
    description=(
        "160-person logistics company. Recognition and reward are inconsistent; "
        "some teams seem to be optimizing for what actually gets rewarded, "
        "others seem to have disengaged from the reward system altogether."
    ),
    profile_type="moderate",
    target_state="motivational_architecture_failure",
    intake={
        "headcount":          152,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["motivational_architecture_failure", "the_wrong_reward"],
        severity_tier="Entrenched",
    ),
)

EXP_MAF_03 = TestCase(
    test_id="EXP-MAF-03",
    description=(
        "55-person agency. A couple of employees have mentioned feeling like "
        "effort doesn't matter much here, but most of the team still seems "
        "engaged."
    ),
    profile_type="weak",
    target_state="motivational_architecture_failure",
    intake={
        "headcount":          45,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["motivational_architecture_failure", "invisible_burnout"],
        severity_tier="Entrenched",
    ),
)


# -- Attitude: Cultural Overtime ---------------------------------------------------

EXP_CO_01 = TestCase(
    test_id="EXP-CO-01",
    description=(
        "220-person marketing agency. Written policy prohibits off-clock work "
        "for nonexempt staff. In practice, managers expect same-evening replies "
        "to messages and set deadlines that require it. Nobody has been "
        "instructed to work off the clock, and nearly everyone does."
    ),
    profile_type="high_confidence",
    target_state="cultural_overtime",
    intake={
        "headcount":          152,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      ["CA"],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["cultural_overtime"],
        severity_tier="Entrenched",
    ),
)

EXP_CO_02 = TestCase(
    test_id="EXP-CO-02",
    description=(
        "90-person restaurant group corporate office. Some managers expect "
        "after-hours responsiveness, others don't. A couple of nonexempt staff "
        "have mentioned answering messages at home."
    ),
    profile_type="moderate",
    target_state="cultural_overtime",
    intake={
        "headcount":          45,
        "industry":           "Retail & Hospitality",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["cultural_overtime", "the_tolerated_violation"],
        severity_tier="Emerging",
    ),
)

EXP_CO_03 = TestCase(
    test_id="EXP-CO-03",
    description=(
        "30-person boutique firm. One employee mentioned checking email at "
        "night occasionally. No pattern of expectation has been described."
    ),
    profile_type="weak",
    target_state="cultural_overtime",
    intake={
        "headcount":          45,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["cultural_overtime", "invisible_burnout"],
        severity_tier="Emerging",
    ),
)


# -- Aptitude: Invisible Performance Management -----------------------------------

EXP_IPM_01 = TestCase(
    test_id="EXP-IPM-01",
    description=(
        "180-person engineering firm. A manager has managed one employee's "
        "underperformance entirely through hallway conversations for over a "
        "year — the judgment is accurate, coworkers agree with it, but nothing "
        "is written down. HR attempted a termination and legal flagged the file "
        "as indefensible purely on documentation grounds."
    ),
    profile_type="high_confidence",
    target_state="invisible_performance_management",
    intake={
        "headcount":          152,
        "industry":           "Technology",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["external_legal_claim"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["invisible_performance_management"],
        severity_tier="Emerging",
    ),
)

EXP_IPM_02 = TestCase(
    test_id="EXP-IPM-02",
    description=(
        "110-person healthcare practice. A manager gives verbal feedback "
        "regularly and it seems to land, but formal write-ups are rare. No "
        "termination attempt has surfaced the gap yet."
    ),
    profile_type="moderate",
    target_state="invisible_performance_management",
    intake={
        "headcount":          152,
        "industry":           "Healthcare & Life Sciences",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["invisible_performance_management", "the_paper_tiger"],
        severity_tier="Emerging",
    ),
)

EXP_IPM_03 = TestCase(
    test_id="EXP-IPM-03",
    description=(
        "35-person studio. One manager mentions preferring verbal feedback "
        "over written reviews. No performance issue has come up that tested it."
    ),
    profile_type="weak",
    target_state="invisible_performance_management",
    intake={
        "headcount":          45,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["invisible_performance_management", "the_undefined_role"],
        severity_tier="Emerging",
    ),
)


# -- Alliance: Distributed Culture Fragmentation ----------------------------------

EXP_DCF_01 = TestCase(
    test_id="EXP-DCF-01",
    description=(
        "260-person software company, half remote and half in-office. The two "
        "groups describe fundamentally different experiences — different "
        "access to leadership, different promotion patterns, different senses "
        "of what the culture actually is. Employees openly refer to it as two "
        "companies sharing a name."
    ),
    profile_type="high_confidence",
    target_state="distributed_culture_fragmentation",
    intake={
        "headcount":          328,
        "industry":           "Technology",
        "org_type":           "PE or VC-backed",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["distributed_culture_fragmentation"],
        severity_tier="Emerging",
    ),
)

EXP_DCF_02 = TestCase(
    test_id="EXP-DCF-02",
    description=(
        "130-person professional services firm split across two office "
        "locations plus remote staff. Some divergence in how each group "
        "experiences leadership access, but not yet a fully separate culture."
    ),
    profile_type="moderate",
    target_state="distributed_culture_fragmentation",
    intake={
        "headcount":          152,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["distributed_culture_fragmentation", "silosolation"],
        severity_tier="Emerging",
    ),
)

EXP_DCF_03 = TestCase(
    test_id="EXP-DCF-03",
    description=(
        "45-person agency that recently allowed some remote work. Too early to "
        "tell whether a location-based divide is forming."
    ),
    profile_type="weak",
    target_state="distributed_culture_fragmentation",
    intake={
        "headcount":          45,
        "industry":           "Other",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="multi_state",
        identified_states=["distributed_culture_fragmentation", "culture_drift"],
        severity_tier="Emerging",
    ),
)


# -- Attitude: The Inner Circle (MC_CENTROID_39 follow-up, this session) --------

EXP_IC_01 = TestCase(
    test_id="EXP-IC-01",
    description=(
        "400-person financial services firm. A small group of senior leaders "
        "has covered for each other's costly mistakes for years -- one "
        "director's failed initiative was quietly absorbed, another's "
        "compliance shortcut was never escalated. Decisions on budget and "
        "promotion are made among this same small group regardless of who "
        "is closest to the issue. Staff outside the group have stopped "
        "expecting to be included."
    ),
    profile_type="high_confidence",
    target_state="the_inner_circle",
    intake={
        "headcount":          412,
        "industry":           "Financial Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "C-suite",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_inner_circle"],
        severity_tier="Emerging",
    ),
)

EXP_IC_02 = TestCase(
    test_id="EXP-IC-02",
    description=(
        "180-person healthcare organization. A senior leadership group has "
        "started to notice their own mistakes get less scrutiny than "
        "others', and there's some sense that decisions cluster among a "
        "familiar few. Not yet a fixed pattern across every major call."
    ),
    profile_type="moderate",
    target_state="the_inner_circle",
    intake={
        "headcount":          184,
        "industry":           "Healthcare",
        "org_type":           "Nonprofit",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "HR leader",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_inner_circle"],
        severity_tier="Emerging",
    ),
)

EXP_IC_03 = TestCase(
    test_id="EXP-IC-03",
    description=(
        "55-person professional services firm. One senior leader mentioned "
        "offhand that a peer's error was handled quietly. No pattern "
        "confirmed, no sense that decisions are concentrated among a "
        "specific group."
    ),
    profile_type="weak",
    target_state="the_inner_circle",
    intake={
        "headcount":          55,
        "industry":           "Professional Services",
        "org_type":           "Privately held professional leadership",
        "jurisdictions":      [],
        "significant_events": ["none"],
        "principal_role":     "Owner or founder",
    },
    answers=[],
    expected=ExpectedOutput(
        output_type="single_state",
        identified_states=["the_inner_circle"],
        severity_tier="Emerging",
    ),
)


EXPANSION_PROFILES = [
    EXP_CC_01, EXP_CC_02, EXP_CC_03,
    EXP_SDB_01, EXP_SDB_02, EXP_SDB_03,
    EXP_DIA_01, EXP_DIA_02, EXP_DIA_03,
    EXP_PAG_01, EXP_PAG_02, EXP_PAG_03,
    EXP_WT_01, EXP_WT_02, EXP_WT_03,
    EXP_HDA_01, EXP_HDA_02, EXP_HDA_03,
    EXP_MAF_01, EXP_MAF_02, EXP_MAF_03,
    EXP_CO_01, EXP_CO_02, EXP_CO_03,
    EXP_IPM_01, EXP_IPM_02, EXP_IPM_03,
    EXP_DCF_01, EXP_DCF_02, EXP_DCF_03,
    EXP_IC_01, EXP_IC_02, EXP_IC_03,
]
