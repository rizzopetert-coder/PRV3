"use client";

import type { ReactNode } from "react";
import dynamic from "next/dynamic";
import { useBrand } from "@/components/BrandContext";

// PRV3 site chrome for /diagnostic on principal_resolution only.
// Code-split via next/dynamic from THIS client component: a static import
// (or next/dynamic from the server layout, which Next does not split) puts
// the chrome chunk -- PR service tier names, nav labels -- into what
// hr-dx.com's /diagnostic downloads even though it never renders there.
const SiteChrome = dynamic(() =>
  import("@/components/SiteChrome").then((m) => m.SiteChrome),
);

export default function DiagnosticChrome({ children }: { children: ReactNode }) {
  const brand = useBrand();
  if (brand === "principal_resolution") {
    return <SiteChrome>{children}</SiteChrome>;
  }
  return <>{children}</>;
}
