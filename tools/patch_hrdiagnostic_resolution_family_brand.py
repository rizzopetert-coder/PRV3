"""
Items F/I/J -- brand threaded through the API layer and the Python engine so
an hr-dx.com (hr_diagnostic) session never receives PR service tier names in
resolution_family, the raw resolution_routing fallback, or the AI-generated
synthesis text (including its failure-case backup copy).

Mapping (Pete, 2026-09-26):
  People Tactics & Strategy (engine Roadmap)          -> HR Consulting
  Training & Development   (engine Development)       -> HR Consulting, referencing
        Employee Training & Education / Learning & Development Consulting
  Executive Advisory       (engine Executive Counsel) -> HR Consulting, referencing
        Employee Development, Coaching & Performance Management
  First Call               (engine Intervention)      -> HR Consulting, framed with urgency

Where each piece lands:
  - resolution_family (web payload): "HR Consulting" for every family and
    compound on hr_diagnostic (web/lib/diagnostic-completion.ts).
  - resolution_routing (web payload, raw text fallback rendered by
    PrivateOutput Blocks 2/4 and Copy Results): "HR Consulting" on
    hr_diagnostic ("" stays "" -- same empty-routing behavior as PR).
  - AI synthesis: the locked system prompt already forbids any service name
    except the resolution_family it is given, so the lever is the value
    passed in, not the prompt. On hr_diagnostic, main.py passes
    hr_diagnostic_synthesis_family(...) -- "HR Consulting", plus the mapped
    service references and an urgency cue -- instead of the PR commercial
    name. OUTPUT_SYNTHESIS_SYSTEM_PROMPT is untouched.
  - Backup copy (LLM timeout/failure): get_fallback_synthesis() checks the
    hr_diagnostic table first, keyed by that exact context string. Four
    tier-agnostic entries (NEW COPY, Pete review needed before push);
    compounds use the highest-priority family's entry: Intervention
    (urgency) > first of Development/Executive Counsel > Roadmap.

Brand transport: web sends brand in the /api/complete payload
(CompletePayload.brand, from session.brand, already stored at session
start). api/engine.py accepts "principal_resolution" | "hr_diagnostic",
anything else or absent -> "principal_resolution" (unchanged behavior for
every existing caller). run_accumulated_engine(brand=...) defaults to
principal_resolution. Path B (/api/result) and condensed are 404 on hr-dx,
so only Path 1's completion needs the brand.

Usage:
    python tools/patch_hrdiagnostic_resolution_family_brand.py --dry-run
    python tools/patch_hrdiagnostic_resolution_family_brand.py --write
"""
import argparse
import pathlib
import sys

