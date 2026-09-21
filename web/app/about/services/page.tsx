import type { Metadata } from "next";
import ServicesPageContent from "@/components/ServicesPageContent";

export const metadata: Metadata = {
  title: "Services | Principal Resolution",
};

// Section id attributes (added for /book/toc's resolution_family badge --
// see web/app/book/toc/page.tsx's RESOLUTION_FAMILY_ANCHORS, 97 real badge
// links). Originally plain kebab-case slugs of each commercial name AT THE
// TIME they were added: #people-tactics-and-strategy, #training-development,
// #intervention, #executive-advisory. A later commercial-name correction
// renamed the display names ("People Tactics and Strategy" -> "People
// Tactics & Strategy", "Intervention" -> "First Call") WITHOUT renaming
// these ids -- deliberate, Pete's explicit instruction: the ids are frozen,
// internal technical identifiers, invisible to users, and renaming them
// would require updating all 97 book/toc references for zero user-visible
// benefit. Do not "fix" these ids to match the current display names without
// also updating book/toc's own map in the same change.
//
// Content and theme-conditional styling live in ServicesPageContent.tsx
// (client component, Dark/Neutral pilot this session) -- split out
// because metadata exports require a Server Component, and this page
// now needs the live theme (useTheme(), /about/*-scoped ThemeSwitcher)
// to pick the right per-theme heading/tag color, which requires a
// Client Component.
export default function ServicesPage() {
  return <ServicesPageContent />;
}
