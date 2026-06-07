"""
Patch script: MOB v3.9 -> v4.0
Targeted compression pass: Sections 9, 13, 15.
Confirmed by Pete Session 35. Sections 1-8, 10-12, 14, 16 untouched.
Usage: python tools/patch_mob_s35_compression.py          # dry run
       python tools/patch_mob_s35_compression.py --write  # apply
"""
import sys
from pathlib import Path

MOB = Path("tools/_mob.txt")
content = MOB.read_text(encoding="utf-8")
original = content

EM = "—"   # em-dash U+2014

# File escaping reference:
# Bold markers:  \\\*\\\* (3 backslashes + asterisk on each side)
# Underscores in filenames: \\_  (2 backslashes + underscore)
# In raw strings: r"\\\*" = 3 backslashes + asterisk  (matches file)
#                 r"\\_"  = 2 backslashes + underscore (matches file)


# =============================================================================
# SECTION 9: Replace Sessions 20-28 verbose blocks with compressed entries
# Start anchor: \\\*\\\*Session 20 changes  (3 backslashes + * on each side)
# End anchor:   "Commit: 30738d4."  (inclusive)
# =============================================================================

SEC9_START = r"\\\*\\\*Session 20 changes"
SEC9_END   = "Commit: 30738d4."

idx9_s = content.find(SEC9_START)
if idx9_s == -1:
    print("FAIL: Section 9 start anchor not found")
    sys.exit(1)

idx9_e = content.find(SEC9_END, idx9_s)
if idx9_e == -1:
    print("FAIL: Section 9 end anchor not found")
    sys.exit(1)
idx9_e += len(SEC9_END)

_SEP = "\n\n  \n\n  \n\n  \n\n"

SEC9_NEW = (
    "\\*\\*[S20] HC/extreme state_targets gating + the_unexamined_algorithm"
    f" {EM} locked:\\*\\*"
    " generate_answers() in calibration_runner.py: HC/extreme profiles call"
    " best_option_for_state() on state_targets questions only; _neutral_option() elsewhere."
    " the_unexamined_algorithm: auth_l=0.50, apt_l=0.35, all other fields=0.10."
    + _SEP +
    "\\*\\*[S21] SALIENCE_PROFILES weighted cosine + v15 authority drain"
    f" {EM} locked:\\*\\*"
    " Phase 2 calibration metric updated to SALIENCE_PROFILES weighted cosine"
    " (target dimension fields: 2.5, off-axis: 0.4). v15 authority drain:"
    " authority_liability stripped from Q07/Q09/Q16/Q20/Q26/Q29 secondary options."
    " Q06 APT-PT-00 state_targets corrected."
    + _SEP +
    "\\*\\*[S22] v16 negative authority contrast injection"
    f" {EM} locked:\\*\\*"
    " Contrast injection across 8 option vectors, 6 questions"
    " (Q14-B/C, Q16-B/C, Q22-B, Q26-C, Q35-B, Q36-E)."
    " Total installed authority drain: -1.20."
    + _SEP +
    "\\*\\*[S23] Q20 C/D authority_liability 0.60->0.80"
    f" {EM} locked:\\*\\*"
    " Track 2 (Q20 C/D raise) retained. Track 1 (culture_drift salience reduction)"
    " and Track 3 (Authority vector sharpening) applied and reverted."
    " states.py and salience.py net unchanged from pre-session committed state."
    " Q20 0.80 is the sole lasting change."
    + _SEP +
    "\\*\\*[S26] leadership_deafness reshape + cluster cleanup + top-cluster criterion"
    f" {EM} locked:\\*\\*"
    " leadership_deafness att_l raised 0.35->0.50."
    " C-Silence/C-InfoFlow dismantled: cluster_id=None for"
    " what_nobody_says, the_unreported_hazard, the_unlocked_door,"
    " leadership_deafness, the_suppression_filter. C-Manager/C-Culture retained."
    " _passes_cluster_criterion(): target passes if score >= rank_1_score"
    f" {EM} SCD_WCS_CLUSTER_WINDOW (initial 0.20). HC 38/47."
    + _SEP +
    "\\*\\*[S27] CENTROID_FIELD_SCALARS + window 0.35, 28-round calibration"
    f" {EM} HC RESOLVED {EM} locked:\\*\\*"
    " CENTROID_FIELD_SCALARS per-field scalars added to accumulation.py (Path B):"
    " mu_focused[f] = MC_CENTROID_39[f] * CENTROID_FIELD_SCALARS[f] * (N/39.0)."
    " SCD_WCS_CLUSTER_WINDOW raised 0.20->0.35 (Path C)."
    " 28-round autonomous calibration, no regressions: HC 47/47 RESOLVED."
    " Final scalars: apt_l=0.2415, auth_l=0.3318, all_l=0.2185, att_l=0.4267 (all asset=0.4000)."
    " _PRECOMPUTED_NOISE_BASELINE recalibrated (mean 0.8724). --output-json flag added."
    " Commit: 15ffb8d."
    + _SEP +
    "\\*\\*[S28] Prominence criterion for moderate/weak"
    f" {EM} locked:\\*\\*"
    " _passes_prominence_criterion() added to calibration_runner.py."
    " Pass conditions (both required):"
    " (1) target score >= SCD_WCS_ALIGNMENT_THRESHOLD;"
    " (2) target score >= rank_1_score - delta"
    " (MODERATE_PROMINENCE_DELTA=0.20, WEAK_PROMINENCE_DELTA=0.50)."
    " WEAK delta adjusted from 0.45 for Authority HIGH tier geometry."
    " 57/142->133/142. Commit: 30738d4."
)

