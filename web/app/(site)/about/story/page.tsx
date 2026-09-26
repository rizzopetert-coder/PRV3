import type { Metadata } from "next";
import StoryPageContent from "@/components/StoryPageContent";

export const metadata: Metadata = {
  title: "Our Story | Principal Resolution",
};

// Content and theme-conditional heading color live in
// StoryPageContent.tsx (client component, Dark/Neutral rollout this
// session) -- split out because metadata exports require a Server
// Component, and this page now needs the live theme (useTheme(),
// /about/*-scoped ThemeSwitcher) to pick the right per-theme heading
// color, which requires a Client Component. Same pattern as
// /about/services (commit bfc137b).
export default function StoryPage() {
  return <StoryPageContent />;
}
