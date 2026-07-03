"""Interleaved thinking agent backend.

This module keeps the Code2Math-specific interleaved tool-calling loop in this
repository instead of requiring users to install a patched smolagents fork.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

from rich.console import Console
from rich.panel import Panel
from smolagents import PythonInterpreterTool
from smolagents.models import get_tool_json_schema


class InterleavedThinkingAgent:
    """Minimal OpenAI-style tool-calling agent with persistent messages.

    It preserves assistant messages, reasoning content when available, tool
    calls, and tool responses in ``messages.json``. The same instance can be
    run again after appending feedback to continue the conversation.
    """

    def __init__(self, model, tools: list[Any], system_prompt: str, max_steps: int = 30):
        self.model = model
        self.tools = {tool.name: tool for tool in tools}
        self.system_prompt = system_prompt
        self.max_steps = max_steps
        self.messages: list[dict | Any] = []
        self._original_task: str | None = None
        self._messages_metadata: dict[str, Any] = {}
        self._messages_json_file: str | None = None
        self._log_file_path: str | None = None

        if not hasattr(model, "client"):
            raise TypeError("InterleavedThinkingAgent requires a model with an OpenAI-compatible client attribute")
        self.client = model.client

    def append_feedback(self, feedback: str) -> None:
        self.messages.append({"role": "user", "content": feedback})
        self._update_messages_json()

    def run(self, task: str, log_file_path: str | None = None) -> Any:
        self._setup_logging(task=task, log_file_path=log_file_path)

        if not self.messages:
            self.messages = [{"role": "system", "content": self.system_prompt}]

        if self._original_task is None:
            self._original_task = task
            self.messages.append({"role": "user", "content": task})
            self._messages_metadata.update(
                {
                    "task": task,
                    "model": getattr(self.model, "model_id", "unknown"),
                    "started_at": datetime.now().isoformat(),
                    "messages": [],
                }
            )
        else:
            self._messages_metadata["retry_count"] = self._messages_metadata.get("retry_count", 0) + 1
            self._messages_metadata["last_retry_at"] = datetime.now().isoformat()

        self._update_messages_json()
        console = Console(file=open(self._log_file_path, "a", encoding="utf-8"), width=120) if self._log_file_path else None
        try:
            if console:
                console.print(Panel(task if self._original_task == task else "Retry with feedback", title="Task"))

            for step in range(1, self.max_steps + 1):
                completion = self.client.chat.completions.create(
                    model=self.model.model_id,
                    messages=self._serializable_messages(),
                    tools=[get_tool_json_schema(tool) for tool in self.tools.values()],
                )
                message = completion.choices[0].message
                self.messages.append(message)
                self._update_messages_json()

                reasoning = getattr(message, "reasoning_content", None)
                if console and reasoning:
                    console.rule(f"Reasoning {step}")
                    console.print(reasoning)

                if console and message.content:
                    console.rule(f"Assistant {step}")
                    console.print(message.content)

                if not message.tool_calls:
                    self._mark_complete(message.content)
                    return message.content

                tool_outputs = self._process_tool_calls(message.tool_calls)
                self.messages.extend(tool_outputs)
                self._update_messages_json()

                final_calls = [tc for tc in message.tool_calls if tc.function.name == "final_answer"]
                if final_calls:
                    final_value = final_calls[0].function.arguments
                    self._mark_complete(final_value)
                    return final_value

            raise RuntimeError(f"InterleavedThinkingAgent exceeded max_steps={self.max_steps}")
        finally:
            if console:
                console.file.close()

    def _setup_logging(self, task: str, log_file_path: str | None) -> None:
        if log_file_path:
            log_dir = os.path.dirname(log_file_path)
            os.makedirs(log_dir, exist_ok=True)
            self._log_file_path = log_file_path
            self._messages_json_file = os.path.join(log_dir, "messages.json")
            return

        model_id = getattr(self.model, "model_id", "model").replace("/", "_").replace(":", "_")
        log_dir = os.path.join("logs", "interleaved_thinking", model_id, datetime.now().strftime("task_%Y%m%d_%H%M%S"))
        os.makedirs(log_dir, exist_ok=True)
        self._log_file_path = os.path.join(log_dir, "run.log")
        self._messages_json_file = os.path.join(log_dir, "messages.json")

    def _serializable_messages(self) -> list[dict]:
        messages = []
        for msg in self.messages:
            if isinstance(msg, dict):
                messages.append(msg)
            elif hasattr(msg, "model_dump"):
                data = msg.model_dump(exclude_none=True)
                reasoning = getattr(msg, "reasoning_content", None)
                if reasoning:
                    data["reasoning_content"] = reasoning
                messages.append(data)
        return messages

    def _update_messages_json(self) -> None:
        if not self._messages_json_file:
            return
        self._messages_metadata["messages"] = self._serializable_messages()
        with open(self._messages_json_file, "w", encoding="utf-8") as f:
            json.dump(self._messages_metadata, f, ensure_ascii=False, indent=2)

    def _process_tool_calls(self, tool_calls) -> list[dict]:
        outputs = []
        for tool_call in tool_calls:
            func_name = tool_call.function.name
            arguments_str = tool_call.function.arguments
            tool = self.tools.get(func_name)
            if tool is None:
                result = f"Error: unknown tool {func_name!r}"
            else:
                try:
                    if func_name == "final_answer":
                        result = tool(arguments_str)
                    else:
                        arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                        result = tool(**arguments)
                except Exception as exc:
                    result = f"Error: {type(exc).__name__}: {exc}"
            outputs.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": str(result),
                }
            )
        return outputs

    def _mark_complete(self, final_answer: Any) -> None:
        self._messages_metadata["finished_at"] = datetime.now().isoformat()
        self._messages_metadata["status"] = "completed"
        self._messages_metadata["final_answer"] = final_answer
        self._update_messages_json()


def python_tool(authorized_imports: list[str]) -> PythonInterpreterTool:
    return PythonInterpreterTool(authorized_imports=authorized_imports)
