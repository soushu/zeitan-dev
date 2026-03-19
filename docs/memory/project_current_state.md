---
name: project_current_state
description: 現在の開発状態・ブランチ状況・起動方法
type: project
---

## Current State (2026-03-19)
- 現在のブランチ: **develop**（全 feature/* マージ済み）
- CI/CD 環境構築完了、ステージング稼働中
- 起動方法:
  - バックエンド: `uvicorn api.main:app --reload`
  - フロント: `cd frontend && npm run dev` (port 3000)
- 次の作業は develop から新しい feature/* ブランチを切って開始すること
