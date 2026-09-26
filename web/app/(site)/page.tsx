import { headers } from "next/headers";
import HomeClient from "@/components/home/HomeClient";

// Forces "/" to be dynamically rendered per-request (Cache-Control:
// private, no-cache, no-store -- never CDN-cached) so middleware.ts's
// Host-based rewrite (hr_diagnostic -> /diagnostic) is re-evaluated on
// every request. Without this, Vercel's CDN caches "/" once at the
// deployment level and serves the identical cached HTML to every domain
// attached to the deployment, bypassing middleware's per-Host decision
// entirely -- confirmed directly this session (byte-identical ETag
// between hr-dx.com/ and principalresolution.com/). headers()'s return
// value is unused -- calling it is what triggers dynamic rendering, the
// same mechanism already used in web/app/diagnostic/layout.tsx's
// resolveRequestBrand(). Scoped to this one leaf route only -- page.tsx
// has no descendants, so this does not cascade to any other route.
export default async function Home() {
  await headers();
  return <HomeClient />;
}
