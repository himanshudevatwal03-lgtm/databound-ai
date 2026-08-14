"""
user.py

The User ORM model.

Every piece of data in DataBound AI — documents, collections, notes,
bookmarks, flashcards — ultimately belongs to a user. This model is the
one every future table's `user_id` foreign key points back to, and the
`ownership checks` mentioned throughout the project spec all boil down to
"does this row's user_id match the currently authenticated user's id?".
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID

from app.database.session import Base


class User(Base):
    __tablename__ = "users"

    # UUIDs (rather than incrementing integers) for primary keys: they're
    # safe to expose in API responses/URLs without leaking how many users
    # have signed up, and they never collide across environments.
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)

    # Never store plaintext passwords — only a bcrypt hash (see
    # app/core/security.py). This column intentionally isn't called
    # "password" to make it harder to accidentally return it in an API
    # response and have it look like a real password.
    password_hash = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
