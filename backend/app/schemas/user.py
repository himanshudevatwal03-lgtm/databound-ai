"""
user.py (schemas)

Pydantic models define the *shape* of data crossing the API boundary —
what a request body must contain, and what a response will look like.
These are deliberately separate from the SQLAlchemy model in
app/models/user.py: the ORM model describes a database row (including
password_hash), while these schemas describe what's safe to accept from,
or return to, the outside world. UserResponse in particular is what keeps
password_hash from ever accidentally leaking into an API response.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """Request body for POST /api/auth/register."""

    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """Request body for POST /api/auth/login."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    What we return to describe a user — notably, no password_hash.

    model_config's from_attributes=True lets us build this directly from
    a SQLAlchemy User object (UserResponse.model_validate(user_row))
    instead of manually copying each field.
    """

    id: uuid.UUID
    name: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    """Response body for a successful login or registration."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """The decoded contents of a JWT's payload, once verified."""

    sub: str  # "subject" — we store the user's id (as a string) here
    exp: int  # expiration timestamp
