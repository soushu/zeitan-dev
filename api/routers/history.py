"""History Router - 計算履歴エンドポイント."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import extract, func
from sqlalchemy.orm import Session

from api.models import SessionDetail, SessionSummary, TradeResultResponse, TransactionResponse
from src.models.orm import CalcSession, Transaction
from src.utils.database import get_db
from src.utils.db_service import get_session_detail, get_sessions

router = APIRouter()


@router.get("/history", response_model=list[SessionSummary])
async def list_history(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(None, description="年度でフィルタ（例: 2024）"),
):
    """計算履歴一覧を返す（最新順）。tax_year は取引データの最小年度。"""
    sessions = get_sessions(db)

    # セッションごとの最小取引年度を一括取得（サブクエリ）
    year_rows = (
        db.query(
            Transaction.session_id,
            func.min(Transaction.timestamp).label("min_ts"),
        )
        .group_by(Transaction.session_id)
        .all()
    )
    year_map: dict[int, int] = {
        row.session_id: row.min_ts.year for row in year_rows if row.min_ts
    }

    result = []
    for s in sessions:
        tax_year = year_map.get(s.id)
        if year is not None and tax_year != year:
            continue
        summary = SessionSummary.model_validate(s)
        summary.tax_year = tax_year
        result.append(summary)
    return result


@router.get("/history/years", response_model=list[int])
async def list_available_years(db: Session = Depends(get_db)):
    """計算履歴に存在する年度一覧を返す（降順）。"""
    year_rows = (
        db.query(
            func.min(Transaction.timestamp).label("min_ts"),
        )
        .group_by(Transaction.session_id)
        .all()
    )
    years = sorted(
        {row.min_ts.year for row in year_rows if row.min_ts},
        reverse=True,
    )
    return years


@router.get("/history/{session_id}", response_model=SessionDetail)
async def get_history_detail(session_id: int, db: Session = Depends(get_db)):
    """指定セッションの詳細を返す.

    Raises:
        HTTPException: セッションが存在しない場合（404）
    """
    session = get_session_detail(db, session_id)
    if session is None:
        raise HTTPException(status_code=404, detail=f"セッション {session_id} が見つかりません")

    return SessionDetail(
        id=session.id,
        created_at=session.created_at,
        calc_method=session.calc_method,
        total_profit_loss=session.total_profit_loss,
        transaction_count=session.transaction_count,
        note=session.note,
        transactions=[
            TransactionResponse(
                timestamp=tx.timestamp,
                exchange=tx.exchange,
                symbol=tx.symbol,
                type=tx.type,
                amount=tx.amount,
                price=tx.price,
                fee=tx.fee,
            )
            for tx in session.transactions
        ],
        results=[
            TradeResultResponse(
                timestamp=r.timestamp,
                exchange=r.exchange,
                symbol=r.symbol,
                type=r.type,
                amount=r.amount,
                price=r.price,
                fee=r.fee,
                profit_loss=r.profit_loss,
                average_cost_after=r.average_cost_after,
                average_cost_used=r.average_cost_used,
            )
            for r in session.results
        ],
    )
