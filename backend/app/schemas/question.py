"""
question.py (schemas)

Matches the API response format from spec section 43 exactly:

    {
      "answer": "...",
      "supported": true,
      "sources": [{"document_id": ..., "filename": ..., "page_number": ...,
                    "row_number": ..., "text": ...}]
    }

QuestionRequest.answer_style corresponds to spec section 34 ("Answer
Style") — short/detailed/bullet_points/simple. The factual content stays
grounded regardless of style; only formatting/length changes (see the
STYLE_INSTRUCTIONS mapping in app/services/qa.py).
"""

import uuid
from typing import Literal

from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    document_id: uuid.UUID | None = None
    collection_id: uuid.UUID | None = None
    answer_style: Literal["short", "detailed", "bullet_points", "simple"] = "detailed"


class Source(BaseModel):
    document_id: uuid.UUID
    filename: str
    page_number: int | None
    row_number: int | None
    text: str


class AnswerResponse(BaseModel):
    answer: str
    supported: bool
    sources: list[Source]
