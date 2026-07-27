"""
PRV3 MOB Closeout -- /book Content Architecture Phase 2 (this session)

Six edits to tools/_mob.txt, plus one companion edit to CLAUDE.md:
  1. MOB version header v4.68 -> v4.69
  2. Section 13 -- replace the "/book navigation and organization" open-item
     row with a RESOLVED status pointing to Section 16 + 13a
  3. Section 13a -- append 3 new Decision Register rows
  4. Section 14 -- append 1 new Locked Decisions Log row
  5. Section 16 -- append the full session-log entry (with one sentence
     corrected per Pete's explicit instruction -- see note below)
  6. CLAUDE.md -- MOB version cross-reference v4.68 -> v4.69 (standard
     companion update matching every prior version bump in the session
     log; not explicitly restated in Pete's instructions this time, but
     included since it's the ironclad pattern, flagged in the dry-run)

Section 16 entry correction, confirmed with Pete before writing: the
"Of the 42:" sentence as originally drafted calls out FTA-17, LIB-037,
and LIB-052 individually and then separately says "28 more" and "~13
flagged" -- which double-counts those three if read as a strict sum
(45, not 42). The actual verified partition (confirmed via this
session's own pre-flight check script) is HOLD=13 (including FTA-17
and LIB-037), WRITE=28 (including LIB-052), PARTIAL=1 (LIB-014),
summing correctly to 42. Rephrased per Pete's explicit direction so
FTA-17/LIB-037/LIB-052 read as members of those buckets, not a fourth
category layered on top. Every fact in the original sentence is
preserved -- only the framing changed. No other part of the entry was
altered.

Usage:
  python tools/patch_mob_book_phase2_closeout.py --dry-run
  python tools/patch_mob_book_phase2_closeout.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parent.parent
MOB_FILE = REPO_ROOT / "tools" / "_mob.txt"
CLAUDE_FILE = REPO_ROOT / "CLAUDE.md"

# --- Edit 1: version header ---------------------------------------------

OLD_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.68"
NEW_VERSION_HEADER = "\\\\\\#\\\\\\# MOB v4.69"

# --- Edit 2: Section 13 row replacement ----------------------------------

OLD_SECTION13_ROW = "| /book navigation and organization | Not urgent, no action yet. /book went live this session with all 87 pieces, but the index page is a flat list (id/title/href only, sorted by manifest order) — no filtering, tagging, theming, or any navigation mechanism for 87+ growing pieces. Pete wants this addressed with genuine innovation in how readers benefit from the library, not just a basic filter UI. Open questions to resolve whenever picked up: (1) right taxonomy for organizing pieces — by existing contentType (methodology/memo/case_pattern), by the 57-state taxonomy dimension (Aptitude/Authority/Alliance/Attitude), by severity tier, by a new editorial theme/tag system, or some combination; (2) whether this needs new per-piece metadata authored on book-manifest.ts entries (tags, themes — a content-tagging pass across all 87+ pieces, similar in shape to this session's observation_text authoring project) or whether existing data can do most of the work without new authoring; (3) what's genuinely novel here beyond filter dropdowns and checkboxes — worth a real brainstorm before defaulting to standard filtering UI; (4) whether this connects to and can reuse the staged-sequence/LinkedIn-promotional-order batching logic already built this session. No design proposal yet. |"

NEW_SECTION13_ROW = "| /book navigation and organization | RESOLVED (this session) — see Section 16 entry and Section 13a. Taxonomy-based dimension/state/pillar navigation, URL structure, and Schema.org structured data built and shipped (commit a91a28c). Remaining backlog from the original open-item framing: diagnostic-to-library cross-linking (Phase 3, unscoped) and an RSS/JSON feed (Phase 4, unscoped) — both deferred, not started. |"

# --- Edit 3: Section 13a -- append 3 rows --------------------------------

SECTION13A_ANCHOR = "calibration-vs-live parity or extends Phase 1's reachable question set |"

SECTION13A_NEW_ROWS = """
| /book Phase 2 navigation architecture | 3 | Closed — live in Production via a91a28c | N/A | This session | Closed, no further check-in. Phase 3 (cross-linking) and Phase 4 (feed) are separate, unscoped future decisions, not a reopening of this row |
| Public dimension labels (Aptitude/Authority/Alliance/Attitude → plainspoken strings) | 3 | Locked | N/A | This session | Reused verbatim across the diagnostic self-selection surface and /book nav — one vocabulary, not two. Closed |
| "Same Rules, Different Results" (draft rename of expansion-state "Disparate Impact Architecture," public/diagnostic-facing only) | 3 | Provisional Hold, not Locked | Attorney review — same gate as LinkedIn/coaching template, not yet scheduled | This session | Legal-characterization risk (naming a user's org with an EEOC-recognized legal term), not just a voice question. Revisit whenever the attorney-review gate opens, not before |"""

# --- Edit 4: Section 14 -- append 1 row ----------------------------------

SECTION14_ANCHOR = "warrants a bump per the closeout protocol; no new locked decision recorded. MOB v4.40. |"

SECTION14_NEW_ROW = """
| **July 2026 — /book Content Architecture Phase 2 (schema lock)** | primaryDimension on BookPiece is permanently optional (not a 5th enum value) — locked this session per Gemini's Issue 1 ruling, adopted as-is. LIB-014 is a documented, permanent exception carrying secondaryDimensions but no primaryDimension, reflecting genuine co-equal dual-state status rather than a forced tie-break. MOB v4.69. |"""

# --- Edit 5: Section 16 -- append full entry -----------------------------

SECTION16_ENTRY = """| July 2026 — /book Content Architecture Phase 2: navigation, URL structure, structured data, and public taxonomy labeling — built and shipped, commit a91a28c | Opened on a request for novel /book organization/sharing approaches (SEO, social, newsletter-readiness). Resolved into a phased plan: canonical metadata (found already largely satisfied by existing teaser field), taxonomy-based navigation + URL + structured data (this session's scope), diagnostic-to-library cross-linking, and an RSS/JSON feed (both deferred, unscoped). **Plainspoken-naming pass, parallel thread:** four dimension public labels drafted (Aptitude/Authority/Alliance/Attitude → "How the work actually gets done" / "Who really has the power to decide" / "How people work together" / "How people show up"), confirmed for reuse verbatim across both the diagnostic self-selection surface and /book navigation — one taxonomy, one vocabulary, not a variant set. Two live-state name flags surfaced (Invisible Influence Architecture, Silosolation — the latter a portmanteau, arguably a P-10 coined-term violation) and several draft expansion-state candidates, none acted on this session beyond the one below. One draft expansion-state name change made and gated: "Disparate Impact Architecture" → **"Same Rules, Different Results"** for diagnostic/public-facing use only — the legal term itself stays permitted in citation/shareable-output content where precision to counsel matters. This rename is NOT a closed decision — it is gated on attorney review, same as the existing LinkedIn/coaching-template gate, since naming a user's org with an EEOC-recognized legal term on a self-diagnosis surface raises a genuine legal-characterization question, not just a voice one. Flagged for whoever runs that review next, not urgent otherwise. **Gemini structural review, /book Phase 2:** sent after a direct-read correction of prior assumptions (BookPiece.signatureId declared but populated on 0/88 entries; relatedSlug piece-to-piece, not piece-to-state, on 10/88; teaser already fully populated 88/88, meaning the previously-scoped "Phase 1 metadata" work was mostly already done) — this correction came from reading the actual manifest before sending anything to Gemini, not from assumption. Gemini returned a hybrid dimension+pillar model: primaryDimension (initially required, later permanently optional per a follow-up ruling — see below) + secondaryDimensions + stateIds on BookPiece; routes at /book/dimension/[slug], /book/state/[slug] (threshold-gated, ≥2 published pieces required to generate), /book/pillar/[slug]; Schema.org Article JSON-LD on piece pages. **Two Gemini recommendations overridden, not adopted as-is** — both are instances of the same known fabrication-adjacent pattern (confident-sounding precision without real justification), now confirmed to extend beyond citation/figure fabrication into architectural recommendations: (1) Gemini's proposed public dimension labels ("Capability & Execution," "Decision Rights & Governance," etc.) were exactly the corporate register P-10 rules out — Gemini was never given the already-drafted plainspoken labels, invented its own, and they were discarded wholesale in favor of the four already agreed. (2) Gemini's LIB-014 tie-break (primaryDimension: "aptitude" over "authority," justified as giving it "a stable home in the Aptitude bucket") gave a reason that applies equally to either dimension — an unforced, unjustified pick presented as a reasoned one. Resolved instead via Gemini's own alternative (Option 2): primaryDimension left unset, secondaryDimensions: ["aptitude","authority"], consistent with the Session-64 lock's own framing of the two states as co-equal. **contentPillar backfill (Step 0):** found FTA-01–17 uniformly tagged "Reframe" and FTA-18–53 uniformly untagged — a clean batch-completion gap, not scattered judgment calls; applied "Reframe" to all 36. One real Claude.ai-side error surfaced and corrected mid-session: an initial regex-based scan (non-block-bounded, whole-text) mis-attributed LIB-052 as missing contentPillar when it had in fact carried "Pattern Named" since its creation commit (git-blame confirmed, d1f69d8, 2026-07-08) — corrected via direct re-verification once CC's live-repo read conflicted with the earlier claim; net effect, no data was wrongly changed, but worth recording as a Claude.ai verification-method failure alongside the existing Gemini-fabrication learnings, not just a Gemini-specific risk. **Schema build (Steps 1–2):** DimensionKey + primaryDimension/secondaryDimensions/stateIds added to BookPiece, landed optional first specifically to avoid a broken-tsc window between Step 1's field addition and Step 2's population (CC flagged this sequencing risk proactively before writing). Title-exact-match against taxonomy.ts's 47 live states found 46 matches, 42 unmatched — a stated "34 LIB + 8 FTA" breakdown was independently recomputed and corrected to the true 35 LIB + 7 FTA (same total, mislabeled split, no missing entries). Of the 42 (partition: 13 held permanently unset — including FTA-17, Session-64 lock, and LIB-037, parked/out of scope, the remainder flagged as genuinely non-dimension-specific practitioner-methodology content and sent to Gemini as a schema question rather than force-guessed — plus 1 partial [LIB-014, per the Gemini-override above] plus 28 written this session, one of which, LIB-052, was resolved via its existing relatedSlug → paper-shield rather than a content judgment call): the remaining 27 resolved via direct content-based judgment (dimension only, three of them also getting an explicit stateIds match where the teaser named the state directly: LIB-044→silosolation, LIB-045→the_broken_compass, LIB-047→decision_paralysis). **Gemini's schema ruling adopted:** primaryDimension made permanently optional (not a 5th "cross_cutting" enum value, which would have forced a fake dimension-nav route) — the 13 entries close as permanently-unset, not pending. One data-quality aside surfaced in reconciling this: LIB-035 is contentType "memo" while its near-identical sibling LIB-036 is contentType "methodology" — doesn't change this decision, flagged for a future contentType pass. **Caught mid-build:** the original 46 title-exact matches from Step 2's discovery pass had only ever been dry-run, never actually written — surfaced when the state-route's generateStaticParams sample came back with zero qualifying states instead of the expected several, since every stateIds-bearing entry sat at count=1 with the 46 unwritten. Corrected: 46 written, verified disjoint from the 28-entry confident batch, zero pre-existing-field conflicts. **Route-template error, caught and corrected across three handoffs:** the original Step 4/5 handoff assumed a flat /book/[slug] canonical route; the actual live structure is /book/[type]/[slug] (app/book/[type]/[slug]/page.tsx) — a Claude.ai drafting error, not a repo change, caught by CC checking the real directory before building rather than building against the handoff's assumption. Corrected in the route/schema handoffs that followed; did not require a Gemini re-review, since the hybrid architecture itself doesn't depend on the literal route template. **Step 4 build:** version-checked against installed Next.js 16.2.9 docs before writing any route code (per standing practice established this session, not assumed from training data) — confirmed async params convention matches existing [type]/[slug] code, confirmed static-segment (dimension/state/pillar) precedence over the sibling [type] dynamic segment is unaffected in this version. State route threshold-gated at ≥2 published pieces per state; 6 states qualified from live data (decision_paralysis, paper_shield, silosolation, the_broken_compass, the_founders_grip, the_overloaded_manager). Slug conventions: pillar = kebab-case; state = taxonomy id with underscores→hyphens, grounded in the existing relatedSlug precedent already in the codebase (LIB-052's "paper-shield") rather than invented fresh. DimensionKey duplicate-declaration cleanup (book-manifest.ts vs. book-taxonomy-labels.ts) folded into Step 4 rather than left as silent drift. **Step 5:** Schema.org JSON-LD added to /book/[type]/[slug] via a <script type="application/ld+json"> tag (verified against installed-version docs, not assumed to be a generateMetadata mechanism as Gemini's original example implied); about field populated only when primaryDimension is set (reusing the exact same public label used in nav, not a third phrasing), omitted entirely — not null, not a fallback — for the 14 permanently-dimensionless entries including LIB-014, which does not get its secondaryDimensions used as a substitute primary. **Final verification, all 6 checks run fresh, not inferred:** tsc clean; contentPillar 87/88 (LIB-037 sole exclusion); primaryDimension 74/88 (a Claude.ai arithmetic error of 75 was caught and corrected here too — LIB-014 correctly holds secondaryDimensions instead of primaryDimension, not both, so 28+46=74 is right); stateIds 51/88; route diff clean (app/book/page.tsx byte-for-byte unchanged, [type]/[slug]/page.tsx diff is exactly the Step 5 addition); clinical boundary clean (zero "engine" string matches across all six touched/created files, direct grep not assumed). Committed a91a28c (14 files, 1922 insertions, 1 deletion) after explicit confirmation; pushed clean to origin/main (4c98f93..a91a28c) on separate explicit instruction, per the standing distinction between commit and push as separate authorized actions. **Pattern worth naming for the Key Learnings record:** this session surfaced Gemini's confident-unjustified-precision pattern in two NEW forms beyond citation/figure fabrication — overriding an explicit prior instruction without being given the context to know it existed (labels), and an arbitrary tie-break dressed as reasoned analysis (LIB-014) — meaning the standing verification discipline needs to extend to any Gemini architectural recommendation carrying a stated rationale, not just numeric/citation claims. Also worth naming: two "assumed-written-but-wasn't" gaps occurred this session on the Claude.ai side (LIB-052's phantom contentPillar-missing claim, the 46-unwritten title-matches) — both caught by CC verifying live repo state rather than trusting a prior summary, reinforcing rather than requiring new the existing "verify actual state, don't assume" discipline already in the MOB's learnings. MOB version bumped v4.68 → v4.69: new locked architecture (/book Phase 2 nav/schema/routes/JSON-LD) plus two new-form Gemini-reliability findings warrant it per the closeout protocol. | This session (Claude.ai + Claude Code + Gemini) | MOB v4.69 |"""

# --- Edit 6: CLAUDE.md version cross-reference ---------------------------

OLD_CLAUDE_VERSION = "| MOB version | v4.68 |"
NEW_CLAUDE_VERSION = "| MOB version | v4.69 |"


def verify_anchor(text: str, anchor: str, label: str) -> None:
    count = text.count(anchor)
    if count != 1:
        print(f"ABORT -- anchor '{label}' matched {count} times, need exactly 1", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    mob_text = MOB_FILE.read_text(encoding="utf-8")
    claude_text = CLAUDE_FILE.read_text(encoding="utf-8")

    verify_anchor(mob_text, OLD_VERSION_HEADER, "version header")
    verify_anchor(mob_text, OLD_SECTION13_ROW, "section 13 row")
    verify_anchor(mob_text, SECTION13A_ANCHOR, "section 13a anchor")
    verify_anchor(mob_text, SECTION14_ANCHOR, "section 14 anchor")
    verify_anchor(claude_text, OLD_CLAUDE_VERSION, "CLAUDE.md version")

    new_mob = mob_text
    new_mob = new_mob.replace(OLD_VERSION_HEADER, NEW_VERSION_HEADER, 1)
    new_mob = new_mob.replace(OLD_SECTION13_ROW, NEW_SECTION13_ROW, 1)
    new_mob = new_mob.replace(SECTION13A_ANCHOR, SECTION13A_ANCHOR + "\n" + SECTION13A_NEW_ROWS.strip("\n"), 1)
    new_mob = new_mob.replace(SECTION14_ANCHOR, SECTION14_ANCHOR + "\n" + SECTION14_NEW_ROW.strip("\n"), 1)
    new_mob = new_mob.rstrip("\n") + "\n" + SECTION16_ENTRY + "\n"

    new_claude = claude_text.replace(OLD_CLAUDE_VERSION, NEW_CLAUDE_VERSION, 1)

    print("=" * 100)
    print("EDIT 1 -- MOB version header")
    print(f"BEFORE: {OLD_VERSION_HEADER}")
    print(f"AFTER:  {NEW_VERSION_HEADER}")

    print("\n" + "=" * 100)
    print("EDIT 2 -- Section 13 row replacement")
    print("BEFORE:")
    print(OLD_SECTION13_ROW)
    print("AFTER:")
    print(NEW_SECTION13_ROW)

    print("\n" + "=" * 100)
    print("EDIT 3 -- Section 13a: 3 new rows appended after the existing last row")
    print(SECTION13A_NEW_ROWS)

    print("\n" + "=" * 100)
    print("EDIT 4 -- Section 14: 1 new row appended after the existing last row")
    print(SECTION14_NEW_ROW)

    print("\n" + "=" * 100)
    print("EDIT 5 -- Section 16: new entry appended at end of file")
    print(SECTION16_ENTRY)

    print("\n" + "=" * 100)
    print("EDIT 6 -- CLAUDE.md version cross-reference")
    print(f"BEFORE: {OLD_CLAUDE_VERSION}")
    print(f"AFTER:  {NEW_CLAUDE_VERSION}")

    print("\n" + "=" * 100)
    print(f"MOB file: {len(mob_text)} chars -> {len(new_mob)} chars ({len(new_mob) - len(mob_text):+d})")
    print(f"CLAUDE.md: {len(claude_text)} chars -> {len(new_claude)} chars ({len(new_claude) - len(claude_text):+d})")

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    MOB_FILE.write_text(new_mob, encoding="utf-8")
    CLAUDE_FILE.write_text(new_claude, encoding="utf-8")
    print(f"\nWROTE {MOB_FILE.relative_to(REPO_ROOT)}")
    print(f"WROTE {CLAUDE_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
