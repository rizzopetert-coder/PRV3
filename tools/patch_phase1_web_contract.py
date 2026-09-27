"""
Phase 1 (report redesign), commit 5: web contract additions (Pete,
2026-09-27). Additive only: every new field is optional, so every existing
payload builder, fixture, and test compiles unchanged. No component renders
any of it until Phase 3; diagnostic-completion.ts passes the engine's new
fields through so they reach the client payload (needed for live
verification, and for Phase 3).

web/lib/types.ts
  - SynthesisFields.executive_summary?: string
  - EvidenceReceipt {category, rationale, triggering_answer?}
  - FrictionTaxEstimate / LegalTailRiskExposure: driving_factors?: EvidenceReceipt[]
  - TacticalFlaggedItem, TacticalFinding {section_id, section_name,
    flagged_count, total_count, synthesis_text, flagged_items[]}
  - AssetEvidence {strongest_axes[], contributing_signals[], net_scores}
  - ServiceCostComparison {target_service_name, inaction_cost_low/high,
    service_estimate_low/high (nullable), pricing_model_note}
  - QualifiedStateEntry
  - PrivateOutputPayload: asset_evidence?, service_cost_comparison?,
    tactical_findings?, all_qualified_states?
web/lib/engine-client.ts   EngineResult mirrors the engine's new keys.
web/lib/diagnostic-completion.ts   pass-through; asset_evidence stays absent
  (not {}) when the engine omits it.

Usage:
    python tools/patch_phase1_web_contract.py --dry-run
    python tools/patch_phase1_web_contract.py --write
"""
import argparse
import pathlib
import sys

TY = pathlib.Path('web/lib/types.ts')
EC = pathlib.Path('web/lib/engine-client.ts')
DC = pathlib.Path('web/lib/diagnostic-completion.ts')

NEW_TYPES = '''
// ---------------------------------------------------------------------------
// Phase 1 report redesign (2026-09-27) -- engine data for Phase 3. Nothing
// renders these yet. See tools/patch_phase1_*.py for the engine side.
// ---------------------------------------------------------------------------

// One step of "show your work". triggering_answer is present only when the
// respondent's answer has authored observation_text -- never raw option text.
export interface EvidenceReceipt {
  category: string;
  rationale: string;
  triggering_answer?: string;
}

export interface TacticalFlaggedItem {
  question_id: string;
  option_id: string;
  severity: "minor" | "severe";
  question_text: string;
}

// One TC-* section. synthesis_text is "" for a section with no gaps.
export interface TacticalFinding {
  section_id: string;
  section_name: string;
  flagged_count: number;
  total_count: number;
  synthesis_text: string;
  flagged_items: TacticalFlaggedItem[];
}

export type AssetAxis = "aptitude" | "authority" | "alliance" | "attitude";

// Absent entirely (never {}) when every net asset score is zero.
export interface AssetEvidence {
  strongest_axes: AssetAxis[];
  contributing_signals: Array<{ axis: AssetAxis; observation_text: string }>;
  net_scores: Record<AssetAxis, number>;
}

// Service estimates stay null until pricing exists (parked decision).
export interface ServiceCostComparison {
  target_service_name: string;
  inaction_cost_low: number | null;
  inaction_cost_high: number | null;
  service_estimate_low: number | null;
  service_estimate_high: number | null;
  pricing_model_note: string;
}

// Every above-floor state, score-descending, in single and multi mode.
export interface QualifiedStateEntry {
  state_id: string;
  state_name: string;
  score: number;
  descriptive_prose: string;
}
'''

