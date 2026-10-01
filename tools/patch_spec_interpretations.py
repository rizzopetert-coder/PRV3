"""
Record in the spec addendum the interpretation calls Pete accepted after Stages 4 and 6
(2026-09-30 build, reported 2026-10-01), plus the Stage 5 field name.

Usage: python tools/patch_spec_interpretations.py --dry-run | --write
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "prompts/friction-tax-rebuild-build-spec.md"

SECTION = """
### Accepted interpretation calls (Pete, accepted after Stages 4 and 6)

- `driving_factors` is dropped from `friction_tax_estimate`, because the receipts moved to `private_output.friction_receipts`. Section 6's shape line, which lists `driving_factors` inside the estimate, was internally inconsistent with the adopted "receipts move to a sibling" decision. The estimate carries `currency`, `typical_baseline` and `excess` only.
- The ledger footnote (`FRICTION_TAX_LEDGER_FOOTNOTE`) and the ledger standalone note (`FRICTION_TAX_LEDGER_STANDALONE_NOTE`) are deleted, because they described severity-scaled per-row estimates and were false under the new model. They only ever rendered behind `FRICTION_DOLLARS_VISIBLE`.
- The share-payload strip covers the four top-level names (`friction_tax_estimate`, `legal_tail_risk_band`, `friction_receipts`, `channels`). The ledger, which carries `channels` on each row, is never written to a share (the write is a whitelist), and the guard test scans any depth.

### Stage 5 field name

The spec does not name the condensed single value. The engine returns `condensed_departure_cost: { amount, currency }` (industry wage, OEWS May 2025, times 0.333, `amount` null for an unrecognized industry) from `/api/condensed-complete`, and the condensed payload carries `departure_cost` of the same shape. The retired `condensed_financial_range` and `financial_range` are read as no figure, never converted, because the basis differs.
"""

raw = P.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
t = raw.replace("\r\n", "\n")
assert "Accepted interpretation calls" not in t
t = t.rstrip("\n") + "\n" + SECTION
print("appended", "CRLF" if crlf else "LF")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("WROTE")
else:
    print("DRY RUN")
