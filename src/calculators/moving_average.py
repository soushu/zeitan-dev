"""移動平均法による暗号資産税金計算エンジン.

移動平均法:
- 購入時: 新しい平均取得原価 = (既存保有額 + 購入額) / (既存数量 + 購入数量)
- 売却時: 売却損益 = (売却価格 - 平均取得原価) × 売却数量
"""

from datetime import datetime
from typing import TypedDict

from ..parsers.base import TransactionFormat


class HoldingStatus(TypedDict):
    """保有状況."""

    symbol: str  # 通貨ペア（例: BTC/JPY）
    amount: float  # 保有数量
    average_cost: float  # 平均取得原価（円/単位）


class TradeResult(TypedDict):
    """取引結果."""

    timestamp: datetime  # 取引日時
    exchange: str  # 取引所
    symbol: str  # 通貨ペア
    type: str  # 'buy' or 'sell'
    amount: float  # 取引数量
    price: float  # 取引価格（円/単位）
    fee: float  # 手数料（円）
    profit_loss: float  # 損益（円）売却時のみ、購入時は0
    average_cost_after: float  # 取引後の平均取得原価


class MovingAverageCalculator:
    """移動平均法による税金計算エンジン.

    取引を時系列順に処理し、各売却取引での損益を計算します。
    """

    def __init__(self) -> None:
        """計算エンジンを初期化."""
        # 通貨ペアごとの保有状況を管理
        self.holdings: dict[str, HoldingStatus] = {}

    def calculate(self, transactions: list[TransactionFormat]) -> list[TradeResult]:
        """取引リストから損益を計算する.

        Args:
            transactions: TransactionFormatのリスト（時系列順にソート済みを想定）。

        Returns:
            TradeResultのリスト。各取引の損益情報を含む。
        """
        # 取引を時系列順にソート
        sorted_txs = sorted(transactions, key=lambda x: x["timestamp"])
        results: list[TradeResult] = []

        for tx in sorted_txs:
            symbol = tx["symbol"]
            amount = tx["amount"]
            price = tx["price"]
            fee = tx["fee"]
            tx_type = tx["type"]

            # 保有状況の初期化
            if symbol not in self.holdings:
                self.holdings[symbol] = HoldingStatus(
                    symbol=symbol,
                    amount=0.0,
                    average_cost=0.0,
                )

            holding = self.holdings[symbol]
            profit_loss = 0.0

            if tx_type == "buy":
                # 購入時: 平均取得原価を更新
                total_cost_before = holding["amount"] * holding["average_cost"]
                purchase_cost = amount * price + fee  # 手数料は取得原価に含める
                new_amount = holding["amount"] + amount

                if new_amount > 0:
                    new_average_cost = (total_cost_before + purchase_cost) / new_amount
                else:
                    new_average_cost = 0.0

                holding["amount"] = new_amount
                holding["average_cost"] = new_average_cost

            elif tx_type == "sell":
                # 売却時: 損益を計算
                if holding["amount"] <= 0:
                    raise ValueError(
                        f"保有数量不足: {symbol} を売却しようとしましたが、保有数量が 0 です。"
                    )

                sale_revenue = amount * price - fee  # 売却収入から手数料を差し引く
                cost_basis = amount * holding["average_cost"]  # 取得原価
                profit_loss = sale_revenue - cost_basis

                # 保有数量を減らす（平均取得原価は変わらない）
                holding["amount"] -= amount

                if holding["amount"] < 0:
                    raise ValueError(
                        f"保有数量不足: {symbol} の保有数量が負になりました。"
                    )

            # 結果を記録
            results.append(
                TradeResult(
                    timestamp=tx["timestamp"],
                    exchange=tx["exchange"],
                    symbol=symbol,
                    type=tx_type,
                    amount=amount,
                    price=price,
                    fee=fee,
                    profit_loss=profit_loss,
                    average_cost_after=holding["average_cost"],
                )
            )

        return results

    def get_holdings(self) -> dict[str, HoldingStatus]:
        """現在の保有状況を取得する.

        Returns:
            通貨ペアごとの保有状況の辞書。
        """
        return self.holdings.copy()

    def get_total_profit_loss(self, results: list[TradeResult]) -> float:
        """総損益を計算する.

        Args:
            results: calculate() の結果。

        Returns:
            総損益（円）。
        """
        return sum(r["profit_loss"] for r in results)
