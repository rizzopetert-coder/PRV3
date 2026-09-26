"""
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
    ok = bool(copy) and not pr_hits(copy) and ";" not in copy and "\u2014" not in copy and "HR Consulting" in copy
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

print(f"\n{len(PASS)} passed, {len(FAIL)} failed")
if FAIL:
    print("FAILED:", *FAIL, sep="\n  ")
    sys.exit(1)
print("All tests passed.")
