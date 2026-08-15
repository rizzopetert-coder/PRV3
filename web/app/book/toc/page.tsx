"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { BOOK_STATE_INDEX, type StateDimension, type BookStateEntry } from "@/lib/book-state-index";
import { stateIdToSlug } from "@/lib/state-slug";
import { states as taxonomyStates, signatures } from "@/data/taxonomy";
import { bookManifest } from "@/lib/book-manifest";
import { translateResolutionFamily } from "@/lib/resolution-family";

// Filterable grid, replacing the prior dimension-grouped flat list.
// Two independent tag families -- dimension (4, from book-state-index.ts)
// and signature (5, from taxonomy.ts's signatures export) -- combine OR
// within a family, AND across families, per the approved concept
// (prompts/book-toc-fuller-vision.md) and Phase 2 Gemini clearance
// (prompts/book-toc-gemini-review-phase2.md). Content (name,
// descriptive_prose) stays a verbatim mirror of engine/data/states.py --
// see web/lib/book-state-index.ts's own header for the sync discipline.

const DIMENSION_ORDER: StateDimension[] = ["aptitude", "authority", "alliance", "attitude"];

// Raw engine resolution_family key -> /about/services anchor id. Keys match
// web/lib/resolution-family.ts's ENGINE_TO_COMMERCIAL_NAME exactly; anchors
// match the ids added to web/app/about/services/page.tsx this session.
const RESOLUTION_FAMILY_ANCHORS: Record<string, string> = {
  Roadmap: "people-tactics-and-strategy",
  Development: "training-development",
  Intervention: "intervention",
  "Executive Counsel": "executive-advisory",
};

// Per-state signature membership, joined by id from taxonomy.ts's states
// array (not present on BookStateEntry itself). All 58 ids confirmed
// matching 1:1 between the two files this session (Phase 1).
const SIGNATURE_MEMBERSHIP: Record<string, string[]> = Object.fromEntries(
  taxonomyStates.map((s) => [s.id, [s.signatureId, ...(s.secondarySignatureIds ?? [])]])
);

// Published-piece linkage per state, computed once from bookManifest --
// same STATE_THRESHOLD=2 rule web/app/book/state/[stateSlug]/page.tsx uses
// to decide whether a state gets its own aggregation page, so a card's
// media link never points at a page that doesn't exist.
const STATE_THRESHOLD = 2;

interface MediaLink {
  href: string;
  label: string;
}

function computeMediaLinks(): Record<string, MediaLink> {
  const piecesByState = new Map<string, { href: string; title: string }[]>();
  for (const piece of bookManifest) {
    if (piece.status !== "published" || !piece.stateIds) continue;
    for (const stateId of piece.stateIds) {
      const list = piecesByState.get(stateId) ?? [];
      list.push({ href: `/book/${piece.contentType}/${piece.slug}`, title: piece.title });
      piecesByState.set(stateId, list);
    }
  }

  const links: Record<string, MediaLink> = {};
  for (const [stateId, pieces] of piecesByState) {
    if (pieces.length >= STATE_THRESHOLD) {
      links[stateId] = {
        href: `/book/state/${stateIdToSlug(stateId)}`,
        label: `${pieces.length} related pieces`,
      };
    } else {
      links[stateId] = { href: pieces[0].href, label: pieces[0].title };
    }
  }
  return links;
}

const MEDIA_LINKS = computeMediaLinks();

function ResolutionFamilyBadge({ resolutionFamily }: { resolutionFamily: string }) {
  const parts = resolutionFamily.split(" + ").map((p) => p.trim());
  return (
    <p className="font-ui text-xs text-gray-500">
      {parts.map((part, i) => {
        const anchor = RESOLUTION_FAMILY_ANCHORS[part];
        const label = translateResolutionFamily(part);
        return (
          <span key={part}>
            {i > 0 && " + "}
            {anchor ? (
              <Link href={`/about/services#${anchor}`} className="underline hover:text-charcoal">
                {label}
              </Link>
            ) : (
              label
            )}
          </span>
        );
      })}
    </p>
  );
}

