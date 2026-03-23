"""DB サービス層のテスト（インメモリ SQLite で隔離）."""

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.models.orm import CalcSession
from src.utils.database import Base
from src.utils.db_service import (
    get_session_detail,
    get_sessions,
    save_calculation,
)


@pytest.fixture()
def db():
    """インメモリ SQLite を使うテスト用 DB セッション."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # ORM モデルを登録
    from src.models import orm  # noqa: F401

    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


def _sample_transactions():
    return [
        {
            "timestamp": datetime(2024, 1, 1, 10, 0, 0),
            "exchange": "bitflyer",
            "symbol": "BTC/JPY",
            "type": "buy",
            "amount": 1.0,
            "price": 5_000_000.0,
            "fee": 1000.0,
        },
        {
            "timestamp": datetime(2024, 1, 2, 10, 0, 0),
            "exchange": "bitflyer",
            "symbol": "BTC/JPY",
            "type": "sell",
            "amount": 1.0,
            "price": 5_500_000.0,
            "fee": 1000.0,
        },
    ]


def _sample_results():
    return [
        {
            "timestamp": datetime(2024, 1, 1, 10, 0, 0),
            "exchange": "bitflyer",
            "symbol": "BTC/JPY",
            "type": "buy",
            "amount": 1.0,
            "price": 5_000_000.0,
            "fee": 1000.0,
            "profit_loss": 0.0,
            "average_cost_after": 5_001_000.0,
        },
        {
            "timestamp": datetime(2024, 1, 2, 10, 0, 0),
            "exchange": "bitflyer",
            "symbol": "BTC/JPY",
            "type": "sell",
            "amount": 1.0,
            "price": 5_500_000.0,
            "fee": 1000.0,
            "profit_loss": 498_000.0,
            "average_cost_after": None,
        },
    ]


class TestSaveCalculation:
    """save_calculation のテスト."""

    def test_save_calculation(self, db):
        """session, transaction, result が正しく保存されること."""
        txs = _sample_transactions()
        results = _sample_results()

        calc_session = save_calculation(
            db=db,
            transactions=txs,
            results=results,
            total_profit_loss=498_000.0,
            calc_method="moving_average",
        )

        assert calc_session.id is not None
        assert calc_session.calc_method == "moving_average"
        assert calc_session.total_profit_loss == 498_000.0
        assert calc_session.transaction_count == 2
        assert len(calc_session.transactions) == 2
        assert len(calc_session.results) == 2

    def test_get_sessions(self, db):
        """複数セッションが取得できること."""
        save_calculation(db, _sample_transactions(), _sample_results(), 100.0, "moving_average")
        save_calculation(db, _sample_transactions(), _sample_results(), 200.0, "total_average")

        sessions = get_sessions(db)
        assert len(sessions) == 2

    def test_get_session_detail_includes_transactions(self, db):
        """セッション詳細にリレーションが含まれること."""
        saved = save_calculation(
            db, _sample_transactions(), _sample_results(), 498_000.0, "moving_average"
        )
        detail = get_session_detail(db, saved.id)

        assert detail is not None
        assert detail.id == saved.id
        assert len(detail.transactions) == 2
        assert len(detail.results) == 2

    def test_get_session_detail_not_found(self, db):
        """存在しない session_id では None が返ること."""
        result = get_session_detail(db, session_id=9999)
        assert result is None

    def test_transaction_cascade_delete(self, db):
        """セッション削除時に関連データも削除されること."""
        from src.models.orm import TradeResultRecord, Transaction

        saved = save_calculation(
            db, _sample_transactions(), _sample_results(), 498_000.0, "moving_average"
        )
        session_id = saved.id

        db.delete(saved)
        db.commit()

        assert db.query(CalcSession).filter(CalcSession.id == session_id).first() is None
        assert db.query(Transaction).filter(Transaction.session_id == session_id).count() == 0
        assert db.query(TradeResultRecord).filter(TradeResultRecord.session_id == session_id).count() == 0
