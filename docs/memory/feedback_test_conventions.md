---
name: feedback_test_conventions
description: テスト実行方法・規約（pytest, SQLite, API テスト）
type: feedback
---

- pytest, PYTHONPATH=. venv/bin/pytest tests/ -v
- インメモリ SQLite テスト: `StaticPool` 必須
- API テスト: `app.dependency_overrides[get_db]` でテスト用DBに差し替え
- テスト数: 119件全パス確認済み

**Why:** テスト環境の一貫性を保ち、CI/CD でも安定して動作させるため。
**How to apply:** 新しいテスト追加時はこの規約に従う。テスト用CSVは `data/uploads/` に統一。
