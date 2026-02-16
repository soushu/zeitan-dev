"""PDFレポーター のユニットテスト."""

from datetime import datetime

import pytest

from src.reporters import PDFReporter


class TestPDFReporter:
    """PDFReporter のテスト."""

    def test_generate_pdf_simple(self) -> None:
        """シンプルなPDFレポートが生成できること."""
        reporter = PDFReporter()

        results = [
            {
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "exchange": "bitflyer",
                "symbol": "BTC/JPY",
                "type": "buy",
                "amount": 1.0,
                "price": 5000000.0,
                "fee": 1000.0,
                "profit_loss": 0.0,
            },
            {
                "timestamp": datetime(2024, 1, 2, 10, 0, 0),
                "exchange": "bitflyer",
                "symbol": "BTC/JPY",
                "type": "sell",
                "amount": 1.0,
                "price": 5500000.0,
                "fee": 1000.0,
                "profit_loss": 498000.0,
            },
        ]

        pdf_bytes = reporter.generate(
            results=results,
            total_profit_loss=498000.0,
            calc_method="移動平均法",
        )

        # PDFが生成されたことを確認
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        # PDFヘッダーを確認
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_with_edge_cases(self) -> None:
        """エッジケースを含むPDFレポートが生成できること."""
        reporter = PDFReporter()

        results = [
            {
                "timestamp": datetime(2024, 1, 1, 10, 0, 0),
                "exchange": "coincheck",
                "symbol": "ETH/JPY",
                "type": "airdrop",
                "amount": 10.0,
                "price": 300000.0,
                "fee": 0.0,
                "profit_loss": 3000000.0,
            },
            {
                "timestamp": datetime(2024, 1, 2, 10, 0, 0),
                "exchange": "bitflyer",
                "symbol": "BCH/JPY",
                "type": "fork",
                "amount": 2.0,
                "price": 50000.0,
                "fee": 0.0,
                "profit_loss": 100000.0,
            },
            {
                "timestamp": datetime(2024, 1, 3, 10, 0, 0),
                "exchange": "coincheck",
                "symbol": "ETH/JPY",
                "type": "reward",
                "amount": 0.5,
                "price": 320000.0,
                "fee": 0.0,
                "profit_loss": 160000.0,
            },
        ]

        pdf_bytes = reporter.generate(
            results=results,
            total_profit_loss=3260000.0,
            calc_method="総平均法",
        )

        # PDFが生成されたことを確認
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_empty_results(self) -> None:
        """結果が空の場合でもPDFが生成できること."""
        reporter = PDFReporter()

        pdf_bytes = reporter.generate(
            results=[],
            total_profit_loss=0.0,
            calc_method="移動平均法",
        )

        # PDFが生成されたことを確認
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"

    def test_generate_pdf_large_dataset(self) -> None:
        """大量のデータでもPDFが生成できること."""
        reporter = PDFReporter()

        # 100件のダミーデータを生成
        results = [
            {
                "timestamp": datetime(2024, (i // 28) + 1, (i % 28) + 1, 10, 0, 0),
                "exchange": "bitflyer",
                "symbol": "BTC/JPY",
                "type": "buy" if i % 2 == 0 else "sell",
                "amount": 0.1,
                "price": 5000000.0 + i * 10000,
                "fee": 100.0,
                "profit_loss": 0.0 if i % 2 == 0 else 10000.0,
            }
            for i in range(100)
        ]

        pdf_bytes = reporter.generate(
            results=results,
            total_profit_loss=500000.0,
            calc_method="移動平均法",
        )

        # PDFが生成されたことを確認
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes[:4] == b"%PDF"
