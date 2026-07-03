"""Model construction for Code2Math pipelines."""

from __future__ import annotations

import base64

from smolagents import LiteLLMModel, OpenAIServerModel

from .config import PipelineConfig


def create_model(model_name: str, config: PipelineConfig):
    """Create a smolagents model from Code2Math environment config."""
    if "Qwen3-235B-A22B-Thinking" in model_name:
        if not (config.qwen_api_ak and config.qwen_api_sk and config.qwen_thinking_url):
            raise ValueError("Qwen thinking models require API_AK, API_SK, and QWEN_THINKING_URL")
        token = base64.b64encode(f"{config.qwen_api_ak}:{config.qwen_api_sk}".encode()).decode()
        return LiteLLMModel(
            model_id=model_name,
            api_base=config.qwen_thinking_url,
            headers={"Authorization": f"Basic {token}"},
            api_key="placeholder-key-for-client",
            timeout=300,
        )

    if "Qwen3-235B-A22B-Instruct" in model_name:
        if not (config.qwen_api_ak and config.qwen_api_sk and config.qwen_instruct_url):
            raise ValueError("Qwen instruct models require API_AK, API_SK, and QWEN_INSTRUCT_URL")
        token = base64.b64encode(f"{config.qwen_api_ak}:{config.qwen_api_sk}".encode()).decode()
        return LiteLLMModel(
            model_id=model_name,
            api_base=config.qwen_instruct_url,
            headers={"Authorization": f"Basic {token}"},
            api_key="placeholder-key-for-client",
            timeout=300,
        )

    if not (config.api_base and config.api_key):
        raise ValueError("OpenAI-compatible models require URL and KEY")
    return OpenAIServerModel(model_id=model_name, api_base=config.api_base, api_key=config.api_key, timeout=300)
