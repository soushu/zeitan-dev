"""CoinbaseのCSVパーサー."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat


class CoinbaseParser(BaseParser):
    """CoinbaseのCSV取引履歴をパースする.

    Coinbase CSV形式:
    - Timestamp: 取引日時
    - Transaction Type: Buy, Sell等
    - Asset: 資産名（例: BTC）
    - Quantity Transacted: 取引数量
    - Spot Price Currency: 決済通貨（USD, JPY等）
    - Spot Price at Transaction: 取引時の価格
    - Fees and/or Spread: 手数料
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "coinbase"

    def validate(self, file_path: str | Path) -> bool:
        """CSVがCoinbase形式か検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            # Coinbase CSVの必須カラムをチェック
            required_cols = {
                "Timestamp",
                "Transaction Type",
                "Asset",
                "Quantity Transacted",
            }
            return required_cols.issubset(set(df.columns))
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """CoinbaseのCSVをパースして標準形式に変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            # トランザクションタイプ
            tx_type_raw = str(row["Transaction Type"]).lower()

            # Buy/Sell以外はスキップ（Receive, Send等）
            if "buy" in tx_type_raw:
                tx_type = "buy"
            elif "sell" in tx_type_raw:
                tx_type = "sell"
            else:
                continue  # その他のトランザクションはスキップ

            # 日時のパース
            timestamp_str = str(row["Timestamp"])
            timestamp = pd.to_datetime(timestamp_str).to_pydatetime()

            # 資産名と通貨ペア
            asset = str(row["Asset"])
            spot_currency = str(row.get("Spot Price Currency", "USD"))
            symbol = f"{asset}/{spot_currency}"

            # 数量・価格・手数料
            amount = abs(float(row["Quantity Transacted"]))
            price = float(row.get("Spot Price at Transaction", 0.0))
            fee = float(row.get("Fees and/or Spread", 0.0))

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
