"""
embeddings.py

Provider abstraction for turning text into vectors (spec section 4:
"Create a configurable embedding service... should NOT be tightly coupled
to one provider"). Two implementations exist behind one interface:

  LocalHashingEmbeddingProvider (default) — deterministic, dependency-free,
    no API key or network call required. It works the moment the app is
    deployed, which matters a lot for a portfolio project someone else
    should be able to spin up without first acquiring paid API credits.
    The tradeoff is real and worth stating plainly: this captures LEXICAL
    similarity (shared words) via a hashing trick, not learned semantic
    meaning. "cat" and "feline" will NOT be seen as related — a real
    embedding model would catch that; this won't. It's good enough to
    prove the full retrieval pipeline end-to-end (chunk -> embed -> store
    -> nearest-neighbor search -> relevant chunks come back) and to
    exercise the anti-hallucination behavior arriving in Phase 6 with
    real, deterministic, reproducible test data.

  OpenAIEmbeddingProvider — real semantic embeddings via OpenAI's API.
    Swap to this by setting EMBEDDING_PROVIDER=openai and LLM_API_KEY to
    an OpenAI key. Requesting `dimensions` explicitly keeps the output
    size consistent with EMBEDDING_DIMENSIONS regardless of which
    provider generated it, since text-embedding-3 models support
    truncating their output to a requested size.

get_embedding_provider() is the one function the rest of the app calls —
nothing outside this file needs to know which implementation is active.
"""

import hashlib
import math
import re
from abc import ABC, abstractmethod

from app.config import settings


class EmbeddingProvider(ABC):
    dimensions: int

    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Returns one embedding vector per input text, same order."""
        ...


_TOKEN_RE = re.compile(r"[a-z0-9]+")


class LocalHashingEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = _TOKEN_RE.findall(text.lower())

        for token in tokens:
            # Hash each token to a bucket (dimension index) and a sign.
            # This is the "hashing trick": instead of a fixed vocabulary,
            # we let hash collisions stand in for a learned representation.
            # Repeated tokens accumulate, so word frequency still matters.
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 0:
            vector = [v / norm for v in vector]
        return vector


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        import httpx

        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {settings.LLM_API_KEY}"},
            json={
                "model": settings.EMBEDDING_MODEL,
                "input": texts,
                "dimensions": self.dimensions,
            },
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        # OpenAI's response items aren't guaranteed to be in input order —
        # each carries its own `index`, so sort by that rather than trust
        # array order.
        items = sorted(data["data"], key=lambda item: item["index"])
        return [item["embedding"] for item in items]


def get_embedding_provider() -> EmbeddingProvider:
    if settings.EMBEDDING_PROVIDER == "openai":
        return OpenAIEmbeddingProvider(settings.EMBEDDING_DIMENSIONS)
    return LocalHashingEmbeddingProvider(settings.EMBEDDING_DIMENSIONS)
