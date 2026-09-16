// PRV3 — Contact constants and mailto helper
// web/lib/contact.ts
//
// Single source for the contact address and the mailto-link encoding
// convention, shared by web/app/ask/page.tsx and (once wired)
// web/app/diagnostic/page.tsx's Phase 4 "Start a conversation" CTA --
// previously pete@principalresolution.com was a single inline string in
// ask/page.tsx with no reusable export; this replaces that with one
// definition so a second consumer doesn't hardcode a second instance.

export const CONTACT_EMAIL = "pete@principalresolution.com";

// encodeURIComponent handles \n as %0A, the correct mailto line-break
// encoding -- no separate newline handling needed.
export function buildMailtoLink(subject: string, body: string): string {
  return `mailto:${CONTACT_EMAIL}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}
