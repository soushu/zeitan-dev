"""FastAPI Pydantic Models."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TransactionResponse(BaseModel):
    """取引レスポンスモデル."""

    timestamp: datetime
    exchange: str
    symbol: str
    type: str
    amount: float
    price: float
    fee: float


class CalculateRequest(BaseModel):
    """計算リクエストモデル."""

    transactions: list[TransactionResponse]
    method: Literal["moving_average", "total_average"] = Field(
        default="moving_average",
        description="計算方法: moving_average (移動平均法) or total_average (総平均法)",
    )


class TradeResultResponse(BaseModel):
    """取引結果レスポンスモデル."""

    timestamp: datetime
    exchange: str
    symbol: str
    type: str
    amount: float
    price: float
    fee: float
    profit_loss: float
    average_cost_after: float | None = None
    average_cost_used: float | None = None


class CalculateResponse(BaseModel):
    """計算レスポンスモデル."""

    results: list[TradeResultResponse]
    total_profit_loss: float
    method: str


class ExchangeInfo(BaseModel):
    """取引所情報モデル."""

    id: str
    name: str
    category: Literal["domestic", "international"]


class ExchangesResponse(BaseModel):
    """取引所一覧レスポンスモデル."""

    exchanges: list[ExchangeInfo]
    total: int


class ErrorResponse(BaseModel):
    """エラーレスポンスモデル."""

    error: str
    detail: str | None = None


class CalculateResponseWithSession(CalculateResponse):
    """セッションID付き計算レスポンス."""

    session_id: int


class SessionSummary(BaseModel):
    """計算履歴一覧用サマリー."""

    id: int
    created_at: datetime
    calc_method: str
    total_profit_loss: float
    transaction_count: int
    note: Optional[str] = None

    model_config = {"from_attributes": True}


class SessionDetail(SessionSummary):
    """計算履歴詳細（取引・結果含む）."""

    transactions: list[TransactionResponse]
    results: list[TradeResultResponse]
