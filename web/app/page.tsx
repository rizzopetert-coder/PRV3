import Link from "next/link";
import { ConstellationField } from "@/components/ConstellationField";

export default function Home() {
  return (
    <main className="min-h-screen bg-paper">
      <div className="max-w-2xl mx-auto px-6 py-16 md:px-10 md:py-24">

        {/* Section 1 — Opening statements (hero) — Stage 4 proof point.
            Wrapper mechanics (relative + overflow-hidden + absolute-inset
            motif behind centered-z-index content) ported from
            mockups/pr-ambient-constellation-animation.html's .hero/.
            ambient-svg/.hero-content rules. Copy and left alignment are
            this site's own existing approved content, not the mockup's
            placeholder text — only the layout technique is borrowed. */}
        <section className="relative overflow-hidden min-h-105 flex items-center mb-16">
          <ConstellationField mode="ambient" />
          <div className="relative z-10">
            <p className="font-display text-3xl md:text-5xl leading-tight text-charcoal my-8 md:my-12">
              People problems are usually structural problems wearing a
              person&apos;s name.
            </p>
            <p className="font-display text-3xl md:text-5xl leading-tight text-charcoal my-8 md:my-12">
              No fixed methodology. Every read starts from your organization, not
              a template applied to it.
            </p>
            {/* Muted-text technique ported from the mockup's .lede rule
                (opacity on the base ink color, not a separate gray
                shade) — applied here to match the hero specifically;
                Sections 2/3 below keep the site's existing gray-scale
                treatment, which is a hierarchy choice independent of
                which token system is active. */}
            <p className="font-ui text-base text-charcoal opacity-70 mt-4">
              If something in your organization isn&apos;t working and you
              can&apos;t quite name it, you&apos;ve come to the right place.
            </p>
          </div>
        </section>

        {/* Section 2 — Three paths */}
        <section className="mb-16 space-y-10">

          {/* Orientation copy — closes the site-wide orientation gap
              (Section 13, item 5) alongside the diagnostic-to-services
              funnel clarification, per Pete's direction to handle both
              together. Sits directly above the three entry points below,
              sharing this section's own space-y-10 rhythm rather than a
              separate margin, so it reads as one continuous run into the
              buttons rather than a fourth separated block. Second
              paragraph echoes the three button labels below verbatim --
              keep in sync if those labels ever change. */}
          <div className="space-y-4">
            <p className="font-ui text-base text-charcoal">
              The diagnostic names the specific condition producing the
              friction inside an organization, whatever&apos;s driving it,
              however it&apos;s showing up. From there,{" "}
              <Link href="/about/services" className="underline hover:text-charcoal">
                what we do
              </Link>{" "}
              depends on what it finds.
            </p>
            <p className="font-ui text-base text-charcoal">
              Not sure where to start? Begin the diagnostic if something
              specific is already on your mind. Explore the conditions if
              you want to see whether this is a known pattern first. Just
              ask if you&apos;d rather talk it through before doing
              either.
            </p>
          </div>

          {/* Path 1 — primary */}
          <div className="space-y-2" data-emphasis="primary">
            <h2 className="font-display text-xl font-bold text-charcoal">
              Start with the diagnostic.
            </h2>
            <p className="font-ui text-base text-gray-600">
              Answer questions. Get a precise read of what your organization is
              carrying.
            </p>
            <div className="pt-2">
              <Link
                href="/diagnostic"
                className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 hover:bg-gray-700 transition-colors"
              >
                Begin the diagnostic →
              </Link>
            </div>
          </div>

          {/* Path 2 — secondary */}
          <div className="space-y-2" data-emphasis="secondary">
            <h3 className="font-ui text-lg font-semibold text-charcoal">
              Start by recognizing what&apos;s familiar.
            </h3>
            <p className="font-ui text-sm text-gray-600">
              Select the conditions that sound like yours. See what they mean
              together.
            </p>
            <div className="pt-1">
              <Link
                href="/diagnostic"
                className="inline-block border border-charcoal text-charcoal font-ui text-sm font-medium px-5 py-2 hover:bg-gray-100 transition-colors"
              >
                Explore the conditions →
              </Link>
            </div>
          </div>

          {/* Path 3 — secondary */}
          <div className="space-y-2" data-emphasis="secondary">
            <h3 className="font-ui text-lg font-semibold text-charcoal">
              Come with a specific situation.
            </h3>
            <p className="font-ui text-sm text-gray-600">
              If you already know what you&apos;re dealing with, start a
              conversation directly.
            </p>
            <div className="pt-1">
              <Link
                href="/ask"
                className="inline-block border border-charcoal text-charcoal font-ui text-sm font-medium px-5 py-2 hover:bg-gray-100 transition-colors"
              >
                Just ask →
              </Link>
            </div>
          </div>

          {/* Content link */}
          <div className="pt-2">
            <Link
              href="/book"
              className="font-ui text-sm text-gray-500 hover:text-charcoal transition-colors"
            >
              Explore the research and thinking behind the work. →
            </Link>
          </div>
        </section>

        {/* Section 3 — Footer line */}
        <section className="mt-16">
          <p className="font-ui text-sm text-gray-400">
            Principal Resolution.
          </p>
        </section>

      </div>
    </main>
  );
}
