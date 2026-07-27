import { notFound } from "next/navigation";
import Link from "next/link";
import { bookManifest, type BookPiece } from "@/lib/book-manifest";

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

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-12">{pillar}</h1>
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
