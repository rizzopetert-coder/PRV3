# Verifying Gemini's Scope-Expansion Review — 4 Claims Checked

Date: 2026-08-24. Verification only. No vector values proposed, no candidates searched, no code touched. Gemini's "cleared to scope" not treated as authorization.

## 1. SCD-WCS scale-invariance claim — **algebra correct, conclusion doesn't apply to what was actually proposed**

Pulled the real formula from `engine/accumulation.py::rank_states()` directly:

```python
num = np.sum(w * vec_A_displaced * vec_B)
den = (np.sqrt(np.sum(w * vec_A_displaced ** 2)) * np.sqrt(np.sum(w * vec_B ** 2)))
sim = num / den
```

**Gemini's described formula matches this exactly** — weighted cosine, session vector (`vec_A_displaced`) centroid-displaced, state vector `B` undisplaced, the same weight array `w` applied to the numerator cross-term and both halves of the denominator. Not a mischaracterization.

**The scale-invariance math itself is correct, confirmed both algebraically and empirically.** If `B → k·B` for positive scalar `k`, both `num` and `den` scale by `k`, and `sim` is unchanged. Verified directly: uniformly scaling `the_second_close`'s entire 8-field vector by ×1.3 left its score unchanged to floating-point precision (0.9061831399952652 → ...653).

**But this doesn't refute what was actually proposed.** The prior scoping document's "budget expansion" idea was never uniform scaling of the whole vector — it was specifically "a genuinely stronger alliance concentration... closer to `built_to_fail`'s own 0.60-class magnitude," i.e., raising *one* dominant field while holding the others fixed. That is not scale-invariant, confirmed empirically: raising only `alliance_liability` from 0.45 to 0.60 (nothing else touched) changed the score substantially, 0.9062 → 0.9439. **Gemini's algebra is sound; its use of that algebra to reject "budget expansion as a standalone lever" targets an operation (uniform scaling) that was never actually the proposal on the table.**

## 2. Arithmetic on Gemini's `the_paper_tiger` proposal — **confirmed inconsistent**

Gemini proposes Aptitude=0.40 / Authority=0.30 / Attitude=0.20, no stated Alliance, while insisting the 0.90 invariant should hold.

`0.40 + 0.30 + 0.20 = 0.90` — **already exactly 0.90 with the three stated values alone**, leaving no room for Alliance at all. Checked the taxonomy's real floor convention directly: **zero states anywhere in all 58 have any liability field at exactly 0.0** — every state carries a nonzero floor on all four liability fields. Any realistic Alliance value (0.10 or 0.15, matching the two floor conventions actually used elsewhere in the taxonomy) pushes the real total to 1.00 or 1.05 — breaking the exact invariant Gemini itself insists on. **A real, confirmed arithmetic inconsistency in Gemini's own proposal, not a rounding artifact.**

## 3. `silosolation`/`the_arbitrary_standard` tie status — **Gemini is right; not stale this time**

Pulled both states' real current `dimensional_vector` and `SALIENCE_PROFILES` fresh, directly:

```
silosolation:            vector (0.15,0.15,0.45,0.15,0.15,0.15,0.15,0.15)  salience {auth:2.0, all:2.5, apt:0.4, att:0.4} (both liability+asset pairs)
the_arbitrary_standard:  vector (0.15,0.15,0.45,0.15,0.15,0.15,0.15,0.15)  salience {auth:2.0, all:2.5, apt:0.4, att:0.4} (both liability+asset pairs)

vectors identical:  True
salience identical: True
```

**A genuine, live, 175/175 tie between these two states today, confirmed directly — Gemini's claim holds.**

