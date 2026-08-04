"""
PRV3 -- Append Addendum 13 to prompts/friction-tax-legal-compliance-
methodology.md: OSHA State Plan research, final 6 states (North
Carolina, Puerto Rico, Vermont, Virginia, Wyoming, Michigan). Completes
the full 22-state statutory-maximum roster. Documentation only -- no
engine/ or web/ changes. Also updates Addendum 9's "Exact remaining
scope" tracking (fully-unresearched list now empty; Virginia's dollar-
figure conflict and Wyoming's unconfirmed current figure become the
two priority items; actual-average-backfill list fully updated).

Usage:
  python tools/patch_legal_compliance_addendum13.py --dry-run
  python tools/patch_legal_compliance_addendum13.py --write
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
    "### Exact remaining scope, so it's pickable up without rediscovery\n"
    "\n"
    "**Fully unresearched: NONE remaining.** All states from OSHA's 22-state private-sector\n"
    "State Plan roster now have at least a primary-sourced statutory-maximum finding (Addenda\n"
    "6-8, 12, 13). Two items remain genuinely open, not closed: Virginia's exact current dollar\n"
    "figure (Addendum 13 -- a real conflict between sources, not yet resolved) and New Mexico's\n"
    "exact operative dollar figure (Addendum 12 -- conformance mechanism confirmed, actual\n"
    "figures in FOM-6-Appendix-A-2024 not located via search).\n"
    "\n"
    "**Needs actual-average backfill, updated:** California, Washington, Alaska, Hawaii, Arizona\n"
    "(partial -- case examples only), Indiana, Iowa, Kentucky (figure found, Addendum 12 --\n"
    "'within the FRL' -- now that Michigan's report defines FRL as a computed national-average-\n"
    "offset band [Addendum 13], KY's figure could be revisited for real meaning, but KY's own\n"
    "specific percentage was not independently confirmed), Maryland (pre-2024-reform figure\n"
    "flagged stale, needs a post-reform figure), Nevada (statutory confirmed, average not\n"
    "researched), Tennessee (no average found, AES extreme-case anchor only, explicitly not a\n"
    "substitute), Minnesota (now at full statutory parity, separate average likely not a\n"
    "meaningful category going forward), Utah (no average found), North Carolina (statutory\n"
    "only, no average researched), Puerto Rico (statutory only, no average researched), Vermont\n"
    "(statutory only, no average researched), Virginia (statutory itself unresolved -- see\n"
    "conflict above, average not researched), Wyoming (current statutory not even confirmed yet\n"
    "-- average out of scope until that's resolved). South Carolina and Oregon remain the two\n"
    "states with confirmed actual-average figures from earlier addenda, unchanged.\n"
    "\n"
    "**Priority order if resumed:** two genuinely unresolved items take priority over any new\n"
    "actual-average research: (1) Virginia's dollar-figure conflict (Addendum 13) -- check\n"
    "VOSH's current official poster or Field Operations Manual directly; (2) Wyoming's current\n"
    "2025 figure (Addendum 13) -- the only researched state where even the current statutory\n"
    "maximum, not just the average, remains unconfirmed; check Wyoming DWS's current OSHA\n"
    "rules/poster page directly rather than relying on the 2020-era proposed-rule document found\n"
    "this pass. After those two: actual-average backfill is now the primary remaining category\n"
    "of work, not fresh statutory research -- the full 22-state statutory-maximum roster is\n"
    "otherwise complete across Addenda 6-8, 12, and 13.",
)

# ---------------------------------------------------------------------
# 2. Append Addendum 13, before "## Structural implications"
# ---------------------------------------------------------------------

ADDENDUM_13 = '''## Addendum 13 — OSHA State Plan Research, Final 6 States (North Carolina, Puerto Rico, Vermont, Virginia, Wyoming, Michigan)

**Status:** Completes primary-source research on all states from Addendum 9's "fully
unresearched" list. Combined with Addendum 12, this closes the full 22-state OSHA State Plan
roster for statutory-maximum research (actual-average backfill remains separately open for
several states -- see updated Addendum 9 tracking below). NOT yet reviewed by Gemini --
research documentation, not a design decision.

### North Carolina -- clean conformance mechanism, confirmed current

A 2022 Appropriations Act amended North Carolina G.S. Section 95-138 to require NC OSH to
track federal penalty levels via annual CPI-based adjustment, effective July 1 of each year.
Confirmed via NCDOL's own July 2, 2025 press release ("N.C. Department of Labor Updates Civil
Penalty Structure for Workplace Safety Violations," labor.nc.gov/news/press-releases):
"effective July 1, 2025, in accordance with annual adjustments tied to the U.S. Consumer Price
Index." NC's own FOM Chapter 6 page
(labor.nc.gov/osh/osh-enforcement-procedures/fom-chapter-06-penalties) directly cites the
current $165,514 repeat-violation maximum, confirming full current federal parity ($16,550
serious / $165,514 willful-repeat) as of the July 2025 update. Note: several third-party sites
(a contractor-authority blog, an adecco resource page) still display the stale 2024 figures
($16,131/$161,323) -- treating NCDOL's own primary source and FOM page as authoritative over
these, consistent with standing citation-verification practice.

### Puerto Rico -- resolves Addendum 9's "no effective date" gap entirely

Act No. 212-2024 (amending the Puerto Rico Workplace Safety and Health Act, Act No. 16 of
August 5, 1975) took effect November 3, 2025 per PR OSHA's own public notice. Confirmed
identically across five independent law-firm sources (Littler, Jackson Lewis, Mondaq, Lexology,
National Law Review, all dated Nov-Dec 2025): willful/repeat minimum $11,823, maximum
$165,514; serious violations $1,221-$16,550; non-serious up to $16,550; failure to correct up
to $16,550/day; posting violations up to $16,550. Full current federal parity, the newest
conformance update confirmed across this entire research effort.

### Vermont -- real conformance mechanism, minor procedural wrinkle

S.135 (2017 legislative session) amended 21 V.S.A. Section 210, VOSHA's penalty structure,
adding an annual CPI-based adjustment provision. Per VOSHA's own penalty-adjustments page
(labor.vermont.gov): "the final penalties are a calculation by the Federal Department of Labor
based on the annual Consumer Price Index... and are effective January 1st." Real finding: for
the 2024 cycle specifically, VOSHA states the adjustment "will be effective on February 1,
2024" -- a one-month slip from the statute's own January 1st target, worth noting as a minor
implementation gap rather than the statutory design itself. A separate VOSHA FAQ page still
states serious violations carry a penalty "of up to $14,00[0]" -- contradicted by the primary
penalty-adjustments page and treated as a stale, uncorrected artifact, not an alternate current
figure.

### Virginia -- GENUINE UNRESOLVED CONFLICT, not smoothed over

Virginia Code Section 40.1-49.4.P establishes an annual conformance cycle, confirmed via
Virginia DOLI's own document (townhall.virginia.gov) as effective August 1, 2025 for citations
opened on or after that date. THE ACTUAL DOLLAR FIGURE IS DISPUTED ACROSS SOURCES, NOT RESOLVED
HERE:
- LegalClarity (Dec 2025) and a Virginia employer's guide (Willcox Savage, April 2025) both
  cite full current federal parity: $16,550 serious / $165,514 willful-repeat.
- Two independent labor-poster compliance sites (All In One Poster Co., Aug 2025; Labor Law
  Education Center, Nov 2025), both citing VOSH's own revised workplace poster, state $16,287
  serious / $162,849 willful-repeat -- a DIFFERENT figure that does not match any federal
  figure found in this entire research effort (not 2024's $16,131/$161,323, not 2025's
  $16,550/$165,514).

DO NOT pick one of these as correct without further verification -- the $16,287 figure suggests
Virginia's own August 1 cycle may compute independently from federal's January 15 cycle rather
than simply copying federal's current number (structurally similar to Maryland's timing lag,
Addendum 12, but here the number itself diverges, not just the timing). Flagged for direct
verification against VOSH's actual current poster or Field Operations Manual next time this is
picked up -- do not guess.

### Wyoming -- mechanism confirmed, current figure NOT found, real caution reinforced

A Wyoming Department of Workforce Services proposed-rule document (dated around December
2020/January 2021, dws.wyo.gov) shows Wyoming adopts federal penalty levels via periodic
administrative rulemaking (incorporation by reference of OSHA's Field Operations Manual), not
automatic statutory adoption -- and that document was still proposing adoption of federal's
JANUARY 2020 penalty levels nearly a year after they took effect federally (the rule updates
"the adoption date from 1/23/19 to 1/10/2020," itself proposed for a Dec 2020/Jan 2021 comment
period). SIGNIFICANT: this means Wyoming's "Yes/Identical" entry in OSHA's official
adoption-tracking table does NOT imply real-time or even same-year tracking -- it means
eventual, rulemaking-cycle-dependent adoption with a documented multi-month-to-year lag. This
is a SECOND confirmed instance of the Michigan false-positive caution from Addendum 8 (a
"Yes/Identical" table entry does not by itself confirm current parity) -- Wyoming joins
Michigan as a state where the table's positive signal actively undersells a real lag. No
current 2025 dollar figure for Wyoming was located this pass -- flagged for direct pickup
(Wyoming DWS's current OSHA rules page or current poster) rather than assumed from the stale
2020-era document found here.

### Michigan -- closes Addendum 9's flagged gap: BOTH statutory and actual-average found

Statutory, confirmed via Michigan's own current law text (MCL 408.1035,
legislature.mi.gov/Laws/MCL): "the board shall assess the employer a civil penalty of not more
than $7,000.00" for a serious violation -- mandatory language, materially below federal's
$16,550, unchanged from pre-2016 levels. Real-world enforcement anchor: a MIOSHA case against
LG Energy Solution Michigan Inc. (Holland, MI; case opened October 25, 2023, per AOL News/The
Sentinel reporting) assessed two willful violations at exactly $70,000 each -- Michigan's own
statutory cap, not federal's $165,514, confirming the low ceiling is being applied in real
recent enforcement, not just a stale statute nobody actually uses.

ACTUAL-AVERAGE FOUND, directly comparable to Oregon ($604), Maryland ($862-892), South
Carolina ($2,019): Michigan's own FY2021 Comprehensive FAME Report (osha.gov/sites/default/files,
"michigan-fy-2021-comprehensive-fame-report.pdf"): "The average current penalty per serious
violation in the private sector during FY 2021 was $1,217.24 (SAMM 8: 1-250+ workers)." Same
report explicitly confirms non-adoption as of that date: "The Michigan State Plan has not yet
completed the legislative changes to increase maximum penalties" -- direct government
confirmation consistent with every other source found on Michigan across this whole research
effort.

### Bonus finding: "FRL" now defined, resolving Kentucky's flagged hedge in Addendum 12

The same Michigan FY2021 FAME report explicitly defines FRL for one of its metrics: "The FRL is
-25% of the three-year national average ($3,100.37), which equals $2,325.28." This confirms FRL
("Federal Reference Level," a SAMM 8-8d State Plan monitoring comparator) is a COMPUTED
PERCENTAGE-OFFSET BAND FROM A ROLLING NATIONAL AVERAGE -- not the federal statutory maximum, and
the percentage varies by the specific metric being measured (Michigan's serious-penalty metric
uses -25%; a different SAMM metric in the same report uses +/-20% for violations-per-inspection).
This retroactively validates the caution flagged on Kentucky's figure in Addendum 12 ("Page ten
of the FAME acknowledges Kentucky's average serious penalty... was within the FRL in all but
one category") -- that hedge was correct to apply, since FRL is genuinely a distinct, computed
metric, not a stand-in for the federal dollar maximum. Kentucky's actual-average figure could
now be revisited with this definition if useful, though the exact percentage Kentucky's own
FAME report used for that specific metric still was not independently confirmed this pass --
not assumed to also be -25% just because Michigan's report used that figure for its own
measure.

## Structural implications (bigger than Option A)'''

edit(
    DOC,
    "## Structural implications (bigger than Option A)",
    ADDENDUM_13,
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
