"""
PRV3 -- /book Content Architecture Phase 2, Step 5
Schema.org JSON-LD (Article) for app/book/[type]/[slug]/page.tsx.

Verified against the installed Next.js 16.2.9 docs
(node_modules/next/dist/docs/01-app/02-guides/json-ld.md) before
writing, per standing instruction not to assume the original handoff's
"via generateMetadata" framing was correct: current official guidance
is a <script type="application/ld+json"> rendered directly in the page
component, not generateMetadata (this file has no generateMetadata to
begin with -- confirmed by direct read -- so this addition is purely
additive, nothing existing to alter). The docs also flag an XSS
consideration for dangerouslySetInnerHTML -- JSON.stringify does not
sanitize, so `<` is escaped to its unicode equivalent before injection,
per the official recommendation.

`about` field handling, confirmed with Pete before writing:
  - primaryDimension set -> about = [{ "@type": "Thing", name:
    PUBLIC_DIMENSION_LABELS[dim].title }] (reuses the same public label
    already shown in nav, not a third phrasing)
  - primaryDimension unset (13 permanently-exempt entries, and LIB-014
    which has secondaryDimensions but no primaryDimension) -> "about"
    omitted entirely. contentPillar was considered as a fallback and
    rejected: it's internal editorial categorization (Reframe,
    Underneath, etc.), not real-world subject matter, so using it as
    a schema.org "about" subject would be semantically wrong, not just
    a weaker signal. LIB-014's secondaryDimensions are explicitly NOT
    used as a substitute primary here, matching the instruction not to
    default into that without a deliberate, separately-flagged choice.

Canonical URL uses the corrected /book/[type]/[slug] template
throughout (confirmed live in Step 4), not the flat /book/[slug] from
the original (pre-correction) Gemini review example.

Usage:
  python tools/patch_book_step5_jsonld.py --dry-run
  python tools/patch_book_step5_jsonld.py --write
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = REPO_ROOT / "web"
MANIFEST_FILE = WEB_ROOT / "lib" / "book-manifest.ts"
PAGE_FILE = WEB_ROOT / "app" / "book" / "[type]" / "[slug]" / "page.tsx"

OLD_IMPORTS = '''import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { bookManifest, type BookContentType } from "@/lib/book-manifest";
import { getBookPieceContent } from "@/lib/book-content";'''

NEW_IMPORTS = '''import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import { bookManifest, type BookContentType, type BookPiece } from "@/lib/book-manifest";
import { getBookPieceContent } from "@/lib/book-content";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";'''

JSONLD_FUNCTION = '''
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
  // is unset -- see this script's module docstring for why.
  if (piece.primaryDimension) {
    jsonLd.about = [
      { "@type": "Thing", name: PUBLIC_DIMENSION_LABELS[piece.primaryDimension].title },
    ];
  }

  return jsonLd;
}
'''

OLD_BODY_START = '''  const body = getBookPieceContent(piece.contentType, piece.slug);

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className={headingClass}>{piece.title}</h1>'''

NEW_BODY_START = '''  const body = getBookPieceContent(piece.contentType, piece.slug);
  const jsonLd = buildJsonLd(piece);

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd).replace(/</g, "\\\\u003c") }}
      />
      <h1 className={headingClass}>{piece.title}</h1>'''


def build_sample_jsonld(piece_id: str) -> dict | None:
    """Mirrors buildJsonLd()'s real branching against live manifest data,
    for the dry-run sample -- not hand-written expected output."""
    text = MANIFEST_FILE.read_text(encoding="utf-8")
    labels_text = (WEB_ROOT / "lib" / "book-taxonomy-labels.ts").read_text(encoding="utf-8")

    blocks = re.findall(r'\{\s*id: "[^"]+".*?\n  \},', text, re.DOTALL)
    block = next((b for b in blocks if re.search(rf'id: "{re.escape(piece_id)}"', b)), None)
    if block is None:
        return None

    def field(name: str) -> str | None:
        m = re.search(rf'{name}: "((?:[^"\\]|\\.)*)"', block)
        return m.group(1) if m else None

    title = field("title")
    teaser = field("teaser")
    content_type = field("contentType")
    slug = field("slug")
    dim = field("primaryDimension")

    jsonld: dict = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": title,
        "description": teaser,
        "author": {"@type": "Organization", "name": "Principal Resolution"},
        "publisher": {"@type": "Organization", "name": "Principal Resolution"},
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": f"https://principalresolution.com/book/{content_type}/{slug}",
        },
    }

    if dim:
        title_map = {}
        for m in re.finditer(r'(\w+):\s*\{\s*title:\s*"([^"]*)"', labels_text):
            title_map[m.group(1)] = m.group(2)
        jsonld["about"] = [{"@type": "Thing", "name": title_map.get(dim, f"<{dim} label not found>")}]

    return jsonld


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    text = PAGE_FILE.read_text(encoding="utf-8")

    if text.count(OLD_IMPORTS) != 1:
        print(f"ABORT -- expected imports block matched {text.count(OLD_IMPORTS)} times, need 1", file=sys.stderr)
        sys.exit(1)
    if text.count(OLD_BODY_START) != 1:
        print(f"ABORT -- expected body-start block matched {text.count(OLD_BODY_START)} times, need 1", file=sys.stderr)
        sys.exit(1)
    if "generateMetadata" in text:
        print("ABORT -- page already has generateMetadata; this script assumes none exists", file=sys.stderr)
        sys.exit(1)

    new_text = text.replace(OLD_IMPORTS, NEW_IMPORTS, 1)
    # Insert the new function right after the imports/VALID_TYPES block,
    # before the Props interface.
    anchor = 'interface Props {'
    if new_text.count(anchor) != 1:
        print(f"ABORT -- anchor 'interface Props {{' matched {new_text.count(anchor)} times, need 1", file=sys.stderr)
        sys.exit(1)
    new_text = new_text.replace(anchor, JSONLD_FUNCTION.strip("\n") + "\n\n" + anchor, 1)
    new_text = new_text.replace(OLD_BODY_START, NEW_BODY_START, 1)

    print("=" * 100)
    print("EDIT -- app/book/[type]/[slug]/page.tsx")
    print("=" * 100)
    print("1. Imports: add type BookPiece + PUBLIC_DIMENSION_LABELS import")
    print("-" * 100)
    print("BEFORE:")
    print(OLD_IMPORTS)
    print("AFTER:")
    print(NEW_IMPORTS)
    print("-" * 100)
    print("2. New function inserted before `interface Props {`:")
    print(JSONLD_FUNCTION)
    print("-" * 100)
    print("3. Page body: add <script type=\"application/ld+json\"> as first child of <main>")
    print("BEFORE:")
    print(OLD_BODY_START)
    print("AFTER:")
    print(NEW_BODY_START)

    print("\n" + "=" * 100)
    print("SAMPLE JSON-LD OUTPUT (computed from live manifest data, 3 cases)")
    print("=" * 100)
    for piece_id, label in [
        ("FTA-18", "primaryDimension SET (aptitude)"),
        ("LIB-021", "permanently-exempt, no primaryDimension"),
        ("LIB-014", "secondaryDimensions only, no primaryDimension"),
    ]:
        sample = build_sample_jsonld(piece_id)
        print(f"\n--- {piece_id} ({label}) ---")
        print(json.dumps(sample, indent=2))

    print("\n" + "=" * 100)
    print("Confirm: no generateMetadata exists on this page (nothing altered there):", "generateMetadata" not in text)

    if args.dry_run:
        print("\nDRY RUN -- no file written.")
        return

    PAGE_FILE.write_text(new_text, encoding="utf-8")
    print(f"\nWROTE {PAGE_FILE.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