content = content[:idx9_s] + SEC9_NEW + content[idx9_e:]
print("Section 9: OK")


# =============================================================================
# SECTION 13: Replace Phase 1 summary through open items end.
# Start anchor: r"\\\*\\\*Phase 1 summary"
# End anchor (inclusive): "| Content library citation audit | Open. E2, E5, E7 priority. |"
# =============================================================================

SEC13_START = r"\\\*\\\*Phase 1 summary"
SEC13_END   = "| Content library citation audit | Open. E2, E5, E7 priority. |"

idx13_s = content.find(SEC13_START)
if idx13_s == -1:
    print("FAIL: Section 13 start anchor not found")
    sys.exit(1)

idx13_e = content.find(SEC13_END, idx13_s)
if idx13_e == -1:
    print("FAIL: Section 13 end anchor not found")
    sys.exit(1)
idx13_e += len(SEC13_END)

_NL  = "\n\n  \n\n  \n\n  \n\n"
_NL2 = "\n\n\n\n"

def _row(item, desc):
    return f"| {item} | {desc} |"

SEC13_NEW = (
    f"\\*\\*Phase 1 {EM} CLOSED Session 12.\\*\\*"
    " Synthetic injection confirmed dimensional routing at dimension level."
    f" 26/142 synthetic profiles passed {EM} zero cross-dimension errors."
    " Gemini confirmed transition to Phase 2."
    + _NL +
    f"\\*\\*Phase 2 {EM} CLOSED Session 29 at 137/142 (96.5%):"
    f" 47 HC + 1 extreme HC + 44 moderate + 45 weak.\\*\\*"
    " Key interventions:\n\n"
    f"\\- v12 (S19): _neutral_option() fixed, signal-driven mode activated {EM} 14/142\n\n"
    f"\\- v21 (S24): SCD-WCS metric + centroid displacement implemented"
    f" {EM} coordinate-space change, HC 0/47\n\n"
    f"\\- v23 (S26): leadership_deafness reshape + top-cluster criterion"
    f" {EM} 42/142, HC 38/47\n\n"
    f"\\- v24 (S27): CENTROID_FIELD_SCALARS + window=0.35,"
    f" 28-round autonomous calibration {EM} HC 47/47 RESOLVED\n\n"
    f"\\- v25 (S28): Prominence criterion added {EM} 133/142\n\n"
    f"\\- v26 (S29): MODERATE_PROMINENCE_DELTA 0.20->0.26 {EM} 137/142\n\n"
    f"\\- v27 (S29): the_undefined_role dual-axis reshape,"
    f" sink collapsed 23->1 {EM} Phase 2 CLOSED\n\n"
    "Full progression in Section 16 session log."
    + _NL +
    f"\\*\\*5 remaining structural failures (deferred Phase 3):\\*\\*"
    " identity_erosion moderate (gap -0.4266), transition_paralysis moderate (-0.3441),"
    " the_untouchable moderate (-0.3079), leadership_deafness weak (-0.5502),"
    " the_untouchable weak (-0.6027). All built_to_fail casualties."
    f" Defer to real-world signal {EM} checkpoint routing and narrative prompts"
    " not exercised in synthetic testing."
    + _NL +
    "\\*\\*Open items\\*\\*"
    + _NL +
    _row("Router prerequisites",
         f"Deferred {EM} HC criterion met via cluster window."
         " Two prerequisites unmet for re-attempt:"
         " (a) intra-dimensional sink suppression;"
         " (b) question library signal sufficient for all 4 dimensions under generate_answers().")
    + _NL2 +
    "| --- | --- |"
    + _NL2 +
    _row("culture_drift intra-dimensional dominance",
         "Captures 15/17 Attitude HC profiles within Attitude-only competition pool."
         " Primary Attitude sink. Not resolved by salience reduction (Track 1 reverted). Phase 3 scope.")
    + _NL2 +
    _row("the_overloaded_manager co-dominant sink",
         "Aptitude primary salience (2.5). Persistent secondary sink.")
    + _NL2 +
    _row("the_uninitiated intra-Authority sink",
         "Residual moderate Authority sink.")
    + _NL2 +
    _row("paper_shield intra-Authority sink",
         "Secondary intra-Authority sink. Persistent.")
    + _NL2 +
    _row("APT-PT-00 (the_paper_tiger)",
         "Routes to built_to_fail (x3) + culture_drift (x1) in v20. Severity escalation flag in use.")
    + _NL2 +
    _row("the_fracture",
         "Routes to the_suppression_filter (x2) + the_overloaded_manager (x1).")
    + _NL2 +
    _row("Mode 2 floor deficits (Track 4)",
         "the_arbitrary_standard, what_nobody_says, the_dormant_talent,"
         " the_overloaded_manager. Deferred.")
    + _NL2 +
    _row("Q06 neutral drain", "Skipped v17-v20. Carries forward.")
    + _NL2 +
    _row("VERIFY-Q25 copy review", "Queued.")
    + _NL2 +
    _row("Q23-A SEVER-05 paths", "Queued.")
    + _NL2 +
    _row("Negative accumulated values assertion", "Queued.")
    + _NL2 +
    _row("Construction and Logistics intake expansion", "Queued.")
    + _NL2 +
    _row("The Dormant Talent Signal Map correction",
         "Signal Map lists Attitude/Alliance; states.py correctly assigns"
         " primary_dimension=Aptitude. Document requires correction.")
    + _NL2 +
    _row("built_to_fail as structural rank-1 sink",
         "Remains rank-1 for ~83+ profiles (all types) under v24/v25."
         " HC passes via cluster criterion; moderate/weak via prominence criterion."
         " Intervention requires: (a) question library signal to displace btf from rank-1,"
         f" or (b) salience adjustment. Deferred {EM} Pete decides.")
    + _NL2 +
    _row("5 remaining structural failures",
         "identity_erosion moderate (gap -0.4266), transition_paralysis moderate (-0.3441),"
         " the_untouchable moderate (-0.3079), leadership_deafness weak (-0.5502),"
         " the_untouchable weak (-0.6027). All built_to_fail casualties. Deferred to Phase 3.")
    + _NL2 +
    _row("Asset axis calibration",
         "Deferred to Phase 3. CENTROID_FIELD_SCALARS 0.4000 values are displacement scalars,"
         " not state-vector asset field values (tier-standard 0.10/0.15)."
         " See Section 9 asset field correction note.")
    + _NL2 +
    _row("Rank 2 (Q5/Q7 attitude injection)",
         "Stood down Session 29. Gemini assessed insufficient against -0.43 gap."
         " Revisit only with real-world signal. Not live work.")
    + _NL2 +
    _row("Gemini commercial brief", "Produced Session 31. Pete to engage separately.")
    + _NL2 +
    _row("The Work", "Held. Weight confirmed. Address unknown.")
    + _NL2 +
    _row("Service-specific path design",
         "How each of the four resolution services presents on the site."
         " What a practitioner-directed arrival finds.")
    + _NL2 +
    _row("Menu execution layout",
         "How the two-tier structure looks on the page."
         " Weight and position of Diagnostic relative to the four.")
    + _NL2 +
    _row("Content library citation audit", "Open. E2, E5, E7 priority.")
    + _NL2 +
    _row("LinkedIn BD legal read",
         "Required before personal account amplification."
         " Non-solicitation agreement with OneDigital governs."
         " Attorney to advise on: passive content sharing,"
         " definition of solicitation under agreement, LinkedIn as channel.")
)

