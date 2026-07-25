import fs from "fs";
import path from "path";
import type { BookContentType } from "@/lib/book-manifest";

const CONTENT_ROOT = path.join(process.cwd(), "content", "book");

/**
 * Reads a /book piece's raw markdown body from web/content/book/{type}/{slug}.md
 * and strips a leading H1, if present. page.tsx already renders the real
 * title from book-manifest.ts -- an in-body "# Title" line (present in most
 * files as the first line) would otherwise duplicate it. Stripped
 * unconditionally on position (first non-empty line is a level-1 heading),
 * not by string-matching piece.title -- an exact-match requirement would be
 * fragile against whitespace, punctuation, or rewording drift between the
 * title field and the file.
 */
export function getBookPieceContent(contentType: BookContentType, slug: string): string {
  const filePath = path.join(CONTENT_ROOT, contentType, `${slug}.md`);
  const raw = fs.readFileSync(filePath, "utf-8");
  return stripLeadingH1(raw);
}

function stripLeadingH1(markdown: string): string {
  const lines = markdown.split("\n");
  let i = 0;
  while (i < lines.length && lines[i].trim() === "") {
    i++;
  }
  if (i < lines.length && /^#\s+/.test(lines[i])) {
    lines.splice(i, 1);
    return lines.join("\n").replace(/^\n+/, "");
  }
  return markdown;
}
