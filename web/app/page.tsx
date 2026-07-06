import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-paper">
      <div className="max-w-2xl mx-auto px-6 py-16 md:px-10 md:py-24">

        {/* Section 1 — Opening statements */}
        <section className="mb-16">
          <p className="font-display text-3xl md:text-5xl leading-tight text-charcoal my-8 md:my-12">
            We don&apos;t arrive with a methodology and fit you into it. We start
            with you.
          </p>
          <p className="font-display text-3xl md:text-5xl leading-tight text-charcoal my-8 md:my-12">
            We don&apos;t fix people problems. We change the conditions that
            produce them.
          </p>
          <p className="font-ui text-base text-gray-500 mt-4">
            If something in your organization isn&apos;t working and you
            can&apos;t quite name it, you&apos;ve come to the right place.
          </p>
        </section>

        {/* Section 2 — Three paths */}
        <section className="mb-16 space-y-10">

          {/* Path 1 — primary */}
          <div className="space-y-2">
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
          <div className="space-y-2">
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
          <div className="space-y-2">
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
