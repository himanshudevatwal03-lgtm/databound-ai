"""
llm.py

Provider abstraction for the model that actually generates answers (spec
section 4: "Create a clean AI service interface so the LLM provider/model
can be changed later"). Mirrors the shape of app/services/embeddings.py —
one interface, swappable implementations, one factory function the rest
of the app calls.

AnthropicLLMProvider is the only implementation for now, using the
Messages API directly over HTTP rather than the SDK, to avoid adding a
dependency for what's a handful of straightforward request/response
fields. Swapping to a different provider (OpenAI, etc.) later means
adding one more class here and a branch in get_llm_provider() — nothing
else in the app needs to change, since app/services/qa.py only calls
generate().

Requires LLM_API_KEY to be set to a real Anthropic API key. If it isn't,
get_llm_provider() raises LLMNotConfiguredError rather than failing with
a confusing HTTP error deep inside a request — see how app/api/questions.py
turns that into a clear 503 response.
"""

from abc import ABC, abstractmethod

from app.config import settings


class LLMNotConfiguredError(Exception):
    """Raised when no LLM_API_KEY is set. Callers turn this into a clear
    503 response rather than letting a request fail with a raw connection
    or auth error partway through."""


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, system_prompt: str, user_message: str) -> str:
        """Returns the model's plain-text response."""
        ...


class AnthropicLLMProvider(LLMProvider):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model

    def generate(self, system_prompt: str, user_message: str) -> str:
        import httpx

        response = httpx.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self.model,
                "max_tokens": 1024,
                "system": system_prompt,
                "messages": [{"role": "user", "content": user_message}],
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        # Content is a list of blocks (text, tool_use, ...); we only ever
        # send plain text prompts here, so concatenating any text blocks
        # covers the response completely.
        return "".join(block["text"] for block in data["content"] if block["type"] == "text").strip()


def get_llm_provider() -> LLMProvider:
    if not settings.LLM_API_KEY:
        raise LLMNotConfiguredError(
            "LLM_API_KEY is not set. Question answering requires a real "
            "Anthropic API key — see the README's Environment Variables "
            "section."
        )
    return AnthropicLLMProvider(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL)
