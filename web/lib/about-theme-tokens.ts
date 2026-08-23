import type { ThemeName } from "@/components/ThemeSwitcher";

// Shared /about/* section-heading color per theme -- the LARGE/DECORATIVE-
// ONLY tier color locked for /about/services (commit bfc137b): Warm's
// dusk-blue, Dark's oxide (its only color in this tier), Neutral's taupe
// (Pete's pick among three same-tier candidates). Every /about/* page
// that gets wired into the theme system reuses this exact assignment --
// extending the decision to a new page means importing this, not
// re-deriving or duplicating the mapping.
export const ABOUT_HEADING_CLASS: Record<ThemeName, string> = {
  warm: "text-dusk-blue",
  dark: "text-oxide",
  neutral: "text-taupe",
};
