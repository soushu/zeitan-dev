"""KrakenのCSVパーサー."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat


class KrakenParser(BaseParser):
    """KrakenのCSV取引履歴をパースする.

    Kraken CSV形式:
    - time: 取引日時（Unix timestamp or ISO format）
    - type: buy or sell
    - asset: 資産名
    - amount: 取引数量
    - price: 価格
    - fee: 手数料
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子を返す."""
        return "kraken"

    def validate(self, file_path: str | Path) -> bool:
        """CSVがKraken形式か検証する."""
        try:
            df = pd.read_csv(file_path, encoding="utf-8", nrows=1)
            # Kraken CSVの必須カラムをチェック
            # Krakenは複数のCSVフォーマットがあるため、柔軟に対応
            has_time = "time" in df.columns or "txid" in df.columns
            has_type = "type" in df.columns
            has_pair = "pair" in df.columns or "asset" in df.columns

            return has_time and has_type and has_pair
        except Exception:
            return False

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """KrakenのCSVをパースして標準形式に変換する."""
        df = pd.read_csv(file_path, encoding="utf-8")

        transactions: list[TransactionFormat] = []

        for _, row in df.iterrows():
            # トランザクションタイプ
            tx_type_raw = str(row["type"]).lower()
            if tx_type_raw not in ("buy", "sell"):
                continue  # その他のタイプはスキップ

            # 日時のパース
            time_col = "time" if "time" in df.columns else "txid"
            time_str = str(row[time_col])
            try:
                # Unix timestampの場合
                if time_str.isdigit():
                    timestamp = datetime.fromtimestamp(float(time_str))
                else:
                    # ISO formatの場合
                    timestamp = pd.to_datetime(time_str).to_pydatetime()
            except Exception:
                # パースできない場合は現在時刻
                timestamp = datetime.now()

            # 通貨ペア
            if "pair" in df.columns:
                pair = str(row["pair"])
                # Krakenのペア形式（例: XXBTZUSD → BTC/USD）
                if pair.startswith("XX") or pair.startswith("XZ"):
                    # 先頭のXXやXZを削除
                    pair = pair[2:]
                if "USD" in pair:
                    symbol = pair.replace("USD", "/USD")
                elif "EUR" in pair:
                    symbol = pair.replace("EUR", "/EUR")
                elif "JPY" in pair:
                    symbol = pair.replace("JPY", "/JPY")
                else:
                    symbol = pair
            elif "asset" in df.columns:
                asset = str(row["asset"])
                currency = str(row.get("currency", "USD"))
                symbol = f"{asset}/{currency}"
            else:
                symbol = "UNKNOWN"

            # 数量・価格・手数料
            amount = float(row.get("vol", row.get("amount", 0.0)))
            price = float(row.get("price", 0.0))
            fee = float(row.get("fee", 0.0))

            transactions.append(
                TransactionFormat(
                    timestamp=timestamp,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=tx_type_raw,
                    amount=amount,
                    price=price,
                    fee=fee,
                )
            )

        return transactions
