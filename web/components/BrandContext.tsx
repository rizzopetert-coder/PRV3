"use client";

import { createContext, useContext, type ReactNode } from "react";
import type { Brand } from "@/lib/brand";

const BrandContext = createContext<Brand>("principal_resolution");

export function BrandProvider({
  brand,
  children,
}: {
  brand: Brand;
  children: ReactNode;
}) {
  return <BrandContext.Provider value={brand}>{children}</BrandContext.Provider>;
}

export function useBrand(): Brand {
  return useContext(BrandContext);
}
