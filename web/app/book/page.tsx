import Link from "next/link";
import { bookManifest } from "@/lib/book-manifest";

export default function BookPage() {
  const published = bookManifest.filter((p) => p.status === "published");

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-gray-900 mb-4">The Book</h1>
      <p className="font-ui text-base text-gray-600 mb-12">
        Explore the research and thinking behind the work.
      </p>
      {published.length === 0 ? (
        <p className="font-ui text-base text-gray-400">Coming soon.</p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {published.map((piece) => (
            <li key={piece.id} className="py-8">
              <Link href={`/book/${piece.contentType}/${piece.slug}`} className="block">
                <h2
                  className={
                    piece.voice === "from_the_author"
                      ? "font-display text-xl text-gray-900 mb-2"
                      : "font-ui text-xl font-medium text-gray-900 mb-2"
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
