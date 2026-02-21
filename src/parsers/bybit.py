"""BybitのCSVパーサー."""

from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat


class BybitParser(BaseParser):
    """BybitのCSV取引履歴をパースする.

    Bybit CSV形式:
    - Date(UTC): 取引日時（UTC）
    - Pair: 通貨ペア（例: BTCUSDT）
    - Side: Buy or Sell
    - Filled Price: 約定価格
    - Qty: 約定数量
    - Fee: 手数料
    - Fee Asset: 手数料通貨
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "bybit"

    def validate(self, file_path: str | Path) -> bool:
        """CSVがBybit形式か検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            required_cols = {"Date(UTC)", "Pair", "Side", "Filled Price", "Qty", "Fee"}
            return required_cols.issubset(set(df.columns))
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """BybitのCSVをパースして標準形式に変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            # 日時のパース（UTC）
            date_str = str(row["Date(UTC)"])
            timestamp = pd.to_datetime(date_str).to_pydatetime()

            # 通貨ペアの変換（BTCUSDT → BTC/USDT）
            pair = str(row["Pair"])
            if "USDT" in pair:
                symbol = pair.replace("USDT", "/USDT")
            elif "USDC" in pair:
                symbol = pair.replace("USDC", "/USDC")
            elif "BTC" in pair and pair != "BTC":
                symbol = pair.replace("BTC", "/BTC")
            elif "ETH" in pair and pair != "ETH":
                symbol = pair.replace("ETH", "/ETH")
            else:
                symbol = pair

            # 売買区分
            side = str(row["Side"]).upper()
            tx_type = "buy" if side == "BUY" else "sell"

            # 数量・価格・手数料
            amount = float(row["Qty"])
            price = float(row["Filled Price"])
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
