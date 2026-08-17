"""
collection.py (schemas)

Request/response shapes for the collections API. Kept intentionally thin
— a collection is just a named grouping, so there's not much to validate
beyond "name is present and reasonable".
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class CollectionCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=2000)


class CollectionResponse(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    document_count: int = 0
    created_at: datetime

    model_config = {"from_attributes": True}
