"""Robust parsing helpers for LLM agent outputs."""

from __future__ import annotations

import ast
import json
import re
from typing import Any


def _as_text(output: Any) -> str:
    if isinstance(output, str):
        return output
    if hasattr(output, "to_raw"):
        try:
            return str(output.to_raw())
        except Exception:
            pass
    return str(output)


def parse_mapping(output: Any, required_keys: list[str]) -> dict:
    """Extract a dict containing required keys from strings or agent outputs."""
    if isinstance(output, dict) and all(key in output for key in required_keys):
        return output

    text = _as_text(output).strip()
    candidates = []
    candidates.extend(match.group(1).strip() for match in re.finditer(r"```(?:json|python)?\s*(.*?)```", text, re.S))
    if "FINAL_JSON:" in text:
        candidates.append(text.split("FINAL_JSON:")[-1].strip())
    candidates.append(text)

    decoder = json.JSONDecoder()
    for candidate in candidates:
        for start in [m.start() for m in re.finditer(r"[\{\[]", candidate)]:
            snippet = candidate[start:].strip()
            parsed = None
            try:
                parsed, _ = decoder.raw_decode(snippet)
            except Exception:
                end = max(snippet.rfind("}"), snippet.rfind("]"))
                if end != -1:
                    try:
                        parsed = ast.literal_eval(snippet[: end + 1])
                    except Exception:
                        parsed = None
            if isinstance(parsed, dict) and all(key in parsed for key in required_keys):
                return parsed

    raise ValueError(f"Could not parse required keys {required_keys} from output")


def pick_keys(mapping: dict, required_keys: list[str]) -> dict:
    missing = [key for key in required_keys if key not in mapping]
    if missing:
        raise ValueError(f"Missing required keys: {missing}")
    return {key: mapping[key] for key in required_keys}
