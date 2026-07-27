"""
PRV3 -- /book Content Architecture Phase 2, Step 4
DimensionKey dedup + three new nav routes (dimension / state / pillar),
built as static-segment siblings to the existing app/book/[type]/[slug]
dynamic segment.

Verified against the actually-installed Next.js 16.2.9 App Router docs
(node_modules/next/dist/docs) before writing, per standing instruction
not to assume training-data conventions:
  - `params` is a Promise, awaited inside the page body -- matches the
    existing app/book/[type]/[slug]/page.tsx convention exactly, so
    these new routes follow the same plain `interface Props` shape
    rather than the newer PageProps<'/route'> typed-route helper this
    version also offers (existing codebase doesn't use that helper;
    matching existing convention, not introducing a second style).
  - No Cache Components flag in next.config.ts -- generateStaticParams
    returning an empty array (relevant if a route's qualifying set were
    ever empty) is valid here, not a build error.
  - Static path segments (literal folder names like "dimension",
    "state", "pillar") take precedence over a sibling dynamic segment
    ([type]) at the same directory level -- this is long-standing App
    Router routing precedence, not something version-specific, and
    nothing in the installed docs contradicts it. No naming collision
    exists between "dimension"/"state"/"pillar" and anything [type]
    would need to match.

Route logic:
  - dimension/[dimensionSlug]: one page per DimensionKey (4 total,
    always generated -- PUBLIC_DIMENSION_LABELS is a fixed 4-entry
    Record). Lists published pieces with matching primaryDimension.
  - pillar/[pillarSlug]: one page per contentPillar value (5 total,
    always generated). Lists published pieces with matching
    contentPillar.
  - state/[stateSlug]: THRESHOLD-GATED. generateStaticParams computes,
    from live bookManifest data, which state ids are referenced by
    >=2 published pieces via stateIds, and returns ONLY those as
    static params -- non-qualifying states are omitted at the
    generateStaticParams level, not filtered by a runtime check. A
    notFound() safety net still exists in the page body for direct
    requests to a non-generated stateSlug, mirroring the existing
    [type]/[slug]/page.tsx's own defensive pattern (build-time
    generateStaticParams filtering + runtime notFound() as a fallback,
    not either/or) -- default dynamicParams behavior means Next will
    still invoke the page function for an unlisted param at runtime,
    so this fallback is necessary, not decorative.

Also folds in the DimensionKey dedup: book-taxonomy-labels.ts now
imports DimensionKey from book-manifest.ts (the older/root declaration)
instead of redeclaring it.

Usage:
  python tools/patch_book_step4_routes.py --dry-run
  python tools/patch_book_step4_routes.py --write
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_ROOT = REPO_ROOT / "web"
MANIFEST_FILE = WEB_ROOT / "lib" / "book-manifest.ts"
LABELS_FILE = WEB_ROOT / "lib" / "book-taxonomy-labels.ts"

DIMENSION_PAGE = WEB_ROOT / "app" / "book" / "dimension" / "[dimensionSlug]" / "page.tsx"
STATE_PAGE = WEB_ROOT / "app" / "book" / "state" / "[stateSlug]" / "page.tsx"
PILLAR_PAGE = WEB_ROOT / "app" / "book" / "pillar" / "[pillarSlug]" / "page.tsx"

# --- Edit 1: DimensionKey dedup ---------------------------------------------

OLD_LABELS = '''export type DimensionKey = "aptitude" | "authority" | "alliance" | "attitude";

export const PUBLIC_DIMENSION_LABELS: Record<DimensionKey, { title: string; description: string }> = {'''

NEW_LABELS = '''import type { DimensionKey } from "./book-manifest";

export const PUBLIC_DIMENSION_LABELS: Record<DimensionKey, { title: string; description: string }> = {'''

# --- New file 1: dimension pillar page --------------------------------------

DIMENSION_PAGE_CONTENT = '''import { notFound } from "next/navigation";
import Link from "next/link";
import { bookManifest, type DimensionKey } from "@/lib/book-manifest";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";

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

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-4">{label.title}</h1>
      <p className="font-ui text-base text-gray-600 mb-12">{label.description}</p>
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
'''

# --- New file 2: pillar page -------------------------------------------------

PILLAR_PAGE_CONTENT = '''import { notFound } from "next/navigation";
import Link from "next/link";
import { bookManifest, type BookPiece } from "@/lib/book-manifest";

type ContentPillar = NonNullable<BookPiece["contentPillar"]>;

const PILLARS: ContentPillar[] = ["Reframe", "Pattern Named", "Case Composited", "Underneath", "Foundation"];

function slugifyPillar(pillar: string): string {
  return pillar.toLowerCase().replace(/\\s+/g, "-");
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
'''

# --- New file 3: state page (threshold-gated) -------------------------------

STATE_PAGE_CONTENT = '''import { notFound } from "next/navigation";
import Link from "next/link";
import { bookManifest } from "@/lib/book-manifest";
import { states } from "@/data/taxonomy";

const STATE_THRESHOLD = 2;

function stateIdToSlug(id: string): string {
  return id.replace(/_/g, "-");
}

function slugToStateId(slug: string): string {
  return slug.replace(/-/g, "_");
}

function computeQualifyingStateIds(): Set<string> {
  const counts = new Map<string, number>();
  for (const piece of bookManifest) {
    if (piece.status !== "published" || !piece.stateIds) continue;
    for (const stateId of piece.stateIds) {
      counts.set(stateId, (counts.get(stateId) ?? 0) + 1);
    }
  }
  const qualifying = new Set<string>();
  for (const [stateId, count] of counts) {
    if (count >= STATE_THRESHOLD) qualifying.add(stateId);
  }
  return qualifying;
}

// Computed once at module load -- bookManifest is static data, not
// runtime-dependent, so this is safe to share between
// generateStaticParams and the page body without recomputing per request.
const QUALIFYING_STATE_IDS = computeQualifyingStateIds();

interface Props {
  params: Promise<{ stateSlug: string }>;
}

export function generateStaticParams() {
  // Threshold gating happens here, by omission -- states below
  // STATE_THRESHOLD simply never appear in this returned array, so
  // Next.js never statically generates a page for them.
  return Array.from(QUALIFYING_STATE_IDS).map((stateId) => ({
    stateSlug: stateIdToSlug(stateId),
  }));
}

export default async function StatePage({ params }: Props) {
  const { stateSlug } = await params;
  const stateId = slugToStateId(stateSlug);

  // Defensive fallback for a direct request to a non-generated
  // stateSlug (Next's default dynamicParams behavior still invokes
  // this page function for unlisted params) -- mirrors the existing
  // app/book/[type]/[slug]/page.tsx's own notFound() pattern, not a
  // second gating mechanism competing with generateStaticParams above.
  if (!QUALIFYING_STATE_IDS.has(stateId)) {
    notFound();
  }

  const state = states.find((s) => s.id === stateId);
  if (!state) notFound();

  const pieces = bookManifest.filter(
    (p) => p.status === "published" && p.stateIds?.includes(stateId)
  );

  return (
    <main className="max-w-3xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-12">{state.name}</h1>
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
    </main>
  );
}
'''

NEW_FILES = [
    (DIMENSION_PAGE, DIMENSION_PAGE_CONTENT),
    (PILLAR_PAGE, PILLAR_PAGE_CONTENT),
    (STATE_PAGE, STATE_PAGE_CONTENT),
]


def compute_sample_params() -> None:
    """Mirrors each route's real generateStaticParams logic against live
    manifest/taxonomy data, so the output can be checked before it's
    trusted at scale -- not hardcoded expectations."""
    manifest_text = MANIFEST_FILE.read_text(encoding="utf-8")
    blocks = re.findall(r'\{\s*id: "[^"]+".*?\n  \},', manifest_text, re.DOTALL)

    dims = set()
    pillars = set()
    state_counts: dict[str, int] = {}
    for b in blocks:
        status_m = re.search(r'status: "([^"]+)"', b)
        if not status_m or status_m.group(1) != "published":
            continue
        dim_m = re.search(r'primaryDimension: "([^"]+)"', b)
        if dim_m:
            dims.add(dim_m.group(1))
        pillar_m = re.search(r'contentPillar: "([^"]+)"', b)
        if pillar_m:
            pillars.add(pillar_m.group(1))
        sids_m = re.search(r'stateIds: \[(.*?)\]', b)
        if sids_m:
            for sid in re.findall(r'"([^"]+)"', sids_m.group(1)):
                state_counts[sid] = state_counts.get(sid, 0) + 1

    qualifying_states = sorted(s for s, c in state_counts.items() if c >= 2)

    print("SAMPLE generateStaticParams OUTPUT (computed from live data):")
    print(f"  dimension route -- always all 4: {sorted(['aptitude', 'authority', 'alliance', 'attitude'])}")
    print(f"    -> sample single entry: {{ dimensionSlug: 'aptitude' }}")
    print(f"  pillar route -- always all 5 fixed values")
    print(f"    -> sample single entry: {{ pillarSlug: 'reframe' }}  (from 'Reframe')")
    print(f"  state route -- threshold-gated, >=2 published pieces via stateIds")
    print(f"    -> qualifying state ids found: {qualifying_states}")
    if qualifying_states:
        sample = qualifying_states[0]
        print(f"    -> sample single entry: {{ stateSlug: '{sample.replace('_', '-')}' }}  (from '{sample}', count={state_counts[sample]})")
    non_qualifying_examples = sorted(s for s, c in state_counts.items() if c < 2)[:3]
    print(f"    -> non-qualifying (count=1) examples, correctly OMITTED: {non_qualifying_examples}")


def main() -> None:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--dry-run", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()

    labels_text = LABELS_FILE.read_text(encoding="utf-8")
    if labels_text.count(OLD_LABELS) != 1:
        print(f"ABORT -- expected book-taxonomy-labels.ts content matched {labels_text.count(OLD_LABELS)} times, need 1", file=sys.stderr)
        sys.exit(1)
    new_labels_text = labels_text.replace(OLD_LABELS, NEW_LABELS, 1)

    for path, _ in NEW_FILES:
        if path.exists():
            print(f"ABORT -- {path.relative_to(REPO_ROOT)} already exists", file=sys.stderr)
            sys.exit(1)

    print("=" * 100)
    print("EDIT -- DimensionKey dedup (web/lib/book-taxonomy-labels.ts)")
    print("=" * 100)
    print("BEFORE:")
    print(OLD_LABELS)
    print("-" * 100)
    print("AFTER:")
    print(NEW_LABELS)

    print("\n" + "=" * 100)
    print("NEW FILES")
    print("=" * 100)
    for path, content in NEW_FILES:
        print(f"\n--- {path.relative_to(REPO_ROOT)} ---")
        print(content)

    print("=" * 100)
    compute_sample_params()
    print("=" * 100)

    if args.dry_run:
        print("\nDRY RUN -- no files written.")
        return

    LABELS_FILE.write_text(new_labels_text, encoding="utf-8")
    print(f"\nWROTE {LABELS_FILE.relative_to(REPO_ROOT)}")
    for path, content in NEW_FILES:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        print(f"WROTE {path.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
