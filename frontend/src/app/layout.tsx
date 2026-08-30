import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";

import "./globals.css";

const inter = Inter({ subsets: ["latin", "latin-ext"], display: "swap", variable: "--font-inter" });
const fraunces = Fraunces({
  subsets: ["latin"],
  display: "swap",
  weight: ["600", "700"],
  variable: "--font-fraunces",
});

export const metadata: Metadata = {
  title: "Sarathi",
  description:
    "An agent that watches every government exam in India for one student, and only speaks when something needs them.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${fraunces.variable}`}>
      <body className="font-sans antialiased">{children}</body>
    </html>
  );
}
