"""FastAPI Pydantic Models."""

from datetime import datetime
from typing import Literal

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
