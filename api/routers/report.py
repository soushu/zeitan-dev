"""Report Router."""

import io

import pandas as pd
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response, StreamingResponse

from api.models import CalculateRequest, ErrorResponse, ExchangeInfo, ExchangesResponse
from src.calculators import MovingAverageCalculator, TotalAverageCalculator
from src.parsers.base import TransactionFormat
from src.reporters import PDFReporter

router = APIRouter()


@router.post(
    "/report/csv",
    response_class=StreamingResponse,
    responses={400: {"model": ErrorResponse}},
)
async def generate_csv_report(request: CalculateRequest):
    """CSVレポートを生成する.

    Args:
        request: 計算リクエスト

    Returns:
        CSVファイル（ダウンロード）

    Raises:
        HTTPException: レポート生成に失敗した場合
    """
    try:
        # 取引データを変換
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

        # 計算実行
        if request.method == "moving_average":
            calculator = MovingAverageCalculator()
        else:
            calculator = TotalAverageCalculator()

        results = calculator.calculate(transactions)

        # DataFrameに変換
        df = pd.DataFrame(results)

        # CSVバイナリ生成
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")

        return StreamingResponse(
            io.BytesIO(csv_bytes),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=zeitan_report_{request.method}.csv"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSVレポート生成エラー: {str(e)}")


@router.post(
    "/report/pdf",
    response_class=Response,
    responses={400: {"model": ErrorResponse}},
)
async def generate_pdf_report(request: CalculateRequest):
    """PDFレポートを生成する.

    Args:
        request: 計算リクエスト

    Returns:
        PDFファイル（ダウンロード）

    Raises:
        HTTPException: レポート生成に失敗した場合
    """
    try:
        # 取引データを変換
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

        # 計算実行
        if request.method == "moving_average":
            calculator = MovingAverageCalculator()
            calc_method_jp = "移動平均法"
        else:
            calculator = TotalAverageCalculator()
            calc_method_jp = "総平均法"

        results = calculator.calculate(transactions)
        total_pl = calculator.get_total_profit_loss(results)

        # PDF生成
        reporter = PDFReporter()
        pdf_bytes = reporter.generate(
            results=results,
            total_profit_loss=total_pl,
            calc_method=calc_method_jp,
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=zeitan_report_{request.method}.pdf"
            },
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDFレポート生成エラー: {str(e)}")


@router.get("/exchanges", response_model=ExchangesResponse)
async def get_exchanges():
    """対応取引所一覧を取得する.

    Returns:
        取引所一覧
    """
    exchanges = [
        # 国内取引所
        ExchangeInfo(id="bitflyer", name="bitFlyer", category="domestic"),
        ExchangeInfo(id="coincheck", name="Coincheck", category="domestic"),
        ExchangeInfo(id="gmo", name="GMOコイン", category="domestic"),
        ExchangeInfo(id="bitbank", name="bitbank", category="domestic"),
        ExchangeInfo(id="sbivc", name="SBI VCトレード", category="domestic"),
        ExchangeInfo(id="rakuten", name="楽天ウォレット", category="domestic"),
        ExchangeInfo(id="linebitmax", name="LINE BITMAX", category="domestic"),
        # 海外取引所
        ExchangeInfo(id="binance", name="Binance", category="international"),
        ExchangeInfo(id="coinbase", name="Coinbase", category="international"),
        ExchangeInfo(id="kraken", name="Kraken", category="international"),
    ]

    return ExchangesResponse(exchanges=exchanges, total=len(exchanges))
