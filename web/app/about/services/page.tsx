import type { Metadata } from "next";
import ServicesPageContent from "@/components/ServicesPageContent";

export const metadata: Metadata = {
  title: "Services | Principal Resolution",
};

// Section id attributes (added for /book/toc's planned resolution_family
// badge, this session) -- plain kebab-case slugs of each real commercial
// name, matching web/lib/resolution-family.ts's ENGINE_TO_COMMERCIAL_NAME
// output exactly: "People Tactics and Strategy" -> #people-tactics-and-
// strategy, "Training & Development" -> #training-development,
// "Intervention" -> #intervention, "Executive Advisory" -> #executive-
// advisory. No shared slugify utility used -- only 4 fixed values, hand-
// matched here; whoever builds the badge should link directly to these
// exact anchors rather than deriving a slug from the commercial name at
// runtime, since "Training & Development"'s real anchor drops the
// ampersand rather than encoding it.
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
