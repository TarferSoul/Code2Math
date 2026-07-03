"""Three-stage Code2Math pipeline."""

from __future__ import annotations

import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from .agents import AgentSettings, Backend, DifficultyVerifier, ProblemEvolver, SolvabilityVerifier
from .config import PipelineConfig, model_label


class Code2MathPipeline:
    """Run problem evolution, solvability verification, and difficulty verification."""

    def __init__(
        self,
        original_problems: list[dict],
        config: PipelineConfig,
        backend: Backend,
        retry_max_round: int = 1,
        with_demonstrations: bool = True,
        demonstration_num: int = 6,
        max_failure_count: int = 20,
        output_dir: str | Path = "adapted_problems",
    ):
        self.original_problems = original_problems
        self.config = config
        self.backend = backend
        self.max_failure_count = max_failure_count
        self.settings = AgentSettings(
            config=config,
            backend=backend,
            retry_max_round=retry_max_round,
            with_demonstrations=with_demonstrations,
            demonstration_num=demonstration_num,
        )
        output_dir = Path(output_dir) / backend
        output_dir.mkdir(parents=True, exist_ok=True)
        self.save_file = output_dir / (
            f"{model_label(config.evolve_model)}_{model_label(config.verify_model)}_"
            f"{'with' if with_demonstrations else 'without'}_demo_{demonstration_num}.json"
        )
        self.file_lock = threading.Lock()

    def run_problem(self, problem_id: int) -> dict:
        original_problem = self.original_problems[problem_id]
        evolver = ProblemEvolver(self.settings)
        solvability_verifier = SolvabilityVerifier(self.settings)
        difficulty_verifier = DifficultyVerifier(self.settings)

        try:
            new_problem = evolver.evolve(original_problem, problem_id)
        except Exception as exc:
            return self._failure("evolution", None, exc)

        try:
            solvable, solvability_output = solvability_verifier.verify(new_problem, problem_id)
        except Exception as exc:
            return self._failure("solvability", new_problem, exc)
        if not solvable:
            return {
                "status": False,
                "failure_stage": "solvability",
                "new_problem": new_problem,
                "solvability": False,
                "solvability_verifier_output": solvability_output,
                "difficulty": None,
                "difficulty_verifier_output": None,
            }

        try:
            difficult, difficulty_output = difficulty_verifier.verify(original_problem, new_problem, problem_id)
        except Exception as exc:
            return {
                **self._failure("difficulty", new_problem, exc),
                "solvability": True,
                "solvability_verifier_output": solvability_output,
            }

        return {
            "status": bool(difficult),
            "failure_stage": None if difficult else "difficulty",
            "new_problem": new_problem,
            "solvability": True,
            "solvability_verifier_output": solvability_output,
            "difficulty": bool(difficult),
            "difficulty_verifier_output": difficulty_output,
        }

    def run(self, max_workers: int = 5) -> list[dict]:
        progress = self._load_or_create_progress()
        self._save_progress(progress)

        while True:
            pending = []
            for idx, item in enumerate(progress):
                if item["status"] == "success":
                    continue
                total_failures = sum(item["failure_counts"].values())
                if total_failures >= self.max_failure_count:
                    item["status"] = "failed_max_retries"
                    continue
                pending.append(idx)

            if not pending:
                break

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_idx = {executor.submit(self.run_problem, idx): idx for idx in pending}
                for future in as_completed(future_to_idx):
                    idx = future_to_idx[future]
                    result = future.result()
                    item = progress[idx]
                    item["result_data"] = result
                    if result["status"] is True:
                        item["status"] = "success"
                    else:
                        item["status"] = f"failed_{result.get('failure_stage') or 'unknown'}"
                        stage = result.get("failure_stage")
                        if stage in item["failure_counts"]:
                            item["failure_counts"][stage] += 1
                    self._save_progress(progress)

        return progress

    def _failure(self, stage: str, new_problem: dict | None, exc: Exception) -> dict:
        return {
            "status": False,
            "failure_stage": stage,
            "new_problem": new_problem,
            "solvability": None,
            "solvability_verifier_output": {"status": "FAIL", "reason": f"{type(exc).__name__}: {exc}"},
            "difficulty": None,
            "difficulty_verifier_output": None,
        }

    def _load_or_create_progress(self) -> list[dict]:
        if self.save_file.exists():
            with self.save_file.open("r", encoding="utf-8") as f:
                progress = json.load(f)
        else:
            progress = []

        target_len = len(self.original_problems)
        if len(progress) < target_len:
            progress.extend([None] * (target_len - len(progress)))
        elif len(progress) > target_len:
            progress = progress[:target_len]

        for idx, item in enumerate(progress):
            if not isinstance(item, dict) or "failure_counts" not in item:
                progress[idx] = {
                    "status": "pending",
                    "result_data": None,
                    "failure_counts": {"evolution": 0, "solvability": 0, "difficulty": 0},
                }
        return progress

    def _save_progress(self, progress: list[dict]) -> None:
        with self.file_lock:
            os.makedirs(self.save_file.parent, exist_ok=True)
            with self.save_file.open("w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
