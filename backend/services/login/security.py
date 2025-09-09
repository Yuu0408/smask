# security.py
import time
from typing import Any, Literal

import jwt
from passlib.context import CryptContext

from conf.setting import settings  # you already use this in auth.py

# bcrypt hasher
_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")


# --- Password helpers ---
def hash_password(password: str) -> str:
    return _pwd.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _pwd.verify(plain_password, hashed_password)


# --- JWT helpers ---
ALGO = "HS256"

def _create_token(
    sub: str,
    token_type: Literal["access", "refresh"],
    minutes: int,
    extra: dict[str, Any],
) -> str:
    now = int(time.time())
    payload = {
        "sub": sub,        # user id (string; can be UUID)
        "type": token_type,
        "iat": now,
        "exp": now + minutes * 60,
        **extra,           # e.g., {"ver": token_version}
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGO)


def create_access_token(user_id: Any, token_version: int) -> str:
    # cast to str so UUIDs work cleanly in JWT
    return _create_token(str(user_id), "access", settings.ACCESS_TOKEN_EXPIRE, {"ver": token_version})


def create_refresh_token(user_id: Any, token_version: int) -> str:
    return _create_token(str(user_id), "refresh", settings.REFRESH_TOKEN_EXPIRE, {"ver": token_version})


def decode_token(token: str) -> dict:
    # raises jwt.ExpiredSignatureError, jwt.InvalidTokenError on failure (auth.py catches generically)
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGO])
