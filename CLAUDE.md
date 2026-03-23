# Zeitan Dev - Claude Code Guide

## Project
暗号資産税金計算アプリ。FastAPI + Next.js (App Router) + PostgreSQL。

## Development Workflow
1. develop から `feature/*` ブランチを切る
2. 実装
3. ブラウザで動作確認（問題があれば修正→再確認を繰り返す）
4. 問題なければユーザーに報告し、マージ指示を待つ
5. **main へのマージはユーザー指示があるまで絶対にしない**

## Git Rules
- main に直接コミット禁止
- develop に直接コミット禁止（ドキュメントのみ例外）
- fast-forward マージ禁止（必ず `--no-ff`）
- feature ブランチはマージ後も削除しない

## Local Dev
- Backend: `uvicorn api.main:app --reload` (port 8000)
- Frontend: `cd frontend && npm run dev` (port 3000)
- Test: `PYTHONPATH=. venv/Scripts/pytest tests/ -v`

## Architecture
- Backend: `api/` (FastAPI routers), `src/` (models, parsers, utils)
- Frontend: `frontend/` (Next.js 16, TypeScript, Tailwind v4, shadcn/ui)
- DB: PostgreSQL (prod/staging), SQLite (local)

## Deploy
- Staging: dev.zeitan.soushu.biz (develop branch, auto-deploy)
- Production: zeitan.soushu.biz (main branch, auto-deploy)

## Memory
詳細なメモリは `docs/memory/` を参照。
