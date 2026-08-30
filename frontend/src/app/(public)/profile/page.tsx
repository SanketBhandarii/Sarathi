import { redirect } from "next/navigation";

import { currentUser } from "@/lib/session";

import { ProfileForm } from "./form";

export const dynamic = "force-dynamic";

export default async function ProfilePage() {
  const session = await currentUser();
  if (!session) redirect("/sign-in");
  if (session.me.student_id) redirect("/dashboard");
  return <ProfileForm token={session.token} />;
}
