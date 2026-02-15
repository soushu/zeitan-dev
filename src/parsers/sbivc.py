"""SBI VCトレード 取引履歴CSVパーサー."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat

# SBI VCトレード CSV の想定ヘッダー
# 注: 実際のCSVフォーマットに応じて調整が必要
SBIVC_REQUIRED_COLUMNS = ["約定日時", "取引区分", "銘柄", "約定数量", "約定価格", "手数料"]
# 取引区分 → 標準 type
KIND_MAP = {"買": "buy", "購入": "buy", "売": "sell", "売却": "sell", "現物買い": "buy", "現物売り": "sell"}
# 銘柄 → シンボル（現物円建て）
CURRENCY_TO_SYMBOL = {"BTC": "BTC/JPY", "ETH": "ETH/JPY", "XRP": "XRP/JPY"}


def _parse_datetime(s: str) -> datetime:
    """SBI VCトレード 日時文字列を datetime に変換する."""
    s = s.strip()
    # 一般的なフォーマットを試行
    for fmt in [
        "%Y/%m/%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M",
        "%Y-%m-%d %H:%M",
    ]:
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"日時フォーマットが不正です: {s}")


class SBIVCParser(BaseParser):
    """SBI VCトレード の取引履歴CSVを標準フォーマットに変換するパーサー.

    Note:
        実際のCSVフォーマットは TRADE_RECORD_LIST_xxxxx.csv を想定。
        UTF-8 (BOM付き) エンコーディング。
        実際のCSVに応じて列名やフォーマットの調整が必要な場合があります。
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子."""
        return "sbivc"

    def validate(self, file_path: str | Path) -> bool:
        """CSV が SBI VCトレード 形式か検証する."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")
        if not path.is_file():
            return False
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", nrows=1, index_col=False)
        except Exception:
            try:
                df = pd.read_csv(path, encoding="utf-8", nrows=1, index_col=False)
            except Exception:
                return False
        for col in SBIVC_REQUIRED_COLUMNS:
            if col not in df.columns:
                return False
        return True

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """SBI VCトレード CSV をパースし、標準フォーマットの取引リストを返す."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")

        if not self.validate(path):
            raise ValueError(f"SBI VCトレード 形式ではありません: {path}")

        try:
            df = pd.read_csv(path, encoding="utf-8-sig", index_col=False)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="utf-8", index_col=False)

        required = ["約定日時", "取引区分", "銘柄", "約定数量", "約定価格"]
        df = df.dropna(subset=[c for c in required if c in df.columns])
        results: list[TransactionFormat] = []

        for _, row in df.iterrows():
            kind = str(row["取引区分"]).strip()
            if kind not in KIND_MAP:
                continue
            currency = str(row["銘柄"]).strip().upper()
            # 銘柄が "BTC/JPY" の形式の場合はそのまま、"BTC" の場合は "/JPY" を追加
            if "/" in currency:
                symbol = currency
            else:
                symbol = CURRENCY_TO_SYMBOL.get(currency, f"{currency}/JPY")

            ts = _parse_datetime(str(row["約定日時"]))
            amount = float(row["約定数量"])
            price = float(row["約定価格"])
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
