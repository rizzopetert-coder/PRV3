"""
HRdiagnostic.com -- wire the Tactical & Compliance module end to end.
Confirmed against live source before writing, not assumed:

- session.question_sequence (session-store.ts) is the real per-session
  routing array the answer route reads/writes directly (indexOf,
  isLastQuestionInSequence, next-question lookup) -- confirmed via
  grep, every consumer reads session.question_sequence, never the
  static PHASE_1_QUESTION_SEQUENCE template directly. Appending TC-*
  IDs there is the correct, minimal integration point; the base
  PHASE_1_QUESTION_SEQUENCE constant itself is never touched.
- isLastQuestion is fully dynamic (currentIndex === sequence.length - 1,
  confirmed in isLastQuestionInSequence()'s own body) -- not a hardcoded
  "Q34" check. Appending 40 TC questions correctly pushes completion
  (and narrative modulation's own end-of-sequence trigger) to the last
  TC question, not a stale midpoint.
- get_question_copy()'s own docstring states the established principle:
  question text/options are never hand-duplicated in TypeScript, fetched
  live via invokeQuestionCopy() instead. TC results resolution follows
  the same pattern -- question_text/option_text come from a fresh
  invokeQuestionCopy() call per TC-* answer at completion time, not a
  static TS mirror. Only "intent" (which has no engine-side existence at
  all -- confirmed not a QuestionDefinition field) gets a small,
  narrowly-scoped TS lookup (web/data/tactical-question-meta.ts,
  generated separately).
- enableEngage defaults true and DiagnosticFlow.tsx never overrides it --
  confirmed via grep. The "Start the engagement" CTA (-> /engage, which
  Part A's middleware already blocks on hr_diagnostic) would otherwise be
  a second dead-link surprise, same class as the self-select gate found
  and fixed last pass. Suppressed here via the same useBrand() already
  imported into PrivateOutput.tsx.

Usage:
    python tools/patch_hrdiagnostic_tc_wiring.py --dry-run
    python tools/patch_hrdiagnostic_tc_wiring.py --write
"""
import argparse
import pathlib
import sys

# ---------------------------------------------------------------------------
# web/lib/types.ts -- new shared type for the TC results response shape.
# ---------------------------------------------------------------------------
TYPES_PATH = pathlib.Path('web/lib/types.ts')
TYPES_ANCHOR_OLD = 'export interface PrivateOutputPayload {\n'
TYPES_ANCHOR_NEW = '''// HRdiagnostic.com only. Assembled server-side at session completion
// (web/lib/diagnostic-completion.ts) from session.answers_log's TC-*
// entries -- never part of the Python engine's own PrivateOutputPayload,
// since these questions carry zero scoring signal and the engine has no
// concept of "section" or "referral." question_text/selected_option_text
// come from a live invokeQuestionCopy() call per answer, matching this
// codebase's standing principle that question copy is never hand-
// duplicated in TypeScript -- only intent (no engine-side existence at
// all) and referral (a pure frontend/business concern) are TS-native.
export interface TacticalAnswerResult {
  question_id: string;
  question_text: string;
  selected_option_text: string;
  intent: string;
}

export interface TacticalSectionResult {
  question_set_id: string;
  referral: string[];
  answers: TacticalAnswerResult[];
}

export interface PrivateOutputPayload {
'''

# ---------------------------------------------------------------------------
# web/lib/session-store.ts -- brand field + brand-conditional sequence.
# ---------------------------------------------------------------------------
SESSION_STORE_PATH = pathlib.Path('web/lib/session-store.ts')

SS_IMPORTS_OLD = '''import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import type { PrivateIntakeEcho } from "@/lib/types";
import type { SeverityInputPayload } from "@/lib/engine-client";'''
SS_IMPORTS_NEW = '''import { Redis } from "@upstash/redis";
import { nanoid } from "nanoid";
import type { PrivateIntakeEcho } from "@/lib/types";
import type { SeverityInputPayload } from "@/lib/engine-client";
import type { Brand } from "@/lib/brand";
import { TACTICAL_QUESTION_META } from "@/data/tactical-question-meta";'''

SS_INTERFACE_OLD = '''export interface DiagnosticSession {
  session_id: string;
  intake: PrivateIntakeEcho;'''
SS_INTERFACE_NEW = '''export interface DiagnosticSession {
  session_id: string;
  // Resolved once at createSession() time from the request's Host header
  // and persisted for the session's full lifetime (a multi-request flow) --
  // re-deriving it per request would be redundant and risks inconsistency
  // if a request ever arrived without the header. Drives whether TC-*
  // questions are appended to question_sequence below and whether
  // diagnostic-completion.ts resolves tactical_results.
  brand: Brand;
  intake: PrivateIntakeEcho;'''