HR_BLOCK_PY = '''


# ── hr_diagnostic (hr-dx.com) brand mapping ────────────────────────────────────
# PR's commercial tier names must never reach an hr-dx.com session. Every
# engine family maps to "HR Consulting" (the display value the web layer
# uses for resolution_family / resolution_routing on that brand), with the
# mapped OneDigital service references and an urgency cue carried into the
# AI synthesis context string below. Mapping per Pete, 2026-09-26. Mirrored
# on the web side by web/lib/resolution-family.ts's
# HR_DIAGNOSTIC_RESOLUTION_FAMILY -- keep both in lockstep.

HR_DIAGNOSTIC_FAMILY_NAME: str = "HR Consulting"

HR_DIAGNOSTIC_FAMILY_REFERENCES: dict[str, str] = {
    "Development":       "Employee Training & Education and Learning & Development Consulting",
    "Executive Counsel": "Employee Development, Coaching & Performance Management",
}

_HR_DIAGNOSTIC_URGENT_FAMILY = "Intervention"
_HR_DIAGNOSTIC_KNOWN_FAMILIES = ("Roadmap", "Development", "Intervention", "Executive Counsel")


def _hr_parts(engine_family_str: str) -> list[str]:
    # Unknown parts are dropped, never passed through -- a pass-through could
    # carry a PR name onto hr-dx.com.
    return [
        p.strip() for p in engine_family_str.split(" + ")
        if p.strip() in _HR_DIAGNOSTIC_KNOWN_FAMILIES
    ]


def hr_diagnostic_synthesis_family(engine_family_str: str) -> str:
    """
    hr_diagnostic replacement for translate_resolution_family() at the AI
    synthesis call site. Returns the resolution_family context string the
    synthesis prompt receives -- "HR Consulting", plus ", through <refs>"
    for Development / Executive Counsel and ", engaged immediately" when
    Intervention is present. Empty or wholly-unknown input returns "" (same
    as the PR path's empty-routing case).
    """
    parts = _hr_parts(engine_family_str)
    if not parts:
        return ""
    refs: list[str] = []
    for p in parts:
        ref = HR_DIAGNOSTIC_FAMILY_REFERENCES.get(p)
        if ref and ref not in refs:
            refs.append(ref)
    text = HR_DIAGNOSTIC_FAMILY_NAME
    if refs:
        text += ", through " + " and ".join(refs)
    if _HR_DIAGNOSTIC_URGENT_FAMILY in parts:
        text += ", engaged immediately"
    return text


# Failure-case backup copy for hr_diagnostic -- NEW COPY (2026-09-26),
# pending Pete's review. Tier-agnostic, one entry per engine family. Same
# fill pattern as the PR table (fallback_synthesis._make_entry puts the
# one string into liability/framing/resolution_framing text alike).
HR_DIAGNOSTIC_FALLBACK_COPY: dict[str, str] = {
    "Roadmap": (
        "The conditions producing this live in how the organization is designed, not in the people "
        "working inside it. HR Consulting addresses that structure directly, targeted at what the "
        "diagnostic found rather than at the symptoms."
    ),
    "Development": (
        "There is a capability gap. HR Consulting addresses it through Employee Training & Education "
        "and Learning & Development Consulting, built around the specific skills and practices the "
        "diagnostic identified."
    ),
    "Executive Counsel": (
        "The decisions this situation requires sit at the leadership level. HR Consulting supports "
        "them through Employee Development, Coaching & Performance Management, with an outside "
        "perspective that is hard to get from inside the organization."
    ),
    "Intervention": (
        "What the diagnostic found is active now and should not wait. HR Consulting engages directly "
        "and promptly, while there is still room to shape the outcome."
    ),
}


def hr_diagnostic_fallback_copy(engine_family_str: str) -> str:
    """
    Backup copy for an hr_diagnostic session. Compounds use the
    highest-priority family: Intervention (urgency) first, then the first
    of Development / Executive Counsel in order, then Roadmap.
    """
    parts = _hr_parts(engine_family_str)
    if not parts:
        return ""
    if _HR_DIAGNOSTIC_URGENT_FAMILY in parts:
        return HR_DIAGNOSTIC_FALLBACK_COPY[_HR_DIAGNOSTIC_URGENT_FAMILY]
    for p in parts:
        if p in HR_DIAGNOSTIC_FAMILY_REFERENCES:
            return HR_DIAGNOSTIC_FALLBACK_COPY[p]
    return HR_DIAGNOSTIC_FALLBACK_COPY[parts[0]]


def _build_hr_fallback_by_context() -> dict[str, str]:
    # Keyed by the exact context string synthesize() receives, so
    # get_fallback_synthesis() can resolve it without a brand parameter.
    # Every ordered combination of distinct known families (lengths 1-4),
    # so any compound the taxonomy or a causation override produces is
    # covered. Two engine strings can share a context string (e.g. Roadmap
    # + Intervention / Intervention + Roadmap) -- asserted to map to the
    # same copy, never silently overwritten.
    from itertools import permutations
    table: dict[str, str] = {}
    for n in range(1, len(_HR_DIAGNOSTIC_KNOWN_FAMILIES) + 1):
        for combo in permutations(_HR_DIAGNOSTIC_KNOWN_FAMILIES, n):
            engine_str = " + ".join(combo)
            ctx = hr_diagnostic_synthesis_family(engine_str)
            copy = hr_diagnostic_fallback_copy(engine_str)
            existing = table.get(ctx)
            if existing is not None and existing != copy:
                raise ValueError(f"hr_diagnostic fallback conflict for context {ctx!r}")
            table[ctx] = copy
    return table


HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT: dict[str, str] = _build_hr_fallback_by_context()
'''

