"""Portfolio Router - ポートフォリオエンドポイント."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.models.orm import User
from src.utils.auth import get_current_user
from src.utils.database import get_db
from src.utils.portfolio import calculate_portfolio

router = APIRouter()


class CurrencyHolding(BaseModel):
    """通貨別保有情報."""
    symbol: str
    amount: float
    average_cost: float
    last_price: float
    current_value: float
    cost_basis: float
    unrealized_pnl: float
    allocation_pct: float


class PortfolioResponse(BaseModel):
    """ポートフォリオレスポンス."""
    total_value: float
    total_cost: float
    unrealized_pnl: float
    holdings: list[CurrencyHolding]
    session_id: Optional[int] = None
    calc_method: Optional[str] = None


@router.get("/portfolio", response_model=PortfolioResponse)
async def get_portfolio(
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    """ポートフォリオ（保有資産概要）を取得."""
    data = calculate_portfolio(db, user_id=user.id if user else None)
    return PortfolioResponse(**data)