content = content[:idx13_s] + SEC13_NEW + content[idx13_e:]
print("Section 13: OK")


# =============================================================================
# SECTION 15: Compress per-file session histories to current state only.
# Strategy: find each long entry by file-path anchor, replace entire line.
# NOTE: Filename underscores in file use \\_  (2 backslashes + underscore).
#       In raw strings this is r"\\_".
# =============================================================================

def replace_line_by_anchor(c, anchor, new_line, label):
    """Find the line starting with anchor, replace it with new_line."""
    idx = c.find(anchor)
    if idx == -1:
        print(f"FAIL: Section 15 entry not found: {label}")
        sys.exit(1)
    idx_end = c.find("\n", idx)
    if idx_end == -1:
        idx_end = len(c)
    return c[:idx] + new_line + c[idx_end:]


# engine/data/states.py  (no underscores in path segments needing double-escape)
ANCHOR_STATES = r"| \\\*\\\*engine/data/states.py\\\*\\\*"
NEW_STATES = (
    r"| \\\*\\\*engine/data/states.py\\\*\\\* | "
    "47 state profiles. All 47 states at explicit DimensionalVector overrides"
    f" {EM} global tier standardization complete (S17). Current locked changes:"
    r" the\_unexamined\_algorithm auth\_l=0.50/apt\_l=0.35 (S20);"
    r" leadership\_deafness att\_l=0.50 (S26);"
    r" cluster\_id=None for C-Silence/C-InfoFlow 5 states (S26);"
    r" the\_undefined\_role dual-axis reshape apt\_l/auth\_l=0.35/0.35, sink 23->1 (S29). |"
)
content = replace_line_by_anchor(content, ANCHOR_STATES, NEW_STATES, "states.py")
print("Section 15 states.py: OK")


