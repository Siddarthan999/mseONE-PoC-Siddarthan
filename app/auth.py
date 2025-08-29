# app/auth.py
import os
import time
from typing import Any, Dict

import httpx
from jose import jwt
from fastapi import HTTPException, Request

OIDC_ISSUER = os.getenv("OIDC_ISSUER")
JWKS_URL = os.getenv("OIDC_JWKS_URL")
AUDIENCE = os.getenv("OIDC_AUDIENCE")
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() == "true"

_jwks_cache: Dict[str, Any] = {}
_jwks_fetched_at = 0.0


def _get_jwks() -> Dict[str, Any]:
    """Fetch and cache JWKS keys for 10 minutes."""
    global _jwks_cache, _jwks_fetched_at
    if not _jwks_cache or time.time() - _jwks_fetched_at > 600:
        if not JWKS_URL:
            raise HTTPException(status_code=500, detail="JWKS URL not configured")
        with httpx.Client(timeout=5) as c:
            jwks = c.get(JWKS_URL).json()
        _jwks_cache = {k["kid"]: k for k in jwks.get("keys", [])}
        _jwks_fetched_at = time.time()
    return _jwks_cache


def _get_public_key(token: str) -> Dict[str, Any]:
    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")
    if not kid:
        raise HTTPException(status_code=401, detail="Missing kid in token header")
    jwks = _get_jwks()
    key = jwks.get(kid)
    if not key:
        # refresh once if unknown kid
        _jwks_cache.clear()
        jwks = _get_jwks()
        key = jwks.get(kid)
        if not key:
            raise HTTPException(status_code=401, detail="Unknown signing key")
    return key


def validate_token(token: str) -> Dict[str, Any]:
    key = _get_public_key(token)
    options = {"verify_aud": bool(AUDIENCE)}
    try:
        return jwt.decode(
            token,
            key,
            algorithms=[key.get("alg", "RS256")],
            audience=AUDIENCE if AUDIENCE else None,
            issuer=OIDC_ISSUER if OIDC_ISSUER else None,
            options=options,
        )
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


async def auth_context(request: Request):
    """
    Strawberry context getter.
    - Validates Bearer token (unless REQUIRE_AUTH=false)
    - Allows unauthenticated access for GraphQL Playground UI (Accept: text/html)
    - Returns {'claims': ..., 'user': {...}}
    """

    # ✅ Allow the GraphQL Playground (browser UI) without token
    if "text/html" in request.headers.get("accept", ""):
        return {"claims": {}, "user": None}

    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        if not REQUIRE_AUTH:
            return {"claims": {}, "user": None}
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Use Bearer token")

    token = auth.split(" ", 1)[1].strip()
    claims = validate_token(token)
    user = {
        "sub": claims.get("sub"),
        "username": claims.get("preferred_username"),
        "email": claims.get("email"),
        "roles": claims.get("realm_access", {}).get("roles", []),
    }
    return {"claims": claims, "user": user}


def require_roles(info, required: list[str]):
    roles = set(info.context.get("user", {}).get("roles") or [])
    if not set(required).issubset(roles):
        raise HTTPException(status_code=403, detail="Forbidden: missing required role(s)")