SS_CREATESESSION_OLD = '''export async function createSession(intake: PrivateIntakeEcho): Promise<DiagnosticSession> {
  const session: DiagnosticSession = {
    session_id: nanoid(),
    intake,
    next_question_id: PHASE_1_QUESTION_SEQUENCE[0],
    accumulated_vector: { ...ZERO_VECTOR },
    answers_log: [],
    status: "in_progress",
    checkpoint_q11: null,
    checkpoint_q19: null,
    checkpoint_q27: null,
    question_sequence: [...PHASE_1_QUESTION_SEQUENCE],'''
SS_CREATESESSION_NEW = '''export async function createSession(
  intake: PrivateIntakeEcho,
  // Defaulted, not required -- session-store.test.ts and
  // session/undo/route.test.ts call createSession(FAKE_INTAKE) at 8 sites
  // with no brand argument, exercising undo logic that has nothing to do
  // with brand/TC behavior. Forcing a required param would mean editing
  // 8 unrelated test call sites for no behavioral gain; the real
  // production caller (session/start/route.ts) always passes an explicit
  // resolved brand, so this default is never silently relied on in the
  // actual request path.
  brand: Brand = "principal_resolution",
): Promise<DiagnosticSession> {
  // TC-* module appended only for hr_diagnostic -- the base
  // PHASE_1_QUESTION_SEQUENCE template is never mutated, matching its own
  // "never mutated" doc comment above. Order matches the JSON's own
  // question_sets array order (10 sections x 4 questions), not
  // re-sorted or interleaved.
  const questionSequence =
    brand === "hr_diagnostic"
      ? [...PHASE_1_QUESTION_SEQUENCE, ...Object.keys(TACTICAL_QUESTION_META)]
      : [...PHASE_1_QUESTION_SEQUENCE];

  const session: DiagnosticSession = {
    session_id: nanoid(),
    brand,
    intake,
    next_question_id: questionSequence[0],
    accumulated_vector: { ...ZERO_VECTOR },
    answers_log: [],
    status: "in_progress",
    checkpoint_q11: null,
    checkpoint_q19: null,
    checkpoint_q27: null,
    question_sequence: questionSequence,'''

SESSION_STORE_EDITS = [
    (SS_IMPORTS_OLD, SS_IMPORTS_NEW, 'imports'),
    (SS_INTERFACE_OLD, SS_INTERFACE_NEW, 'DiagnosticSession.brand field'),
    (SS_CREATESESSION_OLD, SS_CREATESESSION_NEW, 'createSession() brand param + conditional sequence'),
]

# ---------------------------------------------------------------------------
# web/app/api/diagnostic/session/start/route.ts -- resolve + pass brand.
# ---------------------------------------------------------------------------
START_ROUTE_PATH = pathlib.Path('web/app/api/diagnostic/session/start/route.ts')

START_IMPORT_OLD = '''import { createSession, resolveQuestionLabel } from "@/lib/session-store";'''
START_IMPORT_NEW = '''import { createSession, resolveQuestionLabel } from "@/lib/session-store";
import { resolveBrand } from "@/lib/brand";'''

START_CALL_OLD = '''  const session = await createSession(body);'''
START_CALL_NEW = '''  const brand = resolveBrand(request.headers.get("host"));
  const session = await createSession(body, brand);'''

START_ROUTE_EDITS = [
    (START_IMPORT_OLD, START_IMPORT_NEW, 'import resolveBrand'),
    (START_CALL_OLD, START_CALL_NEW, 'resolve brand, pass to createSession'),
]

# ---------------------------------------------------------------------------
# web/lib/diagnostic-completion.ts -- resolve TC results at completion.
# ---------------------------------------------------------------------------
COMPLETION_PATH = pathlib.Path('web/lib/diagnostic-completion.ts')

