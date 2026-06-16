import type { Metadata } from "next";
import { Geist, Geist_Mono, Lora, Inter } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
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
      className={`${geistSans.variable} ${geistMono.variable} ${lora.variable} ${inter.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <nav className="flex justify-between items-center px-6 py-4 border-b border-gray-100 bg-white">
          <Link
            href="/"
            className="font-ui text-sm font-semibold text-gray-900 hover:text-gray-600 transition-colors"
          >
            Principal Resolution
          </Link>
          <Link
            href="/book"
            className="font-ui text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            The Book
          </Link>
        </nav>
        {children}
      </body>
    </html>
  );
}
