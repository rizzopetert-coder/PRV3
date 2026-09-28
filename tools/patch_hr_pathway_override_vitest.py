"""
hr-dx drawer vs causation override (Pete, 2026-09-28): code trace only.

hr_pathway (web/lib/diagnostic-completion.ts) = hrPathwayForRouting(
engineResult.private_output.resolution_routing). The engine sets that key
from effective_resolution_routing in assemble_output (engine/contract.py),
i.e. AFTER apply_causation_override, the same value Call 1 and the backup
copy now use (79c419d). So the drawer already follows the overridden family.

This adds one vitest pinning it: an overridden result (the_uninitiated,
default Intervention = First Call, diffuse -> Development) must give
hr_pathway "capability", never "urgent" (what the pre-override Intervention
would give).

Usage: python tools/patch_hr_pathway_override_vitest.py --dry-run | --write
"""
import argparse, pathlib, sys

T = pathlib.Path('web/lib/diagnostic-completion-brand.test.ts')
ANCHOR = '''  it("principal_resolution unchanged: translated family, raw routing", async () => {'''
NEW = '''  it("hr_diagnostic: hr_pathway follows the causation-overridden routing, not the state's default family", async () => {
    // the_uninitiated defaults to Intervention (First Call, "urgent"). With a
    // diffuse pattern the engine overrides it to Development before writing
    // private_output.resolution_routing, and the narrative is written for
    // Development too. The drawer must match: "capability", not "urgent".
    const base = engineResult("Development", false);
    mockInvokeComplete.mockResolvedValueOnce({
      ...base,
      identified_states: [{ state_id: "the_uninitiated", state_name: "The Uninitiated", score: 1, descriptive_prose: "" }],
      private_output: { ...base.private_output, causation_pattern: { pattern: "diffuse", dispersion: 0.5, qualified_state_count: 1 } },
    });
    const result = (await (await completeDiagnosticSession(session("hr_diagnostic"))).json()).result;
    expect(result.hr_pathway).toBe("capability");
    expect(result.hr_pathway).not.toBe("urgent");
    expect(result.resolution_family).toBe("HR Consulting");
  });

'''

ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
a = ap.parse_args(); t = T.read_text(encoding='utf-8')
if t.count(ANCHOR) != 1:
    print(f'ERROR anchor x{t.count(ANCHOR)}', file=sys.stderr); sys.exit(1)
t = t.replace(ANCHOR, NEW + ANCHOR, 1); print(f'[{T} :: override pathway test] OK')
if a.dry_run:
    print('DRY RUN -- nothing written.')
else:
    T.write_text(t, encoding='utf-8'); print('WROTE')
