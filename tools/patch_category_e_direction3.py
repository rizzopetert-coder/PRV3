"""
PRV3 -- Category E, Direction 3 (editorial/typographic hero: cluster
display). Gemini architecture review cleared the design direction
(delta-weight bucket at 0.08, core cluster capped at 5, "+N" overflow
affordance); two of five verification-gate claims corrected before this
build (see the prior session's verification report):

1. Real component path is web/components/PrivateOutput.tsx --
   web/app/diagnostic/components/PrivateOutput.tsx (Gemini's claimed path)
   does not exist.
2. web/lib/output-renderer.ts's renderPrivateOutput() is real but has zero
   callers anywhere in the codebase -- PrivateOutput.tsx reads the raw
   PrivateOutputPayload directly, never through that view-model layer.
   Modifying it would compile clean and change nothing about what a
   respondent sees. All bucketing logic goes inline in PrivateOutput.tsx
   instead; output-renderer.ts is untouched by this patch, per Pete's
   explicit instruction not to touch, delete, or "clean up" it as part of
   this work.

Both further instances of the standing Gemini-verification-catches-real-
errors pattern already logged multiple times this project.

Font tokens: --font-display (Lora) and --font-ui (Inter) only, confirmed
real in globals.css. --font-sans exists but maps to Geist Sans, a
different typeface -- deliberately not used anywhere in this build.

secondary_states confirmed the correct, fully unfiltered source (both
Path A and Path B construction sites build it straight from the engine's
rank-sorted qualified-state list, no truncation) -- zero backend/route
changes needed, confirmed before writing this patch.

Content decision, flagged explicitly for Pete's review (beyond pure
layout): the literal per-state percentage ("(4%)") is DROPPED from the
core cluster display. Showing that number repeated 5 times was the exact
visual symptom motivating this redesign (near-identical percentages
undermining the "co-occurring" framing) -- typographic presence (real
named text, Lora, uniform "secondary" weight per Gemini's type scale)
carries the signal instead of a number that was often uninformative by
construction. Reversible if Pete wants the number back.

Edge-case verification (Gemini's own Phase 3 recommendation), pulled from
real high_confidence calibration profiles run through the actual engine
pipeline, not synthetic/invented weight arrays:
  - APT-OM-01 (n=2): weights [0.50, 0.50] -- core_cluster_size=1, overflow=0
  - EXP-IC-01 (n=25): weights 0.0411..0.0395 -- core_cluster_size=5 (cap),
    overflow=19
  - ATT-BC-01 (n=32, the real max in the 58-profile sample -- closest
    available to Pete's "~30+" ask): weights 0.0322..0.0306 --
    core_cluster_size=5 (cap), overflow=26
Logic-level verification only (bucketing membership counts, no runtime
errors at either extreme) -- this cannot confirm visual layout without a
browser, which Pete is verifying live post-push, same as Direction 1.

One observation worth flagging: in all three real edge cases, the 0.08
delta-weight threshold never excluded a state the 5-cap wouldn't have
excluded anyway. Real qualified-state raw scores cluster within the 0.05
live margin gate; after normalization (dividing by the sum of N close
scores), the resulting weight deltas shrink further as N grows, so in
practice the cap does most of the real bounding work for large clusters.
Not a bug -- a genuine property of the real distribution, noted for
Pete's awareness, not acted on (the 0.08 threshold stays as specified).

Usage:
  python tools/patch_category_e_direction3.py --dry-run
  python tools/patch_category_e_direction3.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


FILE = "web/components/PrivateOutput.tsx"

# ═══════════════════════════════════════════════════════════════════════
# Import StateRef (needed for the new helper function's type signature).
# ═══════════════════════════════════════════════════════════════════════

edit(
    FILE,
    'import type { PrivateOutputPayload, SeverityTier } from "@/lib/types";',
    'import type { PrivateOutputPayload, SeverityTier, StateRef } from "@/lib/types";',
)

# ═══════════════════════════════════════════════════════════════════════
# Core cluster bucketing helper -- module level, alongside firstSentence().
# ═══════════════════════════════════════════════════════════════════════

edit(
    FILE,
    'function firstSentence(text: string): string {\n'
    '  const match = text.match(/\\.\\s/);\n'
    '  if (!match || match.index === undefined) return text;\n'
    '  return text.slice(0, match.index + 1);\n'
    '}',
    'function firstSentence(text: string): string {\n'
    '  const match = text.match(/\\.\\s/);\n'
    '  if (!match || match.index === undefined) return text;\n'
    '  return text.slice(0, match.index + 1);\n'
    '}\n'
    '\n'
    '// Core cluster bucketing (Direction 3, Category E, this session) --\n'
    '// Gemini-reviewed design: delta-weight bucket at 0.08 of the primary\n'
    '// state\'s normalized weight, core cluster capped at 5, everything else\n'
    '// folds into a "+N co-occurring conditions" overflow count. Replaces a\n'
    '// fixed 2/3-state tier, ruled out by real distribution data (58 real\n'
    '// high_confidence profiles: median 7 qualified states, 50% displaying\n'
    '// an identical percentage -- see\n'
    '// prompts/category-e-direction3-cluster-display.md). secondary_states\n'
    '// arrives already sorted descending by weight (both construction sites\n'
    '// -- session/answer/route.ts and result/route.ts -- build it straight\n'
    '// from the engine\'s own rank-sorted rankings), so no re-sort here.\n'
    'const CORE_CLUSTER_DELTA = 0.08;\n'
    'const CORE_CLUSTER_CAP = 5;\n'
    '\n'
    'function buildCoreCluster(\n'
    '  secondaryStates: StateRef[],\n'
    '  primaryWeight: number,\n'
    '): { core: StateRef[]; overflowCount: number } {\n'
    '  const withinDelta = secondaryStates.filter(\n'
    '    (s) => primaryWeight - s.weight <= CORE_CLUSTER_DELTA,\n'
    '  );\n'
    '  const core = withinDelta.slice(0, CORE_CLUSTER_CAP);\n'
    '  return { core, overflowCount: secondaryStates.length - core.length };\n'
    '}',
)

# ═══════════════════════════════════════════════════════════════════════
# Compute the cluster inside the component body, right after `accent`.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FILE,
    '  const accent = severityAccentTokens(payload.severity);\n'
    '\n'
    '  return (',
    '  const accent = severityAccentTokens(payload.severity);\n'
    '\n'
    '  // Direction 3, this session -- see buildCoreCluster() above.\n'
    '  const { core: coreCluster, overflowCount } = buildCoreCluster(\n'
    '    payload.secondary_states,\n'
    '    payload.primary_state.weight,\n'
    '  );\n'
    '\n'
    '  return (',
)

# ═══════════════════════════════════════════════════════════════════════
# Block 1 -- hero typographic treatment + softened eyebrow copy.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FILE,
    '      {/* Block 1 — Condition header */}\n'
    '      <div className="pb-4">\n'
    '        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n'
    '          Condition identified\n'
    '        </p>\n'
    '        <div className="flex items-center gap-2 flex-wrap mb-2">\n'
    '          <span className="text-[13px] font-medium text-gray-500">\n'
    '            {payload.primary_state.name}\n'
    '          </span>',
    '      {/* Block 1 — Condition header. Hero typographic treatment\n'
    '          (Direction 3, this session): the primary condition name gets\n'
    '          the largest type in the report (font-display/Lora), replacing\n'
    '          the prior text-[13px] treatment -- still one verdict named\n'
    '          with confidence, per Output Precision. Eyebrow softened from\n'
    '          "Condition identified" (implies singularity) to "Most\n'
    '          prominent pattern" (signals rank without claiming exclusivity)\n'
    '          -- per prompts/category-e-direction3-cluster-display.md. */}\n'
    '      <div className="pb-4">\n'
    '        <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n'
    '          Most prominent pattern\n'
    '        </p>\n'
    '        <div className="flex items-center gap-3 flex-wrap mb-2">\n'
    '          <span className="font-display text-3xl font-semibold text-charcoal">\n'
    '            {payload.primary_state.name}\n'
    '          </span>',
)

# ═══════════════════════════════════════════════════════════════════════
# Block 4b -- Also present -> Core cluster + overflow affordance.
# ═══════════════════════════════════════════════════════════════════════

edit(
    FILE,
    '      {/* Block 4b — Secondary states acknowledgment (omit entirely if none) */}\n'
    '      {payload.secondary_states.length > 0 && (\n'
    '        <div className="py-4">\n'
    '          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-2">\n'
    '            Also present\n'
    '          </p>\n'
    '          <ul className="space-y-3">\n'
    '            {payload.secondary_states.map((s) => (\n'
    '              <li key={s.id}>\n'
    '                <a\n'
    '                  href={`/book/toc#${stateIdToSlug(s.id)}`}\n'
    '                  className="text-[13px] font-medium text-charcoal hover:underline"\n'
    '                >\n'
    '                  {s.name} ({(s.weight * 100).toFixed(0)}%)\n'
    '                </a>\n'
    '                {s.descriptive_prose && (\n'
    '                  <p className="text-[12px] text-gray-500 leading-relaxed mt-0.5">\n'
    '                    {firstSentence(s.descriptive_prose)}\n'
    '                  </p>\n'
    '                )}\n'
    '              </li>\n'
    '            ))}\n'
    '          </ul>',
    '      {/* Block 4b — Core cluster of co-occurring conditions (Direction\n'
    '          3, this session). Replaces the flat "Also present" bulleted\n'
    '          list (with its per-state percentage that a fixed 2/3-state\n'
    '          tier and near-uniform real weights made frequently\n'
    '          uninformative -- confirmed via real distribution data, see\n'
    '          prompts/category-e-direction3-cluster-display.md) with a\n'
    '          variable-length cluster: real typographic presence\n'
    '          (font-display/Lora, uniform "secondary" weight -- a clear step\n'
    '          down from the Block 1 hero, not graduated per member) for\n'
    '          every state in the core cluster, plus a "+N co-occurring\n'
    '          conditions" overflow affordance for the rest. Section label\n'
    '          softened from "Also present" to "Co-occurring conditions" --\n'
    '          signals real co-existence, not an afterthought footnote.\n'
    '          Percentage intentionally dropped from display -- see this\n'
    '          patch script\'s own docstring for the full rationale. */}\n'
    '      {payload.secondary_states.length > 0 && (\n'
    '        <div className="py-4">\n'
    '          <p className="text-[11px] uppercase tracking-wide text-gray-400 mb-3">\n'
    '            Co-occurring conditions\n'
    '          </p>\n'
    '          <ul className="space-y-4">\n'
    '            {coreCluster.map((s) => (\n'
    '              <li key={s.id}>\n'
    '                <a\n'
    '                  href={`/book/toc#${stateIdToSlug(s.id)}`}\n'
    '                  className="font-display text-lg text-charcoal hover:underline"\n'
    '                >\n'
    '                  {s.name}\n'
    '                </a>\n'
    '                {s.descriptive_prose && (\n'
    '                  <p className="text-[12px] text-gray-500 leading-relaxed mt-0.5">\n'
    '                    {firstSentence(s.descriptive_prose)}\n'
    '                  </p>\n'
    '                )}\n'
    '              </li>\n'
    '            ))}\n'
    '          </ul>\n'
    '          {overflowCount > 0 && (\n'
    '            <p className="font-ui text-[12px] text-gray-400 mt-3">\n'
    '              +{overflowCount} co-occurring condition{overflowCount === 1 ? "" : "s"}\n'
    '            </p>\n'
    '          )}',
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
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
