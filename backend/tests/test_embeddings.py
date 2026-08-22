"""
test_embeddings.py

Unit tests for LocalHashingEmbeddingProvider. These pin down the
properties that actually matter for retrieval to work correctly:
deterministic, correctly-sized, normalized, and — critically — texts
sharing more words end up more similar (higher cosine similarity) than
texts sharing none. That last property is the whole reason retrieval
returns sensible results despite this provider not being a "real"
semantic model.
"""

import math

from app.services.embeddings import LocalHashingEmbeddingProvider


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def test_embedding_has_configured_dimensions():
    provider = LocalHashingEmbeddingProvider(dimensions=384)
    [vector] = provider.embed_texts(["Rahul's CGPA is 8.4."])
    assert len(vector) == 384


def test_embedding_is_deterministic():
    provider = LocalHashingEmbeddingProvider(dimensions=128)
    [a] = provider.embed_texts(["Rahul's CGPA is 8.4."])
    [b] = provider.embed_texts(["Rahul's CGPA is 8.4."])
    assert a == b


def test_embedding_is_normalized():
    provider = LocalHashingEmbeddingProvider(dimensions=128)
    [vector] = provider.embed_texts(["The quick brown fox jumps over the lazy dog."])
    norm = math.sqrt(sum(v * v for v in vector))
    assert abs(norm - 1.0) < 1e-6


def test_empty_text_produces_zero_vector():
    provider = LocalHashingEmbeddingProvider(dimensions=64)
    [vector] = provider.embed_texts([""])
    assert all(v == 0.0 for v in vector)


def test_shared_words_increase_similarity():
    """
    The property retrieval actually depends on: a query sharing words
    with a document should be more similar to it than to an unrelated
    document — even though this is lexical, not learned, similarity.
    """
    provider = LocalHashingEmbeddingProvider(dimensions=256)

    query = "What is Rahul's CGPA?"
    relevant_doc = "Rahul's CGPA is 8.4."
    unrelated_doc = "The company was founded in 2015 in Bengaluru."

    [q_vec, rel_vec, unrel_vec] = provider.embed_texts([query, relevant_doc, unrelated_doc])

    sim_relevant = _cosine_similarity(q_vec, rel_vec)
    sim_unrelated = _cosine_similarity(q_vec, unrel_vec)

    assert sim_relevant > sim_unrelated


def test_different_dimension_instances_are_independent():
    small = LocalHashingEmbeddingProvider(dimensions=32)
    large = LocalHashingEmbeddingProvider(dimensions=512)
    [v_small] = small.embed_texts(["test text"])
    [v_large] = large.embed_texts(["test text"])
    assert len(v_small) == 32
    assert len(v_large) == 512
