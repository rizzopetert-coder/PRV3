"""
hr-dx "About this report" drawer copy + Executive Advisory AI context
(Pete-approved copy, 2026-09-27).

1. Drawer copy. Four family-specific texts replace the generic fallback on
   hr_diagnostic. The page could not tell families apart -- F/I/J
   deliberately set resolution_family/resolution_routing to "HR Consulting"
   for hr_diagnostic -- so the payload gains a neutral `hr_pathway`
   ("structure" | "capability" | "leadership" | "urgent"), computed
   server-side for hr_diagnostic only (web/lib/resolution-family.ts
   hrPathwayForRouting). Compounds use the same priority as the backup copy:
   urgent (Intervention) > first of capability/leadership in order >
   structure. Copy lives in web/data/results-pathway-detail-hr.ts, loaded
   only by the (already code-split) ResultsOrientationHR.

2. Executive Advisory AI context -> plain "HR Consulting" (the "through
   Employee Development, Coaching & Performance Management" reference
   dropped). Training & Development keeps its reference.

   Consequence handled here: the hr backup-copy table was keyed by the
   context string, and Executive Advisory's string now equals People
   Tactics & Strategy's ("HR Consulting") while their backup copy differs --
   _build_hr_fallback_by_context() would raise at import. The lookup is now
   keyed by engine family instead: synthesize(..., fallback_key=...) with
   `hr_diagnostic::<engine family>` from main.py; get_fallback_synthesis()
   resolves that prefix via hr_diagnostic_fallback_copy(). The compound
   priority list is now explicit (_HR_DIAGNOSTIC_SPECIALTY_PRIORITY) instead
   of inferred from which families carry a reference, so backup selection
   is unchanged. The approved Executive Advisory BACKUP copy itself is
   untouched.

Usage:
    python tools/patch_hr_drawer_copy_and_ea_context.py --dry-run
    python tools/patch_hr_drawer_copy_and_ea_context.py --write
"""
import argparse
import pathlib
import sys

NEW_FILES = {
    pathlib.Path('web/data/results-pathway-detail-hr.ts'): '''import type { HrPathway } from "@/lib/types";

// hr_diagnostic "About this report" drawer details, keyed by the neutral
// hr_pathway the server computes (web/lib/resolution-family.ts
// hrPathwayForRouting). Pete-approved copy, 2026-09-27. Imported only by
// ResultsOrientationHR.tsx (code-split, hr_diagnostic only). No PR service
// tier names -- hr-dx must never download those.
export const RESULTS_PATHWAY_DETAIL_HR: Record<HrPathway, string> = {
  structure:
    "This pathway addresses how the organization is structured to operate, not just the people currently working within it. HR Consulting looks at where decision rights, role clarity, and reporting lines interact with what this diagnostic found, and builds a plan from there.",
  capability:
    "This pathway addresses a capability gap the diagnostic surfaced. HR Consulting, through Employee Training & Education and Learning & Development Consulting, builds a plan targeted at what was actually found, not a generic curriculum.",
  leadership:
    "This pathway centers on decisions that sit at the leadership level. HR Consulting brings an outside perspective to those decisions and practical support in acting on them.",
  urgent:
    "This pathway is for something that needs attention now, not on the usual planning cycle. HR Consulting can engage directly and quickly, working alongside leadership on what the diagnostic found before it develops further.",
};
''',
    pathlib.Path('web/components/ResultsOrientationHR.tsx'): '''"use client";

import ContextOrientation from "@/components/ContextOrientation";
import { getResultsOrientation } from "@/data/orientation-copy";
import { RESULTS_PATHWAY_DETAIL_HR } from "@/data/results-pathway-detail-hr";
import type { HrPathway, SeverityTier } from "@/lib/types";

// hr_diagnostic "About this report" drawer. Details come from the neutral
// hr_pathway (server-computed, no PR tier names); absent pathway (empty
// routing) falls back to orientation-copy.ts's generic
// RESULTS_FAMILY_DETAIL_FALLBACK. Loaded via next/dynamic from
// PrivateOutput.tsx only when brand is hr_diagnostic.
export default function ResultsOrientationHR({
  topic,
  severity,
  pathway,
}: {
  topic: string;
  severity: SeverityTier;
  pathway?: HrPathway;
}) {
  return (
    <ContextOrientation
      variant="inline"
      topic={topic}
      {...getResultsOrientation(severity, pathway ? RESULTS_PATHWAY_DETAIL_HR[pathway] : undefined)}
    />
  );
}
''',
}

