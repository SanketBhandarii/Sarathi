import { redirect } from "next/navigation";

import { whereToResume } from "@/lib/session";

import { JoinForm } from "./form";

export const dynamic = "force-dynamic";

export default async function JoinPage() {
  const resume = await whereToResume();
  if (resume) redirect(resume);
  return <JoinForm />;
}
