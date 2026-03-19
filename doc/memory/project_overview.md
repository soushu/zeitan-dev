---
name: project_overview
description: Zeitan プロジェクトの全体概要・アーキテクチャ・技術スタック
type: project
---

## Project Overview
暗号資産税金計算アプリ。CSV→パース→計算→DB永続化→表示の流れ。
- **Next.js フロント** (`frontend/`) ← メインUI
- FastAPI バックエンド (`api/main.py`)
- SQLAlchemy 2.0 ORM + PostgreSQL（本番/ステージング）/ SQLite（ローカル）
- Streamlit (`src/main.py`) は並行運用中だが非推奨

## Key Architecture
- `src/utils/database.py`: engine, SessionLocal, Base, get_db(), init_db()
  - DATABASE_URL env var → SQLite フォールバック（絶対パス）
- `src/models/orm.py`: CalcSession / Transaction / TradeResultRecord（Mapped スタイル）
- `src/utils/db_service.py`: save_calculation / get_sessions / get_session_detail
- `api/routers/`: history.py, dashboard.py, parse.py, calculate.py, report.py

## Next.js Frontend (`frontend/`)
- Next.js 16 (App Router) + TypeScript + Tailwind CSS v4 + shadcn/ui
- `lib/types.ts`: FastAPI Pydantic モデル対応の TS 型
- `lib/api.ts`: parse/calculate/report/history/dashboard の fetch クライアント
- `next.config.ts`: `/api/*` → `BACKEND_URL` env var（デフォルト `http://localhost:8000`）リバースプロキシ
- ビルド: `next build --webpack`（Turbopack は e2-micro で OOM するため）
- 起動: `cd frontend && npm run dev` (port 3000)

## Shared Components (frontend/components/)
- `NavLinks.tsx`: usePathname() によるアクティブナビ（"use client" 必須）
- `BreakdownTables.tsx`: 通貨別・取引所別テーブル（計算結果・履歴詳細の両方で使用）
- `lib/format.ts`: formatJPY / formatDate / methodLabel 共通化

## Dashboard (`/dashboard` route)
- `api/routers/dashboard.py`: GET /api/dashboard?session_id=N
- `frontend/components/DashboardClient.tsx`: KPIカード・月別グラフ・通貨別/取引所別テーブル
- recharts 3.7.0 使用

## Timezone Handling
- 全タイムスタンプを **JST naive datetime** に統一して保存
- `src/parsers/base.py`: `utc_to_jst(dt)` ヘルパー定義
- 全16パーサー修正済み
