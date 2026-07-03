"""Tool helpers used by the Code2Math agents."""

from __future__ import annotations

import json
from typing import Any

from smolagents import Tool


class FlexibleFinalAnswerTool(Tool):
    name = "final_answer"
    description = "Provides a final answer to the given problem."
    inputs = {"answer": {"type": "any", "description": "The final answer to the problem"}}
    output_type = "any"
    skip_forward_signature_validation = True

    def forward(self, answer: Any) -> Any:
        if isinstance(answer, dict):
            return answer
        if isinstance(answer, str):
            stripped = answer.strip()
            if stripped.startswith(("{", "[")) and stripped.endswith(("}", "]")):
                try:
                    return json.loads(stripped)
                except Exception:
                    return answer
        return answer
