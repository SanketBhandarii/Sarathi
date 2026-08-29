from __future__ import annotations

import json
import sys

import truststore

truststore.inject_into_ssl()

from agents.extractor import extract_rules
from app.core.config import get_settings
from app.extraction.store import ExamRulesStore
from app.extraction.document import load_pages


def main(match: str) -> int:
    root = get_settings().notifications_path
    index = json.loads((root / "index.json").read_text("utf-8"))
    doc = next(d for d in index["documents"] if match.lower() in d["title"].lower())

    store = ExamRulesStore(get_settings().exams_path)
    cached = store.get(doc["sha256"])
    pages = load_pages(root / doc["relative_path"])
    rules = cached or extract_rules(pages, doc["title"], doc["source_id"], doc["sha256"])
    store.put(rules)
    print("from cache" if cached else "freshly extracted")

    print(f"exam: {rules.exam_name}")
    if rules.age:
        a = rules.age
        print(f"age: {a.minimum_years} to {a.maximum_years}, as on {a.reckoned_on}")
        print(f'   page {a.citation.page}: "{a.citation.quote[:110]}"')
    print(f"relaxations: {len(rules.age_relaxations)}")
    for r in rules.age_relaxations:
        print(f"   {r.category[:44]:<46} +{r.extra_years}y  (page {r.citation.page})")
    print(f"qualifications: {len(rules.qualifications)}")
    for q in rules.qualifications:
        print(f"   {q.requirement[:70]}  (page {q.citation.page})")
    print(f"fees: {len(rules.fees)}")
    for f in rules.fees:
        print(f"   Rs {f.amount_rupees:>8.0f}  {f.applies_to[:52]}  (page {f.citation.page})")
    print(f"dates: {len(rules.key_dates)}")
    for d in rules.key_dates[:8]:
        print(f"   {d.happens_on}  {d.label[:56]}  (page {d.citation.page})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "CRP-PO"))
