from __future__ import annotations

import re

from app.student.qualifications import LEVEL_LABEL, RANK, Level

LEVEL_PATTERNS: list[tuple[Level, tuple[str, ...]]] = [
    (
        Level.POST_GRADUATION,
        (r"post[\s\-]*grad", r"\bmaster'?s?\b", r"\bm\.?\s?(a|sc|com|tech|e|ed)\b", r"\bpg\b"),
    ),
    (
        Level.GRADUATION,
        (
            r"\bdegree\b", r"\bgraduat", r"\bbachelor", r"\bb\.?\s?(a|sc|com|tech|e|ed)\b",
            r"three\s+year\s+degree", r"university\s+degree",
        ),
    ),
    (Level.DIPLOMA, (r"\bdiploma\b", r"polytechnic")),
    (Level.ITI, (r"\biti\b", r"industrial\s+training", r"national\s+trade\s+certificate", r"\bnac\b")),
    (
        Level.CLASS_12,
        (
            r"12th", r"10\s*\+\s*2", r"intermediate", r"senior\s+secondary",
            r"higher\s+secondary", r"\bhsc\b", r"\bxii\b",
        ),
    ),
    (
        Level.CLASS_10,
        (r"10th", r"matricul", r"\bsslc\b", r"\bssc\b", r"secondary\s+school", r"\bx\b"),
    ),
]


def level_asked_for(requirement: str) -> Level | None:
    text = " ".join(requirement.split())
    for level, patterns in LEVEL_PATTERNS:
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            return level
    return None


def satisfies(student_level: Level | None, needed: Level) -> bool:
    if student_level is None:
        return False
    return RANK[student_level] >= RANK[needed]


def what_is_missing(needed: Level, highest: Level | None) -> str:
    needed_name = LEVEL_LABEL[needed].lower()
    if highest is None:
        return f"This exam needs {needed_name}. You have not added any qualification yet."
    return (
        f"This exam needs {needed_name}. Your highest is "
        f"{LEVEL_LABEL[highest].lower()}."
    )


OPTIONAL_MARKERS = (
    r"desirable",
    r"preferab",
    r"will be an added advantage",
    r"added advantage",
    r"not essential",
)


def is_only_desirable(*texts: str) -> bool:
    joined = " ".join(t for t in texts if t)
    return any(re.search(marker, joined, re.IGNORECASE) for marker in OPTIONAL_MARKERS)
