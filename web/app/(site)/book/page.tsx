"use client";

import Link from "next/link";
import { bookManifest } from "@/lib/book-manifest";
import { useTheme } from "@/components/ThemeSwitcher";
import { HEADING_ACCENT_CLASS } from "@/lib/theme-role-tokens";

// Dark/Neutral rollout, Gemini-cleared batch (this session). h1 -> heading
// accent. Intro copy, "Coming soon." fallback, and each list item's
// teaser -> oxide-text (Pete's call: teaser/secondary text treated as
// body-copy tier, not left neutral gray the way /about/story's eyebrow
// labels were). List-item titles -> oxide-text too (Pete's call: treated
// as link/body text, not a heading role, since the whole row is a Link).
export default function BookPage() {
  const theme = useTheme();
  const published = bookManifest.filter((p) => p.status === "published");

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className={`font-display text-3xl ${HEADING_ACCENT_CLASS[theme]} mb-4`}>The Book</h1>
      <p className="font-ui text-base text-oxide-text mb-12">
        Explore the research and thinking behind the work.
      </p>
      {published.length === 0 ? (
        <p className="font-ui text-base text-oxide-text">Coming soon.</p>
      ) : (
        <ul className="divide-y divide-gray-100">
          {published.map((piece) => (
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