# engine/data/questions.py
ANCHOR_Q = r"| \\\*\\\*engine/data/questions.py\\\*\\\*"
NEW_Q = (
    r"| \\\*\\\*engine/data/questions.py\\\*\\\* | "
    r"67 entries. All options in \_opt\_contrib. SEVER-05 signed delta contributions."
    " Contrast fields injected S18 (Q02-B, Q04-D, Q10-C, Q11-C, Q15-C, Q23-C/D)"
    " and S22 (Q14-B/C, Q16-B/C, Q22-B, Q26-C, Q35-B, Q36-E)."
    r" Q20 C/D auth\_l=0.80 (S23). \\*\\*Do not modify without Gemini brief.\\*\\* |"
)
content = replace_line_by_anchor(content, ANCHOR_Q, NEW_Q, "questions.py")
print("Section 15 questions.py: OK")


# engine/data/salience.py
ANCHOR_SAL = r"| \\\*\\\*engine/data/salience.py\\\*\\\*"
NEW_SAL = (
    r"| \\\*\\\*engine/data/salience.py\\\*\\\* | "
    "SALIENCE_PROFILES weight vectors. Three-Tier standard."
    r" culture\_drift and the\_suppression\_filter reverted to standard (S26). |"
)
content = replace_line_by_anchor(content, ANCHOR_SAL, NEW_SAL, "salience.py")
print("Section 15 salience.py: OK")


