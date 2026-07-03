"""Math evolution and verification agents."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Literal

from rich.console import Console
from smolagents import CodeAgent
from smolagents.monitoring import AgentLogger, LogLevel

from prompts.prompt_math import (
    difficulty_prompt_template_with_demonstrations,
    evolve_prompt_template_with_demonstrations,
    solvability_prompt_template,
)

from .config import PipelineConfig, model_label
from .interleaved import InterleavedThinkingAgent, python_tool
from .models import create_model
from .parsing import parse_mapping, pick_keys
from .tools import FlexibleFinalAnswerTool


Backend = Literal["codeagent", "interleaved"]


AUTHORIZED_IMPORTS = [
    "json",
    "math",
    "random",
    "statistics",
    "datetime",
    "itertools",
    "collections",
    "fractions",
    "decimal",
    "re",
    "functools",
    "mpmath",
    "numpy.*",
    "scipy.*",
    "pandas.*",
    "openpyxl",
    "sympy.*",
    "z3.*",
    "networkx.*",
    "shapely.*",
    "PIL",
]


def _demonstrations(example_num: int, base_dir: str = "math_demonstrations") -> str:
    import json

    chunks = []
    for demo_file in sorted(os.path.join(root, name) for root, _, files in os.walk(base_dir) for name in files if name.endswith(".json")):
        if len(chunks) >= example_num:
            break
        with open(demo_file, "r", encoding="utf-8") as f:
            chunks.append(json.dumps(json.load(f), ensure_ascii=False, indent=2))
    return "\n\n".join(chunks)


def _format_prompt(template: str, demonstration_num: int, with_demonstrations: bool) -> str:
    if with_demonstrations:
        return template.replace("{demonstrations}", _demonstrations(demonstration_num))
    return template


@dataclass
class AgentSettings:
    config: PipelineConfig
    backend: Backend
    retry_max_round: int = 1
    with_demonstrations: bool = True
    demonstration_num: int = 6
    max_steps: int = 30


class MathAgentBase:
    def __init__(self, model_name: str, system_prompt: str, log_root: str, settings: AgentSettings):
        self.model_name = model_name
        self.system_prompt = system_prompt
        self.log_root = log_root
        self.settings = settings
        self.model = create_model(model_name, settings.config)

    def _log_file_path(self, problem_id: int) -> str:
        return os.path.join(self.log_root, model_label(self.model_name), f"task_{problem_id}", "task_log.log")

    def _code_agent(self, log_file_path: str) -> CodeAgent:
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        file_handle = open(log_file_path, "w", encoding="utf-8")
        logger = AgentLogger(console=Console(file=file_handle, record=True), level=LogLevel.INFO)
        agent = CodeAgent(
            model=self.model,
            tools=[FlexibleFinalAnswerTool()],
            add_base_tools=True,
            additional_authorized_imports=AUTHORIZED_IMPORTS,
            max_print_outputs_length=20000,
            logger=logger,
            verbosity_level=LogLevel.ERROR,
            max_steps=self.settings.max_steps,
        )
        agent.prompt_templates["system_prompt"] = self.system_prompt
        return agent

    def _interleaved_agent(self) -> InterleavedThinkingAgent:
        return InterleavedThinkingAgent(
            model=self.model,
            tools=[python_tool(AUTHORIZED_IMPORTS), FlexibleFinalAnswerTool()],
            system_prompt=self.system_prompt,
            max_steps=self.settings.max_steps,
        )

    def run_agent(self, user_prompt: str, problem_id: int, required_keys: list[str]) -> dict:
        log_file_path = self._log_file_path(problem_id)
        last_error: Exception | None = None

        if self.settings.backend == "interleaved":
            agent = self._interleaved_agent()
            for retry in range(self.settings.retry_max_round):
                try:
                    output = agent.run(user_prompt, log_file_path=log_file_path)
                    return pick_keys(parse_mapping(output, required_keys), required_keys)
                except Exception as exc:
                    last_error = exc
                    if retry < self.settings.retry_max_round - 1:
                        agent.append_feedback(
                            "Your previous response did not match the required output schema. "
                            f"Return a final_answer dictionary with exactly these keys: {required_keys}."
                        )
            raise last_error or RuntimeError("interleaved agent failed")

        for _ in range(self.settings.retry_max_round):
            try:
                output = self._code_agent(log_file_path).run(user_prompt)
                return pick_keys(parse_mapping(output, required_keys), required_keys)
            except Exception as exc:
                last_error = exc
        raise last_error or RuntimeError("code agent failed")


class ProblemEvolver(MathAgentBase):
    def __init__(self, settings: AgentSettings):
        super().__init__(
            settings.config.evolve_model,
            _format_prompt(evolve_prompt_template_with_demonstrations, settings.demonstration_num, settings.with_demonstrations),
            os.path.join("logs", "evolution"),
            settings,
        )

    def evolve(self, original_problem: dict, problem_id: int) -> dict:
        prompt = f"""
The description of the original problem is:
{original_problem["problem_description"]}
The solution steps are:
{original_problem["solution_steps"]}
The answer is: {original_problem["answer"]}

Return a Python dictionary via final_answer with exactly:
- new_problem
- new_solution_steps
- new_answer
"""
        return self.run_agent(prompt, problem_id, ["new_problem", "new_solution_steps", "new_answer"])


class SolvabilityVerifier(MathAgentBase):
    def __init__(self, settings: AgentSettings):
        super().__init__(
            settings.config.verify_model,
            solvability_prompt_template,
            os.path.join("logs", "solvability"),
            settings,
        )

    def verify(self, new_problem: dict, problem_id: int) -> tuple[bool, dict]:
        prompt = f"""
The description of this problem is:
{new_problem["new_problem"]}
The tentative solution steps are:
{new_problem["new_solution_steps"]}
The answer is: {new_problem["new_answer"]}

Return a Python dictionary via final_answer with exactly:
- status: PASS or FAIL
- reason
"""
        output = self.run_agent(prompt, problem_id, ["status", "reason"])
        return output.get("status") == "PASS", output


class DifficultyVerifier(MathAgentBase):
    def __init__(self, settings: AgentSettings):
        super().__init__(
            settings.config.verify_model,
            _format_prompt(
                difficulty_prompt_template_with_demonstrations,
                settings.demonstration_num,
                settings.with_demonstrations,
            ),
            os.path.join("logs", "difficulty"),
            settings,
        )

    def verify(self, original_problem: dict, new_problem: dict, problem_id: int) -> tuple[bool, dict]:
        prompt = f"""
The description of the original problem is:
{original_problem["problem_description"]}
The tentative solution steps of the original problem are:
{original_problem["solution_steps"]}
The answer of the original problem is: {original_problem["answer"]}

The description of the new problem is:
{new_problem["new_problem"]}
The tentative solution steps of the new problem are:
{new_problem["new_solution_steps"]}
The answer of the new problem is: {new_problem["new_answer"]}

Return a Python dictionary via final_answer with exactly:
- status: PASS or FAIL
- score: integer from 1 to 5
- reason
"""
        output = self.run_agent(prompt, problem_id, ["status", "score", "reason"])
        return output.get("status") == "PASS", output
