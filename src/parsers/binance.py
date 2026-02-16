"""BinanceのCSVパーサー."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat


class BinanceParser(BaseParser):
    """BinanceのCSV取引履歴をパースする.

    Binance CSV形式:
    - Date(UTC): 取引日時（UTC）
    - Pair: 通貨ペア（例: BTCUSDT）
    - Side: BUY or SELL
    - Price: 約定価格
    - Executed: 約定数量
    - Amount: 取引金額
    - Fee: 手数料
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "binance"

    def validate(self, file_path: str | Path) -> bool:
        """CSVがBinance形式か検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            # Binance CSVの必須カラムをチェック
            required_cols = {"Date(UTC)", "Pair", "Side", "Price", "Executed", "Fee"}
            return required_cols.issubset(set(df.columns))
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """BinanceのCSVをパースして標準形式に変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            # 日時のパース（UTC）
            date_str = str(row["Date(UTC)"])
            timestamp = pd.to_datetime(date_str).to_pydatetime()

            # 通貨ペアの変換（BTCUSDT → BTC/USDT）
            pair = str(row["Pair"])
            # 一般的な通貨ペアパターン（BTC, ETH, BNB等）
            if "USDT" in pair:
                symbol = pair.replace("USDT", "/USDT")
            elif "BUSD" in pair:
                symbol = pair.replace("BUSD", "/BUSD")
            elif "BTC" in pair and pair != "BTC":
                symbol = pair.replace("BTC", "/BTC")
            elif "ETH" in pair and pair != "ETH":
                symbol = pair.replace("ETH", "/ETH")
            else:
                symbol = pair  # フォールバック

            # 売買区分
            side = str(row["Side"]).upper()
            tx_type = "buy" if side == "BUY" else "sell"

            # 数量・価格・手数料
            amount = float(row["Executed"])
            price = float(row["Price"])
            fee = float(row.get("Fee", 0.0))

            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=tx_type,
                    amount=amount,
                    price=price,
                    fee=fee,
                )
            )

        return transactions
