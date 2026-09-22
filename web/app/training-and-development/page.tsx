import type { Metadata } from "next";
import Link from "next/link";

// Landing page shell and body copy shipped MOB v4.317 -- see
// tools/_mob.txt Section 16. Corrects the /about/services-era description (the full
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
          Training built around what your people actually need: we coach
          individuals, run group sessions, or work co-led with your own
          leaders.
        </h1>
        <div className="space-y-4">
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            Most training gets bought off a shelf. A leadership workshop
            that fits every company fits none of them particularly well,
            and everyone in the room knows it. Six months later the binder
            is somewhere in a drawer and nothing about how the team
            actually works has changed.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            We build the training around your people first, and choose the
            format second. Sometimes that&apos;s one person getting
            individual coaching through a specific transition. Sometimes
            it&apos;s a group session built around a pattern we&apos;ve
            actually seen in your organization, not a generic curriculum
            with your logo added. Sometimes the strongest version is
            co-led — your own leaders in the room, building the
            capability to run it themselves next time instead of needing
            us again.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            If you&apos;re not sure whether the gap is a training gap or
            something structural underneath it, that&apos;s what the
            diagnostic is for. Fifteen minutes tells you which of the four
            conditions applies before you commit to any of them.
          </p>
        </div>
        <Link
          href="/diagnostic"
          className="inline-block mt-8 font-ui text-sm font-medium text-ink underline hover:opacity-90 transition-opacity"
        >
          Take the diagnostic →
        </Link>
      </div>
    </main>
  );
}
