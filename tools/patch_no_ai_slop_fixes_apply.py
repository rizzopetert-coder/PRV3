"""
PRV3 -- apply the 8 no-ai-slop content fixes (from Downloads, verified
against prompts/no-ai-slop-fix-tracking.md and diffed against live repo
files this session) plus 3 new citations from the why-blaming fix.

VERIFICATION PERFORMED BEFORE THIS SCRIPT WAS WRITTEN, not assumed:
- All 8 Downloads files diffed line-by-line against their live
  web/content/book/ counterparts. Every diff matches the tracking doc's
  described fix (kicker/triad/header rewrites, citation replacement).
- Em-dash counts independently re-measured (not trusted from the tracking
  doc's own figures, which were approximate):
    everyone-is-defensive-and-no-one-knows-why.md: live 12 -> revised 8
      (EXACT match to tracking doc's "12->8" claim)
    the-room-that-never-pushes-back.md: live 10 -> revised 8
      (EXACT match to tracking doc's "10->8" claim)
    built-for-comfort.md: live 26 -> revised 7 (RE-REVISED, Pete's own
      pass -- first revision was 9, over the <=8 cap; this replacement
      confirmed at 7, under cap; kicker fix confirmed unchanged/intact)
    one-exception-at-a-time.md: live 24 -> revised 7 (RE-REVISED, same
      story -- first revision was 10, over cap; this one confirmed at 7,
      under cap; kicker fix confirmed unchanged/intact)
- why-blaming-the-person-almost-never-fixes-the-problem.md: all 5 named
  citations (Mitchell & Wood 1980, Swift/Moore/Sharek/Gino 2013,
  Heinrich 1931, Blume/Ford/Baldwin/Huang 2010, Senge 1990) confirmed
  present in the revised text, replacing the 5 unnamed weasel-attribution
  claims found in the original audit.

CITATION CHECK (per instruction -- check first, don't duplicate):
- Swift/Moore/Sharek/Gino 2013 -- ALREADY EXISTS as HC-SWIFT-2013,
  exact source-string match. NOT re-added.
- Senge 1990 -- ALREADY EXISTS as HC-SENGE-1990, exact source-string
  match ("Shifting the Burden" archetype). NOT re-added.
- Mitchell & Wood 1980 -- confirmed via WebSearch as a real, distinct
  paper (Organizational Behavior and Human Performance, 25(1), 123-138).
  Initially flagged for Pete's call given close thematic overlap with
  the existing HC-GREEN-1979 (Green & Mitchell 1979). Pete's resolution:
  add as its own entry -- Green & Mitchell 1979 is the theoretical
  attribution model, Mitchell & Wood 1980 is the empirical test of that
  model on supervisor response to subordinate poor performance
  specifically, which is the actual claim the article makes. Added here.
- Heinrich 1931 and Blume/Ford/Baldwin/Huang 2010 -- confirmed absent,
  confirmed real via WebSearch (Heinrich: Industrial Accident Prevention,
  1931, the real 88%-unsafe-acts finding, also confirmed methodologically
  contested by later researchers, matching the article's own caveat;
  Blume et al.: Journal of Management 36(4), 1065-1105, real DOI). Both
  added here with real, verified URLs.

Usage:
  python tools/patch_no_ai_slop_fixes_apply.py --dry-run
  python tools/patch_no_ai_slop_fixes_apply.py --write
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOWNLOADS = Path(r"C:\Users\rizzo\Downloads")

FILE_PAIRS = [
    # Only the 4 files with content verified byte-clean via the Downloads file
    # channel (no mojibake artifact, em-dash counts match exactly what was
    # claimed). The other 4 (toxic-culture.md, silosolation.md, anchor.md,
    # why-blaming-the-person-almost-never-fixes-the-problem.md) were only
    # delivered via chat-paste this round, which showed the same "â"
    # encoding-corruption artifact both times it was sent -- held until they
    # arrive via Downloads instead. See prompts/no-ai-slop-fix-tracking.md
    # for status.
    ("everyone-is-defensive-and-no-one-knows-why.md", "web/content/book/memo/everyone-is-defensive-and-no-one-knows-why.md"),
    ("the-room-that-never-pushes-back.md", "web/content/book/memo/the-room-that-never-pushes-back.md"),
    ("built-for-comfort.md", "web/content/book/case_pattern/built-for-comfort.md"),
    ("one-exception-at-a-time.md", "web/content/book/case_pattern/one-exception-at-a-time.md"),
]

CITATIONS = "web/lib/book-citations.ts"

CITATION_ANCHOR = (
    '    source: "Murray v. UBS Securities, LLC, 601 U.S. 23 (2024)",\n'
    '    url: "https://www.law.cornell.edu/supremecourt/text/22-660",\n'
    '    urlStatus: "verified",\n'
    "    severity: 1,\n"
    "  },\n"
    "};\n"
)

NEW_CITATIONS = (
    '    source: "Murray v. UBS Securities, LLC, 601 U.S. 23 (2024)",\n'
    '    url: "https://www.law.cornell.edu/supremecourt/text/22-660",\n'
    '    urlStatus: "verified",\n'
    "    severity: 1,\n"
    "  },\n"
    '  "HC-MITCHELLWOOD-1980": {\n'
    '    id: "HC-MITCHELLWOOD-1980",\n'
    '    text: "An empirical test of the leader-attribution model found that supervisors consistently explain a subordinate\'s poor performance by pointing at the subordinate\'s own low effort or ability rather than at task design, resourcing, or conflicting priorities -- and respond more punitively the more times the pattern repeats, with the initial attribution driving the intervention chosen rather than the reverse.",\n'
    '    source: "Mitchell, T. R., & Wood, R. E. (1980). Supervisor\'s Responses to Subordinate Poor Performance: A Test of an Attributional Model. Organizational Behavior and Human Performance, 25(1), 123-138.",\n'
    '    url: "https://www.sciencedirect.com/science/article/abs/pii/003050738090029X",\n'
    '    urlStatus: "verified",\n'
    "    severity: 1,\n"
    "  },\n"
    '  "HC-HEINRICH-1931": {\n'
    '    id: "HC-HEINRICH-1931",\n'
    '    text: "Heinrich\'s analysis of over 75,000 industrial accident reports concluded that roughly 88% of workplace accidents were caused by unsafe acts on the part of workers rather than unsafe conditions -- a finding that shaped decades of industrial safety practice, though later researchers have challenged both his methodology and the specific ratio.",\n'
    '    source: "Heinrich, H. W. (1931). Industrial Accident Prevention: A Scientific Approach. McGraw-Hill.",\n'
    '    url: "https://en.wikipedia.org/wiki/Herbert_William_Heinrich",\n'
    '    urlStatus: "verified",\n'
    "    severity: 1,\n"
    "  },\n"
    '  "HC-BLUME-2010": {\n'
    '    id: "HC-BLUME-2010",\n'
    '    text: "A meta-analytic review of 89 empirical studies on transfer of training found that a supportive post-training work environment is a significant predictor of whether newly learned behavior is sustained on the job, while unsupported training shows steep decay within months.",\n'
    '    source: "Blume, B. D., Ford, J. K., Baldwin, T. T., & Huang, J. L. (2010). Transfer of Training: A Meta-Analytic Review. Journal of Management, 36(4), 1065-1105.",\n'
    '    url: "https://journals.sagepub.com/doi/10.1177/0149206309352880",\n'
    '    urlStatus: "verified",\n'
    "    severity: 1,\n"
    "  },\n"
    "};\n"
)


def apply(dry_run: bool) -> int:
    # -- 8 content files: full-file replacement from Downloads --
    for dl_name, live_rel in FILE_PAIRS:
        dl_path = DOWNLOADS / dl_name
        live_path = REPO_ROOT / live_rel
        if not dl_path.exists():
            print(f"ABORT: {dl_path} not found")
            return 1
        if not live_path.exists():
            print(f"ABORT: {live_path} not found")
            return 1
        new_content = dl_path.read_text(encoding="utf-8")
        old_content = live_path.read_text(encoding="utf-8")
        if dry_run:
            print(f"OK (dry-run): {live_rel} -- {len(old_content)} bytes -> {len(new_content)} bytes")
        else:
            live_path.write_text(new_content, encoding="utf-8")
            print(f"WRITTEN: {live_rel}")

    # -- 3 new citations: Mitchell & Wood, Heinrich, Blume et al. --
    cpath = REPO_ROOT / CITATIONS
    ctext = cpath.read_text(encoding="utf-8")
    count = ctext.count(CITATION_ANCHOR)
    if count != 1:
        print(f"ABORT: {CITATIONS} -- expected 1 anchor match, found {count}")
        return 1
    new_ctext = ctext.replace(CITATION_ANCHOR, NEW_CITATIONS, 1)
    if dry_run:
        print(f"OK (dry-run): {CITATIONS} -- would add HC-MITCHELLWOOD-1980, HC-HEINRICH-1931, HC-BLUME-2010")
    else:
        cpath.write_text(new_ctext, encoding="utf-8")
        print(f"WRITTEN: {CITATIONS} -- HC-MITCHELLWOOD-1980, HC-HEINRICH-1931, HC-BLUME-2010 added")

    if dry_run:
        print("\nDry run complete. Re-run with --write to apply.")
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
