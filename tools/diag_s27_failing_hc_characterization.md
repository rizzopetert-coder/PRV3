========================================================================
PRV3 Session 27 — 9 Failing HC Profiles Diagnostic
Engine: v23 | Cluster window: Delta=0.2
========================================================================

## SECTION 1: state_targets coverage — all 47 HC states
State                                          Qs     HC status  Question IDs
------------------------------------------------------------------------------------------
built_to_fail                                   8       passing  Q03A, Q03A-D-FOLLOW, Q20, Q35, Q36, Q39, SEVER-02, VERIFY-Q20
culture_drift                                   4       passing  Q11, Q27B, SEVER-10, VERIFY-Q27B
decision_blindness                              3       passing  Q06, Q31, VERIFY-Q31
decision_paralysis                              8       passing  Q01, Q13, Q20, Q21, SEVER-02, SEVER-03, VERIFY-Q20, VERIFY-Q21
dueling_narratives                              1       FAILING  Q19
groundhog_day                                   3       passing  Q17, Q32, VERIFY-Q32
heard_and_ignored                               2       passing  Q04, Q06
hr_capture                                      2       FAILING  Q02, Q04
identity_erosion                                4       passing  Q03A-D-FOLLOW, Q27B, SEVER-10, VERIFY-Q27B
invisible_burnout                               3       passing  Q24, SEVER-06, VERIFY-Q24
invisible_influence_architecture                1       passing  Q33
leadership_continuity_risk                      8       FAILING  Q03A-D-FOLLOW, Q23, Q25, Q33, Q38, SEVER-05, SEVER-07, VERIFY-Q25
leadership_deafness                             3       passing  Q04, Q08, Q12
narrative_lock                                  5       passing  Q17, Q32, Q34, SEVER-13, VERIFY-Q32
paper_shield                                    4       FAILING  Q10, Q23, Q33, SEVER-05
pay_exposure                                    1       passing  Q14
silosolation                                    6       passing  Q03A-D-FOLLOW, Q07, Q09, Q26, SEVER-08, VERIFY-Q26
the_arbitrary_standard                          3       passing  Q05, Q11, Q15
the_basement_standard                           2       passing  Q05, Q11
the_broken_compass                              7       passing  Q11, Q13, Q17, Q32, Q34, SEVER-13, VERIFY-Q32
the_burned_credibility                          4       passing  Q03A, Q13, Q17, Q34
the_culture_that_wasnt                          3       passing  Q27B, SEVER-10, VERIFY-Q27B
the_diversity_ceiling                           6       passing  Q15, Q16, Q29, SEVER-01, SEVER-12, VERIFY-Q16
the_dormant_talent                              5       passing  Q12, Q15, Q25, SEVER-07, VERIFY-Q25
the_exposed                                     1       passing  Q02
the_founders_grip                               2       passing  Q01, Q03A-D-FOLLOW
the_fracture                                    6       passing  Q03A-D-FOLLOW, Q07, Q09, Q26, SEVER-08, VERIFY-Q26
the_inside_track                                3       passing  Q05, Q11, Q15
the_lost_map                                    5       passing  Q01, Q13, Q21, Q30, VERIFY-Q21
the_overloaded_manager                          3       passing  Q12, Q35, Q38
the_paper_tiger                                 6       passing  Q05, Q06, Q10, Q12, Q36, Q39
the_pay_fog                                     3       FAILING  Q14, Q16, Q19
the_policy_lag                                  7       FAILING  Q06, Q10, Q19, Q22, Q37, SEVER-04, VERIFY-Q22
the_second_close                                5       passing  Q03A, Q03A-D-FOLLOW, Q27A, SEVER-09, VERIFY-Q27A
the_suppression_filter                          5       passing  Q04, Q08, Q12, Q18, Q30
the_tolerated_violation                         1       FAILING  Q06
the_undefined_role                              6       passing  Q20, Q35, Q36, Q37, SEVER-02, VERIFY-Q20
the_unexamined_algorithm                        3       FAILING  Q22, Q37, VERIFY-Q22
the_unformed_leader                             5       passing  Q12, Q25, Q38, Q39, VERIFY-Q25
the_uninitiated                                 2       passing  Q03A, Q03A-D-FOLLOW
the_unlocked_door                               1       passing  Q18
the_unreported_hazard                           1       passing  Q18
the_unsolved_problem                            8       passing  Q03A, Q03A-D-FOLLOW, Q06, Q28, Q31, SEVER-11, VERIFY-Q28, VERIFY-Q31
the_untouchable                                 2       passing  Q05, Q12
the_wrong_reward                                2       passing  Q05, Q11
transition_paralysis                            2       FAILING  Q03A, Q03A-D-FOLLOW
what_nobody_says                                2       passing  Q04, Q18

Summary (question count):
  Passing HC states (38): min=1, max=8, mean=3.8
  Failing HC states (9):  min=1, max=8, mean=3.4

