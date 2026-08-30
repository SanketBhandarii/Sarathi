import { redirect } from "next/navigation";

import { whereToResume } from "@/lib/session";

import { SignInForm } from "./form";

export const dynamic = "force-dynamic";

export default async function SignInPage() {
  const resume = await whereToResume();
  if (resume) redirect(resume);
  return <SignInForm />;
}
