import { notFound } from "next/navigation";
import { getShareRecord } from "@/lib/share-store";
import ShareableOutput from "@/components/ShareableOutput";

// Server Component — no "use client".
// Upstash credentials never reach the browser bundle.
//
// Reads Redis directly via web/lib/share-store.ts, shared with
// web/app/api/share/[id]/route.ts -- previously this fetched that same
// route via resolveBaseUrl()/process.env.VERCEL_URL, a server-to-server
// self-fetch that this project's ssoProtection setting (deploymentType:
// "all_except_custom_domains") blocks unconditionally, confirmed live via
// a 302 to Vercel's own auth wall. That made this page show "not found"
// for every share link regardless of whether the record was valid.
// Reading Redis directly removes the self-fetch, and that failure mode,
// entirely.

interface SharePageProps {
  params: Promise<{ id: string }>;
}

export default async function SharePage({ params }: SharePageProps) {
  const { id } = await params;

  const payload = await getShareRecord(id);

  if (payload === null) {
    notFound();
  }

  return (
    <main className="min-h-screen bg-paper px-6 py-10 md:px-10 md:py-14">
      <ShareableOutput payload={payload} />
    </main>
  );
}
