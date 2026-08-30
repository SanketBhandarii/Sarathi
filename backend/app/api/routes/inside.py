from __future__ import annotations

import json
import time

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import get_settings
from app.db.repositories import documents as docs_repo
from app.extraction.document import load_pages
from app.extraction.review import (
    check_citations,
    check_values,
    unsound_checks,
    unsupported_values,
)
from app.storage.cache import NotificationCache

router = APIRouter(prefix="/inside", tags=["inside"])


class ToolOut(BaseModel):
    name: str
    what_it_does: str


class AgentOut(BaseModel):
    name: str
    job: str
    model_role: str
    tools: list[ToolOut]


class EdgeOut(BaseModel):
    frm: str
    to: str
    when: str


class GraphOut(BaseModel):
    agents: list[AgentOut]
    edges: list[EdgeOut]
    loops_back: bool
    max_passes: int


def _tools_of(agent) -> list[ToolOut]:
    config = agent.tool_registry.get_all_tools_config()
    found: list[ToolOut] = []
    for name in agent.tool_names:
        spec = config.get(name, {})
        description = spec.get("description", "") if isinstance(spec, dict) else ""
        first_line = description.strip().splitlines()[0] if description.strip() else ""
        found.append(ToolOut(name=name, what_it_does=first_line or "no description"))
    return found


@router.get("/graph", response_model=GraphOut)
def read_graph() -> GraphOut:
    from agents.graph import MAX_PASSES, build_checker, build_reader

    reader = build_reader()
    checker = build_checker()

    return GraphOut(
        agents=[
            AgentOut(
                name=reader.name,
                job="reads a section of the notification and writes down what it found",
                model_role="the stronger model, because misreading a rule is the worst failure",
                tools=_tools_of(reader),
            ),
            AgentOut(
                name=checker.name,
                job="compares every recorded number against the page it claims to come from",
                model_role="the same model, given a tool that does the comparison in code",
                tools=_tools_of(checker),
            ),
        ],
        edges=[
            EdgeOut(frm="reader", to="checker", when="always"),
            EdgeOut(
                frm="checker",
                to="reader",
                when="only when the checker reported problems",
            ),
        ],
        loops_back=True,
        max_passes=MAX_PASSES,
    )


class CheckLine(BaseModel):
    field: str
    page: int
    quote: str
    quote_is_on_that_page: bool
    match: str
    value: float | None = None
    value_is_in_the_quote: bool | None = None


class VerifyOut(BaseModel):
    exam_name: str
    source_id: str
    document_pages: int
    quotes_checked: int
    numbers_checked: int
    problems: int
    took_seconds: float
    used_a_model: bool
    lines: list[CheckLine]


@router.get("/verify", response_model=VerifyOut)
def verify_live(
    document_sha256: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> VerifyOut:
    rules_list = docs_repo.all_rules(db)
    if not rules_list:
        raise HTTPException(status_code=404, detail="no exam rules loaded yet")

    rules = next(
        (r for r in rules_list if r.document_sha256 == document_sha256),
        None,
    ) or max(rules_list, key=lambda r: len(r.all_citations()))

    settings = get_settings()
    cache = NotificationCache(settings.notifications_path)
    cached = cache.index.by_hash().get(rules.document_sha256)
    if cached is None:
        raise HTTPException(status_code=404, detail="the pdf for those rules is not cached")

    started = time.perf_counter()
    pages = load_pages(cached.path_under(cache.root))
    citations = check_citations(rules, pages)
    values = check_values(rules)
    took = time.perf_counter() - started

    by_field = {v.field: v for v in values}
    lines = [
        CheckLine(
            field=c.field,
            page=c.page,
            quote=c.quote[:150],
            quote_is_on_that_page=c.is_sound,
            match=f"{c.match_ratio:.0%}",
            value=by_field[c.field].value if c.field in by_field else None,
            value_is_in_the_quote=by_field[c.field].supported if c.field in by_field else None,
        )
        for c in citations
    ]

    return VerifyOut(
        exam_name=rules.exam_name,
        source_id=rules.source_id,
        document_pages=len(pages),
        quotes_checked=len(citations),
        numbers_checked=len(values),
        problems=len(unsound_checks(citations)) + len(unsupported_values(values)),
        took_seconds=round(took, 3),
        used_a_model=False,
        lines=lines,
    )
