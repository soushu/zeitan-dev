"""DB操作サービス層（ルーターを薄く保つため）."""

from src.models.orm import CalcSession, TradeResultRecord, Transaction
from src.parsers.base import TransactionFormat
from sqlalchemy.orm import Session


def save_calculation(
    db: Session,
    transactions: list[TransactionFormat],
    results: list[dict],
    total_profit_loss: float,
    calc_method: str,
) -> CalcSession:
    """計算結果を DB に保存して CalcSession を返す.

    Args:
        db: DB セッション。
        transactions: 入力取引データ。
        results: 計算結果（dict リスト）。
        total_profit_loss: 総損益。
        calc_method: 計算方法名。

    Returns:
        保存された CalcSession。
    """
    session = CalcSession(
        calc_method=calc_method,
        total_profit_loss=total_profit_loss,
        transaction_count=len(transactions),
    )
    db.add(session)
    db.flush()  # session.id を確定させる

    for tx in transactions:
        db.add(
            Transaction(
                session_id=session.id,
                timestamp=tx["timestamp"],
                exchange=tx["exchange"],
                symbol=tx["symbol"],
                type=tx["type"],
                amount=tx["amount"],
                price=tx["price"],
                fee=tx["fee"],
            )
        )

    for r in results:
        db.add(
            TradeResultRecord(
                session_id=session.id,
                timestamp=r["timestamp"],
                exchange=r["exchange"],
                symbol=r["symbol"],
                type=r["type"],
                amount=r["amount"],
                price=r["price"],
                fee=r["fee"],
                profit_loss=r["profit_loss"],
                average_cost_after=r.get("average_cost_after"),
                average_cost_used=r.get("average_cost_used"),
            )
        )

    db.commit()
    db.refresh(session)
    return session


def get_sessions(db: Session) -> list[CalcSession]:
    """全セッションを新しい順で返す."""
    return (
        db.query(CalcSession).order_by(CalcSession.created_at.desc()).all()
    )


def get_session_detail(db: Session, session_id: int) -> CalcSession | None:
    """セッション詳細（リレーション含む）を返す。存在しなければ None."""
    return db.query(CalcSession).filter(CalcSession.id == session_id).first()
