from dataclasses import dataclass

from .deduplication import deduplicate_candidates
from .models import Candidate
from .scoring import (
    evaluate_candidate,
    score_candidate,
)


@dataclass(frozen=True)
class RejectedCandidate:
    """Public explanation for a rejected candidate."""

    path: list[str]
    score: int
    reason: str
    evidence: list[str]

    def __post_init__(self) -> None:
        if not isinstance(self.path, list):
            raise TypeError(
                "path must be a list"
            )

        if not all(
            isinstance(step, str)
            for step in self.path
        ):
            raise TypeError(
                "path must contain strings"
            )

        if not isinstance(self.score, int):
            raise TypeError(
                "score must be an integer"
            )

        if not isinstance(self.reason, str):
            raise TypeError(
                "reason must be a string"
            )

        if not isinstance(self.evidence, list):
            raise TypeError(
                "evidence must be a list"
            )

        if not all(
            isinstance(item, str)
            for item in self.evidence
        ):
            raise TypeError(
                "evidence must contain strings"
            )


@dataclass(frozen=True)
class SearchResult:
    """Structured result returned by bounded search."""

    best_candidate: Candidate
    expanded_count: int
    depth_reached: int
    budget_exhausted: bool
    width: int
    depth_limit: int
    rejected_count: int = 0
    duplicate_count: int = 0
    rejected_candidates: tuple[
        RejectedCandidate,
        ...,
    ] = ()

    def __post_init__(self) -> None:
        if not isinstance(
            self.best_candidate,
            Candidate,
        ):
            raise TypeError(
                "best_candidate must be a Candidate"
            )

        if not isinstance(
            self.expanded_count,
            int,
        ):
            raise TypeError(
                "expanded_count must be an integer"
            )

        if self.expanded_count < 0:
            raise ValueError(
                "expanded_count must not be negative"
            )

        if not isinstance(
            self.depth_reached,
            int,
        ):
            raise TypeError(
                "depth_reached must be an integer"
            )

        if self.depth_reached < 0:
            raise ValueError(
                "depth_reached must not be negative"
            )

        if not isinstance(
            self.budget_exhausted,
            bool,
        ):
            raise TypeError(
                "budget_exhausted must be a boolean"
            )

        if not isinstance(
            self.width,
            int,
        ):
            raise TypeError(
                "width must be an integer"
            )

        if self.width < 1:
            raise ValueError(
                "width must be at least 1"
            )

        if not isinstance(
            self.depth_limit,
            int,
        ):
            raise TypeError(
                "depth_limit must be an integer"
            )

        if self.depth_limit < 0:
            raise ValueError(
                "depth_limit must not be negative"
            )

        if not isinstance(
            self.rejected_count,
            int,
        ):
            raise TypeError(
                "rejected_count must be an integer"
            )

        if self.rejected_count < 0:
            raise ValueError(
                "rejected_count must not be negative"
            )

        if not isinstance(
            self.duplicate_count,
            int,
        ):
            raise TypeError(
                "duplicate_count must be an integer"
            )

        if self.duplicate_count < 0:
            raise ValueError(
                "duplicate_count must not be negative"
            )

        if not isinstance(
            self.rejected_candidates,
            tuple,
        ):
            raise TypeError(
                "rejected_candidates must be a tuple"
            )

        if not all(
            isinstance(
                item,
                RejectedCandidate,
            )
            for item in self.rejected_candidates
        ):
            raise TypeError(
                "rejected_candidates must contain "
                "RejectedCandidate values"
            )


BRANCHES = [
    (
        "verify evidence",
        3,
        "evidence_checked",
    ),
    (
        "ask for missing input",
        2,
        "input_requested",
    ),
    (
        "make a bounded change",
        1,
        "change_bounded",
    ),
]


def expand_candidate(
    candidate: Candidate,
) -> list[Candidate]:
    """
    Generate candidate branches.

    The branch score stored here is only a temporary
    value. The safety-aware scoring layer recalculates
    the final score before candidates enter the next
    search frontier.
    """

    if not isinstance(
        candidate,
        Candidate,
    ):
        raise TypeError(
            "candidate must be a Candidate"
        )

    expanded: list[Candidate] = []

    for (
        action,
        score_delta,
        evidence_id,
    ) in BRANCHES:
        expanded.append(
            Candidate(
                path=[
                    *candidate.path,
                    action,
                ],
                score=(
                    candidate.score
                    + score_delta
                ),
                evidence=[
                    *candidate.evidence,
                    evidence_id,
                ],
                cost=candidate.cost + 1,
            )
        )

    return expanded


def select_top_candidates(
    candidates: list[Candidate],
    width: int,
) -> list[Candidate]:
    """Keep only the highest-scoring candidates."""

    if not isinstance(
        candidates,
        list,
    ):
        raise TypeError(
            "candidates must be a list"
        )

    if not isinstance(
        width,
        int,
    ):
        raise TypeError(
            "width must be an integer"
        )

    if width < 1:
        raise ValueError(
            "width must be at least 1"
        )

    ordered = sorted(
        candidates,
        key=lambda candidate: (
            -candidate.score,
            candidate.cost,
            tuple(candidate.path),
        ),
    )

    return ordered[:width]


