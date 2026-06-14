import { notFound } from "next/navigation";
import type { ShareableOutputPayload } from "@/lib/types";
import ShareableOutput from "@/components/ShareableOutput";

// Server Component — no "use client".
// Upstash credentials never reach the browser bundle.
// All Redis access is via the /api/share/[id] route, server-side only.

function resolveBaseUrl(): string {
  if (process.env.VERCEL_URL) {
    return `https://${process.env.VERCEL_URL}`;
  }
  return "http://localhost:3000";
}

interface SharePageProps {
  params: Promise<{ id: string }>;
}

export default async function SharePage({ params }: SharePageProps) {
  const { id } = await params;

  let payload: ShareableOutputPayload;
  try {
    const res = await fetch(`${resolveBaseUrl()}/api/share/${id}`, {
      cache: "no-store",
    });
    if (!res.ok) {
      notFound();
    }
    payload = (await res.json()) as ShareableOutputPayload;
  } catch {
    notFound();
  }

  return (
    <main className="min-h-screen bg-gray-50 px-6 py-10 md:px-10 md:py-14">
      <ShareableOutput payload={payload} />
    </main>
  );
}
