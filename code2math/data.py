"""Dataset loading utilities."""

from __future__ import annotations

import json
from pathlib import Path


def load_original_problems(path: str | Path = "original_problems.json") -> list[dict]:
    """Load seed math problems from a JSON file."""
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError(f"Expected a list of problems in {path}")
    return data


def load_previous_round(path: str | Path) -> list[dict]:
    """Load successful evolved problems as seed problems for a later round."""
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    seeds: list[dict] = []
    for item in data:
        result = item.get("result_data") if isinstance(item, dict) else None
        new_problem = result.get("new_problem") if isinstance(result, dict) else None
        if isinstance(new_problem, dict):
            seeds.append(
                {
                    "problem_description": new_problem["new_problem"],
                    "solution_steps": new_problem["new_solution_steps"],
                    "answer": new_problem["new_answer"],
                }
            )
    return seeds
