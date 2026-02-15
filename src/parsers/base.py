"""取引所CSVパーサーの抽象基底クラス."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class TransactionFormat(TypedDict):
    """標準取引レコード形式（全パーサーの共通出力）."""

    timestamp: datetime
    exchange: str
    symbol: str
    type: str  # 'buy' or 'sell'
    amount: float
    price: float
    fee: float


class BaseParser(ABC):
    """取引所CSVを標準フォーマットに変換するパーサーの抽象基底クラス.

    各取引所（bitFlyer, Coincheck, GMOコイン, bitbank）用パーサーは
    このクラスを継承し、parse() と validate() を実装する。
    """

    @property
    @abstractmethod
    def exchange_name(self) -> str:
        """取引所識別子を返す.

        Returns:
            'bitflyer', 'coincheck', 'gmo', 'bitbank' のいずれか。
        """
        ...

    @abstractmethod
    def parse(self, file_path: str | Path) -> list[TransactionFormat]:
        """CSVファイルをパースし、標準フォーマットの取引リストを返す.

        Args:
            file_path: 取引履歴CSVのパス（文字列または Path）。

        Returns:
            TransactionFormat のリスト。各要素は timestamp, exchange, symbol,
            type, amount, price, fee を持つ。

        Raises:
            FileNotFoundError: ファイルが存在しない場合。
            ValueError: CSV形式が不正な場合。
        """
        ...

    @abstractmethod
    def validate(self, file_path: str | Path) -> bool:
        """CSVがこの取引所の形式に沿っているか検証する.

        Args:
            file_path: 取引履歴CSVのパス（文字列または Path）。

        Returns:
            形式が正しければ True、そうでなければ False。

        Raises:
            FileNotFoundError: ファイルが存在しない場合。
        """
        ...
