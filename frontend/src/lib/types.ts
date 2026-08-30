export type Bucket =
  | "apply_now"
  | "coming_soon"
  | "not_yet"
  | "closed_for_now"
  | "not_for_you"
  | "unknown";

export type Layer =
  | "central"
  | "your_state"
  | "your_city"
  | "open_to_all_states"
  | "another_state";

export type Language = "en" | "hi";

export interface Citation {
  page: number;
  quote: string;
}

export interface Reason {
  text: string;
  citation: Citation | null;
  blocks_application: boolean;
  is_permanent: boolean;
}

export interface RadarEntry {
  exam_name: string;
  official_title: string;
  body: string;
  body_full: string;
  source_id: string;
  bucket: Bucket;
  headline: string;
  layer: Layer;
  layer_label: string;
  reasons: Reason[];
  rules_known: boolean;
  official_url: string | null;
  document_title: string | null;
  closing_text: string | null;
  closing_on: string | null;
  fee_payable: number | null;
  unchecked: string[];
}

export interface Radar {
  language: Language;
  student_name: string;
  generated_on: string;
  total_watched: number;
  counts: Partial<Record<Bucket, number>>;
  entries: RadarEntry[];
}

export interface Student {
  id: number;
  name: string;
  date_of_birth: string;
  category: string;
  gender: string;
  is_pwbd: boolean;
  is_ex_serviceman: boolean;
  state: string;
  district: string;
  age_today: number;
  education: {
    degree: string;
    stream: string | null;
    completed_year: number | null;
    percentage: number | null;
    is_completed: boolean;
  };
}

export interface Deadline {
  exam_name: string;
  source_id: string;
  label: string;
  due_on: string;
  days_left: number;
  is_approximate: boolean;
  you_can_apply: boolean;
  citation_page: number | null;
  citation_quote: string | null;
  urgency: "today" | "this week" | "this month" | "later";
  plain_words: string;
}

export interface JournalEvent {
  kind: string;
  detail: string;
  worth_telling: boolean;
}

export interface JournalRun {
  id: number;
  ran_at: string;
  sources_checked: number;
  citations_verified: number;
  rules_evaluated: number;
  changes_found: number;
  messages_sent: number;
  seconds_taken: number;
  was_silent: boolean;
  checks_run: number;
  events: JournalEvent[];
}

export interface FeeSaving {
  exam_name: string;
  source_id: string;
  you_pay: number;
  others_pay: number;
  saved: number;
  is_free_for_you: boolean;
  plain_words: string;
}

export interface SavingsSummary {
  student_name: string;
  savings: FeeSaving[];
  total_saved: number;
  message: string;
}

export interface AgeCliff {
  student_name: string;
  next_birthday: string;
  turning: number;
  exams_closing: {
    exam_name: string;
    source_id: string;
    limit_for_you: number;
    closes_on_birthday: number;
    closes_on: string;
  }[];
  has_warning: boolean;
  message: string;
}

export interface DocumentSpec {
  kind: "photograph" | "signature" | "thumb_impression";
  label: string;
  width_px: number | null;
  height_px: number | null;
  min_kb: number | null;
  max_kb: number | null;
  needed: string;
}

export interface MadeDocument {
  kind: DocumentSpec["kind"];
  label: string;
  width_px: number;
  height_px: number;
  size_kb: number;
  padded: boolean;
  matches_spec: boolean;
  needed: string;
  image_base64: string;
}