function StateCard({ entry }: { entry: BookStateEntry }) {
  const memberships = SIGNATURE_MEMBERSHIP[entry.id] ?? [];
  const media = MEDIA_LINKS[entry.id];

  return (
    <div
      id={stateIdToSlug(entry.id)}
      className="rounded-xl border border-gray-200 bg-white p-5 flex flex-col gap-3"
    >
      <div className="flex flex-wrap gap-1.5">
        <span className="font-mono text-[10px] uppercase tracking-wide text-gray-400 border border-gray-200 rounded-full px-2 py-0.5">
          {entry.dimension}
        </span>
        {memberships.map((sigId) => {
          const sig = signatures.find((s) => s.id === sigId);
          if (!sig) return null;
          return (
            <span
              key={sigId}
              className="font-mono text-[10px] uppercase tracking-wide text-slate border border-slate rounded-full px-2 py-0.5"
            >
              {sig.name}
            </span>
          );
        })}
      </div>

      <h3 className="font-display text-lg text-charcoal">{entry.name}</h3>
      <p className="font-ui text-sm text-gray-500 leading-relaxed">{entry.descriptiveProse}</p>

      <ResolutionFamilyBadge resolutionFamily={entry.resolutionFamily} />

      {media && (
        <Link href={media.href} className="font-ui text-sm text-charcoal underline hover:no-underline">
          {media.label} →
        </Link>
      )}
    </div>
  );
}

export default function StatesTocPage() {
  const [dimensionFilters, setDimensionFilters] = useState<Set<StateDimension>>(new Set());
  const [signatureFilters, setSignatureFilters] = useState<Set<string>>(new Set());

  function toggleDimension(dim: StateDimension) {
    setDimensionFilters((prev) => {
      const next = new Set(prev);
      if (next.has(dim)) next.delete(dim);
      else next.add(dim);
      return next;
    });
  }

  function toggleSignature(sigId: string) {
    setSignatureFilters((prev) => {
      const next = new Set(prev);
      if (next.has(sigId)) next.delete(sigId);
      else next.add(sigId);
      return next;
    });
  }

  const filtered = useMemo(() => {
    return BOOK_STATE_INDEX.filter((entry) => {
      const dimMatch = dimensionFilters.size === 0 || dimensionFilters.has(entry.dimension);
      const memberships = SIGNATURE_MEMBERSHIP[entry.id] ?? [];
      const sigMatch =
        signatureFilters.size === 0 || memberships.some((id) => signatureFilters.has(id));
      return dimMatch && sigMatch;
    });
  }, [dimensionFilters, signatureFilters]);

  return (
    <main className="max-w-5xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-4">All States</h1>
      <p className="font-ui text-base text-gray-600 mb-10">
        The full set of organizational conditions the diagnostic identifies. Filter by dimension,
        by signature, or both.
      </p>

      <div className="mb-10 space-y-4">
        <div>
          <p className="font-mono text-[11px] uppercase tracking-wide text-gray-400 mb-2">
            Dimension
          </p>
          <div className="flex flex-wrap gap-2">
            {DIMENSION_ORDER.map((dim) => (
              <button
                key={dim}
                onClick={() => toggleDimension(dim)}
                aria-pressed={dimensionFilters.has(dim)}
                className={`font-mono text-xs uppercase tracking-wide rounded-full px-3 py-1 border transition-colors ${
                  dimensionFilters.has(dim)
                    ? "border-charcoal bg-charcoal text-paper"
                    : "border-gray-300 text-gray-600 hover:border-charcoal"
                }`}
              >
                {dim}
              </button>
            ))}
          </div>
        </div>

        <div>
          <p className="font-mono text-[11px] uppercase tracking-wide text-gray-400 mb-2">
            Signature
          </p>
          <div className="flex flex-wrap gap-2">
            {signatures.map((sig) => (
              <button
                key={sig.id}
                onClick={() => toggleSignature(sig.id)}
                aria-pressed={signatureFilters.has(sig.id)}
                className={`font-mono text-xs uppercase tracking-wide rounded-full px-3 py-1 border transition-colors ${
                  signatureFilters.has(sig.id)
                    ? "border-slate bg-slate text-paper"
                    : "border-gray-300 text-gray-600 hover:border-slate"
                }`}
              >
                {sig.name}
              </button>
            ))}
          </div>
        </div>

        {(dimensionFilters.size > 0 || signatureFilters.size > 0) && (
          <button
            onClick={() => {
              setDimensionFilters(new Set());
              setSignatureFilters(new Set());
            }}
            className="font-ui text-xs text-gray-500 hover:text-charcoal underline"
          >
            Clear filters
          </button>
        )}
      </div>

      <p className="font-ui text-sm text-gray-400 mb-6">
        {filtered.length} of {BOOK_STATE_INDEX.length} conditions
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {filtered.map((entry) => (
          <StateCard key={entry.id} entry={entry} />
        ))}
      </div>

      {filtered.length === 0 && (
        <p className="font-ui text-sm text-gray-500 mt-8">
          No conditions match the selected filters.
        </p>
      )}
    </main>
  );
}