EDITS = [
    # ── engine/resolution_families.py ─────────────────────────────────────────
    (pathlib.Path('engine/resolution_families.py'),
     '    translated = [ENGINE_TO_COMMERCIAL_NAME.get(p, p) for p in parts]\n'
     '    return " + ".join(translated)\n',
     '    translated = [ENGINE_TO_COMMERCIAL_NAME.get(p, p) for p in parts]\n'
     '    return " + ".join(translated)\n' + HR_BLOCK_PY.rstrip('\n') + '\n',
     'hr_diagnostic mapping block'),

    # ── engine/data/fallback_synthesis.py ─────────────────────────────────────
    (pathlib.Path('engine/data/fallback_synthesis.py'),
     'from engine.resolution_families import RESOLUTION_FALLBACK_COPY, _FALLBACK_GENERIC\n',
     'from engine.resolution_families import (\n'
     '    RESOLUTION_FALLBACK_COPY,\n'
     '    _FALLBACK_GENERIC,\n'
     '    HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT,\n'
     ')\n',
     'import hr table'),
    (pathlib.Path('engine/data/fallback_synthesis.py'),
     '    Returns generic fallback entry if key is not found.\n'
     '    """\n'
     '    if " + " in commercial_name:\n',
     '    Returns generic fallback entry if key is not found.\n'
     '\n'
     '    hr_diagnostic context strings (engine.resolution_families.\n'
     '    hr_diagnostic_synthesis_family(), all prefixed "HR Consulting") are\n'
     '    checked first and resolve to the hr_diagnostic backup copy -- never\n'
     '    to a PR-named entry.\n'
     '    """\n'
     '    hr_copy = HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT.get(commercial_name)\n'
     '    if hr_copy is not None:\n'
     '        return _make_entry(hr_copy)\n'
     '    if " + " in commercial_name:\n',
     'hr lookup first'),

    # ── engine/main.py ────────────────────────────────────────────────────────
    (pathlib.Path('engine/main.py'),
     'from engine.resolution_families import translate_resolution_family\n',
     'from engine.resolution_families import (\n'
     '    translate_resolution_family,\n'
     '    hr_diagnostic_synthesis_family,\n'
     ')\n',
     'import hr helper'),
    (pathlib.Path('engine/main.py'),
     '    narrative_signals_count: int = 0,\n'
     '    pre_narrative_vector: Optional[dict] = None,\n'
     ') -> dict:\n',
     '    narrative_signals_count: int = 0,\n'
     '    pre_narrative_vector: Optional[dict] = None,\n'
     '    # "principal_resolution" | "hr_diagnostic". hr_diagnostic swaps the\n'
     '    # AI synthesis context (and so its backup copy) off PR tier names --\n'
     '    # see engine/resolution_families.py\'s hr_diagnostic block.\n'
     '    brand: str = "principal_resolution",\n'
     ') -> dict:\n',
     'brand param'),
    (pathlib.Path('engine/main.py'),
     '        commercial_family = translate_resolution_family(\n'
     '            output_package.private.resolution_family\n'
     '            if output_package.private else ""\n'
     '        )\n'
     '        asset_obj = _compute_asset_score(accumulated_vector, lead_id)\n',
     '        engine_family = (\n'
     '            output_package.private.resolution_family\n'
     '            if output_package.private else ""\n'
     '        )\n'
     '        commercial_family = (\n'
     '            hr_diagnostic_synthesis_family(engine_family)\n'
     '            if brand == "hr_diagnostic"\n'
     '            else translate_resolution_family(engine_family)\n'
     '        )\n'
     '        asset_obj = _compute_asset_score(accumulated_vector, lead_id)\n',
     'brand-aware synthesis family'),

    # ── api/engine.py ─────────────────────────────────────────────────────────
    (pathlib.Path('api/engine.py'),
     '        pre_narrative_vector = payload.get("pre_narrative_vector") if isinstance(payload, dict) else None\n'
     '        result = run_accumulated_engine(\n'
     '            accumulated_vector, intake, answered_question_count, checkpoint_results,\n'
     '            severity_inputs, answers_log, narrative_response, narrative_severity_addition,\n'
     '            narrative_trigger_point, narrative_overall_confidence, narrative_signals_count,\n'
     '            pre_narrative_vector,\n'
     '        )\n',
     '        pre_narrative_vector = payload.get("pre_narrative_vector") if isinstance(payload, dict) else None\n'
     '        # hr_diagnostic (hr-dx.com) keeps PR tier names out of the AI\n'
     '        # synthesis. Anything other than the two known brands, or absent\n'
     '        # (every pre-existing caller), is principal_resolution -- unchanged.\n'
     '        brand = payload.get("brand") if isinstance(payload, dict) else None\n'
     '        if brand not in ("principal_resolution", "hr_diagnostic"):\n'
     '            brand = "principal_resolution"\n'
     '        result = run_accumulated_engine(\n'
     '            accumulated_vector, intake, answered_question_count, checkpoint_results,\n'
     '            severity_inputs, answers_log, narrative_response, narrative_severity_addition,\n'
     '            narrative_trigger_point, narrative_overall_confidence, narrative_signals_count,\n'
     '            pre_narrative_vector, brand=brand,\n'
     '        )\n',
     'read + pass brand'),

    # ── web/lib/resolution-family.ts ──────────────────────────────────────────
    (pathlib.Path('web/lib/resolution-family.ts'),
     'import type { ResolutionFamily } from "@/lib/types";\n',
     'import type { ResolutionFamily } from "@/lib/types";\n'
     '\n'
     '// hr_diagnostic (hr-dx.com) display value for resolution_family and\n'
     '// resolution_routing -- every engine family and compound maps here, so\n'
     '// no PR tier name reaches that brand. Mirrors engine/resolution_\n'
     '// families.py\'s HR_DIAGNOSTIC_FAMILY_NAME; keep both in lockstep.\n'
     '// Server-side only (imported by route/lib code, never a client component).\n'
     'export const HR_DIAGNOSTIC_RESOLUTION_FAMILY: ResolutionFamily = "HR Consulting";\n',
     'hr constant'),

    # ── web/lib/engine-client.ts ──────────────────────────────────────────────
    (pathlib.Path('web/lib/engine-client.ts'),
     '  pre_narrative_vector?: AccumulatedVector;\n'
     '}\n'
     '\n'
     'export async function invokeComplete(\n',
     '  pre_narrative_vector?: AccumulatedVector;\n'
     '  // hr_diagnostic keeps PR tier names out of the AI synthesis (see\n'
     '  // api/engine.py). Absent -> principal_resolution on the engine side.\n'
     '  brand?: Brand;\n'
     '}\n'
     '\n'
     'export async function invokeComplete(\n',
     'CompletePayload.brand'),

    # ── web/lib/diagnostic-completion.ts ──────────────────────────────────────
    (pathlib.Path('web/lib/diagnostic-completion.ts'),
     'import { translateResolutionFamily } from "@/lib/resolution-family";\n',
     'import {\n'
     '  translateResolutionFamily,\n'
     '  HR_DIAGNOSTIC_RESOLUTION_FAMILY,\n'
     '} from "@/lib/resolution-family";\n',
     'import hr constant'),
    (pathlib.Path('web/lib/diagnostic-completion.ts'),
     '    pre_narrative_vector: session.pre_narrative_vector ?? undefined,\n'
     '  });\n',
     '    pre_narrative_vector: session.pre_narrative_vector ?? undefined,\n'
     '    brand: session.brand,\n'
     '  });\n',
     'send brand'),
    (pathlib.Path('web/lib/diagnostic-completion.ts'),
     '    resolution_family: translateResolutionFamily(engineResult.private_output.resolution_routing),\n'
     '    resolution_routing: engineResult.private_output.resolution_routing,\n',
     '    // hr_diagnostic: both fields are brand-safe display text -- PrivateOutput\n'
     '    // renders resolution_routing raw as a fallback (Blocks 2/4, Copy\n'
     '    // Results), so the raw engine name must not pass through either.\n'
     '    // Empty routing stays empty, same as principal_resolution.\n'
     '    resolution_family: isHrDiagnostic\n'
     '      ? (rawRouting ? HR_DIAGNOSTIC_RESOLUTION_FAMILY : "")\n'
     '      : translateResolutionFamily(rawRouting),\n'
     '    resolution_routing: isHrDiagnostic\n'
     '      ? (rawRouting ? HR_DIAGNOSTIC_RESOLUTION_FAMILY : "")\n'
     '      : rawRouting,\n',
     'brand-safe payload fields'),
    (pathlib.Path('web/lib/diagnostic-completion.ts'),
     '  const privatePayload: PrivateOutputPayload = {\n',
     '  const isHrDiagnostic = session.brand === "hr_diagnostic";\n'
     '  const rawRouting = engineResult.private_output.resolution_routing;\n'
     '\n'
     '  const privatePayload: PrivateOutputPayload = {\n',
     'hr locals'),
]

