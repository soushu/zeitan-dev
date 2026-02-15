"""bitFlyer 取引履歴CSVパーサー."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat

# bitFlyer CSV の必須ヘッダー
BITFLYER_REQUIRED_COLUMNS = ["日時", "種別", "通貨", "数量", "価格", "手数料"]
# 種別 → 標準 type
KIND_MAP = {"買": "buy", "売": "sell"}
# 通貨 → シンボル（現物円建て）
CURRENCY_TO_SYMBOL = {"BTC": "BTC/JPY", "ETH": "ETH/JPY"}


def _parse_datetime(s: str) -> datetime:
    """bitFlyer 日時文字列を datetime に変換する."""
    return datetime.strptime(s.strip(), "%Y/%m/%d %H:%M:%S")


class BitflyerParser(BaseParser):
    """bitFlyer の取引履歴CSVを標準フォーマットに変換するパーサー."""

    @property
    def exchange_name(self) -> str:
        """取引所識別子."""
        return "bitflyer"

    def validate(self, file_path: str | Path) -> bool:
        """CSV が bitFlyer 形式か検証する."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")
        if not path.is_file():
            return False
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", nrows=1, index_col=False)
        except Exception:
            try:
                df = pd.read_csv(path, encoding="cp932", nrows=1, index_col=False)
            except Exception:
                return False
        for col in BITFLYER_REQUIRED_COLUMNS:
            if col not in df.columns:
                return False
        return True

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """bitFlyer CSV をパースし、標準フォーマットの取引リストを返す."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")

        if not self.validate(path):
            raise ValueError(f"bitFlyer 形式ではありません: {path}")

        try:
            df = pd.read_csv(path, encoding="utf-8-sig", index_col=False)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="cp932", index_col=False)

        required = ["日時", "種別", "通貨", "数量", "価格"]
        df = df.dropna(subset=[c for c in required if c in df.columns])
        results: list[TransactionFormat] = []

        for _, row in df.iterrows():
            kind = str(row["種別"]).strip()
            if kind not in KIND_MAP:
                continue
            currency = str(row["通貨"]).strip().upper()
            symbol = CURRENCY_TO_SYMBOL.get(currency, f"{currency}/JPY")

            ts = _parse_datetime(str(row["日時"]))
            amount = float(row["数量"])
            price = float(row["価格"])
            fee = float(row["手数料"]) if pd.notna(row["手数料"]) else 0.0

            results.append(
                TransactionFormat(
                    timestamp=ts,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=KIND_MAP[kind],
                    amount=amount,
                    price=price,
                    fee=fee,
                )
            )

        return results
