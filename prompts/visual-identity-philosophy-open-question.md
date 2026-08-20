# Visual Identity Philosophy — Open Question, Flagged for Real Discussion

Status: RAW FINDING, still not a final decision. This session (Claude.ai) adds a new connecting
finding and a proposed reframe/direction below — still flagged for the Quarterly Step-Back, not
resolved here. Treat it as its own decision, not folded into any in-flight task.

## Origin, Pete's own words
"I want the rust glow. I want more color in general. The site does not look professionally
designed. It lacks effort. I get 'minimalism' but this does not land that way. It lands
amateur."

Raised while reviewing the resized homepage constellation figure live. Not a request specific to
that one shape — a broader reaction to the site's overall visual character.

## Why this is bigger than the task it surfaced during
The current visual identity is not a default or an unexamined choice — it's an explicit, stated
governing principle from the Principal Brief, reaffirmed multiple times this session:

- Locked 3-color palette (paper / charcoal / slate / rust).
- Rust reserved strictly for Endemic severity, never decorative — restated as recently as
  Category E's original brief this session: "when full color finally appears, it should land as
  a diagnosis, not a UI state change."
- Saint-Exupéry discipline ("nothing left to take away") as the named design philosophy,
  explicitly distinguished from "minimalism as aesthetic" in that same brief.

Pete's feedback — wanting rust used decoratively on a page with no real diagnosis behind it, and
wanting "more color in general" — is a direct reversal of that stated philosophy, not an
extension or refinement of it. Worth being explicit about that rather than treating it as a
small color tweak.

## The real fork, not yet resolved
Two genuinely different problems, requiring different fixes:

1. **Craft-execution problem.** The restrained philosophy is still the right strategic choice,
   but its execution has consistently read as cheap rather than intentional. This is the same
   diagnosis Category E's Direction 1 made at the very start of this session's visual-identity
   work ("tests whether 'cheap-looking' is a craft-execution problem, most likely, rather than a
   concept problem"). If still true after everything shipped since — Direction 1's rendering
   upgrade, Direction 3's editorial hero, the Direction 1 Refinement legibility/motion pass, the
   gestalt-interpretability addenda on both ConstellationField and /book/toc — that's a real,
   concerning signal: multiple genuine craft improvements have shipped and been individually
   verified as working, and the site still isn't landing as professionally designed. Worth
   sitting with that rather than assuming the next craft pass will be the one that finally works.

2. **Philosophy problem.** Restraint itself isn't functioning as a brand differentiator for this
   business, regardless of execution quality. This is a legitimate, real call to make — but it's
   a full reversal of a stated design philosophy that essentially every visual component built
   this session (ConstellationField's rendering, the diagnostic results page, /book/toc, the
   homepage) was built against. Not a quick fix. A rebrief.

## What this is NOT
Not a decision to make mid-task, and not something to resolve by guessing which fork is true and
quietly picking a direction. Both forks are plausible; they require genuinely different next
steps (a craft audit vs. a governing-principle change), and guessing wrong wastes real work
either way.

## Recommendation, not yet actioned
Treat this as its own real conversation — plausibly a good fit for the Quarterly Step-Back
(last run August 2, due ~August 23, roughly a week out) rather than a same-session pivot made in
the middle of a resize task. Bring real evidence to that conversation: specific pages/components
Pete finds "amateur," specific comparisons to sites/brands that land the way he wants this one
to, and an honest look at whether the craft-execution fixes already shipped this session moved
the needle at all in his eyes.

## Relationship to the still-open text-collision question (constellation resize)
That question (options A/B/C/D from earlier — does the resized shape need repositioning or
altered text spacing to avoid overlapping the hero copy) is now lower-priority and possibly
premature to lock in. If the philosophy question resolves toward "more color, more presence,"
the whole visual approach to that shape may change again regardless of how the collision
question gets answered today. Recommend holding that decision loosely rather than finalizing it
before the bigger question is resolved — not urgent, no work is blocked by leaving it open.

---

## This session's (Claude.ai) proposed direction for the Step-Back — NOT a final decision

**New finding, connecting two facts from this session's own work:** `--urgency` (the v2 token
carrying rust's Endemic-only meaning) is confirmed dormant in production — defined in
`web/app/globals.css`, zero live utility-class usage, same as the original `--color-rust` before
it. Separately, the SeverityResult per-state redesign shipped this session corrects a defect
where severity was being over-escalated — broadcast to unrelated states rather than attributed
per-state — meaning Endemic readings are now rarer and more accurate than before this session's
own fix.

The design philosophy's entire payoff ("when full color finally appears, it should land as a
diagnosis, not a UI state change") depends on that moment actually occurring for users with
meaningful frequency. This session's own correct, necessary severity fix makes that moment fire
even less often than it already did. Worth stating plainly at the Step-Back: **the central
visual-philosophy mechanism may be effectively unobserved by real users** — which would explain
"lands amateur" independent of any craft-execution quality. A restraint mechanism nobody ever
sees pay off reads as an absence, not a discipline.

**Proposed reframe of the craft-vs-philosophy fork:** not a clean either/or. The Core Reframe's
philosophical case (the differentiator is delivery style — magnanimous but unflinching — not the
taxonomy) doesn't require a colorless palette. Restraint and warmth aren't opposites. The likely
real problem: the original 3-color lock conflated "restrained" with "monochrome except one rare
severity event" — a stricter reading of the Saint-Exupéry principle than the philosophy itself
actually requires.

**Proposed direction:** the already-partially-built v2/OD-07 token system may already be the
correct answer. It already separates two genuinely different jobs that the original 3-color lock
collapsed into one color (rust): `--oxide` as a general-use accent (warmth, presence, everyday
use) and `--urgency` (rust's exact meaning, Endemic-only, still fully exclusive) as the reserved
diagnostic-moment color. A two-tier system, not an abandonment of restraint — general color gets
real presence; the reserved color keeps its exclusivity and its payoff, whenever it fires.

Currently `--oxide`/v2 is live only on the homepage (Stage 4 proof point); every other route
still runs the original Session 58 tokens (`--color-paper/-charcoal/-slate/-rust`) unchanged.

**Proposed Step-Back question:** should the v2 token system become the site-wide standard, not
just a homepage proof point?

**Explicitly not a final decision.** This is this session's (Claude.ai) proposed framing for Pete
to bring into the Step-Back conversation, alongside the doc's own existing recommendation above
(specific "amateur"-reading pages/components, comparison sites/brands, an honest read on whether
shipped craft fixes moved the needle).
