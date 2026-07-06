import Link from "next/link";

export default function AskPage() {
  return (
    <main className="max-w-2xl mx-auto px-6 py-16">
      <h1 className="font-display text-3xl text-charcoal mb-4">Just Ask.</h1>
      <p className="font-ui text-base text-gray-500 mb-8">
        If you already know what you&apos;re dealing with, start a conversation
        directly.
      </p>
      <Link
        href="mailto:pete@principalresolution.com"
        className="inline-block bg-charcoal text-white font-ui text-sm font-medium px-6 py-3 hover:bg-gray-700 transition-colors"
      >
        Get in touch →
      </Link>
    </main>
  );
}
