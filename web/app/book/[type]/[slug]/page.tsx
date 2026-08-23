import { notFound } from "next/navigation";
import { bookManifest, type BookContentType, type BookPiece } from "@/lib/book-manifest";
import { getBookPieceContent } from "@/lib/book-content";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";
import BookPieceContent from "@/components/BookPieceContent";

const VALID_TYPES = new Set<BookContentType>(["memo", "methodology", "case_pattern"]);

function buildJsonLd(piece: BookPiece): Record<string, unknown> {
  const jsonLd: Record<string, unknown> = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: piece.title,
    description: piece.teaser,
    author: { "@type": "Organization", name: "Principal Resolution" },
    publisher: { "@type": "Organization", name: "Principal Resolution" },
    mainEntityOfPage: {
      "@type": "WebPage",
      "@id": `https://principalresolution.com/book/${piece.contentType}/${piece.slug}`,
    },
  };

  // Omitted entirely (not a contentPillar fallback) when primaryDimension
  // is unset -- contentPillar is internal editorial categorization, not
  // real-world subject matter, so it isn't a valid schema.org "about" topic.
  if (piece.primaryDimension) {
    jsonLd.about = [
      { "@type": "Thing", name: PUBLIC_DIMENSION_LABELS[piece.primaryDimension].title },
    ];
  }

  return jsonLd;
}

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

  const body = getBookPieceContent(piece.contentType, piece.slug);
  const jsonLd = buildJsonLd(piece);

  return <BookPieceContent piece={piece} body={body} jsonLd={jsonLd} />;
}
