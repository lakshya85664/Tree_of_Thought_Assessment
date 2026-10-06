from dataclasses import dataclass

from .models import Candidate


@dataclass(frozen=True)
class CandidateEvaluation:
    """Safety and scoring evaluation for one candidate."""

    goal_progress: int
    evidence_coverage: int
    risk: int
    total_score: int
    safe: bool
    rejection_reason: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("goal_progress", self.goal_progress),
            ("evidence_coverage", self.evidence_coverage),
            ("risk", self.risk),
            ("total_score", self.total_score),
        ):
            if not isinstance(value, int):
                raise TypeError(
                    f"{name} must be an integer"
                )

        if self.goal_progress < 0:
            raise ValueError(
                "goal_progress must not be negative"
            )

        if self.evidence_coverage < 0:
            raise ValueError(
                "evidence_coverage must not be negative"
            )

        if self.risk < 0:
            raise ValueError(
                "risk must not be negative"
            )

        if not isinstance(self.safe, bool):
            raise TypeError(
                "safe must be a boolean"
            )

        if (
            self.rejection_reason is not None
            and not isinstance(
                self.rejection_reason,
                str,
            )
        ):
            raise TypeError(
                "rejection_reason must be a string or None"
            )


def evaluate_candidate(
    candidate: Candidate,
) -> CandidateEvaluation:
    """
    Evaluate a candidate using goal progress,
    evidence coverage, and risk.

    Score formula:

        total_score =
            goal_progress
            + evidence_coverage
            - risk

    Candidates containing an explicitly unsafe action
    are rejected regardless of their raw score.
    """

    if not isinstance(
        candidate,
        Candidate,
    ):
        raise TypeError(
            "candidate must be a Candidate"
        )

    goal_progress = len(
        candidate.path
    )

    evidence_coverage = len(
        set(candidate.evidence)
    )

    unsafe_actions = {
        "execute unrestricted action",
        "bypass safety check",
        "expose secret",
        "delete without approval",
    }

    candidate_actions = {
        step.lower().strip()
        for step in candidate.path
    }

    detected_unsafe_actions = (
        candidate_actions
        & unsafe_actions
    )

    risk = (
        10
        if detected_unsafe_actions
        else 0
    )

    total_score = (
        goal_progress
        + evidence_coverage
        - risk
    )

    if detected_unsafe_actions:
        return CandidateEvaluation(
            goal_progress=goal_progress,
            evidence_coverage=evidence_coverage,
            risk=risk,
            total_score=total_score,
            safe=False,
            rejection_reason=(
                "candidate contains an unsafe action"
            ),
        )

    return CandidateEvaluation(
        goal_progress=goal_progress,
        evidence_coverage=evidence_coverage,
        risk=risk,
        total_score=total_score,
        safe=True,
        rejection_reason=None,
    )


def score_candidate(
    candidate: Candidate,
) -> Candidate:
    """
    Return a candidate with its score updated using
    the safety-aware evaluation.

    Unsafe candidates are rejected by raising ValueError.
    """

    evaluation = evaluate_candidate(
        candidate
    )

    if not evaluation.safe:
        raise ValueError(
            evaluation.rejection_reason
            or "candidate rejected as unsafe"
        )

    return Candidate(
        path=list(candidate.path),
        score=evaluation.total_score,
        evidence=list(candidate.evidence),
        cost=candidate.cost,
    )


def safe_candidates(
    candidates: list[Candidate],
) -> list[Candidate]:
    """Return only candidates that pass the safety check."""

    if not isinstance(
        candidates,
        list,
    ):
        raise TypeError(
            "candidates must be a list"
        )

    result: list[Candidate] = []

    for candidate in candidates:
        evaluation = evaluate_candidate(
            candidate
        )

        if evaluation.safe:
            result.append(
                score_candidate(candidate)
            )

    return result