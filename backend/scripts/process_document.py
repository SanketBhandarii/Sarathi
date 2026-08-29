from __future__ import annotations

import json
import sys

import truststore

truststore.inject_into_ssl()

from agents.pipeline import extract_and_verify
from app.core.config import get_settings
from app.extraction.document import load_pages
from app.extraction.store import ExamRulesStore


def main(match: str) -> int:
    settings = get_settings()
    root = settings.notifications_path
    index = json.loads((root / "index.json").read_text("utf-8"))
    doc = next(d for d in index["documents"] if match.lower() in d["title"].lower())

    pages = load_pages(root / doc["relative_path"])
    result = extract_and_verify(
        pages, doc["title"], doc["source_id"], doc["sha256"], use_model_review=False
    )

    for line in result.history:
        print(" ", line)
    print()
    print("attempts:", result.attempts)
    print("trustworthy:", result.trustworthy)
    if result.rules.could_not_verify:
        print("could not verify, so not shown to the student:")
        for field in result.rules.could_not_verify:
            print(f"   - {field}")
        print()
    if result.verdict.problems:
        for p in result.verdict.problems:
            print(f"   [{p.severity}] {p.field}: {p.problem}")
    else:
        r = result.rules
        if r.age:
            print(f"   age {r.age.minimum_years}-{r.age.maximum_years} as on {r.age.reckoned_on}")
        else:
            print("   age rule not readable")
        print(f"   {len(r.age_relaxations)} relaxations, {len(r.fees)} fees, {len(r.qualifications)} qualifications")
        ExamRulesStore(settings.exams_path).put(r)
        print("   saved")
    return 0 if result.trustworthy else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "CRP-PO"))
