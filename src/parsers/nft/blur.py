"""Blur NFT Marketplace Parser."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from ..base import BaseParser, TransactionFormat


class BlurParser(BaseParser):
    """Blur NFTマーケットプレイスの取引をパースする.

    期待されるCSVフォーマット:
    - Date: 取引日時（ISO 8601形式）
    - Type: 取引タイプ（Buy, Sell, Bid, List）
    - Collection: NFTコレクション名
    - Item: NFTアイテム名
    - Price ETH: 価格（ETH建て）
    - Price USD: USD建て価格
    - Quantity: 数量（通常は1）
    - Gas: ガス代（ETH）
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "blur"

    def validate(self, file_path: str | Path) -> bool:
        """CSVがBlur形式に沿っているか検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            required_cols = {"Date", "Type", "Collection", "Price ETH"}
            return required_cols.issubset(set(df.columns))
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """Blur CSVをパースし、標準フォーマットに変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            timestamp_str = str(row["Date"])
            tx_type_str = str(row["Type"]).lower()
            collection = str(row["Collection"])
            price_eth = float(row["Price ETH"])

            # オプション情報
            item = str(row.get("Item", "Unknown"))
            quantity = float(row.get("Quantity", 1))
            price_usd = float(row.get("Price USD", 0))
            gas = float(row.get("Gas", 0))

            # タイムスタンプをパース
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.fromtimestamp(float(timestamp_str))

            # symbolは "Collection/Item" の形式
            symbol = f"{collection}/{item}"

            # 取引タイプに応じて処理
            if tx_type_str == "buy":
                tx_type = "nft_buy"
            elif tx_type_str == "sell":
                tx_type = "nft_sell"
            elif tx_type_str in ("bid", "list"):
                # Bid/Listは実際の取引ではないのでスキップ
                continue
            else:
                tx_type = "nft_buy"

            # 価格はUSD建てがあればそれを使用、なければETH価格
            final_price = price_usd if price_usd > 0 else price_eth

            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=tx_type,
                    amount=quantity,
                    price=final_price,
                    fee=gas,
                )
            )

        return transactions
