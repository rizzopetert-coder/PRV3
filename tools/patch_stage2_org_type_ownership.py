"""
Friction tax rebuild, Stage 2 (spec Section 10 step 3): the org type option list is
owned by engine/data/intake.py INTAKE_FIELDS["org_type"], not by friction_tax.py's
ORG_TYPE_SCALARS (which Stage 4 removes). Comment-only edits, the list contents in
both web components are untouched, so the rendered options and submitted values do
not change. tools/test_org_type_lists.py enforces that both web lists equal the
intake list.

Usage: python tools/patch_stage2_org_type_ownership.py --dry-run | --write
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]

EDITS = [
    (R / "web/components/DiagnosticFlow.tsx",
     """// Source of truth is engine/friction_tax.py's ORG_TYPE_SCALARS keys,
// same list web/components/SelfSelectIntakeModal.tsx already carries as
// its own separately-declared constant (that file's own docstring notes
// it must be kept in sync manually) -- duplicated here rather than
// consolidated into a shared export, matching this codebase's existing
// accepted duplication precedent, not a new pattern.
""",
     """// Source of truth is engine/data/intake.py's INTAKE_FIELDS["org_type"].
// tools/test_org_type_lists.py fails if this list drifts from it. Same
// list web/components/SelfSelectIntakeModal.tsx carries as its own
// separately-declared constant, duplicated here rather than consolidated
// into a shared export, matching this codebase's existing accepted
// duplication precedent, not a new pattern.
"""),
    (R / "web/components/SelfSelectIntakeModal.tsx",
     """// Source of truth is engine/friction_tax.py's ORG_TYPE_SCALARS keys --
// verified verbatim against that table (2026-09-08), not assumed.
// Keep in sync manually if that table's keys ever change; also mirrors
// engine/data/intake.py's INTAKE_FIELDS["org_type"] list.
""",
     """// Source of truth is engine/data/intake.py's INTAKE_FIELDS["org_type"].
// tools/test_org_type_lists.py fails if this list drifts from it, and
// from the same list in web/components/DiagnosticFlow.tsx.
"""),
    (R / "engine/data/intake.py",
     '''    "org_type": [
        "Founder-led",''',
     '''    # Source of truth for the org type option list. The two web lists
    # (web/components/DiagnosticFlow.tsx, SelfSelectIntakeModal.tsx) must equal
    # it, enforced by tools/test_org_type_lists.py.
    "org_type": [
        "Founder-led",'''),
]

write = "--write" in sys.argv
for path, old, new in EDITS:
    raw = path.read_bytes().decode("utf-8"); crlf = "\r\n" in raw; t = raw.replace("\r\n", "\n")
    assert t.count(old) == 1, f"{path.name}: anchor count {t.count(old)}"
    t = t.replace(old, new)
    print(f"{path.name}: ok ({'CRLF' if crlf else 'LF'})")
    if write:
        path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8")); print("  WROTE")
print("WRITE" if write else "DRY RUN")
