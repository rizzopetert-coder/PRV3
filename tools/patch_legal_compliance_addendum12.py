"""
PRV3 -- Append Addendum 12 to prompts/friction-tax-legal-compliance-
methodology.md: OSHA State Plan research, 7 more states (Kentucky,
Maryland, New Mexico partial, Nevada bonus, Tennessee, Minnesota, Utah).
Documentation only -- no engine/ or web/ changes. Also updates Addendum
9's "Exact remaining scope" tracking (fully-unresearched list down to
5 + Michigan, New Mexico's new partial-status line, the updated
actual-average-backfill list, and a new priority-order note on
statutory conformance mechanisms and fatality-tier enhancements).

Usage:
  python tools/patch_legal_compliance_addendum12.py --dry-run
  python tools/patch_legal_compliance_addendum12.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


DOC = "prompts/friction-tax-legal-compliance-methodology.md"

# ---------------------------------------------------------------------
# 1. Addendum 9 -- "Exact remaining scope" section, full replacement
# ---------------------------------------------------------------------

edit(
    DOC,
    "### Exact remaining scope, so it's pickable up without rediscovery\n"
    "\n"
    "**Fully unresearched (11 states):** Nevada, New Mexico, North Carolina, Puerto Rico,\n"
    "Tennessee, Utah, Vermont, Virginia, Wyoming, plus formal confirmation of Minnesota and\n"
    "Michigan (Michigan's statutory picture is confirmed materially low via direct current\n"
    "sources; needs its actual-average figure and formal write-up).\n"
    "\n"
    "**Needs actual-average backfill (10 of the 11 already-researched states):** California,\n"
    "Washington, Alaska, Hawaii, Arizona (partial -- has case examples, not a clean average),\n"
    "Indiana, Iowa, Kentucky, Maryland (partial -- has average, needs precise current statutory\n"
    "figure), South Carolina (partial -- has average, needs precise current statutory figure).\n"
    "Only Oregon currently has both numbers complete.\n"
    "\n"
    '**Priority order if resumed:** the explicit "No" or "Pending" entries in OSHA\'s adoption\n'
    "table are the strongest signal for likely-materially-lower states worth checking first\n"
    '(South Carolina already confirmed this pattern); "Yes/Identical" entries need individual\n'
    "verification regardless, per the Michigan false-positive.",
    "### Exact remaining scope, so it's pickable up without rediscovery\n"
    "\n"
    "**Fully unresearched (5 states):** North Carolina, Puerto Rico, Vermont, Virginia,\n"
    "Wyoming, plus Michigan (statutory already confirmed materially low via prior addenda;\n"
    "still needs actual-average figure and formal write-up, per Addendum 8's original flag).\n"
    "\n"
    "**New Mexico -- PARTIAL, not resolved (Addendum 12):** a real statutory conformance\n"
    "mechanism confirmed (SB 229, 2017), operationalized via an internal document\n"
    "(FOM-6-Appendix-A-2024, effective for citations April 1, 2025), but the actual current\n"
    "dollar figures in that document were not located this pass. Do not treat as either\n"
    "'unresearched' or 'done' -- the next pickup should target locating\n"
    "FOM-6-Appendix-A-2024's actual content directly, not re-doing the statutory-mechanism\n"
    "research (already confirmed).\n"
    "\n"
    "**Needs actual-average backfill, updated list:** California, Washington, Alaska, Hawaii,\n"
    "Arizona (partial -- case examples only), Indiana, Iowa, Kentucky (a figure was found in\n"
    "Addendum 12 -- KY's own FAME report citing performance 'within the FRL' -- but flagged as\n"
    "needing confirmation of what FRL denotes before treating as comparable to other states'\n"
    "actual-average figures), Maryland (Addendum 8's $862-892 figure now flagged stale, predates\n"
    "the 2024 conformance reform -- needs a post-reform figure), South Carolina (already have\n"
    "this one, Addendum 8), Nevada (new this pass -- statutory conformance confirmed,\n"
    "actual-average not researched), Tennessee (no actual-average found -- only the AES extreme-\n"
    "case anchor, explicitly not a substitute), Minnesota (now at full statutory parity as of\n"
    "Oct 2025 -- a separate 'actual average' distinct from the statutory figure may not be a\n"
    "meaningful category for this state going forward, unlike states with a real gap between\n"
    "statutory and actual), Utah (no actual-average found).\n"
    "\n"
    '**Priority order if resumed:** the explicit "No" or "Pending" entries in OSHA\'s adoption\n'
    "table are the strongest signal for likely-materially-lower states worth checking first\n"
    '(South Carolina already confirmed this pattern); "Yes/Identical" entries need individual\n'
    "verification regardless, per the Michigan false-positive.\n"
    "\n"
    "Statutory conformance mechanisms (automatic adoption tied to federal's annual cycle) are\n"
    "now confirmed in 6 of the states researched across this whole effort (Alaska, Hawaii, Iowa,\n"
    "Maryland, Minnesota, Nevada) -- when resuming research on the 5 remaining fully-unresearched\n"
    "states (NC, PR, VT, VA, WY) plus Michigan, check for this same conformance-mechanism pattern\n"
    "specifically before assuming each needs an independent from-scratch investigation; the OSHA\n"
    "adoption table's 'Yes/Identical' entries for NC, VA, VT, WY are consistent with this\n"
    "mechanism type but still need individual verification per the standing Michigan\n"
    "false-positive lesson (Addendum 8) -- a 'Yes/Identical' table entry does not by itself\n"
    "confirm a conformance mechanism exists, only that one might. Also check for\n"
    "fatality-specific enhancement tiers (confirmed twice now -- Oregon, Minnesota) in the\n"
    "remaining states.",
)

# ---------------------------------------------------------------------
# 2. Append Addendum 12, before "## Structural implications"
# ---------------------------------------------------------------------

ADDENDUM_12 = '''## Addendum 12 — OSHA State Plan Research, 7 More States

**Status:** Continues the state-by-state OSHA State Plan research from Addenda 6-8, paused per
Addendum 9. 7 states researched this pass: Kentucky, Maryland, New Mexico (partial), Nevada
(bonus, not on the original unresearched list), Tennessee, Minnesota, Utah. Primary-source
rigor, same standard as Addenda 6-8. NOT yet reviewed by Gemini -- this is research
documentation, not a design decision.

### Kentucky -- statutory confirmed current, materially below federal

KY OSH's own Field Operations Manual, Chapter 8 (Penalties), updated November 2025
(elc.ky.gov/workplace-standards, FOM Chapter 08 - Penalties.pdf): maximum penalty for a
serious or other-than-serious violation is $7,000; maximum for willful or repeated is $70,000
(minimum $5,000 for willful, per KRS 338.991(1)). Materially below federal's current $16,550
serious / $165,514 willful-repeat. Confirmed unchanged from prior addenda's understanding, now
sourced to a fresh November 2025 primary document rather than assumed current.

HB 398 (Kentucky Amends Occupational Safety and Health Act), effective June 27, 2025 per
Littler's ASAP summary (littler.com/news-analysis/asap): made civil penalty ISSUANCE
discretionary rather than mandatory ("may" replacing "shall" in the relevant statutory
language) -- a process change, not a dollar-amount change. The $7,000/$70,000 maximums
themselves did not move.

Contradicted third-party claim, worth recording per the standing citation-verification
practice: a March 2025 advocacy blog post (jordanbarab.com/confinedspace, "Kentucky Republicans
Launch OSHA Race to the Bottom") states Kentucky's current maximum willful penalty as "$14,000."
This is directly contradicted by every KY primary source found (the FOM, the OSH Inspection
Guide, the KYOSH Compliance Inspections poster, all independently citing $70,000 for
willful/repeat). Treating the blog's $14,000 figure as an error, not as an alternate current
value.

Actual-average -- found, but flagged as needing definitional confirmation before use:
Kentucky's own FFY2023 FAME Report Response (elc.ky.gov, "FAME Report 2023 Response.pdf")
states: "Page ten (10) of the FAME acknowledges Kentucky's average serious penalty in private
sector was within the FRL in all but one (1) category. Specifically, Kentucky's lone category
below the FRL (greater than 250 workers) was only $190.95 below the FRL." This is a real
primary-source figure from Kentucky's own government document, but "FRL" (likely "Federal
Reference Level," a SAMM 8-8d monitoring comparator OSHA computes for State Plan evaluation, not
directly defined in the excerpt found) is not confirmed in meaning from this source alone. DO
NOT treat this as directly comparable to Oregon's $604 or Maryland's $862-892 "actual average
assessed penalty" figures without first confirming what FRL denotes and how it's computed --
flagging as a genuine data point, not as clean comparable data.

### Maryland -- resolves Addendum 8's "exact figure not captured" gap

Chapter 104, Acts of 2024 (Labor and Employment Article Section 5-810, confirmed via
laborposters.org's MOSH Private Act poster PDF and the MOSH Public Act poster) ties Maryland's
maximum penalty to federal's CPI-U-adjusted figure via an annual conformance mechanism: "The
Commissioner of Labor will annually increase the maximum and minimum willful civil penalties by
the calendar year percentage increase in the Consumer Price Index for All Urban Consumers
(CPI-U)... effective on July 15th of each year." As of the reform's effective date (inspections
on or after July 1, 2024), the maximum was $16,131 (that year's federal level).

Confirmed operating on schedule, not just enacted-but-dormant: an independent November 2025
source (laborlawcenter.com, "Labor Law Poster Alert: Maryland OSHA Posters Revised") confirms
Maryland's official posters were updated July 15, 2025 per this same annual cycle ("As of July
15, 2025, the Maryland Department of Labor has updated its 'Safety and Health Protection on the
Job' posters... part of an annual inflation adjustment process").

Net effect: Maryland runs a consistent ~6-month lag behind federal's own January 15 cycle --
structurally similar to Washington's floor-tied-to-federal mechanism (Addendum 7) but built as a
rolling annual escalator rather than a floor provision. This resolves Addendum 8's flagged gap
("exact current statutory figure not captured").

Actual-average status: the existing $862-892 figure (Addendum 8, sourced to a FY2020 FAME report
plus 2023 corroboration) PREDATES this 2024 reform. Flagging it as likely stale rather than
re-confirming it as current -- no post-reform actual-average figure was found this pass.

### New Mexico -- PARTIAL, not resolved. Real gap identified, not closed.

The published statute text, NMSA 50-9-17 (env.nm.gov/occupational_health_safety, "NM
Occupational Health and Safety Act" PDF), still literally reads: serious violations "not to
exceed seventy thousand dollars ($70,000)" [NOTE: this is the willful/repeat figure per the
Act's structure -- the Act's Section 50-9-17 covers willful/repeat at up to $70,000, minimum
$5,000; posting violations up to $7,000 separately] -- these are pre-2016-catch-up-adjustment
levels, same base-statute pattern seen with other states.

However: Senate Bill 229, signed into law April 6, 2017 (per NM Environment Dept.'s "Archived NM
OSHA Announcements" page), "amended the Occupational Health and Safety Act...to adjust maximum
and minimum penalties in conformance with Federal law." The same source states: "The penalty
levels contained in the FOM-6-Appendix-A-2024 reflect increases to maximum and minimum penalties
to conform with SB 229. This policy is effective for all citations issued on or after April 1,
2025."

REAL GAP, NOT FABRICATED AROUND: I could not locate the actual dollar figures contained in
FOM-6-Appendix-A-2024 -- it's referenced by name in NM OHSB's own announcement page but is not
itself a public-indexed, separately fetchable document via the searches run this pass. This
means New Mexico is confirmed to have a conformance mechanism (like Washington, Maryland,
Nevada, Minnesota) but the actual current operative dollar figures are NOT confirmed -- do not
assume they match federal exactly, do not guess a number. This is a genuine unresolved item, not
a completed state -- mark New Mexico as PARTIAL in Addendum 9's tracking, not as done.

### Nevada -- bonus state, not on the original 11-state unresearched list

Clean, statutorily automatic parity. Senate Bill 40, passed during Nevada's 2019 legislative
session (per business.nv.gov's official 2024 press release, "Nevada OSHA's 2024 workplace safety
violation penalties increase in accordance with federal adjustment for inflation"): "the Division
of Industrial Relations automatically adopts penalties in alignment with those imposed by the
Department of Labor OSHA enforcement program." Confirmed via that same press release applying the
January 15, 2024 federal increase in Nevada effective the identical date (serious: $15,625 to
$16,131; willful/repeat: $156,259 to $161,323 -- matching federal's 2024 figures exactly). Same
category as Alaska/Hawaii/Iowa: statutorily required automatic parity, not case-by-case
adoption.

### Tennessee -- statutory confirmed materially below federal, current

TOSHA's own maximum penalties, confirmed current via an April 2026 local news report (aol.com,
"Tennessee's biggest TOSHA fine is still small by federal standards," citing TOSHA data):
"willful penalties are capped at $70,000 per violation, which is less than half the federal cap
of $165,514... Tennessee is one of a handful of states, including Indiana and Kentucky, that
haven't adopted the higher federal penalty cap enacted in 2016." Serious violation cap confirmed
at $7,000 per a Tennessee municipal-government legal resource (mtas.tennessee.edu, "Civil and
Criminal Liability under TOSHA").

REAL ANCHOR EXAMPLE, EXPLICITLY NOT AN ACTUAL-AVERAGE DATA POINT: the April 7, 2026 TOSHA
citation against Accurate Energetic Systems (AES), following the October 10, 2025 explosion that
killed 16 workers near Bucksnort, TN -- TOSHA's own statement (tn.gov/workforce, official press
statement) confirms this was "the largest-ever conducted by TOSHA" and "culminated in the
agency's highest-ever total penalty": $3.1M across 100 violations, 59 classified willful. Even in
this most extreme case in TOSHA's history, willful violations were still assessed against the
$70,000-per-violation statutory ceiling -- confirming the materially-below-federal cap holds even
at the agency's highest-stakes enforcement action to date. DO NOT use this as a stand-in for an
"actual average assessed penalty" figure (the kind collected for Oregon/Maryland/South Carolina)
-- it is one extreme, high-fatality case, not a routine-violation average. No routine
actual-average figure was found for Tennessee this pass.

### Minnesota -- upgraded from Addendum 8's "bonus, not yet formally researched"

Minnesota Statutes section 182.666, subdivision 6a ("OSHA Penalty Conformance," per house.mn.gov
bill text and dli.mn.gov's own rulemaking page) requires MNOSHA to automatically adopt federal's
current penalty levels. Confirmed via MNOSHA's own rulemaking page
(dli.mn.gov/about-department/rulemaking/minnesota-osha-rulemaking): "MNOSHA published in the
State Register, pursuant to Minnesota Statutes section 182.666, subdivision 6a, the updated
minimum and maximum for penalties (49 SR 178)... to the corresponding federal penalties... The
increase will become effective in Minnesota on Oct. 1, 2025." Confirmed figures at that effective
date: $16,550 serious/nonserious/posting (matching federal exactly), $165,514 willful/repeat
maximum, $11,823 willful minimum -- full current parity with federal as of October 1, 2025.

Distinctive addition, a real state-specific mechanism beyond plain parity: per MNOSHA's own
inspection-and-penalties page (dli.mn.gov/business/workplace-safety-and-health) and the 2022
conformance legislation itself (house.mn.gov bill text, amending Minn. Stat. 182.666 subd. 2):
"If a serious violation... causes or contributes to the death of an employee, the employer shall
be assessed a fine of up to $25,000 for each violation" -- a flat enhancement above the standard
$16,550 cap specifically for fatality-linked serious violations. This is the SECOND
state-specific fatality-enhancement mechanism found across this research effort (Oregon being
the first, Addendum 7's SB 592 fatality tiers) -- worth treating as an emerging pattern, not an
Oregon one-off, when Cluster 5's design is eventually finalized.

### Utah -- recently increased, near-parity with a real timing lag

HB0050 (2025), per BillTrack50's bill summary and confirmed independently via two VirgilHR
legal-update posts (virgilhr.com): raised Utah's maximum serious-violation penalty from $13,653
to $16,131, willful violation range from $9,753-$136,532 to $11,518-$161,323, effective May 7,
2025.

Real timing-lag finding: federal's own maximum had already increased to $16,550 (serious) and
$165,514 (willful) effective January 15, 2025 -- meaning Utah's own increase, when it took
effect on May 7, 2025, landed already ~2.5% behind the federal figure current at that same
moment. A smaller-magnitude version of Maryland's lag pattern (Maryland's is ~6 months by
design; Utah's is an incidental lag from its own separate legislative timeline, not a designed
conformance cycle). No actual-average figure found for Utah this pass.

### Pattern across all 7 states, worth naming for the eventual Cluster 5 design

At least three of the states researched this pass (Maryland, Minnesota, Nevada) plus three
already confirmed in prior addenda (Alaska, Hawaii, Iowa) now carry REAL statutory conformance
mechanisms -- not one-time catch-up adjustments but ongoing automatic adoption tied to federal's
own annual cycle, sometimes with a lag (Maryland: ~6 months by design; Utah: incidental lag from
separate legislative timing). That's six of the states researched across this whole effort
running on some form of conformance mechanism -- a real structural category, not a variant of
"clean parity," worth its own bucket if/when Cluster 5's per-state treatment gets formalized.
Separately: fatality-specific enhancement tiers (Oregon's SB 592 two-tier range, now Minnesota's
flat $25,000 bump) have appeared twice -- worth checking for in the remaining unresearched
states rather than assuming it's unique to Oregon.

## Structural implications (bigger than Option A)'''

edit(
    DOC,
    "3. The band boundaries need the same plausibility check as everything else in this\n"
    "   session -- run real worked multi-cluster examples through them once\n"
    "   compute_legal_compliance_exposure() has real test data to check against, before\n"
    "   treating $100K/$500K/$2M as final.\n"
    "\n"
    "## Structural implications (bigger than Option A)",
    "3. The band boundaries need the same plausibility check as everything else in this\n"
    "   session -- run real worked multi-cluster examples through them once\n"
    "   compute_legal_compliance_exposure() has real test data to check against, before\n"
    "   treating $100K/$500K/$2M as final.\n"
    "\n"
    + ADDENDUM_12,
)


def apply(dry_run: bool) -> int:
    changed = 0
    for rel_path, old, new in EDITS:
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 150 chars): {old[:150]!r}")
            return 1
        new_text = text.replace(old, new, 1)
        if dry_run:
            print(f"OK (dry-run): {rel_path} -- 1 match found, would replace")
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WRITTEN: {rel_path}")
        changed += 1
    print(f"\n{changed}/{len(EDITS)} edits {'validated' if dry_run else 'applied'}.")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    sys.exit(apply(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
