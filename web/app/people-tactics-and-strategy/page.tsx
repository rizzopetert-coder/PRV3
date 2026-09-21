import type { Metadata } from "next";

// Landing page shell (this session). Structure and the sidebar teaser copy
// only -- full body copy is an explicit separate follow-up pass, see
// tools/_mob.txt. Corrects the /about/services-era description
// ("structural diagnosis and resolution," not group training -- that's
// Training & Development's territory). Route slug and display name both
// match engine/resolution_families.py's commercial name for this service
// (Pete's explicit unification decision, this session) -- was /groundwork.

export const metadata: Metadata = {
  title: "People Tactics & Strategy | Principal Resolution",
};

export default function PeopleTacticsAndStrategyPage() {
  return (
    <main className="bg-background min-h-screen">
      <div className="max-w-2xl mx-auto px-6 py-16 md:py-24">
        <p className="font-mono text-xs tracking-widest uppercase text-(--slate) mb-4">
          People Tactics &amp; Strategy
        </p>
        <h1 className="font-display text-3xl md:text-4xl leading-tight text-ink mb-6">
          We find the organizational conditions producing your problems and
          resolve them at the structure, not just the symptom.
        </h1>
        <p className="font-ui text-sm text-(--slate)">
          Full detail on this page is coming soon.
        </p>
      </div>
    </main>
  );
}
