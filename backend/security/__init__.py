"""
Finovate Audit Nexus AI - Security Package
AES-256 encryption, authentication, and session management
Single source of truth for password hashing and verification.
"""
from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a bcrypt hash."""
    return _pwd_context.verify(plain_password, hashed_password)
