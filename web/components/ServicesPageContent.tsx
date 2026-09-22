"use client";

import Link from "next/link";
import { useTheme } from "@/components/ThemeSwitcher";
import { HEADING_ACCENT_CLASS } from "@/lib/theme-role-tokens";

// Brief overview/index (this session) -- replaces the four full service
// descriptions this page used to hold with one-line summaries linking out
// to the four landing pages. Display names and routes both match
// engine/resolution_families.py's commercial names (this session's
// unification decision): People Tactics & Strategy, Training & Development,
// First Call, Executive Advisory.
//
// Anchor ids are UNCHANGED from the old section ids on purpose -- kept
// deliberately decoupled from both the display name AND the route slug
// above: web/app/book/toc/page.tsx links 97 state badges to /about/
// services#people-tactics-and-strategy, #training-development,
// #intervention, and #executive-advisory (RESOLUTION_FAMILY_ANCHORS,
// confirmed live before this edit). Keeping the same four ids means those
// existing deep-links still land on the right summary rather than
// silently going nowhere. Do not rename these ids without also updating
// book/toc/page.tsx's RESOLUTION_FAMILY_ANCHORS.
//
// Heading color logic (HEADING_ACCENT_CLASS, useTheme()) kept unchanged
// from the prior version -- same per-theme WCAG AA verification already
// done for this page, not re-derived here.

const OVERVIEW_ITEMS = [
  {
    id: "people-tactics-and-strategy",
    name: "People Tactics & Strategy",
    teaser:
      "We find the organizational conditions producing your problems and resolve them at the structure, not just the symptom.",
    href: "/people-tactics-and-strategy",
  },
  {
    id: "training-development",
    name: "Training & Development",
    teaser:
      "Training built around what your people actually need: we coach individuals, run group sessions, or work co-led with your own leaders.",
    href: "/training-and-development",
  },
  {
    id: "intervention",
    name: "First Call",
    teaser:
      "Something happened today, and you need someone who has handled it before. Reach out. You will hear back the same day.",
    href: "/first-call",
  },
  {
    id: "executive-advisory",
    name: "Executive Advisory",
    teaser:
      "A standing relationship, built over time. When the hardest decisions arrive, you have someone who already understands your organization instead of starting from scratch.",
    href: "/executive-advisory",
  },
];

export default function ServicesPageContent() {
  const theme = useTheme();
  const heading = `font-display text-2xl md:text-3xl ${HEADING_ACCENT_CLASS[theme]} mb-3`;

  return (
    <main className="bg-background min-h-screen">
      <div className="max-w-3xl mx-auto px-6 py-16 md:py-24">

        <p className="font-ui text-base text-oxide-text leading-relaxed mb-12">
          The diagnostic finds the condition. These are the four ways the work actually gets done. Most engagements use one. Some conditions call for two working together.
        </p>

        <div className="divide-y divide-gray-100">
          {OVERVIEW_ITEMS.map((item) => (
            <section key={item.id} id={item.id} className="py-10 first:pt-0 last:pb-0">
              <h2 className={heading}>{item.name}</h2>
              <p className="font-ui text-base text-oxide-text leading-relaxed mb-4">
                {item.teaser}
              </p>
              <Link
                href={item.href}
                className="font-ui text-sm font-medium text-oxide-text underline hover:opacity-90 transition-opacity"
              >
                Learn more →
              </Link>
            </section>
          ))}
        </div>

        <p className="font-ui text-sm text-gray-400 leading-relaxed mt-12">
          Most engagements use one of these. Some diagnosed conditions call for two working together. That combination gets recommended directly, not guessed at from a menu.
        </p>

      </div>
    </main>
  );
}
