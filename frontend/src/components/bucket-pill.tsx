import type { Bucket } from "@/lib/types";
import { BUCKET_TONE } from "@/lib/format";

export function BucketPill({ bucket, label }: { bucket: Bucket; label: string }) {
  return (
    <span
      className={`inline-flex items-center whitespace-nowrap rounded-pill px-2.5 py-1 text-[11px] font-medium ${BUCKET_TONE[bucket]}`}
    >
      {label}
    </span>
  );
}
