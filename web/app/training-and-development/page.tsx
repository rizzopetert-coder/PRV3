import type { Metadata } from "next";

// Landing page shell (this session). Structure and the sidebar teaser copy
// only -- full body copy is an explicit separate follow-up pass, see
// tools/_mob.txt. Corrects the /about/services-era description (the full
// training delivery service -- individual coaching, group/team training,
// and collaborative sessions co-led with client leaders -- not individual
// coaching only). Route slug and display name both match
// engine/resolution_families.py's commercial name for this service (Pete's
// explicit unification decision, this session) -- was /development.

export const metadata: Metadata = {
  title: "Training & Development | Principal Resolution",
};

export default function TrainingAndDevelopmentPage() {
  return (
    <main className="bg-background min-h-screen">
      <div className="max-w-2xl mx-auto px-6 py-16 md:py-24">
        <p className="font-mono text-xs tracking-widest uppercase text-(--slate) mb-4">
          Training &amp; Development
        </p>
        <h1 className="font-display text-3xl md:text-4xl leading-tight text-ink mb-6">
          Training built around what your people actually need: individual
          coaching, group sessions, or work co-led with your own leaders.
        </h1>
        <p className="font-ui text-sm text-(--slate)">
          Full detail on this page is coming soon.
        </p>
      </div>
    </main>
  );
}
