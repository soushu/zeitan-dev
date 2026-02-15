"""bitbank（ビットバンク）取引履歴CSVパーサー."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat

# bitbank 約定履歴CSV の必須ヘッダー
BITBANK_REQUIRED_COLUMNS = ["取引日時", "売/買", "通貨ペア", "数量", "価格", "手数料"]
# 売/買 → 標準 type
SIDE_MAP = {"買": "buy", "売": "sell"}
# 通貨ペア（btc_jpy, eth_jpy 等）→ シンボル
PAIR_TO_SYMBOL = {"btc_jpy": "BTC/JPY", "eth_jpy": "ETH/JPY"}


def _parse_datetime(s: str) -> datetime:
    """bitbank 取引日時文字列を datetime に変換する."""
    s = s.strip()
    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    raise ValueError(f"日時形式が不正です: {s}")


def _pair_to_symbol(pair: str) -> str:
    """通貨ペア表記をシンボルに変換する。例: btc_jpy -> BTC/JPY."""
    key = pair.strip().lower().replace("-", "_")
    return PAIR_TO_SYMBOL.get(key, f"{key.upper().replace('_', '/')}")


class BitbankParser(BaseParser):
    """bitbank の約定履歴CSVを標準フォーマットに変換するパーサー."""

    @property
    def exchange_name(self) -> str:
        """取引所識別子."""
        return "bitbank"

    def validate(self, file_path: str | Path) -> bool:
        """CSV が bitbank 形式か検証する."""
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
        for col in BITBANK_REQUIRED_COLUMNS:
            if col not in df.columns:
                return False
        return True

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """bitbank CSV をパースし、標準フォーマットの取引リストを返す."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")

        if not self.validate(path):
            raise ValueError(f"bitbank 形式ではありません: {path}")

        try:
            df = pd.read_csv(path, encoding="utf-8-sig", index_col=False)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="cp932", index_col=False)

        required = ["取引日時", "売/買", "通貨ペア", "数量", "価格", "手数料"]
        df = df.dropna(subset=[c for c in required if c in df.columns])
        results: list[TransactionFormat] = []

        for _, row in df.iterrows():
            side = str(row["売/買"]).strip()
            if side not in SIDE_MAP:
                continue

            ts = _parse_datetime(str(row["取引日時"]))
            pair = str(row["通貨ペア"]).strip()
            symbol = _pair_to_symbol(pair)
            amount = float(row["数量"])
            price = float(row["価格"])
            fee = float(row["手数料"]) if pd.notna(row["手数料"]) else 0.0

            results.append(
                TransactionFormat(
                    timestamp=ts,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=SIDE_MAP[side],
                    amount=amount,
                    price=price,
                    fee=fee,
                )
            )

        return results
