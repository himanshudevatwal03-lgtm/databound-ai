"""
security.py

Two responsibilities, kept together because they're both "cryptographic
primitives the rest of the app shouldn't have to think about":

1. Password hashing — using bcrypt via passlib. We NEVER store or compare
   plaintext passwords; hash_password() is called once at registration,
   and verify_password() re-hashes the login attempt's password and
   compares hashes (bcrypt handles the salt internally).

2. JWT (JSON Web Token) creation/verification — how a user "stays logged
   in" across requests. After login, the server hands back a signed token
   containing the user's id and an expiry. The browser sends that token
   back on every subsequent request (in the Authorization header), and
   decode_access_token() verifies the signature and expiry without ever
   needing to touch the database or ask for a password again.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# bcrypt is the industry-standard choice for password hashing: it's slow
# by design (resistant to brute-force) and handles salting automatically.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)


def create_access_token(subject: str) -> str:
    """
    Creates a signed JWT for the given subject (the user's id, as a
    string). The token embeds its own expiry, so the server never needs
    to store session state — verifying a token is enough to know both who
    the user is and whether their session is still valid.
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": subject, "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> str | None:
    """
    Verifies a JWT's signature and expiry, returning the subject (user id)
    if valid, or None if the token is invalid/expired/tampered with.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
