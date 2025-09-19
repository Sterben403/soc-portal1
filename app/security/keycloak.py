import os
from functools import lru_cache
from fastapi import Header, HTTPException, status
import jwt
from jwt import PyJWKClient

KC_BASE = os.getenv("KC_BASE_URL", "http://keycloak:8080")
KC_REALM = os.getenv("KC_REALM", "soc")
KC_CLIENT_ID = os.getenv("KC_CLIENT_ID", "soc-portal")
# Пусто = не проверяем audience. Если хочешь строго — поставь clientId.
KC_AUDIENCE = os.getenv("KC_AUDIENCE", "")
ALGO = "RS256"

JWKS_URL = f"{KC_BASE}/realms/{KC_REALM}/protocol/openid-connect/certs"
_jwks_client = PyJWKClient(JWKS_URL)

def _issuer() -> str:
    return f"{KC_BASE}/realms/{KC_REALM}"

def _decode(token: str) -> dict:
    try:
        signing_key = _jwks_client.get_signing_key_from_jwt(token).key
        return jwt.decode(
            token,
            signing_key,
            algorithms=[ALGO],
            issuer=_issuer(),
            audience=KC_AUDIENCE if KC_AUDIENCE else None,
            options={"verify_aud": bool(KC_AUDIENCE)},  # если пусто — не проверяем aud
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

def _bearer(auth: str | None) -> str:
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header missing")
    return auth.split(" ", 1)[1]

def get_current_claims(authorization: str | None = Header(None)) -> dict:
    token = _bearer(authorization)
    return _decode(token)

def get_roles(claims: dict) -> list[str]:
    return claims.get("realm_access", {}).get("roles", []) or []

def require_roles(*allowed: str):
    def dep(authorization: str | None = Header(None)):
        claims = get_current_claims(authorization)
        roles = get_roles(claims)
        if not any(r in roles for r in allowed):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
        return claims
    return dep
