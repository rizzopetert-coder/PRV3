import { SiteChrome } from "@/components/SiteChrome";

/**
 * PRV3 site chrome scoped to the (site) route group. Moved out of the root
 * layout so app/diagnostic/ (a sibling of this group, not a child) only
 * gets it where its own layout opts in -- principal_resolution only, never
 * hr-dx.com. "(site)" is a route group, not a URL segment -- every route
 * under it keeps its exact existing path.
 */
export default function SiteLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <SiteChrome>{children}</SiteChrome>;
}
