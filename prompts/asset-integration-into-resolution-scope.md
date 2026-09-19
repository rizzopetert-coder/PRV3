# Scope: Working Identified Assets into Proposed Solutions

**Status: scope resolved this session. No build sequencing, no architecture decisions made on any of the three options below — this file records scope only, for whoever picks this up next.**

## What this is

A scope decision on the general question "how should identified assets (strengths, not just liabilities) work into the resolution/recommendation the diagnostic produces." Resolved this session, then **revised mid-session after Pete reconsidered** — recorded explicitly below rather than silently overwritten, per the same correction/flag discipline used for the Loureiro pricing correction earlier this session (state what changed and why, not just the final answer).

## In scope

### Option 1 — Synthesis-level

Have the LLM synthesis prompt explicitly draw on `primary_asset_domain` when generating `resolution_framing_text` / `resolution_routing`, so the recommended direction names a leveraged strength, not just an addressed weakness.

No new engine math. A synthesis-prompt change only.

### Option 2 — Ledger-level parity

A structural analog to the friction tax ledger, but for assets: itemized counterbalancing strengths and what they represent.

Real new engine work, same weight class as the friction tax ledger build. Will need its own Gemini architecture gate when scoped for build, same as the ledger did — not a lightweight addition.

### Option 3 — Service-routing level (reconsidered — originally excluded, then reinstated by Pete directly, this session)

Weighting `resolution_family` / service-recommendation logic on the asset profile, not just the liability profile, so a strong asset on a given axis can itself shift which service gets recommended, not only which condition gets named.

**This was originally scoped out of this pass, then Pete reinstated it directly mid-session.** Recording the reversal explicitly, not folding it silently into the option list as if it had always been in scope.

**Weight flag, to carry forward every time this file is picked up:** this is the highest-leverage and highest-risk of the three. It touches `engine/resolution_families.py`'s routing logic, which currently routes on condition/liability signal only — introducing asset-weighted routing is a change to a core decision path, not an additive field. This needs its own careful architecture review when it comes up for build, on the same order of scrutiny as Option 2, not the lightweight synthesis-prompt change Option 1 is. Do not let this get scoped as equivalent effort to Option 1 just because the three are listed together here.

## Not closed

Pete's own note: **"perhaps more"** beyond these three. This list is a floor, not a ceiling — do not treat it as exhaustive when this is next picked up.
