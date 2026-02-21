"""Zeitan FastAPI メインアプリケーション."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import calculate, history, parse, report
from src.utils.database import init_db

app = FastAPI(
    title="Zeitan API",
    description="暗号資産税金計算API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に制限
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def on_startup():
    """起動時にテーブルを初期化する."""
    init_db()


# ルーター登録
app.include_router(parse.router, prefix="/api", tags=["parse"])
app.include_router(calculate.router, prefix="/api", tags=["calculate"])
app.include_router(report.router, prefix="/api", tags=["report"])
app.include_router(history.router, prefix="/api", tags=["history"])


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
    return {"status": "healthy"}
