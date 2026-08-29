from __future__ import annotations

from app.corrigendum.diff import ChangeKind, Corrigendum, RuleChange
from app.extraction.schema import AgeRelaxation, ApplicationFee, ExamRules, KeyDate


def _as_text(value: object) -> str | None:
    return None if value is None else str(value)


def _compare_age(old: ExamRules, new: ExamRules) -> list[RuleChange]:
    if old.age is None or new.age is None:
        return []
    changes: list[RuleChange] = []
    for field in ("minimum_years", "maximum_years", "reckoned_on"):
        before = getattr(old.age, field)
        after = getattr(new.age, field)
        if before != after:
            changes.append(
                RuleChange(
                    kind=ChangeKind.AGE_CHANGED,
                    field=f"the {field.replace('_', ' ')}",
                    told_you=_as_text(before),
                    now_says=_as_text(after),
                    old_citation=old.age.citation,
                    new_citation=new.age.citation,
                )
            )
    return changes


def _key(item: object) -> str:
    if isinstance(item, AgeRelaxation):
        return item.category.strip().lower()[:40]
    if isinstance(item, ApplicationFee):
        return item.applies_to.strip().lower()[:40]
    if isinstance(item, KeyDate):
        return item.label.strip().lower()[:40]
    return str(item)


def _compare_list(
    old_items: list, new_items: list, kind: ChangeKind, value_of, label_of
) -> list[RuleChange]:
    before = {_key(i): i for i in old_items}
    after = {_key(i): i for i in new_items}
    changes: list[RuleChange] = []

    for key, new_item in after.items():
        old_item = before.get(key)
        if old_item is None:
            changes.append(
                RuleChange(
                    kind=ChangeKind.RULE_ADDED,
                    field=label_of(new_item),
                    told_you=None,
                    now_says=_as_text(value_of(new_item)),
                    new_citation=new_item.citation,
                )
            )
        elif value_of(old_item) != value_of(new_item):
            changes.append(
                RuleChange(
                    kind=kind,
                    field=label_of(new_item),
                    told_you=_as_text(value_of(old_item)),
                    now_says=_as_text(value_of(new_item)),
                    old_citation=old_item.citation,
                    new_citation=new_item.citation,
                )
            )

    for key, old_item in before.items():
        if key not in after:
            changes.append(
                RuleChange(
                    kind=ChangeKind.RULE_REMOVED,
                    field=label_of(old_item),
                    told_you=_as_text(value_of(old_item)),
                    now_says=None,
                    old_citation=old_item.citation,
                )
            )
    return changes


def compare(old: ExamRules, new: ExamRules) -> Corrigendum:
    changes = _compare_age(old, new)

    changes += _compare_list(
        old.age_relaxations, new.age_relaxations, ChangeKind.RELAXATION_CHANGED,
        value_of=lambda r: r.extra_years,
        label_of=lambda r: f"the relaxation for {r.category[:44]}",
    )
    changes += _compare_list(
        old.fees, new.fees, ChangeKind.FEE_CHANGED,
        value_of=lambda f: f.amount_rupees,
        label_of=lambda f: f"the fee for {f.applies_to[:44]}",
    )
    changes += _compare_list(
        old.key_dates, new.key_dates, ChangeKind.DATE_MOVED,
        value_of=lambda d: d.happens_on,
        label_of=lambda d: d.label[:56],
    )
    changes += _compare_list(
        old.qualifications, new.qualifications, ChangeKind.QUALIFICATION_CHANGED,
        value_of=lambda q: q.minimum_percentage,
        label_of=lambda q: f"the qualification {q.requirement[:40]}",
    )

    return Corrigendum(
        exam_name=new.exam_name,
        source_id=new.source_id,
        old_document_sha256=old.document_sha256,
        new_document_sha256=new.document_sha256,
        changes=changes,
    )
