"""
collection.py (model)

A collection is just a user-defined folder for documents (see spec
section 17: "Collections / Folders"). Deleting a collection unassigns its
documents (sets document.collection_id to NULL) rather than deleting the
documents themselves — losing a folder shouldn't silently destroy the
files in it. See documents.py's delete endpoint for the actual deletion
logic and its "no orphaned records" guarantee.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class Collection(Base):
    __tablename__ = "collections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
