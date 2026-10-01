"""
Friction tax rebuild, Stage 3 (R1): wage refresh with a frozen Legal copy.

engine/friction_tax.py
  1. The existing May 2023 table is renamed _LEGAL_WAGE_DATA_MAY2023, text and
     values untouched, with a comment explaining why it exists (R1, Legal
     byte-identity, moving Legal to May 2025 is a separate future decision).
  2. A new _INDUSTRY_WAGE_DATA holds the May 2025 W values (spec Section 3,
     verified 2026-09-30 against oesm25in4.zip, nat3d_M2025_dl.xlsx and
     nat3d_owner_M2025_dl.xlsx).
  3. _oh_compensatory_damages_pricing() reads the frozen table, and the comments
     and docstrings that name the table it reads follow.
  4. get_industry_wage() docstring says May 2025 and 11 industries.
tools/test_friction_tax.py
  5. The Ohio expected-value comment names the frozen table.

Usage: python tools/patch_stage3_wage_refresh.py --dry-run | --write | --print-table
"""
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1]
FT = R / "engine/friction_tax.py"
TEST = R / "tools/test_friction_tax.py"

SRC = ("BLS OEWS May 2025, oesm25in4.zip, nat3d_M2025_dl.xlsx (national, 3-digit NAICS, "
       "all occupations 00-0000), employment-weighted mean of A_MEAN over {comp}. "
       "Total employment {emp}. Recomputed and re-verified against the primary file on 2026-09-30. ")
W25 = [
    ("Professional Services", 108640, "NAICS 541 (Professional, Scientific, and Technical Services)", "10,800,470", "", "BLS_OEWS_2025_naics3_541"),
    ("Healthcare & Life Sciences", 70969, "NAICS 621, 622, 623 and 624", "22,889,480",
     "NAICS 622 uses the privately owned rows (OWN_CODE 5) from nat3d_owner_M2025_dl.xlsx (5,570,850 employees at $89,460), state and local hospitals excluded (Decision 12). ", "BLS_OEWS_2025_hc_621_624_private622"),
    ("Financial Services", 100842, "NAICS sector 52 (Finance and Insurance)", "6,281,650", "", "BLS_OEWS_2025_naics2_52"),
    ("Technology", 115030, "NAICS sector 51 (Information)", "2,879,630",
     "Sector 51 is broader than ideal for a Technology label (includes telecom, broadcasting, publishing), carried over from the May 2023 entry. ", "BLS_OEWS_2025_sector51_information"),
    ("Manufacturing", 69131, "NAICS sectors 31-33", "12,654,340", "", "BLS_OEWS_2025_naics2_31-33"),
    ("Retail & Hospitality", 42024, "NAICS sectors 44-45 plus 721 (Accommodation) and 722 (Food Services and Drinking Places)", "29,780,010",
     "721 carries ownership code 57 with no privately owned row published, left as published and disclosed. ", "BLS_OEWS_2025_retail_hospitality_weighted"),
    ("Nonprofit & Education", 72765, "NAICS 611 (privately owned rows, OWN_CODE 5, from nat3d_owner_M2025_dl.xlsx: 3,344,880 employees at $73,400) plus 813 (1,429,400 employees at $71,280)", "4,774,280",
     "State and local schools are excluded (Decision 12). ", "BLS_OEWS_2025_nonprofit_education_611private_813"),
    ("Government & Public Sector", 80290, "the OEWS government designation (999000, all ownership)", "10,242,890",
     "Federal, state and local government excluding state and local schools, hospitals and the Postal Service. ", "BLS_OEWS_2025_sector99_government"),
    ("Construction", 72146, "NAICS sector 23", "8,298,380", "", "BLS_OEWS_2025_naics2_23"),
    ("Transportation & Warehousing", 64331, "NAICS sectors 48-49", "7,448,650",
     "491 (Postal Service) is a federal ownership row with no private row published, left as published and disclosed. ", "BLS_OEWS_2025_naics2_48-49"),
    ("Other", 67977, "NAICS sectors 11, 21, 22, 42, 53, 55, 56 and 71, plus 811 and 812 (sector 81 less 813)", "27,796,970",
     "713 carries ownership code 57 with no privately owned row published, left as published and disclosed. ", "BLS_OEWS_2025_other_residual"),
]


def new_table() -> str:
    out = (
        "# BLS OEWS May 2025 mean annual wage W by engine industry, as (wage, source,\n"
        "# citation_id) tuples. Each is the employment-weighted mean of the 3-digit NAICS\n"
        "# all-occupation A_MEAN values over the industry mapping committed in\n"
        "# prompts/friction-tax-rebuild-source-verification.md Section 2b, with the\n"
        "# privately owned rows for NAICS 611 and 622 (Decision 12). Files: oesm25in4.zip,\n"
        "# nat3d_M2025_dl.xlsx and nat3d_owner_M2025_dl.xlsx. Verified against the primary\n"
        "# files 2026-09-30 (all 11 match prompts/friction-tax-rebuild-build-spec.md\n"
        "# Section 3). Read by get_industry_wage() and the PAYROLL_BASELINE_GRID build,\n"
        "# NOT by Legal/Compliance, which reads _LEGAL_WAGE_DATA_MAY2023 above.\n"
        "_INDUSTRY_WAGE_DATA: dict[str, tuple[float, str, str]] = {\n"
    )
    for name, w, comp, emp, extra, cid in W25:
        text = SRC.format(comp=comp, emp=emp) + extra + f"Mean annual wage: ${w:,}."
        lines, cur = [], ""
        for wd in text.split(" "):
            if cur and len(cur) + len(wd) + 1 > 70:
                lines.append(cur + " ")
                cur = wd
            else:
                cur = (cur + " " + wd) if cur else wd
        lines.append(cur)
        lit = "\n".join(f'        "{ln}"' for ln in lines)
        out += f'    "{name}": (\n        {w}.0,\n{lit},\n        "{cid}",\n    ),\n'
    return out + "}\n"


