"use client";

import { useTheme, type ThemeName } from "@/components/ThemeSwitcher";
import { HEADING_ACCENT_CLASS } from "@/lib/theme-role-tokens";

// Dark/Neutral pilot (this session), same tier discipline as Warm's
// original pilot (commit 76815a7) -- see prompts/visual-identity-v3-
// palette-expansion.md for each theme's tier table. Body copy stays a
// single static class: oxide-text is the one role name shared across
// all three themes' own [data-theme] blocks, so it re-colors correctly
// via the CSS cascade alone, no conditional needed. Headings and tags
// use theme-specific token names (Warm's dusk-blue/umber, Dark's
// oxide/warm-gray, Neutral's taupe/oxide) that only exist under their
// own theme's scope, so picking the right one requires knowing the live
// theme -- hence useTheme() and this file being a client component.
//
// Role -> tier mapping, re-derived per theme (not copied from Warm):
//   Dark: oxide-text is the documented "any text role" choice (its own
//     tier table's explicit rule), so body reuses it; oxide is Dark's
//     only LARGE/DECORATIVE-ONLY color, so headings use it by necessity,
//     not choice; warm-gray is Pete's pick among four equally-valid
//     TEXT-SAFE candidates for tags (amber/sage/warm-gray/dusty-blue).
//   Neutral (tiers taken against paper, since this page uses bg-paper,
//     not --field -- three of Neutral's seven colors change tier
//     between the two): taupe is Pete's pick among three equally-valid
//     LARGE/DECORATIVE-ONLY candidates (taupe/sage-gray/cool-gray) for
//     headings; oxide is the only remaining TEXT-SAFE non-CTA color left
//     for tags once oxide-text is spoken for by body copy (plum is
//     CTA-exclusive, excluded the same way Warm left berry unused).
//
// Heading color now lives in web/lib/theme-role-tokens.ts, shared with
// /about/story and /about/method -- this was the first page to define
// it, not the only owner of the decision.
const TAG_CLASS: Record<ThemeName, string> = {
  warm: "text-umber",
  dark: "text-warm-gray",
  neutral: "text-oxide",
};

export default function ServicesPageContent() {
  const theme = useTheme();
  const heading = `font-display text-2xl md:text-3xl ${HEADING_ACCENT_CLASS[theme]} mb-3`;
  const tag = `font-ui text-sm ${TAG_CLASS[theme]} italic mb-6`;

  return (
    <main className="bg-paper min-h-screen">
      <div className="max-w-3xl mx-auto px-6 py-16 md:py-24">

        <p className="font-ui text-base text-oxide-text leading-relaxed mb-12">
          The diagnostic finds the condition. These are the four ways the work actually gets done. Most engagements use one. Some conditions call for two working together.
        </p>

        <div className="divide-y divide-gray-100">

          <section id="people-tactics-and-strategy" className="pb-12">
            <h2 className={heading}>People Tactics and Strategy</h2>
            <p className={tag}>Org assessment, people strategy, and the tactical HR work required to act on it. Not just structure on paper — the actual decisions about how people are organized, managed, and supported, and the hands-on work to make those decisions real.</p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              Some problems live in how the organization is built, not in the people inside it. People Tactics and Strategy starts with an honest look at your structure, your roles, and your people decisions, then does the tactical work to fix what&apos;s not working. Org charts that don&apos;t match how work actually happens. Roles with no clear owner. Decisions that get made twice because nobody agreed who makes them the first time.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              This isn&apos;t a slide deck handed to your team to implement on their own. It&apos;s assessment, strategy, and the on-the-ground work to carry it out.
            </p>
          </section>

          <section id="training-development" className="py-12">
            <h2 className={heading}>Training &amp; Development</h2>
            <p className={tag}>Leadership development, team coaching, and teambuilding, built around what your people actually need rather than a packaged program.</p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              Training &amp; Development covers what most firms split into four different vendors: leadership development, coaching, teambuilding, and skills training. Here it&apos;s one service, built around the specific gap the diagnostic found, not a course catalog.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              A leader who needs to give harder feedback gets coaching, not a seminar. A team that&apos;s stopped trusting each other gets teambuilding that actually changes how they work together afterward, not a retreat with a trust fall and a debrief. Whatever the gap, the work is built to close it, not just to have happened.
            </p>
          </section>

          <section id="intervention" className="py-12">
            <h2 className={heading}>Intervention</h2>
            <p className={tag}>Immediate, in-the-room expertise for a situation that&apos;s live right now.</p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              Some situations can&apos;t wait for a plan. Intervention means someone in the room, with the standing and the expertise to move a live situation, for as long as it takes to resolve.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              This isn&apos;t advice from the outside. It&apos;s direct, immersive engagement inside the situation, while there&apos;s still room to shape how it ends.
            </p>
          </section>

          <section id="executive-advisory" className="pt-12">
            <h2 className={heading}>Executive Advisory</h2>
            <p className={tag}>A confidential, ongoing relationship for the decisions that can&apos;t be discussed with anyone inside the organization.</p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              Yes, it&apos;s what it sounds like. Executive Advisory is a standing, confidential relationship with someone who has no stake in the outcome except getting it right. Available before you need it urgently, and especially valuable once you do.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              The honest read on your own situation gets harder to find the longer you&apos;re inside it. This is that read, without the politics attached to every word inside the building.
            </p>
          </section>

        </div>

        <p className="font-ui text-sm text-gray-400 leading-relaxed mt-12">
          Most engagements use one of these. Some diagnosed conditions call for two working together. That combination gets recommended directly, not guessed at from a menu.
        </p>

      </div>
    </main>
  );
}
