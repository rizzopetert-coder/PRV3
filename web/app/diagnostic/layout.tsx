import type { Metadata } from "next";
import { headers } from "next/headers";
import { BRAND_HEADER, resolveBrandForRequest, type Brand } from "@/lib/brand";
import { BrandProvider } from "@/components/BrandContext";

/**
 * Brand-aware metadata and BrandProvider scoped to the /diagnostic route
 * segment only (supersedes the root-layout approach from the prior pass,
 * which forced the whole site into dynamic rendering -- confirmed via a
 * real build, every one of 36 routes flipped Static -> Dynamic). /diagnostic
 * was already client-rendered/stateful and never a static route to begin
 * with, so scoping brand detection here costs nothing additional -- the
 * rest of the site keeps its existing static generation unchanged.
 */
async function resolveRequestBrand(): Promise<Brand> {
  const headersList = await headers();
  const forwarded = headersList.get(BRAND_HEADER);
  if (forwarded === "hr_diagnostic" || forwarded === "principal_resolution") {
    return forwarded;
  }
  // Defensive fallback if middleware's header is ever absent -- also
  // covers the debug override consistently, not just the plain Host path.
  return resolveBrandForRequest(headersList);
}

export async function generateMetadata(): Promise<Metadata> {
  const brand = await resolveRequestBrand();
  if (brand === "hr_diagnostic") {
    return {
      title: "HR Diagnostic",
      description: "Organizational diagnostic",
      // Placeholder -- Pete to supply final favicon/OG assets separately.
      icons: { icon: "/favicon.ico" },
    };
  }
  return {
    title: "Principal Resolution",
    description: "Organizational diagnostic",
  };
}

export default async function DiagnosticLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const brand = await resolveRequestBrand();
  return <BrandProvider brand={brand}>{children}</BrandProvider>;
}
