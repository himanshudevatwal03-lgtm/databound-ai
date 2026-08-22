"""
document_chunk.py (model)

The unit that Phase 5's retrieval actually searches over. One row per
chunk produced by app/services/chunking.py, with its embedding vector
stored alongside it via pgvector.

`user_id` is denormalized here (also reachable via document_id ->
documents.user_id) purely so ownership filtering on searches doesn't
require an extra join — every retrieval query filters chunks directly by
`DocumentChunk.user_id == current_user.id`.

The embedding column's dimensionality is fixed to
settings.EMBEDDING_DIMENSIONS at import time. Changing that setting after
documents have already been indexed does NOT retroactively resize
existing data — see the note on EMBEDDING_DIMENSIONS in app/config.py.
"""

import uuid
from datetime import datetime, timezone

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.config import settings
from app.database.session import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    row_number = Column(Integer, nullable=True)

    embedding = Column(Vector(settings.EMBEDDING_DIMENSIONS), nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
