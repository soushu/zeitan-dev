"""Liquidity Pool (Uniswap V2/V3, Sushiswap等) Parser."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from ..base import BaseParser, TransactionFormat


class LiquidityPoolParser(BaseParser):
    """流動性プール取引をパースする.

    期待されるCSVフォーマット:
    - Timestamp: 取引日時（ISO 8601形式）
    - Action: 取引タイプ（Add Liquidity, Remove Liquidity）
    - Token A: トークンAシンボル
    - Amount A: トークンA数量
    - Token B: トークンBシンボル
    - Amount B: トークンB数量
    - LP Token: LPトークン数量
    - Price USD: USD建て価格（オプション）
    - Fee: 手数料（USD）
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "liquidity_pool"

    def validate(self, file_path: str | Path) -> bool:
        """CSVが流動性プール形式に沿っているか検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            required_cols = {"Timestamp", "Action", "Token A", "Amount A", "Token B", "Amount B"}
            return required_cols.issubset(set(df.columns))
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """流動性プールCSVをパースし、標準フォーマットに変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            timestamp_str = str(row["Timestamp"])
            action = str(row["Action"]).lower()
            token_a = str(row["Token A"])
            amount_a = float(row["Amount A"])
            token_b = str(row["Token B"])
            amount_b = float(row["Amount B"])

            # オプション情報
            lp_token = float(row.get("LP Token", 0))
            price_usd = float(row.get("Price USD", 0))
            fee = float(row.get("Fee", 0))

            # タイムスタンプをパース
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.fromtimestamp(float(timestamp_str))

            # アクションに応じて取引タイプを決定
            if "add" in action:
                # Add Liquidity = 流動性追加
                tx_type = "liquidity_add"
            elif "remove" in action:
                # Remove Liquidity = 流動性削除
                tx_type = "liquidity_remove"
            else:
                tx_type = "liquidity_add"  # デフォルト

            # Token A の取引を記録
            symbol_a = f"{token_a}/JPY"
            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=symbol_a,
                    type=tx_type,
                    amount=amount_a,
                    price=price_usd,
                    fee=fee / 2 if fee > 0 else 0,  # 手数料を2つのトークンで分割
                )
            )

            # Token B の取引を記録
            symbol_b = f"{token_b}/JPY"
            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=symbol_b,
                    type=tx_type,
                    amount=amount_b,
                    price=price_usd,
                    fee=fee / 2 if fee > 0 else 0,
                )
            )

        return transactions
