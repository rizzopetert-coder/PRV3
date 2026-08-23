"use client";

import Link from "next/link";
import type { BookPiece } from "@/lib/book-manifest";
import { useTheme } from "@/components/ThemeSwitcher";
import { HEADING_ACCENT_CLASS } from "@/lib/theme-role-tokens";

// Shared rendering for /book/state/[stateSlug], /book/dimension/
// [dimensionSlug], /book/pillar/[pillarSlug] -- Dark/Neutral rollout,
// Gemini-cleared batch (this session). Genuinely identical rendering
// pattern across all three (h1, optional intro paragraph, pieces list
// or "Coming soon."), so shared here rather than duplicated three times
// -- each route's own page.tsx stays a thin Server Component (keeps
// generateStaticParams/notFound/data lookup) and passes its resolved
// data down as props. h1 -> heading accent (Pete's call). Description,
// "Coming soon.", and each piece's teaser -> oxide-text (Pete's call).
// List-item titles -> oxide-text, not a heading role (Pete's call).
interface Props {
  title: string;
  description?: string;
  pieces: BookPiece[];
}

export default function BookTaxonomyListContent({ title, description, pieces }: Props) {
  const theme = useTheme();
  const heading = HEADING_ACCENT_CLASS[theme];

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className={`font-display text-3xl ${heading} ${description ? "mb-4" : "mb-12"}`}>{title}</h1>
      {description && <p className="font-ui text-base text-oxide-text mb-12">{description}</p>}
      {pieces.length === 0 ? (
        <p className="font-ui text-base text-oxide-text">Coming soon.</p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {pieces.map((piece) => (
            <li key={piece.id} className="py-8">
              <Link href={`/book/${piece.contentType}/${piece.slug}`} className="block">
                <h2
                  className={
                    piece.voice === "from_the_author"
                      ? "font-display text-xl text-oxide-text mb-2"
                      : "font-ui text-xl font-medium text-oxide-text mb-2"
                  }
                >
                  {piece.title}
                </h2>
                <p className="font-ui text-sm text-oxide-text">{piece.teaser}</p>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </main>
  );
}
