import pytest

from thought_tree.deduplication import (
    deduplicate_candidates,
    state_key,
)
from thought_tree.models import Candidate
from thought_tree.search import (
    deduplicate_and_count,
    search,
)


def test_state_key_uses_path_and_evidence():
    candidate = Candidate(
        path=[
            "verify evidence",
            "make decision",
        ],
        score=10,
        evidence=[
            "E1",
            "E2",
        ],
        cost=2,
    )

    assert state_key(candidate) == (
        (
            "verify evidence",
            "make decision",
        ),
        (
            "E1",
            "E2",
        ),
    )


def test_same_state_has_same_key():
    first = Candidate(
        path=["verify evidence"],
        score=2,
        evidence=["E1"],
        cost=1,
    )

    second = Candidate(
        path=["verify evidence"],
        score=99,
        evidence=["E1"],
        cost=10,
    )

    assert state_key(first) == state_key(
        second
    )


def test_deduplication_removes_equivalent_states():
    first = Candidate(
        path=["verify evidence"],
        score=2,
        evidence=["E1"],
        cost=1,
    )

    duplicate = Candidate(
        path=["verify evidence"],
        score=8,
        evidence=["E1"],
        cost=4,
    )

    result = deduplicate_candidates(
        [first, duplicate]
    )

    assert len(result) == 1
    assert result[0] == first


def test_deduplication_preserves_distinct_paths():
    candidates = [
        Candidate(
            path=["verify evidence"],
            score=2,
            evidence=["E1"],
            cost=1,
        ),
        Candidate(
            path=["ask for missing input"],
            score=2,
            evidence=["E1"],
            cost=1,
        ),
    ]

    result = deduplicate_candidates(
        candidates
    )

    assert len(result) == 2


def test_deduplication_preserves_distinct_evidence():
    candidates = [
        Candidate(
            path=["verify evidence"],
            score=2,
            evidence=["E1"],
            cost=1,
        ),
        Candidate(
            path=["verify evidence"],
            score=2,
            evidence=["E2"],
            cost=1,
        ),
    ]

    result = deduplicate_candidates(
        candidates
    )

    assert len(result) == 2


def test_empty_candidate_list_is_supported():
    assert deduplicate_candidates([]) == []


def test_invalid_candidate_list_is_rejected():
    with pytest.raises(TypeError):
        deduplicate_candidates(
            "not-a-list"
        )


def test_invalid_candidate_is_rejected():
    with pytest.raises(TypeError):
        state_key(
            "not-a-candidate"
        )


def test_search_result_tracks_duplicate_count():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
        expand=True,
    )

    assert result.duplicate_count == 0


def test_deduplicate_and_count_reports_removed_states():
    first = Candidate(
        path=["verify evidence"],
        score=2,
        evidence=["E1"],
        cost=1,
    )

    duplicate = Candidate(
        path=["verify evidence"],
        score=99,
        evidence=["E1"],
        cost=10,
    )

    unique, duplicate_count = (
        deduplicate_and_count(
            [first, duplicate]
        )
    )

    assert unique == [first]
    assert duplicate_count == 1


def test_deduplicate_and_count_keeps_distinct_states():
    candidates = [
        Candidate(
            path=["step one"],
            score=1,
            evidence=["E1"],
            cost=1,
        ),
        Candidate(
            path=["step two"],
            score=2,
            evidence=["E2"],
            cost=1,
        ),
    ]

    unique, duplicate_count = (
        deduplicate_and_count(
            candidates
        )
    )

    assert unique == candidates
    assert duplicate_count == 0


def test_search_preserves_bounded_width_after_deduplication():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
        expand=True,
    )

    assert result.width == 2
    assert result.depth_reached == 2
    assert result.expanded_count == 9