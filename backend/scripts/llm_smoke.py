"""MANUAL LLM smoke test — ONE real request. NOT part of the pytest suite (no paid call runs
in CI). Run it by hand after configuring a provider in the environment to confirm the wiring
end to end:

    DOCURA_LLM_PROVIDER=openai_compatible \\
    DOCURA_LLM_MODEL=gpt-4o-mini \\
    DOCURA_LLM_API_KEY=sk-... \\
    .venv/Scripts/python.exe -m scripts.llm_smoke "what do I need for a voter ID"

It sends exactly one message through the real provider selected by the settings, prints the
structured intent, and reports whether the deterministic fallback had to be used. It prints no
secrets. If no LLM is configured it says so and exits without any network call.
"""

from __future__ import annotations

import sys

from app.core.config import Settings
from app.services.chatbot.intent import select_intent_provider


def main() -> int:
    message = sys.argv[1] if len(sys.argv) > 1 else "what documents do I need for a voter ID"
    settings = Settings()  # reads DOCURA_* from the environment / .env
    if not settings.llm_configured:
        print("No LLM configured (set DOCURA_LLM_PROVIDER, DOCURA_LLM_MODEL, DOCURA_LLM_API_KEY).")
        print("Nothing sent; the chatbot would use the deterministic provider.")
        return 0

    print(f"provider={settings.llm_provider.value} model={settings.llm_model} (key hidden)")
    print(f"message: {message!r}")
    intent = select_intent_provider(settings).classify(message)  # ONE real request
    used_fallback = ":fallback:" in intent.method
    print("--- result ---")
    print(f"task_type       : {intent.task_type.value}")
    print(f"confidence      : {intent.confidence}")
    print(f"entities        : {intent.entities}")
    print(f"reason          : {intent.reason}")
    print(f"method          : {intent.method}")
    print(f"used fallback   : {used_fallback}")
    if used_fallback:
        print("NOTE: the LLM request failed and the deterministic provider answered instead.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
