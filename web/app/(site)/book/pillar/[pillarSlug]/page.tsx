import { notFound } from "next/navigation";
import { bookManifest, type BookPiece } from "@/lib/book-manifest";
import BookTaxonomyListContent from "@/components/BookTaxonomyListContent";

type ContentPillar = NonNullable<BookPiece["contentPillar"]>;

const PILLARS: ContentPillar[] = ["Reframe", "Pattern Named", "Case Composited", "Underneath", "Foundation"];

function slugifyPillar(pillar: string): string {
  return pillar.toLowerCase().replace(/\s+/g, "-");
}

const SLUG_TO_PILLAR = new Map<string, ContentPillar>(PILLARS.map((p) => [slugifyPillar(p), p]));

interface Props {
  params: Promise<{ pillarSlug: string }>;
}

export function generateStaticParams() {
  return PILLARS.map((pillar) => ({ pillarSlug: slugifyPillar(pillar) }));
}

export default async function PillarPage({ params }: Props) {
  const { pillarSlug } = await params;
  const pillar = SLUG_TO_PILLAR.get(pillarSlug);

  if (!pillar) notFound();

  const pieces = bookManifest.filter((p) => p.status === "published" && p.contentPillar === pillar);

  return <BookTaxonomyListContent title={pillar} pieces={pieces} />;
}
