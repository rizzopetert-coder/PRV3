import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [
      { source: "/services", destination: "/about/services" },
    ];
  },
};

export default nextConfig;
