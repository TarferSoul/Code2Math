# Code2Math

**Can Your Code Agent Effectively Evolve Math Problems Through Exploration?**

This repository contains the public Code2Math artifacts: seed math problems, evolved problem sets, demonstration examples, prompt templates, and the code-agent pipelines used to evolve and verify high-difficulty mathematical problems.

Paper: [arXiv:2603.03202](https://arxiv.org/abs/2603.03202)

## Contents

- `original_problems.json` - 100 seed math problems.
- `evolved_problems/` - evolved problem sets from the main model runs.
- `math_demonstrations/` - few-shot demonstrations grouped by math category.
- `prompts/prompt_math.py` - prompt templates for evolution, verification, solving, and evaluation.
- `code2math/` - reusable Python package for the code-agent pipelines.
- `scripts/` - command-line entry points for running the two full pipelines.

## The Two Full Code-Agent Pipelines

Code2Math uses the same three-stage workflow in both variants:

1. `ProblemEvolver` proposes a harder version of a seed problem.
2. `SolvabilityVerifier` checks that the evolved problem is well-formed and solvable.
3. `DifficultyVerifier` checks that the new problem meaningfully increases the burden of discovery.

The repository exposes two complete code-agent backends for this workflow:

### 1. Standard CodeAgent Backend

Run with:

```bash
python scripts/run_code_agent_pipeline.py --max-workers 5
```

This uses the standard `smolagents.CodeAgent` execution model with authorized Python imports for mathematical exploration.

### 2. Interleaved-Thinking Backend

Run with:

```bash
python scripts/run_interleaved_pipeline.py --max-workers 5
```

This backend keeps an OpenAI-style `messages + tool_calls + tool responses` loop and writes the full trajectory to `messages.json`. It preserves reasoning content when the model provider returns it, which is useful for inspecting thinking-model runs and retry feedback.

The interleaved backend is implemented in this repository as a small compatibility layer, so users do not need to install a patched `smolagents` fork.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your model endpoint and API key:

```dotenv
URL=https://your-openai-compatible-endpoint/v1
KEY=your_api_key
EVOLVE_MODEL=your-evolver-model
VERIFY_MODEL=your-verifier-model
```

Qwen-style Basic-auth endpoints are also supported through `API_AK`, `API_SK`, `QWEN_THINKING_URL`, and `QWEN_INSTRUCT_URL`.

## Output

By default, results are written under:

```text
adapted_problems/
  codeagent/
  interleaved/
```

Agent logs are written under `logs/`. These generated outputs are intentionally ignored by git.

Each result entry records:

- pipeline status
- failure stage, if any
- evolved problem, solution, and answer
- solvability-verifier output
- difficulty-verifier output

## Data Format

Seed problems use:

```json
{
  "problem_description": "...",
  "solution_steps": "...",
  "answer": "..."
}
```

Evolved problems use:

```json
{
  "status": "success",
  "result_data": {
    "status": true,
    "new_problem": {
      "new_problem": "...",
      "new_solution_steps": "...",
      "new_answer": "..."
    },
    "solvability_verifier_output": {},
    "difficulty_verifier_output": {}
  }
}
```

## Notes

- Do not commit `.env`, logs, or generated run outputs.
- The single-turn no-code pipeline used in later experiments is not part of this open-source package; this release focuses on the two full code-agent workflows.
- The prompts and demonstrations are included so runs can be reproduced or adapted with other OpenAI-compatible model providers.

## Citation

If you use Code2Math data, prompts, or code, please cite:

```bibtex
@misc{guo2026code2mathcodeagenteffectively,
      title={Code2Math: Can Your Code Agent Effectively Evolve Math Problems Through Exploration?},
      author={Dadi Guo and Yuejin Xie and Qingyu Liu and Jiayu Liu and Zhiyuan Fan and Qihan Ren and Shuai Shao and Tianyi Zhou and Dongrui Liu and Yi R. Fung},
      year={2026},
      eprint={2603.03202},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2603.03202},
}
```

## License

MIT License. See [LICENSE](LICENSE).
