"""Calculate Router."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.models import (
    CalculateRequest,
    CalculateResponseWithSession,
    ErrorResponse,
    TradeResultResponse,
)
from src.calculators import MovingAverageCalculator, TotalAverageCalculator
from src.parsers.base import TransactionFormat
from src.utils.database import get_db
from src.utils.db_service import save_calculation

router = APIRouter()


@router.post(
    "/calculate",
    response_model=CalculateResponseWithSession,
    responses={400: {"model": ErrorResponse}},
)
async def calculate_tax(request: CalculateRequest, db: Session = Depends(get_db)):
    """税金計算を実行する.

    Args:
        request: 計算リクエスト（取引データと計算方法）
        db: DB セッション。

    Returns:
        計算結果（各取引の損益、総損益、session_id）

    Raises:
        HTTPException: 計算に失敗した場合
    """
    try:
        # リクエストをTransactionFormatに変換
        transactions: list[TransactionFormat] = [
            TransactionFormat(
                timestamp=tx.timestamp,
                exchange=tx.exchange,
                symbol=tx.symbol,
                type=tx.type,
                amount=tx.amount,
                price=tx.price,
                fee=tx.fee,
            )
            for tx in request.transactions
        ]

        # 計算方法を選択
        if request.method == "moving_average":
            calculator = MovingAverageCalculator()
        elif request.method == "total_average":
            calculator = TotalAverageCalculator()
        else:
            raise HTTPException(
                status_code=400,
                detail=f"無効な計算方法: {request.method}",
            )

        # 計算実行
        results = calculator.calculate(transactions)
        total_pl = calculator.get_total_profit_loss(results)

        # レスポンス形式に変換
        result_responses = [
            TradeResultResponse(
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
            for r in results
        ]

        # DB に保存
        calc_session = save_calculation(
            db=db,
            transactions=transactions,
            results=results,
            total_profit_loss=total_pl,
            calc_method=request.method,
        )

        return CalculateResponseWithSession(
            results=result_responses,
            total_profit_loss=total_pl,
            method=request.method,
            session_id=calc_session.id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"計算エラー: {str(e)}")
