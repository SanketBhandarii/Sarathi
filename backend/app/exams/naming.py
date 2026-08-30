from __future__ import annotations

import re

from pydantic import BaseModel

BODY_NAME: dict[str, str] = {
    "ssc": "SSC",
    "upsc": "UPSC",
    "ibps": "IBPS",
    "mpsc": "MPSC",
    "bmc": "BMC",
}

BODY_FULL: dict[str, str] = {
    "ssc": "Staff Selection Commission",
    "upsc": "Union Public Service Commission",
    "ibps": "Institute of Banking Personnel Selection",
    "mpsc": "Maharashtra Public Service Commission",
    "bmc": "Brihanmumbai Municipal Corporation",
}

KNOWN: list[tuple[str, str]] = [
    (r"crp[\s\-]*po", "IBPS PO"),
    (r"crp[\s\-]*clerk", "IBPS Clerk"),
    (r"crp[\s\-]*rrb", "IBPS RRB"),
    (r"crp[\s\-]*(so|sp)\b", "IBPS SO"),
    (r"combined\s+graduate\s+level", "SSC CGL"),
    (r"combined\s+higher\s+secondary", "SSC CHSL"),
    (r"multi[\s\-]*tasking", "SSC MTS"),
    (r"constables?\s*\(?gd", "SSC GD Constable"),
    (r"junior\s+engineer", "SSC JE"),
    (r"stenographer", "SSC Stenographer"),
    (r"sub[\s\-]*inspector", "SSC CPO"),
    (r"combined\s+hindi\s+translator", "SSC JHT"),
    (r"selection\s+post", "SSC Selection Posts"),
    (r"jsa\s*/\s*ldc", "SSC JSA/LDC Departmental"),
    (r"ssa\s*/\s*udc", "SSC SSA/UDC Departmental"),
    (r"aso grade.*departmental", "SSC ASO Departmental"),
    (r"deputy\s+superintendent", "MPSC Deputy Superintendent"),
    (r"deputy\s+engineer", "MPSC Deputy Engineer"),

    (r"civil\s+services", "UPSC CSE"),
    (r"engineering\s+services", "UPSC ESE"),
    (r"combined\s+defence", "UPSC CDS"),
    (r"national\s+defence", "UPSC NDA"),
    (r"state\s+services", "MPSC State Services"),
    (r"group[\s\-]*c\s+services", "MPSC Group C"),
    (r"group[\s\-]*b\s+services", "MPSC Group B"),
    (r"civil\s+judge", "MPSC Civil Judge"),
]

ADVT_PATTERN = re.compile(r"advt?\.?\s*no\.?\s*([0-9]+)\s*[/\-]\s*([0-9]{4})", re.IGNORECASE)
ADVERTISEMENT_PATTERN = re.compile(r"advertisement\s*no\.?\s*([0-9]+)\s*[\-/]\s*([0-9]{4})", re.IGNORECASE)
YEAR_PATTERN = re.compile(r"\b(20[2-4][0-9])\b")
NOISE = re.compile(r"^(advt?\.?\s*no\.?\s*[0-9/\-]+\s*[\- to ]?\s*)", re.IGNORECASE)


class ExamName(BaseModel):
    short: str
    full: str
    body: str
    body_full: str
    raw: str


def _year_in(title: str) -> str | None:
    years = YEAR_PATTERN.findall(title)
    return years[-1] if years else None


def _advertisement_number(title: str) -> str | None:
    for pattern in (ADVT_PATTERN, ADVERTISEMENT_PATTERN):
        found = pattern.search(title)
        if found:
            return f"{int(found.group(1))}/{found.group(2)}"
    return None


def _tidy(title: str) -> str:
    cleaned = NOISE.sub("", " ".join(title.split())).strip(" -:,")
    return cleaned or title.strip()


def _shorten(title: str, body: str, limit: int = 42) -> str:
    head = title if title.upper().startswith(body.upper()) else f"{body} {title}"
    if len(head) <= limit:
        return head
    words: list[str] = []
    for word in head.split():
        if len(" ".join([*words, word])) > limit:
            break
        words.append(word)
    return " ".join(words) + "…"


def name_for(raw_title: str, source_id: str) -> ExamName:
    body = BODY_NAME.get(source_id, source_id.upper())
    body_full = BODY_FULL.get(source_id, body)
    title = " ".join(raw_title.split())
    year = _year_in(title)

    for pattern, label in KNOWN:
        if re.search(pattern, title, re.IGNORECASE):
            short = f"{label} {year}" if year and year not in label else label
            return ExamName(
                short=short, full=_tidy(title), body=body, body_full=body_full, raw=raw_title
            )

    advertisement = _advertisement_number(title)
    if advertisement:
        short = f"{body} Advt {advertisement}"
        return ExamName(
            short=short, full=_tidy(title), body=body, body_full=body_full, raw=raw_title
        )

    tidied = _tidy(title)
    return ExamName(
        short=_shorten(tidied, body), full=tidied, body=body, body_full=body_full, raw=raw_title
    )
