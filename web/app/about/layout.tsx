import { ThemeSwitcher } from "@/components/ThemeSwitcher";

// Scoped ThemeSwitcher mount, /about/* only (Gemini-cleared, see
// prompts/gemini-themeswitcher-review-verification.md, commit 1ffb3e7 --
// explicitly NOT mounted in NavBar.tsx or the root layout). This layout
// applies to every route under /about (the hub, /about/story,
// /about/method, /about/services) and nowhere else -- Next.js App Router
// scopes a nested layout.tsx to its own route segment and everything
// beneath it, with no way for a route outside /about to pick it up.
//
// ThemeSwitcher writes data-theme to document.documentElement, which is
// global, not scoped to this subtree -- switching themes here still
// visually affects any other route for the rest of that browser session
// if the user navigates away (expected per the review, not a bug).
export default function AboutLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <>
      <div className="max-w-3xl mx-auto px-6 pt-6 flex justify-end">
        <div className="w-56">
          <ThemeSwitcher />
        </div>
      </div>
      {children}
    </>
  );
}
