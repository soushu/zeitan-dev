"""総平均法による暗号資産税金計算エンジン.

総平均法:
- 年間平均取得原価 = 年間総購入額 / 年間総購入数量
- 年間売却損益 = Σ[(売却価格 - 年間平均取得原価) × 売却数量]
- エアドロップ・報酬: 受取時の時価で取得、雑所得として計上
- ハードフォーク: 受取時の時価で取得、雑所得として計上
- 送金: 課税なし
"""

from datetime import datetime
from typing import TypedDict

from ..parsers.base import TransactionFormat


class YearlyAverageCost(TypedDict):
    """年間平均取得原価."""

    year: int  # 年
    symbol: str  # 通貨ペア
    total_purchase_amount: float  # 年間総購入数量
    total_purchase_cost: float  # 年間総購入額（円、手数料込み）
    average_cost: float  # 年間平均取得原価（円/単位）


class TradeResult(TypedDict):
    """取引結果."""

    timestamp: datetime  # 取引日時
    exchange: str  # 取引所
    symbol: str  # 通貨ペア
    type: str  # 'buy', 'sell', 'airdrop', 'fork', 'reward', 'transfer_in', 'transfer_out'
    amount: float  # 取引数量
    price: float  # 取引価格（円/単位）
    fee: float  # 手数料（円）
    profit_loss: float  # 損益（円）売却時=譲渡所得、報酬等=雑所得、購入・送金=0
    average_cost_used: float  # 使用した平均取得原価


class TotalAverageCalculator:
    """総平均法による税金計算エンジン.

    年間の全購入取引から平均取得原価を計算し、
    各売却取引での損益を計算します。
    """

    def __init__(self) -> None:
        """計算エンジンを初期化."""
        # (年, 通貨ペア) ごとの平均取得原価
        self.yearly_avg_costs: dict[tuple[int, str], YearlyAverageCost] = {}

    def calculate(self, transactions: list[TransactionFormat]) -> list[TradeResult]:
        """取引リストから損益を計算する.

        Args:
            transactions: TransactionFormatのリスト。

        Returns:
            TradeResultのリスト。各取引の損益情報を含む。
        """
        # 取引を時系列順にソート
        sorted_txs = sorted(transactions, key=lambda x: x["timestamp"])

        # Step 1: 年間平均取得原価を計算
        self._calculate_yearly_average_costs(sorted_txs)

        # Step 2: 各取引の損益を計算
        results: list[TradeResult] = []

        for tx in sorted_txs:
            symbol = tx["symbol"]
            amount = tx["amount"]
            price = tx["price"]
            fee = tx["fee"]
            tx_type = tx["type"]
            year = tx["timestamp"].year

            # その年の平均取得原価を取得
            key = (year, symbol)
            avg_cost_data = self.yearly_avg_costs.get(key)
            average_cost = avg_cost_data["average_cost"] if avg_cost_data else 0.0

            profit_loss = 0.0

            if tx_type == "sell":
                # 売却時: 損益を計算
                sale_revenue = amount * price - fee  # 売却収入から手数料を差し引く
                cost_basis = amount * average_cost  # 取得原価
                profit_loss = sale_revenue - cost_basis

            elif tx_type in ("airdrop", "fork", "reward"):
                # エアドロップ・フォーク・報酬: 受取時の時価を雑所得として計上
                income_value = amount * price
                profit_loss = income_value

            elif tx_type in ("buy", "transfer_in", "transfer_out"):
                # 購入・送金: 損益なし
                profit_loss = 0.0

            else:
                raise ValueError(f"不明な取引タイプ: {tx_type}")

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
                    average_cost_used=average_cost,
                )
            )

        return results

    def _calculate_yearly_average_costs(
        self, transactions: list[TransactionFormat]
    ) -> None:
        """年間平均取得原価を計算する.

        Args:
            transactions: TransactionFormatのリスト（時系列順ソート済み）。
        """
        # (年, 通貨ペア) ごとの購入集計
        yearly_purchases: dict[tuple[int, str], dict] = {}

        for tx in transactions:
            # 購入・エアドロップ・フォーク・報酬・転入を取得コストに含める
            if tx["type"] not in ("buy", "airdrop", "fork", "reward", "transfer_in"):
                continue

            year = tx["timestamp"].year
            symbol = tx["symbol"]
            amount = tx["amount"]
            price = tx["price"]
            fee = tx["fee"]
            tx_type = tx["type"]

            key = (year, symbol)

            if key not in yearly_purchases:
                yearly_purchases[key] = {
                    "total_amount": 0.0,
                    "total_cost": 0.0,
                }

            # 取得原価の計算
            if tx_type == "buy":
                purchase_cost = amount * price + fee  # 手数料は取得原価に含める
            elif tx_type in ("airdrop", "fork", "reward"):
                purchase_cost = amount * price  # 受取時の時価が取得原価
            elif tx_type == "transfer_in":
                purchase_cost = amount * price if price > 0 else 0  # 指定された原価または0
            else:
                purchase_cost = 0.0

            yearly_purchases[key]["total_amount"] += amount
            yearly_purchases[key]["total_cost"] += purchase_cost

        # 平均取得原価を計算
        for (year, symbol), data in yearly_purchases.items():
            total_amount = data["total_amount"]
            total_cost = data["total_cost"]

            if total_amount > 0:
                average_cost = total_cost / total_amount
            else:
                average_cost = 0.0

            self.yearly_avg_costs[(year, symbol)] = YearlyAverageCost(
                year=year,
                symbol=symbol,
                total_purchase_amount=total_amount,
                total_purchase_cost=total_cost,
                average_cost=average_cost,
            )

    def get_yearly_average_costs(self) -> dict[tuple[int, str], YearlyAverageCost]:
        """年間平均取得原価を取得する.

        Returns:
            (年, 通貨ペア) ごとの年間平均取得原価の辞書。
        """
        return self.yearly_avg_costs.copy()

    def get_total_profit_loss(self, results: list[TradeResult]) -> float:
        """総損益を計算する.

        Args:
            results: calculate() の結果。

        Returns:
            総損益（円）。
        """
        return sum(r["profit_loss"] for r in results)
