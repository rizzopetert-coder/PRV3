"""
Friction tax rebuild, Stage 3a (R2, pulled forward): gate the condensed report's
"Estimated cost of one departure in this pattern" block, and its "roughly 50-75%"
copy, behind FRICTION_DOLLARS_VISIBLE, the same constant PrivateOutput.tsx uses.
When the flag is false the whole block and its trailing divider are omitted, so no
copy is shown at all (the unavailable note would tell the reader data is missing,
which is false for a hidden figure). The visible branch is the existing markup,
unchanged. No API, payload or engine change.

Usage: python tools/patch_stage3a_condensed_hide.py --dry-run | --write
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "web/components/CondensedOutput.tsx"

EDITS = [
 ('import { formatUsdRange } from "@/lib/output-text";\n',
  'import { formatUsdRange, FRICTION_DOLLARS_VISIBLE } from "@/lib/output-text";\n'),
 ('''      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      {/* Financial benchmark. Null-path: omitted with an explicit unavailable
          note, never a broken figure, when get_industry_wage() returned None
          for an unrecognized industry (Decision Register). */}
      <div className="py-4">
''',
  '''      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      {/* Financial benchmark. Hidden while FRICTION_DOLLARS_VISIBLE is false
          (R2, friction tax rebuild): the block, its copy and its trailing
          divider are omitted entirely, no replacement text. When visible, the
          null-path shows an explicit unavailable note, never a broken figure,
          when get_industry_wage() returned None for an unrecognized industry
          (Decision Register). */}
      {FRICTION_DOLLARS_VISIBLE && (
      <>
      <div className="py-4">
'''),
 ('''      </div>

      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />

      {/* Resolution family + CTA.''',
  '''      </div>

      <div style={{ height: 0, borderTop: "0.5px solid #e5e7eb" }} />
      </>
      )}

      {/* Resolution family + CTA.'''),
]
raw = P.read_bytes().decode("utf-8"); crlf = "\r\n" in raw; t = raw.replace("\r\n", "\n")
for o, n in EDITS:
    assert t.count(o) == 1, f"anchor count {t.count(o)}: {o[:60]!r}"
    t = t.replace(o, n)
print("3 edits ok", "CRLF" if crlf else "LF")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8")); print("WROTE")
else:
    print("DRY RUN")
