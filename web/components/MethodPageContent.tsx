"use client";

import { useTheme } from "@/components/ThemeSwitcher";
import { ABOUT_HEADING_CLASS } from "@/lib/about-theme-tokens";

// Dark/Neutral rollout (this session), same pattern as
// StoryPageContent.tsx -- see that file's header comment and
// web/lib/about-theme-tokens.ts for the shared heading-color decision.
export default function MethodPageContent() {
  const theme = useTheme();
  const heading = `font-display text-2xl md:text-3xl ${ABOUT_HEADING_CLASS[theme]} mb-8`;

  return (
    <main className="bg-paper min-h-screen">
      <div className="max-w-3xl mx-auto px-6 py-16 md:py-24">
        <div className="divide-y divide-gray-100">

          <section className="pb-16">
            <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">The Evidence</p>
            <h2 className={heading}>It Kept Showing Up</h2>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              I noticed these patterns before I ever called myself a consultant — in my own work, watching the same dynamics play out under different names in different rooms.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              Then I was suddenly exposed to many client organizations at once, and the coincidence stopped looking like coincidence. The same conditions kept surfacing — in exit interviews, in engagement survey results, in how leaders actually behaved under pressure — across organizations that had nothing in common except the pattern itself.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              After several years of navigating that, watching it hold up client after client, I went looking for confirmation outside my own observation. Court records from employment litigation. Insurance claims data. Anonymous reviews written after someone had already decided to leave. Years of conference agendas built around what practitioners were worried about that year. Decades of organizational psychology research asking why certain conditions produce certain outcomes, and by what mechanism.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              None of those sources talk to each other. A litigation record doesn&apos;t know what an exit interview says. An insurance actuary isn&apos;t reading Glassdoor. And when I laid them side by side against what I&apos;d already seen firsthand, the same conditions kept surfacing — not because I was looking for confirmation, but because the pattern was already there before I went looking a second time.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              What an organization says is wrong and what&apos;s actually wrong are almost never the same thing. That gap is the reason most fixes don&apos;t hold. It&apos;s also the thing I saw first in my own work, then watched repeat across every external source I checked.
            </p>
          </section>

          <section className="pt-16">
            <p className="font-ui text-xs tracking-widest uppercase text-gray-400 mb-2">What This Isn&apos;t</p>
            <h2 className={heading}>Not a Framework to Learn</h2>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              None of this is a system you need to study before I can help you. The pattern came first — from years of direct observation, then confirmed against sources that had every reason to disagree with each other.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              That&apos;s the difference between a framework and a diagnosis. A framework asks you to learn its language. A diagnosis just needs to be right.
            </p>
          </section>

        </div>
      </div>
    </main>
  );
}
