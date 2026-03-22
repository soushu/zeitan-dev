"""問題取引の自動検出ユーティリティ."""

from collections import defaultdict
from src.parsers.base import TransactionFormat


def detect_alerts(transactions: list[TransactionFormat]) -> list[dict]:
    """取引データから問題のある取引を検出する.

    検出する問題:
    1. 売却数量 > 保有数量（oversell）
    2. 購入履歴なしに売却（no_buy_before_sell）
    3. 同一タイムスタンプ・通貨・数量の重複取引（duplicate）

    Args:
        transactions: 時系列順の取引データ。

    Returns:
        アラートのリスト。
    """
    sorted_txs = sorted(transactions, key=lambda x: x["timestamp"])
    alerts: list[dict] = []
    holdings: dict[str, float] = defaultdict(float)
    has_bought: set[str] = set()

    # 重複検出用
    seen: dict[tuple, int] = {}

    for i, tx in enumerate(sorted_txs):
        symbol = tx["symbol"]
        amount = tx["amount"]
        tx_type = tx["type"]
        key = (str(tx["timestamp"]), symbol, tx_type, amount)

        # 重複検出
        if key in seen:
            alerts.append({
                "type": "duplicate",
                "severity": "warning",
                "symbol": symbol,
                "message": f"{symbol} に重複の可能性がある取引があります（{tx['timestamp']}）",
                "transaction_index": i,
            })
        seen[key] = i

        if tx_type == "buy":
            holdings[symbol] += amount
            has_bought.add(symbol)
        elif tx_type in ("sell", "swap", "nft_sell"):
            # 購入履歴なしに売却
            if symbol not in has_bought and holdings[symbol] <= 0:
                alerts.append({
                    "type": "no_buy_before_sell",
                    "severity": "error",
                    "symbol": symbol,
                    "message": f"{symbol} の購入履歴がないまま売却されています",
                    "transaction_index": i,
                })
            # 売却数量 > 保有数量
            elif amount > holdings[symbol] + 1e-8:
                alerts.append({
                    "type": "oversell",
                    "severity": "error",
                    "symbol": symbol,
                    "message": (
                        f"{symbol} の売却数量（{amount}）が保有数量（{holdings[symbol]:.8f}）を超えています"
                    ),
                    "transaction_index": i,
                })
            holdings[symbol] -= amount
        elif tx_type in ("airdrop", "fork", "reward", "transfer_in", "liquidity_remove", "nft_buy"):
            holdings[symbol] += amount
            if tx_type not in ("airdrop", "fork", "reward"):
                has_bought.add(symbol)
        elif tx_type in ("transfer_out", "liquidity_add", "lending"):
            holdings[symbol] -= amount

    return alerts
