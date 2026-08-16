"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { Drawer } from "vaul";
import { BOOK_STATE_INDEX, type StateDimension, type BookStateEntry } from "@/lib/book-state-index";
import { stateIdToSlug } from "@/lib/state-slug";
import { states as taxonomyStates, signatures } from "@/data/taxonomy";
import { bookManifest } from "@/lib/book-manifest";
import { translateResolutionFamily } from "@/lib/resolution-family";
import { PUBLIC_DIMENSION_LABELS } from "@/lib/book-taxonomy-labels";

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

// Gestalt Pass Layer 1 + 2 (this session) -- copy is DRAFT, swappable
// before final commit, not P-10 locked -- Pete's explicit call to build
// against it now rather than wait
// (prompts/book-toc-gestalt-pass-draft-copy.md is the source of record).
const LAYER1_ADDITION =
  "Each one is a real, calibrated pattern the diagnostic can identify — not a label invented for this page. The tags below are two different ways of grouping the same 58 conditions: which part of the organization a condition lives in, and which broader pattern it belongs to.";

const TERMS_GUIDE_TITLE = "Terminology Guide";
const TERMS_GUIDE_TRIGGER_TEXT = "What do these terms mean";

// Signatures have no existing locked copy source (unlike dimensions, which
// reuse PUBLIC_DIMENSION_LABELS verbatim at render time below, not
// duplicated here) -- this is genuinely first-pass content itself, keyed
// by the real signature id so a missing/renamed signature fails loudly
// rather than silently rendering blank.
const SIGNATURE_DEFINITIONS: Record<string, string> = {
  leadership_bottleneck:
    "Too much depends on too few people at the top. Decisions, institutional knowledge, and continuity all run through a small number of individuals, and the organization hasn't built a way to function without them.",
  culture_erosion:
    "What's said and what's rewarded have drifted apart. Standards, recognition, and accountability aren't applied the same way to everyone, and the gap between stated values and lived experience is wide enough that people have stopped trusting the stated version.",
  stunted_growth:
    "People and roles aren't developing the way the organization needs them to. Managers are undertrained, talent goes unused, and the gap between what a role requires and what the person in it is equipped for keeps widening instead of closing.",
  compounding_risks:
    "Individually survivable problems that are stacking on top of each other. No single one would sink the organization, but they're reinforcing each other in ways that make each one harder to see and harder to fix in isolation.",
  information_blindness:
    "The organization can't see its own real condition. What leadership hears and what's actually happening have diverged, and the mechanisms that would normally surface that gap aren't working.",
};

