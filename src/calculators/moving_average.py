"""移動平均法による暗号資産税金計算エンジン.

移動平均法:
- 購入時: 新しい平均取得原価 = (既存保有額 + 購入額) / (既存数量 + 購入数量)
- 売却時: 売却損益 = (売却価格 - 平均取得原価) × 売却数量
- エアドロップ・報酬: 受取時の時価で取得、雑所得として計上
- ハードフォーク: 受取時の時価で取得、雑所得として計上
- 送金: 保有数量の増減のみ（課税なし）
- DeFi Swap: トークン交換、売却として扱い損益計算
- 流動性追加: 保有数量減少、課税なし
- 流動性削除: 保有数量増加、受取時の時価で取得
- NFT売買: 通常の売買と同様に損益計算
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
    type: str  # 'buy', 'sell', 'airdrop', 'fork', 'reward', 'transfer_in', 'transfer_out', 'swap', 'liquidity_add', 'liquidity_remove', 'lending', 'nft_buy', 'nft_sell'
    amount: float  # 取引数量
    price: float  # 取引価格（円/単位）
    fee: float  # 手数料（円）
    profit_loss: float  # 損益（円）売却時=譲渡所得、報酬等=雑所得、購入・送金=0
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

            elif tx_type in ("airdrop", "fork", "reward"):
                # エアドロップ・フォーク・報酬: 受取時の時価で取得、雑所得として計上
                # 受取時の時価 = price（取引時の市場価格）
                income_value = amount * price  # 雑所得額
                profit_loss = income_value  # 雑所得として記録

                # 保有に追加（取得原価 = 受取時の時価）
                total_cost_before = holding["amount"] * holding["average_cost"]
                acquisition_cost = income_value  # 受取時の時価が取得原価
                new_amount = holding["amount"] + amount

                if new_amount > 0:
                    new_average_cost = (total_cost_before + acquisition_cost) / new_amount
                else:
                    new_average_cost = 0.0

                holding["amount"] = new_amount
                holding["average_cost"] = new_average_cost

            elif tx_type == "transfer_in":
                # 他の取引所・ウォレットからの受取
                # 課税なし、保有数量を増やす（平均取得原価は元のまま維持）
                # price=0の場合は平均取得原価を維持、price>0の場合は指定された原価で取得
                total_cost_before = holding["amount"] * holding["average_cost"]
                acquisition_cost = amount * price if price > 0 else 0
                new_amount = holding["amount"] + amount

                if new_amount > 0:
                    new_average_cost = (total_cost_before + acquisition_cost) / new_amount
                else:
                    new_average_cost = 0.0

                holding["amount"] = new_amount
                holding["average_cost"] = new_average_cost
                profit_loss = 0.0  # 課税なし

            elif tx_type == "transfer_out":
                # 他の取引所・ウォレットへの送金
                # 課税なし、保有数量を減らす、手数料を考慮
                if holding["amount"] < amount:
                    raise ValueError(
                        f"保有数量不足: {symbol} を送金しようとしましたが、保有数量が不足しています。"
                    )

                holding["amount"] -= amount
                profit_loss = 0.0  # 課税なし

            elif tx_type == "swap":
                # DeFiプロトコルでのトークン交換（例: ETH → USDC）
                # 売却として扱い、損益を計算
                if holding["amount"] <= 0:
                    raise ValueError(
                        f"保有数量不足: {symbol} をswapしようとしましたが、保有数量が 0 です。"
                    )

                swap_revenue = amount * price - fee  # swap収入から手数料を差し引く
                cost_basis = amount * holding["average_cost"]  # 取得原価
                profit_loss = swap_revenue - cost_basis

                # 保有数量を減らす
                holding["amount"] -= amount

                if holding["amount"] < 0:
                    raise ValueError(
                        f"保有数量不足: {symbol} の保有数量が負になりました。"
                    )

            elif tx_type == "liquidity_add":
                # 流動性プールへの資産預入
                # 課税なし、保有数量を減らす
                if holding["amount"] < amount:
                    raise ValueError(
                        f"保有数量不足: {symbol} を流動性追加しようとしましたが、保有数量が不足しています。"
                    )

                holding["amount"] -= amount
                profit_loss = 0.0  # 課税なし

            elif tx_type == "liquidity_remove":
                # 流動性プールからの資産引出
                # 受取時の時価で取得、保有数量を増やす
                total_cost_before = holding["amount"] * holding["average_cost"]
                acquisition_cost = amount * price  # 受取時の時価
                new_amount = holding["amount"] + amount

                if new_amount > 0:
                    new_average_cost = (total_cost_before + acquisition_cost) / new_amount
                else:
                    new_average_cost = 0.0

                holding["amount"] = new_amount
                holding["average_cost"] = new_average_cost
                profit_loss = 0.0  # 引出時点では課税なし（後の売却時に損益発生）

            elif tx_type == "lending":
                # レンディングプロトコルでの貸出
                # 課税なし、保有数量を減らす（実際は貸し出し中だが簡易的に減算）
                if holding["amount"] < amount:
                    raise ValueError(
                        f"保有数量不足: {symbol} を貸し出そうとしましたが、保有数量が不足しています。"
                    )

                holding["amount"] -= amount
                profit_loss = 0.0  # 課税なし

            elif tx_type == "nft_buy":
                # NFTの購入
                # 通常の購入と同様に処理
                total_cost_before = holding["amount"] * holding["average_cost"]
                purchase_cost = amount * price + fee  # 手数料は取得原価に含める
                new_amount = holding["amount"] + amount

                if new_amount > 0:
                    new_average_cost = (total_cost_before + purchase_cost) / new_amount
                else:
                    new_average_cost = 0.0

                holding["amount"] = new_amount
                holding["average_cost"] = new_average_cost
                profit_loss = 0.0  # 購入時は損益なし

            elif tx_type == "nft_sell":
                # NFTの売却
                # 通常の売却と同様に損益を計算
                if holding["amount"] <= 0:
                    raise ValueError(
                        f"保有数量不足: {symbol} (NFT) を売却しようとしましたが、保有数量が 0 です。"
                    )

                sale_revenue = amount * price - fee  # 売却収入から手数料を差し引く
                cost_basis = amount * holding["average_cost"]  # 取得原価
                profit_loss = sale_revenue - cost_basis

                # 保有数量を減らす
                holding["amount"] -= amount

                if holding["amount"] < 0:
                    raise ValueError(
                        f"保有数量不足: {symbol} (NFT) の保有数量が負になりました。"
                    )

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
