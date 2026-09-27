"""
Phase 2 Part A follow-up: remove code the restructure left unused.
PrivateOutput: SEVERITY_TIER_BAND + tierFillPercent (moved into
ConditionsList with the severity bars). ShareableOutput: the header accent
and its import (the name + badge header it styled is gone).

Usage: python tools/patch_phase2_unused_cleanup.py --dry-run | --write
"""
import argparse, pathlib, sys
PO = pathlib.Path('web/components/PrivateOutput.tsx')
SO = pathlib.Path('web/components/ShareableOutput.tsx')
PO_OLD = '''// Visualize Your Data (Layer 3). Mirrors engine/severity.py's
// classify_severity() CALIBRATION TARGET default boundaries (0-100
// scale; EMERGING_MAX/ENTRENCHED_MAX confirmed None/live-on-default
// at HEAD) -- same accepted mirror-drift risk SEVERITY_ANCHOR above
// already carries for SEVERITY_TIER_DESCRIPTIONS, not a new pattern.
const SEVERITY_TIER_BAND: Record<SeverityTier, { min: number; max: number }> = {
  Emerging:   { min: 0,  max: 33 },
  Entrenched: { min: 33, max: 66 },
  Endemic:    { min: 66, max: 100 },
};

function tierFillPercent(tier: SeverityTier, score: number): number {
  const { min, max } = SEVERITY_TIER_BAND[tier];
  const fraction = (score - min) / (max - min);
  return Math.max(0, Math.min(1, fraction)) * 100;
}
'''
def main():
    ap = argparse.ArgumentParser(); g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true'); g.add_argument('--write', action='store_true')
    a = ap.parse_args()
    po = PO.read_text(encoding='utf-8'); so = SO.read_text(encoding='utf-8')
    if po.count(PO_OLD) != 1: print('ERROR po', file=sys.stderr); sys.exit(1)
    po = po.replace(PO_OLD, '', 1); print('[PrivateOutput] tier band helpers removed')
    lines = so.split('\n')
    start = next(i for i, l in enumerate(lines) if l.strip().startswith('// Severity-conditional accent'))
    end = next(i for i in range(start, len(lines)) if 'const accent = severityAccentTokens' in lines[i])
    removed = lines[start:end + 1]
    del lines[start:end + 1]
    if start < len(lines) and lines[start].strip() == '' and lines[start - 1].strip() == '':
        del lines[start]
    so = '\n'.join(lines)
    imp = 'import { severityAccentTokens } from "@/components/ConstellationField";\n'
    if so.count(imp) != 1 or 'severityAccentTokens(' in so.replace(imp, ''):
        print('ERROR so import', file=sys.stderr); sys.exit(1)
    so = so.replace(imp, '', 1); print(f'[ShareableOutput] accent removed ({len(removed)} lines) + import')
    if a.dry_run: print('DRY RUN -- nothing written.'); return
    PO.write_text(po, encoding='utf-8'); SO.write_text(so, encoding='utf-8'); print('WROTE')
if __name__ == '__main__': main()
