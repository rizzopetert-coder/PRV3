import type { Metadata } from "next";
import Link from "next/link";

// Landing page shell and body copy shipped MOB v4.317 -- see
// tools/_mob.txt Section 16. Corrects the /about/services-era description
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
        <div className="space-y-4">
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            People challenges are rarely a simple, single problem to solve.
            A manager who can&apos;t hold a team together is a web of
            nuanced storylines. By the time it escalates to a
            decision-maker&apos;s desk, each of those storylines is a
            compounding problem for the business. The best-case solution
            requires hours of effort, patience, and expertise. That&apos;s
            where we come in.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            We work inside your organization alongside the people who have
            to live with the outcome, building the structural fix rather
            than handing you a slide deck and a bill. This is embedded
            work, not a report. Engagements are scoped to what&apos;s
            actually in front of you, priced by the work required rather
            than a fixed package, with day rates available when the work
            calls for us on-site.
          </p>
          <p className="font-ui text-sm text-(--slate) leading-relaxed">
            If you&apos;re not sure whether what you&apos;re facing is a
            People Tactics &amp; Strategy problem or something else,
            that&apos;s what the diagnostic is for. Fifteen minutes tells
            you which of the four conditions applies before you commit to
            any of them.
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
