"use client";

import Link from "next/link";
import { useTheme } from "@/components/ThemeSwitcher";
import { HEADING_ACCENT_CLASS, POP_CLASS } from "@/lib/theme-role-tokens";

// Dark/Neutral rollout, Gemini-cleared batch (this session, gated on
// Task 1's claim verification). h1 -> heading accent (Pete's call,
// extending the role beyond section headings to page titles). Body ->
// oxide-text. "Get in touch" -> first real application of the locked
// pop-color rule (Pete's explicit call): background fill only, exactly
// once on this page, paired with each theme's own --cta-text (not a
// hardcoded white -- computed contrast, not estimated: white fails WCAG
// AA against Dark's fuchsia specifically, 3.72:1; each theme's
// --cta-text clears 4.5:1 against its own pop color, 4.9-7.04).
export default function AskPage() {
  const theme = useTheme();

  return (
    <main className="max-w-2xl mx-auto px-6 py-16">
      <h1 className={`font-display text-3xl ${HEADING_ACCENT_CLASS[theme]} mb-4`}>Just Ask.</h1>
      <p className="font-ui text-base text-oxide-text mb-8">
        If you already know what you&apos;re dealing with, start a conversation
        directly.
      </p>
      <Link
        href="mailto:pete@principalresolution.com"
        className={`inline-block ${POP_CLASS[theme]} text-cta-text font-ui text-sm font-medium px-6 py-3 hover:opacity-90 transition-opacity`}
      >
        Get in touch →
      </Link>
    </main>
  );
}
