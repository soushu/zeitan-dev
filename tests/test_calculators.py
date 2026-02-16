"""税金計算エンジンのユニットテスト."""

from datetime import datetime

import pytest

from src.calculators import MovingAverageCalculator, TotalAverageCalculator
from src.parsers.base import TransactionFormat


class TestMovingAverageCalculator:
    """MovingAverageCalculator のテスト."""

    def test_simple_buy_and_sell(self) -> None:
        """単純な買い→売りで利益が出るケース."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=5000000.0,
                fee=1000.0,
            ),
            TransactionFormat(
                timestamp=datetime(2024, 1, 2, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=1.0,
                price=5500000.0,
                fee=1000.0,
            ),
        ]

        results = calculator.calculate(transactions)
        assert len(results) == 2

        # 購入時の結果
        buy_result = results[0]
        assert buy_result["type"] == "buy"
        assert buy_result["profit_loss"] == 0.0
        # 平均取得原価 = (1.0 * 5000000 + 1000) / 1.0 = 5001000
        assert buy_result["average_cost_after"] == pytest.approx(5001000.0)

        # 売却時の結果
        sell_result = results[1]
        assert sell_result["type"] == "sell"
        # 売却収入 = 1.0 * 5500000 - 1000 = 5499000
        # 取得原価 = 1.0 * 5001000 = 5001000
        # 損益 = 5499000 - 5001000 = 498000
        assert sell_result["profit_loss"] == pytest.approx(498000.0)

    def test_multiple_purchases_average_cost(self) -> None:
        """複数回購入後に売却し、平均取得原価が正しく計算されること."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            # 1回目の購入: 1 BTC @ 5,000,000円
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=5000000.0,
                fee=0.0,
            ),
            # 2回目の購入: 1 BTC @ 6,000,000円
            TransactionFormat(
                timestamp=datetime(2024, 1, 2, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=6000000.0,
                fee=0.0,
            ),
            # 売却: 2 BTC @ 7,000,000円
            TransactionFormat(
                timestamp=datetime(2024, 1, 3, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=2.0,
                price=7000000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # 平均取得原価 = (5,000,000 + 6,000,000) / 2 = 5,500,000
        buy2_result = results[1]
        assert buy2_result["average_cost_after"] == pytest.approx(5500000.0)

        # 売却損益 = (7,000,000 - 5,500,000) * 2 = 3,000,000
        sell_result = results[2]
        assert sell_result["profit_loss"] == pytest.approx(3000000.0)

    def test_sell_with_loss(self) -> None:
        """売却で損失が出るケース."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=6000000.0,
                fee=0.0,
            ),
            TransactionFormat(
                timestamp=datetime(2024, 1, 2, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=1.0,
                price=5000000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)
        sell_result = results[1]

        # 損益 = 5,000,000 - 6,000,000 = -1,000,000
        assert sell_result["profit_loss"] == pytest.approx(-1000000.0)

    def test_get_total_profit_loss(self) -> None:
        """総損益の計算が正しいこと."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=5000000.0,
                fee=0.0,
            ),
            TransactionFormat(
                timestamp=datetime(2024, 1, 2, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=1.0,
                price=5500000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)
        total_pl = calculator.get_total_profit_loss(results)

        # 総損益 = 500,000
        assert total_pl == pytest.approx(500000.0)

    def test_insufficient_balance_raises_error(self) -> None:
        """保有数量不足の場合にエラーが発生すること."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            # 購入なしで売却
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=1.0,
                price=5000000.0,
                fee=0.0,
            ),
        ]

        with pytest.raises(ValueError, match="保有数量不足"):
            calculator.calculate(transactions)

    def test_airdrop_transaction(self) -> None:
        """エアドロップ取引が正しく処理されること."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            # エアドロップで10 ETH受取（時価30万円/ETH）
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="coincheck",
                symbol="ETH/JPY",
                type="airdrop",
                amount=10.0,
                price=300000.0,  # 受取時の時価
                fee=0.0,
            ),
            # 5 ETH売却
            TransactionFormat(
                timestamp=datetime(2024, 2, 1, 10, 0, 0),
                exchange="coincheck",
                symbol="ETH/JPY",
                type="sell",
                amount=5.0,
                price=350000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # エアドロップ: 雑所得 = 10 * 300000 = 3,000,000円
        airdrop_result = results[0]
        assert airdrop_result["type"] == "airdrop"
        assert airdrop_result["profit_loss"] == pytest.approx(3000000.0)
        assert airdrop_result["average_cost_after"] == pytest.approx(300000.0)

        # 売却: 譲渡所得 = (350000 - 300000) * 5 = 250,000円
        sell_result = results[1]
        assert sell_result["profit_loss"] == pytest.approx(250000.0)

    def test_fork_transaction(self) -> None:
        """ハードフォーク取引が正しく処理されること."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            # BTCを保有していた状態で、フォークによりBCH受取
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BCH/JPY",
                type="fork",
                amount=2.0,
                price=50000.0,  # 受取時の時価
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # フォーク: 雑所得 = 2 * 50000 = 100,000円
        fork_result = results[0]
        assert fork_result["type"] == "fork"
        assert fork_result["profit_loss"] == pytest.approx(100000.0)
        assert fork_result["average_cost_after"] == pytest.approx(50000.0)

    def test_reward_transaction(self) -> None:
        """ステーキング報酬が正しく処理されること."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            # 既存のETH保有（購入）
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="coincheck",
                symbol="ETH/JPY",
                type="buy",
                amount=10.0,
                price=300000.0,
                fee=0.0,
            ),
            # ステーキング報酬: 0.5 ETH（時価32万円）
            TransactionFormat(
                timestamp=datetime(2024, 2, 1, 10, 0, 0),
                exchange="coincheck",
                symbol="ETH/JPY",
                type="reward",
                amount=0.5,
                price=320000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # 購入
        buy_result = results[0]
        assert buy_result["average_cost_after"] == pytest.approx(300000.0)

        # 報酬: 雑所得 = 0.5 * 320000 = 160,000円
        reward_result = results[1]
        assert reward_result["type"] == "reward"
        assert reward_result["profit_loss"] == pytest.approx(160000.0)
        # 平均取得原価 = (10 * 300000 + 0.5 * 320000) / 10.5 ≈ 301,904円
        assert reward_result["average_cost_after"] == pytest.approx(301904.76, rel=1e-2)

    def test_transfer_in_and_out(self) -> None:
        """送金（転入・転出）が正しく処理されること."""
        calculator = MovingAverageCalculator()
        transactions: list[TransactionFormat] = [
            # 取引所Aで購入
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=5000000.0,
                fee=0.0,
            ),
            # 取引所Aから送金（転出）
            TransactionFormat(
                timestamp=datetime(2024, 1, 2, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="transfer_out",
                amount=0.5,
                price=0.0,
                fee=0.0,
            ),
            # 取引所Bで受取（転入）- 元の取得原価を引き継ぐ
            TransactionFormat(
                timestamp=datetime(2024, 1, 3, 10, 0, 0),
                exchange="coincheck",
                symbol="BTC/JPY",
                type="transfer_in",
                amount=0.5,
                price=5000000.0,  # 元の取得原価
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # 転出: 課税なし
        transfer_out_result = results[1]
        assert transfer_out_result["type"] == "transfer_out"
        assert transfer_out_result["profit_loss"] == 0.0

        # 転入: 課税なし
        transfer_in_result = results[2]
        assert transfer_in_result["type"] == "transfer_in"
        assert transfer_in_result["profit_loss"] == 0.0


class TestTotalAverageCalculator:
    """TotalAverageCalculator のテスト."""

    def test_simple_buy_and_sell_same_year(self) -> None:
        """同じ年内での買い→売りで利益が出るケース."""
        calculator = TotalAverageCalculator()
        transactions: list[TransactionFormat] = [
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=5000000.0,
                fee=1000.0,
            ),
            TransactionFormat(
                timestamp=datetime(2024, 6, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=1.0,
                price=5500000.0,
                fee=1000.0,
            ),
        ]

        results = calculator.calculate(transactions)
        assert len(results) == 2

        # 年間平均取得原価 = (1.0 * 5000000 + 1000) / 1.0 = 5001000
        sell_result = results[1]
        assert sell_result["average_cost_used"] == pytest.approx(5001000.0)

        # 売却収入 = 1.0 * 5500000 - 1000 = 5499000
        # 取得原価 = 1.0 * 5001000 = 5001000
        # 損益 = 5499000 - 5001000 = 498000
        assert sell_result["profit_loss"] == pytest.approx(498000.0)

    def test_multiple_purchases_same_year(self) -> None:
        """同じ年に複数回購入し、年間平均取得原価が正しく計算されること."""
        calculator = TotalAverageCalculator()
        transactions: list[TransactionFormat] = [
            # 1回目の購入: 1 BTC @ 5,000,000円
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=5000000.0,
                fee=0.0,
            ),
            # 2回目の購入: 1 BTC @ 6,000,000円
            TransactionFormat(
                timestamp=datetime(2024, 3, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=6000000.0,
                fee=0.0,
            ),
            # 売却: 2 BTC @ 7,000,000円
            TransactionFormat(
                timestamp=datetime(2024, 6, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=2.0,
                price=7000000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # 年間平均取得原価 = (5,000,000 + 6,000,000) / 2 = 5,500,000
        sell_result = results[2]
        assert sell_result["average_cost_used"] == pytest.approx(5500000.0)

        # 売却損益 = (7,000,000 - 5,500,000) * 2 = 3,000,000
        assert sell_result["profit_loss"] == pytest.approx(3000000.0)

    def test_multiple_years(self) -> None:
        """複数年にまたがる取引で、年ごとに平均取得原価が計算されること."""
        calculator = TotalAverageCalculator()
        transactions: list[TransactionFormat] = [
            # 2024年の購入: 1 BTC @ 5,000,000円
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=5000000.0,
                fee=0.0,
            ),
            # 2024年の売却: 1 BTC @ 5,500,000円
            TransactionFormat(
                timestamp=datetime(2024, 6, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=1.0,
                price=5500000.0,
                fee=0.0,
            ),
            # 2025年の購入: 1 BTC @ 6,000,000円
            TransactionFormat(
                timestamp=datetime(2025, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=6000000.0,
                fee=0.0,
            ),
            # 2025年の売却: 1 BTC @ 6,500,000円
            TransactionFormat(
                timestamp=datetime(2025, 6, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=1.0,
                price=6500000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # 2024年の売却
        sell_2024 = results[1]
        assert sell_2024["average_cost_used"] == pytest.approx(5000000.0)
        assert sell_2024["profit_loss"] == pytest.approx(500000.0)

        # 2025年の売却
        sell_2025 = results[3]
        assert sell_2025["average_cost_used"] == pytest.approx(6000000.0)
        assert sell_2025["profit_loss"] == pytest.approx(500000.0)

    def test_get_total_profit_loss(self) -> None:
        """総損益の計算が正しいこと."""
        calculator = TotalAverageCalculator()
        transactions: list[TransactionFormat] = [
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=1.0,
                price=5000000.0,
                fee=0.0,
            ),
            TransactionFormat(
                timestamp=datetime(2024, 6, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="sell",
                amount=1.0,
                price=5500000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)
        total_pl = calculator.get_total_profit_loss(results)

        # 総損益 = 500,000
        assert total_pl == pytest.approx(500000.0)

    def test_get_yearly_average_costs(self) -> None:
        """年間平均取得原価の取得が正しいこと."""
        calculator = TotalAverageCalculator()
        transactions: list[TransactionFormat] = [
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BTC/JPY",
                type="buy",
                amount=2.0,
                price=5000000.0,
                fee=0.0,
            ),
        ]

        calculator.calculate(transactions)
        yearly_costs = calculator.get_yearly_average_costs()

        assert (2024, "BTC/JPY") in yearly_costs
        cost_data = yearly_costs[(2024, "BTC/JPY")]
        assert cost_data["year"] == 2024
        assert cost_data["symbol"] == "BTC/JPY"
        assert cost_data["total_purchase_amount"] == pytest.approx(2.0)
        assert cost_data["total_purchase_cost"] == pytest.approx(10000000.0)
        assert cost_data["average_cost"] == pytest.approx(5000000.0)

    def test_airdrop_included_in_average_cost(self) -> None:
        """エアドロップが年間平均取得原価に含まれること."""
        calculator = TotalAverageCalculator()
        transactions: list[TransactionFormat] = [
            # 通常購入: 1 ETH @ 300,000円
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="coincheck",
                symbol="ETH/JPY",
                type="buy",
                amount=1.0,
                price=300000.0,
                fee=0.0,
            ),
            # エアドロップ: 1 ETH @ 時価320,000円
            TransactionFormat(
                timestamp=datetime(2024, 2, 1, 10, 0, 0),
                exchange="coincheck",
                symbol="ETH/JPY",
                type="airdrop",
                amount=1.0,
                price=320000.0,
                fee=0.0,
            ),
            # 売却: 2 ETH @ 350,000円
            TransactionFormat(
                timestamp=datetime(2024, 3, 1, 10, 0, 0),
                exchange="coincheck",
                symbol="ETH/JPY",
                type="sell",
                amount=2.0,
                price=350000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # エアドロップ: 雑所得 = 1 * 320000 = 320,000円
        airdrop_result = results[1]
        assert airdrop_result["type"] == "airdrop"
        assert airdrop_result["profit_loss"] == pytest.approx(320000.0)

        # 年間平均取得原価 = (300000 + 320000) / 2 = 310,000円
        sell_result = results[2]
        assert sell_result["average_cost_used"] == pytest.approx(310000.0)
        # 売却損益 = (350000 - 310000) * 2 = 80,000円
        assert sell_result["profit_loss"] == pytest.approx(80000.0)

    def test_reward_and_fork_transactions(self) -> None:
        """報酬とフォークが正しく処理されること."""
        calculator = TotalAverageCalculator()
        transactions: list[TransactionFormat] = [
            # ステーキング報酬
            TransactionFormat(
                timestamp=datetime(2024, 1, 1, 10, 0, 0),
                exchange="coincheck",
                symbol="ETH/JPY",
                type="reward",
                amount=0.5,
                price=300000.0,
                fee=0.0,
            ),
            # ハードフォーク
            TransactionFormat(
                timestamp=datetime(2024, 2, 1, 10, 0, 0),
                exchange="bitflyer",
                symbol="BCH/JPY",
                type="fork",
                amount=2.0,
                price=50000.0,
                fee=0.0,
            ),
        ]

        results = calculator.calculate(transactions)

        # 報酬: 雑所得 = 0.5 * 300000 = 150,000円
        reward_result = results[0]
        assert reward_result["profit_loss"] == pytest.approx(150000.0)

        # フォーク: 雑所得 = 2 * 50000 = 100,000円
        fork_result = results[1]
        assert fork_result["profit_loss"] == pytest.approx(100000.0)
