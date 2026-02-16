"""取引所CSVパーサーのユニットテスト."""

from datetime import datetime
from pathlib import Path

import pytest

from src.parsers import (
    BinanceParser,
    BitbankParser,
    BitflyerParser,
    CoinbaseParser,
    CoincheckParser,
    GMOParser,
    KrakenParser,
    LineBitmaxParser,
    RakutenParser,
    SBIVCParser,
)
from src.parsers.base import TransactionFormat

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class TestBitflyerParser:
    """BitflyerParser のテスト."""

    def test_exchange_name(self) -> None:
        """exchange_name が 'bitflyer' であること."""
        parser = BitflyerParser()
        assert parser.exchange_name == "bitflyer"

    def test_validate_ok(self) -> None:
        """正しい bitFlyer CSV で validate が True を返すこと."""
        parser = BitflyerParser()
        path = FIXTURES_DIR / "sample_bitflyer.csv"
        assert path.exists()
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルで FileNotFoundError が発生すること."""
        parser = BitflyerParser()
        with pytest.raises(FileNotFoundError):
            parser.validate(FIXTURES_DIR / "nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """parse が標準フォーマットのリストを返すこと."""
        parser = BitflyerParser()
        path = FIXTURES_DIR / "sample_bitflyer.csv"
        result = parser.parse(path)
        assert len(result) == 3
        for row in result:
            assert isinstance(row, dict)
            assert set(row.keys()) == {
                "timestamp",
                "exchange",
                "symbol",
                "type",
                "amount",
                "price",
                "fee",
            }
            assert isinstance(row["timestamp"], datetime)
            assert row["exchange"] == "bitflyer"
            assert row["symbol"] in ("BTC/JPY", "ETH/JPY")
            assert row["type"] in ("buy", "sell")
            assert isinstance(row["amount"], float)
            assert isinstance(row["price"], float)
            assert isinstance(row["fee"], (int, float))

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = BitflyerParser()
        path = FIXTURES_DIR / "sample_bitflyer.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/JPY"
        assert first["amount"] == 0.01
        assert first["price"] == 5000000.0
        assert first["fee"] == 50.0
        assert first["timestamp"].year == 2024 and first["timestamp"].month == 1


class TestCoincheckParser:
    """CoincheckParser のテスト."""

    def test_exchange_name(self) -> None:
        """exchange_name が 'coincheck' であること."""
        parser = CoincheckParser()
        assert parser.exchange_name == "coincheck"

    def test_validate_ok(self) -> None:
        """正しい Coincheck CSV で validate が True を返すこと."""
        parser = CoincheckParser()
        path = FIXTURES_DIR / "sample_coincheck.csv"
        assert path.exists()
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルで FileNotFoundError が発生すること."""
        parser = CoincheckParser()
        with pytest.raises(FileNotFoundError):
            parser.validate(FIXTURES_DIR / "nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """parse が標準フォーマットのリストを返すこと."""
        parser = CoincheckParser()
        path = FIXTURES_DIR / "sample_coincheck.csv"
        result = parser.parse(path)
        assert len(result) == 3
        for row in result:
            assert isinstance(row, dict)
            assert set(row.keys()) == {
                "timestamp",
                "exchange",
                "symbol",
                "type",
                "amount",
                "price",
                "fee",
            }
            assert isinstance(row["timestamp"], datetime)
            assert row["exchange"] == "coincheck"
            assert row["symbol"] == "BTC/JPY"
            assert row["type"] in ("buy", "sell")
            assert isinstance(row["amount"], float)
            assert isinstance(row["price"], float)
            assert isinstance(row["fee"], (int, float))

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = CoincheckParser()
        path = FIXTURES_DIR / "sample_coincheck.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/JPY"
        assert first["amount"] == 0.01
        assert first["price"] == 5000000.0
        assert first["fee"] == 0.0
        assert first["timestamp"].year == 2024 and first["timestamp"].month == 1

    def test_parse_fee_and_third_row(self) -> None:
        """3行目で手数料(円)が正しくパースされること."""
        parser = CoincheckParser()
        path = FIXTURES_DIR / "sample_coincheck.csv"
        result = parser.parse(path)
        assert len(result) >= 3
        third = result[2]
        assert third["fee"] == 100.0
        assert third["amount"] == 0.5
        assert third["price"] == 350000.0


class TestGMOParser:
    """GMOParser のテスト."""

    def test_exchange_name(self) -> None:
        """exchange_name が 'gmo' であること."""
        parser = GMOParser()
        assert parser.exchange_name == "gmo"

    def test_validate_ok(self) -> None:
        """正しい GMOコイン CSV で validate が True を返すこと."""
        parser = GMOParser()
        path = FIXTURES_DIR / "sample_gmo.csv"
        assert path.exists()
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルで FileNotFoundError が発生すること."""
        parser = GMOParser()
        with pytest.raises(FileNotFoundError):
            parser.validate(FIXTURES_DIR / "nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """parse が標準フォーマットのリストを返すこと."""
        parser = GMOParser()
        path = FIXTURES_DIR / "sample_gmo.csv"
        result = parser.parse(path)
        assert len(result) == 3
        for row in result:
            assert isinstance(row, dict)
            assert set(row.keys()) == {
                "timestamp",
                "exchange",
                "symbol",
                "type",
                "amount",
                "price",
                "fee",
            }
            assert isinstance(row["timestamp"], datetime)
            assert row["exchange"] == "gmo"
            assert row["symbol"] in ("BTC/JPY", "ETH/JPY")
            assert row["type"] in ("buy", "sell")
            assert isinstance(row["amount"], float)
            assert isinstance(row["price"], float)
            assert isinstance(row["fee"], (int, float))

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = GMOParser()
        path = FIXTURES_DIR / "sample_gmo.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/JPY"
        assert first["amount"] == 0.01
        assert first["price"] == 5000000.0
        assert first["fee"] == 50.0
        assert first["timestamp"].year == 2024 and first["timestamp"].month == 1

    def test_parse_eth_row(self) -> None:
        """3行目（ETH）が正しくパースされること."""
        parser = GMOParser()
        path = FIXTURES_DIR / "sample_gmo.csv"
        result = parser.parse(path)
        assert len(result) >= 3
        third = result[2]
        assert third["symbol"] == "ETH/JPY"
        assert third["amount"] == 0.5
        assert third["price"] == 350000.0
        assert third["fee"] == 100.0


class TestBitbankParser:
    """BitbankParser のテスト."""

    def test_exchange_name(self) -> None:
        """exchange_name が 'bitbank' であること."""
        parser = BitbankParser()
        assert parser.exchange_name == "bitbank"

    def test_validate_ok(self) -> None:
        """正しい bitbank CSV で validate が True を返すこと."""
        parser = BitbankParser()
        path = FIXTURES_DIR / "sample_bitbank.csv"
        assert path.exists()
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルで FileNotFoundError が発生すること."""
        parser = BitbankParser()
        with pytest.raises(FileNotFoundError):
            parser.validate(FIXTURES_DIR / "nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """parse が標準フォーマットのリストを返すこと."""
        parser = BitbankParser()
        path = FIXTURES_DIR / "sample_bitbank.csv"
        result = parser.parse(path)
        assert len(result) == 3
        for row in result:
            assert isinstance(row, dict)
            assert set(row.keys()) == {
                "timestamp",
                "exchange",
                "symbol",
                "type",
                "amount",
                "price",
                "fee",
            }
            assert isinstance(row["timestamp"], datetime)
            assert row["exchange"] == "bitbank"
            assert row["symbol"] in ("BTC/JPY", "ETH/JPY")
            assert row["type"] in ("buy", "sell")
            assert isinstance(row["amount"], float)
            assert isinstance(row["price"], float)
            assert isinstance(row["fee"], (int, float))

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = BitbankParser()
        path = FIXTURES_DIR / "sample_bitbank.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/JPY"
        assert first["amount"] == 0.01
        assert first["price"] == 5000000.0
        assert first["fee"] == 50.0
        assert first["timestamp"].year == 2024 and first["timestamp"].month == 1

    def test_parse_eth_row(self) -> None:
        """3行目（ETH）が正しくパースされること."""
        parser = BitbankParser()
        path = FIXTURES_DIR / "sample_bitbank.csv"
        result = parser.parse(path)
        assert len(result) >= 3
        third = result[2]
        assert third["symbol"] == "ETH/JPY"
        assert third["amount"] == 0.5
        assert third["price"] == 350000.0
        assert third["fee"] == 100.0


class TestSBIVCParser:
    """SBIVCParser のテスト."""

    def test_exchange_name(self) -> None:
        """exchange_name が 'sbivc' であること."""
        parser = SBIVCParser()
        assert parser.exchange_name == "sbivc"

    def test_validate_ok(self) -> None:
        """正しい SBI VCトレード CSV で validate が True を返すこと."""
        parser = SBIVCParser()
        path = FIXTURES_DIR / "sample_sbivc.csv"
        assert path.exists()
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルで FileNotFoundError が発生すること."""
        parser = SBIVCParser()
        with pytest.raises(FileNotFoundError):
            parser.validate(FIXTURES_DIR / "nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """parse が標準フォーマットのリストを返すこと."""
        parser = SBIVCParser()
        path = FIXTURES_DIR / "sample_sbivc.csv"
        result = parser.parse(path)
        assert len(result) == 3
        for row in result:
            assert isinstance(row, dict)
            assert set(row.keys()) == {
                "timestamp",
                "exchange",
                "symbol",
                "type",
                "amount",
                "price",
                "fee",
            }
            assert isinstance(row["timestamp"], datetime)
            assert row["exchange"] == "sbivc"
            assert row["symbol"] in ("BTC/JPY", "ETH/JPY")
            assert row["type"] in ("buy", "sell")
            assert isinstance(row["amount"], float)
            assert isinstance(row["price"], float)
            assert isinstance(row["fee"], (int, float))

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = SBIVCParser()
        path = FIXTURES_DIR / "sample_sbivc.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/JPY"
        assert first["amount"] == 0.01
        assert first["price"] == 5000000.0
        assert first["fee"] == 50.0
        assert first["timestamp"].year == 2024 and first["timestamp"].month == 1


class TestRakutenParser:
    """RakutenParser のテスト."""

    def test_exchange_name(self) -> None:
        """exchange_name が 'rakuten' であること."""
        parser = RakutenParser()
        assert parser.exchange_name == "rakuten"

    def test_validate_ok(self) -> None:
        """正しい 楽天ウォレット CSV で validate が True を返すこと."""
        parser = RakutenParser()
        path = FIXTURES_DIR / "sample_rakuten.csv"
        assert path.exists()
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルで FileNotFoundError が発生すること."""
        parser = RakutenParser()
        with pytest.raises(FileNotFoundError):
            parser.validate(FIXTURES_DIR / "nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """parse が標準フォーマットのリストを返すこと."""
        parser = RakutenParser()
        path = FIXTURES_DIR / "sample_rakuten.csv"
        result = parser.parse(path)
        assert len(result) == 3
        for row in result:
            assert isinstance(row, dict)
            assert set(row.keys()) == {
                "timestamp",
                "exchange",
                "symbol",
                "type",
                "amount",
                "price",
                "fee",
            }
            assert isinstance(row["timestamp"], datetime)
            assert row["exchange"] == "rakuten"
            assert row["symbol"] in ("BTC/JPY", "ETH/JPY")
            assert row["type"] in ("buy", "sell")
            assert isinstance(row["amount"], float)
            assert isinstance(row["price"], float)
            assert isinstance(row["fee"], (int, float))

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = RakutenParser()
        path = FIXTURES_DIR / "sample_rakuten.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/JPY"
        assert first["amount"] == 0.01
        assert first["price"] == 5000000.0
        assert first["fee"] == 50.0
        assert first["timestamp"].year == 2024 and first["timestamp"].month == 1


class TestLineBitmaxParser:
    """LineBitmaxParser のテスト."""

    def test_exchange_name(self) -> None:
        """exchange_name が 'linebitmax' であること."""
        parser = LineBitmaxParser()
        assert parser.exchange_name == "linebitmax"

    def test_validate_ok(self) -> None:
        """正しい LINE BITMAX CSV で validate が True を返すこと."""
        parser = LineBitmaxParser()
        path = FIXTURES_DIR / "sample_linebitmax.csv"
        assert path.exists()
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルで FileNotFoundError が発生すること."""
        parser = LineBitmaxParser()
        with pytest.raises(FileNotFoundError):
            parser.validate(FIXTURES_DIR / "nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """parse が標準フォーマットのリストを返すこと."""
        parser = LineBitmaxParser()
        path = FIXTURES_DIR / "sample_linebitmax.csv"
        result = parser.parse(path)
        assert len(result) == 3
        for row in result:
            assert isinstance(row, dict)
            assert set(row.keys()) == {
                "timestamp",
                "exchange",
                "symbol",
                "type",
                "amount",
                "price",
                "fee",
            }
            assert isinstance(row["timestamp"], datetime)
            assert row["exchange"] == "linebitmax"
            assert row["symbol"] in ("BTC/JPY", "ETH/JPY")
            assert row["type"] in ("buy", "sell")
            assert isinstance(row["amount"], float)
            assert isinstance(row["price"], float)
            assert isinstance(row["fee"], (int, float))

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = LineBitmaxParser()
        path = FIXTURES_DIR / "sample_linebitmax.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/JPY"
        assert first["amount"] == 0.01
        assert first["price"] == 5000000.0
        assert first["fee"] == 50.0
        assert first["timestamp"].year == 2024 and first["timestamp"].month == 1


class TestBinanceParser:
    """BinanceParser のテスト."""

    def test_exchange_name(self) -> None:
        """取引所名が正しいこと."""
        parser = BinanceParser()
        assert parser.exchange_name == "binance"

    def test_validate_ok(self) -> None:
        """正しいBinance CSVを検証できること."""
        parser = BinanceParser()
        path = FIXTURES_DIR / "sample_binance.csv"
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルでエラーが発生すること."""
        parser = BinanceParser()
        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """パース結果が標準フォーマットを満たすこと."""
        parser = BinanceParser()
        path = FIXTURES_DIR / "sample_binance.csv"
        result = parser.parse(path)
        assert isinstance(result, list)
        assert len(result) > 0

        for row in result:
            assert "timestamp" in row
            assert "exchange" in row
            assert "symbol" in row
            assert "type" in row
            assert "amount" in row
            assert "price" in row
            assert "fee" in row

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = BinanceParser()
        path = FIXTURES_DIR / "sample_binance.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/USDT"
        assert first["amount"] == 0.5
        assert first["price"] == 42000.0
        assert first["fee"] == 10.5


class TestCoinbaseParser:
    """CoinbaseParser のテスト."""

    def test_exchange_name(self) -> None:
        """取引所名が正しいこと."""
        parser = CoinbaseParser()
        assert parser.exchange_name == "coinbase"

    def test_validate_ok(self) -> None:
        """正しいCoinbase CSVを検証できること."""
        parser = CoinbaseParser()
        path = FIXTURES_DIR / "sample_coinbase.csv"
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルでエラーが発生すること."""
        parser = CoinbaseParser()
        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """パース結果が標準フォーマットを満たすこと."""
        parser = CoinbaseParser()
        path = FIXTURES_DIR / "sample_coinbase.csv"
        result = parser.parse(path)
        assert isinstance(result, list)
        assert len(result) > 0

        for row in result:
            assert "timestamp" in row
            assert "exchange" in row
            assert "symbol" in row
            assert "type" in row
            assert "amount" in row
            assert "price" in row
            assert "fee" in row

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = CoinbaseParser()
        path = FIXTURES_DIR / "sample_coinbase.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/USD"
        assert first["amount"] == 0.5
        assert first["price"] == 42000.0
        assert first["fee"] == 50.0


class TestKrakenParser:
    """KrakenParser のテスト."""

    def test_exchange_name(self) -> None:
        """取引所名が正しいこと."""
        parser = KrakenParser()
        assert parser.exchange_name == "kraken"

    def test_validate_ok(self) -> None:
        """正しいKraken CSVを検証できること."""
        parser = KrakenParser()
        path = FIXTURES_DIR / "sample_kraken.csv"
        assert parser.validate(path) is True

    def test_validate_file_not_found(self) -> None:
        """存在しないファイルでエラーが発生すること."""
        parser = KrakenParser()
        with pytest.raises(FileNotFoundError):
            parser.parse("nonexistent.csv")

    def test_parse_returns_standard_format(self) -> None:
        """パース結果が標準フォーマットを満たすこと."""
        parser = KrakenParser()
        path = FIXTURES_DIR / "sample_kraken.csv"
        result = parser.parse(path)
        assert isinstance(result, list)
        assert len(result) > 0

        for row in result:
            assert "timestamp" in row
            assert "exchange" in row
            assert "symbol" in row
            assert "type" in row
            assert "amount" in row
            assert "price" in row
            assert "fee" in row

    def test_parse_values(self) -> None:
        """サンプルCSVの1行目が正しくパースされること."""
        parser = KrakenParser()
        path = FIXTURES_DIR / "sample_kraken.csv"
        result = parser.parse(path)
        first = result[0]
        assert first["type"] == "buy"
        assert first["symbol"] == "BTC/USD"
        assert first["amount"] == 0.5
        assert first["price"] == 42000.0
        assert first["fee"] == 25.0
