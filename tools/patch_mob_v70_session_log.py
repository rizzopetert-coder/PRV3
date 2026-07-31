"""
PRV3 -- Combined write: CLAUDE.md Standing Rules bullet (em-dash rule) +
CLAUDE.md MOB version cross-reference + tools/_mob.txt version header +
tools/_mob.txt Section 16 new session log row.

Four anchored edits, each verified unique before write:
  1. CLAUDE.md: insert new em-dash Standing Rules bullet after the
     existing "No semicolons in any string or copy." bullet.
  2. CLAUDE.md: | MOB version | v4.69 | -> v4.70.
  3. tools/_mob.txt: \\\\\\#\\\\\\# MOB v4.69 header -> v4.70.
  4. tools/_mob.txt: insert new Section 16 row after the "Diagnostic
     fast-forward tool" row (MOB v4.67), before "Session 1" (MOB v1.0).

Content confirmed verbatim via two dry-run passes this session (P-##
overlap check, then the corrected Standing-Rules-bullet version).

Usage:
  python tools/patch_mob_v70_session_log.py --dry-run
  python tools/patch_mob_v70_session_log.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
CLAUDE_MD = REPO_ROOT / "CLAUDE.md"
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"

# ── CLAUDE.md edit 1: new Standing Rules bullet ─────────────────────────────

CLAUDE_ANCHOR_1 = "- No semicolons in any string or copy.\n- No coined terms requiring a glossary in any output string.\n"
CLAUDE_REPLACEMENT_1 = (
    "- No semicolons in any string or copy.\n"
    "- No em-dashes as default connective tissue. An em-dash is permitted "
    "only to mark a genuine interruption or pivot for emphasis, something "
    "a comma, colon, or rephrase can't do as well, not a habitual way to "
    "link two clauses. Default to a comma, colon, or rephrase first. When "
    "used, write a real em-dash, never a \"--\" placeholder. In LLM "
    "system-prompt content specs, avoid entirely.\n"
    "- No coined terms requiring a glossary in any output string.\n"
)

# ── CLAUDE.md edit 2: version cross-reference ───────────────────────────────

CLAUDE_ANCHOR_2 = "| MOB version | v4.69 |"
CLAUDE_REPLACEMENT_2 = "| MOB version | v4.70 |"

# ── tools/_mob.txt edit 1: version header ───────────────────────────────────

MOB_ANCHOR_1 = "\\\\\\#\\\\\\# MOB v4.69"
MOB_REPLACEMENT_1 = "\\\\\\#\\\\\\# MOB v4.70"

# ── tools/_mob.txt edit 2: new Section 16 row ───────────────────────────────

MOB_ANCHOR_2 = "| **May 2026 — Session 1** | Taxonomy consolidation (108 to 47 states)"

NEW_ROW = (
    "| **July 2026 — Diagnostic Dimension Expansion, Report Depth Initiative "
    "(Tiers 1 and 4), Friction Tax architecture decisions** | Four "
    "independent threads closed out and pushed this session. "
    "**Diagnostic Dimension Expansion -- COMPLETE.** Five candidates from "
    "an earlier dimension-expansion discussion reconciled against real "
    "engine code across two rounds of Gemini reconciliation (first round "
    "contained fabricated mechanism detail caught via direct source read; "
    "second round verified clean). Decisions: trajectory (build), cascade "
    "risk (build), reversibility (parked as internal synthesis context "
    "only, not surfaced), SPOF/diffuse causation (build, output contract "
    "only -- resolution_families.py routing influence explicitly split "
    "off as a separate later decision, not done), urgency window "
    "(deferred, no real signal exists to derive it from). Ground truth "
    "and full decision record: prompts/diagnostic-dimension-expansion.md. "
    "Built and pushed: cascade_risk (f4ee405), causation_pattern "
    "(1b75a1b), trajectory (518545a), plan-doc hash update (d4e3301) -- "
    "all private_output-nested, Path B (result/route.ts) untouched for "
    "cascade_risk and causation_pattern. Calibration held 169/172 "
    "throughout. **Report Depth Initiative Tier 1 -- COMPLETE, Tier 2 "
    "retroactively CLOSED.** Plan doc: prompts/report-depth-initiative.md. "
    "Tier 1 (render already-computed synthesis.framing_text/"
    "observable_indicators, secondary_states acknowledgment, "
    "primary_asset_domain payload fix threaded through Path 1 and Path B) "
    "built and pushed: 3710f37 (build), 71dbb41 (plan doc update). Tier 2 "
    "(compute_causation_pattern/compute_cascade_risk wiring) was already "
    "satisfied by the Diagnostic Dimension Expansion work above, noted in "
    "the plan doc ahead of this initiative's own sequencing. Tier 4's "
    "per-state prose and resolution-family copy NOT started. **Report "
    "Depth Tier 4: headline field -- COMPLETE.** New synthesis.headline "
    "field (8th field), private and shareable, board-safe register. "
    "Content spec approved after two rounds of live content-quality "
    "testing (first pass found a severity-tier language collision -- "
    "Emerging and Endemic both drifting to Entrenched's \"settled\" "
    "framing -- fixed by giving each tier its own distinct anchor "
    "vocabulary plus an explicit anti-repetition instruction; re-test "
    "confirmed zero overlap across tiers). Built and pushed: a0981e0 "
    "(Python core -- system prompt, SynthesisResult, "
    "fallback_synthesis.py, contract.py; correct constant is "
    "_SYNTHESIS_FIELDS, not _PRIVATE_OUTPUT_FIELDS), 2a0bc77 (web layer "
    "-- types.ts, engine-client.ts, both private route builders, "
    "share/create/route.ts, both render components). Calibration held "
    "169/172 throughout. Remaining: 57-state descriptive prose, 4 "
    "resolution-family \"COPY PENDING\" blurbs, visual/layout treatment "
    "-- all NOT started. **Friction tax (Report Depth Tier 3) -- "
    "architecture fully decided, nothing built.** Four durable decision "
    "docs committed and pushed, no code changes: "
    "prompts/friction-tax-unit-decision.md (payroll-based not "
    "revenue-based units; two comment-only edits landed in "
    "engine/friction_tax.py, commit 820ded6), "
    "prompts/friction-tax-band-segmentation.md (band_low segmented by "
    "headcount x industry, org_type as a secondary modifier not a third "
    "axis; also logged -- _ORG_SIZE_BANDS's legacy keys don't match "
    "IntakeData.headcount's real values, commit f5fe432), "
    "prompts/friction-tax-client-copy.md (approved short/long "
    "client-facing explanation copy, held in reserve, neither placement "
    "exists yet, commit c28d64b), "
    "prompts/friction-tax-architecture-decision.md (full approved "
    "architecture -- composite tuple-keyed "
    "Dict[Tuple[str, str], PayrollBaselineEntry] registry, 54 cells "
    "(6 real IntakeData.headcount buckets x 9 IntakeData.industry "
    "categories, retiring legacy band keys), ORG_TYPE_SCALARS as a "
    "standalone multiplicative scalar table (6 values) applied to the "
    "grid lookup result, compute_friction_tax() signature to gain "
    "industry/org_type params, commit 3fed318). Verified against real "
    "code before this decision was written: multi-state averaging logic "
    "(arithmetic mean across state_ids, friction_tax.py:185-206) "
    "confirmed accurate; zero live pipeline call sites today (only 4 "
    "test calls in tools/test_friction_tax.py, none exercising "
    "multi-element state_ids -- flagged as a test-coverage gap to close "
    "during implementation). Next steps, not yet started: the actual "
    "code restructure, and real benchmark research to populate 54 grid "
    "cells + 6 org_type scalars + 57 STATE_MULTIPLIERS values (likely a "
    "Gemini research pass, independently verified per standing "
    "discipline). **Standing rule added this session, finalized as a new "
    "CLAUDE.md Standing Rules bullet (not a P-##):** checked the full "
    "P-01 through P-12 Governing Principles set for overlap first -- "
    "P-10 (brand voice) was the closest candidate but doesn't cover "
    "punctuation or connector style; CLAUDE.md's existing \"No "
    "semicolons in any string or copy.\" bullet was the better "
    "precedent, so the new rule landed alongside it instead. Final "
    "rule, tempered from an outright ban to \"permitted where earned\": "
    "no em-dashes as default connective tissue, permitted only for a "
    "genuine interruption or pivot a comma/colon/rephrase can't do as "
    "well, a real em-dash when used (never a \"--\" placeholder), "
    "avoided entirely in LLM system-prompt content specs. Applied this "
    "session, under the interim stricter standard in effect at the "
    "time, to the headline field's system prompt (5 pre-existing "
    "field-spec labels corrected) and to all four friction-tax decision "
    "docs -- both remain consistent with the final tempered rule (the "
    "system prompt is exactly the \"avoid entirely\" case; the "
    "friction-tax copy has no interruption/pivot use that would have "
    "earned an em-dash under the final standard either). **Open items "
    "carried forward, unchanged:** /diagnostic reskin Stage 3-5 scope "
    "gap, still unresolved, no surviving durable plan doc found; "
    "causation_pattern's resolution_families.py routing influence, "
    "split off this session, still not started, no durable scoping doc "
    "exists yet. CLAUDE.md MOB version cross-reference updated "
    "v4.69->v4.70. MOB version bumped to v4.70 -- three new engine "
    "output fields, a completed report-depth tier, four new "
    "friction-tax locked decisions, and a new standing rule all warrant "
    "a bump per the closeout protocol. MOB v4.70. |\n"
)

MOB_REPLACEMENT_2 = NEW_ROW + MOB_ANCHOR_2


def _apply(text: str, anchor: str, replacement: str, label: str) -> str:
    count = text.count(anchor)
    if count == 0:
        print(f"ABORT -- anchor not found: {label}", file=sys.stderr)
        sys.exit(1)
    if count > 1:
        print(f"ABORT -- anchor not unique ({count} matches): {label}", file=sys.stderr)
        sys.exit(1)
    return text.replace(anchor, replacement)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    claude_text = CLAUDE_MD.read_text(encoding="utf-8")
    mob_text = MOB_FILE.read_text(encoding="utf-8")

    claude_text = _apply(claude_text, CLAUDE_ANCHOR_1, CLAUDE_REPLACEMENT_1, "CLAUDE.md Standing Rules bullet")
    claude_text = _apply(claude_text, CLAUDE_ANCHOR_2, CLAUDE_REPLACEMENT_2, "CLAUDE.md MOB version cross-reference")
    mob_text = _apply(mob_text, MOB_ANCHOR_1, MOB_REPLACEMENT_1, "tools/_mob.txt version header")
    mob_text = _apply(mob_text, MOB_ANCHOR_2, MOB_REPLACEMENT_2, "tools/_mob.txt Session 16 new row")

    print("All 4 anchors found and unique. Changes:")
    print("=" * 72)
    print("1. CLAUDE.md -- new Standing Rules bullet (em-dash rule)")
    print("2. CLAUDE.md -- MOB version v4.69 -> v4.70")
    print("3. tools/_mob.txt -- header MOB v4.69 -> v4.70")
    print("4. tools/_mob.txt -- new Section 16 row (Diagnostic Dimension")
    print("   Expansion / Report Depth Tiers 1+4 / Friction Tax architecture)")
    print("=" * 72)

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    CLAUDE_MD.write_text(claude_text, encoding="utf-8")
    MOB_FILE.write_text(mob_text, encoding="utf-8")
    print("\nWROTE CLAUDE.md")
    print("WROTE tools/_mob.txt")


if __name__ == "__main__":
    main()