## SECTION 2: Actual scores and ranks — 9 failing HC states
State                                         Tgt score  Rank Rank-1 sink                                   R1 score     Gap  Pass
----------------------------------------------------------------------------------------------------------------------------------
the_pay_fog                                     -0.8117    40 built_to_fail                                  -0.6001  0.2117     N  <<BURIED
the_tolerated_violation                         -0.9372    45 leadership_deafness                            -0.7223  0.2150     N  <<BURIED
dueling_narratives                              -0.8487    36 built_to_fail                                  -0.6334  0.2154     N  <<BURIED
transition_paralysis                            -0.8712    37 leadership_deafness                            -0.6335  0.2377     N  <<BURIED
the_unexamined_algorithm                        -0.8480    41 built_to_fail                                  -0.5851  0.2629     N  <<BURIED
hr_capture                                      -0.9090    32 the_diversity_ceiling                          -0.5897  0.3193     N  <<BURIED
leadership_continuity_risk                      -0.8742    38 built_to_fail                                  -0.5257  0.3485     N  <<BURIED
paper_shield                                    -0.8803    30 built_to_fail                                  -0.4796  0.4006     N  <<BURIED
the_policy_lag                                  -0.7491    33 built_to_fail                                  -0.2068  0.5424     N  <<BURIED

Top-5 rankings for each failing state:

  the_pay_fog (target rank=40, score=-0.8117, gap=0.2117):
    rank  1: built_to_fail                                score=-0.6001
    rank  2: the_paper_tiger                              score=-0.6001
    rank  3: identity_erosion                             score=-0.6407
    rank  4: the_culture_that_wasnt                       score=-0.6407
    rank  5: narrative_lock                               score=-0.6407

  the_tolerated_violation (target rank=45, score=-0.9372, gap=0.2150):
    rank  1: leadership_deafness                          score=-0.7223
    rank  2: the_diversity_ceiling                        score=-0.7497
    rank  3: the_burned_credibility                       score=-0.7497
    rank  4: invisible_burnout                            score=-0.7497
    rank  5: the_basement_standard                        score=-0.7497

  dueling_narratives (target rank=36, score=-0.8487, gap=0.2154):
    rank  1: built_to_fail                                score=-0.6334
    rank  2: the_paper_tiger                              score=-0.6334
    rank  3: identity_erosion                             score=-0.6594
    rank  4: the_culture_that_wasnt                       score=-0.6594
    rank  5: narrative_lock                               score=-0.6594

  transition_paralysis (target rank=37, score=-0.8712, gap=0.2377):
    rank  1: leadership_deafness                          score=-0.6335
    rank  2: identity_erosion                             score=-0.6624
    rank  3: the_culture_that_wasnt                       score=-0.6624
    rank  4: narrative_lock                               score=-0.6624
    rank  5: the_unreported_hazard                        score=-0.6624

  the_unexamined_algorithm (target rank=41, score=-0.8480, gap=0.2629):
    rank  1: built_to_fail                                score=-0.5851
    rank  2: the_paper_tiger                              score=-0.5851
    rank  3: the_undefined_role                           score=-0.6398
    rank  4: the_unformed_leader                          score=-0.6423
    rank  5: the_dormant_talent                           score=-0.6423

  hr_capture (target rank=32, score=-0.9090, gap=0.3193):
    rank  1: the_diversity_ceiling                        score=-0.5897
    rank  2: the_burned_credibility                       score=-0.5897
    rank  3: invisible_burnout                            score=-0.5897
    rank  4: the_basement_standard                        score=-0.5897
    rank  5: the_inside_track                             score=-0.5897

  leadership_continuity_risk (target rank=38, score=-0.8742, gap=0.3485):
    rank  1: built_to_fail                                score=-0.5257
    rank  2: the_paper_tiger                              score=-0.5257
    rank  3: the_undefined_role                           score=-0.6223
    rank  4: the_unformed_leader                          score=-0.6604
    rank  5: the_dormant_talent                           score=-0.6604

  paper_shield (target rank=30, score=-0.8803, gap=0.4006):
    rank  1: built_to_fail                                score=-0.4796
    rank  2: the_paper_tiger                              score=-0.4796
    rank  3: the_undefined_role                           score=-0.5652
    rank  4: the_unformed_leader                          score=-0.6013
    rank  5: the_dormant_talent                           score=-0.6013

  the_policy_lag (target rank=33, score=-0.7491, gap=0.5424):
    rank  1: built_to_fail                                score=-0.2068
    rank  2: the_paper_tiger                              score=-0.2068
    rank  3: the_undefined_role                           score=-0.3105
    rank  4: the_unformed_leader                          score=-0.3953
    rank  5: the_dormant_talent                           score=-0.3953

