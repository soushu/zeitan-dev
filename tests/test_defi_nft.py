"""DeFi/NFT パーサーと計算のテスト."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.calculators import MovingAverageCalculator, TotalAverageCalculator
from src.parsers.base import TransactionFormat
from src.parsers.defi import AaveParser, LiquidityPoolParser, UniswapParser
from src.parsers.nft import BlurParser, OpenSeaParser


class TestUniswapParser:
    """Uniswapパーサーのテスト."""

    @pytest.fixture
    def sample_csv(self) -> Path:
        """テスト用CSVを作成."""
        csv_content = """Timestamp,Token In,Amount In,Token Out,Amount Out,Price USD,Fee
2024-01-15T10:00:00Z,ETH,1.0,USDC,3000.0,3000.0,5.0
2024-01-16T11:00:00Z,USDC,2000.0,DAI,2000.0,1.0,3.0"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            f.write(csv_content)
            return Path(f.name)

    def test_exchange_name(self) -> None:
        """取引所名が正しいこと."""
        parser = UniswapParser()
        assert parser.exchange_name == "uniswap"

    def test_validate(self, sample_csv: Path) -> None:
        """バリデーションが正しく動作すること."""
        parser = UniswapParser()
        assert parser.validate(sample_csv) is True

    def test_parse(self, sample_csv: Path) -> None:
        """パースが正しく動作すること."""
        parser = UniswapParser()
        transactions = parser.parse(sample_csv)

        # 2つのswap取引 × 2トランザクション（swap + buy）= 4トランザクション
        assert len(transactions) == 4

        # 最初のswap取引
        assert transactions[0]["exchange"] == "uniswap"
        assert transactions[0]["symbol"] == "ETH/USDC"
        assert transactions[0]["type"] == "swap"
        assert transactions[0]["amount"] == 1.0
        assert transactions[0]["fee"] == 5.0

        # 最初のbuy取引
        assert transactions[1]["type"] == "buy"
        assert transactions[1]["amount"] == 3000.0


class TestAaveParser:
    """Aaveパーサーのテスト."""

    @pytest.fixture
    def sample_csv(self) -> Path:
        """テスト用CSVを作成."""
        csv_content = """Timestamp,Action,Asset,Amount,Price USD,Fee
2024-01-15T10:00:00Z,Deposit,ETH,2.0,3000.0,0.5
2024-01-16T11:00:00Z,Withdraw,ETH,1.0,3100.0,0.3
2024-01-17T12:00:00Z,Borrow,USDC,5000.0,1.0,1.0
2024-01-18T13:00:00Z,Repay,USDC,2500.0,1.0,0.5"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            f.write(csv_content)
            return Path(f.name)

    def test_exchange_name(self) -> None:
        """取引所名が正しいこと."""
        parser = AaveParser()
        assert parser.exchange_name == "aave"

    def test_validate(self, sample_csv: Path) -> None:
        """バリデーションが正しく動作すること."""
        parser = AaveParser()
        assert parser.validate(sample_csv) is True

    def test_parse(self, sample_csv: Path) -> None:
        """パースが正しく動作すること."""
        parser = AaveParser()
        transactions = parser.parse(sample_csv)

        assert len(transactions) == 4

        # Deposit -> lending
        assert transactions[0]["type"] == "lending"
        assert transactions[0]["symbol"] == "ETH/JPY"

        # Withdraw -> transfer_in
        assert transactions[1]["type"] == "transfer_in"

        # Borrow -> transfer_in
        assert transactions[2]["type"] == "transfer_in"

        # Repay -> transfer_out
        assert transactions[3]["type"] == "transfer_out"


class TestLiquidityPoolParser:
    """流動性プールパーサーのテスト."""

    @pytest.fixture
    def sample_csv(self) -> Path:
        """テスト用CSVを作成."""
        csv_content = """Timestamp,Action,Token A,Amount A,Token B,Amount B,LP Token,Price USD,Fee
