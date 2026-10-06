import pytest

from thought_tree.models import Candidate
from thought_tree.scoring import (
    CandidateEvaluation,
    evaluate_candidate,
    safe_candidates,
    score_candidate,
)
from thought_tree.search import score_and_filter


def test_evaluation_returns_structured_result():
    candidate = Candidate(
        path=["verify evidence"],
        score=0,
        evidence=["evidence_checked"],
        cost=1,
    )

    result = evaluate_candidate(
        candidate
    )

    assert isinstance(
        result,
        CandidateEvaluation,
    )


def test_goal_progress_is_based_on_path():
    candidate = Candidate(
        path=[
            "step one",
            "step two",
            "step three",
        ],
        score=0,
        evidence=[],
        cost=3,
    )

    result = evaluate_candidate(
        candidate
    )

    assert result.goal_progress == 3


def test_evidence_coverage_counts_unique_evidence():
    candidate = Candidate(
        path=["verify evidence"],
        score=0,
        evidence=[
            "E1",
            "E1",
            "E2",
        ],
        cost=1,
    )

    result = evaluate_candidate(
        candidate
    )

    assert result.evidence_coverage == 2


def test_total_score_uses_progress_evidence_and_risk():
    candidate = Candidate(
        path=[
            "step one",
            "step two",
        ],
        score=0,
        evidence=[
            "E1",
            "E2",
        ],
        cost=2,
    )

    result = evaluate_candidate(
        candidate
    )

    assert result.goal_progress == 2
    assert result.evidence_coverage == 2
    assert result.risk == 0
    assert result.total_score == 4
    assert result.safe is True


def test_unsafe_candidate_is_rejected():
    candidate = Candidate(
        path=[
            "verify evidence",
            "bypass safety check",
        ],
        score=100,
        evidence=[
            "E1",
            "E2",
        ],
        cost=2,
    )

    result = evaluate_candidate(
        candidate
    )

    assert result.safe is False
    assert result.risk == 10
    assert result.rejection_reason is not None


def test_score_candidate_updates_score():
    candidate = Candidate(
        path=[
            "verify evidence",
        ],
        score=0,
        evidence=[
            "evidence_checked",
        ],
        cost=1,
    )

    scored = score_candidate(
        candidate
    )

    assert scored.score == 2
    assert scored.path == candidate.path
    assert scored.evidence == candidate.evidence
    assert scored.cost == candidate.cost


def test_score_candidate_rejects_unsafe_work():
    candidate = Candidate(
        path=[
            "execute unrestricted action",
        ],
        score=100,
        evidence=[
            "E1",
        ],
        cost=1,
    )

    with pytest.raises(ValueError):
        score_candidate(candidate)


def test_safe_candidates_filters_unsafe_work():
    safe = Candidate(
        path=["verify evidence"],
        score=0,
        evidence=["E1"],
        cost=1,
    )

    unsafe = Candidate(
        path=["expose secret"],
        score=100,
        evidence=["E2"],
        cost=1,
    )

    result = safe_candidates(
        [safe, unsafe]
    )

    assert len(result) == 1
    assert result[0].path == [
        "verify evidence"
    ]
    assert result[0].score == 2


def test_search_scoring_filters_unsafe_candidates():
    safe = Candidate(
        path=["verify evidence"],
        score=0,
        evidence=["E1"],
        cost=1,
    )

    unsafe = Candidate(
        path=[
            "execute unrestricted action"
        ],
        score=100,
        evidence=["E2"],
        cost=1,
    )

    result, rejected = score_and_filter(
        [safe, unsafe]
    )

    assert rejected == 1

    assert len(result) == 1

    assert result[0].path == [
        "verify evidence"
    ]

    assert result[0].score == 2