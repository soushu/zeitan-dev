"""ポートフォリオ集計ユーティリティ."""

from collections import defaultdict
from sqlalchemy.orm import Session
from src.models.orm import CalcSession, Transaction


def calculate_portfolio(db: Session, user_id: int | None = None) -> dict:
    """全セッションの取引データからポートフォリオを集計する.

    Args:
        db: DBセッション
        user_id: ユーザーID（Noneなら全ユーザー）

    Returns:
        ポートフォリオデータ辞書
    """
    query = db.query(Transaction).join(CalcSession)
    if user_id is not None:
        query = query.filter(CalcSession.user_id == user_id)

    # 最新セッションの取引のみ使用（同じデータの重複を避ける）
    latest_session_query = db.query(CalcSession)
    if user_id is not None:
        latest_session_query = latest_session_query.filter(CalcSession.user_id == user_id)
    latest_session = latest_session_query.order_by(CalcSession.created_at.desc()).first()

    if latest_session is None:
        return {
            "total_invested": 0,
            "holdings": [],
        }

    transactions = (
        db.query(Transaction)
        .filter(Transaction.session_id == latest_session.id)
        .order_by(Transaction.timestamp)
        .all()
    )

    # 通貨ごとの保有量と投資額を集計
    holdings: dict[str, dict] = defaultdict(lambda: {
        "amount": 0.0,
        "total_cost": 0.0,
        "last_price": 0.0,
        "buy_count": 0,
        "sell_count": 0,
    })

    for tx in transactions:
        symbol = tx.symbol
        h = holdings[symbol]
        h["last_price"] = tx.price  # 最終取引価格を記録

        if tx.type in ("buy", "airdrop", "fork", "reward", "transfer_in", "nft_buy"):
            h["amount"] += tx.amount
            h["total_cost"] += tx.amount * tx.price + tx.fee
            h["buy_count"] += 1
        elif tx.type in ("sell", "swap", "nft_sell", "transfer_out"):
            h["amount"] -= tx.amount
            h["sell_count"] += 1

    # 保有量 > 0 の通貨のみ抽出
    result_holdings = []
    total_value = 0.0
    total_cost = 0.0

    for symbol, h in holdings.items():
        if h["amount"] <= 1e-8:
            continue

        avg_cost = h["total_cost"] / max(h["amount"] + (h["sell_count"] * h["amount"] / max(h["buy_count"], 1)), 1e-8)
        current_value = h["amount"] * h["last_price"]
        cost_basis = h["amount"] * avg_cost if avg_cost > 0 else 0
        unrealized_pnl = current_value - cost_basis

        result_holdings.append({
            "symbol": symbol,
            "amount": round(h["amount"], 8),
            "average_cost": round(avg_cost, 2),
            "last_price": round(h["last_price"], 2),
            "current_value": round(current_value, 2),
            "cost_basis": round(cost_basis, 2),
            "unrealized_pnl": round(unrealized_pnl, 2),
        })

        total_value += current_value
        total_cost += cost_basis

    # allocation_pct を計算
    for h in result_holdings:
        h["allocation_pct"] = round(h["current_value"] / total_value * 100, 1) if total_value > 0 else 0

    result_holdings.sort(key=lambda x: x["current_value"], reverse=True)

    return {
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "unrealized_pnl": round(total_value - total_cost, 2),
        "holdings": result_holdings,
        "session_id": latest_session.id,
        "calc_method": latest_session.calc_method,
    }