2024-01-15T10:00:00Z,Add Liquidity,ETH,1.0,USDC,3000.0,100.0,3000.0,10.0
2024-01-20T15:00:00Z,Remove Liquidity,ETH,0.5,USDC,1600.0,50.0,3200.0,5.0"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            f.write(csv_content)
            return Path(f.name)

    def test_exchange_name(self) -> None:
        """取引所名が正しいこと."""
        parser = LiquidityPoolParser()
        assert parser.exchange_name == "liquidity_pool"

    def test_validate(self, sample_csv: Path) -> None:
        """バリデーションが正しく動作すること."""
        parser = LiquidityPoolParser()
        assert parser.validate(sample_csv) is True

    def test_parse(self, sample_csv: Path) -> None:
        """パースが正しく動作すること."""
        parser = LiquidityPoolParser()
        transactions = parser.parse(sample_csv)

        # 2つのアクション × 2トークン = 4トランザクション
        assert len(transactions) == 4

        # Add Liquidity
        assert transactions[0]["type"] == "liquidity_add"
        assert transactions[0]["symbol"] == "ETH/JPY"
        assert transactions[0]["amount"] == 1.0

        assert transactions[1]["type"] == "liquidity_add"
        assert transactions[1]["symbol"] == "USDC/JPY"
        assert transactions[1]["amount"] == 3000.0

        # Remove Liquidity
        assert transactions[2]["type"] == "liquidity_remove"
        assert transactions[3]["type"] == "liquidity_remove"


class TestOpenSeaParser:
    """OpenSeaパーサーのテスト."""

    @pytest.fixture
    def sample_csv(self) -> Path:
        """テスト用CSVを作成."""
        csv_content = """Timestamp,Event Type,NFT Collection,NFT Name,Token ID,Quantity,Price,Price USD,Gas Fee
2024-01-15T10:00:00Z,Purchase,CryptoPunks,Punk #1234,1234,1,50.0,150000.0,0.01
2024-02-01T14:00:00Z,Sale,CryptoPunks,Punk #1234,1234,1,55.0,175000.0,0.015
2024-02-05T16:00:00Z,Mint,Azuki,Azuki #5678,5678,1,1.0,3000.0,0.005"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            f.write(csv_content)
            return Path(f.name)

    def test_exchange_name(self) -> None:
        """取引所名が正しいこと."""
        parser = OpenSeaParser()
        assert parser.exchange_name == "opensea"

    def test_validate(self, sample_csv: Path) -> None:
        """バリデーションが正しく動作すること."""
        parser = OpenSeaParser()
        assert parser.validate(sample_csv) is True

    def test_parse(self, sample_csv: Path) -> None:
        """パースが正しく動作すること."""
        parser = OpenSeaParser()
        transactions = parser.parse(sample_csv)

        assert len(transactions) == 3

        # Purchase -> nft_buy
        assert transactions[0]["type"] == "nft_buy"
        assert transactions[0]["symbol"] == "CryptoPunks/Punk #1234"
        assert transactions[0]["price"] == 150000.0
        assert transactions[0]["amount"] == 1

        # Sale -> nft_sell
        assert transactions[1]["type"] == "nft_sell"
        assert transactions[1]["price"] == 175000.0

        # Mint -> nft_buy
        assert transactions[2]["type"] == "nft_buy"


class TestBlurParser:
    """Blurパーサーのテスト."""

    @pytest.fixture
    def sample_csv(self) -> Path:
        """テスト用CSVを作成."""
        csv_content = """Date,Type,Collection,Item,Price ETH,Price USD,Quantity,Gas
2024-01-15T10:00:00Z,Buy,Azuki,Azuki #100,10.0,30000.0,1,0.008
2024-02-01T14:00:00Z,Sell,Azuki,Azuki #100,12.0,38000.0,1,0.01"""

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as f:
            f.write(csv_content)
            return Path(f.name)

    def test_exchange_name(self) -> None:
        """取引所名が正しいこと."""
        parser = BlurParser()
        assert parser.exchange_name == "blur"

    def test_validate(self, sample_csv: Path) -> None:
        """バリデーションが正しく動作すること."""
        parser = BlurParser()
        assert parser.validate(sample_csv) is True

    def test_parse(self, sample_csv: Path) -> None:
        """パースが正しく動作すること."""
        parser = BlurParser()
        transactions = parser.parse(sample_csv)

        assert len(transactions) == 2

        # Buy
        assert transactions[0]["type"] == "nft_buy"
        assert transactions[0]["symbol"] == "Azuki/Azuki #100"
        assert transactions[0]["price"] == 30000.0

        # Sell
        assert transactions[1]["type"] == "nft_sell"
        assert transactions[1]["price"] == 38000.0


