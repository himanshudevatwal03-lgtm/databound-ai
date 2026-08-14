"""
deps.py

FastAPI dependencies related to "who is making this request". The star of
this file is get_current_user: adding it as a parameter to any route
instantly makes that route require a valid login, e.g.:

    @router.get("/documents")
    def list_documents(current_user: User = Depends(get_current_user)):
        # current_user is guaranteed to be a real, authenticated User here

This is also where every future "does this user own this resource?" check
starts: current_user.id is the value every ownership check compares
against.
"""

import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database.session import get_db
from app.models.user import User

# OAuth2PasswordBearer doesn't implement OAuth2 itself here — we're using
# it purely as a standard way to (a) tell FastAPI's /docs UI to show an
# "Authorize" button, and (b) extract the bearer token from the
# Authorization header. tokenUrl points at our login endpoint so the docs
# UI knows where to get a token from.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_error

    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise credentials_error

    user = db.query(User).filter(User.id == user_uuid).first()
    if user is None:
        raise credentials_error

    return user