**Reconciling this with the tracker's "closes rank-6 entirely" (commit `e9a2750`, confirmed real via `git log`):** that claim is also real, but narrower than a literal reading suggests. The tracker's own detailed rows (both states' individual entries) make clear what "closes rank-6" actually meant: each of the three rank-6 states (`the_second_close`, `silosolation`, `the_arbitrary_standard`) received a real, deliberate, documented disposition, and each one's *exact tie against `the_second_close`* (the cluster's reference/baseline state) was broken via a salience-only tie-break. `silosolation`'s own row states plainly it "still loses its own 3 dedicated profiles outright to `the_second_close`... confirmed unmovable even at extreme magnitude" and that "a real fix would mean raising the authored vector itself" — the tracker never claimed `silosolation` and `the_arbitrary_standard` became mutually distinguished from *each other*, because both received the identical Authority-secondary treatment (0.4→2.0) independently, for the same textual reason, landing on the same value. **Both things are true at once: rank-6 was genuinely closed in the specific sense the commit meant, and the silosolation/`the_arbitrary_standard` pairing specifically remains a live, unaddressed tie today.** Gemini's finding is accurate, not a stale-context error like the earlier IPM value.

## 4. `the_paper_tiger`'s shipped salience vs. Gemini's proposed reshape — **doesn't compose into an improvement**

Confirmed commit context: `58a19a0`, "SCD-WCS pilot — salience differentiation, `built_to_fail`/`the_paper_tiger` (rank 8)." Shipped salience: `aptitude=1.0, authority=1.0, alliance=0.4, attitude=1.5` (both liability+asset pairs) — deliberately down-weighting aptitude and up-weighting attitude relative to the standard flat template, to compensate for the shared vector's aptitude-dominant shape not matching `the_paper_tiger`'s own attitude-flavored text.

**Real current baseline, pulled fresh (own dedicated profiles, before any reshape):** `the_paper_tiger` already loses all 4 of its own profiles to `built_to_fail` today, at **own_rank 8-9** — a pre-existing, already-documented residual (the tracker's own row: "Still occasionally loses to `built_to_fail` on `built_to_fail`'s own turf — expected, untouched by this fix").

**Ran Gemini's proposed reshape (0.40/0.30/[Alliance]/0.20) composed with this real, unchanged, already-shipped salience — not tested in isolation.** Tried both Alliance interpretations from Item 2 (0.0, literal; 0.15, realistic floor):

| | Own-profile rank (4 profiles) | Own-profile score |
|---|---|---|
| Current (no reshape) | 8, 8, 9, 8 | 0.806 / 0.806 / 0.817 / 0.900 |
| Gemini's reshape, Alliance=0.0 | 9, 9, 9, 9 | 0.723 / 0.723 / 0.746 / 0.854 |
| Gemini's reshape, Alliance=0.15 | 9, 9, 9, 9 | 0.725 / 0.725 / 0.752 / 0.863 |

**Not a catastrophic new conflict — `the_paper_tiger` was already losing these profiles before any change. But it's not an improvement either: rank stays essentially flat (8-9 → 9), and the own-profile scores actually drop on 3 of 4 profiles.** The mechanism: the existing salience already up-weights attitude (1.5×) and authority (1.0×) specifically to compensate for the *old* aptitude-dominant vector shape. Layering a *new* vector shape — which independently also raises authority (0.10→0.30) and attitude (0.10→0.20) — on top of salience that was calibrated against the old shape doesn't add up to a better fit; it pulls the resulting direction away from where `the_paper_tiger`'s own real test-profile signal concentrates, rather than toward it. **If this reshape is pursued, the salience needs to be re-derived alongside it, not composed with the version that was calibrated for a different vector — applying the new vector on top of the old salience does not achieve whatever improvement the reshape proposal was meant to deliver.**

---

## Bottom line

Two of four Gemini claims check out cleanly (#1's formula description, #3's tie status). Two carry real, confirmed problems: #1's algebra is correct but doesn't support the conclusion drawn from it (targets an operation nobody proposed), and #2's own arithmetic is internally inconsistent. #4 isn't wrong so much as incomplete — the proposed reshape was evidently never tested against the real, already-shipped salience it would actually have to coexist with, and doing so here shows it doesn't accomplish the apparent goal. None of this is treated as authorization to scope, propose, or search further — that's Pete's call, informed by these four findings.
