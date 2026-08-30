import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { Sidebar } from "@/components/sidebar";
import { TopBar } from "@/components/top-bar";
import { DEMO_STUDENT, api } from "@/lib/api";

import "./globals.css";

const inter = Inter({
  subsets: ["latin", "latin-ext"],
  display: "swap",
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Sarathi",
  description: "An agent that watches every government exam for one student.",
};

async function loadStudent() {
  try {
    return await api.student(DEMO_STUDENT);
  } catch {
    return null;
  }
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const student = await loadStudent();

  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased">
        <div className="flex min-h-screen">
          <Sidebar
            studentName={student?.name ?? "Not connected"}
            district={student ? `${student.district}, ${student.state}` : "—"}
          />
          <div className="flex min-w-0 flex-1 flex-col">
            <TopBar student={student} />
            <main className="min-w-0 flex-1 px-5 pb-10 pt-5 lg:px-7">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
