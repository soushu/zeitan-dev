"""Dashboard Router - ダッシュボード集計エンドポイント."""

from collections import defaultdict

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.models import (
    CurrencyBreakdown,
    DashboardResponse,
    ExchangeBreakdown,
    MonthlyBreakdown,
    SessionSummary,
)
from src.models.orm import CalcSession, TradeResultRecord, Transaction
from src.utils.database import get_db
from src.utils.db_service import get_sessions

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    session_id: int | None = Query(default=None, description="セッションID（省略時は最新）"),
    db: Session = Depends(get_db),
):
    """ダッシュボード集計データを返す.

    通貨別・取引所別・月別の損益内訳を返します。
    session_id を省略すると最新のセッションを使用します。
    """
    # セッション取得
    if session_id is not None:
        session = db.query(CalcSession).filter(CalcSession.id == session_id).first()
        if session is None:
            raise HTTPException(status_code=404, detail=f"セッション {session_id} が見つかりません")
    else:
        session = db.query(CalcSession).order_by(CalcSession.created_at.desc()).first()
        if session is None:
            raise HTTPException(status_code=404, detail="計算履歴がありません")

    # 計算結果レコード取得
    results = (
        db.query(TradeResultRecord)
        .filter(TradeResultRecord.session_id == session.id)
        .all()
    )

    # ── 集計処理 ──────────────────────────────────────────
    sell_count = sum(1 for r in results if r.type == "sell")
    buy_count = sum(1 for r in results if r.type == "buy")

    # 通貨別集計
    currency_map: dict[str, dict] = defaultdict(
        lambda: {"profit_loss": 0.0, "transaction_count": 0, "sell_count": 0, "buy_count": 0}
    )
    for r in results:
        c = currency_map[r.symbol]
        c["profit_loss"] += r.profit_loss
        c["transaction_count"] += 1
        if r.type == "sell":
            c["sell_count"] += 1
        elif r.type == "buy":
            c["buy_count"] += 1

    by_currency = [
        CurrencyBreakdown(
            symbol=sym,
            profit_loss=round(v["profit_loss"], 0),
            transaction_count=v["transaction_count"],
            sell_count=v["sell_count"],
            buy_count=v["buy_count"],
        )
        for sym, v in sorted(currency_map.items(), key=lambda x: -abs(x[1]["profit_loss"]))
    ]

    # 取引所別集計
    exchange_map: dict[str, dict] = defaultdict(
        lambda: {"profit_loss": 0.0, "transaction_count": 0}
    )
    for r in results:
        e = exchange_map[r.exchange]
        e["profit_loss"] += r.profit_loss
        e["transaction_count"] += 1

    by_exchange = [
        ExchangeBreakdown(
            exchange=ex,
            profit_loss=round(v["profit_loss"], 0),
            transaction_count=v["transaction_count"],
        )
        for ex, v in sorted(exchange_map.items(), key=lambda x: -abs(x[1]["profit_loss"]))
    ]

    # tax_year（最小取引年度）
    min_ts = db.query(func.min(Transaction.timestamp)).filter(
        Transaction.session_id == session.id
    ).scalar()
    tax_year = min_ts.year if min_ts else None

    # 月別集計（取引日時ベース）— tax_year の1〜12月を全てパディング
    month_map: dict[str, dict] = defaultdict(
        lambda: {"profit_loss": 0.0, "sell_count": 0}
    )
    for r in results:
        ym = r.timestamp.strftime("%Y-%m")
        month_map[ym]["profit_loss"] += r.profit_loss
        if r.type == "sell":
            month_map[ym]["sell_count"] += 1

    # tax_year が分かれば 12ヶ月分を埋める（データなし月は 0）
    if tax_year:
        for m in range(1, 13):
            ym = f"{tax_year}-{m:02d}"
            if ym not in month_map:
                month_map[ym] = {"profit_loss": 0.0, "sell_count": 0}

    by_month = [
        MonthlyBreakdown(
            year_month=ym,
            profit_loss=round(v["profit_loss"], 0),
            sell_count=v["sell_count"],
        )
        for ym, v in sorted(month_map.items())
        if not tax_year or ym.startswith(str(tax_year))
    ]

    # 全セッション一覧（セレクター用）
    all_sessions = get_sessions(db)
    year_rows = (
        db.query(Transaction.session_id, func.min(Transaction.timestamp).label("min_ts"))
        .group_by(Transaction.session_id)
        .all()
    )
    year_map = {row.session_id: row.min_ts.year for row in year_rows if row.min_ts}
    available = []
    for s in all_sessions:
        summary = SessionSummary.model_validate(s)
        summary.tax_year = year_map.get(s.id)
        available.append(summary)

    return DashboardResponse(
        session_id=session.id,
        tax_year=tax_year,
        calc_method=session.calc_method,
        total_profit_loss=session.total_profit_loss,
        transaction_count=session.transaction_count,
        sell_count=sell_count,
        buy_count=buy_count,
        by_currency=by_currency,
        by_exchange=by_exchange,
        by_month=by_month,
        available_sessions=available,
    )
