import { redirect } from "next/navigation";

import { currentUser } from "@/lib/session";

import { PhotosForm, type MasterDocument } from "./form";

export const dynamic = "force-dynamic";

const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8000";

async function loadDocuments(token: string): Promise<MasterDocument[]> {
  try {
    const response = await fetch(`${BASE}/me/documents`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!response.ok) return [];
    return (await response.json()) as MasterDocument[];
  } catch {
    return [];
  }
}

export default async function PhotosPage() {
  const session = await currentUser();
  if (!session) redirect("/sign-in");
  if (!session.me.student_id) redirect("/profile");

  const documents = await loadDocuments(session.token);
  return <PhotosForm token={session.token} initial={documents} />;
}
