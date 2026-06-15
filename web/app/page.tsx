import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-2xl mx-auto px-6 py-16 md:px-10 md:py-24">

        {/* Section 1 — Opening */}
        <section className="mb-14">
          <p className="font-display text-xl leading-relaxed text-gray-900 mb-6">
            Most organizations know something is wrong before they can say what
            it is. The presenting complaint — the thing that prompted someone to
            look for help — is real. It is rarely the whole story.
          </p>
          <p className="font-display text-xl leading-relaxed text-gray-500">
            We don&apos;t arrive with a methodology and fit you into it. We start
            with you.
          </p>
        </section>

        {/* Section 2 — Practice description */}
        <section className="mb-14">
          <p className="text-base leading-relaxed text-gray-700">
            Principal Resolution is an organizational friction consulting
            practice. We identify the conditions underneath the presenting
            complaint — the ones producing it, sustaining it, and making it
            resistant to the solutions that should be working. We name them
            precisely. We put their coexistence in context. Then we resolve them.
          </p>
        </section>

        {/* Section 3 — Differentiator */}
        <section className="mb-14">
          <p className="text-base leading-relaxed text-gray-900 font-medium">
            Every other consulting service addresses the presenting complaint. We
            address the condition underneath it. That distinction is the practice.
          </p>
        </section>

        {/* Section 4 — Path introduction */}
        <section className="mb-12">
          <h2 className="font-display text-lg font-medium text-gray-900 mb-4">
            How people work with us
          </h2>
          <div className="space-y-3">
            <p className="text-base leading-relaxed text-gray-700">
              There is no single entry point here. Organizations arrive at
              different stages of understanding — some know precisely what
              they&apos;re dealing with, some have a direction but not a name for
              it, some are starting from a felt sense that something is wrong.
              We meet you where you are.
            </p>
            <p className="text-base leading-relaxed text-gray-700">
              Three paths in. All of them lead to the same place.
            </p>
          </div>
        </section>

        {/* Section 5 — Three paths */}
        <section className="space-y-12 mb-14">

          {/* Path 1 */}
          <div className="space-y-3">
            <h3 className="font-display text-base font-medium text-gray-900">
              Take the diagnostic
            </h3>
            <p className="text-sm leading-relaxed text-gray-700">
              The instrument observes. The engine infers. The output names.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              You respond to a structured sequence of questions designed to
              surface organizational signal without telegraphing what
              they&apos;re measuring. The engine reads the pattern. What comes
              back is a precise identification of the conditions present in your
              organization — named, contextualized, and routed to a resolution
              path.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              No two signatures are identical. Yours won&apos;t be either.
            </p>
            <Link
              href="/diagnostic"
              className="font-ui inline-block text-sm font-medium text-gray-900 underline underline-offset-2 decoration-gray-400 hover:decoration-gray-900 transition-colors"
            >
              Take the diagnostic →
            </Link>
          </div>

          {/* Path 2 */}
          <div className="space-y-3">
            <h3 className="font-display text-base font-medium text-gray-900">
              Read the signatures
            </h3>
            <p className="text-sm leading-relaxed text-gray-700">
              If you&apos;d rather start by recognizing than responding, start
              here.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              Browse the conditions we identify — all 47 of them, each described
              in plain language — and select the ones that resemble what
              you&apos;re seeing in your organization. The engine assembles what
              your selections suggest into a signature: which patterns are
              present, what their coexistence means, and what resolution looks
              like from where you are.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              Either way, what you build here is a starting point. The diagnostic
              finds what you weren&apos;t looking for.
            </p>
            <Link
              href="/diagnostic"
              className="font-ui inline-block text-sm font-medium text-gray-900 underline underline-offset-2 decoration-gray-400 hover:decoration-gray-900 transition-colors"
            >
              Browse the signatures →
            </Link>
          </div>

          {/* Path 3 */}
          <div className="space-y-3">
            <h3 className="font-display text-base font-medium text-gray-900">
              Start a conversation
            </h3>
            <p className="text-sm leading-relaxed text-gray-700">
              If you already know what you&apos;re dealing with and you&apos;re
              ready to talk about what to do, skip the instrument entirely.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              Tell us what&apos;s happening. We&apos;ll tell you what we see and
              whether we&apos;re the right practice for it.
            </p>
            <button
              type="button"
              className="font-ui text-sm font-medium text-gray-900 underline underline-offset-2 decoration-gray-400"
            >
              Start a conversation →
            </button>
          </div>

        </section>

        {/* Section 6 — Load-bearing statement */}
        <section className="mb-14">
          <p className="font-display text-xl leading-relaxed text-gray-900">
            We don&apos;t fix people problems. We change the conditions that
            produce them.
          </p>
        </section>

        {/* Section 7 — Service orientation */}
        <section className="mb-14">
          <h2 className="font-display text-lg font-medium text-gray-900 mb-4">
            What resolution looks like
          </h2>
          <div className="space-y-4">
            <p className="text-sm leading-relaxed text-gray-700">
              The diagnostic is where every engagement begins. What follows
              depends on what it finds.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              For some organizations the work is structural — roles, processes,
              decision rights, accountability architecture that hasn&apos;t kept
              pace with what the organization has become.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              For some it&apos;s cultural — the conditions that have made it
              impossible for people to do what the organization needs them to do.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              For some it&apos;s acute — something is happening now and it
              can&apos;t wait for a deliberate process.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              For some it&apos;s developmental — the people the organization
              needs to grow into its next chapter aren&apos;t being built.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              For some it&apos;s a standing resource — a thought partner outside
              the org chart who can be reached when the situation requires honest
              counsel rather than managed advice.
            </p>
            <p className="text-sm leading-relaxed text-gray-700">
              The diagnostic tells us which. Sometimes it tells us several at
              once.
            </p>
            <button
              type="button"
              className="font-ui text-sm font-medium text-gray-900 underline underline-offset-2 decoration-gray-400"
            >
              Learn about our services →
            </button>
          </div>
        </section>

        {/* Section 8 — Footer line */}
        <section className="pt-10 border-t border-gray-200">
          <p className="text-sm text-gray-500 leading-relaxed">
            Principal Resolution operates on three commitments: effectiveness,
            candor, and humanity. You&apos;ll see them in the work before you see
            them on the page.
          </p>
        </section>

      </div>
    </main>
  );
}
