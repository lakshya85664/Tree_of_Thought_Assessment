import pytest

from thought_tree.models import Candidate
from thought_tree.search import SearchResult, search


def test_candidate_stores_required_state():
    candidate = Candidate(
        path=[
            "verify evidence",
            "make decision",
        ],
        score=8,
        evidence=[
            "E1",
            "E2",
        ],
        cost=2,
    )

    assert candidate.path == [
        "verify evidence",
        "make decision",
    ]

    assert candidate.score == 8

    assert candidate.evidence == [
        "E1",
        "E2",
    ]

    assert candidate.cost == 2


def test_candidate_has_safe_defaults():
    candidate = Candidate()

    assert candidate.path == []
    assert candidate.score == 0
    assert candidate.evidence == []
    assert candidate.cost == 0


def test_candidate_rejects_invalid_path():
    with pytest.raises(TypeError):
        Candidate(
            path="not-a-list",
            score=1,
            evidence=[],
            cost=0,
        )


def test_candidate_rejects_non_string_path_items():
    with pytest.raises(TypeError):
        Candidate(
            path=[
                "valid",
                123,
            ],
            score=1,
            evidence=[],
            cost=0,
        )


def test_candidate_rejects_negative_cost():
    with pytest.raises(ValueError):
        Candidate(
            path=["step"],
            score=1,
            evidence=[],
            cost=-1,
        )


def test_candidate_is_immutable():
    candidate = Candidate(
        path=["step"],
        score=5,
        evidence=["E1"],
        cost=1,
    )

    with pytest.raises(AttributeError):
        candidate.score = 10


def test_search_returns_structured_result():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
    )

    assert isinstance(
        result,
        SearchResult,
    )


def test_search_returns_initial_candidate():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
    )

    assert result.best_candidate.path == [
        "make a safe decision"
    ]

    assert result.best_candidate.score == 0
    assert result.best_candidate.evidence == []
    assert result.best_candidate.cost == 0


def test_search_starts_with_zero_expansions():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
    )

    assert result.expanded_count == 0
    assert result.depth_reached == 0


def test_zero_depth_is_a_terminal_boundary():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=0,
    )

    assert result.budget_exhausted is True


def test_invalid_width_is_rejected():
    with pytest.raises(ValueError):
        search(
            goal="make a safe decision",
            width=0,
            depth=2,
        )


def test_invalid_depth_is_rejected():
    with pytest.raises(ValueError):
        search(
            goal="make a safe decision",
            width=2,
            depth=-1,
        )


def test_empty_goal_is_rejected():
    with pytest.raises(ValueError):
        search(
            goal="",
            width=2,
            depth=2,
        )