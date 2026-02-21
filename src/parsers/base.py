"""取引所CSVパーサーの抽象基底クラス.

トランザクションタイプの説明:
- 'buy': 通常の購入取引
- 'sell': 通常の売却取引
- 'airdrop': エアドロップによる無償付与（税法上は雑所得、受取時の時価で取得）
- 'fork': ハードフォークによる新通貨取得（税法上は雑所得、受取時の時価で取得）
- 'reward': ステーキング・マイニング報酬（税法上は雑所得、受取時の時価で取得）
- 'transfer_in': 他の取引所・ウォレットからの受取（課税なし、元の取得原価を引き継ぐ）
- 'transfer_out': 他の取引所・ウォレットへの送金（課税なし、保有数量から減算）
- 'swap': DeFiプロトコルでのトークン交換（売却と購入の組み合わせとして処理）
- 'liquidity_add': 流動性プールへの資産預入（保有数量から減算、LPトークン受取）
- 'liquidity_remove': 流動性プールからの資産引出（LPトークン消費、資産受取）
- 'lending': レンディングプロトコルでの貸出・借入
- 'nft_buy': NFTの購入（購入額 + 手数料が取得原価）
- 'nft_sell': NFTの売却（売却額 - 手数料 - 取得原価 = 損益）
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TypedDict


class TransactionFormat(TypedDict):
    """標準取引レコード形式（全パーサーの共通出力）."""

    timestamp: datetime
    exchange: str
    symbol: str
    type: str  # 'buy', 'sell', 'airdrop', 'fork', 'reward', 'transfer_in', 'transfer_out', 'swap', 'liquidity_add', 'liquidity_remove', 'lending', 'nft_buy', 'nft_sell'
    amount: float
    price: float  # エアドロップ・報酬の場合は受取時の時価、送金の場合は0、DeFi/NFTは市場価格
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
