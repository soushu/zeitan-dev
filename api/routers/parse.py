"""CSV Parse Router."""

import tempfile
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from api.models import ErrorResponse, TransactionResponse
from src.parsers import (
    AaveParser,
    BinanceParser,
    BitbankParser,
    BitflyerParser,
    BlurParser,
    BybitParser,
    CoinbaseParser,
    CoincheckParser,
    GMOParser,
    KrakenParser,
    LiquidityPoolParser,
    LineBitmaxParser,
    OpenSeaParser,
    RakutenParser,
    SBIVCParser,
    UniswapParser,
)
from src.parsers.base import BaseParser

router = APIRouter()

# パーサーマッピング
PARSERS: dict[str, BaseParser] = {
    # 国内取引所
    "bitflyer": BitflyerParser(),
    "coincheck": CoincheckParser(),
    "gmo": GMOParser(),
    "bitbank": BitbankParser(),
    "sbivc": SBIVCParser(),
    "rakuten": RakutenParser(),
    "linebitmax": LineBitmaxParser(),
    # 海外取引所
    "binance": BinanceParser(),
    "bybit": BybitParser(),
    "coinbase": CoinbaseParser(),
    "kraken": KrakenParser(),
    # DeFi
    "uniswap": UniswapParser(),
    "aave": AaveParser(),
    "liquidity_pool": LiquidityPoolParser(),
    # NFT
    "opensea": OpenSeaParser(),
    "blur": BlurParser(),
}


def detect_exchange(file_path: Path) -> str | None:
    """CSVファイルから取引所を自動検出する."""
    for exchange_name, parser in PARSERS.items():
        try:
            if parser.validate(file_path):
                return exchange_name
        except Exception:
            continue
    return None


@router.post(
    "/parse",
    response_model=list[TransactionResponse],
    responses={400: {"model": ErrorResponse}},
)
async def parse_csv(file: UploadFile = File(...)):
    """CSVファイルをアップロードしてパースする.

    Args:
        file: CSVファイル

    Returns:
        パースされた取引データのリスト

    Raises:
        HTTPException: パースに失敗した場合
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="ファイル名が必要です")

    # 一時ファイルとして保存
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = Path(temp_file.name)

        # 取引所を自動検出
        exchange = detect_exchange(temp_path)
        if not exchange:
            raise HTTPException(
                status_code=400,
                detail="サポートされていない取引所形式です",
            )

        # パース
        parser = PARSERS[exchange]
        transactions = parser.parse(temp_path)

        # 一時ファイルを削除
        temp_path.unlink()

        # レスポンス形式に変換
        return [
            TransactionResponse(
                timestamp=tx["timestamp"],
                exchange=tx["exchange"],
                symbol=tx["symbol"],
                type=tx["type"],
                amount=tx["amount"],
                price=tx["price"],
                fee=tx["fee"],
            )
            for tx in transactions
        ]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"パースエラー: {str(e)}")
