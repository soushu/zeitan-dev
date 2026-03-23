"""Zeitan FastAPI メインアプリケーション."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, calculate, dashboard, history, parse, portfolio, report
from src.utils.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """アプリケーションライフサイクル管理."""
    init_db()
    yield


app = FastAPI(
    title="Zeitan API",
    description="暗号資産税金計算API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# CORS設定（ALLOWED_ORIGINS 環境変数で制御、未設定時は localhost のみ許可）
_raw_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000")
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)


# ルーター登録
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(parse.router, prefix="/api", tags=["parse"])
app.include_router(calculate.router, prefix="/api", tags=["calculate"])
app.include_router(report.router, prefix="/api", tags=["report"])
app.include_router(history.router, prefix="/api", tags=["history"])
app.include_router(dashboard.router, prefix="/api", tags=["dashboard"])
app.include_router(portfolio.router, prefix="/api", tags=["portfolio"])


@app.get("/")
async def root():
    """ルートエンドポイント."""
    return {
        "message": "Zeitan API",
        "version": "1.0.0",
        "docs": "/api/docs",
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント."""
    return {"status": "healthy", "version": "1.0.1"}
