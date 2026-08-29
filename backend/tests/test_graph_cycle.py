from __future__ import annotations

from dataclasses import dataclass

from agents.graph import _checker_found_problems


@dataclass
class FakeResult:
    result: str


@dataclass
class FakeState:
    results: dict[str, FakeResult]


def test_no_cycle_when_the_checker_is_happy():
    state = FakeState({"checker": FakeResult("all good. nothing wrong here")})
    assert _checker_found_problems(state) is False


def test_cycle_fires_when_the_checker_reports_problems():
    state = FakeState(
        {"checker": FakeResult("problems found:\n- age.maximum_years: recorded as 45")}
    )
    assert _checker_found_problems(state) is True


def test_cycle_is_case_insensitive():
    state = FakeState({"checker": FakeResult("PROBLEMS FOUND: one claim is wrong")})
    assert _checker_found_problems(state) is True


def test_no_cycle_before_the_checker_has_run():
    assert _checker_found_problems(FakeState({})) is False


def test_graph_wires_reader_to_checker_and_back():
    from agents.graph import build_reading_graph

    graph = build_reading_graph()
    edges = {(e.from_node.node_id, e.to_node.node_id) for e in graph.edges}
    assert ("reader", "checker") in edges
    assert ("checker", "reader") in edges

    back_edge = next(e for e in graph.edges if e.to_node.node_id == "reader")
    assert back_edge.condition is not None