ENGINE_CLIENT_BRAND_IMPORT = (
    pathlib.Path('web/lib/engine-client.ts'),
    'import type { AccumulatedVector, AnswerLogEntry } from "@/lib/session-store";\n',
    'import type { AccumulatedVector, AnswerLogEntry } from "@/lib/session-store";\n'
    'import type { Brand } from "@/lib/brand";\n',
    'import Brand type',
)
EDITS.insert(EDITS.index(next(e for e in EDITS if e[3] == 'CompletePayload.brand')), ENGINE_CLIENT_BRAND_IMPORT)

PY_TEST = pathlib.Path('tools/test_hr_diagnostic_brand.py')
PY_TEST_CONTENT = '''"""
hr_diagnostic brand -- engine-side verification (items F/I/J).

Proves no PR service tier name reaches an hr_diagnostic session through the
AI synthesis context, the synthesis prompt, or the failure-case backup copy,
and that principal_resolution behavior is unchanged. Drives the real
run_accumulated_engine() path (fallback mode via a missing anthropic module,
LLM mode via a fake one that captures the prompt) -- no real API call.
"""

import json
import sys
import types
import unittest.mock as mock
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from engine.data.states import STATE_PROFILES, DIMENSIONAL_FIELDS
from engine.data.fallback_synthesis import get_fallback_synthesis
from engine.resolution_families import (
    hr_diagnostic_synthesis_family,
    HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT,
    HR_DIAGNOSTIC_FALLBACK_COPY,
)
from engine.main import run_accumulated_engine

PASS, FAIL = [], []


def check(label, cond, detail=""):
    (PASS if cond else FAIL).append(label)
    print(f"  {'PASS' if cond else 'FAIL'}  {label}" + (f" -- {detail}" if detail and not cond else ""))


PR_TERMS = (
    "People Tactics", "Training & Development", "First Call", "Executive Advisory",
    "Principal Resolution", "Groundwork", "Roadmap", "Intervention", "Executive Counsel",
)
SYNTH_TEXT_FIELDS = (
    "liability_condition_text", "asset_resolution_anchor_text", "framing_text",
    "resolution_framing_text", "headline",
)
INTAKE = {"organization_size": 152, "industry": "Technology", "role_level": "CEO"}


def pr_hits(text):
    return [t for t in PR_TERMS if t in text]


def synth_blob(s):
    return " ".join([str(s.get(f, "")) for f in SYNTH_TEXT_FIELDS] + [str(i) for i in s.get("observable_indicators", [])])


print("hr_diagnostic_synthesis_family -- four singles")
expected = {
    "Roadmap": "HR Consulting",
    "Development": "HR Consulting, through Employee Training & Education and Learning & Development Consulting",
    "Executive Counsel": "HR Consulting, through Employee Development, Coaching & Performance Management",
    "Intervention": "HR Consulting, engaged immediately",
}
for fam, want in expected.items():
    got = hr_diagnostic_synthesis_family(fam)
    check(f"{fam} -> {want!r}", got == want, f"got {got!r}")
check("empty -> empty", hr_diagnostic_synthesis_family("") == "")
check("unknown part dropped, never passed through",
      hr_diagnostic_synthesis_family("First Call") == "" and
      hr_diagnostic_synthesis_family("Roadmap + Groundwork") == "HR Consulting")

print("every family string in the taxonomy (all 58 states)")
families = sorted({p.resolution_family for p in STATE_PROFILES.values()})
for fam in families:
    ctx = hr_diagnostic_synthesis_family(fam)
    check(f"context for {fam!r} starts 'HR Consulting', no PR terms",
          ctx.startswith("HR Consulting") and not pr_hits(ctx), ctx)
    check(f"backup copy exists for {fam!r}", ctx in HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT)

print("hr_diagnostic backup copy -- content rules")
for ctx, copy in HR_DIAGNOSTIC_FALLBACK_BY_CONTEXT.items():
    ok = bool(copy) and not pr_hits(copy) and ";" not in copy and "\\u2014" not in copy and "HR Consulting" in copy
    check(f"backup copy for {ctx!r}: non-empty, no PR terms, no semicolon, no em-dash", ok, copy)
check("four base entries", sorted(HR_DIAGNOSTIC_FALLBACK_COPY) == sorted(expected))
check("urgency copy wins for any compound with Intervention",
      get_fallback_synthesis(hr_diagnostic_synthesis_family("Executive Counsel + Intervention"), "Entrenched")["resolution_framing_text"]
      == HR_DIAGNOSTIC_FALLBACK_COPY["Intervention"])

print("get_fallback_synthesis -- hr keys resolve hr copy, all tiers, all fields")
for fam in families:
    ctx = hr_diagnostic_synthesis_family(fam)
    for tier in ("Emerging", "Entrenched", "Endemic", None):
        fb = get_fallback_synthesis(ctx, tier)
        blob = " ".join(str(v) for v in fb.values())
        check(f"{fam} / {tier}: no PR terms", not pr_hits(blob), str(pr_hits(blob)))

print("principal_resolution regression -- PR fallback unchanged")
fb_pr = get_fallback_synthesis("First Call", "Emerging")
check("PR 'First Call' fallback still names First Call", "First Call" in fb_pr["resolution_framing_text"])
fb_pr2 = get_fallback_synthesis("People Tactics & Strategy + First Call", None)
check("PR compound fallback still names both tiers",
      "People Tactics & Strategy" in fb_pr2["resolution_framing_text"] and "First Call" in fb_pr2["resolution_framing_text"])

# ── End to end through run_accumulated_engine() ──────────────────────────────
def state_vector(sid, scale=3.0):
    p = STATE_PROFILES[sid]
    return {f: float(getattr(p.dimensional_vector, f)) * scale for f in DIMENSIONAL_FIELDS}


examples = {}
for sid, p in STATE_PROFILES.items():
    examples.setdefault(p.resolution_family, sid)

print("run_accumulated_engine, fallback path (anthropic absent)")
routed = 0
with mock.patch.dict("sys.modules", {"anthropic": None}):
    for fam, sid in examples.items():
        vec = state_vector(sid)
        hr = run_accumulated_engine(vec, INTAKE, 27, brand="hr_diagnostic")
        pr = run_accumulated_engine(vec, INTAKE, 27)
        routing = hr["private_output"]["resolution_routing"]
        if not routing:
            continue
        routed += 1
        hs, ps = hr["synthesis"], pr["synthesis"]
        check(f"[{routing}] hr synthesis is fallback", hs["is_fallback"] is True)
        check(f"[{routing}] hr synthesis text: no PR terms", not pr_hits(synth_blob(hs)), str(pr_hits(synth_blob(hs))))
        check(f"[{routing}] hr resolution_framing_text names HR Consulting", "HR Consulting" in hs["resolution_framing_text"])
        check(f"[{routing}] PR default still names a PR tier", any(t in ps["resolution_framing_text"] for t in PR_TERMS[:4]))
        check(f"[{routing}] raw private_output routing is the engine name (web layer overrides it)",
              routing == pr["private_output"]["resolution_routing"])
check("at least one real routing exercised end to end", routed >= 1, f"routed={routed}")

print("run_accumulated_engine, LLM path (fake anthropic captures the prompt)")
captured = []


class _FakeMessages:
    def create(self, **kw):
        captured.append(kw)
        body = json.dumps({
            "liability_condition_text": "x", "asset_resolution_anchor_text": "x", "framing_text": "x",
            "observable_indicators": ["x"], "resolution_framing_text": "x", "headline": "x",
            "synthesis_confidence": 0.9,
        })
        return types.SimpleNamespace(content=[types.SimpleNamespace(text=body)])


class _FakeClient:
    def __init__(self, *a, **k):
        self.messages = _FakeMessages()


fake_anthropic = types.ModuleType("anthropic")
fake_anthropic.Anthropic = _FakeClient
with mock.patch.dict("sys.modules", {"anthropic": fake_anthropic}):
    for fam, sid in examples.items():
        captured.clear()
        r = run_accumulated_engine(state_vector(sid), INTAKE, 27, brand="hr_diagnostic")
        routing = r["private_output"]["resolution_routing"]
        if not routing or not captured:
            continue
        prompt = captured[-1]["messages"][0]["content"]
        line = next((l for l in prompt.splitlines() if l.startswith("resolution_family:")), "")
        check(f"[{routing}] prompt resolution_family line is hr context, no PR terms",
              line.startswith("resolution_family: HR Consulting") and not pr_hits(line), line)
        check(f"[{routing}] LLM result used (not fallback)", r["synthesis"]["is_fallback"] is False)
        captured.clear()
        run_accumulated_engine(state_vector(sid), INTAKE, 27)
        pr_line = next((l for l in captured[-1]["messages"][0]["content"].splitlines() if l.startswith("resolution_family:")), "")
        check(f"[{routing}] PR default prompt still carries the PR commercial name",
              any(t in pr_line for t in PR_TERMS[:4]), pr_line)

print(f"\\n{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", *FAIL, sep="\\n  ")
    sys.exit(1)
print("All tests passed.")
'''

