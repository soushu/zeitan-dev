"""FastAPI エンドポイントのテスト."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


class TestAPIEndpoints:
    """API エンドポイントのテスト."""

    def test_root_endpoint(self) -> None:
        """ルートエンドポイントが正しく応答すること."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_check(self) -> None:
        """ヘルスチェックエンドポイントが正しく応答すること."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_get_exchanges(self) -> None:
        """取引所一覧が取得できること."""
        response = client.get("/api/exchanges")
        assert response.status_code == 200
        data = response.json()
        assert "exchanges" in data
        assert "total" in data
        assert data["total"] == 10  # 国内7 + 海外3

    def test_calculate_moving_average(self) -> None:
        """移動平均法で計算できること."""
        request_data = {
            "transactions": [
                {
                    "timestamp": "2024-01-01T10:00:00",
                    "exchange": "bitflyer",
                    "symbol": "BTC/JPY",
                    "type": "buy",
                    "amount": 1.0,
                    "price": 5000000.0,
                    "fee": 1000.0,
                },
                {
                    "timestamp": "2024-01-02T10:00:00",
                    "exchange": "bitflyer",
                    "symbol": "BTC/JPY",
                    "type": "sell",
                    "amount": 1.0,
                    "price": 5500000.0,
                    "fee": 1000.0,
                },
            ],
            "method": "moving_average",
        }

        response = client.post("/api/calculate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total_profit_loss" in data
        assert "method" in data
        assert data["method"] == "moving_average"
        assert len(data["results"]) == 2

    def test_calculate_total_average(self) -> None:
        """総平均法で計算できること."""
        request_data = {
            "transactions": [
                {
                    "timestamp": "2024-01-01T10:00:00",
                    "exchange": "coincheck",
                    "symbol": "ETH/JPY",
                    "type": "buy",
                    "amount": 10.0,
                    "price": 300000.0,
                    "fee": 500.0,
                },
                {
                    "timestamp": "2024-01-02T10:00:00",
                    "exchange": "coincheck",
                    "symbol": "ETH/JPY",
                    "type": "sell",
                    "amount": 5.0,
                    "price": 350000.0,
                    "fee": 250.0,
                },
            ],
            "method": "total_average",
        }

        response = client.post("/api/calculate", json=request_data)
        assert response.status_code == 200
        data = response.json()
        assert data["method"] == "total_average"
        assert len(data["results"]) == 2

    def test_calculate_invalid_method(self) -> None:
        """無効な計算方法でエラーになること."""
        request_data = {
            "transactions": [],
            "method": "invalid_method",
        }

        response = client.post("/api/calculate", json=request_data)
        assert response.status_code == 422  # Validation error
