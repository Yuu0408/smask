# auth.py
from repositories.medical_record_repo import MedicalRecordRepo
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


def get_current_user(request: Request, db: Session = Depends(get_session)) -> User:
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")

    token = auth.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    user = db.get(User, payload.get("sub"))
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    if payload.get("ver") != user.token_version:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    return user

@router.get("/me", response_model=UserPublic)
def get_me(current: User = Depends(get_current_user), db: Session = Depends(get_session)):
    medical_record_repo = MedicalRecordRepo(db)
    record_id = medical_record_repo.get_latest_record_id(user_id=current.id)
    if not record_id:
        record_id = ""
    return UserPublic(id=str(current.id), record_id=str(record_id), username=current.username, is_active=current.is_active, role=current.role_type)

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
    medical_record_repo = MedicalRecordRepo(db)
    record_id = medical_record_repo.get_latest_record_id(user_id=user.id)
    if not record_id:
        record_id = ""
    return TokenResponse(
        accessToken=access,
        user=UserPublic(id=str(user.id), record_id=str(record_id), username=user.username, is_active=user.is_active, role=user.role_type),
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

    user = db.get(User, payload["sub"])
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
    medical_record_repo = MedicalRecordRepo(db)
    record_id = medical_record_repo.get_latest_record_id(user_id=user.id)
    if not record_id:
        record_id = ""
    return TokenResponse(
        accessToken=new_access,
        user=UserPublic(id=str(user.id), record_id=str(record_id), username=user.username, is_active=user.is_active, role=user.role_type),
    )

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_session)):
    # Enforce required metadata for doctor role
    if payload.role == "doctor":
        meta = payload.metadata or {}
        addr = meta.get("address")
        fac = meta.get("facility")
        if not addr or not fac:
            raise HTTPException(status_code=400, detail="Doctor registration requires address and facility")
    user = User(
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role_type=payload.role,
        user_metadata=payload.metadata or {},
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
    medical_record_repo = MedicalRecordRepo(db)
    record_id = medical_record_repo.get_latest_record_id(user_id=user.id)
    if not record_id:
        record_id = ""
    return {
        "accessToken": access,
        "user": UserPublic(id=str(user.id), record_id=str(record_id), username=user.username, is_active=user.is_active, role=user.role_type),
    }

@router.post("/logout")
def logout(response: Response, db: Session = Depends(get_session), request: Request = None):
    # If you want server-side revoke, you can bump version if user is known.
    # Without an access token here, a simple cookie clear is okay.
    clear_refresh_cookie(response)
    return {"ok": True}



