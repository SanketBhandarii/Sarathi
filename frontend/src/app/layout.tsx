import type { Metadata } from "next";
import { Fraunces, Inter } from "next/font/google";

import { Sidebar } from "@/components/sidebar";
import { TopBar } from "@/components/top-bar";
import { DEMO_STUDENT, DEMO_TODAY, api } from "@/lib/api";

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
  description: "An agent that watches every government exam for one student.",
};

async function loadShell() {
  try {
    const [student, deadlines] = await Promise.all([
      api.student(DEMO_STUDENT),
      api.deadlines(DEMO_STUDENT, { today: DEMO_TODAY }),
    ]);
    return { student, urgent: deadlines.filter((d) => d.days_left <= 30).length };
  } catch {
    return { student: null, urgent: 0 };
  }
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const { student, urgent } = await loadShell();

  return (
    <html lang="en" className={`${inter.variable} ${fraunces.variable}`}>
      <body className="font-sans antialiased">
        <div className="min-h-screen p-0 lg:p-6">
          <div className="flex min-h-screen overflow-hidden border-line bg-shell lg:min-h-[calc(100vh-3rem)] lg:rounded-shell lg:border lg:shadow-[0_1px_3px_rgba(16,17,20,0.06)]">
            <Sidebar unread={urgent} />
            <div className="flex min-w-0 flex-1 flex-col">
              <TopBar student={student} hasNews={urgent > 0} />
              <main className="min-w-0 flex-1 overflow-x-hidden px-6 pb-10 pt-6">{children}</main>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
