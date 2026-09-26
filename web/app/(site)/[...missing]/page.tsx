import { notFound } from "next/navigation";

/**
 * Catch-all for URLs no real route matches, so they render
 * app/(site)/not-found.tsx (with PRV3 chrome) instead of the chrome-free
 * root not-found. Lowest-priority match: every real route, static or
 * dynamic, still wins. hr-dx.com never reaches it -- middleware.ts answers
 * every non-allowlisted path with a bare 404 before Next's router runs.
 */
export default function MissingPage() {
  notFound();
}
