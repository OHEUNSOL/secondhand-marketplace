from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import User
from app.routers.deps import get_current_user
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.services.errors import ServiceError

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        user = service.signup(payload)
        return UserResponse.model_validate(user)
    except ServiceError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        access_token, refresh_token = service.login(payload)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except ServiceError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        access_token, refresh_token = service.refresh(payload.refresh_token)
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
    except ServiceError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
