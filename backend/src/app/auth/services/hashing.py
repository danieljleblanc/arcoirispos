# backend/src/app/auth/services/hashing.py

from passlib.context import CryptContext

# Bcrypt under Python 3.14 needs explicit rounds to avoid warnings.
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,     # ← safe & explicit
)


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against the stored bcrypt hash.
    """
    return pwd_context.verify(plain_password, hashed_password)
