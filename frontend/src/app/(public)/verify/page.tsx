import { redirect } from "next/navigation";

import { whereToResume } from "@/lib/session";

import { VerifyScreen } from "./form";

export const dynamic = "force-dynamic";

export default async function VerifyPage() {
  const resume = await whereToResume();
  if (resume) redirect(resume);
  return <VerifyScreen />;
}
