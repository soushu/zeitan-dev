"""Auth Router - ユーザー認証エンドポイント."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from src.models.orm import User
from src.utils.auth import (
    create_access_token,
    hash_password,
    require_user,
    verify_password,
)
from src.utils.database import get_db

router = APIRouter()


class RegisterRequest(BaseModel):
    """ユーザー登録リクエスト."""

    email: EmailStr
    password: str
    name: str | None = None


class LoginRequest(BaseModel):
    """ログインリクエスト."""

    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """認証レスポンス."""

    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """ユーザー情報レスポンス."""

    id: int
    email: str
    name: str | None
    model_config = {"from_attributes": True}


@router.post("/auth/register", response_model=AuthResponse, status_code=201)
async def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """新規ユーザー登録."""
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="このメールアドレスは既に登録されています",
        )

    if len(req.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="パスワードは8文字以上で入力してください",
        )

    user = User(
        email=req.email,
        hashed_password=hash_password(req.password),
        name=req.name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.email)
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/auth/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: Session = Depends(get_db)):
    """ログイン."""
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="メールアドレスまたはパスワードが正しくありません",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアカウントは無効化されています",
        )

    token = create_access_token(user.id, user.email)
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_user)):
    """現在のユーザー情報を取得."""
    return UserResponse.model_validate(user)
