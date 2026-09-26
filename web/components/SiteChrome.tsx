import type { ReactNode } from "react";
import { NavBar } from "@/components/NavBar";
import { MobileMenu } from "@/components/MobileMenu";
import { ServiceSidebar } from "@/components/ServiceSidebar";

/**
 * PRV3 site chrome -- NavBar, MobileMenu, ServiceSidebar -- as one unit.
 * Rendered by app/(site)/layout.tsx, by app/diagnostic/layout.tsx for
 * principal_resolution only, and by app/not-found.tsx. Never rendered on
 * hr-dx.com: nothing on that brand's allowed surface reaches any of the
 * three call sites with chrome enabled.
 *
 * Fragment, no wrapper element, so the DOM under <body> matches the
 * pre-split root layout exactly.
 */
export function SiteChrome({ children }: { children: ReactNode }) {
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
          wiring itself, including its thin-strip variant on /diagnostic.
          See ServiceSidebar.tsx's own header comment. */}
      <ServiceSidebar>{children}</ServiceSidebar>
    </>
  );
}
