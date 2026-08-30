"use client";

import Link from "next/link";
import { SignatureField } from "@/components/home/SignatureField";
import { WayfindingGrid } from "@/components/home/WayfindingGrid";
import { useScrollReveal } from "@/components/home/useScrollReveal";

// Homepage restructure (this session) -- copy below is Pete's final
// approved text, pulled verbatim from the approved HTML mockup, not
// paraphrased or re-derived. Palette is strict local scope via the
// .home-scope wrapper (globals.css) -- --home-paper/--home-field-raise/
// --home-slate never touch the sitewide --color-paper/--color-slate flat
// tokens (see globals.css comment: --color-slate is the live render color
// for every non-Endemic severity badge, a global change would silently
// recolor real client diagnostic output).

const TAGS = [
  "Leadership behaviors",
  "Planning",
  "Structures",
  "Policies",
  "Practices",
  "Incentives",
  "Disincentives",
  "Benefits",
];

function VoiceSection() {
  const { ref, className } = useScrollReveal<HTMLDivElement>();

  return (
    <section ref={ref} className={`max-w-3xl mx-auto ${className}`}>
      <p className="font-mono text-xs tracking-widest text-(--home-slate) mb-6">
        THE PERSPECTIVE
      </p>
      <p className="font-display text-2xl md:text-3xl leading-relaxed text-charcoal mb-6">
        Many of the &quot;people problems&quot; leaders describe are the
        symptoms of deeper conditions that are more challenging to work
        through. Because they&apos;re more challenging, and often require
        leaders to look in the mirror, it is often easier for leaders to
        believe they&apos;re a training or a PIP or a termination away from
        resolving their problems. But workplace performance and behaviors
        are significantly influenced by leadership behaviors: consistency,
        accountability, strong communication, and a fundamental
        understanding of the organization&apos;s values. Consistent
        leadership behaviors result in more consistent employee behaviors,
        and more consistent, more predictable results.
      </p>
      <p className="font-ui text-base leading-relaxed text-charcoal opacity-80 mb-4">
        Clients don&apos;t need another framework or slide deck. They want a
        confidant and advisor with a perspective they know they can trust. A
        partner with a genuine understanding of their business, their
        history, their values, and what they&apos;re actually trying to
        build. And given all that, someone who can filter out the noise and
        give the objective truth.
      </p>
      <p className="font-ui text-base leading-relaxed text-charcoal opacity-80 mb-10">
        I don&apos;t tell you what decision to make. Decide what&apos;s best
        for your business, and give me the marching orders. We&apos;ll help
        you get there.
      </p>
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-full bg-(--home-slate) text-white flex items-center justify-center font-display text-lg shrink-0">
          P
        </div>
        <p className="font-ui text-sm text-charcoal opacity-70">
          Founder, Principal Resolution
        </p>
      </div>
    </section>
  );
}

function CloserSection() {
  const { ref, className } = useScrollReveal<HTMLDivElement>();

  return (
    <section ref={ref} className={`text-center max-w-xl mx-auto ${className}`}>
      <h2 className="font-display text-3xl text-charcoal mb-4">
        Give the Diagnostic a try.
      </h2>
      <p className="font-ui text-base text-charcoal opacity-70 mb-8">
        No pitch, no pressure. If anything sounds familiar, reach out.
      </p>
      <Link
        href="/diagnostic"
        className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 hover:bg-gray-700 transition-colors"
      >
        Begin the diagnostic →
      </Link>
    </section>
  );
}

export default function Home() {
  return (
    <main className="home-scope bg-(--home-paper) min-h-screen">
      <div className="max-w-5xl mx-auto px-6 py-16 md:px-10 md:py-24 space-y-24">

        {/* Hero */}
        <section className="grid lg:grid-cols-2 gap-12 items-center">
          <div>
            <p className="font-mono text-xs tracking-widest text-(--home-slate) mb-4">
              PRINCIPAL RESOLUTION
            </p>
            <h1 className="font-display text-4xl md:text-5xl leading-tight text-charcoal mb-6">
              What looks like a people problem is usually{" "}
              <em className="not-italic font-semibold text-(--home-slate)">
                structural
              </em>
              .
            </h1>
            <div className="flex flex-wrap gap-2 mb-6">
              {TAGS.map((tag) => (
                <span
                  key={tag}
                  className="font-ui text-xs uppercase tracking-wide text-(--home-slate) border border-(--home-slate) px-3 py-1"
                >
                  {tag}
                </span>
              ))}
            </div>
            <p className="font-ui text-base text-charcoal opacity-80 leading-relaxed">
              Issues and inconsistencies with these things often produce
              &quot;people problems&quot; while masking the deeper
              fundamentals underneath. I help leaders find the real
              conditions threatening their organization, then work through
              what is found together.
            </p>
          </div>

          {/* Signature field -- SignatureField (homepage-local), not
              ConstellationField mode="ambient" -- that component's static
              outline fell short of the approved mockup (no breathing
              rings, no vertex dots, no ambient motion), confirmed by Pete
              against a live screenshot. ConstellationField.tsx itself is
              untouched -- see SignatureField.tsx's own header comment. */}
          <SignatureField />
        </section>

        {/* Credential band */}
        <p className="font-mono text-xs tracking-widest text-(--home-slate) text-center">
          58 STATES · 4 DIMENSIONS · 1 INSTRUMENT
        </p>

        <VoiceSection />

        {/* Wayfinding */}
        <section>
          <p className="font-mono text-xs tracking-widest text-(--home-slate) mb-6 text-center">
            WHERE TO GO FROM HERE
          </p>
          <WayfindingGrid />
        </section>

        <CloserSection />

        {/* Footer */}
        <p className="font-ui text-sm text-gray-400 text-center">
          Principal Resolution.
        </p>

      </div>
    </main>
  );
}
