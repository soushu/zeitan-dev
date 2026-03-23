"""データベース接続管理."""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# プロジェクトルートの絶対パス（起動ディレクトリ差異を回避）
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# DATABASE_URL: 未設定時は SQLite にフォールバック
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{PROJECT_ROOT}/zeitan.db")

# SQLite の場合のみ check_same_thread=False を付与
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """SQLAlchemy 2.0 DeclarativeBase."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI Depends() 用 DB セッションジェネレーター."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """テーブルを冪等に作成する（起動時に呼び出す）."""
    # ORM モデルをインポートして Base に登録させる
    from src.models import orm  # noqa: F401

    Base.metadata.create_all(bind=engine)
