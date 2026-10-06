# Topic 5: Implement Tree of Thought in Code

## Project Overview

This project implements a deterministic, bounded Tree of Thought search system in Python. The system represents alternative reasoning states as typed `Candidate` objects, expands only a bounded frontier, evaluates candidates for goal progress, evidence coverage, and risk, rejects unsafe work, removes equivalent states, and returns the best safe candidate.

The implementation is intentionally local and deterministic. It uses synthetic data only and does not require credentials, external APIs, or network access.

## Assessment Tasks

### Task 1 — Candidate State
Implemented `Candidate` with `path`, `score`, `evidence`, and `cost`, with typed validation for malformed values.

### Task 2 — Bounded Expansion
Implemented candidate branching and bounded frontier selection using configurable width and depth limits. Only the retained frontier is expanded at the next depth.

### Task 3 — Scoring and Safety
Candidates are evaluated using goal progress, unique evidence coverage, and risk.

`total_score = goal_progress + evidence_coverage - risk`

Explicitly unsafe actions are rejected regardless of raw score.

### Task 4 — Deduplication
Equivalent states are identified using a canonical key based on path and evidence. Duplicate states are removed before frontier selection.

### Task 5 — Best Safe Candidate and Rejection Explanations
The search returns the best safe candidate and structured public explanations for rejected candidates. These explanations contain path, score, evidence, and a concise safety reason rather than private chain-of-thought.

## Search Pipeline

```text
Candidate Expansion
        ↓
Safety Evaluation
        ↓
Reject Unsafe Candidates
        ↓
Deduplicate Equivalent States
        ↓
Score Remaining Candidates
        ↓
Keep Top WIDTH
        ↓
Next Depth
```

## Required CLI

```cmd
python -m thought_tree.cli search --input examples\problem.json --output outputs\best_path.json
```

Verified result:
- Best path: `make a safe decision -> ask for missing input -> make a bounded change`
- Score: `5`
- Cost: `2`
- Expanded candidates: `9`
- Rejected candidates: `0`
- Duplicate states removed: `0`
- Depth reached: `2`

## Evidence

Generate deterministic evidence with:

```cmd
python -m thought_tree.evidence
```

Artifacts:

```text
evidence/
├── traces/
│   └── search_trace.json
└── state_snapshots/
    ├── initial_state.json
    ├── depth_1_frontier.json
    └── depth_2_frontier.json
```

The evidence scenario deliberately includes a synthetic unsafe candidate so the safety rejection mechanism is observable. This is separate from the normal CLI example, which contains no unsafe branch.

## Testing

Final verified regression:

```text
53 passed
```

The suite covers candidate validation, bounded expansion, width/depth limits, scoring, evidence coverage, unsafe candidate rejection, state deduplication, rejection explanations, best-candidate selection, boundary conditions, and established search contracts.

## Project Structure

```text
Tree_of_Thought_Assessment/
├── thought_tree/
│   ├── __init__.py
│   ├── models.py
│   ├── search.py
│   ├── scoring.py
│   ├── deduplication.py
│   ├── evidence.py
│   └── cli.py
├── tests/
│   ├── test_task1.py
│   ├── test_task2.py
│   ├── test_task3.py
│   ├── test_task4.py
│   └── test_task5.py
├── examples/
│   └── problem.json
├── evidence/
│   ├── traces/
│   └── state_snapshots/
├── outputs/
│   └── best_path.json
├── requirements.txt
├── pyproject.toml
└── .gitignore
```

## Reflection

Implementing this Tree of Thought assessment helped me understand how bounded search can turn multiple candidate reasoning paths into a controlled software workflow. The most important lesson was that generating alternatives is not enough; the search must also control width and depth so computation remains predictable. I implemented a typed candidate state containing the path, score, evidence, and cost, which made the search state explicit and testable.

The scoring stage showed how multiple factors can be combined into a deterministic decision rule. Goal progress and evidence coverage reward useful candidates, while risk prevents unsafe work from being selected. I also learned that safety should be enforced before a candidate can enter the next frontier, rather than treating safety as an afterthought.

Deduplication was another important part of the implementation. Equivalent logical states can otherwise consume search capacity repeatedly. Using a canonical state key based on path and evidence provided a simple deterministic mechanism for removing those duplicates before frontier selection.

A practical challenge was maintaining compatibility while extending the implementation. Task 5 required richer rejection explanations, but Task 3 already established a two-value scoring function contract. Instead of breaking that contract, I introduced a separate detailed scoring function and kept the original interface unchanged.

Finally, the evidence generator demonstrated the value of observable state snapshots and traces. The implementation can now show bounded expansion, safety rejection, deduplication statistics, and final selection using synthetic local data. This made the final system easier to test, explain, and verify without exposing private chain-of-thought.
