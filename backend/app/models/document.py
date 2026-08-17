"""
document.py (model)

Represents one uploaded file. Two design choices worth calling out:

1. We don't keep the original uploaded file on disk. Render's (and most
   PaaS) filesystems are ephemeral — anything written to disk disappears
   on the next deploy or restart. Instead, we extract the file's content
   once at upload time and store that extracted content in Postgres
   (which *is* persistent), then discard the temp file. This trades away
   "download my original file back" for "this actually survives a
   redeploy", which is the right trade for a Q&A-over-documents product.

2. `extracted_content` is a JSONB column with a shape that depends on
   file_type, deliberately structured now so Phase 4's chunking step has
   something clean to work from instead of one giant text blob:

     TXT:  {"type": "txt", "text": "..."}
     PDF:  {"type": "pdf", "pages": [{"page_number": 1, "text": "..."}, ...]}
     CSV:  {"type": "csv", "columns": [...], "rows": [{"row_number": 1, "data": {...}}, ...]}

See app/services/document_processing.py for what builds this shape.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, Integer, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.database.session import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    collection_id = Column(
        UUID(as_uuid=True), ForeignKey("collections.id", ondelete="SET NULL"), nullable=True, index=True
    )

    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # "txt" | "pdf" | "csv"
    file_size = Column(Integer, nullable=False)  # bytes

    version = Column(Integer, nullable=False, default=1)
    # "processing" | "ready" | "failed" — set to "failed" (with an error
    # message in processing_error) rather than rejecting the upload
    # outright for errors discovered only during extraction, so the user
    # can see what went wrong instead of just getting a bare 400.
    status = Column(String, nullable=False, default="processing")
    processing_error = Column(Text, nullable=True)

    extracted_content = Column(JSONB, nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
