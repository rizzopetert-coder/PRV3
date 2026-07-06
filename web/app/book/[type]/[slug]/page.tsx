import { notFound } from "next/navigation";
import { bookManifest, type BookContentType } from "@/lib/book-manifest";

const VALID_TYPES = new Set<BookContentType>(["memo", "methodology", "case_pattern"]);

interface Props {
  params: Promise<{ type: string; slug: string }>;
}

export function generateStaticParams() {
  return bookManifest
    .filter((p) => p.status === "published")
    .map((p) => ({ type: p.contentType, slug: p.slug }));
}

export default async function BookPiecePage({ params }: Props) {
  const { type, slug } = await params;

  if (!VALID_TYPES.has(type as BookContentType)) {
    notFound();
  }

  const piece = bookManifest.find(
    (p) => p.contentType === type && p.slug === slug && p.status === "published"
  );

  if (!piece) notFound();

  const headingClass =
    piece.voice === "from_the_author"
      ? "font-display text-3xl text-charcoal mb-4"
      : "font-ui text-3xl font-medium text-charcoal mb-4";

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className={headingClass}>{piece.title}</h1>
      <p className="font-ui text-sm text-gray-400 mb-8">{piece.teaser}</p>
      {/* Content body — rendered from web/content/book/{type}/{slug}.md in content migration pass */}
    </main>
  );
}
