import type { Metadata } from "next";

// Landing page shell (this session). Structure and the sidebar teaser copy
// only -- full body copy is an explicit separate follow-up pass, see
// tools/_mob.txt. Copy here must not assume a visitor already has a
// standing relationship with the practice -- this is often their first
// encounter with the page. Route slug and display name both match
// engine/resolution_families.py's commercial name for this service (Pete's
// explicit unification decision, this session) -- was /advisory.

export const metadata: Metadata = {
  title: "Executive Advisory | Principal Resolution",
};

export default function ExecutiveAdvisoryPage() {
  return (
    <main className="bg-background min-h-screen">
      <div className="max-w-2xl mx-auto px-6 py-16 md:py-24">
        <p className="font-mono text-xs tracking-widest uppercase text-(--slate) mb-4">
          Executive Advisory
        </p>
        <h1 className="font-display text-3xl md:text-4xl leading-tight text-ink mb-6">
          A standing relationship, built over time. When the hardest
          decisions arrive, you have someone who already understands your
          organization instead of starting from scratch.
        </h1>
        <p className="font-ui text-sm text-(--slate)">
          Full detail on this page is coming soon.
        </p>
      </div>
    </main>
  );
}