COMPLETION_IMPORTS_OLD = '''import { NextResponse } from "next/server";
import { completeSession, type DiagnosticSession } from "@/lib/session-store";
import { invokeComplete } from "@/lib/engine-client";
import type {
  PrivateOutputPayload,
  StateRef,
  SynthesisFields,
} from "@/lib/types";
import { translateResolutionFamily } from "@/lib/resolution-family";'''
COMPLETION_IMPORTS_NEW = '''import { NextResponse } from "next/server";
import { completeSession, type DiagnosticSession } from "@/lib/session-store";
import { invokeComplete, invokeQuestionCopy } from "@/lib/engine-client";
import type {
  PrivateOutputPayload,
  StateRef,
  SynthesisFields,
  TacticalSectionResult,
} from "@/lib/types";
import { translateResolutionFamily } from "@/lib/resolution-family";
import { TACTICAL_QUESTION_META } from "@/data/tactical-question-meta";
import { getTacticalReferrals } from "@/data/tactical-referrals";

// HRdiagnostic.com only. Resolves session.answers_log's TC-* entries into
// display-ready results, grouped by section. Fetches question_text/
// option_text live via invokeQuestionCopy() (one call per answered TC
// question, run concurrently) -- matches this codebase's standing
// principle that question copy is never hand-duplicated in TypeScript
// (get_question_copy()'s own docstring, engine/main.py). intent and
// question_set_id have no engine-side existence, so those come from the
// small TS-only lookup (web/data/tactical-question-meta.ts) instead.
async function resolveTacticalResults(
  session: DiagnosticSession,
): Promise<TacticalSectionResult[] | undefined> {
  if (session.brand !== "hr_diagnostic") return undefined;

  const tacticalEntries = session.answers_log.filter((e) =>
    e.question_id.startsWith("TC-"),
  );
  if (tacticalEntries.length === 0) return undefined;

  const resolved = await Promise.all(
    tacticalEntries.map(async (entry) => {
      const meta = TACTICAL_QUESTION_META[entry.question_id];
      const copy = await invokeQuestionCopy(entry.question_id);
      const selectedOptionId = entry.option_ids[0];
      const selectedOptionText =
        copy.options.find((o) => o.option_id === selectedOptionId)?.option_text ??
        selectedOptionId;
      return {
        question_set_id: meta?.question_set_id ?? "unknown",
        intent: meta?.intent ?? "",
        result: {
          question_id: entry.question_id,
          question_text: copy.question_text,
          selected_option_text: selectedOptionText,
          intent: meta?.intent ?? "",
        },
      };
    }),
  );

  const bySection = new Map<string, TacticalSectionResult>();
  for (const { question_set_id, result } of resolved) {
    if (!bySection.has(question_set_id)) {
      bySection.set(question_set_id, {
        question_set_id,
        referral: getTacticalReferrals(question_set_id),
        answers: [],
      });
    }
    bySection.get(question_set_id)!.answers.push(result);
  }

  // Section order matches TACTICAL_QUESTION_META's own key insertion
  // order (the JSON's question_sets array order), not re-sorted.
  const sectionOrder = [
    ...new Set(Object.values(TACTICAL_QUESTION_META).map((m) => m.question_set_id)),
  ];
  return sectionOrder
    .map((id) => bySection.get(id))
    .filter((s): s is TacticalSectionResult => s !== undefined);
}'''

COMPLETION_RETURN_OLD = '''  return NextResponse.json({ status: "complete", result: privatePayload });
}'''
COMPLETION_RETURN_NEW = '''  const tacticalResults = await resolveTacticalResults(session);

  return NextResponse.json({
    status: "complete",
    result: privatePayload,
    ...(tacticalResults ? { tactical_results: tacticalResults } : {}),
  });
}'''

COMPLETION_EDITS = [
    (COMPLETION_IMPORTS_OLD, COMPLETION_IMPORTS_NEW, 'imports + resolveTacticalResults()'),
    (COMPLETION_RETURN_OLD, COMPLETION_RETURN_NEW, 'attach tactical_results to response'),
]

# ---------------------------------------------------------------------------
# web/components/DiagnosticFlow.tsx -- thread tacticalResults through state.
# ---------------------------------------------------------------------------
FLOW_PATH = pathlib.Path('web/components/DiagnosticFlow.tsx')

FLOW_IMPORT_OLD = '''import type { PrivateOutputPayload } from "@/lib/types";'''
FLOW_IMPORT_NEW = '''import type { PrivateOutputPayload, TacticalSectionResult } from "@/lib/types";'''

FLOW_TYPE_OLD = '''  | { phase: "complete"; result: PrivateOutputPayload }'''
FLOW_TYPE_NEW = '''  | { phase: "complete"; result: PrivateOutputPayload; tacticalResults?: TacticalSectionResult[] }'''

FLOW_SETSTATE_OLD = '''        setState({ phase: "complete", result: data.result as PrivateOutputPayload });'''
FLOW_SETSTATE_NEW = '''        setState({
          phase: "complete",
          result: data.result as PrivateOutputPayload,
          tacticalResults: data.tactical_results as TacticalSectionResult[] | undefined,
        });'''

