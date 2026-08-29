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


def _matches(text: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def label_applies_to(label: str, student: StudentProfile) -> bool:
    if _matches(label, PWBD_PATTERNS) and student.is_pwbd:
        return True
    if _matches(label, EX_SERVICEMEN_PATTERNS) and student.is_ex_serviceman:
        return True
    if _matches(label, FEMALE_PATTERNS) and student.gender is Gender.FEMALE:
        return True

    patterns = CATEGORY_PATTERNS.get(student.category, ())
    return _matches(label, patterns)


def best_relaxation_years(labels_and_years: list[tuple[str, int]], student: StudentProfile) -> tuple[int, str | None]:
    applicable = [(years, label) for label, years in labels_and_years if label_applies_to(label, student)]
    if not applicable:
        return 0, None
    years, label = max(applicable)
    return years, label