// Shared between the desktop panel and the mobile Drawer -- same two
// semantic sub-sections (h3 + dl/dt/dd, a real glossary structure, not a
// flat list), same content, different wrapper. Dimensions pulled verbatim
// from PUBLIC_DIMENSION_LABELS at render time, not reconstructed from any
// draft-copy placeholder text.
function TermsGuideContent() {
  return (
    <>
      <section aria-labelledby="terms-guide-dimensions">
        <h3
          id="terms-guide-dimensions"
          className="font-ui text-[11px] font-semibold uppercase tracking-wide text-gray-400 mb-2"
        >
          Dimensions
        </h3>
        <dl className="space-y-2 mb-4">
          {DIMENSION_ORDER.map((dim) => (
            <div key={dim}>
              <dt className="font-ui text-xs font-semibold text-charcoal capitalize">{dim}</dt>
              <dd className="font-ui text-[11px] text-gray-500 leading-relaxed">
                {PUBLIC_DIMENSION_LABELS[dim].description}
              </dd>
            </div>
          ))}
        </dl>
      </section>
      <section aria-labelledby="terms-guide-signatures">
        <h3
          id="terms-guide-signatures"
          className="font-ui text-[11px] font-semibold uppercase tracking-wide text-gray-400 mb-2"
        >
          Signatures
        </h3>
        <dl className="space-y-2">
          {signatures.map((sig) => (
            <div key={sig.id}>
              <dt className="font-ui text-xs font-semibold text-charcoal">{sig.name}</dt>
              <dd className="font-ui text-[11px] text-gray-500 leading-relaxed">
                {SIGNATURE_DEFINITIONS[sig.id]}
              </dd>
            </div>
          ))}
        </dl>
      </section>
    </>
  );
}

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

  // Gestalt Pass Layer 2 (this session) -- same termsHovered/termsTapped
  // two-boolean split as Category E's addendum, same reasoning: a real
  // <button> fires a native synthetic click on Enter/Space, which would
  // open the Drawer.Root below (real body-scroll-lock) from keyboard
  // focus alone. preventDefault() on the button's onKeyDown suppresses
  // that native click, so only an actual pointer click sets termsTapped.
  const [termsHovered, setTermsHovered] = useState(false);
  const [termsTapped, setTermsTapped] = useState(false);

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
      <p className="font-ui text-base text-gray-600 mb-4">
        The full set of organizational conditions the diagnostic identifies. Filter by dimension,
        by signature, or both.
      </p>
      <p className="font-ui text-base text-gray-600 mb-4">{LAYER1_ADDITION}</p>

      {/* Gestalt Pass Layer 2 (this session) -- combined terminology
          guide. Trigger placed in normal document flow, after the intro
          copy above, before the filter-bar div (option (A), Gemini-
          cleared) -- DOM order alone gives it tab-first placement ahead
          of the filter chips, no tabIndex trick needed. The `relative`
          wrapper below exists only to anchor the desktop panel's absolute
          positioning to this specific trigger -- unlike the
          ConstellationField addendum's corner-math, this page has no
          fixed coordinate space to place against, so it's a plain local
          CSS anchor, not a page-level layout decision. Unlike the
          addendum's two decorative, pointer-events-none panels (short
          enough to never need scrolling), this panel holds 9 real entries
          and must be interactive/scrollable -- so pointer-events stay on,
          and the panel is positioned flush against the trigger (top-full,
          zero gap) rather than at a fixed pixel offset, so a mouse moving
          from the trigger into the panel never crosses a dead gap that
          would fire mouseleave and close it prematurely. */}
      <div className="relative inline-block mb-10">
        <button
          type="button"
          aria-label={TERMS_GUIDE_TRIGGER_TEXT}
          aria-expanded={termsHovered || termsTapped}
          className="font-ui text-sm text-gray-500 hover:text-charcoal transition-colors underline decoration-dotted underline-offset-2"
          onMouseEnter={() => setTermsHovered(true)}
          onFocus={() => setTermsHovered(true)}
          onBlur={() => setTermsHovered(false)}
          onClick={() => setTermsTapped((cur) => !cur)}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault();
              setTermsHovered((cur) => !cur);
            }
          }}
        >
          {TERMS_GUIDE_TRIGGER_TEXT}
        </button>

        {termsHovered && (
          <div
            className="hidden md:block absolute z-10 top-full left-0 w-80 max-h-96 overflow-y-auto rounded-md border border-gray-200 bg-white p-4 shadow-lg"
            onMouseLeave={() => setTermsHovered(false)}
          >
            <TermsGuideContent />
          </div>
        )}
      </div>

      {/* Mobile gestalt drawer (this session) -- independent Drawer.Root
          instance, separate from ConstellationField's, per the confirmed
          option (a)/(A) precedent. Opens only from an actual click/tap on
          the trigger above, never from hover or keyboard focus alone. */}
      <Drawer.Root open={termsTapped} onOpenChange={setTermsTapped}>
        <Drawer.Portal>
          <Drawer.Overlay className="fixed inset-0 bg-black/30 z-40 md:hidden" />
          <Drawer.Content className="fixed bottom-0 left-0 right-0 z-50 bg-white rounded-t-2xl max-h-[80vh] flex flex-col md:hidden">
            <Drawer.Title className="sr-only">{TERMS_GUIDE_TITLE}</Drawer.Title>
            <div className="w-10 h-1 bg-gray-300 rounded-full mx-auto mt-3 mb-2 shrink-0" />
            <div className="overflow-y-auto p-4 pb-8">
              <p className="font-ui text-sm font-semibold text-charcoal mb-3">{TERMS_GUIDE_TITLE}</p>
              <TermsGuideContent />
            </div>
          </Drawer.Content>
        </Drawer.Portal>
      </Drawer.Root>

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
