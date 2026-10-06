import json
from pathlib import Path
from typing import Any

from .deduplication import deduplicate_candidates
from .models import Candidate
from .scoring import evaluate_candidate, score_candidate
from .search import expand_candidate


def candidate_to_dict(
    candidate: Candidate,
) -> dict[str, Any]:
    """Convert a candidate into public evidence data."""

    return {
        "path": list(candidate.path),
        "score": candidate.score,
        "evidence": list(candidate.evidence),
        "cost": candidate.cost,
    }


def write_json(
    path: Path,
    data: Any,
) -> None:
    """Write deterministic JSON evidence."""

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    path.write_text(
        json.dumps(
            data,
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )


def generate_evidence(
    output_root: Path,
) -> None:
    """
    Generate deterministic Tree of Thought evidence.

    The evidence contains:
    - initial state
    - depth snapshots
    - safety rejection
    - deduplication
    - final best candidate
    """

    traces_dir = (
        output_root / "traces"
    )

    snapshots_dir = (
        output_root / "state_snapshots"
    )

    initial = Candidate(
        path=["make a safe decision"],
        score=0,
        evidence=[],
        cost=0,
    )

    write_json(
        snapshots_dir / "initial_state.json",
        {
            "depth": 0,
            "frontier": [
                candidate_to_dict(initial)
            ],
        },
    )

    frontier = [initial]
    trace: list[dict[str, Any]] = []

    trace.append(
        {
            "event": "initial_state",
            "depth": 0,
            "candidate_count": 1,
        }
    )

    for depth in range(1, 3):
        expanded: list[Candidate] = []

        for candidate in frontier:
            expanded.extend(
                expand_candidate(candidate)
            )

        unsafe = Candidate(
            path=[
                *frontier[0].path,
                "bypass safety check",
            ],
            score=999,
            evidence=[
                *frontier[0].evidence,
                "unsafe_test_evidence",
            ],
            cost=frontier[0].cost + 1,
        )

        expanded.append(unsafe)

        safe_candidates: list[Candidate] = []
        rejected_candidates: list[
            dict[str, Any]
        ] = []

        for candidate in expanded:
            evaluation = evaluate_candidate(
                candidate
            )

            if not evaluation.safe:
                rejected_candidates.append(
                    {
                        "path": list(
                            candidate.path
                        ),
                        "score": (
                            evaluation.total_score
                        ),
                        "reason": (
                            evaluation.rejection_reason
                            or "candidate rejected"
                        ),
                        "evidence": list(
                            candidate.evidence
                        ),
                    }
                )
                continue

            safe_candidates.append(
                score_candidate(candidate)
            )

        unique_candidates = (
            deduplicate_candidates(
                safe_candidates
            )
        )

        frontier = sorted(
            unique_candidates,
            key=lambda candidate: (
                -candidate.score,
                candidate.cost,
                tuple(candidate.path),
            ),
        )[:2]

        write_json(
            snapshots_dir
            / f"depth_{depth}_frontier.json",
            {
                "depth": depth,
                "expanded_count": len(
                    expanded
                ),
                "rejected_count": len(
                    rejected_candidates
                ),
                "duplicate_count": (
                    len(safe_candidates)
                    - len(unique_candidates)
                ),
                "rejected_candidates": (
                    rejected_candidates
                ),
                "frontier": [
                    candidate_to_dict(
                        candidate
                    )
                    for candidate in frontier
                ],
            },
        )

        trace.append(
            {
                "event": "depth_complete",
                "depth": depth,
                "expanded_count": len(
                    expanded
                ),
                "rejected_count": len(
                    rejected_candidates
                ),
                "duplicate_count": (
                    len(safe_candidates)
                    - len(unique_candidates)
                ),
                "frontier_count": len(
                    frontier
                ),
            }
        )

    best = frontier[0]

    trace.append(
        {
            "event": "search_complete",
            "depth": 2,
            "best_candidate": (
                candidate_to_dict(best)
            ),
        }
    )

    write_json(
        traces_dir / "search_trace.json",
        {
            "assessment": (
                "Topic 5: Implement Tree of Thought in Code"
            ),
            "bounded_width": 2,
            "bounded_depth": 2,
            "events": trace,
        },
    )


def main() -> None:
    """Generate evidence in the repository."""

    generate_evidence(
        Path("evidence")
    )

    print(
        "Evidence generated successfully."
    )


if __name__ == "__main__":
    main()