# engine/data/intake.py
ANCHOR_INT = r"| \\\*\\\*engine/data/intake.py\\\*\\\*"
NEW_INT = (
    r"| \\\*\\\*engine/data/intake.py\\\*\\\* | "
    "Intake field definitions and prior adjusters."
    r" Three PriorAdjuster entries: attitude\_conduct (1.10x),"
    r" attitude\_departure (1.07x), aptitude\_redesign (1.12x). All calibration targets. |"
)
content = replace_line_by_anchor(content, ANCHOR_INT, NEW_INT, "intake.py")
print("Section 15 intake.py: OK")


# engine/output.py
ANCHOR_OUT = r"| \\\*\\\*engine/output.py\\\*\\\*"
NEW_OUT = (
    r"| \\\*\\\*engine/output.py\\\*\\\* | "
    r"Output engine. SIGNAL\_FLOOR\_MULTIPLIER\_DEFAULT 1.08x."
    r" SCD\_WCS\_ALIGNMENT\_THRESHOLD=-0.4000 governs floor gating."
    r" \_PRECOMPUTED\_NOISE\_BASELINE mean 0.8724 (v24 calibration, used for score\_lift\_pct only). |"
)
content = replace_line_by_anchor(content, ANCHOR_OUT, NEW_OUT, "output.py")
print("Section 15 output.py: OK")


# engine/accumulation.py
ANCHOR_ACC = r"| \\\*\\\*engine/accumulation.py\\\*\\\*"
NEW_ACC = (
    r"| \\\*\\\*engine/accumulation.py\\\*\\\* | "
    r"Accumulation engine. SCD-WCS implemented. MC\_CENTROID\_39 constant."
    r" CENTROID\_FIELD\_SCALARS per-field scalars (Path B)."
    " Final v24 values: apt_l=0.2415, auth_l=0.3318, all_l=0.2185, att_l=0.4267."
    r" answered\_question\_count parameter in rank\_states(). |"
)
content = replace_line_by_anchor(content, ANCHOR_ACC, NEW_ACC, "accumulation.py")
print("Section 15 accumulation.py: OK")


# tools/calibration_runner.py — file uses \\\ (3 backslashes) before underscore in filename
ANCHOR_CR = r"| \\\*\\\*tools/calibration\\\_runner.py\\\*\\\*"
NEW_CR = (
    r"| \\\*\\\*tools/calibration\\\_runner.py\\\*\\\* | "
    "Phase 1/2 calibration runner. Signal-driven mode."
    " HC/extreme state_targets gating. SALIENCE_PROFILES weighted cosine."
    " _passes_cluster_criterion() for HC/extreme (SCD_WCS_CLUSTER_WINDOW=0.35)."
    " _passes_prominence_criterion() for moderate/weak. --output-json flag for harness. |"
)
content = replace_line_by_anchor(content, ANCHOR_CR, NEW_CR, "calibration_runner.py")
print("Section 15 calibration_runner.py: OK")


# tools/patch_v21_cdwcs.py
ANCHOR_CDWCS = r"| \\\*\\\*tools/patch\\\_v21\\\_cdwcs.py\\\*\\\*"
NEW_CDWCS = (
    r"| \\\*\\\*tools/patch\\\_v21\\\_cdwcs.py\\\*\\\* | "
    "S24. Applied SCD-WCS: MC_CENTROID_39 constant, rank_states() displacement, answered_question_count. |"
)
content = replace_line_by_anchor(content, ANCHOR_CDWCS, NEW_CDWCS, "patch_v21_cdwcs.py")
print("Section 15 patch_v21_cdwcs.py: OK")


