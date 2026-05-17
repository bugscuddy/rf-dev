"""
Dashboard Authentication Module
Protects the control panel from unauthorized access using token-based auth.

On first boot, generates a unique access token stored locally.
The token is required for all POST (mutation) endpoints.
GET (read-only) endpoints remain public for mesh transparency.
"""

import os
import secrets
import hashlib
import logging
from typing import Optional
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

logger = logging.getLogger(__name__)

TOKEN_FILE = os.path.join(os.path.dirname(__file__), ".meshwork_token")

security = HTTPBearer(auto_error=False)


def _generate_token() -> str:
    """Generate a cryptographically secure token."""
    return secrets.token_urlsafe(32)


def _hash_token(token: str) -> str:
    """Hash token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()


def init_auth() -> str:
    """
    Initialize authentication. On first run, generates and stores a token.
    Returns the plaintext token (only shown once on first boot).
    """
    if os.path.exists(TOKEN_FILE):
        logger.info("Auth token file already exists")
        return ""  # Token already exists, don't reveal it again

    token = _generate_token()
    hashed = _hash_token(token)

    with open(TOKEN_FILE, "w") as f:
        f.write(hashed)

    logger.info("Generated new auth token on first boot")
    return token


def get_stored_hash() -> Optional[str]:
    """Read the stored token hash."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        return f.read().strip()


def verify_token(token: str) -> bool:
    """Verify a token against the stored hash."""
    stored_hash = get_stored_hash()
    if stored_hash is None:
        logger.warning("Token verification failed: no stored hash found")
        return False
    result = _hash_token(token) == stored_hash
    if not result:
        logger.warning("Token verification failed: invalid token")
    return result


async def require_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> str:
    """
    FastAPI dependency that requires valid authentication.
    Use on POST endpoints that mutate state.
    
    Accepts Bearer token in Authorization header.
    """
    if credentials is None:
        logger.warning("Authentication required: no credentials provided")
        raise HTTPException(status_code=401, detail="Authentication required")

    if not verify_token(credentials.credentials):
        logger.warning("Authentication failed: invalid token")
        raise HTTPException(status_code=403, detail="Invalid token")

    logger.debug("Authentication successful")
    return credentials.credentials


def reset_token() -> str:
    """Reset the auth token. Returns the new plaintext token."""
    if os.path.exists(TOKEN_FILE):
        os.remove(TOKEN_FILE)
        logger.warning("Auth token reset")
    return init_auth()