FT_EDITS = [
    ("""# Real BLS OEWS May 2023 mean annual wage figures, by industry, as
# (wage, source, citation_id) tuples. 6 are single-sector lookups; 2
# (Retail & Hospitality, Nonprofit & Education) are employment-weighted
# means across multiple real BLS components, documented plainly below
# rather than presented as a single sector pull.
_INDUSTRY_WAGE_DATA: dict[str, tuple[float, str, str]] = {
""",
     """# FROZEN COPY, read ONLY by Legal/Compliance (friction tax rebuild, R1, Pete
# 2026-09-30). Legal's Ohio compensatory-damages formula
# (_oh_compensatory_damages_pricing) prices off this May 2023 table, and Legal
# outputs must stay byte-identical to the Phase 0 baseline
# (tools/capture_legal_baseline.py --check) while friction wages move to May
# 2025 in _INDUSTRY_WAGE_DATA below. Do not edit these values. Moving Legal to
# May 2025 wages is a separate future decision that deliberately changes the
# Legal baseline, not part of the friction rebuild.
#
# Real BLS OEWS May 2023 mean annual wage figures, by industry, as
# (wage, source, citation_id) tuples. 6 are single-sector lookups; 2
# (Retail & Hospitality, Nonprofit & Education) are employment-weighted
# means across multiple real BLS components, documented plainly below
# rather than presented as a single sector pull.
_LEGAL_WAGE_DATA_MAY2023: dict[str, tuple[float, str, str]] = {
"""),
    ("""        "BLS_OEWS_2023_other_nine_component_residual",
    ),
}
""",
     """        "BLS_OEWS_2023_other_nine_component_residual",
    ),
}

""" + new_table()),
    ("""    Public accessor for _INDUSTRY_WAGE_DATA's per-employee mean annual wage
    (BLS OEWS May 2023), keyed by the same 9 industry categories intake
    already collects""",
     """    Public accessor for _INDUSTRY_WAGE_DATA's per-employee mean annual wage
    (BLS OEWS May 2025), keyed by the same 11 industry categories intake
    already collects"""),
    ("        # compensatory base = _INDUSTRY_WAGE_DATA x\n",
     "        # compensatory base = _LEGAL_WAGE_DATA_MAY2023 x\n"),
    ("    x _INDUSTRY_WAGE_DATA) for both branches to apply their multiplier\n",
     "    x _LEGAL_WAGE_DATA_MAY2023) for both branches to apply their multiplier\n"),
    ("    compensatory_base = _INDUSTRY_WAGE_DATA[industry]'s real BLS OEWS wage\n",
     "    compensatory_base = _LEGAL_WAGE_DATA_MAY2023[industry]'s real BLS OEWS wage\n"),
    ("    _INDUSTRY_WAGE_DATA key -- should never happen against real\n",
     "    _LEGAL_WAGE_DATA_MAY2023 key -- should never happen against real\n"),
    ("    wage_entry = _INDUSTRY_WAGE_DATA.get(industry)\n",
     "    wage_entry = _LEGAL_WAGE_DATA_MAY2023.get(industry)\n"),
    ('            "unrecognized industry=%r has no _INDUSTRY_WAGE_DATA entry",\n',
     '            "unrecognized industry=%r has no _LEGAL_WAGE_DATA_MAY2023 entry",\n'),
    ("    _INDUSTRY_WAGE_DATA for _oh_compensatory_damages_pricing(). Every\n",
     "    _LEGAL_WAGE_DATA_MAY2023 for _oh_compensatory_damages_pricing(). Every\n"),
]
TEST_EDITS = [
    ('# -- compensatory_base = _INDUSTRY_WAGE_DATA["Professional Services"][0] (102,670.0) x --\n',
     '# -- compensatory_base = _LEGAL_WAGE_DATA_MAY2023["Professional Services"][0] (102,670.0) x --\n'),
]


def apply(path, edits, write):
    raw = path.read_bytes().decode("utf-8")
    crlf = "\r\n" in raw
    t = raw.replace("\r\n", "\n")
    for o, n in edits:
        assert t.count(o) == 1, f"{path.name}: anchor count {t.count(o)}: {o[:70]!r}"
        t = t.replace(o, n)
    print(f"{path.name}: {len(edits)} edits ok ({'CRLF' if crlf else 'LF'})")
    if write:
        path.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
        print("  WROTE")


if __name__ == "__main__":
    w = "--write" in sys.argv
    if "--print-table" in sys.argv:
        print(new_table())
        sys.exit(0)
    apply(FT, FT_EDITS, w)
    apply(TEST, TEST_EDITS, w)
    print("WRITE" if w else "DRY RUN")
