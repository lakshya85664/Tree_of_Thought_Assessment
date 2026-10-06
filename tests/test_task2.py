import pytest

from thought_tree.models import Candidate
from thought_tree.search import (
    expand_candidate,
    search,
    select_top_candidates,
)


def test_candidate_expands_into_multiple_branches():
    candidate = Candidate(
        path=["make a safe decision"],
        score=0,
        evidence=[],
        cost=0,
    )

    children = expand_candidate(
        candidate
    )

    assert len(children) == 3


def test_expansion_extends_path():
    candidate = Candidate(
        path=["make a safe decision"],
        score=0,
        evidence=[],
        cost=0,
    )

    children = expand_candidate(
        candidate
    )

    for child in children:
        assert len(child.path) == 2

        assert child.path[0] == (
            "make a safe decision"
        )


def test_expansion_increases_cost():
    candidate = Candidate(
        path=["make a safe decision"],
        score=0,
        evidence=[],
        cost=0,
    )

    children = expand_candidate(
        candidate
    )

    for child in children:
        assert child.cost == 1


def test_top_candidates_are_bounded_by_width():
    candidates = [
        Candidate(
            path=[
                f"candidate-{index}"
            ],
            score=index,
            evidence=[],
            cost=1,
        )
        for index in range(5)
    ]

    selected = select_top_candidates(
        candidates,
        width=2,
    )

    assert len(selected) == 2

    assert [
        candidate.score
        for candidate in selected
    ] == [4, 3]


def test_search_expands_only_bounded_frontier():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=1,
        expand=True,
    )

    assert result.depth_reached == 1

    assert result.expanded_count == 3

    assert result.width == 2

    assert len(
        result.best_candidate.path
    ) == 2


def test_search_keeps_width_bounded_at_each_depth():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
        expand=True,
    )

    assert result.depth_reached == 2

    # First depth:
    # 1 candidate -> 3 branches.
    #
    # Only 2 survive because width = 2.
    #
    # Second depth:
    # 2 candidates -> 6 branches.
    #
    # Total expansions = 3 + 6 = 9.
    assert result.expanded_count == 9

    assert result.width == 2


def test_expansion_rejects_invalid_candidate():
    with pytest.raises(TypeError):
        expand_candidate(
            "not-a-candidate"
        )


def test_width_must_be_positive():
    with pytest.raises(ValueError):
        select_top_candidates(
            [],
            width=0,
        )