"""
web/app/diagnostic/page.tsx: wire SelfSelectIntakeModal into
SelfSelectionInterface. Four anchored edits, applied atomically (all
four must match or nothing is written):

  1. Import SelfSelectIntakeModal.
  2. Add isIntakeModalOpen state.
  3. handleTakeDiagnostic() now takes the collected intake as a
     parameter instead of hardcoding a blank one; new
     handleIntakeSubmit() closes the modal and forwards to it.
  4. Phase 4 CTA opens the modal instead of calling
     handleTakeDiagnostic() directly; modal rendered at the end of the
     component's JSX tree (a fixed-overlay component, position doesn't
     affect layout).

Usage:
    python tools/patch_wire_self_select_intake_modal.py --dry-run
    python tools/patch_wire_self_select_intake_modal.py --write
"""
import argparse
import pathlib
import sys

PATH = pathlib.Path('web/app/diagnostic/page.tsx')

EDIT_1_OLD = '''import DiagnosticFlow from "@/components/DiagnosticFlow";'''
EDIT_1_NEW = '''import DiagnosticFlow from "@/components/DiagnosticFlow";
import SelfSelectIntakeModal from "@/components/SelfSelectIntakeModal";'''

EDIT_2_OLD = '''  const [intakeForShare, setIntakeForShare] = useState<EnginePayload["intake"] | null>(null);
  const [isLoadingResult, setIsLoadingResult] = useState(false);'''
EDIT_2_NEW = '''  const [intakeForShare, setIntakeForShare] = useState<EnginePayload["intake"] | null>(null);
  const [isLoadingResult, setIsLoadingResult] = useState(false);
  const [isIntakeModalOpen, setIsIntakeModalOpen] = useState(false);'''

EDIT_3_OLD = '''  async function handleTakeDiagnostic() {
    if (selectedStateIds.size === 0) return;
    const intake: EnginePayload["intake"] = {
      headcount: "",
      industry: "",
      orgType: "",
      jurisdictions: [],
      significantEvents: [],
      principalRole: "",
    };
    setIntakeForShare(intake);
    setIsLoadingResult(true);
    try {
      const res = await fetch("/api/result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selectedStateIds: [...selectedStateIds], intake }),
      });
      if (!res.ok) return;
      const payload = (await res.json()) as PrivateOutputPayload;
      setResultPayload(payload);
      onPhaseAdvance(5);
    } finally {
      setIsLoadingResult(false);
    }
  }'''
EDIT_3_NEW = '''  // Real intake (headcount, industry, org_type, jurisdictions) now
  // collected via SelfSelectIntakeModal before this runs -- previously
  // hardcoded entirely blank here, which this session's earlier
  // engine-side fix made degrade cleanly rather than 500, but still
  // meant no self-select result was ever priced.
  async function handleTakeDiagnostic(intake: EnginePayload["intake"]) {
    if (selectedStateIds.size === 0) return;
    setIntakeForShare(intake);
    setIsLoadingResult(true);
    try {
      const res = await fetch("/api/result", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ selectedStateIds: [...selectedStateIds], intake }),
      });
      if (!res.ok) return;
      const payload = (await res.json()) as PrivateOutputPayload;
      setResultPayload(payload);
      onPhaseAdvance(5);
    } finally {
      setIsLoadingResult(false);
    }
  }

  function handleIntakeSubmit(intake: EnginePayload["intake"]) {
    setIsIntakeModalOpen(false);
    handleTakeDiagnostic(intake);
  }'''

EDIT_4_OLD = '''              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handleTakeDiagnostic}
                  disabled={isLoadingResult}
                  className="flex-1 bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {isLoadingResult ? "Synthesizing…" : uiCopy.diagnosticCTA}
                </button>
                <button className="flex-1 border border-charcoal text-charcoal font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-100 transition-colors">
                  {uiCopy.conversationCTA}
                </button>
              </div>
            </div>
          )}

        </div>
      </main>'''
EDIT_4_NEW = '''              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => setIsIntakeModalOpen(true)}
                  disabled={isLoadingResult}
                  className="flex-1 bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-60 disabled:cursor-not-allowed"
                >
                  {isLoadingResult ? "Synthesizing…" : uiCopy.diagnosticCTA}
                </button>
                <button className="flex-1 border border-charcoal text-charcoal font-ui text-sm font-medium px-5 py-3 rounded-lg hover:bg-gray-100 transition-colors">
                  {uiCopy.conversationCTA}
                </button>
              </div>
            </div>
          )}

        </div>
      </main>

      <SelfSelectIntakeModal
        open={isIntakeModalOpen}
        onClose={() => setIsIntakeModalOpen(false)}
        onSubmit={handleIntakeSubmit}
      />'''

EDITS = [
    ('import SelfSelectIntakeModal', EDIT_1_OLD, EDIT_1_NEW),
    ('isIntakeModalOpen state', EDIT_2_OLD, EDIT_2_NEW),
    ('handleTakeDiagnostic signature + handleIntakeSubmit', EDIT_3_OLD, EDIT_3_NEW),
    ('Phase 4 CTA + modal render', EDIT_4_OLD, EDIT_4_NEW),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    content = PATH.read_text(encoding='utf-8')

    errors = []
    for label, old, new in EDITS:
        count = content.count(old)
        if count != 1:
            errors.append(f'"{label}": anchor found {count} times, expected exactly 1.')

    if errors:
        for e in errors:
            print(f'ERROR: {e}', file=sys.stderr)
        sys.exit(1)

    new_content = content
    for label, old, new in EDITS:
        new_content = new_content.replace(old, new, 1)

    if args.dry_run:
        print(f'DRY RUN -- all {len(EDITS)} anchors found exactly once, replacement would apply cleanly.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')
    else:
        PATH.write_text(new_content, encoding='utf-8')
        print(f'WRITE complete -- {len(EDITS)} edits applied.')
        print(f'Old length: {len(content)}, new length: {len(new_content)}, delta: {len(new_content) - len(content)}')


if __name__ == '__main__':
    main()
