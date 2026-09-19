# Candidate Future Task: Remove numpy from engine/accumulation.py

**Status: candidate, not scheduled, not actioned.** Found during the 2026-09-19 Vercel
Function Storage investigation. Explicitly gated below — do not pick this up without first
satisfying both gates.

## What was found

`requirements.txt` lists exactly four packages: `fastapi`, `uvicorn`, `numpy`, `anthropic`.
`numpy` has exactly one import site in the entire codebase — `engine/accumulation.py:14`
(`import numpy as np`) — confirmed via direct grep, not assumed.

All 8 real call sites are basic 8-element vector arithmetic for the SCD-WCS
weighted-cosine-similarity calculation (`DIMENSIONAL_FIELDS` has 8 entries):

```
engine/accumulation.py:557   mu_N = np.array([...])
engine/accumulation.py:558   vec_A = np.array([...])
engine/accumulation.py:562   if np.linalg.norm(vec_A_displaced) < 1e-5:
engine/accumulation.py:574   vec_B = np.array([...])
engine/accumulation.py:578   w = np.array([...])
engine/accumulation.py:580   w = np.ones(len(fields))
engine/accumulation.py:582   num = np.sum(w * vec_A_displaced * vec_B)
engine/accumulation.py:583-584   den = (np.sqrt(np.sum(w * vec_A_displaced ** 2)) *
                                          np.sqrt(np.sum(w * vec_B ** 2)))
```

Array construction, elementwise multiply, `sum`, `sqrt`, `linalg.norm` — over an 8-element
vector. None of this needs numpy's compiled performance; it's the kind of arithmetic pure
Python (`math.sqrt`, list comprehensions, `sum()` over a generator) handles identically at
this size, with no expected numeric difference for such a small vector.

**Low-risk characterization, not a proven-safe one.** "Low risk" here means: numpy is used
in exactly one place, for one well-understood calculation, with an obvious pure-Python
equivalent. It does not mean "verified safe to ship" — see the gates below.

## Why this matters for Function Storage

`numpy` is the single heaviest of the four `requirements.txt` packages by a wide margin
(compiled C extensions; a local-machine proxy measurement — not Vercel's own runtime,
illustrative only — put a local install at 30.3 MB). It is bundled into `api/engine.py`'s
deployed Python function on every single deployment, and per the 2026-09-19 investigation,
Function Storage is a *cumulative retained-bundle-size* problem, not a deployment-count one
(that was fixed 2026-09-05 and confirmed still holding). Removing numpy would shrink every
future deployment's Python function bundle by roughly its own installed size, times however
many deployments Vercel retains.

## What is NOT known, and why this isn't scheduled yet

**No tool available in the 2026-09-19 investigation could produce an exact per-deployment
function bundle size, or a verified total across the 11 currently-retained deployments.**
Removing numpy is a real, plausible lever — it has not been shown to actually move the
Function Storage number by any confirmed amount. Proposing and shipping a fix on the
strength of "this is probably a meaningful chunk" without a real before/after number would
be exactly the kind of confident-but-unverified claim this project's own Cross-Environment
Verification Discipline exists to prevent.

## Gates — both required before this is picked up

1. **A confirmed per-deployment storage number showing this would actually help.** Not "we
   think it's big" — an actual measurement (Vercel dashboard breakdown, `vercel inspect`
   output, or whatever surface eventually exposes it) showing the Python function's
   contribution to Function Storage, ideally isolating numpy's own share of it. If the real
   driver turns out to be something else (the `sharp` native-binary install flagged in the
   same investigation, the Next.js build output generally, or something not yet found), this
   task is the wrong fix and should stay parked.
2. **Its own full calibration re-run when it's picked up, not bundled into unrelated
   cleanup work.** Even though the arithmetic is simple, replacing numpy's `sum`/`sqrt`/
   `linalg.norm` with pure Python is a change to the accumulation engine's actual scoring
   math (`engine/accumulation.py` is Tier 1). It must go through the same discipline every
   other engine change in this project does: dry-run, full 11-script suite, and the
   175-profile calibration suite confirmed at whatever the then-current baseline is (171/175
   as of 2026-09-19), re-run fresh for this change specifically — not assumed clean because
   the math "should" be identical, and not folded into a larger commit where a calibration
   shift could get attributed to the wrong change.

## What this is not

Not a request to remove `sharp`, `fastapi`, `uvicorn`, or `anthropic` — none of those were
investigated for removability, and `sharp`'s presence is flagged separately (Section 16,
2026-09-19) as its own open question, not bundled into this task.
