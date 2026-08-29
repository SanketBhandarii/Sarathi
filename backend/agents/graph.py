from __future__ import annotations

from dataclasses import dataclass

from strands import Agent
from strands.multiagent import GraphBuilder
from strands.multiagent.graph import GraphState

from agents.models import patient_retries, tool_calling_model
from agents.pacing import pacer
from agents.prompts import GRAPH_CHECKER_SYSTEM, GRAPH_READER_SYSTEM
from app.extraction.schema import ExamRules
from tools import extraction_tools as et

MAX_PASSES = 6
PROBLEM_MARKER = "problems found"


def build_reader() -> Agent:
    return Agent(
        model=tool_calling_model(),
        system_prompt=GRAPH_READER_SYSTEM,
        tools=[et.read_section, et.record_age_rule, et.record_age_relaxation],
        callback_handler=None,
        retry_strategy=patient_retries(),
        hooks=[pacer()],
        name="reader",
        description="reads the age rules out of a notification and records them",
    )


def build_checker() -> Agent:
    return Agent(
        model=tool_calling_model(),
        system_prompt=GRAPH_CHECKER_SYSTEM,
        tools=[et.check_what_was_recorded],
        callback_handler=None,
        retry_strategy=patient_retries(),
        hooks=[pacer()],
        name="checker",
        description="checks recorded claims against the pages of the notification",
    )


def _checker_found_problems(state: GraphState) -> bool:
    result = state.results.get("checker")
    if result is None:
        return False
    return PROBLEM_MARKER in str(result.result).lower()


def build_reading_graph():
    builder = GraphBuilder()
    builder.add_node(build_reader(), "reader")
    builder.add_node(build_checker(), "checker")
    builder.add_edge("reader", "checker")
    builder.add_edge("checker", "reader", condition=_checker_found_problems)
    builder.set_entry_point("reader")
    builder.reset_on_revisit(True)
    builder.set_max_node_executions(MAX_PASSES)
    return builder.build()


@dataclass
class GraphOutcome:
    rules: ExamRules | None
    passes: int
    order: list[str]
    status: str


def read_document(sha256: str, exam_name: str, source_id: str) -> GraphOutcome:
    et.start_draft(sha256, exam_name, source_id)
    graph = build_reading_graph()

    task = (
        f"document_sha256: {sha256}\n"
        f"notification: {exam_name}\n\n"
        "Read the age section of this notification and record the age limits and "
        "every age relaxation, each with the page and the sentence it came from."
    )
    result = graph(task)
    order = [node.node_id for node in result.execution_order]

    return GraphOutcome(
        rules=et.draft_for(sha256),
        passes=order.count("reader"),
        order=order,
        status=str(result.status),
    )
