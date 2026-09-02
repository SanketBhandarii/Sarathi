from __future__ import annotations

import re

from app.student.profile import Category, Gender, StudentProfile

CATEGORY_PATTERNS: dict[Category, tuple[str, ...]] = {
    Category.SC: (r"scheduled\s*caste", r"\bsc\b"),
    Category.ST: (r"scheduled\s*tribe", r"\bst\b"),
    Category.OBC: (r"other\s*backward", r"\bobc\b", r"non[\s-]*creamy"),
    Category.EWS: (r"economically\s*weaker", r"\bews\b"),
    Category.UR: (r"unreserved", r"general\s*category", r"\bur\b", r"\bgen\b"),
}

PWBD_PATTERNS = (r"benchmark\s*disabilit", r"\bpwbd\b", r"\bpwd\b", r"persons?\s*with\s*disabilit")
EX_SERVICEMEN_PATTERNS = (r"ex[\s-]*servicem", r"commissioned\s*officer", r"\becos?\b", r"\bsscos?\b")
FEMALE_PATTERNS = (r"\bwomen\b", r"\bfemale\b")

BOTH_AT_ONCE = (r"\+", r"&", r"belonging\s+to", r"who\s+are\s+also", r"\bcum\b", r"along\s+with")


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def categories_named_in(label: str) -> set[Category]:
    return {
        category
        for category, patterns in CATEGORY_PATTERNS.items()
        if _matches(label, patterns)
    }


def names_one_person_with_every_trait(label: str) -> bool:
    return _matches(label, BOTH_AT_ONCE)


def label_applies_to(label: str, student: StudentProfile) -> bool:
    named_categories = categories_named_in(label)
    names_pwbd = _matches(label, PWBD_PATTERNS)
    names_ex_serviceman = _matches(label, EX_SERVICEMEN_PATTERNS)
    names_women = _matches(label, FEMALE_PATTERNS)

    if not (named_categories or names_pwbd or names_ex_serviceman or names_women):
        return False

    category_fits = student.category in named_categories
    checks = [
        (bool(named_categories), category_fits),
        (names_pwbd, student.is_pwbd),
        (names_ex_serviceman, student.is_ex_serviceman),
        (names_women, student.gender is Gender.FEMALE),
    ]
    asked = [holds for named, holds in checks if named]

    if names_one_person_with_every_trait(label):
        return all(asked)
    return any(asked)


def best_relaxation_years(labels_and_years: list[tuple[str, int]], student: StudentProfile) -> tuple[int, str | None]:
    applicable = [(years, label) for label, years in labels_and_years if label_applies_to(label, student)]
    if not applicable:
        return 0, None
    years, label = max(applicable)
    return years, label
