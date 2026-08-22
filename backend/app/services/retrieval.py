"""
retrieval.py

Semantic search over a user's indexed chunks: embed the query with the
same provider used to index the documents, then ask pgvector for the
nearest chunks by cosine distance. This is the "Retrieval" half of RAG —
Phase 5 will feed these results to an LLM as the ONLY context it's
allowed to answer from; nothing here talks to an LLM.

Every query is scoped to `user_id` — the same ownership-filtering pattern
used everywhere else in this project, so one user's search can never
surface another user's documents.
"""

import uuid

from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.services.embeddings import get_embedding_provider


def search(
    db: Session,
    user_id: uuid.UUID,
    query: str,
    top_k: int = 5,
    document_id: uuid.UUID | None = None,
    collection_id: uuid.UUID | None = None,
) -> list[dict]:
    """
    Returns up to `top_k` chunks most similar to `query`, each as:
        {chunk_id, document_id, filename, file_type, text,
         page_number, row_number, similarity}
    ordered by similarity descending (1.0 = identical, 0.0 = unrelated
    for normalized vectors — see cosine_distance below). An empty list
    means nothing relevant was found; the caller (Phase 5's QA pipeline)
    is responsible for turning that into "not enough information" rather
    than asking an LLM to guess.
    """
    provider = get_embedding_provider()
    query_vector = provider.embed_texts([query])[0]

    # pgvector's cosine_distance = 1 - cosine_similarity, so ordering
    # ascending by distance is the same as ordering descending by
    # similarity. We select the distance explicitly (rather than just
    # order_by it) because we need the actual number to report back.
    distance_col = DocumentChunk.embedding.cosine_distance(query_vector).label("distance")

    query_obj = (
        db.query(DocumentChunk, Document.filename, Document.file_type, distance_col)
        .join(Document, DocumentChunk.document_id == Document.id)
        .filter(DocumentChunk.user_id == user_id)
    )
    if document_id is not None:
        query_obj = query_obj.filter(DocumentChunk.document_id == document_id)
    if collection_id is not None:
        query_obj = query_obj.filter(Document.collection_id == collection_id)

    rows = query_obj.order_by(distance_col).limit(top_k).all()

    results = []
    for chunk, filename, file_type, distance in rows:
        results.append(
            {
                "chunk_id": chunk.id,
                "document_id": chunk.document_id,
                "filename": filename,
                "file_type": file_type,
                "text": chunk.text,
                "page_number": chunk.page_number,
                "row_number": chunk.row_number,
                "similarity": 1.0 - float(distance),
            }
        )
    return results
