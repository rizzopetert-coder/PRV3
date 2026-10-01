"""
Record the Stage 3a sequencing change (Pete, 2026-09-30) in the spec addendum's
stage map. Stage 3 changes the visible condensed figure through get_industry_wage,
so the R2 condensed hide ships first as Stage 3a. Stage 5 keeps the single-value
formula, the response shape change and the types.

Usage: python tools/patch_spec_stage3a_sequencing.py --dry-run | --write
"""
import sys
from pathlib import Path
P = Path(__file__).resolve().parents[1] / "prompts/friction-tax-rebuild-build-spec.md"
OLD = "Stage 8 = step 9 (production round-trip)."
NEW = (OLD + "\n\n**Sequencing change (Pete, 2026-09-30): Stage 3a.** Stage 3 changes the condensed \"cost of one departure\" figure through `get_industry_wage`, and that figure is visible today. Pushing Stage 3 first would change a public number before it is hidden. So the R2 condensed hide moves forward as Stage 3a and ships before the wage refresh: `web/components/CondensedOutput.tsx` gates the block behind `FRICTION_DOLLARS_VISIBLE`, omits the block and its \"roughly 50-75%\" copy entirely when hidden (no replacement text, the unavailable note would tell the reader data is missing), and a vitest fails if the figure or the copy renders while the flag is false. No API, payload or engine change. Stage 5 keeps the rest of its scope: the wage x 0.333 single value, the `/api/condensed-complete` response shape change, and the types.")
raw = P.read_bytes().decode("utf-8"); crlf = "\r\n" in raw; t = raw.replace("\r\n", "\n")
assert t.count(OLD) == 1 and "Stage 3a" not in t
t = t.replace(OLD, NEW)
print("ok", "CRLF" if crlf else "LF")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8")); print("WROTE")
else: print("DRY RUN")
