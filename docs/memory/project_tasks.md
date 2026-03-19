---
name: project_tasks
description: 残タスク一覧（優先度順）と将来タスク
type: project
---

## 残タスク（優先度順）
1. 計算方法ワンクリック切替（再アップロード不要で移動平均⇔総平均切替、Backend: `/api/recalculate/{session_id}`）
2. 年度フィルター機能強化（履歴一覧に年度ドロップダウン、`/api/history?year=2024`）
3. スマホ対応（レスポンシブデザイン、テーブル横スクロール、モバイルメニュー）
4. 要処理アラート機能（Gtax参考、売却>保有の問題取引を自動検出）

**Why:** ユーザー体験向上と実用性強化のため。
**How to apply:** 新タスク着手時は develop から feature/* ブランチを切る。

## 将来タスク（Phase 4以降）
- ユーザー管理（Supabase Auth）・マルチユーザー対応
- 決済機能（Stripe）
- 新税制エンジン（申告分離課税 20.315%・損失繰越3年）
