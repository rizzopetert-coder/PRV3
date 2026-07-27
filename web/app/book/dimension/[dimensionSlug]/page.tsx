import { notFound } from "next/navigation";
import Link from "next/link";
import { bookManifest, type DimensionKey } from "@/lib/book-manifest";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";

const VALID_DIMENSIONS = new Set<DimensionKey>(["aptitude", "authority", "alliance", "attitude"]);

interface Props {
  params: Promise<{ dimensionSlug: string }>;
}

export function generateStaticParams() {
  return (Object.keys(PUBLIC_DIMENSION_LABELS) as DimensionKey[]).map((dimensionSlug) => ({
    dimensionSlug,
  }));
}

export default async function DimensionPage({ params }: Props) {
  const { dimensionSlug } = await params;

  if (!VALID_DIMENSIONS.has(dimensionSlug as DimensionKey)) {
    notFound();
  }
  const dimension = dimensionSlug as DimensionKey;
  const label = PUBLIC_DIMENSION_LABELS[dimension];

  const pieces = bookManifest.filter(
    (p) => p.status === "published" && p.primaryDimension === dimension
  );

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-4">{label.title}</h1>
      <p className="font-ui text-base text-gray-600 mb-12">{label.description}</p>
      {pieces.length === 0 ? (
        <p className="font-ui text-base text-gray-400">Coming soon.</p>
      ) : (
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
      )}
    </main>
  );
}
