"""
PRV3 Scoring Engine — Section I.4
Jurisdiction Lookup Table

One entry per US jurisdiction (50 states + DC).
Three Boolean trigger categories per jurisdiction:

  transparency  — pay transparency and compensation disclosure laws
                  LOCKED: True for CA, CO, NY, WA, IL, MA per spec
  retaliation   — whistleblower protection statute strength
                  NULL: legal review required before values are set
  procedural    — required training and policy mandates beyond federal baseline
                  NULL: legal review required before values are set

multi_state_flag logic is computed at runtime from intake field 3, not stored
here. When True (principal selected 5+ jurisdictions), engine applies the
highest-restriction profile across all selected states per Boolean category.

Spec reference: Section I.4 and OD-09

IMPORTANT: retaliation and procedural values must be populated by legal counsel
before the engine handles jurisdiction-sensitive output. Do not set these values
speculatively. They are initialized as None (null) per spec instruction.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class JurisdictionProfile:
    """
    Scoring profile for one US jurisdiction.

    transparency:  True if jurisdiction has active pay transparency or
                   compensation disclosure law.
    retaliation:   True if jurisdiction has strong whistleblower protection
                   statute. None = legal review required, treat as False
                   (most conservative) in production until populated.
    procedural:    True if jurisdiction has required training or policy
                   mandates beyond federal baseline. None = legal review
                   required, treat as False until populated.
    """
    jurisdiction_id: str           # Two-letter US state abbreviation
    jurisdiction_name: str         # Full state name
    transparency:  bool            # LOCKED for named high-regulation states
    retaliation:   Optional[bool]  # None = legal review required
    procedural:    Optional[bool]  # None = legal review required


# Named high-regulation jurisdictions — transparency = True (LOCKED per spec I.4)
_TRANSPARENCY_TRUE = {"CA", "CO", "NY", "WA", "IL", "MA"}


def _j(jid: str, name: str) -> JurisdictionProfile:
    return JurisdictionProfile(
        jurisdiction_id=jid,
        jurisdiction_name=name,
        transparency=(jid in _TRANSPARENCY_TRUE),
        retaliation=None,   # Legal review required
        procedural=None,    # Legal review required
    )


JURISDICTION_TABLE: dict[str, JurisdictionProfile] = {j.jurisdiction_id: j for j in [
    _j("AL", "Alabama"),
    _j("AK", "Alaska"),
    _j("AZ", "Arizona"),
    _j("AR", "Arkansas"),
    _j("CA", "California"),
    _j("CO", "Colorado"),
    _j("CT", "Connecticut"),
    _j("DE", "Delaware"),
    _j("DC", "District of Columbia"),
    _j("FL", "Florida"),
    _j("GA", "Georgia"),
    _j("HI", "Hawaii"),
    _j("ID", "Idaho"),
    _j("IL", "Illinois"),
    _j("IN", "Indiana"),
    _j("IA", "Iowa"),
    _j("KS", "Kansas"),
    _j("KY", "Kentucky"),
    _j("LA", "Louisiana"),
    _j("ME", "Maine"),
    _j("MD", "Maryland"),
    _j("MA", "Massachusetts"),
    _j("MI", "Michigan"),
    _j("MN", "Minnesota"),
    _j("MS", "Mississippi"),
    _j("MO", "Missouri"),
    _j("MT", "Montana"),
    _j("NE", "Nebraska"),
    _j("NV", "Nevada"),
    _j("NH", "New Hampshire"),
    _j("NJ", "New Jersey"),
    _j("NM", "New Mexico"),
    _j("NY", "New York"),
    _j("NC", "North Carolina"),
    _j("ND", "North Dakota"),
    _j("OH", "Ohio"),
    _j("OK", "Oklahoma"),
    _j("OR", "Oregon"),
    _j("PA", "Pennsylvania"),
    _j("RI", "Rhode Island"),
    _j("SC", "South Carolina"),
    _j("SD", "South Dakota"),
    _j("TN", "Tennessee"),
    _j("TX", "Texas"),
    _j("UT", "Utah"),
    _j("VT", "Vermont"),
    _j("VA", "Virginia"),
    _j("WA", "Washington"),
    _j("WV", "West Virginia"),
    _j("WI", "Wisconsin"),
    _j("WY", "Wyoming"),
]}


def resolve_jurisdiction_flags(
    selected_jurisdictions: list,
) -> dict:
    """
    Given a list of jurisdiction_ids from intake field 3, return the
    effective Boolean flags for this session.

    multi_state_flag is True when 5+ jurisdictions are selected.
    When True, engine applies the highest-restriction profile:
      transparency = True if ANY selected jurisdiction has transparency = True
      retaliation  = True if ANY selected jurisdiction has retaliation = True
      procedural   = True if ANY selected jurisdiction has procedural = True
    None values (legal review pending) propagate conservatively as None
    unless overridden by a True value in another jurisdiction.

    Single-jurisdiction sessions use that jurisdiction's profile directly.
    """
    if not selected_jurisdictions:
        return {
            "transparency": False,
            "retaliation": None,
            "procedural": None,
            "multi_state_flag": False,
        }

    multi_state = len(selected_jurisdictions) >= 5
    profiles = [
        JURISDICTION_TABLE[jid]
        for jid in selected_jurisdictions
        if jid in JURISDICTION_TABLE
    ]

    if not profiles:
        return {
            "transparency": False,
            "retaliation": None,
            "procedural": None,
            "multi_state_flag": multi_state,
        }

    # Highest-restriction rule: True wins over None wins over False
    def highest(values):
        if any(v is True for v in values):
            return True
        if any(v is None for v in values):
            return None
        return False

    return {
        "transparency": highest([p.transparency for p in profiles]),
        "retaliation":  highest([p.retaliation  for p in profiles]),
        "procedural":   highest([p.procedural    for p in profiles]),
        "multi_state_flag": multi_state,
    }
