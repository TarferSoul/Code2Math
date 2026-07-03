"""Code2Math code-agent pipelines."""

__all__ = ["Code2MathPipeline"]


def __getattr__(name):
    if name == "Code2MathPipeline":
        from .framework import Code2MathPipeline

        return Code2MathPipeline
    raise AttributeError(name)