EDITS = [
    # ── engine/resolution_families.py ─────────────────────────────────────────
    ('engine/resolution_families.py',
     'HR_DIAGNOSTIC_FAMILY_REFERENCES: dict[str, str] = {\n'
     '    "Development":       "Employee Training & Education and Learning & Development Consulting",\n'
     '    "Executive Counsel": "Employee Development, Coaching & Performance Management",\n'
     '}\n'
     '\n'
     '_HR_DIAGNOSTIC_URGENT_FAMILY = "Intervention"\n'
     '_HR_DIAGNOSTIC_KNOWN_FAMILIES = ("Roadmap", "Development", "Intervention", "Executive Counsel")\n',
     '# Service references carried into the AI synthesis context. Executive\n'
     '# Counsel\'s reference was dropped 2026-09-27 (Pete) -- it now reads plain\n'
     '# "HR Consulting", matching the drawer copy. Development keeps its own.\n'
     'HR_DIAGNOSTIC_FAMILY_REFERENCES: dict[str, str] = {\n'
     '    "Development":       "Employee Training & Education and Learning & Development Consulting",\n'
     '}\n'
     '\n'
     '_HR_DIAGNOSTIC_URGENT_FAMILY = "Intervention"\n'
     '_HR_DIAGNOSTIC_KNOWN_FAMILIES = ("Roadmap", "Development", "Intervention", "Executive Counsel")\n'
     '# Compound priority for backup copy (and the web drawer\'s hr_pathway,\n'
     '# mirrored in web/lib/resolution-family.ts): Intervention first, then the\n'
     '# first of these in order, then the first part. Explicit -- not inferred\n'
     '# from which families carry a context reference.\n'
     '_HR_DIAGNOSTIC_SPECIALTY_PRIORITY = ("Development", "Executive Counsel")\n',
     'references + priority'),
    ('engine/resolution_families.py',
     '    for p in parts:\n'
     '        if p in HR_DIAGNOSTIC_FAMILY_REFERENCES:\n'
     '            return HR_DIAGNOSTIC_FALLBACK_COPY[p]\n'
     '    return HR_DIAGNOSTIC_FALLBACK_COPY[parts[0]]\n',
     '    for p in parts:\n'
     '        if p in _HR_DIAGNOSTIC_SPECIALTY_PRIORITY:\n'
     '            return HR_DIAGNOSTIC_FALLBACK_COPY[p]\n'
     '    return HR_DIAGNOSTIC_FALLBACK_COPY[parts[0]]\n',
     'explicit priority'),
    ('engine/resolution_families.py',
     'def _build_hr_fallback_by_context() -> dict[str, str]:\n'
     '    # Keyed by the exact context string synthesize() receives, so\n'
     '    # get_fallback_synthesis() can resolve it without a brand parameter.\n'
     '    # Every ordered combination of distinct known families (lengths 1-4),\n'
     '    # so any compound the taxonomy or a causation override produces is\n'
     '    # covered. Two engine strings can share a context string (e.g. Roadmap\n'
     '    # + Intervention / Intervention + Roadmap) -- asserted to map to the\n'
     '    # same copy, never silently overwritten.\n'
     '    from itertools import permutations\n'
     '    table: dict[str, str] = {}\n'
     '    for n in range(1, len(_HR_DIAGNOSTIC_KNOWN_FAMILIES) + 1):\n'
     '        for combo in permutations(_HR_DIAGNOSTIC_KNOWN_FAMILIES, n):\n'
     '            engine_str = " + ".join(combo)\n'
     '            ctx = hr_diagnostic_synthesis_family(engine_str)\n'
     '            copy = hr_diagnostic_fallback_copy(engine_str)\n'
     '            existing = table.get(ctx)\n'
     '            if existing is not None and existing != copy:\n'
     '                raise ValueError(f"hr_diagnostic fallback conflict for context {ctx!r}")\n'
     '            table[ctx] = copy\n'
     '    return table\n'
     '\n'
     '\n'
     'HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT: dict[str, str] = _build_hr_fallback_by_context()\n',
     '# Backup-copy lookup key for hr_diagnostic, passed to synthesize() as\n'
     '# fallback_key. Keyed by ENGINE family, not by the AI context string:\n'
     '# since 2026-09-27 different families share a context string (Roadmap and\n'
     '# Executive Counsel both read "HR Consulting") but keep distinct backup\n'
     '# copy. get_fallback_synthesis() resolves the prefix.\n'
     'HR_DIAGNOSTIC_FALLBACK_KEY_PREFIX = "hr_diagnostic::"\n'
     '\n'
     '\n'
     'def hr_diagnostic_fallback_key(engine_family_str: str) -> str:\n'
     '    return HR_DIAGNOSTIC_FALLBACK_KEY_PREFIX + engine_family_str\n',
     'key-based lookup replaces context table'),

    # ── engine/data/fallback_synthesis.py ─────────────────────────────────────
    ('engine/data/fallback_synthesis.py',
     '    _FALLBACK_GENERIC,\n    HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT,\n)\n',
     '    _FALLBACK_GENERIC,\n    HR_DIAGNOSTIC_FALLBACK_KEY_PREFIX,\n    hr_diagnostic_fallback_copy,\n)\n',
     'imports'),
    ('engine/data/fallback_synthesis.py',
     '    hr_copy = HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT.get(commercial_name)\n'
     '    if hr_copy is not None:\n'
     '        return _make_entry(hr_copy)\n',
     '    if commercial_name.startswith(HR_DIAGNOSTIC_FALLBACK_KEY_PREFIX):\n'
     '        hr_copy = hr_diagnostic_fallback_copy(commercial_name[len(HR_DIAGNOSTIC_FALLBACK_KEY_PREFIX):])\n'
     '        return _make_entry(hr_copy) if hr_copy else _FALLBACK_GENERIC_ENTRY\n',
     'hr key lookup'),

    # ── engine/output_synthesis.py ────────────────────────────────────────────
    ('engine/output_synthesis.py',
     '    model: str = "claude-sonnet-5",\n    client=None,\n    timeout: float = 15.0,\n) -> SynthesisResult:\n',
     '    model: str = "claude-sonnet-5",\n    client=None,\n    timeout: float = 15.0,\n'
     '    # Backup-copy lookup key when it must differ from the AI context string\n'
     '    # (hr_diagnostic: engine/resolution_families.hr_diagnostic_fallback_key).\n'
     '    fallback_key: str | None = None,\n'
     ') -> SynthesisResult:\n',
     'synthesize fallback_key param'),
    ('engine/output_synthesis.py',
     '    if intake is None:\n        intake = {}\n',
     '    if intake is None:\n        intake = {}\n    fb_key = fallback_key or resolution_family\n',
     'fb_key'),
    ('engine/output_synthesis.py',
     '    except ImportError:\n        fb = get_fallback_synthesis(resolution_family, severity_tier)\n',
     '    except ImportError:\n        fb = get_fallback_synthesis(fb_key, severity_tier)\n',
     'import-error fallback'),
    ('engine/output_synthesis.py',
     '    except Exception as e:\n        fb = get_fallback_synthesis(resolution_family, severity_tier)\n',
     '    except Exception as e:\n        fb = get_fallback_synthesis(fb_key, severity_tier)\n',
     'api-error fallback'),
    ('engine/output_synthesis.py',
     '    return _parse_synthesis_response(response_text, resolution_family, severity_tier)\n',
     '    return _parse_synthesis_response(response_text, fb_key, severity_tier)\n',
     'parse fallback'),
    ('engine/output_synthesis.py',
     '        signal_map_context: str = "",\n        timeout: float = 15.0,\n    ) -> SynthesisResult:\n'
     '        """Run synthesis and store result for downstream access."""\n',
     '        signal_map_context: str = "",\n        timeout: float = 15.0,\n        fallback_key: str | None = None,\n'
     '    ) -> SynthesisResult:\n'
     '        """Run synthesis and store result for downstream access."""\n',
     'engine method param'),
    ('engine/output_synthesis.py',
     '            client=self._client,\n            timeout=timeout,\n        )\n        return self.result\n',
     '            client=self._client,\n            timeout=timeout,\n            fallback_key=fallback_key,\n'
     '        )\n        return self.result\n',
     'engine method pass-through'),

    # ── engine/main.py ────────────────────────────────────────────────────────
    ('engine/main.py',
     '    hr_diagnostic_synthesis_family,\n)\n',
     '    hr_diagnostic_synthesis_family,\n    hr_diagnostic_fallback_key,\n)\n',
     'main import'),
    ('engine/main.py',
     '            resolution_family=commercial_family,\n'
     '            asset_score=asset_obj["score"],\n'
     '            liability_score=liability_obj["score"],\n'
     '            narrative_response=narrative_response,\n'
     '            intake=intake,\n'
     '            signal_map_context=signal_map_context,\n'
     '        )\n',
     '            resolution_family=commercial_family,\n'
     '            asset_score=asset_obj["score"],\n'
     '            liability_score=liability_obj["score"],\n'
     '            narrative_response=narrative_response,\n'
     '            intake=intake,\n'
     '            signal_map_context=signal_map_context,\n'
     '            fallback_key=(\n'
     '                hr_diagnostic_fallback_key(engine_family)\n'
     '                if brand == "hr_diagnostic" else None\n'
     '            ),\n'
     '        )\n',
     'main passes fallback_key'),

    # ── web/lib/types.ts ──────────────────────────────────────────────────────
    ('web/lib/types.ts',
     '  resolution_routing: string; // human-readable routing description\n',
     '  resolution_routing: string; // human-readable routing description\n'
     '  // hr_diagnostic only: neutral pathway key for the "About this report"\n'
     '  // drawer (resolution_family is "HR Consulting" for every family there).\n'
     '  hr_pathway?: HrPathway;\n',
     'payload hr_pathway'),
    ('web/lib/types.ts',
     'export type ResolutionFamily = SingleResolutionFamily | (string & {});\n',
     'export type ResolutionFamily = SingleResolutionFamily | (string & {});\n'
     '\n'
     '// hr_diagnostic drawer pathway -- neutral, never a PR tier name.\n'
     'export type HrPathway = "structure" | "capability" | "leadership" | "urgent";\n',
     'HrPathway type'),

    # ── web/lib/resolution-family.ts ──────────────────────────────────────────
    ('web/lib/resolution-family.ts',
     'import type { ResolutionFamily } from "@/lib/types";\n',
     'import type { HrPathway, ResolutionFamily } from "@/lib/types";\n',
     'import HrPathway'),
    ('web/lib/resolution-family.ts',
     'export const HR_DIAGNOSTIC_RESOLUTION_FAMILY: ResolutionFamily = "HR Consulting";\n',
     'export const HR_DIAGNOSTIC_RESOLUTION_FAMILY: ResolutionFamily = "HR Consulting";\n'
     '\n'
     '// hr_diagnostic drawer pathway from the raw engine routing. Same compound\n'
     '// priority as the hr backup copy (engine/resolution_families.py\n'
     '// _HR_DIAGNOSTIC_SPECIALTY_PRIORITY): Intervention first, then the first\n'
     '// of Development / Executive Counsel in order, then the first part.\n'
     '// Unknown or empty routing -> undefined (drawer uses its generic text).\n'
     'const HR_PATHWAY_BY_ENGINE_FAMILY: Record<string, HrPathway> = {\n'
     '  Roadmap: "structure",\n'
     '  Development: "capability",\n'
     '  "Executive Counsel": "leadership",\n'
     '  Intervention: "urgent",\n'
     '};\n'
     '\n'
     'export function hrPathwayForRouting(engineFamilyStr: string): HrPathway | undefined {\n'
     '  const parts = engineFamilyStr\n'
     '    .split(" + ")\n'
     '    .map((p) => p.trim())\n'
     '    .filter((p) => p in HR_PATHWAY_BY_ENGINE_FAMILY);\n'
     '  if (parts.length === 0) return undefined;\n'
     '  if (parts.includes("Intervention")) return "urgent";\n'
     '  const specialty = parts.find((p) => p === "Development" || p === "Executive Counsel");\n'
     '  return HR_PATHWAY_BY_ENGINE_FAMILY[specialty ?? parts[0]];\n'
     '}\n',
     'hrPathwayForRouting'),

    # ── web/lib/diagnostic-completion.ts ──────────────────────────────────────
    ('web/lib/diagnostic-completion.ts',
     '  HR_DIAGNOSTIC_RESOLUTION_FAMILY,\n} from "@/lib/resolution-family";\n',
     '  HR_DIAGNOSTIC_RESOLUTION_FAMILY,\n  hrPathwayForRouting,\n} from "@/lib/resolution-family";\n',
     'import hrPathwayForRouting'),
    ('web/lib/diagnostic-completion.ts',
     '    resolution_routing: isHrDiagnostic\n'
     '      ? (rawRouting ? HR_DIAGNOSTIC_RESOLUTION_FAMILY : "")\n'
     '      : rawRouting,\n',
     '    resolution_routing: isHrDiagnostic\n'
     '      ? (rawRouting ? HR_DIAGNOSTIC_RESOLUTION_FAMILY : "")\n'
     '      : rawRouting,\n'
     '    ...(isHrDiagnostic ? { hr_pathway: hrPathwayForRouting(rawRouting) } : {}),\n',
     'payload sets hr_pathway'),

    # ── web/components/PrivateOutput.tsx ──────────────────────────────────────
    ('web/components/PrivateOutput.tsx',
     '          <ResultsOrientationHR topic="output-private" severity={payload.severity} />\n',
     '          <ResultsOrientationHR\n'
     '            topic="output-private"\n'
     '            severity={payload.severity}\n'
     '            pathway={payload.hr_pathway}\n'
     '          />\n',
     'pass pathway'),

    # ── vitest ────────────────────────────────────────────────────────────────
    ('web/lib/diagnostic-completion-brand.test.ts',
     '      const blob = `${result.resolution_family} ${result.resolution_routing}`;\n'
     '      for (const t of PR_TERMS) expect(blob).not.toContain(t);\n'
     '    });\n'
     '  }\n',
     '      const blob = `${result.resolution_family} ${result.resolution_routing}`;\n'
     '      for (const t of PR_TERMS) expect(blob).not.toContain(t);\n'
     '      expect(result.hr_pathway).toBe(EXPECTED_PATHWAY[routing]);\n'
     '    });\n'
     '  }\n'
     '\n'
     '  it("principal_resolution payload carries no hr_pathway", async () => {\n'
     '    const result = await run("principal_resolution", "Intervention + Roadmap");\n'
     '    expect(result.hr_pathway).toBeUndefined();\n'
     '  });\n',
     'vitest hr_pathway assertions'),
    ('web/lib/diagnostic-completion-brand.test.ts',
     '  const ROUTINGS = [',
     '  // Same compound priority as the hr backup copy: urgent first, then the\n'
     '  // first of capability/leadership, then structure.\n'
     '  const EXPECTED_PATHWAY: Record<string, string> = {\n'
     '    Roadmap: "structure",\n'
     '    Development: "capability",\n'
     '    Intervention: "urgent",\n'
     '    "Executive Counsel": "leadership",\n'
     '    "Intervention + Executive Counsel": "urgent",\n'
     '    "Roadmap + Intervention": "urgent",\n'
     '    "Development + Roadmap": "capability",\n'
     '  };\n'
     '\n'
     '  const ROUTINGS = [',
     'vitest expected map'),

    # ── tools/test_hr_diagnostic_brand.py ─────────────────────────────────────
    ('tools/test_hr_diagnostic_brand.py',
     '    HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT,\n    HR_DIAGNOSTIC_FALLBACK_COPY,\n)\n',
     '    hr_diagnostic_fallback_key,\n    HR_DIAGNOSTIC_FALLBACK_COPY,\n)\n',
     'test import'),
    ('tools/test_hr_diagnostic_brand.py',
     '    "Executive Counsel": "HR Consulting, through Employee Development, Coaching & Performance Management",\n',
     '    "Executive Counsel": "HR Consulting",\n',
     'pin EA context'),
    ('tools/test_hr_diagnostic_brand.py',
     'check("urgency + reference combo reads as prose",\n'
     '      hr_diagnostic_synthesis_family("Executive Counsel + Intervention")\n'
     '      == "HR Consulting on an urgent basis, through Employee Development, Coaching & Performance Management")\n'
     'check("old \'engaged immediately\' cue gone from every context string",\n'
     '      all("engaged immediately" not in c for c in HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT))\n',
     'check("Executive Advisory + urgency reads as plain urgent HR Consulting",\n'
     '      hr_diagnostic_synthesis_family("Executive Counsel + Intervention") == "HR Consulting on an urgent basis")\n'
     'check("Training & Development + urgency keeps its reference",\n'
     '      hr_diagnostic_synthesis_family("Development + Intervention")\n'
     '      == "HR Consulting on an urgent basis, through Employee Training & Education and Learning & Development Consulting")\n'
     'check("Executive Advisory reference gone from every family context string",\n'
     '      all("Coaching & Performance Management" not in hr_diagnostic_synthesis_family(f)\n'
     '          for f in {p.resolution_family for p in STATE_PROFILES.values()}))\n'
     'check("old \'engaged immediately\' cue gone from every context string",\n'
     '      all("engaged immediately" not in hr_diagnostic_synthesis_family(f)\n'
     '          for f in {p.resolution_family for p in STATE_PROFILES.values()}))\n'
     'check("shared context string, distinct backup copy (key is engine family)",\n'
     '      hr_diagnostic_synthesis_family("Roadmap") == hr_diagnostic_synthesis_family("Executive Counsel")\n'
     '      and get_fallback_synthesis(hr_diagnostic_fallback_key("Roadmap"), None)["resolution_framing_text"]\n'
     '      != get_fallback_synthesis(hr_diagnostic_fallback_key("Executive Counsel"), None)["resolution_framing_text"])\n',
     'context checks'),
    ('tools/test_hr_diagnostic_brand.py',
     '    check(f"backup copy exists for {fam!r}", ctx in HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT)\n',
     '    check(f"backup copy exists for {fam!r}",\n'
     '          get_fallback_synthesis(hr_diagnostic_fallback_key(fam), None)["resolution_framing_text"]\n'
     '          in HR_DIAGNOSTIC_FALLBACK_COPY.values())\n',
     'backup exists per family'),
    ('tools/test_hr_diagnostic_brand.py',
     'for ctx, copy in HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT.items():\n'
     '    ok = bool(copy) and not pr_hits(copy) and ";" not in copy and "\\u2014" not in copy and "HR Consulting" in copy\n'
     '    check(f"backup copy for {ctx!r}: non-empty, no PR terms, no semicolon, no em-dash", ok, copy)\n',
     'for fam_key, copy in HR_DIAGNOSTIC_FALLBACK_COPY.items():\n'
     '    ok = bool(copy) and not pr_hits(copy) and ";" not in copy and "\\u2014" not in copy and "HR Consulting" in copy\n'
     '    check(f"backup copy for {fam_key!r}: non-empty, no PR terms, no semicolon, no em-dash", ok, copy)\n',
     'content rules loop'),
    ('tools/test_hr_diagnostic_brand.py',
     '      get_fallback_synthesis(hr_diagnostic_synthesis_family("Executive Counsel + Intervention"), "Entrenched")["resolution_framing_text"]\n',
     '      get_fallback_synthesis(hr_diagnostic_fallback_key("Executive Counsel + Intervention"), "Entrenched")["resolution_framing_text"]\n',
     'urgency wins via key'),
    ('tools/test_hr_diagnostic_brand.py',
     '      get_fallback_synthesis(hr_diagnostic_synthesis_family("Roadmap + Intervention"), "Endemic")["resolution_framing_text"]\n',
     '      get_fallback_synthesis(hr_diagnostic_fallback_key("Roadmap + Intervention"), "Endemic")["resolution_framing_text"]\n',
     'corrected First Call via key'),
    ('tools/test_hr_diagnostic_brand.py',
     '          for c in HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT.values()))\n',
     '          for c in HR_DIAGNOSTIC_FALLBACK_COPY.values()))\n',
     'old clause over copy table'),
    ('tools/test_hr_diagnostic_brand.py',
     '    ctx = hr_diagnostic_synthesis_family(fam)\n'
     '    for tier in ("Emerging", "Entrenched", "Endemic", None):\n'
     '        fb = get_fallback_synthesis(ctx, tier)\n',
     '    key = hr_diagnostic_fallback_key(fam)\n'
     '    for tier in ("Emerging", "Entrenched", "Endemic", None):\n'
     '        fb = get_fallback_synthesis(key, tier)\n',
     'tier loop via key'),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    if pathlib.Path('web/data/results-pathway-detail-hr.ts').exists():
        print('ERROR: pathway copy file already exists.', file=sys.stderr)
        sys.exit(1)
    edited = {}
    for rel, old, new, label in EDITS:
        p = pathlib.Path(rel)
        t = edited.get(p, p.read_text(encoding='utf-8'))
        if t.count(old) != 1:
            print(f'ERROR: {p} :: {label} anchor found {t.count(old)} times.', file=sys.stderr)
            sys.exit(1)
        edited[p] = t.replace(old, new, 1)
        print(f'[{p} :: {label}] OK')
    for p, t in edited.items():
        if 'HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT' in t:
            print(f'ERROR: {p} still references HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT.', file=sys.stderr)
            sys.exit(1)
    for text in NEW_FILES.values():
        for bad in (';"', '\u2014', 'People Tactics', 'First Call', 'Executive Advisory', 'Training & Development'):
            if bad in text:
                print(f'ERROR: new file contains {bad!r}.', file=sys.stderr)
                sys.exit(1)
    if args.dry_run:
        print('DRY RUN -- all anchors found. Nothing written.')
        return
    for p, t in NEW_FILES.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE: {p}')
    for p, t in edited.items():
        p.write_text(t, encoding='utf-8')
        print(f'WROTE (edited): {p}')


if __name__ == '__main__':
    main()
