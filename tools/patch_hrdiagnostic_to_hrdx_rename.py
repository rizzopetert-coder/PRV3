"""
Domain rename: hrdiagnostic.com -> hr-dx.com (hrdiagnostic.com and hrdx.com
were both unavailable, per Pete). Updates every live reference to the old
domain string across web/, engine/, and tools/_mob.txt's one currently-open
backlog line.

Scope, per repo-wide grep (17 files matched "hrdiagnostic" case-
insensitive, reported in full before this script was written):
- web/lib/brand.ts: HR_DIAGNOSTIC_HOSTS Set values -- the actual functional
  change, everything else in this script is comment/doc correctness.
- 8 comment references across web/ (middleware.ts, types.ts,
  diagnostic-completion.ts, diagnostic-completion.test.ts,
  PrivateOutput.tsx x2, tactical-referrals.ts, tactical-question-meta.ts)
  and 2 in engine/data/questions.py -- all say "hrdiagnostic.com" or
  "HRdiagnostic.com" with the literal domain, now factually wrong.
- tools/_mob.txt:1515 -- the ATT-* backlog bullet logged this session,
  still open, references "HRdiagnostic.com Tactical & Compliance module".

Deliberately NOT touched (a judgment call reported to Pete, not decided
silently): the historical patch_*.py scripts from this session
(patch_hrdiagnostic_tc_wiring.py, patch_hrdiagnostic_hostname_branding.py,
patch_hrdiagnostic_routing_walloff.py,
patch_hrdiagnostic_debug_brand_override.py, patch_engine_tc_questions.py,
patch_mob_att_prominence_backlog.py, _gen_tactical_meta.py) and their
filenames. These are immutable audit trail of what was actually run --
hrdiagnostic.com was genuinely the domain in play at the time, matching
this repo's own established convention of never retroactively rewriting
already-applied patch scripts when project state later moves on.

Usage:
    python tools/patch_hrdiagnostic_to_hrdx_rename.py --dry-run
    python tools/patch_hrdiagnostic_to_hrdx_rename.py --write
"""
import argparse
import pathlib
import sys

EDITS = [
    (
        pathlib.Path('web/lib/brand.ts'),
        [(
            '''const HR_DIAGNOSTIC_HOSTS = new Set([
  "hrdiagnostic.com",
  "www.hrdiagnostic.com",
]);''',
            '''const HR_DIAGNOSTIC_HOSTS = new Set([
  "hr-dx.com",
  "www.hr-dx.com",
]);''',
            'HR_DIAGNOSTIC_HOSTS Set values',
        )],
    ),
    (
        pathlib.Path('web/middleware.ts'),
        [(
            ' * explicitly hrdiagnostic.com) is completely unaffected: every path',
            ' * explicitly hr-dx.com) is completely unaffected: every path',
            'header comment',
        )],
    ),
    (
        pathlib.Path('web/lib/types.ts'),
        [(
            '// HRdiagnostic.com only. Assembled server-side at session completion',
            '// hr-dx.com only. Assembled server-side at session completion',
            'TacticalSectionResult header comment',
        )],
    ),
    (
        pathlib.Path('web/lib/diagnostic-completion.ts'),
        [(
            '// HRdiagnostic.com only. Resolves session.answers_log\'s TC-* entries into',
            '// hr-dx.com only. Resolves session.answers_log\'s TC-* entries into',
            'resolveTacticalResults() header comment',
        )],
    ),
    (
        pathlib.Path('web/lib/diagnostic-completion.test.ts'),
        [(
            '// resolveTacticalResults() (HRdiagnostic.com only), this session.',
            '// resolveTacticalResults() (hr-dx.com only), this session.',
            'file header comment',
        )],
    ),
    (
        pathlib.Path('web/components/PrivateOutput.tsx'),
        [
            (
                '  // HRdiagnostic.com only -- undefined for every principal_resolution',
                '  // hr-dx.com only -- undefined for every principal_resolution',
                'tacticalResults prop comment',
            ),
            (
                '      {/* Block 8 -- Tactical & Compliance results (HRdiagnostic.com only).',
                '      {/* Block 8 -- Tactical & Compliance results (hr-dx.com only).',
                'Block 8 JSX comment',
            ),
        ],
    ),
    (
        pathlib.Path('web/data/tactical-referrals.ts'),
        [(
            ' * HRdiagnostic.com-only: per-section OneDigital referral mapping for the',
            ' * hr-dx.com-only: per-section OneDigital referral mapping for the',
            'file header comment',
        )],
    ),
    (
        pathlib.Path('web/data/tactical-question-meta.ts'),
        [(
            ' * HRdiagnostic.com-only. Minimal per-question metadata that has NO home',
            ' * hr-dx.com-only. Minimal per-question metadata that has NO home',
            'file header comment',
        )],
    ),
    (
        pathlib.Path('engine/data/questions.py'),
        [
            (
                '    # -- Tactical & Compliance module (TC-*), hrdiagnostic.com only --------',
                '    # -- Tactical & Compliance module (TC-*), hr-dx.com only --------',
                '_QDATA section comment',
            ),
            (
                '  # TC-* module, hrdiagnostic.com only, 40 total\n',
                '  # TC-* module, hr-dx.com only, 40 total\n',
                'TACTICAL_QUESTION_IDS trailing comment',
            ),
        ],
    ),
    (
        pathlib.Path('tools/_mob.txt'),
        [(
            '(HRdiagnostic.com Tactical & Compliance module, all zero-signal)',
            '(hr-dx.com Tactical & Compliance module, all zero-signal)',
            'ATT-* backlog bullet',
        )],
    ),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    file_contents = {}

    for path, edits in EDITS:
        content = path.read_text(encoding='utf-8')
        new_content = content
        for old, new, label in edits:
            count = new_content.count(old)
            if count != 1:
                print(f'ERROR: {path} :: {label} anchor found {count} times, expected 1.', file=sys.stderr)
                sys.exit(1)
            new_content = new_content.replace(old, new, 1)
            print(f'[{path} :: {label}]')
        file_contents[path] = new_content

    if args.dry_run:
        print('\nDRY RUN -- all anchors found, all edits would apply cleanly. Nothing written.')
    else:
        for path, content in file_contents.items():
            path.write_text(content, encoding='utf-8')
            print(f'WROTE: {path}')


if __name__ == '__main__':
    main()
