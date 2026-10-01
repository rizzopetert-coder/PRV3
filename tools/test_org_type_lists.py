"""
Org type option list ownership (friction tax rebuild, Stage 2).

engine/data/intake.py INTAKE_FIELDS["org_type"] is the source of truth. The two web
components each carry their own ORG_TYPE_OPTIONS constant. This test fails if either
drifts from the intake list, from the exact six values (order included, these are the
rendered options and the submitted values), or if the constant stops being the thing
that is rendered.

Usage: python tools/test_org_type_lists.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(ROOT))
from engine.data.intake import INTAKE_FIELDS

PASS, FAIL = [], []


def check(label, cond, detail=""):
    (PASS if cond else FAIL).append(label if cond else f"{label}: {detail}")


EXPECTED = [
    "Founder-led",
    "PE or VC-backed",
    "Privately held professional leadership",
    "Nonprofit",
    "Publicly traded",
    "Government",
]


def web_list(rel: str) -> list:
    src = (ROOT / rel).read_text(encoding="utf-8")
    m = re.search(r"const ORG_TYPE_OPTIONS = \[(.*?)\];", src, re.S)
    assert m, f"{rel}: ORG_TYPE_OPTIONS not found"
    return re.findall(r'"([^"]*)"', m.group(1))


flow = web_list("web/components/DiagnosticFlow.tsx")
modal = web_list("web/components/SelfSelectIntakeModal.tsx")
intake = list(INTAKE_FIELDS["org_type"])

check("INTAKE_FIELDS['org_type'] is the exact six values in order", intake == EXPECTED, f"got {intake}")
check("DiagnosticFlow.tsx ORG_TYPE_OPTIONS equals the intake list", flow == intake, f"got {flow}")
check("SelfSelectIntakeModal.tsx ORG_TYPE_OPTIONS equals the intake list", modal == intake, f"got {modal}")

flow_src = (ROOT / "web/components/DiagnosticFlow.tsx").read_text(encoding="utf-8")
modal_src = (ROOT / "web/components/SelfSelectIntakeModal.tsx").read_text(encoding="utf-8")
check("DiagnosticFlow renders the Organization type select from ORG_TYPE_OPTIONS",
      'field("Organization type", "org_type", ORG_TYPE_OPTIONS)' in flow_src)
check("SelfSelectIntakeModal renders its select options from ORG_TYPE_OPTIONS",
      "{ORG_TYPE_OPTIONS.map(" in modal_src)
check("the source-of-truth note names engine/data/intake.py in both components",
      'INTAKE_FIELDS["org_type"]' in flow_src and 'INTAKE_FIELDS["org_type"]' in modal_src)
check("neither component still names ORG_TYPE_SCALARS as the source of truth",
      "ORG_TYPE_SCALARS" not in flow_src and "ORG_TYPE_SCALARS" not in modal_src)

print(f"\nPASS: {len(PASS)}   FAIL: {len(FAIL)}")
for f in FAIL:
    print("  FAIL", f)
if not FAIL:
    print("All tests passed.")
sys.exit(1 if FAIL else 0)
