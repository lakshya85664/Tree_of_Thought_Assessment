from dataclasses import dataclass, field


@dataclass(frozen=True)
class Candidate:
    """
    Represents one candidate reasoning path.

    path:
        Ordered actions/steps taken by this candidate.

    score:
        Numeric score representing the quality of the candidate.

    evidence:
        Evidence collected or used by the candidate.

    cost:
        Bounded search cost consumed by the candidate.
    """

    path: list[str] = field(default_factory=list)
    score: int = 0
    evidence: list[str] = field(default_factory=list)
    cost: int = 0

    def __post_init__(self) -> None:
        if not isinstance(self.path, list):
            raise TypeError("path must be a list")

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

        if not isinstance(self.cost, int):
            raise TypeError(
                "cost must be an integer"
            )

        if self.cost < 0:
            raise ValueError(
                "cost must not be negative"
            )