def score_and_filter_with_explanations(
    candidates: list[Candidate],
) -> tuple[
    list[Candidate],
    int,
    tuple[RejectedCandidate, ...],
]:
    """
    Score candidates and reject unsafe candidates.

    Returns:
        (
            safe_scored_candidates,
            rejected_count,
            rejection_explanations,
        )
    """

    if not isinstance(
        candidates,
        list,
    ):
        raise TypeError(
            "candidates must be a list"
        )

    safe: list[Candidate] = []
    rejected: list[RejectedCandidate] = []

    for candidate in candidates:
        evaluation = evaluate_candidate(
            candidate
        )

        if not evaluation.safe:
            rejected.append(
                RejectedCandidate(
                    path=list(candidate.path),
                    score=evaluation.total_score,
                    reason=(
                        evaluation.rejection_reason
                        or "candidate rejected"
                    ),
                    evidence=list(
                        candidate.evidence
                    ),
                )
            )
            continue

        safe.append(
            score_candidate(candidate)
        )

    return (
        safe,
        len(rejected),
        tuple(rejected),
    )


def score_and_filter(
    candidates: list[Candidate],
) -> tuple[list[Candidate], int]:
    """
    Preserve the Task 3 two-value contract.

    Returns:
        (safe_scored_candidates, rejected_count)
    """

    safe, rejected_count, _ = (
        score_and_filter_with_explanations(
            candidates
        )
    )

    return safe, rejected_count


def deduplicate_and_count(
    candidates: list[Candidate],
) -> tuple[list[Candidate], int]:
    """
    Deduplicate candidate states and report how many
    equivalent states were removed.
    """

    if not isinstance(
        candidates,
        list,
    ):
        raise TypeError(
            "candidates must be a list"
        )

    unique = deduplicate_candidates(
        candidates
    )

    duplicate_count = (
        len(candidates) - len(unique)
    )

    return unique, duplicate_count


def search(
    goal: str,
    width: int = 2,
    depth: int = 2,
    expand: bool = False,
) -> SearchResult:
    """
    Run a bounded Tree of Thought search.

    Search order:

        expansion
        -> safety filtering
        -> deduplication
        -> scoring
        -> width selection

    Unsafe candidates are rejected before they can
    enter the next search depth.

    The returned result contains concise public
    explanations for rejected candidates.
    """

    if not isinstance(goal, str):
        raise TypeError(
            "goal must be a string"
        )

    goal = goal.strip()

    if not goal:
        raise ValueError(
            "goal must not be empty"
        )

    if not isinstance(width, int):
        raise TypeError(
            "width must be an integer"
        )

    if width < 1:
        raise ValueError(
            "width must be at least 1"
        )

    if not isinstance(depth, int):
        raise TypeError(
            "depth must be an integer"
        )

    if depth < 0:
        raise ValueError(
            "depth must not be negative"
        )

    if not isinstance(expand, bool):
        raise TypeError(
            "expand must be a boolean"
        )

    initial = Candidate(
        path=[goal],
        score=0,
        evidence=[],
        cost=0,
    )

    if not expand or depth == 0:
        return SearchResult(
            best_candidate=initial,
            expanded_count=0,
            depth_reached=0,
            budget_exhausted=(
                depth == 0
            ),
            width=width,
            depth_limit=depth,
            rejected_count=0,
            duplicate_count=0,
            rejected_candidates=(),
        )

    frontier = [initial]
    expanded_count = 0
    rejected_count = 0
    duplicate_count = 0
    depth_reached = 0

    rejected_candidates: list[
        RejectedCandidate
    ] = []

    for current_depth in range(
        1,
        depth + 1,
    ):
        expanded: list[Candidate] = []

        for candidate in frontier:
            children = expand_candidate(
                candidate
            )

            expanded.extend(children)

            expanded_count += len(children)

        (
            safe_children,
            rejected,
            rejection_explanations,
        ) = score_and_filter_with_explanations(
            expanded
        )

        rejected_count += rejected

        rejected_candidates.extend(
            rejection_explanations
        )

        unique_children, duplicates = (
            deduplicate_and_count(
                safe_children
            )
        )

        duplicate_count += duplicates

        frontier = select_top_candidates(
            unique_children,
            width,
        )

        depth_reached = current_depth

        if not frontier:
            break

    if not frontier:
        return SearchResult(
            best_candidate=initial,
            expanded_count=expanded_count,
            depth_reached=depth_reached,
            budget_exhausted=True,
            width=width,
            depth_limit=depth,
            rejected_count=rejected_count,
            duplicate_count=duplicate_count,
            rejected_candidates=tuple(
                rejected_candidates
            ),
        )

    best_candidate = select_top_candidates(
        frontier,
        1,
    )[0]

    return SearchResult(
        best_candidate=best_candidate,
        expanded_count=expanded_count,
        depth_reached=depth_reached,
        budget_exhausted=(
            depth_reached >= depth
        ),
        width=width,
        depth_limit=depth,
        rejected_count=rejected_count,
        duplicate_count=duplicate_count,
        rejected_candidates=tuple(
            rejected_candidates
        ),
    )