## SECTION 3: the_policy_lag — best-option signal map
  Q-ID         Best  auth_l (best)   Neutral  auth_l (neutral)  Best-opt vector (apt / aut / all / att liability)
  ---------------------------------------------------------------------------------------------------------
  Q06             A         0.6000         E            0.0000  apt=0.25  aut=0.60  all=0.00  att=0.30
  Q10             C         0.3000         B            0.0000  apt=0.60  aut=0.30  all=0.00  att=0.00
  Q19             C         0.5000         B            0.2500  apt=0.25  aut=0.50  all=0.00  att=0.25
  Q22             C         0.5000         B           -0.1000  apt=0.25  aut=0.50  all=0.00  att=0.00
  Q37             C         0.4000         B            0.2500  apt=0.60  aut=0.40  all=0.00  att=0.00
  SEVER-04        A         0.4000         A            0.4000  apt=0.40  aut=0.40  all=0.25  att=0.25
  VERIFY-Q22      D         0.6000         B            0.2500  apt=0.60  aut=0.60  all=0.00  att=0.00

  Cumulative authority_liability — state_targets questions only:
    Best-option path:       3.3000
    Neutral path:           1.0500
    Delta (best - neutral): 2.2500

  Full HC session accumulated vector for the_policy_lag (n=39 questions):
  Field                           Accumulated  Centroid*scale   Displaced
  ------------------------------------------------------------------------
  aptitude_liability                   3.8500          3.9565     -0.1065
  aptitude_asset                       0.2500          0.6800     -0.4300
  authority_liability                  4.2350          5.3601     -1.1251
  authority_asset                      1.4850          1.6503     -0.1653
  alliance_liability                   1.3750          2.9859     -1.6109
  alliance_asset                       0.2750          0.1924      0.0826
  attitude_liability                   2.8000          4.8137     -2.0137
  attitude_asset                       2.1500          0.9795      1.1705

## SECTION 4: hr_capture — cross-dimension sink analysis
  SCD-WCS result against hr_capture HC session:
    hr_capture:            rank= 32  score=-0.9090
    the_diversity_ceiling:  rank=  1  score=-0.5897
    Gap (DC over HR): 0.3193

  Profile vectors (hr_capture vs the_diversity_ceiling):
  Field                            HR profile   DC profile
  --------------------------------------------------------
  aptitude_liability                   0.1000       0.1500
  aptitude_asset                       0.1000       0.1500
  authority_liability                  0.6000       0.1500
  authority_asset                      0.1000       0.1500
  alliance_liability                   0.1000       0.1500
  alliance_asset                       0.1000       0.1500
  attitude_liability                   0.1000       0.4500
  attitude_asset                       0.1000       0.1500

  hr_capture HC session: accumulated → displaced (n=39, centroid scale=1.000x):
  Note: displaced = accumulated − (MC_CENTROID_39 × scale). This is what SCD-WCS ranks against.
  Field                           Accumulated  Centroid×scale  Displaced    HR dot    DC dot  Favors
  ----------------------------------------------------------------------------------------------------
  aptitude_liability                   2.6000          3.9565    -1.3565   -0.1357   -0.2035  HR
  aptitude_asset                       0.0000          0.6800    -0.6800   -0.0680   -0.1020  HR
  authority_liability                  3.1900          5.3601    -2.1701   -1.3021   -0.3255  DC
  authority_asset                      1.3200          1.6503    -0.3303   -0.0330   -0.0495  HR
  alliance_liability                   0.8500          2.9859    -2.1359   -0.2136   -0.3204  HR
  alliance_asset                       0.0000          0.1924    -0.1924   -0.0192   -0.0289  HR
  attitude_liability                   3.4800          4.8137    -1.3337   -0.1334   -0.6002  HR
  attitude_asset                       1.9200          0.9795     0.9405    0.0940    0.1411  DC

  Note: 'Favors' reflects raw displaced×profile dot product only.
  Actual SCD-WCS uses salience-weighted cosine + normalization —
  the above is directional intuition, not the exact scoring mechanism.

## SECTION 5: coverage vs. gap correlation — 9 failing states
  State                                            Gap  Q count  Question IDs
  ------------------------------------------------------------------------------------------
  the_policy_lag                                0.5424        7  Q06, Q10, Q19, Q22, Q37, SEVER-04, VERIFY-Q22
  paper_shield                                  0.4006        4  Q10, Q23, Q33, SEVER-05
  leadership_continuity_risk                    0.3485        8  Q03A-D-FOLLOW, Q23, Q25, Q33, Q38, SEVER-05, SEVER-07, VERIFY-Q25
  hr_capture                                    0.3193        2  Q02, Q04
  the_unexamined_algorithm                      0.2629        3  Q22, Q37, VERIFY-Q22
  transition_paralysis                          0.2377        2  Q03A, Q03A-D-FOLLOW
  dueling_narratives                            0.2154        1  Q19
  the_tolerated_violation                       0.2150        1  Q06
  the_pay_fog                                   0.2117        3  Q14, Q16, Q19

  Pearson r (gap vs. question count): 0.750
  Conclusion: positive correlation — unusual, requires investigation.

========================================================================
Diagnostic complete — read-only. No engine files modified.
========================================================================