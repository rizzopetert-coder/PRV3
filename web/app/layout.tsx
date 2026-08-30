import type { Metadata } from "next";
import {
  Geist,
  Geist_Mono,
  IBM_Plex_Mono,
  Lora,
  Inter,
  Source_Serif_4,
} from "next/font/google";
import "./globals.css";
import { NavBar } from "@/components/NavBar";
import { MobileMenu } from "@/components/MobileMenu";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

// Visual identity v2 (OD-07, Stage 1) — replaces JetBrains Mono, which was
// confirmed unused as a live `font-mono` utility anywhere in the site
// before this change (see globals.css).
const ibmPlexMono = IBM_Plex_Mono({
  variable: "--font-ibm-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

const lora = Lora({
  variable: "--font-lora",
  subsets: ["latin"],
  style: ["normal", "italic"],
  weight: ["400", "500", "600", "700"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  weight: ["400", "500"],
});

// Visual identity v2 (OD-07, Stage 1) — new capability (font-serif was
// unmapped/unused before this change), not a change to --font-display
// (Lora), which every existing page still uses unchanged.
const sourceSerif4 = Source_Serif_4({
  variable: "--font-source-serif-4",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Principal Resolution",
  description: "Organizational diagnostic",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${ibmPlexMono.variable} ${lora.variable} ${inter.variable} ${sourceSerif4.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <head>
        {/*
          Visual identity v2 theme persistence (OD-07, Stage 1) — blocking
          script, runs before first paint, sets data-theme on <html> from
          localStorage before React hydrates. ThemeSwitcher (OD-07) is not
          currently mounted anywhere -- infrastructure left dormant after
          the v1 rollback, commit b8860b5. This script may still fire for a
          returning visitor with a stale prv3-theme value in localStorage,
          but doing so has no visible effect today -- no live page consumes
          the resulting data-theme-scoped CSS variables. suppressHydrationWarning
          above is required because this attribute is set outside React's
          render, after the server-rendered markup (which never has
          data-theme) is sent.
        */}
        <script
          dangerouslySetInnerHTML={{
            __html: `try {
  var t = localStorage.getItem("prv3-theme");
  if (t === "dark" || t === "neutral") {
    document.documentElement.setAttribute("data-theme", t);
  }
} catch (e) {}`,
          }}
        />
      </head>
      <body className="min-h-full flex flex-col">
        <NavBar />
        {/* Homepage restructure (this session) -- mounted as a sibling to
            NavBar, not inside it. NavBar.tsx is explicitly out of scope
            (Pete's instruction, 2026-08-29); MobileMenu is fully
            self-contained (own fixed trigger + overlay), so this is the
            only wiring point needed. */}
        <MobileMenu />
        {children}
      </body>
    </html>
  );
}
