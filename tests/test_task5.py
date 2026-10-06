import pytest

from thought_tree.models import Candidate
from thought_tree.search import (
    RejectedCandidate,
    score_and_filter_with_explanations,
    search,
)


def test_rejected_candidate_has_public_explanation():
    rejected = RejectedCandidate(
        path=[
            "verify evidence",
            "bypass safety check",
        ],
        score=-6,
        reason=(
            "candidate contains an unsafe action"
        ),
        evidence=[
            "evidence_checked",
        ],
    )

    assert rejected.path == [
        "verify evidence",
        "bypass safety check",
    ]

    assert rejected.score == -6

    assert rejected.reason == (
        "candidate contains an unsafe action"
    )

    assert rejected.evidence == [
        "evidence_checked"
    ]


def test_score_and_filter_returns_rejection_explanation():
    unsafe = Candidate(
        path=[
            "bypass safety check",
        ],
        score=100,
        evidence=["E1"],
        cost=1,
    )

    (
        safe,
        rejected_count,
        explanations,
    ) = score_and_filter_with_explanations(
        [unsafe]
    )

    assert safe == []
    assert rejected_count == 1
    assert len(explanations) == 1

    assert explanations[0].reason == (
        "candidate contains an unsafe action"
    )


def test_search_returns_best_safe_candidate():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
        expand=True,
    )

    assert result.best_candidate.path

    assert (
        "bypass safety check"
        not in result.best_candidate.path
    )

    assert result.best_candidate.score >= 0


def test_search_rejection_explanations_are_structured():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
        expand=True,
    )

    assert isinstance(
        result.rejected_candidates,
        tuple,
    )

    for item in result.rejected_candidates:
        assert isinstance(
            item,
            RejectedCandidate,
        )
        assert item.reason


def test_search_rejection_count_matches_explanations():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
        expand=True,
    )

    assert result.rejected_count == len(
        result.rejected_candidates
    )


def test_rejected_candidates_never_become_best():
    unsafe = Candidate(
        path=[
            "execute unrestricted action",
        ],
        score=999,
        evidence=["E1"],
        cost=1,
    )

    safe = Candidate(
        path=[
            "verify evidence",
        ],
        score=0,
        evidence=["E2"],
        cost=1,
    )

    (
        safe_results,
        rejected_count,
        explanations,
    ) = score_and_filter_with_explanations(
        [unsafe, safe]
    )

    assert rejected_count == 1
    assert len(explanations) == 1
    assert len(safe_results) == 1

    assert safe_results[0].path == [
        "verify evidence"
    ]


def test_search_result_explains_unsafe_path():
    unsafe = Candidate(
        path=[
            "verify evidence",
            "expose secret",
        ],
        score=100,
        evidence=["E1"],
        cost=2,
    )

    safe = Candidate(
        path=[
            "verify evidence",
            "make a bounded change",
        ],
        score=1,
        evidence=["E2"],
        cost=2,
    )

    (
        safe_results,
        rejected_count,
        explanations,
    ) = score_and_filter_with_explanations(
        [unsafe, safe]
    )

    assert rejected_count == 1

    assert safe_results[0].path == [
        "verify evidence",
        "make a bounded change",
    ]

    assert explanations[0].path == [
        "verify evidence",
        "expose secret",
    ]

    assert "unsafe" in (
        explanations[0].reason.lower()
    )


def test_rejected_candidate_validation():
    with pytest.raises(TypeError):
        RejectedCandidate(
            path="not-a-list",
            score=1,
            reason="reason",
            evidence=[],
        )


def test_rejected_candidate_requires_integer_score():
    with pytest.raises(TypeError):
        RejectedCandidate(
            path=[],
            score="high",
            reason="reason",
            evidence=[],
        )


def test_rejected_candidate_requires_reason():
    with pytest.raises(TypeError):
        RejectedCandidate(
            path=[],
            score=1,
            reason=None,
            evidence=[],
        )


def test_best_candidate_is_always_a_candidate():
    result = search(
        goal="make a safe decision",
        width=2,
        depth=2,
        expand=True,
    )

    assert isinstance(
        result.best_candidate,
        Candidate,
    )