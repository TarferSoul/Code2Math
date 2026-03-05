# Code2Math

**Can Your Code Agent Effectively Evolve Math Problems Through Exploration?**

Open-source evolved mathematical problems, demonstrations, and prompt templates from the Code2Math project.

## 📄 Paper

**Code2Math: Can Your Code Agent Effectively Evolve Math Problems Through Exploration?**

[Dadi Guo](https://github.com/), [Yuejin Xie](https://github.com/), Qingyu Liu, Jiayu Liu, Zhiyuan Fan, Qihan Ren, Shuai Shao, Tianyi Zhou, Dongrui Liu, Yi R. Fung

📖 [arXiv:2603.03202](https://arxiv.org/abs/2603.03202)

## 📦 Contents

### 1. Evolved Problems (`evolved_problems/`)

Mathematical problems evolved from original test sets using different LLM models as evolvers. Each JSON file contains 100 problems with evolution and verification metadata.

**Available Datasets:**
- `deepseek-v3.2_deepseek-v3.2_1_with_demo_6.json` - Evolved using DeepSeek-v3.2
- `deepseek-reasoner_deepseek-reasoner_1_with_demo_6.json` - Evolved using DeepSeek-Reasoner
- `gemini-3-pro-preview-thinking_gemini-3-pro-preview-thinking_1_with_demo_6.json` - Evolved using Gemini-3-Pro
- `kimi-k2-thinking_kimi-k2-thinking_1_with_demo_6.json` - Evolved using Kimi-K2-Thinking
- `doubao-seed-2-0-pro-260215_doubao-seed-2-0-pro-260215_1_with_demo_6.json` - Evolved using Doubao-Seed-2-Pro

**Entry Format:**
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

### 2. Math Demonstrations (`math_demonstrations/`)

Example problem adaptations organized by mathematical category:
- **Algebra** - Algebraic problem variations
- **Algorithm** - Algorithmic problem variants
- **Calculus** - Calculus problem evolutions
- **Combinatorics** - Combinatorial problem adaptations
- **Number Sequences** - Sequence problem variations

Each category contains JSON files with original and evolved problem pairs demonstrating the evolution methodology.

### 3. Prompt Templates (`prompts/`)

Core prompt template (`prompt_math.py`) for:
- Problem evolution (creating harder variants)
- Solvability verification
- Difficulty assessment
- Solution evaluation

## 📖 Citation

If you use these evolved problems or demonstrations in your research, please cite:

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

## 📜 License

MIT License - See [LICENSE](LICENSE) file for details.

## 🔗 Links

- Paper: [arXiv:2603.03202](https://arxiv.org/abs/2603.03202)
- GitHub: [https://github.com/TarferSoul/Code2Math](https://github.com/TarferSoul/Code2Math)

## 🤝 Contributing

We welcome contributions! Please feel free to submit issues or pull requests.

---

Made with ❤️ by the Code2Math Team
