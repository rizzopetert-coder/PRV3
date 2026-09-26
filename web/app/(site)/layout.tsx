import { NavBar } from "@/components/NavBar";
import { MobileMenu } from "@/components/MobileMenu";
import { ServiceSidebar } from "@/components/ServiceSidebar";

/**
 * PRV3 site chrome -- NavBar, MobileMenu, ServiceSidebar -- scoped to the
 * (site) route group only. Moved out of the root layout so app/diagnostic/
 * (a sibling of this group, not a child) never receives it: on hr-dx.com
 * none of this markup is sent at all, not rendered-then-hidden. "(site)"
 * is a route group, not a URL segment -- every route under it keeps its
 * exact existing path.
 *
 * Structure matches the previous root-layout <body> contents exactly
 * (fragment, no wrapper element), so the DOM under <body> is unchanged for
 * every route in this group.
 */
export default function SiteLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <>
      <NavBar />
      {/* Homepage restructure (2026-08-29) -- mounted as a sibling to
          NavBar, not inside it. NavBar.tsx is explicitly out of scope
          (Pete's instruction, 2026-08-29); MobileMenu is fully
          self-contained (own fixed trigger + overlay), so this is the
          only wiring point needed. */}
      <MobileMenu />
      {/* Persistent service sidebar -- ServiceSidebar owns the flex
          wiring itself. See ServiceSidebar.tsx's own header comment. */}
      <ServiceSidebar>{children}</ServiceSidebar>
    </>
  );
}
