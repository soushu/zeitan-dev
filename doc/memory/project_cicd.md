---
name: project_cicd
description: CI/CD デプロイ環境・GCP・systemd・DB 構成
type: project
---

## CI/CD デプロイ環境
- GCPインスタンス: bitpoint-bot (e2-micro, us-west1-b)
- 本番: zeitan.soushu.biz (backend:8003, frontend:3003) ← main ブランチ
- ステージング: dev.zeitan.soushu.biz (backend:8004, frontend:3004) ← develop ブランチ
- GitHub Actions + WIF認証、concurrency group: `deploy-gce`（claudia と共有）
- サーバー上パス: `/home/yutookiguchi/zeitan-dev` (本番) / `zeitan-dev-staging` (ステージング)
- systemd: `zeitan-backend`, `zeitan-frontend`, `zeitan-staging-backend`, `zeitan-staging-frontend`
- DB: PostgreSQL `zeitan` / `zeitan_staging`（claudia ユーザー共有）

**Why:** ステージング環境で develop ブランチを自動デプロイし、本番は main ブランチのみ。
**How to apply:** デプロイ関連の変更は develop→ステージングで検証してから main にマージ。

## 本番リリース注意
- **本番(main)にはまだフロントエンド等マージされていない。初回リリース時に develop→main マージが必要。**
