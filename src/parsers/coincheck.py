"""Coincheck 取引履歴CSVパーサー."""

import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat

# Coincheck CSV の必須ヘッダー（通貨量は BTC(量) 等のいずれかがあればよい）
COINCHECK_REQUIRED_COLUMNS = ["日時", "操作", "レート(円)", "手数料(円)"]
# 操作 → 標準 type（そのまま小文字で使用）
OPERATION_MAP = {"buy": "buy", "sell": "sell"}
# 通貨列パターン: "BTC(量)", "ETH(量)" など（円(量) を除く）
AMOUNT_COL_PATTERN = re.compile(r"^([A-Za-z]+)\(量\)$")


def _parse_datetime(s: str) -> datetime:
    """Coincheck 日時文字列を datetime に変換する."""
    return datetime.strptime(s.strip(), "%Y-%m-%d %H:%M:%S")


def _find_crypto_amount_columns(columns: list[str]) -> list[tuple[str, str]]:
    """列名から (列名, シンボル) のリストを返す。例: BTC(量) -> ('BTC(量)', 'BTC/JPY')."""
    result: list[tuple[str, str]] = []
    for col in columns:
        m = AMOUNT_COL_PATTERN.match(col.strip())
        if m and m.group(1) != "円":
            currency = m.group(1).upper()
            result.append((col, f"{currency}/JPY"))
    return result


class CoincheckParser(BaseParser):
    """Coincheck の取引履歴CSVを標準フォーマットに変換するパーサー."""

    @property
    def exchange_name(self) -> str:
        """取引所識別子."""
        return "coincheck"

    def validate(self, file_path: str | Path) -> bool:
        """CSV が Coincheck 形式か検証する."""
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
        for col in COINCHECK_REQUIRED_COLUMNS:
            if col not in df.columns:
                return False
        if not _find_crypto_amount_columns(list(df.columns)):
            return False
        return True

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """Coincheck CSV をパースし、標準フォーマットの取引リストを返す."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")

        if not self.validate(path):
            raise ValueError(f"Coincheck 形式ではありません: {path}")

        try:
            df = pd.read_csv(path, encoding="utf-8-sig", index_col=False)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="cp932", index_col=False)

        crypto_columns = _find_crypto_amount_columns(list(df.columns))
        if not crypto_columns:
            return []

        required = ["日時", "操作", "レート(円)", "手数料(円)"]
        df = df.dropna(subset=[c for c in required if c in df.columns])
        results: list[TransactionFormat] = []

        for _, row in df.iterrows():
            op = str(row["操作"]).strip().lower()
            if op not in OPERATION_MAP:
                continue
            price = float(row["レート(円)"])
            fee_jpy = 0.0
            if "手数料(円)" in row.index and pd.notna(row["手数料(円)"]):
                try:
                    fee_jpy = float(row["手数料(円)"])
                except (TypeError, ValueError):
                    pass

            # いずれかの通貨量列で非ゼロのものを採用（1行1通貨想定）
            amount = None
            symbol = None
            for col_name, sym in crypto_columns:
                if col_name not in row.index:
                    continue
                try:
                    val = float(row[col_name])
                except (TypeError, ValueError):
                    continue
                if val != 0:
                    amount = val
                    symbol = sym
                    break

            if amount is None or symbol is None:
                continue

            ts = _parse_datetime(str(row["日時"]))
            results.append(
                TransactionFormat(
                    timestamp=ts,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=OPERATION_MAP[op],
                    amount=amount,
                    price=price,
                    fee=fee_jpy,
                )
            )

        return results
