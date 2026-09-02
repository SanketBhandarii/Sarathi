const BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://127.0.0.1:8020";

export type Level =
  | "class_10"
  | "class_12"
  | "iti"
  | "diploma"
  | "graduation"
  | "post_graduation";

export interface SavedQualification {
  level: Level;
  board_or_university: string | null;
  college: string | null;
  stream: string | null;
  marks_kind: "percentage" | "cgpa";
  marks: number | null;
  cgpa_scale: number | null;
  passed_year: number | null;
  is_completed: boolean;
  current_semester: number | null;
  label: string;
  percentage: number | null;
  shown_marks: string;
  conversion_note: string | null;
}

export interface MyProfile {
  student_id: number;
  email: string;
  name: string;
  date_of_birth: string;
  age_today: number;
  category: string;
  gender: string;
  is_pwbd: boolean;
  is_ex_serviceman: boolean;
  state: string;
  district: string;
  qualifications: SavedQualification[];
  highest_label: string | null;
}

export interface MyPicture {
  kind: "photograph" | "signature" | "thumb_impression";
  label: string;
  guidance: string;
  file_id: string | null;
  view_url: string | null;
  is_private: boolean;
  width_px: number | null;
  height_px: number | null;
  byte_size: number | null;
  uploaded_at: string | null;
}

async function mine<T>(path: string, token: string): Promise<T | null> {
  try {
    const response = await fetch(`${BASE}${path}`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export const myProfile = (token: string) => mine<MyProfile>("/auth/profile", token);
export const myPictures = (token: string) => mine<MyPicture[]>("/me/documents", token);

export async function myPhotoUrl(token: string): Promise<string | null> {
  const pictures = await myPictures(token);
  return pictures?.find((one) => one.kind === "photograph")?.view_url ?? null;
}
