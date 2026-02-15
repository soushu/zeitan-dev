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
