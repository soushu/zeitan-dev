"""OpenSea NFT Marketplace Parser."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from ..base import BaseParser, TransactionFormat


class OpenSeaParser(BaseParser):
    """OpenSea NFTマーケットプレイスの取引をパースする.

    期待されるCSVフォーマット:
    - Timestamp: 取引日時（ISO 8601形式）
    - Event Type: 取引タイプ（Sale, Purchase, Mint, Transfer）
    - NFT Collection: NFTコレクション名
    - NFT Name: NFT名
    - Token ID: トークンID
    - Quantity: 数量（通常は1）
    - Price: 価格（ETH建て）
    - Price USD: USD建て価格
    - Gas Fee: ガス代（ETH）
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "opensea"

    def validate(self, file_path: str | Path) -> bool:
        """CSVがOpenSea形式に沿っているか検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            required_cols = {"Timestamp", "Event Type", "NFT Collection", "Price"}
            return required_cols.issubset(set(df.columns))
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """OpenSea CSVをパースし、標準フォーマットに変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            timestamp_str = str(row["Timestamp"])
            event_type = str(row["Event Type"]).lower()
            collection = str(row["NFT Collection"])
            price = float(row.get("Price", 0))

            # オプション情報
            quantity = float(row.get("Quantity", 1))
            price_usd = float(row.get("Price USD", 0))
            gas_fee = float(row.get("Gas Fee", 0))
            token_id = str(row.get("Token ID", ""))

            # タイムスタンプをパース
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            except ValueError:
                timestamp = datetime.fromtimestamp(float(timestamp_str))

            # symbolは "Collection/NFT" の形式
            # NFT名があればそれを使用、なければToken IDを使用
            nft_name = str(row.get("NFT Name", f"#{token_id}"))
            symbol = f"{collection}/{nft_name}"

            # イベントタイプに応じて取引タイプを決定
            if event_type in ("purchase", "mint"):
                # Purchase/Mint = NFT購入
                tx_type = "nft_buy"
                # 価格はUSD建てがあればそれを使用、なければETH価格
                final_price = price_usd if price_usd > 0 else price
            elif event_type == "sale":
                # Sale = NFT売却
                tx_type = "nft_sell"
                final_price = price_usd if price_usd > 0 else price
            elif event_type == "transfer":
                # Transfer = 転送（課税なし）
                tx_type = "transfer_in"
                final_price = 0
            else:
                # その他は購入として扱う
                tx_type = "nft_buy"
                final_price = price_usd if price_usd > 0 else price

            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=tx_type,
                    amount=quantity,
                    price=final_price,
                    fee=gas_fee,
                )
            )

        return transactions
