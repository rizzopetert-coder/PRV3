import Link from "next/link";

/**
 * (site) not-found -- renders inside app/(site)/layout.tsx, so it carries
 * the PRV3 chrome from there. Catches notFound() from any (site) page, plus
 * every unmatched principalresolution.com URL via the [...missing]
 * catch-all beside it. Never reachable on hr-dx.com (middleware.ts 404s
 * every non-allowlisted path first), and unlike the root not-found it is
 * not embedded in /diagnostic's payload -- /diagnostic sits outside (site).
 */
export default function SiteNotFound() {
  return (
    <main className="min-h-screen bg-paper px-6 py-10 md:px-10 md:py-14">
      <p className="text-sm text-gray-500 mb-4">
        This page could not be found.
      </p>
      <Link href="/" className="font-ui text-sm text-charcoal hover:underline">
        Back to the home page
      </Link>
    </main>
  );
}
