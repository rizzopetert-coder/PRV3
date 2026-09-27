"use client";

import { stateIdToSlug } from "@/lib/state-slug";

// principal_resolution-only: co-occurring condition name linking into
// /book/toc. Loaded via next/dynamic from PrivateOutput.tsx only when
// brand is principal_resolution -- /book is walled off on hr-dx.com, and
// the route string itself must not ship there either.
export default function StateBookLinkPR({
  id,
  name,
  label,
}: {
  id: string;
  name: string;
  // Phase 2: a small secondary link (e.g. inside an expanded condition
  // card) instead of the large name link.
  label?: string;
}) {
  if (label) {
    return (
      <a
        href={`/book/toc#${stateIdToSlug(id)}`}
        aria-label={`${label}: ${name}`}
        className="font-ui text-[12px] text-slate hover:underline"
      >
        {label}
      </a>
    );
  }
  return (
    <a
      href={`/book/toc#${stateIdToSlug(id)}`}
      className="font-display text-lg text-charcoal hover:underline"
    >
      {name}
    </a>
  );
}
