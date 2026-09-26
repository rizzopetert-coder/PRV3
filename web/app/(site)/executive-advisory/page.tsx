import type { Metadata } from "next";
import Link from "next/link";

// Landing page shell and body copy shipped MOB v4.317 -- see
// tools/_mob.txt Section 16. Copy here must not assume a visitor already has a
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
        <div className="space-y-4">
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            The hardest decisions rarely arrive on schedule. A
            restructuring you didn&apos;t see coming, a leader who
            isn&apos;t working out, a call that has to be made this week
            and lived with for years. What you need in that moment
            isn&apos;t a smart outside opinion. It&apos;s someone who
            knows your organization well enough to tell you the truth, not
            just what sounds reasonable to a stranger hearing it cold.
            That kind of judgment isn&apos;t available on demand. It has
            to be built.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            Executive Advisory is how it gets built: an ongoing
            relationship instead of a one-off engagement, so the credible
            perspective is earned and present when you need it. Some
            months that looks like a standing conversation. Some months it
            means coaching a specific leader through a transition. Either
            way, the advice you&apos;re getting has your actual history
            behind it, not a first impression.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            If you&apos;re not sure whether what you need is a standing
            relationship or a one-time engagement, that&apos;s what the
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
