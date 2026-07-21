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
          localStorage before React hydrates. Inert today: no page writes
          to prv3-theme yet (ThemeSwitcher isn't mounted anywhere until
          Stage 4), so this never fires in practice until then. Prevents
          flash-of-wrong-theme once it does. suppressHydrationWarning
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
        {children}
      </body>
    </html>
  );
}
