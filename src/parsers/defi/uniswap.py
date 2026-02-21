"""Uniswap DEX Parser."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from ..base import BaseParser, TransactionFormat


class UniswapParser(BaseParser):
    """Uniswap DEX取引をパースする.

    期待されるCSVフォーマット:
    - Timestamp: 取引日時（ISO 8601形式）
    - Token In: 売却トークンシンボル
    - Amount In: 売却数量
    - Token Out: 購入トークンシンボル
    - Amount Out: 購入数量
    - Price USD: USD建て価格（オプション）
    - Fee: 手数料（USD）
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "uniswap"

    def validate(self, file_path: str | Path) -> bool:
        """CSVがUniswap形式に沿っているか検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            required_cols = {"Timestamp", "Token In", "Amount In", "Token Out", "Amount Out"}
            return required_cols.issubset(set(df.columns))
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """Uniswap CSVをパースし、標準フォーマットに変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            timestamp_str = str(row["Timestamp"])
            token_in = str(row["Token In"])
            amount_in = float(row["Amount In"])
            token_out = str(row["Token Out"])
            amount_out = float(row["Amount Out"])

            # 価格情報（オプション）
            price_usd = float(row.get("Price USD", 0))
            fee = float(row.get("Fee", 0))

            # タイムスタンプをパース
            try:
                # ISO 8601形式をパース
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                # Unix timestampの場合
                timestamp = datetime.fromtimestamp(float(timestamp_str))

            # Swap取引（売却）を記録
            # symbolは "TokenIn/TokenOut" の形式
            symbol = f"{token_in}/{token_out}"

            # 価格は売却トークンの単価（TokenOut建て）
            # price = Amount Out / Amount In
            price = amount_out / amount_in if amount_in > 0 else 0

            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type="swap",
                    amount=amount_in,
                    price=price,
                    fee=fee,
                )
            )

            # 購入トークンの取得も記録
            # 逆の取引として buy を記録
            buy_symbol = f"{token_out}/JPY"  # 仮にJPY建てとする
            buy_price = price_usd if price_usd > 0 else 0  # USD価格があればそれを使用

            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=buy_symbol,
                    type="buy",
                    amount=amount_out,
                    price=buy_price,
                    fee=0,  # 手数料は売却側に含めているので0
                )
            )

        return transactions
