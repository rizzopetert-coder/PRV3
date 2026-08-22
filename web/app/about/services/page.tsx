import type { Metadata } from "next";

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

export default function ServicesPage() {
  return (
    <main className="bg-paper min-h-screen">
      <div className="max-w-3xl mx-auto px-6 py-16 md:py-24">

        <p className="font-ui text-base text-oxide-text leading-relaxed mb-12">
          The diagnostic finds the condition. These are the four ways the work actually gets done. Most engagements use one. Some conditions call for two working together.
        </p>

        <div className="divide-y divide-gray-100">

          <section id="people-tactics-and-strategy" className="pb-12">
            <h2 className="font-display text-2xl md:text-3xl text-dusk-blue mb-3">People Tactics and Strategy</h2>
            <p className="font-ui text-sm text-umber italic mb-6">Org assessment, people strategy, and the tactical HR work required to act on it. Not just structure on paper — the actual decisions about how people are organized, managed, and supported, and the hands-on work to make those decisions real.</p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              Some problems live in how the organization is built, not in the people inside it. People Tactics and Strategy starts with an honest look at your structure, your roles, and your people decisions, then does the tactical work to fix what&apos;s not working. Org charts that don&apos;t match how work actually happens. Roles with no clear owner. Decisions that get made twice because nobody agreed who makes them the first time.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              This isn&apos;t a slide deck handed to your team to implement on their own. It&apos;s assessment, strategy, and the on-the-ground work to carry it out.
            </p>
          </section>

          <section id="training-development" className="py-12">
            <h2 className="font-display text-2xl md:text-3xl text-dusk-blue mb-3">Training &amp; Development</h2>
            <p className="font-ui text-sm text-umber italic mb-6">Leadership development, team coaching, and teambuilding, built around what your people actually need rather than a packaged program.</p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              Training &amp; Development covers what most firms split into four different vendors: leadership development, coaching, teambuilding, and skills training. Here it&apos;s one service, built around the specific gap the diagnostic found, not a course catalog.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              A leader who needs to give harder feedback gets coaching, not a seminar. A team that&apos;s stopped trusting each other gets teambuilding that actually changes how they work together afterward, not a retreat with a trust fall and a debrief. Whatever the gap, the work is built to close it, not just to have happened.
            </p>
          </section>

          <section id="intervention" className="py-12">
            <h2 className="font-display text-2xl md:text-3xl text-dusk-blue mb-3">Intervention</h2>
            <p className="font-ui text-sm text-umber italic mb-6">Immediate, in-the-room expertise for a situation that&apos;s live right now.</p>
            <p className="font-ui text-base text-oxide-text leading-relaxed mb-5">
              Some situations can&apos;t wait for a plan. Intervention means someone in the room, with the standing and the expertise to move a live situation, for as long as it takes to resolve.
            </p>
            <p className="font-ui text-base text-oxide-text leading-relaxed">
              This isn&apos;t advice from the outside. It&apos;s direct, immersive engagement inside the situation, while there&apos;s still room to shape how it ends.
            </p>
          </section>

          <section id="executive-advisory" className="pt-12">
            <h2 className="font-display text-2xl md:text-3xl text-dusk-blue mb-3">Executive Advisory</h2>
            <p className="font-ui text-sm text-umber italic mb-6">A confidential, ongoing relationship for the decisions that can&apos;t be discussed with anyone inside the organization.</p>
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
