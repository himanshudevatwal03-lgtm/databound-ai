"""
questions.py (api)

The endpoint spec section 42 lists as `POST /api/questions`. This phase
is deliberately single-shot: ask a question, get a grounded answer back.
No conversation/history persistence yet — that's Phase 7's job (spec's
"conversations, history, follow-up questions"), which will wrap this same
pipeline with a conversations/questions/answers table.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database.session import get_db
from app.models.collection import Collection
from app.models.document import Document
from app.models.user import User
from app.schemas.question import AnswerResponse, QuestionRequest
from app.services.llm import LLMNotConfiguredError
from app.services.qa import answer_question

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("", response_model=AnswerResponse)
def ask_question(
    payload: QuestionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership checks up front: scoping a question to a document/
    # collection you don't own should fail clearly, not silently return
    # "not enough information" as if the scope were just empty.
    if payload.document_id is not None:
        owned = (
            db.query(Document)
            .filter(Document.id == payload.document_id, Document.user_id == current_user.id)
            .first()
        )
        if owned is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Document not found.")

    if payload.collection_id is not None:
        owned = (
            db.query(Collection)
            .filter(Collection.id == payload.collection_id, Collection.user_id == current_user.id)
            .first()
        )
        if owned is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Collection not found.")

    try:
        result = answer_question(
            db,
            user_id=current_user.id,
            question=payload.question,
            document_id=payload.document_id,
            collection_id=payload.collection_id,
            answer_style=payload.answer_style,
        )
    except LLMNotConfiguredError as e:
        # 503, not 500: this isn't a bug, it's a missing piece of
        # configuration the operator needs to fix (set LLM_API_KEY).
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))

    return AnswerResponse(**result)
