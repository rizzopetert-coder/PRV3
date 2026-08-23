"use client";

import ReactMarkdown from "react-markdown";
import type { BookPiece } from "@/lib/book-manifest";
import { useTheme } from "@/components/ThemeSwitcher";
import { HEADING_ACCENT_CLASS } from "@/lib/theme-role-tokens";

// Dark/Neutral rollout, Gemini-cleared batch (this session). h1 and the
// markdown-rendered h2/h3 -> heading accent (Pete's call for h1;
// markdown h2/h3 match /about/story's own section-heading precedent
// directly, not separately asked). Teaser and markdown body/ol text ->
// oxide-text (Pete's call for teaser). <strong> no longer sets an
// explicit color at all -- it's inline emphasis inside a paragraph
// that's already oxide-text, so it now inherits that color via the
// cascade instead of carrying a separate, redundant token reference.
interface Props {
  piece: BookPiece;
  body: string;
  jsonLd: Record<string, unknown>;
}

export default function BookPieceContent({ piece, body, jsonLd }: Props) {
  const theme = useTheme();
  const heading = HEADING_ACCENT_CLASS[theme];
  const headingClass =
    piece.voice === "from_the_author"
      ? `font-display text-3xl ${heading} mb-4`
      : `font-ui text-3xl font-medium ${heading} mb-4`;

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\u003c") }}
      />
      <h1 className={headingClass}>{piece.title}</h1>
      <p className="font-ui text-sm text-oxide-text mb-8">{piece.teaser}</p>
      <ReactMarkdown
        components={{
          h2: ({ children }) => (
            <h2 className={`font-display text-2xl md:text-3xl ${heading} mb-8 mt-12`}>{children}</h2>
          ),
          h3: ({ children }) => (
            <h3 className={`font-display text-xl md:text-2xl ${heading} mb-6 mt-10`}>{children}</h3>
          ),
          p: ({ children }) => (
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">{children}</p>
          ),
          hr: () => <hr className="my-8 border-gray-100" />,
          strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
          em: ({ children }) => <em className="italic">{children}</em>,
          ol: ({ children }) => (
            <ol className="font-ui text-base text-oxide-text leading-relaxed mb-5 list-decimal pl-6 space-y-2">
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
