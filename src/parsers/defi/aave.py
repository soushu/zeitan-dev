"""Aave Lending Protocol Parser."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from ..base import BaseParser, TransactionFormat


class AaveParser(BaseParser):
    """Aave レンディングプロトコルの取引をパースする.

    期待されるCSVフォーマット:
    - Timestamp: 取引日時（ISO 8601形式）
    - Action: 取引タイプ（Deposit, Withdraw, Borrow, Repay）
    - Asset: 資産シンボル（例: ETH, USDC）
    - Amount: 数量
    - Price USD: USD建て価格
    - Fee: 手数料（USD）
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "aave"

    def validate(self, file_path: str | Path) -> bool:
        """CSVがAave形式に沿っているか検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            required_cols = {"Timestamp", "Action", "Asset", "Amount"}
            return required_cols.issubset(set(df.columns))
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """Aave CSVをパースし、標準フォーマットに変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            timestamp_str = str(row["Timestamp"])
            action = str(row["Action"]).lower()
            asset = str(row["Asset"])
            amount = float(row["Amount"])

            # 価格情報（オプション）
            price_usd = float(row.get("Price USD", 0))
            fee = float(row.get("Fee", 0))

            # タイムスタンプをパース
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.fromtimestamp(float(timestamp_str))

            # symbolは "Asset/JPY" の形式（仮にJPY建て）
            symbol = f"{asset}/JPY"

            # アクションに応じて取引タイプを決定
            if action == "deposit":
                # Deposit = 資産を預ける（lending扱い）
                tx_type = "lending"
            elif action == "withdraw":
                # Withdraw = 資産を引き出す（transfer_in扱い）
                tx_type = "transfer_in"
            elif action == "borrow":
                # Borrow = 資産を借りる（transfer_in扱い）
                tx_type = "transfer_in"
            elif action == "repay":
                # Repay = 借金を返済（transfer_out扱い）
                tx_type = "transfer_out"
            else:
                # その他は lending として扱う
                tx_type = "lending"

            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=tx_type,
                    amount=amount,
                    price=price_usd,
                    fee=fee,
                )
            )

        return transactions
