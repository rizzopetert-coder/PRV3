import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { bookManifest, type BookContentType } from "@/lib/book-manifest";
import { getBookPieceContent } from "@/lib/book-content";

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

  const body = getBookPieceContent(piece.contentType, piece.slug);

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className={headingClass}>{piece.title}</h1>
      <p className="font-ui text-sm text-gray-400 mb-8">{piece.teaser}</p>
      <ReactMarkdown
        components={{
          h2: ({ children }) => (
            <h2 className="font-display text-2xl md:text-3xl text-charcoal mb-8 mt-12">{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className="font-display text-xl md:text-2xl text-charcoal mb-6 mt-10">{children}</h3>
          ),
          p: ({ children }) => (
            <p className="font-ui text-base text-gray-600 leading-relaxed mb-5">{children}</p>
          ),
          hr: () => <hr className="my-8 border-gray-100" />,
          strong: ({ children }) => <strong className="font-semibold text-charcoal">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          ol: ({ children }) => (
            <ol className="font-ui text-base text-gray-600 leading-relaxed mb-5 list-decimal pl-6 space-y-2">
              {children}
            </ol>
          ),
          li: ({ children }) => <li>{children}</li>,
        }}
      >
        {body}
      </ReactMarkdown>
    </main>
  );
}
