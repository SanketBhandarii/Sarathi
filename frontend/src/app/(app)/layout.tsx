import { redirect } from "next/navigation";

import { Sidebar } from "@/components/sidebar";
import { TopBar } from "@/components/top-bar";
import { api } from "@/lib/api";
import { currentUser } from "@/lib/session";
import { todayIso } from "@/lib/today";

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const session = await currentUser();
  if (!session) redirect("/sign-in");
  if (!session.me.student_id) redirect("/profile");

  const studentId = session.me.student_id;
  let urgent = 0;
  let student = null;

  try {
    const [profile, deadlines] = await Promise.all([
      api.student(studentId),
      api.deadlines(studentId, { today: todayIso() }),
    ]);
    student = profile;
    urgent = deadlines.filter((d) => d.days_left <= 30).length;
  } catch {
    student = null;
  }

  return (
    <div className="min-h-screen p-0 lg:p-6">
      <div className="flex min-h-screen overflow-hidden border-line bg-shell lg:min-h-[calc(100vh-3rem)] lg:rounded-shell lg:border lg:shadow-[0_1px_3px_rgba(16,17,20,0.06)]">
        <Sidebar
            state={student?.state ?? "Your state"}
            district={student?.district ?? "Your district"}
          />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar student={student} studentId={studentId} urgent={urgent} />
          <main className="min-w-0 flex-1 overflow-x-hidden px-6 pb-10 pt-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