# tools/patch_v21_absolute_threshold.py
ANCHOR_PAT = r"| \\\*\\\*tools/patch\\\_v21\\\_absolute\\\_threshold.py\\\*\\\*"
NEW_PAT = (
    r"| \\\*\\\*tools/patch\\\_v21\\\_absolute\\\_threshold.py\\\*\\\* | "
    "S24. Floor system replacement: SCD_WCS_ALIGNMENT_THRESHOLD=0.25 and check_signal_gate(). |"
)
content = replace_line_by_anchor(content, ANCHOR_PAT, NEW_PAT, "patch_v21_absolute_threshold.py")
print("Section 15 patch_v21_absolute_threshold.py: OK")


# tools/diag_v21_accumulated_centroid.py
ANCHOR_D21 = r"| \\\*\\\*tools/diag\\\_v21\\\_accumulated\\\_centroid.py\\\*\\\*"
NEW_D21 = (
    r"| \\\*\\\*tools/diag\\\_v21\\\_accumulated\\\_centroid.py\\\*\\\* | "
    "S24. Produced MC_CENTROID_39 empirical means. N=1000, seed=42, Q01-Q39. Not committed. |"
)
content = replace_line_by_anchor(content, ANCHOR_D21, NEW_D21, "diag_v21_accumulated_centroid.py")
print("Section 15 diag_v21_accumulated_centroid.py: OK")


# tools/patch_v23_cluster_criterion.py
ANCHOR_P23CC = r"| \\\*\\\*tools/patch\\\_v23\\\_cluster\\\_criterion.py\\\*\\\*"
NEW_P23CC = (
    r"| \\\*\\\*tools/patch\\\_v23\\\_cluster\\\_criterion.py\\\*\\\* | "
    "S26. Adds _passes_cluster_criterion(); SCD_WCS_CLUSTER_WINDOW=0.20. |"
)
content = replace_line_by_anchor(content, ANCHOR_P23CC, NEW_P23CC, "patch_v23_cluster_criterion.py")
print("Section 15 patch_v23_cluster_criterion.py: OK")


# tools/harness_s27_autonomous_calibration.py
ANCHOR_H27 = r"| \\\*\\\*tools/harness\\\_s27\\\_autonomous\\\_calibration.py\\\*\\\*"
NEW_H27 = (
    r"| \\\*\\\*tools/harness\\\_s27\\\_autonomous\\\_calibration.py\\\*\\\* | "
    "S27. Autonomous calibration harness. 28 rounds executed, RESOLVED 47/47 HC. Not committed. |"
)
content = replace_line_by_anchor(content, ANCHOR_H27, NEW_H27, "harness_s27")
print("Section 15 harness_s27: OK")


# tools/diag_s27_failing_hc_characterization.py
ANCHOR_D27PY = r"| \\\*\\\*tools/diag\\\_s27\\\_failing\\\_hc\\\_characterization.py\\\*\\\*"
NEW_D27PY = (
    r"| \\\*\\\*tools/diag\\\_s27\\\_failing\\\_hc\\\_characterization.py\\\*\\\* | "
    "S27. Characterized 9 failing HC profiles under v23. Root cause: authority centroid dominance. Not committed. |"
)
content = replace_line_by_anchor(content, ANCHOR_D27PY, NEW_D27PY, "diag_s27_failing_hc_characterization.py")
print("Section 15 diag_s27_failing_hc_characterization.py: OK")


# tools/diag_s27_failing_hc_characterization.md
ANCHOR_D27MD = r"| \\\*\\\*tools/diag\\\_s27\\\_failing\\\_hc\\\_characterization.md\\\*\\\*"
NEW_D27MD = (
    r"| \\\*\\\*tools/diag\\\_s27\\\_failing\\\_hc\\\_characterization.md\\\*\\\* | "
    "S27. Diagnostic output: displacement paradox finding. Not committed. |"
)
content = replace_line_by_anchor(content, ANCHOR_D27MD, NEW_D27MD, "diag_s27_failing_hc_characterization.md")
print("Section 15 diag_s27_failing_hc_characterization.md: OK")


