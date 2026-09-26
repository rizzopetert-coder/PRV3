"use client";

import { stateIdToSlug } from "@/lib/state-slug";

// principal_resolution-only: co-occurring condition name linking into
// /book/toc. Loaded via next/dynamic from PrivateOutput.tsx only when
// brand is principal_resolution -- /book is walled off on hr-dx.com, and
// the route string itself must not ship there either.
export default function StateBookLinkPR({ id, name }: { id: string; name: string }) {
  return (
    <a
      href={`/book/toc#${stateIdToSlug(id)}`}
      className="font-display text-lg text-charcoal hover:underline"
    >
      {name}
    </a>
  );
}
