"""
retrieval.py (schemas)

Request/response shapes for the Phase 4 search endpoint. This endpoint
exists mainly to make retrieval independently testable and demonstrable
before Phase 5 wires it into an actual LLM-backed question-answering
flow — the shape here (chunk text + similarity + source location) is
exactly what Phase 5's grounded-answer prompt and citations will be built
from.
"""

import uuid

from pydantic import BaseModel


class SearchResult(BaseModel):
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    file_type: str
    text: str
    page_number: int | None
    row_number: int | None
    similarity: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
