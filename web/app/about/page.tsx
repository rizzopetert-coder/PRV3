import type { Metadata } from "next";
import Link from "next/link";

export const metadata: Metadata = {
  title: "About | Principal Resolution",
};

export default function AboutPage() {
  return (
    <main className="bg-paper min-h-screen">
      <div className="max-w-3xl mx-auto px-6 py-16 md:py-24">
        <h1 className="font-display text-3xl text-charcoal mb-4">About</h1>
        <p className="font-ui text-base text-oxide-text mb-12">
          You came here with a question. These three pages each answer a different version of it.
        </p>
        <div className="space-y-4">
          <p className="font-ui text-base text-oxide-text leading-relaxed">
            <Link href="/about/story" className="underline hover:text-hover-ink">The Story</Link> covers who built this practice and the twenty-five years behind it.
          </p>
          <p className="font-ui text-base text-oxide-text leading-relaxed">
            <Link href="/about/method" className="underline hover:text-hover-ink">The Method</Link> explains where the underlying pattern came from, confirmed against sources that had no reason to agree with each other.
          </p>
          <p className="font-ui text-base text-oxide-text leading-relaxed">
            <Link href="/about/services" className="underline hover:text-hover-ink">The Services</Link> lays out what actually happens once a diagnostic finds something real.
          </p>
        </div>
      </div>
    </main>
  );
}
