"""GMOコイン 取引履歴CSVパーサー."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from .base import BaseParser, TransactionFormat

# GMOコイン CSV の必須ヘッダー
GMO_REQUIRED_COLUMNS = ["取引日時", "銘柄", "取引区分", "取引数量", "取引レート", "手数料"]
# 取引区分 → 標準 type
TRADE_TYPE_MAP = {
    "現物買い": "buy",
    "現物売り": "sell",
}
# 銘柄 → シンボル（現物円建て）
SYMBOL_MAP = {"BTC": "BTC/JPY", "ETH": "ETH/JPY"}


def _parse_datetime(s: str) -> datetime:
    """GMOコイン 取引日時文字列を datetime に変換する."""
    return datetime.strptime(s.strip(), "%Y/%m/%d %H:%M:%S")


class GMOParser(BaseParser):
    """GMOコインの取引履歴CSVを標準フォーマットに変換するパーサー."""

    @property
    def exchange_name(self) -> str:
        """取引所識別子."""
        return "gmo"

    def validate(self, file_path: str | Path) -> bool:
        """CSV が GMOコイン形式か検証する."""
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
        for col in GMO_REQUIRED_COLUMNS:
            if col not in df.columns:
                return False
        return True

    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """GMOコイン CSV をパースし、標準フォーマットの取引リストを返す."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"ファイルが存在しません: {path}")

        if not self.validate(path):
            raise ValueError(f"GMOコイン形式ではありません: {path}")

        try:
            df = pd.read_csv(path, encoding="utf-8-sig", index_col=False)
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="cp932", index_col=False)

        required = ["取引日時", "銘柄", "取引区分", "取引数量", "取引レート", "手数料"]
        df = df.dropna(subset=[c for c in required if c in df.columns])
        results: list[TransactionFormat] = []

        for _, row in df.iterrows():
            trade_type = str(row["取引区分"]).strip()
            if trade_type not in TRADE_TYPE_MAP:
                continue
            currency = str(row["銘柄"]).strip().upper()
            symbol = SYMBOL_MAP.get(currency, f"{currency}/JPY")

            ts = _parse_datetime(str(row["取引日時"]))
            amount = float(row["取引数量"])
            price = float(row["取引レート"])
            fee = float(row["手数料"]) if pd.notna(row["手数料"]) else 0.0

            results.append(
                TransactionFormat(
                    timestamp=ts,
                    exchange=self.exchange_name,
                    symbol=symbol,
                    type=TRADE_TYPE_MAP[trade_type],
                    amount=amount,
                    price=price,
                    fee=fee,
                )
            )

        return results