# tools/patch_output_noise_baseline_v24.py
ANCHOR_PNB = r"| \\\*\\\*tools/patch\\\_output\\\_noise\\\_baseline\\\_v24.py\\\*\\\*"
NEW_PNB = (
    r"| \\\*\\\*tools/patch\\\_output\\\_noise\\\_baseline\\\_v24.py\\\*\\\* | "
    "S27. Patches _PRECOMPUTED_NOISE_BASELINE with v24 per-state means. Not committed. |"
)
content = replace_line_by_anchor(content, ANCHOR_PNB, NEW_PNB, "patch_output_noise_baseline_v24.py")
print("Section 15 patch_output_noise_baseline_v24.py: OK")


# tools/test_accumulation.py
ANCHOR_TA = r"| \\\*\\\*tools/test\\\_accumulation.py\\\*\\\*"
NEW_TA = (
    r"| \\\*\\\*tools/test\\\_accumulation.py\\\*\\\* | "
    "S27: hardcoded SCD-WCS distance replaced with structural invariant check."
    " Required for harness compatibility. Committed 15ffb8d. |"
)
content = replace_line_by_anchor(content, ANCHOR_TA, NEW_TA, "test_accumulation.py")
print("Section 15 test_accumulation.py: OK")


# tools/diag_s28_moderate_weak_gap.py
ANCHOR_D28PY = r"| \\\*\\\*tools/diag\\\_s28\\\_moderate\\\_weak\\\_gap.py\\\*\\\*"
NEW_D28PY = (
    r"| \\\*\\\*tools/diag\\\_s28\\\_moderate\\\_weak\\\_gap.py\\\*\\\* | "
    "S28. Characterized 85 failing moderate/weak profiles under v24."
    " All competition-blocked (0 floor-gated). built_to_fail rank-1 in 59/85. Not committed. |"
)
content = replace_line_by_anchor(content, ANCHOR_D28PY, NEW_D28PY, "diag_s28_moderate_weak_gap.py")
print("Section 15 diag_s28_moderate_weak_gap.py: OK")


# tools/diag_s28_moderate_weak_gap.md
ANCHOR_D28MD = r"| \\\*\\\*tools/diag\\\_s28\\\_moderate\\\_weak\\\_gap.md\\\*\\\*"
NEW_D28MD = (
    r"| \\\*\\\*tools/diag\\\_s28\\\_moderate\\\_weak\\\_gap.md\\\*\\\* | "
    "S28. Gap distribution: moderate -0.05 to -0.20, weak -0.30 to -0.50."
    " Mean gap -0.2337. built_to_fail rank-1 in 59/85. Not committed. |"
)
content = replace_line_by_anchor(content, ANCHOR_D28MD, NEW_D28MD, "diag_s28_moderate_weak_gap.md")
print("Section 15 diag_s28_moderate_weak_gap.md: OK")

print("Section 15: all entries OK")


# =============================================================================
# VERSION BUMP: v3.9 -> v4.0
# =============================================================================
VER_FIND    = r"\\\#\\\# MOB v3.9"
VER_REPLACE = r"\\\#\\\# MOB v4.0"

if VER_FIND not in content:
    print("FAIL: version string v3.9 not found")
    sys.exit(1)
content = content.replace(VER_FIND, VER_REPLACE, 1)
print("Version v3.9 -> v4.0: OK")


# =============================================================================
# WRITE / DRY RUN
# =============================================================================
dry_run = "--write" not in sys.argv
if dry_run:
    old_lines = original.splitlines()
    new_lines = content.splitlines()
    delta = len(new_lines) - len(old_lines)
    sign = "+" if delta >= 0 else ""
    print(f"\nDRY RUN complete. Lines: {len(old_lines)} -> {len(new_lines)} ({sign}{delta})")
    print("Run with --write to apply.")
else:
    Path("tools/_mob.txt").write_text(content, encoding="utf-8")
    print("\nWRITE complete. MOB v4.0.")
