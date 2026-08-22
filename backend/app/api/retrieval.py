"""
retrieval.py (api)

A single endpoint: search your own indexed chunks by meaning (well —
by the active embedding provider's notion of meaning; see the docstring
in app/services/embeddings.py for what that means with the default local
provider). This isn't in the original spec's endpoint list because the
spec bundles retrieval into Phase 5's full question-answering flow, but
having it independently callable is what makes retrieval quality
verifiable on its own before an LLM is layered on top — and Phase 5's
POST /api/questions will call app.services.retrieval.search() directly
rather than going through this HTTP endpoint.
"""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.schemas.retrieval import SearchResponse, SearchResult
from app.services.retrieval import search

router = APIRouter(prefix="/retrieval", tags=["retrieval"])


@router.get("/search", response_model=SearchResponse)
def search_documents(
    q: str = Query(min_length=1, max_length=2000),
    document_id: uuid.UUID | None = None,
    collection_id: uuid.UUID | None = None,
    top_k: int = Query(default=settings.TOP_K, ge=1, le=20),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not q.strip():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Query cannot be empty.")

    results = search(
        db,
        user_id=current_user.id,
        query=q,
        top_k=top_k,
        document_id=document_id,
        collection_id=collection_id,
    )
    return SearchResponse(query=q, results=[SearchResult(**r) for r in results])
