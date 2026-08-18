"""
MOB update -- severity follow-on gate: architecture reframe, not a fourth
falsified design. Documentation only, no engine code touched this session.

Replaces Section 13a's "Severity follow-on state scoping" row wholesale
(the prior row described designs 1/2 as falsified and design 3 as untested;
this session's verification found design 3 empirically doesn't over-apply,
but that all three designs operate at the wrong architectural layer --
SeverityResult has no per-state dimension, so no input-filtering design can
fix the defect regardless of which one is chosen). Also appends a new,
separate, low-priority row for a stale git worktree found incidentally this
session.

Re-verified fresh before writing: MOB header confirmed v4.185 (line 9),
CLAUDE.md cross-reference confirmed v4.185 (line 183), Section 13a's
severity row and true last row (the untracked-pile-deletion entry) both
confirmed via direct read immediately before this script was written.

Usage:
    python patch_mob_severity_gate_architecture_reframe.py --dry-run
    python patch_mob_severity_gate_architecture_reframe.py --write
"""
import argparse
import difflib
from pathlib import Path

MOB_PATH = Path("tools/_mob.txt")
CLAUDE_PATH = Path("CLAUDE.md")

OLD_SEVERITY_ROW = Path(
    "C:/Users/rizzo/AppData/Local/Temp/claude/c--Users-rizzo-PRV3/"
    "9354bfe3-2f47-478f-ac95-6d59ebb8dbc1/scratchpad/severity_row_old.txt"
).read_text(encoding="utf-8")

NEW_SEVERITY_ROW = (
    '| Severity follow-on state scoping (SEVER-19 and 31 more, 32 total) -- REFRAMED: not an '
    'input-filtering problem, an output-broadcast architecture gap | 3 | **REFRAMED, this session. '
    'All three candidate input-filtering designs (any-qualifying-state, top-1-only, static-intended-'
    'state-membership) confirmed unable to fix the defect -- not because the third design failed '
    'empirically the way the first two did, but because all three operate one layer above where the '
    'defect actually lives. Real fix requires restructuring SeverityResult itself, not filtering which '
    'inputs feed it. Not scoped, not designed, needs its own session.** | SeverityResult '
    '(engine/severity.py) has no per-state dimension -- until that\'s redesigned, no severity_input '
    'filter of any kind can prevent the resulting tier from being broadcast identically to every '
    'qualifying state regardless of which state the input was actually about | Third candidate design '
    '(static intended-state membership) verification-tested this session, real production path '
    '(accumulate_one_answer()/run_accumulated_engine()), same standard as designs 1 and 2. Reproduced '
    'against 3 real profiles spanning the support spectrum: ATT-UT-01 (the_untouchable, rank 58/58 in '
    'its own natural session, cleared_floor=False -- the weakest real case on record), ATT-BC-01 '
    '(the_burned_credibility, rank 33/58, cleared_floor=False), AUT-IA-01 '
    '(invisible_influence_architecture, rank 2/58, cleared_floor=True). Severity credited '
    'unconditionally in all three (the loosest possible reading of static-membership gating, to '
    'stress-test the specific failure mode: does a weakly-supported state get promoted into '
    'identified_states by severity credit). Result: it does not, in any case, including the extreme '
    '(rank 58/58, floor not cleared) -- confirmed the mechanism cannot promote a state into output '
    'under any of the three designs, because identified_states/routing is computed entirely by '
    'rank_states() + the signal-floor gate before severity_result is calculated at all '
    '(engine/main.py), and SeverityResult is explicitly documented and structured as one tier for the '
    'whole session with zero per-state field anywhere. **This is the real finding, and it reframes the '
    'whole investigation:** the ATT-UT-01 run\'s real output was identified_states = '
    '[the_overloaded_manager, invisible_performance_management, the_undefined_role, '
    'the_unformed_leader, the_dormant_talent, built_to_fail, the_paper_tiger] -- 7 states, none of '
    'them the_untouchable -- yet every one of those 7 received the same Endemic tier (score 100.0) '
    'that the severity input was substantively about the_untouchable\'s specific-manager-protected-by-'
    'politics scenario, via engine/output.py\'s build_private_block(qs, severity_result), called '
    'identically per qualified state with the same session-global severity_result object. This is the '
    'same shape as the original AUT-PS-01 defect that started this whole investigation (severity '
    'firing with zero per-state awareness, landing Endemic instead of the locked Entrenched) -- '
    'reproduced here at architecture scale, and confirmed structurally unfixable by any input-'
    'filtering design: a membership/rank/score filter can only decide whether an input counts toward '
    'the shared pool, never which state the resulting number gets attached to, because the '
    'architecture has no per-state severity concept to attach it to. **Real fix direction, not '
    'designed:** restructure SeverityResult/build_private_block() to carry severity per-state rather '
    'than one shared tier broadcast to every qualifying state. Explicitly not scoped, not designed, no '
    'build plan -- this entry records the finding and the direction only. Needs its own dedicated '
    'session to scope, then a Gemini architecture review before any code, per the Tier 3 Workflow '
    'Governance model (touches a core engine data contract, SeverityResult, consumed by every '
    'downstream output path). **Coverage finding, related but separable:** of 32 live '
    'severity_trigger IDs (55 individual option-instances) in engine/data/questions.py, only 14 have '
    'ever been individually assessed for this leak pattern at all (SEVER-02, 10, 17, 18, 19, 20, 21, '
    '22, 23, 24, 25, 27, 28, 29 -- the original investigation\'s scope). SEVER-05 was explicitly '
    'assessed and found out-of-scope (a different, unrelated defect -- never calibration-tested for '
    'either wired state). SEVER-13 was explicitly assessed and found clean. The remaining 16 have '
    'never been checked either way: SEVER-01, 03, 04, 06, 07, 08, 09, 11, 12, 14, 15, 16, 26, 30, 31, '
    '32. Whatever verification accompanies the eventual per-state redesign needs to cover all 32, not '
    'just the original 14 -- the 16 unchecked IDs are not confirmed safe, just unexamined. '
    '**Scaffolding status, confirmed this session:** tools/patch_severity_follow_on_state_scoping.py '
    'remains uncommitted, unapplied -- now confirmed to encode the top-1-only design (already '
    'falsified for stripping legitimate triggers) and, more fundamentally, to operate at the wrong '
    'architectural layer regardless of which of the three input-filtering designs it encoded. A '
    'future session should not pick this file up assuming it\'s a viable starting point without '
    'reading this entry first. tools/verify_static_membership_gate_design3.py (this session\'s '
    'verification script) also left uncommitted, same convention -- investigation scaffolding, not a '
    'build artifact. | This session (Claude Code), 2026-08-18 | Not a forced check-in, but the framing '
    'has changed materially -- do not resume this as "try a fourth input-filtering design." Next real '
    'step is scoping the SeverityResult per-state redesign as its own session, then Gemini review, '
    'before any code. The 16-ID coverage gap should be folded into that same redesign\'s verification '
    'pass rather than assessed separately first. |\n'
)