FLOW_RENDER_OLD = '''  if (state.phase === "complete") {
    const { result } = state;
    return (
      <div className="max-w-2xl mx-auto px-6 py-16">
        <PrivateOutput
          payload={result}
          selectedStateIds={[
            result.primary_state.id,
            ...result.secondary_states.map((s) => s.id),
          ]}
          intake={{'''
FLOW_RENDER_NEW = '''  if (state.phase === "complete") {
    const { result, tacticalResults } = state;
    return (
      <div className="max-w-2xl mx-auto px-6 py-16">
        <PrivateOutput
          payload={result}
          tacticalResults={tacticalResults}
          selectedStateIds={[
            result.primary_state.id,
            ...result.secondary_states.map((s) => s.id),
          ]}
          intake={{'''

FLOW_EDITS = [
    (FLOW_IMPORT_OLD, FLOW_IMPORT_NEW, 'import TacticalSectionResult', 1),
    (FLOW_TYPE_OLD, FLOW_TYPE_NEW, 'complete phase type', 1),
    (FLOW_SETSTATE_OLD, FLOW_SETSTATE_NEW, 'setState (both call sites)', 2),
    (FLOW_RENDER_OLD, FLOW_RENDER_NEW, 'PrivateOutput render call', 1),
]

# ---------------------------------------------------------------------------
# web/components/PrivateOutput.tsx -- new prop, new results section,
# suppress the Engage CTA on hr_diagnostic (enableEngage defaults true and
# was never overridden -- same dead-link class as the self-select gate).
# ---------------------------------------------------------------------------
PRIVATE_PATH = pathlib.Path('web/components/PrivateOutput.tsx')

PO_IMPORT_OLD = '''import type { PrivateOutputPayload, SeverityTier, LegalTailRiskBand } from "@/lib/types";'''
PO_IMPORT_NEW = '''import type {
  PrivateOutputPayload,
  SeverityTier,
  LegalTailRiskBand,
  TacticalSectionResult,
} from "@/lib/types";'''

PO_PROPS_OLD = '''interface PrivateOutputProps {
  payload: PrivateOutputPayload;
  selectedStateIds: string[];'''
PO_PROPS_NEW = '''interface PrivateOutputProps {
  payload: PrivateOutputPayload;
  // HRdiagnostic.com only -- undefined for every principal_resolution
  // session, and for hr_diagnostic sessions where no TC-* question was
  // ever reached (shouldn't happen in practice, but not assumed).
  tacticalResults?: TacticalSectionResult[];
  selectedStateIds: string[];'''

PO_FN_OLD = '''export default function PrivateOutput({
  payload,
  selectedStateIds,
  intake,
  enableSharing = true,
  enableEngage = true,
}: PrivateOutputProps) {
  const brand = useBrand();'''
PO_FN_NEW = '''export default function PrivateOutput({
  payload,
  tacticalResults,
  selectedStateIds,
  intake,
  enableSharing = true,
  enableEngage = true,
}: PrivateOutputProps) {
  const brand = useBrand();
  // enableEngage defaults true and DiagnosticFlow.tsx never overrides it --
  // the Engage CTA below links to /engage, which middleware.ts blocks
  // entirely on hr_diagnostic. Same dead-link class as the self-select
  // gate found and fixed last pass -- suppressed here rather than left
  // visibly broken.
  const showEngageCta = enableEngage && brand !== "hr_diagnostic";'''

PO_ENGAGE_OLD = '''      {enableEngage && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-[11px] uppercase tracking-wide text-slate mb-3">
            Ready to move on this?
          </p>
          <Link
            href="/engage"
            className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Start the engagement →
          </Link>
        </div>
      )}

      {/* Block 7 — friction_tax_estimate: null in Path B — render nothing */}
    </div>
  );
}'''
PO_ENGAGE_NEW = '''      {showEngageCta && (
        <div className="mt-6 pt-6 border-t border-gray-200">
          <p className="text-[11px] uppercase tracking-wide text-slate mb-3">
            Ready to move on this?
          </p>
          <Link
            href="/engage"
            className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 rounded-lg hover:bg-gray-800 transition-colors"
          >
            Start the engagement →
          </Link>
        </div>
      )}

      {/* Block 7 — friction_tax_estimate: null in Path B — render nothing */}

      {/* Block 8 -- Tactical & Compliance results (HRdiagnostic.com only).
          MVP: plain question/selected-answer list per section, each
          section headed by its OneDigital referral chips. Does not match
          the core diagnostic's narrative styling by design -- Pete's
          explicit instruction, a different report shape for a different
          purpose. */}
      {tacticalResults && tacticalResults.length > 0 && (
        <div className="mt-8 pt-8 border-t border-gray-200">
          <p className="text-[11px] uppercase tracking-wide text-slate mb-4">
            Tactical &amp; compliance review
          </p>
          <div className="space-y-6">
            {tacticalResults.map((section) => (
              <div key={section.question_set_id}>
                <div className="flex flex-wrap gap-2 mb-2">
                  {section.referral.map((r) => (
                    <span
                      key={r}
                      className="text-[10px] uppercase tracking-wide bg-gray-100 text-charcoal rounded-full px-2 py-0.5"
                    >
                      {r}
                    </span>
                  ))}
                </div>
                <ul className="space-y-3">
                  {section.answers.map((a) => (
                    <li key={a.question_id}>
                      <p className="text-sm font-medium text-charcoal">{a.question_text}</p>
                      <p className="text-sm text-slate">{a.selected_option_text}</p>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}'''

