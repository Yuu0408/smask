# auth.py
from fastapi import APIRouter, Depends, HTTPException, Response, status, Request
from sqlalchemy.orm import Session
from database import get_session
from models.entities.model import User
from models.dto.modelDto import LoginRequest, TokenResponse, UserPublic, RegisterRequest
from services.login.security import verify_password, create_access_token, create_refresh_token, decode_token, hash_password
from conf.setting import settings
from sqlalchemy.exc import IntegrityError

router = APIRouter(prefix="/auth", tags=["auth"])

def set_refresh_cookie(resp: Response, token: str):
    resp.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,  # "lax" is decent default; use "none" + secure=true if cross-site
        max_age=settings.REFRESH_TOKEN_EXPIRE * 60,
        path="/auth",  # limit cookie scope to auth routes
    )

def clear_refresh_cookie(resp: Response):
    resp.delete_cookie(settings.COOKIE_NAME, path="/auth")

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_session)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # rotate on login: bump version so any prior refresh is dead
    user.token_version += 1
    db.add(user); db.commit(); db.refresh(user)

    refresh = create_refresh_token(user.id, user.token_version)
    set_refresh_cookie(response, refresh)

    access = create_access_token(user.id, user.token_version)
    return TokenResponse(
        accessToken=access,
        user=UserPublic(id=user.id, username=user.username, is_active=user.is_active),
    )

@router.post("/refresh", response_model=TokenResponse)
def refresh(request: Request, response: Response, db: Session = Depends(get_session)):
    cookie = request.cookies.get(settings.COOKIE_NAME)
    if not cookie:
        raise HTTPException(status_code=401, detail="No refresh token")

    try:
        payload = decode_token(cookie)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh")

    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type")

    user = db.get(User, int(payload["sub"]))
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    # must match current token_version
    if payload.get("ver") != user.token_version:
        raise HTTPException(status_code=401, detail="Refresh token revoked")

    # rotate refresh: bump version -> old refresh becomes invalid immediately
    user.token_version += 1
    db.add(user); db.commit(); db.refresh(user)

    new_refresh = create_refresh_token(user.id, user.token_version)
    set_refresh_cookie(response, new_refresh)

    new_access = create_access_token(user.id, user.token_version)
    return TokenResponse(
        accessToken=new_access,
        user=UserPublic(id=user.id, username=user.username, is_active=user.is_active),
    )

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_session)):
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        is_active=True,
        token_version=0,
    )
    db.add(user)
    try:
        db.commit()
        db.refresh(user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="username already registered")

    # rotate on first issue (optional, keeps parity with login flow)
    user.token_version += 1
    db.add(user); db.commit(); db.refresh(user)

    refresh = create_refresh_token(user.id, user.token_version)
    set_refresh_cookie(response, refresh)

    access = create_access_token(user.id, user.token_version)
    return {
        "accessToken": access,
        "user": UserPublic(id=user.id, username=user.username, is_active=user.is_active),
    }

@router.post("/logout")
def logout(response: Response, db: Session = Depends(get_session), request: Request = None):
    # If you want server-side revoke, you can bump version if user is known.
    # Without an access token here, a simple cookie clear is okay.
    clear_refresh_cookie(response)
    return {"ok": True}
