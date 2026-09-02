import Link from "next/link";

import { CheckCircleIcon, FileIcon, SettingsIcon } from "@/components/icons";
import { Card, Offline, PageHead } from "@/components/ui";
import { initials, longDate, shortDate } from "@/lib/format";
import { myPictures, myProfile } from "@/lib/mine";
import { currentUser } from "@/lib/session";
import { todayDate } from "@/lib/today";

import { ProfileEditor } from "./editor";

export const dynamic = "force-dynamic";

const CATEGORY_LABEL: Record<string, string> = {
  UR: "General / Unreserved",
  OBC: "OBC (Non Creamy Layer)",
  SC: "Scheduled Caste",
  ST: "Scheduled Tribe",
  EWS: "EWS",
};

const GENDER_LABEL: Record<string, string> = {
  male: "Male",
  female: "Female",
  transgender: "Transgender",
};

function Line({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4 border-b border-line py-2.5 last:border-0">
      <span className="text-[12px] text-ink-faint">{label}</span>
      <span className="text-right text-[12.5px] font-medium text-ink">{value}</span>
    </div>
  );
}

export default async function MyProfilePage() {
  const session = await currentUser();
  if (!session) return <Offline hint="Please sign in again." />;

  const [profile, pictures] = await Promise.all([
    myProfile(session.token),
    myPictures(session.token),
  ]);

  if (!profile) {
    return <Offline hint="Your details live on the backend." />;
  }

  const photo = pictures?.find((one) => one.kind === "photograph") ?? null;
  const uploaded = pictures?.filter((one) => one.file_id) ?? [];

  return (
    <div className="flex flex-col gap-6">
      <PageHead date={longDate(todayDate())} greeting="My Profile" />

      <p className="-mt-2 max-w-2xl text-[13px] leading-relaxed text-ink-soft">
        Every verdict Sarathi gives you is worked out from what is on this page. If something here
        is wrong, the answers will be wrong too. Change anything and every exam is judged again.
      </p>

      <div className="grid gap-6 lg:grid-cols-[300px_minmax(0,1fr)]">
        <div className="flex flex-col gap-6">
          <section className="overflow-hidden rounded-card border border-line bg-shell px-5 py-6 text-center">
            {photo?.view_url ? (
              <img
                src={photo.view_url}
                alt={profile.name}
                className="mx-auto h-24 w-24 rounded-full border border-line object-cover"
              />
            ) : (
              <div className="mx-auto flex h-24 w-24 items-center justify-center rounded-full bg-ink text-[26px] font-semibold text-white">
                {initials(profile.name)}
              </div>
            )}

            <h2 className="mt-3.5 text-[17px] font-semibold tracking-tight text-ink">
              {profile.name}
            </h2>
            <p className="mt-0.5 text-[12px] text-ink-soft">{profile.email}</p>
            <p className="mt-2 text-[12px] text-ink-faint">
              {Math.floor(profile.age_today)} years old, {profile.district}, {profile.state}
            </p>

            <Link
              href="/documents"
              className="mt-4 inline-flex cursor-pointer items-center gap-1.5 rounded-[9px] border border-line bg-page px-3.5 py-2 text-[12.5px] font-medium text-ink transition-colors hover:border-accent hover:text-accent"
            >
              <FileIcon className="h-3.5 w-3.5" />
              {photo?.view_url ? "Change your picture" : "Add your picture"}
            </Link>
          </section>

          <Card icon={<FileIcon className="h-4 w-4" />} title="Your pictures">
            <div className="border-t border-line px-5 py-4">
              {uploaded.length === 0 ? (
                <p className="text-[12.5px] leading-relaxed text-ink-soft">
                  You have not added any yet. Forms will ask for a photo, a signature and a thumb
                  impression, each in a size the commission decides.
                </p>
              ) : (
                <ul className="flex flex-col gap-2.5">
                  {uploaded.map((one) => (
                    <li key={one.kind} className="flex items-center gap-3">
                      {one.view_url ? (
                        <img
                          src={one.view_url}
                          alt={one.label}
                          className="h-10 w-10 rounded-[7px] border border-line bg-page object-contain"
                        />
                      ) : null}
                      <div className="min-w-0">
                        <p className="text-[12.5px] font-medium text-ink">{one.label}</p>
                        <p className="text-[11px] text-ink-faint">
                          {one.width_px} by {one.height_px}, added {shortDate(one.uploaded_at)}
                        </p>
                      </div>
                      <CheckCircleIcon className="ml-auto h-4 w-4 text-good" />
                    </li>
                  ))}
                </ul>
              )}
              <Link
                href="/documents"
                className="mt-4 inline-flex cursor-pointer items-center gap-1.5 text-[12.5px] font-medium text-accent hover:underline"
              >
                Open the document maker
              </Link>
            </div>
          </Card>
        </div>

        <div className="flex flex-col gap-6">
          <Card icon={<SettingsIcon className="h-4 w-4" />} title="What Sarathi knows about you">
            <div className="border-t border-line px-5 py-4">
              <div className="grid gap-x-8 sm:grid-cols-2">
                <div>
                  <Line label="Name" value={profile.name} />
                  <Line label="Date of birth" value={shortDate(profile.date_of_birth)} />
                  <Line label="Age today" value={`${profile.age_today} years`} />
                  <Line
                    label="Category"
                    value={CATEGORY_LABEL[profile.category] ?? profile.category}
                  />
                </div>
                <div>
                  <Line label="Gender" value={GENDER_LABEL[profile.gender] ?? profile.gender} />
                  <Line label="State" value={profile.state} />
                  <Line label="District" value={profile.district} />
                  <Line label="Highest finished" value={profile.highest_label ?? "Not given yet"} />
                </div>
              </div>

              {profile.is_pwbd || profile.is_ex_serviceman ? (
                <div className="mt-3 flex flex-wrap gap-2">
                  {profile.is_pwbd ? (
                    <span className="rounded-pill bg-cold-soft px-3 py-1 text-[11.5px] font-medium text-cold">
                      Benchmark disability
                    </span>
                  ) : null}
                  {profile.is_ex_serviceman ? (
                    <span className="rounded-pill bg-cold-soft px-3 py-1 text-[11.5px] font-medium text-cold">
                      Ex serviceman
                    </span>
                  ) : null}
                </div>
              ) : null}
            </div>
          </Card>

          <Card icon={<CheckCircleIcon className="h-4 w-4" />} title="Your education">
            <div className="border-t border-line px-5 py-4">
              {profile.qualifications.length === 0 ? (
                <p className="text-[12.5px] text-ink-soft">Nothing added yet.</p>
              ) : (
                <ul className="flex flex-col gap-3">
                  {profile.qualifications.map((one) => (
                    <li key={one.level} className="rounded-card border border-line bg-page px-4 py-3">
                      <div className="flex flex-wrap items-center gap-2">
                        <p className="text-[13px] font-medium text-ink">{one.label}</p>
                        <span
                          className={`rounded-[6px] px-2 py-0.5 text-[11px] font-medium ${
                            one.is_completed ? "bg-good-soft text-good" : "bg-sun-soft text-sun"
                          }`}
                        >
                          {one.is_completed
                            ? `passed ${one.passed_year ?? ""}`.trim()
                            : `still studying, semester ${one.current_semester ?? "?"}`}
                        </span>
                        <span className="ml-auto text-[12.5px] font-medium tabular text-ink">
                          {one.shown_marks}
                        </span>
                      </div>
                      <p className="mt-1 text-[11.5px] text-ink-soft">
                        {[one.stream, one.college, one.board_or_university]
                          .filter(Boolean)
                          .join(", ") || "No college or board given"}
                      </p>
                      {one.conversion_note ? (
                        <p className="mt-1.5 text-[11px] leading-relaxed text-ink-faint">
                          {one.conversion_note}
                        </p>
                      ) : null}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </Card>

          <ProfileEditor profile={profile} token={session.token} />
        </div>
      </div>
    </div>
  );
}
