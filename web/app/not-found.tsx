import Link from "next/link";

/**
 * Root not-found -- deliberately chrome-free and brand-neutral. Next embeds
 * the root not-found tree in EVERY route's RSC payload, hr-dx.com's
 * /diagnostic included, so any client component referenced here (NavBar,
 * ServiceSidebar...) would ship its JS chunk -- and every PRV3 service name
 * in it -- to hr-dx browsers even though nothing renders. principal
 * resolution.com's 404s with chrome come from app/(site)/not-found.tsx,
 * fed by the app/(site)/[...missing] catch-all.
 */
export default function NotFound() {
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