class TestDeFiCalculations:
    """DeFi取引の計算テスト."""

    def test_swap_transaction_moving_average(self) -> None:
        """Swap取引が正しく計算されること（移動平均法）."""
        calculator = MovingAverageCalculator()

        transactions: list[TransactionFormat] = [
            {
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "exchange": "uniswap",
                "symbol": "ETH/JPY",
                "type": "buy",
                "amount": 2.0,
                "price": 300000.0,
                "fee": 1000.0,
            },
            {
                "timestamp": datetime(2024, 1, 5, 10, 0, 0),
                "exchange": "uniswap",
                "symbol": "ETH/JPY",
                "type": "swap",
                "amount": 1.0,
                "price": 350000.0,
                "fee": 500.0,
            },
        ]

        results = calculator.calculate(transactions)

        # Buy取引
        assert results[0]["profit_loss"] == 0.0

        # Swap取引: (350000 - 500) - 300500 = 49000
        # 平均取得原価 = (300000*2 + 1000) / 2 = 300500
        assert results[1]["profit_loss"] == pytest.approx(49000.0, rel=1e-2)

    def test_liquidity_transactions_moving_average(self) -> None:
        """流動性取引が正しく計算されること（移動平均法）."""
        calculator = MovingAverageCalculator()

        transactions: list[TransactionFormat] = [
            {
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "exchange": "liquidity_pool",
                "symbol": "ETH/JPY",
                "type": "buy",
                "amount": 10.0,
                "price": 300000.0,
                "fee": 0,
            },
            {
                "timestamp": datetime(2024, 1, 5, 10, 0, 0),
                "exchange": "liquidity_pool",
                "symbol": "ETH/JPY",
                "type": "liquidity_add",
                "amount": 5.0,
                "price": 0,
                "fee": 0,
            },
            {
                "timestamp": datetime(2024, 1, 10, 10, 0, 0),
                "exchange": "liquidity_pool",
                "symbol": "ETH/JPY",
                "type": "liquidity_remove",
                "amount": 6.0,
                "price": 320000.0,
                "fee": 0,
            },
        ]

        results = calculator.calculate(transactions)

        # Buy: 損益なし
        assert results[0]["profit_loss"] == 0.0
        assert results[0]["average_cost_after"] == 300000.0

        # Liquidity Add: 損益なし、保有減少
        assert results[1]["profit_loss"] == 0.0

        # Liquidity Remove: 損益なし、保有増加
        assert results[2]["profit_loss"] == 0.0


class TestNFTCalculations:
    """NFT取引の計算テスト."""

    def test_nft_buy_sell_moving_average(self) -> None:
        """NFT売買が正しく計算されること（移動平均法）."""
        calculator = MovingAverageCalculator()

        transactions: list[TransactionFormat] = [
            {
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "exchange": "opensea",
                "symbol": "CryptoPunks/Punk #1234",
                "type": "nft_buy",
                "amount": 1.0,
                "price": 150000.0,
                "fee": 1000.0,
            },
            {
                "timestamp": datetime(2024, 2, 1, 10, 0, 0),
                "exchange": "opensea",
                "symbol": "CryptoPunks/Punk #1234",
                "type": "nft_sell",
                "amount": 1.0,
                "price": 175000.0,
                "fee": 1500.0,
            },
        ]

        results = calculator.calculate(transactions)

        # NFT Buy: 損益なし
        assert results[0]["profit_loss"] == 0.0
        assert results[0]["average_cost_after"] == 151000.0  # (150000 + 1000) / 1

        # NFT Sell: (175000 - 1500) - 151000 = 22500
        assert results[1]["profit_loss"] == pytest.approx(22500.0, rel=1e-2)

    def test_nft_transactions_total_average(self) -> None:
        """NFT取引が正しく計算されること（総平均法）."""
        calculator = TotalAverageCalculator()

        transactions: list[TransactionFormat] = [
            {
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "exchange": "opensea",
                "symbol": "Azuki/Azuki #100",
                "type": "nft_buy",
                "amount": 1.0,
                "price": 30000.0,
                "fee": 500.0,
            },
            {
                "timestamp": datetime(2024, 1, 15, 10, 0, 0),
                "exchange": "opensea",
                "symbol": "Azuki/Azuki #100",
                "type": "nft_buy",
                "amount": 1.0,
                "price": 35000.0,
                "fee": 500.0,
            },
            {
                "timestamp": datetime(2024, 2, 1, 10, 0, 0),
                "exchange": "opensea",
                "symbol": "Azuki/Azuki #100",
                "type": "nft_sell",
                "amount": 1.0,
                "price": 40000.0,
                "fee": 800.0,
            },
        ]

        results = calculator.calculate(transactions)

        # 年間平均取得原価 = (30000 + 500 + 35000 + 500) / 2 = 33000
        # NFT Sell: (40000 - 800) - 33000 = 6200
        assert results[2]["profit_loss"] == pytest.approx(6200.0, rel=1e-2)
        assert results[2]["average_cost_used"] == pytest.approx(33000.0, rel=1e-2)
