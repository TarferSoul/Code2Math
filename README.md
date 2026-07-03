<div align="center">

# Code2Math

### Can Your Code Agent Effectively Evolve Math Problems Through Exploration?

[![arXiv](https://img.shields.io/badge/arXiv-2603.03202-b31b1b.svg)](https://arxiv.org/abs/2603.03202)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](requirements.txt)

</div>

![Code2Math overview](assets/code2math-overview.png)

Code2Math is a code-agent framework for synthesizing harder mathematical problems through executable exploration. Starting from seed problems, an evolution agent searches for deeper variants with Python tools, while two verifier agents filter candidates for mathematical solvability and meaningful difficulty increase.

This repository contains the public Code2Math data, prompt templates, and two full code-agent pipeline implementations.

## News

- **Code released:** full code-agent pipelines are now included under `code2math/`.
- **Data released:** seed problems, evolved problem sets, demonstrations, and prompt templates are available in this repository.
- **Paper:** [Code2Math: Can Your Code Agent Effectively Evolve Math Problems Through Exploration?](https://arxiv.org/abs/2603.03202)

## Authors

Dadi Guo*, Yuejin Xie*, Qingyu Liu*, Weixian Huang*, Jiayu Liu, Zhiyuan Fan, Qihan Ren, Shuai Shao, Tianyi Zhou, Jianjie Feng, Wenze Su, Yujiu Yang, Dongrui Liu (corresponding author), Yi R. (May) Fung (corresponding author)

*Equal contribution.

**Affiliations:** Hong Kong University of Science and Technology, Tsinghua University, Zhejiang University, Nanjing Tech University, Shanghai Jiao Tong University, University of Michigan, Independent Researcher.

## Repository Layout

```text
Code2Math/
  code2math/                 # reusable pipeline package
  scripts/                   # runnable entry points
  prompts/                   # prompt templates
  math_demonstrations/       # few-shot evolution demonstrations
  evolved_problems/          # released evolved problem sets
  original_problems.json     # 100 seed problems
```

## Method

Code2Math decomposes problem evolution into three agents:

1. **Evolution Agent** - proposes harder variants of seed problems through thought, empirical inquiry, and Python-backed exploration.
2. **Solvability Verification Agent** - rejects ill-formed, inconsistent, or unsolvable candidates.
3. **Difficulty Verification Agent** - checks whether the evolved problem increases conceptual discovery burden rather than only adding computation.

The code tools support symbolic computation, graph algorithms, combinatorial enumeration, numerical checks, and constraint-style exploration.

## Full Code-Agent Pipelines

We release two complete implementations of the three-stage workflow.

| Backend | Entry Point | What It Does |
| --- | --- | --- |
| Standard CodeAgent | `scripts/run_code_agent_pipeline.py` | Uses the standard `smolagents.CodeAgent` execution loop. |
| Interleaved Thinking | `scripts/run_interleaved_pipeline.py` | Preserves OpenAI-style `messages`, `tool_calls`, tool responses, and returned reasoning content in `messages.json`. |

### Standard CodeAgent Backend

```bash
python scripts/run_code_agent_pipeline.py --max-workers 5
```

### Interleaved-Thinking Backend

```bash
python scripts/run_interleaved_pipeline.py --max-workers 5
```

The interleaved backend is implemented as a small compatibility layer in this repository, so users do not need to install a patched `smolagents` fork.

## Implementation Note

The implementation builds on and follows the design of [Hugging Face smolagents](https://github.com/huggingface/smolagents), especially its `CodeAgent`, tool abstraction, Python execution tool, and OpenAI-compatible model wrappers. Code2Math adds the math-evolution prompts, three-agent orchestration, output parsing, released datasets, and an interleaved-thinking backend for preserving tool-call trajectories from thinking-model runs.

## Example

![Code-driven problem evolution example](assets/code2math-figure1.png)

## Installation

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with an OpenAI-compatible endpoint:

```dotenv
URL=https://your-openai-compatible-endpoint/v1
KEY=your_api_key
EVOLVE_MODEL=your-evolver-model
VERIFY_MODEL=your-verifier-model
```

Qwen-style Basic-auth endpoints are also supported through `API_AK`, `API_SK`, `QWEN_THINKING_URL`, and `QWEN_INSTRUCT_URL`.

## Outputs

By default, generated results are written under:

```text
adapted_problems/
  codeagent/
  interleaved/
```

Agent logs are written under `logs/`. These generated outputs are ignored by git.

Each result entry records the pipeline status, failure stage if any, evolved problem, verifier outputs, and final difficulty judgment.

## Data Format

Seed problems:

```json
{
  "problem_description": "...",
  "solution_steps": "...",
  "answer": "..."
}
```

Evolved problem records:

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

## Scope

This release focuses on the two full code-agent workflows. The later single-turn no-code pipeline used in internal experiments is intentionally not included.

Please do not commit `.env`, logs, or generated run outputs.

## Citation

If you use Code2Math data, prompts, or code, please cite:

```bibtex
@misc{guo2026code2mathcodeagenteffectively,
      title={Code2Math: Can Your Code Agent Effectively Evolve Math Problems Through Exploration?},
      author={Dadi Guo and Yuejin Xie and Qingyu Liu and Weixian Huang and Jiayu Liu and Zhiyuan Fan and Qihan Ren and Shuai Shao and Tianyi Zhou and Jianjie Feng and Wenze Su and Yujiu Yang and Dongrui Liu and Yi R. Fung},
      year={2026},
      eprint={2603.03202},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2603.03202},
}
```

## License

MIT License. See [LICENSE](LICENSE).
