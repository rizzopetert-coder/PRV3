# Category E, Direction 1 Refinement — Legibility, Motion, Interpretability

Status: DRAFT, concept-level. Not yet through Gemini review. Not started.

## Origin

Direction 1 (rendering-quality upgrade) shipped and was believed closed. Live review against an
actual result (`prv-3.vercel.app`, "The Uninitiated" / Endemic profile) surfaced three real gaps
Pete identified directly, not implied by any prior spec:

1. Doesn't feel like a 2026-built site — not dynamic enough.
2. On the ConstellationField itself: axis labels and features read small, not reader-friendly.
3. No one looking at the shape has any idea what it means, without narration.

Plus a standing communication principle stated explicitly this session, worth recording as its
own durable note since it isn't yet written anywhere else in the project's governing docs:
**spoon-feed meaning when not speaking plainly in brand voice.** A visualization that requires
narration to be understood is failing that standard on its own, independent of craft quality.

## Why this supersedes Direction 2, not sits alongside it

Direction 2 (four-dial instrument-panel reframe) was under consideration as a possible fix for
"doesn't look professionally made." That's not the actual problem. Four separate dials would
carry the same illegibility and the same interpretability gap, multiplied by four — replacing
the shape doesn't address either finding. This is scoped as a **refinement of the shipped
Direction 1 rendering**, not a new visual system. Direction 2 stays shelved.

## Governing-principle basis

P-06 (Principal Brief): *"The instrument meets the user where they are... The instrument cannot
assume the user has done it first."* A result the user can't interpret without outside narration
is a direct P-06 gap, not a polish item. This gives real cover to add explanation without it
reading as decoration against Saint-Exupéry discipline — the addition is the instrument doing
its stated job, not ornamentation on top of it.

## Scope, three parts

**1. Legibility.** Axis labels (APT / AUTH / ALL / ATT) and any other on-shape text sized and
weighted to actually read at a glance, not just be technically present. Current treatment reads
as an afterthought relative to the shape itself.

**2. Motion.** Two distinct pieces, both in the register of restraint the brief requires — motion
in service of the instrument reading correctly, not spectacle for its own sake:
   - An entrance animation on load — the shape assembling/resolving into place rather than
     appearing fully-formed and static.
   - Real interactivity: hover (desktop) or tap (mobile) on a vertex reveals that dimension's
     actual read — this is the mechanism, not a separate feature.

**3. Interpretability, solved by the same interactivity.** The hover/tap-to-reveal state doubles
as the fix for "no one knows what this means" — surfacing plain-brand-voice explanation on
demand, at the specific vertex being examined, rather than permanently cluttering the resting
state with a wall of legend text. Spoon-feed on demand, not spoon-feed always-on — this keeps
the shape's calm resting state intact while making the meaning available the moment someone
looks for it.

## Open, unresolved
- Exact copy for each dimension's on-demand explanation — not yet drafted, needs brand-voice
  pass (P-10: 40% blunt, 60% servant leader, no coined terms).
- Motion implementation approach — still CSS-only per the no-Framer-Motion standing call, but
  the specific entrance-animation mechanism (path draw-in vs. scale/fade vs. something else)
  isn't chosen yet.
- Mobile tap-to-reveal interaction pattern needs its own check — hover doesn't exist on touch,
  so this isn't a straight port of the desktop mechanism.

## Next steps
Touches ConstellationField's shipped rendering system directly — needs Gemini architecture
review before any code changes, per standing protocol, no exception for what might look like a
polish-only change. Not started.
