// PRV3 -- shared state_id <-> URL slug transform.
//
// Extracted from web/app/book/state/[stateSlug]/page.tsx (that page's
// own local copy is untouched, out of scope for this change -- this
// module exists so /book/toc and PrivateOutput.tsx's new secondary-
// state links use the identical transform rather than a third
// independent copy). Underscore-to-hyphen swap, reversible.

export function stateIdToSlug(id: string): string {
  return id.replace(/_/g, "-");
}

export function slugToStateId(slug: string): string {
  return slug.replace(/-/g, "_");
}
