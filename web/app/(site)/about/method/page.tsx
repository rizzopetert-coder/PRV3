import type { Metadata } from "next";
import MethodPageContent from "@/components/MethodPageContent";

export const metadata: Metadata = {
  title: "Our Method | Principal Resolution",
};

// Content and theme-conditional heading color live in
// MethodPageContent.tsx (client component, Dark/Neutral rollout this
// session) -- same split as /about/story and /about/services, for the
// same reason: metadata exports require a Server Component.
export default function MethodPage() {
  return <MethodPageContent />;
}
