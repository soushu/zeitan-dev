"""Auth Router - ユーザー認証エンドポイント."""

import os
import secrets

import httpx
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

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

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


class GoogleCallbackRequest(BaseModel):
    """Google OAuthコールバックリクエスト."""

    code: str
    redirect_uri: str


@router.post("/auth/google", response_model=AuthResponse)
async def google_auth(req: GoogleCallbackRequest, db: Session = Depends(get_db)):
    """Google OAuthでログイン/登録."""
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google認証が設定されていません",
        )

    # 認可コードをアクセストークンに交換
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            GOOGLE_TOKEN_URL,
            data={
                "code": req.code,
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uri": req.redirect_uri,
                "grant_type": "authorization_code",
            },
        )

    if token_res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Google認証に失敗しました",
        )

    token_data = token_res.json()
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Googleアクセストークンの取得に失敗しました",
        )

    # ユーザー情報を取得
    async with httpx.AsyncClient() as client:
        userinfo_res = await client.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
        )

    if userinfo_res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Googleユーザー情報の取得に失敗しました",
        )

    google_user = userinfo_res.json()
    email = google_user.get("email")
    name = google_user.get("name")

    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Googleアカウントからメールアドレスを取得できませんでした",
        )

    # 既存ユーザーを検索、なければ作成
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            hashed_password=hash_password(secrets.token_urlsafe(32)),
            name=name,
        )
        db.add(user)
        db.commit()
        db.refresh(user)

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


@router.get("/auth/google/client-id")
async def get_google_client_id():
    """Google Client IDを返す（フロントエンド用）."""
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google認証が設定されていません",
        )
    return {"client_id": GOOGLE_CLIENT_ID}


@router.get("/auth/me", response_model=UserResponse)
async def get_me(user: User = Depends(require_user)):
    """現在のユーザー情報を取得."""
    return UserResponse.model_validate(user)
