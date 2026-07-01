# The Unexamined Algorithm

You didn't get the interview. Or you did, and the offer never materialized, or the raise you expected didn't come through, or your review landed noticeably lower than you'd anticipated. Somewhere in that entire process, an automated tool made or substantially shaped the underlying decision before any actual person ever meaningfully looked at your file.

Nobody here necessarily set out to build something genuinely unfair to anyone. The efficiency gains were real and measurable, the vendor's original pitch was genuinely compelling, and the tool got adopted specifically because it demonstrably worked — faster, more consistent, and considerably cheaper than the available human alternative. Nobody, in the time since, has actually looked closely at what the tool is genuinely optimizing for underneath that consistent, efficient surface.

---

### Efficient and Untested Are Not the Same Thing

Adopting a tool specifically because it reliably produces faster, more internally consistent decisions is, on its own, a perfectly reasonable operational call for most organizations to make. Assuming that consistency itself necessarily means the underlying decisions are fair is an entirely different claim, and it's precisely the claim nobody has actually gone back and checked. A tool can be remarkably, perfectly consistent and simultaneously consistently wrong in its underlying logic, systematically screening out the same category of candidate every time, or heavily weighting the same problematic proxy variable every cycle. That mechanical consistency will actively make the underlying pattern harder to spot from the outside, not easier, precisely because there's no obvious statistical outlier anywhere to trigger an investigation.

### What "Nobody Has Looked" Actually Means

An unaudited algorithm currently making real employment decisions isn't some kind of neutral, harmless unknown sitting quietly in the background. It's already actively making consequential decisions, right now, today, based on criteria that literally nobody currently at the organization could actually explain if directly asked to. If those particular underlying criteria happen to correlate meaningfully with a legally protected characteristic (age, disability status, or some less obvious proxy variable standing in for either) the organization is actively generating disparate impact at real scale, and doing so with a clean, precisely timestamped decision log that documents exactly how it happened, in granular detail.

That log, contrary to how it might feel, doesn't protect the organization in any meaningful legal sense. It functions instead as the discovery record a plaintiff's attorney would eventually build their entire case around.

### What an Unaudited Tool Looks Like From the Inside

**Employment decisions — hiring, ongoing performance evaluation, compensation — are meaningfully shaped by some form of automated tool.** Screening, ranking, algorithmic scoring, or automated recommendation in any way that meaningfully narrows what an actual human decision-maker ultimately sees and considers.

**Nobody currently employed at the organization can actually explain the specific criteria the tool applies in practice.** Ask the person who originally approved the vendor contract to describe the underlying weighting logic. If the honest answer amounts to "the vendor handles that part," this condition is unambiguously present.

**The tool has been actively in use long enough to have already shaped a meaningful volume of real decisions, with genuinely no audit yet run against it.** The underlying exposure scales directly with both volume and elapsed time. Every additional cycle that passes without an audit represents another substantial batch of consequential decisions made on entirely unexamined criteria.

### Two Questions, Only One Asked

Pointing confidently to real time saved or genuine cost reduced doesn't actually answer the separate and more consequential question of whether the underlying criteria driving those savings are themselves lawful — those are genuinely two entirely separate questions, and to date only one of them has actually been asked by anyone at the organization. A tool can reliably deliver real, measurable efficiency gains and simultaneously be quietly generating legal claims nobody has noticed yet, precisely because efficiency and legal exposure aren't ever measured along the same axis, and improvement on one tells you essentially nothing about the other.

### The Audit Has to Happen Before the Claim Does

**First, obtain the actual underlying criteria directly from the vendor: not the polished marketing description, but the genuine underlying weighting logic itself.** If the vendor is unwilling or genuinely unable to provide this level of detail, that refusal is itself important information the organization should weigh heavily.

**Second, run a proper disparate impact analysis on the organization's own recent decisions that the tool meaningfully influenced, broken out explicitly by protected class.** This is a well-established, standard analytical approach, not some novel or experimental one — it has simply rarely been applied specifically to this particular tool until now.

**Third, decide, based directly on what that audit actually finds, whether to adjust the underlying criteria, add meaningful human review at the actual decision point, or discontinue the tool's use entirely.** Not a predetermined default outcome in any direction — a genuine decision made with the actual data in hand, rather than simply continuing to rely on the vendor's original assurances.

The tool has already made a substantial number of real decisions at this point. What genuinely hasn't happened yet is anyone actually checking whether it made those decisions lawfully.
