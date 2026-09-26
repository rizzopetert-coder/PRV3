import { notFound } from "next/navigation";
import { bookManifest, type DimensionKey } from "@/lib/book-manifest";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";
import BookTaxonomyListContent from "@/components/BookTaxonomyListContent";

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

  return <BookTaxonomyListContent title={label.title} description={label.description} pieces={pieces} />;
}
