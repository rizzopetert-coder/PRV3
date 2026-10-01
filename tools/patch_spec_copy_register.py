"""
Add the unreviewed-copy register to the spec addendum: every string the friction
rebuild introduced or rewrote that sits behind FRICTION_DOLLARS_VISIBLE, with its
location and exact text, for Pete's review before any flag flip. Line numbers are at
the Stage 5 commit that adds this section.

Usage: python tools/patch_spec_copy_register.py --dry-run | --write
"""
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "prompts/friction-tax-rebuild-build-spec.md"

SECTION = """
### Copy requiring Pete's review before any flag flip

Every string the friction rebuild introduced or rewrote that sits behind `FRICTION_DOLLARS_VISIBLE` (false). None of it renders while the flag is false. All of it was drafted by Claude Code during the build and is UNREVIEWED. Flipping the flag is a Tier 4 decision, and the framing rule in Section 2 applies: the total reads as what organizations like the client's typically lose, the engagement line as the gap to the best-run ones, never normal or acceptable, never full engagement. Placeholders in braces are filled from the result.

**Web, typical-loss line and capped percent**

| file:line | exact text | where it renders |
|---|---|---|
| `web/lib/output-text.ts:157-158` | What organizations like yours typically lose to friction each year | caption under the friction figure in the report's cost comparison (`ReportDetails.tsx:96`), and the label of the friction line in Copy results (`output-text.ts:419`) |
| `web/lib/output-text.ts:134` | {percent}% of payroll (for example 9.2% of payroll) | the capped percent line: the figure shown in place of a dollar amount at or above 1,000 employees, in the same two places |

**Engine, friction receipts** (`engine/contract.py`, `_friction_receipts`, rendered in the report's friction ledger footer and in Copy results under "How the friction tax was calculated:", one category label each)

| file:line | exact text | category |
|---|---|---|
| `engine/contract.py:709-714` | Intake counts organizations up to 1,000 employees and prices any larger organization as 1,000. Dollar amounts are withheld for that reason and only percent of payroll is shown. | Payroll baseline, capped (the cap statement) |
| `engine/contract.py:716-721` | Estimated annual payroll for {employees} {industry} employees at the {industry} average wage of {wage}: {payroll}. | Payroll baseline |
| `engine/contract.py:730-739` | This is the gap between organizations like yours and the best-run ones. Gallup finds 31% of U.S. employees engaged against an average of 70% in its best-practice organizations, and each employee below that level costs about 18% of salary. That is {percent}% of payroll, about {amount} a year. (at the cap: "...of payroll." with no amount) | Engagement |
| `engine/contract.py:742-753` | {quit rate}% of employees in {industry} leave each year (BLS JOLTS, 2025). Gallup finds 42% of voluntary exits are preventable, and Work Institute puts the cost of each exit at about 33.3% of salary. That is {percent}% of payroll, about {amount} a year. (at the cap: no amount) | Turnover |
| `engine/contract.py:764-767` | {condition} adds cost through {channels}. (channels from: turnover, lost productivity, weaker decisions, the three channel words predate the rebuild) | Condition, one per condition that switches a channel on, with the respondent's own answer as evidence |
| `engine/contract.py:776-783` | Managers spend about 37% of their time on decisions and about 58% of that time is used ineffectively (McKinsey, 2019). No dollar value is applied. The survey sample skews toward senior leaders at larger companies than most clients, so this is context and not a priced channel. | Decision time |
| `engine/contract.py:786-791` | Together, what organizations like yours typically lose is {percent}% of payroll, about {amount} a year. (at the cap: no amount) | Total |

The category labels themselves (Payroll baseline, Engagement, Turnover, Condition, Decision time, Total) are new in this form too.

**Engine, shared framing constants** (`engine/friction_tax.py:552-553`): "what organizations like yours typically lose" and "the gap between organizations like yours and the best-run ones". They are interpolated into the Total and Engagement receipts above.

**Web, condensed report, visible branch only** (`web/components/CondensedOutput.tsx`)

| file:line | exact text | note |
|---|---|---|
| `CondensedOutput.tsx:140` | Estimated cost of one departure in this pattern | Pre-existing heading, unchanged. Flagged: "in this pattern" is not true, the figure is the industry average wage times 0.333 and does not depend on the pattern. |
| `CondensedOutput.tsx:149-151` | (about one third of one employee's annual pay at the average wage in your industry, based on the Work Institute's estimate of what one voluntary departure costs) | New in Stage 5, replaced "(roughly 50-75% of one departing employee's estimated salary)". Marked UNREVIEWED in the source. Draft: it states the basis (wage x 0.333) but not the Work Institute's low-wage derivation limit. |
| `CondensedOutput.tsx:156` | A benchmark figure isn't available for the industry provided. | Pre-existing note for an unrecognized industry, unchanged. |

**Payload only, not rendered by any current surface** (`engine/friction_tax.py:578-583` and `671-687`): the input names, sources and vintages inside each channel (for example "Engaged share in best-practice organizations", "Gallup Global Indicator: Employee Engagement (gallup.com/394373)", "Work Institute Retention Report (low-wage derivation applied to all salaries)"). They travel in `friction_tax_estimate.typical_baseline.channels[].inputs` and are visible to anyone reading the API response, so they should be reviewed with the rest.

**Pre-existing flag-gated copy the rebuild did not change**: the ledger heading "Friction tax ledger" (`web/components/PrivateOutput.tsx:378`), the Copy results labels "Friction tax ledger:" and "How the friction tax was calculated:" (`web/lib/output-text.ts:401`, `:410`), and the Call 1 and Call 2 no-dollar rule (`engine/output_synthesis.py:50`).
"""

raw = P.read_bytes().decode("utf-8")
crlf = "\r\n" in raw
t = raw.replace("\r\n", "\n")
assert "Copy requiring Pete's review before any flag flip" not in t
t = t.rstrip("\n") + "\n" + SECTION
print("appended", "CRLF" if crlf else "LF")
if "--write" in sys.argv:
    P.write_bytes((t.replace("\n", "\r\n") if crlf else t).encode("utf-8"))
    print("WROTE")
else:
    print("DRY RUN")
