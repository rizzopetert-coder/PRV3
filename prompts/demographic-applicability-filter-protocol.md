# Demographic Applicability Filter — Standing Design Protocol

**Status:** New standing protocol, adopted this session after the SEC/nonprofit mismatch in
Cluster 4's design. Applies to all future PRV3 design work that anchors to real external
sources, not just Friction Tax. Complements, and runs before, the existing worked-dollar-
figure plausibility check (locked earlier this session — see MOB).

## Why this exists

Three times in one session, a design decision anchored to a real, verified external figure and
only checked whether the *magnitude* was plausible, not whether the *mechanism itself even
applies* to the client in question:

1. McKinsey's Fortune-500 decision-making-cost figure, initially used for the attritional
   decision-quality leg — real data, wrong reference class for PRV3's actual SMB/mid-market
   clients.
2. Beck v. Boeing's $72.5M settlement, initially proposed as a fixed dollar ceiling for
   Legal/Compliance — real, verified figure, but proportionally trivial for the company it
   actually happened to and catastrophic when misapplied to a small client, because it was
   never checked against a different company's actual scale.
3. SEC whistleblower award data, anchoring Cluster 4's ceiling — real, verified, but the SEC
   has no jurisdiction over most of PRV3's actual clients (nonprofits, private companies
   outside securities law) at all. This wasn't a magnitude problem — the mechanism doesn't
   apply, at any magnitude.

The existing plausibility-check practice (run a worked dollar example against a real
benchmark) catches instances 1 and 2 reliably, because both are fundamentally about whether a
*number* is the right size. It does not reliably catch instance 3, because the problem isn't
the number — it's that the underlying real-world mechanism doesn't extend to the client at
all. A different, earlier check is needed for that class of error.

## The protocol

Run whenever a design decision anchors to a real external source — case law, agency data, an
industry statistic, a specific statutory mechanism — before any plausibility check on
magnitude:

1. **State the assumption explicitly.** What is this source being treated as generally true
   *of*? Write it as a sentence, not left implicit.
2. **Find the source's own eligibility boundary.** Every real-world figure describes some
   bounded population — a jurisdiction, an industry, a company-size range, a legal status.
   State that boundary explicitly rather than treating the source as universally applicable
   because it's real and verified.
3. **Cross-check against PRV3's actual intake/demographic fields** — whatever the real schema
   collects (industry/sector, org type, headcount, and anything else confirmed against the
   actual codebase, not assumed).
4. **Test at the extremes of each relevant field's range, not the modal case.** The design
   that inspired this protocol used a mid-size professional-services example throughout —
   never once checked against a nonprofit, which is where the mismatch actually lived. Bias
   toward testing the edges of the client range specifically, since that's where applicability
   assumptions break, not the middle.
5. **If the assumption breaks anywhere in that range, the design needs explicit gating by that
   field** — not a uniform rule with an exception patched on after the fact. If it holds
   everywhere across the real range, document that as a confirmed check, not a silent
   assumption.

## Relationship to the existing plausibility-check practice

Applicability first, then magnitude. A mechanism that doesn't apply to a client makes the
magnitude question moot; a mechanism that does apply still needs its dollar figures checked
against a real benchmark, per the existing practice. Both are now standing requirements before
any dollar-bearing or mechanism-bearing design decision is treated as reviewed.
