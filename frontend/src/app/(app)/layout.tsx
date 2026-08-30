import { Sidebar } from "@/components/sidebar";
import { TopBar } from "@/components/top-bar";
import { DEMO_STUDENT, DEMO_TODAY, api } from "@/lib/api";

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

export default async function AppLayout({ children }: { children: React.ReactNode }) {
  const { student, urgent } = await loadShell();

  return (
    <div className="min-h-screen p-0 lg:p-6">
      <div className="flex min-h-screen overflow-hidden border-line bg-shell lg:min-h-[calc(100vh-3rem)] lg:rounded-shell lg:border lg:shadow-[0_1px_3px_rgba(16,17,20,0.06)]">
        <Sidebar unread={urgent} />
        <div className="flex min-w-0 flex-1 flex-col">
          <TopBar student={student} hasNews={urgent > 0} />
          <main className="min-w-0 flex-1 overflow-x-hidden px-6 pb-10 pt-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
