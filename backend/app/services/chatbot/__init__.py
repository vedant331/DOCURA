"""DOCURA chatbot orchestration layer (additive).

A controlled orchestration layer over the existing DOCURA services — NOT a generic LLM agent.
It understands a small, controlled set of tasks (``intent``), consults a requirements seam
(``requirements``) and the user's own record/documents to compute readiness (``readiness``),
and composes a structured reply (``orchestrator``). It never mutates domain data, never submits
a form, never guesses, and is not coupled to any LLM vendor. When no live model is configured,
intent understanding falls back to a transparent deterministic provider, and the requirements
seam honestly reports "unavailable" rather than inventing application requirements.
"""
