"""LINE BITMAX 取引履歴パーサー."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat

# LINE BITMAX の必須列名（XLSXフォーマット）
LINEBITMAX_REQUIRED_COLUMNS = ["約定日時", "売買", "通貨ペア", "約定数量", "約定レート", "手数料"]
# 売買 → 標準 type
KIND_MAP = {"買": "buy", "購入": "buy", "売": "sell", "売却": "sell"}


def _parse_datetime(s: str) -> datetime:
    """LINE BITMAX 日時文字列を datetime に変換する."""
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


class LineBitmaxParser(BaseParser):
    """LINE BITMAX の取引履歴を標準フォーマットに変換するパーサー.

    Note:
        LINE BITMAXはXLSX形式で取引履歴を提供します。
        列名: 注文番号, 約定日時, 通貨ペア, 取引種別, 売買, 注文方式,
              約定数量, 約定レート, 取引金額, 手数料
        CSVとして保存されている場合も対応します。
    """

    @property
    def exchange_name(self) -> str:
        """取引所識別子."""
        return "linebitmax"

    def validate(self, file_path: str | Path) -> bool:
        """ファイルが LINE BITMAX 形式か検証する."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")
        if not path.is_file():
            return False

        # XLSX または CSV に対応
        try:
            if path.suffix.lower() in [".xlsx", ".xls"]:
                df = pd.read_excel(path, nrows=1)
            else:
                df = pd.read_csv(path, encoding="utf-8-sig", nrows=1, index_col=False)
        except Exception:
            try:
                df = pd.read_csv(path, encoding="cp932", nrows=1, index_col=False)
            except Exception:
                return False

        for col in LINEBITMAX_REQUIRED_COLUMNS:
            if col not in df.columns:
                return False
        return True

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """LINE BITMAX ファイルをパースし、標準フォーマットの取引リストを返す."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")

        if not self.validate(path):
            raise ValueError(f"LINE BITMAX 形式ではありません: {path}")

        # XLSX または CSV を読み込み
        if path.suffix.lower() in [".xlsx", ".xls"]:
            df = pd.read_excel(path)
        else:
            try:
                df = pd.read_csv(path, encoding="utf-8-sig", index_col=False)
            except UnicodeDecodeError:
                df = pd.read_csv(path, encoding="cp932", index_col=False)

        required = ["約定日時", "売買", "通貨ペア", "約定数量", "約定レート"]
        df = df.dropna(subset=[c for c in required if c in df.columns])
        results: list[TransactionFormat] = []

        for _, row in df.iterrows():
            kind = str(row["売買"]).strip()
            if kind not in KIND_MAP:
                continue

            # 通貨ペアはそのまま使用（"BTC/JPY" などの形式を想定）
            symbol = str(row["通貨ペア"]).strip().upper()
            # スラッシュがない場合は /JPY を追加
            if "/" not in symbol:
                symbol = f"{symbol}/JPY"

            ts = _parse_datetime(str(row["約定日時"]))
            amount = float(row["約定数量"])
            price = float(row["約定レート"])
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
