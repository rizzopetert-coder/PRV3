import { notFound } from "next/navigation";
import Link from "next/link";
import { bookManifest } from "@/lib/book-manifest";
import { states } from "@/data/taxonomy";

const STATE_THRESHOLD = 2;

function stateIdToSlug(id: string): string {
  return id.replace(/_/g, "-");
}

function slugToStateId(slug: string): string {
  return slug.replace(/-/g, "_");
}

function computeQualifyingStateIds(): Set<string> {
  const counts = new Map<string, number>();
  for (const piece of bookManifest) {
    if (piece.status !== "published" || !piece.stateIds) continue;
    for (const stateId of piece.stateIds) {
      counts.set(stateId, (counts.get(stateId) ?? 0) + 1);
    }
  }
  const qualifying = new Set<string>();
  for (const [stateId, count] of counts) {
    if (count >= STATE_THRESHOLD) qualifying.add(stateId);
  }
  return qualifying;
}

// Computed once at module load -- bookManifest is static data, not
// runtime-dependent, so this is safe to share between
// generateStaticParams and the page body without recomputing per request.
const QUALIFYING_STATE_IDS = computeQualifyingStateIds();

interface Props {
  params: Promise<{ stateSlug: string }>;
}

export function generateStaticParams() {
  // Threshold gating happens here, by omission -- states below
  // STATE_THRESHOLD simply never appear in this returned array, so
  // Next.js never statically generates a page for them.
  return Array.from(QUALIFYING_STATE_IDS).map((stateId) => ({
    stateSlug: stateIdToSlug(stateId),
  }));
}

export default async function StatePage({ params }: Props) {
  const { stateSlug } = await params;
  const stateId = slugToStateId(stateSlug);

  // Defensive fallback for a direct request to a non-generated
  // stateSlug (Next's default dynamicParams behavior still invokes
  // this page function for unlisted params) -- mirrors the existing
  // app/book/[type]/[slug]/page.tsx's own notFound() pattern, not a
  // second gating mechanism competing with generateStaticParams above.
  if (!QUALIFYING_STATE_IDS.has(stateId)) {
    notFound();
  }

  const state = states.find((s) => s.id === stateId);
  if (!state) notFound();

  const pieces = bookManifest.filter(
    (p) => p.status === "published" && p.stateIds?.includes(stateId)
  );

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-12">{state.name}</h1>
      <ul className="divide-y divide-gray-100">
        {pieces.map((piece) => (
          <li key={piece.id} className="py-8">
            <Link href={`/book/${piece.contentType}/${piece.slug}`} className="block">
              <h2
                className={
                  piece.voice === "from_the_author"
                    ? "font-display text-xl text-charcoal mb-2"
                    : "font-ui text-xl font-medium text-charcoal mb-2"
                }
              >
                {piece.title}
              </h2>
              <p className="font-ui text-sm text-gray-500">{piece.teaser}</p>
            </Link>
          </li>
        ))}
      </ul>
    </main>
  );
}