VITEST = pathlib.Path('web/lib/diagnostic-completion-brand.test.ts')
VITEST_CONTENT = '''import { describe, it, expect, vi, beforeEach } from "vitest";

// ---------------------------------------------------------------------------
// completeDiagnosticSession() brand handling (items F/I/J). hr_diagnostic
// payloads must carry no PR tier name in resolution_family or the raw
// resolution_routing fallback, and must send brand to the engine so the AI
// synthesis is brand-safe too. principal_resolution must be unchanged.
// Local Path 1 completion is blocked (no Upstash credentials locally, see
// diagnostic-completion.test.ts's header), so this proves the assembly
// logic directly; the live round-trip is owed on a Preview deploy.
// ---------------------------------------------------------------------------

const mockInvokeComplete = vi.fn();

vi.mock("@/lib/engine-client", () => ({
  invokeComplete: (...args: unknown[]) => mockInvokeComplete(...args),
  invokeQuestionCopy: vi.fn(),
}));

vi.mock("@/lib/session-store", () => ({
  completeSession: vi.fn(),
}));

import { completeDiagnosticSession } from "@/lib/diagnostic-completion";
import type { DiagnosticSession } from "@/lib/session-store";

const PR_TERMS = [
  "People Tactics", "Training & Development", "First Call", "Executive Advisory",
  "Principal Resolution", "Roadmap", "Intervention", "Executive Counsel",
];

const ZERO_VECTOR = {
  aptitude_liability: 0, aptitude_asset: 0,
  authority_liability: 0, authority_asset: 0,
  alliance_liability: 0, alliance_asset: 0,
  attitude_liability: 0, attitude_asset: 0,
};

function session(brand: DiagnosticSession["brand"]): DiagnosticSession {
  return {
    session_id: "t", brand, intake: {} as DiagnosticSession["intake"], next_question_id: "Q01",
    accumulated_vector: { ...ZERO_VECTOR }, answers_log: [], status: "in_progress",
    checkpoint_q11: null, checkpoint_q19: null, checkpoint_q27: null, question_sequence: [],
    severity_inputs: [], severity_follow_on_origins: {}, question_labels: {},
    narrative_fired: false, narrative_response: "", narrative_severity_addition: 0,
    narrative_trigger_point: null, narrative_overall_confidence: 0, narrative_signals_count: 0,
    pre_narrative_vector: null, pending_narrative_prompt: null, pending_completion: false,
  };
}

function engineResult(routing: string, withSynthesis: boolean) {
  return {
    identified_states: [{ state_id: "the_founders_grip", state_name: "The Founder's Grip", score: 1, descriptive_prose: "" }],
    synthesis: withSynthesis
      ? {
          liability_condition_text: "l", asset_resolution_anchor_text: "a", framing_text: "f",
          observable_indicators: [], resolution_framing_text: "r", headline: "h",
          synthesis_confidence: 1, is_fallback: false,
        }
      : null,
    severity: { tier: "Entrenched", by_state: {} },
    private_output: {
      resolution_routing: routing, friction_tax_estimate: null, friction_tax_ledger: null,
      legal_tail_risk_exposure: null, cascade_risk: null, causation_pattern: null,
      trajectory: null, urgency_window: null,
    },
    dimension_summary: {},
    asset_score: { primary_asset_domain: null },
  };
}

async function run(brand: DiagnosticSession["brand"], routing: string, withSynthesis = true) {
  mockInvokeComplete.mockResolvedValueOnce(engineResult(routing, withSynthesis));
  const res = await completeDiagnosticSession(session(brand));
  return (await res.json()).result;
}

describe("completeDiagnosticSession brand handling", () => {
  beforeEach(() => mockInvokeComplete.mockReset());

  const ROUTINGS = ["Roadmap", "Development", "Intervention", "Executive Counsel",
    "Intervention + Executive Counsel", "Roadmap + Intervention", "Development + Roadmap"];

  for (const routing of ROUTINGS) {
    it(`hr_diagnostic [${routing}]: resolution_family and resolution_routing are "HR Consulting"`, async () => {
      const result = await run("hr_diagnostic", routing, false);
      expect(result.resolution_family).toBe("HR Consulting");
      expect(result.resolution_routing).toBe("HR Consulting");
      const blob = `${result.resolution_family} ${result.resolution_routing}`;
      for (const t of PR_TERMS) expect(blob).not.toContain(t);
    });
  }

  it("hr_diagnostic: empty routing stays empty (same as principal_resolution)", async () => {
    const result = await run("hr_diagnostic", "");
    expect(result.resolution_family).toBe("");
    expect(result.resolution_routing).toBe("");
  });

  it("sends brand to the engine for both brands", async () => {
    await run("hr_diagnostic", "Intervention");
    expect(mockInvokeComplete.mock.calls[0][0].brand).toBe("hr_diagnostic");
    await run("principal_resolution", "Intervention");
    expect(mockInvokeComplete.mock.calls[1][0].brand).toBe("principal_resolution");
  });

  it("principal_resolution unchanged: translated family, raw routing", async () => {
    const result = await run("principal_resolution", "Intervention + Roadmap");
    expect(result.resolution_family).toBe("First Call + People Tactics & Strategy");
    expect(result.resolution_routing).toBe("Intervention + Roadmap");
  });
});
'''


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--dry-run', action='store_true')
    g.add_argument('--write', action='store_true')
    args = ap.parse_args()

    for p in (PY_TEST, VITEST):
        if p.exists():
            print(f'ERROR: {p} already exists.', file=sys.stderr)
            sys.exit(1)

    edited = {}
    for path, old, new, label in EDITS:
        text = edited.get(path, path.read_text(encoding='utf-8'))
        count = text.count(old)
        if count != 1:
            print(f'ERROR: {path} :: {label} anchor found {count} times, expected exactly 1.', file=sys.stderr)
            sys.exit(1)
        edited[path] = text.replace(old, new, 1)
        print(f'[{path} :: {label}] OK')

    print(f'=== NEW {PY_TEST} ({len(PY_TEST_CONTENT.splitlines())} lines)')
    print(f'=== NEW {VITEST} ({len(VITEST_CONTENT.splitlines())} lines)')

    if args.dry_run:
        print('DRY RUN -- all anchors found, all edits would apply cleanly. Nothing written.')
        return

    for path, text in edited.items():
        path.write_text(text, encoding='utf-8')
        print(f'WROTE (edited): {path}')
    PY_TEST.write_text(PY_TEST_CONTENT, encoding='utf-8')
    print(f'WROTE: {PY_TEST}')
    VITEST.write_text(VITEST_CONTENT, encoding='utf-8')
    print(f'WROTE: {VITEST}')


if __name__ == '__main__':
    main()
