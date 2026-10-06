import argparse
import json
from pathlib import Path
from typing import Any

from .search import search


def load_problem(
    input_path: Path,
) -> dict[str, Any]:
    """Load and validate a problem JSON file."""

    if not input_path.exists():
        raise ValueError(
            f"input file does not exist: {input_path}"
        )

    try:
        data = json.loads(
            input_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"invalid JSON: {exc.msg}"
        ) from exc

    if not isinstance(data, dict):
        raise ValueError(
            "input must be a JSON object"
        )

    goal = data.get("goal")

    if not isinstance(goal, str):
        raise ValueError(
            "input must contain a string goal"
        )

    if not goal.strip():
        raise ValueError(
            "goal must not be empty"
        )

    width = data.get("width", 2)
    depth = data.get("depth", 2)

    return {
        "goal": goal,
        "width": width,
        "depth": depth,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run the bounded Tree of Thought search."
        )
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    search_parser = subparsers.add_parser(
        "search",
        help="Run bounded search.",
    )

    search_parser.add_argument(
        "--input",
        required=True,
        help="Problem JSON file.",
    )

    search_parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file.",
    )

    args = parser.parse_args()

    if args.command != "search":
        parser.error(
            "unsupported command"
        )

    try:
        problem = load_problem(
            Path(args.input)
        )

        result = search(
            goal=problem["goal"],
            width=problem["width"],
            depth=problem["depth"],
            expand=True,
        )

        rejected_candidates = [
            {
                "path": item.path,
                "score": item.score,
                "reason": item.reason,
                "evidence": item.evidence,
            }
            for item in result.rejected_candidates
        ]

        output = {
            "best_candidate": {
                "path": result.best_candidate.path,
                "score": result.best_candidate.score,
                "evidence": result.best_candidate.evidence,
                "cost": result.best_candidate.cost,
            },
            "search_budget": {
                "expanded_count": (
                    result.expanded_count
                ),
                "depth_reached": (
                    result.depth_reached
                ),
                "budget_exhausted": (
                    result.budget_exhausted
                ),
                "width": result.width,
                "depth": result.depth_limit,
                "rejected_count": (
                    result.rejected_count
                ),
                "duplicate_count": (
                    result.duplicate_count
                ),
            },
            "rejected_candidates": (
                rejected_candidates
            ),
        }

        output_path = Path(
            args.output
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_path.write_text(
            json.dumps(
                output,
                indent=2,
                sort_keys=True,
            ),
            encoding="utf-8",
        )

    except (
        OSError,
        TypeError,
        ValueError,
    ) as exc:
        parser.error(str(exc))

    print(
        f"Search result written to {args.output}"
    )

    print(
        "Best path: "
        + " -> ".join(
            result.best_candidate.path
        )
    )

    print(
        f"Score: "
        f"{result.best_candidate.score}"
    )

    print(
        f"Expanded candidates: "
        f"{result.expanded_count}"
    )

    print(
        f"Rejected candidates: "
        f"{result.rejected_count}"
    )

    print(
        f"Duplicate states removed: "
        f"{result.duplicate_count}"
    )

    print(
        f"Depth reached: "
        f"{result.depth_reached}"
    )

    if result.rejected_candidates:
        print(
            "Rejection explanations:"
        )

        for item in result.rejected_candidates:
            print(
                " - "
                + " -> ".join(item.path)
                + ": "
                + item.reason
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())