PRIVATE_EDITS = [
    (PO_IMPORT_OLD, PO_IMPORT_NEW, 'import TacticalSectionResult', 1),
    (PO_PROPS_OLD, PO_PROPS_NEW, 'tacticalResults prop', 1),
    (PO_FN_OLD, PO_FN_NEW, 'showEngageCta', 1),
    (PO_ENGAGE_OLD, PO_ENGAGE_NEW, 'suppress Engage CTA + Block 8 results section', 1),
]

# ---------------------------------------------------------------------------
# web/lib/session-store.test.ts -- emptySession() test helper builds a
# DiagnosticSession object literal directly (not via createSession()), so
# it needs the new required `brand` field too or tsc/vitest fail to compile.
# Not itself testing brand behavior -- "principal_resolution" is a neutral,
# pre-existing-behavior default, matching createSession()'s own default.
# ---------------------------------------------------------------------------
SESSION_STORE_TEST_PATH = pathlib.Path('web/lib/session-store.test.ts')

SST_OLD = '''    return {
      session_id: "test",
      intake: {} as DiagnosticSession["intake"],'''
SST_NEW = '''    return {
      session_id: "test",
      brand: "principal_resolution",
      intake: {} as DiagnosticSession["intake"],'''

SESSION_STORE_TEST_EDITS = [
    (SST_OLD, SST_NEW, 'emptySession() brand field', 1),
]

ALL_FILE_EDITS = [
    (SESSION_STORE_PATH, [(o, n, l, 1) for o, n, l in SESSION_STORE_EDITS]),
    (SESSION_STORE_TEST_PATH, SESSION_STORE_TEST_EDITS),
    (START_ROUTE_PATH, [(o, n, l, 1) for o, n, l in START_ROUTE_EDITS]),
    (COMPLETION_PATH, [(o, n, l, 1) for o, n, l in COMPLETION_EDITS]),
    (FLOW_PATH, FLOW_EDITS),
    (PRIVATE_PATH, PRIVATE_EDITS),
]


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    # types.ts is a plain single insertion, handled separately (no count check needed beyond 1).
    types_content = TYPES_PATH.read_text(encoding='utf-8')
    if types_content.count(TYPES_ANCHOR_OLD) != 1:
        print(f'ERROR: types.ts anchor found {types_content.count(TYPES_ANCHOR_OLD)} times, expected 1.', file=sys.stderr)
        sys.exit(1)
    new_types_content = types_content.replace(TYPES_ANCHOR_OLD, TYPES_ANCHOR_NEW, 1)
    print(f'[web/lib/types.ts :: TacticalSectionResult types]')
    print(f'Inserted before PrivateOutputPayload.\\n')

    file_contents = {TYPES_PATH: new_types_content}

    for path, edits in ALL_FILE_EDITS:
        content = path.read_text(encoding='utf-8')
        new_content = content
        for old, new, label, expected_count in edits:
            count = new_content.count(old)
            if count != expected_count:
                print(f'ERROR: {path} :: {label} anchor found {count} times, expected {expected_count}.', file=sys.stderr)
                sys.exit(1)
            new_content = new_content.replace(old, new, expected_count)
            print(f'[{path} :: {label}] ({expected_count} occurrence(s))')
            print(f'OLD:\\n{old[:300]}')
            print(f'NEW:\\n{new[:300]}')
            print()
        file_contents[path] = new_content

    if args.dry_run:
        print('DRY RUN -- all anchors found, all edits would apply cleanly. Nothing written.')
    else:
        for path, content in file_contents.items():
            path.write_text(content, encoding='utf-8')
            print(f'WROTE: {path}')


if __name__ == '__main__':
    main()
