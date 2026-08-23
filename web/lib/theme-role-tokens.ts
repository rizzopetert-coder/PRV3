import type { ThemeName } from "@/components/ThemeSwitcher";

// Shared per-theme role colors, extended in this pass beyond /about/*
// (originally web/lib/about-theme-tokens.ts) to /ask and /book/*, per
// Pete's explicit sequencing: reuse the established role assignments,
// don't re-derive them per route.

// Section/page-heading color -- the LARGE/DECORATIVE-ONLY tier color
// locked for /about/services (commit bfc137b): Warm's dusk-blue, Dark's
// oxide (its only color in this tier), Neutral's taupe (Pete's pick
// among three same-tier candidates). Every route that gets wired into
// the theme system reuses this exact assignment -- extending the
// decision to a new route means importing this, not re-deriving or
// duplicating the mapping.
export const HEADING_ACCENT_CLASS: Record<ThemeName, string> = {
  warm: "text-dusk-blue",
  dark: "text-oxide",
  neutral: "text-taupe",
};

// Pop color (berry/fuchsia/plum), locked usage rule (prompts/visual-
// identity-v3-palette-expansion.md): exactly once per page, primary CTA
// only, button fill, no fallback role. First real application: /ask's
// "Get in touch" button, this pass. White text fails WCAG AA against
// Dark's fuchsia specifically (3.72:1, computed, not estimated) -- each
// theme's own pre-existing --cta-text token (already designed for
// filled-CTA-button text, Warm #E9E7E2/Dark #171512/Neutral #FFFFFF)
// clears 4.5:1 against all three pop colors (4.9-7.04), so CTA text
// should always pair with the shared `text-cta-text` class, never a
// hardcoded white.
export const POP_CLASS: Record<ThemeName, string> = {
  warm: "bg-berry",
  dark: "bg-fuchsia",
  neutral: "bg-plum",
};
