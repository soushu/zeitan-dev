"""FastAPI エンドポイントのテスト."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.main import app
from src.utils.database import Base, get_db


def _make_test_db():
    """インメモリ SQLite エンジンとセッションファクトリを返す.

    StaticPool を使い、全接続で同一のインメモリ DB を共有する。
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from src.models import orm  # noqa: F401

    Base.metadata.create_all(bind=engine)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def client():
    """テスト用 DB を使う TestClient."""
    TestingSessionLocal = _make_test_db()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


class TestAPIEndpoints:
    """API エンドポイントのテスト."""

    def test_root_endpoint(self, client) -> None:
        """ルートエンドポイントが正しく応答すること."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health_check(self, client) -> None:
        """ヘルスチェックエンドポイントが正しく応答すること."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_get_exchanges(self, client) -> None:
        """取引所一覧が取得できること."""
        response = client.get("/api/exchanges")
        assert response.status_code == 200
        data = response.json()
        assert "exchanges" in data
        assert "total" in data
        assert data["total"] == 10  # 国内7 + 海外3

    def test_calculate_moving_average(self, client) -> None:
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
        assert "session_id" in data
        assert isinstance(data["session_id"], int)
        assert data["method"] == "moving_average"
        assert len(data["results"]) == 2

    def test_calculate_total_average(self, client) -> None:
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
        assert "session_id" in data
        assert len(data["results"]) == 2

    def test_calculate_invalid_method(self, client) -> None:
        """無効な計算方法でエラーになること."""
        request_data = {
            "transactions": [],
            "method": "invalid_method",
        }

        response = client.post("/api/calculate", json=request_data)
        assert response.status_code == 422  # Validation error

    def test_history_initially_empty(self, client) -> None:
        """計算前は履歴が空であること."""
        response = client.get("/api/history")
        assert response.status_code == 200
        assert response.json() == []

    def test_history_after_calculate(self, client) -> None:
        """計算後に履歴が1件追加されること."""
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
            ],
            "method": "moving_average",
        }
        client.post("/api/calculate", json=request_data)

        response = client.get("/api/history")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["calc_method"] == "moving_average"

    def test_history_detail_not_found(self, client) -> None:
        """存在しない session_id で 404 が返ること."""
        response = client.get("/api/history/9999")
        assert response.status_code == 404

    def test_history_detail(self, client) -> None:
        """計算後に履歴詳細が取得できること."""
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
            ],
            "method": "moving_average",
        }
        calc_resp = client.post("/api/calculate", json=request_data)
        session_id = calc_resp.json()["session_id"]

        response = client.get(f"/api/history/{session_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == session_id
        assert len(data["transactions"]) == 1
        assert len(data["results"]) == 1