EDITS = {
    TY: [
        ('  synthesis_confidence:         number;\n'
         '  is_fallback:                  boolean;\n'
         '}\n'
         '\n'
         '// Airgap enforced',
         '  synthesis_confidence:         number;\n'
         '  is_fallback:                  boolean;\n'
         '  // Phase 1 Call 3. "" or absent when skipped or failed.\n'
         '  executive_summary?:           string;\n'
         '}\n'
         '\n'
         '// Airgap enforced',
         'SynthesisFields.executive_summary'),
        ('export interface FrictionTaxEstimate {\n'
         '  low: number;\n'
         '  high: number;\n'
         '  currency: string;\n'
         '}\n',
         'export interface FrictionTaxEstimate {\n'
         '  low: number;\n'
         '  high: number;\n'
         '  currency: string;\n'
         '  // Phase 1 show-your-work (engine: _friction_driving_factors()).\n'
         '  driving_factors?: EvidenceReceipt[];\n'
         '}\n',
         'FrictionTaxEstimate.driving_factors'),
        ('  specific_caveat: string | null;\n'
         '}\n',
         '  specific_caveat: string | null;\n'
         '  // Phase 1 show-your-work (engine: _legal_driving_factors()).\n'
         '  driving_factors?: EvidenceReceipt[];\n'
         '}\n',
         'LegalTailRiskExposure.driving_factors'),
        ('  primary_asset_domain: string;\n'
         '}\n',
         '  primary_asset_domain: string;\n'
         '\n'
         '  // Phase 1 report redesign -- optional, not rendered until Phase 3.\n'
         '  asset_evidence?: AssetEvidence;\n'
         '  service_cost_comparison?: ServiceCostComparison;\n'
         '  tactical_findings?: TacticalFinding[];\n'
         '  all_qualified_states?: QualifiedStateEntry[];\n'
         '}\n',
         'PrivateOutputPayload additions'),
    ],
    EC: [
        ('import type {\n'
         '  PrivateIntakeEcho, FrictionTaxEstimate, FrictionTaxLedgerEntry, LegalTailRiskExposure,\n'
         '} from "@/lib/types";\n',
         'import type {\n'
         '  PrivateIntakeEcho, FrictionTaxEstimate, FrictionTaxLedgerEntry, LegalTailRiskExposure,\n'
         '  AssetEvidence, ServiceCostComparison, TacticalFinding, QualifiedStateEntry,\n'
         '} from "@/lib/types";\n',
         'imports'),
        ('      response_window: "Extended" | "Near-Term" | "Immediate" | null;\n'
         '    };\n'
         '  };\n'
         '  shareable_output: {\n',
         '      response_window: "Extended" | "Near-Term" | "Immediate" | null;\n'
         '    };\n'
         '    // Phase 1 report redesign (engine/contract.py).\n'
         '    asset_evidence?: AssetEvidence;\n'
         '    service_cost_comparison?: ServiceCostComparison;\n'
         '    tactical_findings?: TacticalFinding[];\n'
         '    all_qualified_states?: QualifiedStateEntry[];\n'
         '  };\n'
         '  shareable_output: {\n',
         'EngineResult.private_output additions'),
        ('    parse_error?:                 string | null;\n'
         '  } | null;\n',
         '    parse_error?:                 string | null;\n'
         '    // Phase 1 Call 3 (engine/exec_summary.py).\n'
         '    executive_summary?:           string;\n'
         '  } | null;\n',
         'EngineResult.synthesis.executive_summary'),
    ],
    DC: [
        ('        synthesis_confidence:         engSynthesis.synthesis_confidence,\n'
         '        is_fallback:                  engSynthesis.is_fallback,\n'
         '      }\n',
         '        synthesis_confidence:         engSynthesis.synthesis_confidence,\n'
         '        is_fallback:                  engSynthesis.is_fallback,\n'
         '        executive_summary:            engSynthesis.executive_summary ?? "",\n'
         '      }\n',
         'executive_summary pass-through'),
        ('        synthesis_confidence:         0.0,\n'
         '        is_fallback:                  true,\n'
         '      };\n',
         '        synthesis_confidence:         0.0,\n'
         '        is_fallback:                  true,\n'
         '        executive_summary:            "",\n'
         '      };\n',
         'executive_summary on the no-synthesis path'),
        ('    primary_asset_domain: engineResult.asset_score.primary_asset_domain,\n'
         '  };\n',
         '    primary_asset_domain: engineResult.asset_score.primary_asset_domain,\n'
         '\n'
         '    // Phase 1 report redesign: passed through, not rendered until Phase 3.\n'
         '    // asset_evidence stays absent (not {}) when the engine omits it.\n'
         '    ...(engineResult.private_output.asset_evidence\n'
         '      ? { asset_evidence: engineResult.private_output.asset_evidence }\n'
         '      : {}),\n'
         '    ...(engineResult.private_output.service_cost_comparison\n'
         '      ? { service_cost_comparison: engineResult.private_output.service_cost_comparison }\n'
         '      : {}),\n'
         '    tactical_findings: engineResult.private_output.tactical_findings ?? [],\n'
         '    all_qualified_states: engineResult.private_output.all_qualified_states ?? [],\n'
         '  };\n',
         'payload pass-through'),
    ],
}


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()
    out = {}
    for path, edits in EDITS.items():
        t = path.read_text(encoding='utf-8')
        for old, new, label in edits:
            n = t.count(old)
            if n != 1:
                print(f'ERROR: {path} :: {label} anchor found {n} times.', file=sys.stderr)
                sys.exit(1)
            t = t.replace(old, new, 1)
            print(f'[{path} :: {label}] OK')
        out[path] = t
    if 'export interface EvidenceReceipt' in out[TY]:
        print('ERROR: types already present.', file=sys.stderr)
        sys.exit(1)
    out[TY] = out[TY].rstrip('\n') + '\n' + NEW_TYPES
    print(f'[{TY} :: new types appended] OK')
    if args.dry_run:
        print('DRY RUN -- nothing written.')
        return
    for path, t in out.items():
        path.write_text(t, encoding='utf-8')
        print(f'WROTE: {path}')


if __name__ == '__main__':
    main()
