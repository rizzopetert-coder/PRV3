import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/services", destination: "/about/services" },
      // Phase 3 (multi-project migration) -- proxies the 8 Python engine
      // routes to Project B (separate Vercel project, api/engine.py's
      // FastAPI app), since this project's Root Directory is now "web"
      // and no longer has any vercel.json routing in scope. ENGINE_BASE_URL
      // is Project B's own deployment URL (auto-generated for now, the
      // engine.principalresolution.com subdomain comes later per the
      // phased plan -- not wired yet, deliberately, to avoid stacking two
      // domain changes at once).
      {
        source: "/api/:path(engine|accumulate|checkpoint|complete|condensed-complete|question-copy|narrative-prompt|narrative-process)",
        destination: `${process.env.ENGINE_BASE_URL}/api/:path`,
      },
    ];
  },
};

export default nextConfig;
