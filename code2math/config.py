"""Configuration helpers for Code2Math."""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class PipelineConfig:
    evolve_model: str
    verify_model: str
    api_base: str | None = None
    api_key: str | None = None
    qwen_api_ak: str | None = None
    qwen_api_sk: str | None = None
    qwen_thinking_url: str | None = None
    qwen_instruct_url: str | None = None


def load_config(dotenv_path: str | None = None) -> PipelineConfig:
    """Load model configuration from environment variables."""
    load_dotenv(dotenv_path=dotenv_path)
    evolve_model = os.getenv("EVOLVE_MODEL")
    verify_model = os.getenv("VERIFY_MODEL")
    if not evolve_model:
        raise ValueError("Missing EVOLVE_MODEL")
    if not verify_model:
        raise ValueError("Missing VERIFY_MODEL")
    return PipelineConfig(
        evolve_model=evolve_model,
        verify_model=verify_model,
        api_base=os.getenv("URL"),
        api_key=os.getenv("KEY"),
        qwen_api_ak=os.getenv("API_AK"),
        qwen_api_sk=os.getenv("API_SK"),
        qwen_thinking_url=os.getenv("QWEN_THINKING_URL"),
        qwen_instruct_url=os.getenv("QWEN_INSTRUCT_URL"),
    )


def model_label(model_name: str) -> str:
    """Return a filesystem-friendly model label."""
    if model_name == "deepseek-chat":
        return "deepseek-v3.2"
    return model_name.replace("/", "_").replace(":", "_")
