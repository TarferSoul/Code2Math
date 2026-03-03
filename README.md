# Code2Math

Open-source evolved mathematical problems and prompt templates.

## Contents

### Evolved Problems (`evolved_problems/`)

This directory contains mathematical problems evolved from original test sets using different LLM models as evolvers. Each JSON file contains 100 problems with:
- Original problem
- Evolved (harder) problem variant
- Evolution and verification metadata
- Reference solutions

**Files:**
- `deepseek-v3.2_deepseek-v3.2_1_with_demo_6.json` - Evolved using DeepSeek-v3.2
- `deepseek-reasoner_deepseek-reasoner_1_with_demo_6.json` - Evolved using DeepSeek-Reasoner
- `gemini-3-pro-preview-thinking_gemini-3-pro-preview-thinking_1_with_demo_6.json` - Evolved using Gemini-3-Pro
- `kimi-k2-thinking_kimi-k2-thinking_1_with_demo_6.json` - Evolved using Kimi-K2-Thinking
- `doubao-seed-2-0-pro-260215_doubao-seed-2-0-pro-260215_1_with_demo_6.json` - Evolved using Doubao-Seed-2-Pro

Each problem entry contains:
```json
{
  "id": "0",
  "status": "success",
  "original_problem": {
    "problem_description": "...",
    "solution_steps": "...",
    "answer": "..."
  },
  "result_data": {
    "evolved_problem": "...",
    "evolved_solution": "...",
    "evolved_answer": "...",
    "solvability_verification": {...},
    "difficulty_verification": {...}
  }
}
```

### Prompt Templates (`prompts/`)

Contains the prompt templates used for:
- Problem evolution (creating harder variants)
- Solvability verification
- Difficulty verification
- Solution evaluation

## License

MIT License - See LICENSE file for details.

## Citation

If you use these evolved problems in your research, please cite:

```bibtex
@misc{code2math2025,
  title={Code2Math: Evolved Mathematical Problem Dataset},
  author={},
  year={2025},
  url={https://github.com/TarferSoul/Code2Math}
}
```
