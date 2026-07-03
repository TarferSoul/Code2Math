"""Run the Code2Math pipeline with the interleaved-thinking backend."""

from __future__ import annotations

import argparse

from code2math import Code2MathPipeline
from code2math.config import load_config
from code2math.data import load_original_problems


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="original_problems.json")
    parser.add_argument("--output-dir", default="adapted_problems")
    parser.add_argument("--max-workers", type=int, default=5)
    parser.add_argument("--retry-max-round", type=int, default=1)
    parser.add_argument("--demo-num", type=int, default=6)
    parser.add_argument("--without-demonstrations", action="store_true")
    args = parser.parse_args()

    pipeline = Code2MathPipeline(
        original_problems=load_original_problems(args.input),
        config=load_config(),
        backend="interleaved",
        retry_max_round=args.retry_max_round,
        with_demonstrations=not args.without_demonstrations,
        demonstration_num=args.demo_num,
        output_dir=args.output_dir,
    )
    pipeline.run(max_workers=args.max_workers)
    print(f"Saved results to {pipeline.save_file}")


if __name__ == "__main__":
    main()