WORKTREE_ROW = (
    '| Stale git worktree found incidentally -- .claude/worktrees/agent-a45f286990d2481e9, checked '
    'out at old commit 3dfd965 | 3 | **OPEN, not investigated, not touched. Low priority, no forced '
    'check-in.** | Unclear whether this is abandoned scaffolding safe to remove, or intentional and '
    'still in use by another agent/process -- needs a look before any action | Surfaced incidentally '
    'during the severity-gate verification session (2026-08-18) while searching tracked source for '
    'cross-references. `git worktree list` confirmed it\'s a genuine second worktree, not a stray '
    'directory, checked out at commit 3dfd965 -- a commit predating this session\'s own work by '
    'several sessions (before the 13a/13b reconciliation, mojibake fix, gitignore addition, and '
    'untracked-pile deletion all landed on main). Not investigated further, not touched. Someone '
    'should check whether it\'s abandoned scaffolding (safe to remove via `git worktree remove`) or '
    'something intentional/still in use before any action is taken. | This session (Claude Code), '
    '2026-08-18 | No forced check-in, low priority. Worth a look next time someone is doing git '
    'housekeeping, not urgent. |\n'
)

REPLACEMENTS = [
    (
        CLAUDE_PATH,
        "CLAUDE.md MOB version cross-reference",
        "| MOB version | v4.185 |",
        "| MOB version | v4.186 |",
    ),
    (
        MOB_PATH,
        "replace severity follow-on state scoping row wholesale",
        OLD_SEVERITY_ROW,
        NEW_SEVERITY_ROW.rstrip("\n"),
    ),
    (
        MOB_PATH,
        "append stale-worktree row at end of Section 13a",
        "This session (Claude Code), 2026-08-18 | Closed, no further check-in "
        "needed on the 76 deleted. The 15 held-back files are their own future consideration -- not "
        "scheduled, Pete's call on when to update their citing comments and revisit removal. |\n",
        "This session (Claude Code), 2026-08-18 | Closed, no further check-in "
        "needed on the 76 deleted. The 15 held-back files are their own future consideration -- not "
        "scheduled, Pete's call on when to update their citing comments and revisit removal. |\n"
        + WORKTREE_ROW,
    ),
]


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    file_texts = {}
    for path, _label, _old, _new in REPLACEMENTS:
        if path not in file_texts:
            file_texts[path] = path.read_text(encoding="utf-8")

    for path, label, old, new in REPLACEMENTS:
        text = file_texts[path]
        count = text.count(old)
        if count != 1:
            raise SystemExit(
                f"ABORT [{label}] in {path}: expected exactly 1 match, found {count}"
            )
        file_texts[path] = text.replace(old, new, 1)

    mob_text = file_texts[MOB_PATH]
    mob_lines = mob_text.split("\n")
    header_idx = 8
    assert mob_lines[header_idx].endswith("MOB v4.185"), (
        f"ABORT [header bump]: line 9 does not end with 'MOB v4.185': {mob_lines[header_idx]!r}"
    )
    mob_lines[header_idx] = mob_lines[header_idx].replace("v4.185", "v4.186")
    file_texts[MOB_PATH] = "\n".join(mob_lines)

    for path, new_text in file_texts.items():
        original = path.read_text(encoding="utf-8")
        if args.dry_run:
            print(f"\n{'=' * 80}\nDIFF: {path}\n{'=' * 80}")
            diff = difflib.unified_diff(
                original.splitlines(keepends=True),
                new_text.splitlines(keepends=True),
                fromfile=f"{path} (before)",
                tofile=f"{path} (after)",
            )
            print("".join(diff))
        else:
            path.write_text(new_text, encoding="utf-8")
            print(f"WROTE: {path}")

    if args.dry_run:
        print("\nDry run complete. No files written. Re-run with --write to apply.")


if __name__ == "__main__":
    main()
