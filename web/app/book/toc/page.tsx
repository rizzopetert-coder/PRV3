import { BOOK_STATE_INDEX, type StateDimension } from "@/lib/book-state-index";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";
import { stateIdToSlug } from "@/lib/state-slug";

// Static content page -- all 58 states, grouped by dimension, each entry
// deep-linkable via #{slug} (PrivateOutput.tsx's secondary-state links
// point here). Content (name, descriptive_prose) is a verbatim mirror of
// engine/data/states.py, not authored on this page -- see
// web/lib/book-state-index.ts's own header for the sync discipline.

const DIMENSION_ORDER: StateDimension[] = ["aptitude", "authority", "alliance", "attitude"];

export default function StatesTocPage() {
  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-4">All States</h1>
      <p className="font-ui text-base text-gray-600 mb-12">
        The full set of organizational conditions the diagnostic identifies,
        grouped by the dimension of the organization each one shows up in.
      </p>

      {DIMENSION_ORDER.map((dimension) => {
        const label = PUBLIC_DIMENSION_LABELS[dimension];
        const entries = BOOK_STATE_INDEX.filter((s) => s.dimension === dimension);

        return (
          <section key={dimension} className="mb-16">
            <h2 className="font-display text-2xl text-charcoal mb-2">{label.title}</h2>
            <p className="font-ui text-sm text-gray-500 mb-8">{label.description}</p>

            <ul className="divide-y divide-gray-100">
              {entries.map((entry) => (
                <li key={entry.id} id={stateIdToSlug(entry.id)} className="py-8">
                  <h3 className="font-display text-xl text-charcoal mb-2">{entry.name}</h3>
                  <p className="font-ui text-sm text-gray-500 leading-relaxed">
                    {entry.descriptiveProse}
                  </p>
                </li>
              ))}
            </ul>
          </section>
        );
      })}
    </main>
  );
}
