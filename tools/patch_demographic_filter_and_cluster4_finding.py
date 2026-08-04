"""
PRV3 -- Add the Demographic Applicability Filter to the MOB's standing
process-rules list (Section 13 Open Items, alongside the /book editorial
standard rows -- this is the closest existing analog: a cross-cutting
methodology rule, not a scoped Tier 3 decision needing a blocker/
check-in structure). Logs a Decision Register entry (Section 13a) for
Cluster 4's confirmed-flawed SEC-anchored ceiling, citing the real
intake schema pulled this session.

Usage:
  python tools/patch_demographic_filter_and_cluster4_finding.py --dry-run
  python tools/patch_demographic_filter_and_cluster4_finding.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

EDITS: list[tuple[str, str, str]] = []


def edit(path: str, old: str, new: str):
    EDITS.append((path, old, new))


edit(
    "tools/_mob.txt",
    "\\\\\\#\\\\\\# MOB v4.84",
    "\\\\\\#\\\\\\# MOB v4.85",
)

# --- Section 13 Open Items: new standing-protocol row, after the last
# /book editorial standard row ---
edit(
    "tools/_mob.txt",
    "| /book editorial standard — reader-as-experiencer voice rule | FTA pieces must address “you” as the person experiencing the condition, not the person structurally causing it — narrow relatability is a failure unless explicitly warranted for that specific state. |",
    "| /book editorial standard — reader-as-experiencer voice rule | FTA pieces must address “you” as the person experiencing the condition, not the person structurally causing it — narrow relatability is a failure unless explicitly warranted for that specific state. |\n\n| Demographic Applicability Filter — standing design protocol, NEW | Adopted this session (prompts/demographic-applicability-filter-protocol.md) after Cluster 4's SEC/nonprofit mismatch exposed a gap in the existing worked-dollar-figure plausibility check: a source can be real, verified, and correctly-sized, and still not apply to a given client at all -- the mechanism doesn't extend, which is not a magnitude problem. Runs BEFORE any dollar-plausibility check whenever a design decision anchors to a real external source (case law, agency data, an industry statistic, a specific statutory mechanism): state the assumption explicitly, find the source's own eligibility boundary, cross-check against PRV3's actual intake/demographic fields (confirmed against the real codebase this session, not assumed -- see Section 13a Cluster 4 entry for the schema pull), test at the extremes of the client range rather than the modal case, and gate the design explicitly if the assumption breaks anywhere in that range. This is the first formal MOB tracking of both this new protocol and the existing dollar-plausibility check as a paired standing requirement -- the dollar-plausibility check itself was previously only referenced inline within individual Decision Register/Priority Queue entries, never given its own row. Applies to all future PRV3 design work, not just Friction Tax. |",
)

# --- Section 13a Decision Register: new row for Cluster 4 finding,
# inserted after the last row in the table (Friction Tax output-ceiling
# plausibility) ---
edit(
    "tools/_mob.txt",
    "Gemini re-review of the rescale (attritional-only scope) -- once returned, CC implements; no further Pete-level decision expected on Option A itself unless Gemini's review surfaces a problem |",
    "Gemini re-review of the rescale (attritional-only scope) -- once returned, CC implements; no further Pete-level decision expected on Option A itself unless Gemini's review surfaces a problem |\n__CLUSTER4_ROW_PLACEHOLDER__",
)


def apply(dry_run: bool) -> int:
    changed = 0

    cluster4_row = (
        "| Cluster 4 (Whistleblower/regulatory) SEC-anchored ceiling -- CONFIRMED FLAWED, applicability not magnitude | 1 (Pete-designated via the Demographic Applicability Filter finding) | Open -- being reworked, NOT implementation-ready | Blocked on org_type-based gating design (or an explicit non-gated fallback) being decided | Cluster 4's ceiling (uncapped, sanction-driven, anchored to SEC whistleblower award data -- $1.9B+ since 2012, largest single award $279M) assumed SEC exposure applies broadly across PRV3's client base. Confirmed this session: the SEC has no jurisdiction over most of PRV3's actual clients -- nonprofits, government entities, privately held companies outside securities law -- at all, regardless of exposure magnitude. This is an applicability error, not a magnitude error (the $1.9B/$279M figures themselves remain real and verified) -- caught by the new Demographic Applicability Filter standing protocol (prompts/demographic-applicability-filter-protocol.md), adopted this session specifically because this case exposed a gap in the existing magnitude-only plausibility check. **Real intake schema pulled and confirmed this session** (engine/data/intake.py INTAKE_FIELDS, engine/accumulation.py IntakeData -- 6 fields: headcount, industry, org_type, jurisdictions, significant_events, principal_role): the field needed to gate this correctly is `org_type` -- 6 values (Founder-led, PE or VC-backed, Privately held professional leadership, Nonprofit, Publicly traded, Government) -- SEC whistleblower jurisdiction realistically applies to Publicly traded (and arguably PE/VC-backed with public debt, a nuance not yet resolved) but not to Nonprofit, Government, or the privately-held categories. `industry` (9 sector values, e.g. \"Nonprofit & Education\") is NOT the right field to gate on -- it conflates sector with legal status; a for-profit private school would also carry that industry value despite not being a nonprofit entity. Confirms Gemini's earlier claim that headcount is SUSB-midpoint-bucketed (engine/friction_tax.py HEADCOUNT_MIDPOINTS, Census SUSB 2022 data) -- true. Do NOT treat Cluster 4 as implementation-ready until org_type-based gating is designed. | This session (Claude Code) | Pete's call -- reopen Cluster 4 design once org_type-based gating (or an explicit non-gated fallback) is decided |\n"
    )

    for rel_path, old, new in EDITS:
        if "__CLUSTER4_ROW_PLACEHOLDER__" in new:
            new = new.replace("__CLUSTER4_ROW_PLACEHOLDER__", cluster4_row)
        path = REPO_ROOT / rel_path
        text = path.read_text(encoding="utf-8")
        count = text.count(old)
        if count != 1:
            print(f"ERROR: {rel_path} -- expected 1 match, found {count}")
            print(f"  old (first 120 chars): {old[:120]!r}")
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
