from .models import Candidate


def state_key(
    candidate: Candidate,
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """
    Return the canonical identity of a candidate state.

    Score and cost are intentionally excluded because
    state identity represents the logical path and
    evidence, not the current evaluation metadata.
    """

    if not isinstance(
        candidate,
        Candidate,
    ):
        raise TypeError(
            "candidate must be a Candidate"
        )

    return (
        tuple(candidate.path),
        tuple(candidate.evidence),
    )


def deduplicate_candidates(
    candidates: list[Candidate],
) -> list[Candidate]:
    """
    Remove equivalent candidate states.

    The first occurrence of each state is retained.
    """

    if not isinstance(
        candidates,
        list,
    ):
        raise TypeError(
            "candidates must be a list"
        )

    unique: list[Candidate] = []
    seen: set[
        tuple[
            tuple[str, ...],
            tuple[str, ...],
        ]
    ] = set()

    for candidate in candidates:
        key = state_key(candidate)

        if key in seen:
            continue

        seen.add(key)
        unique.append(candidate)

    return unique