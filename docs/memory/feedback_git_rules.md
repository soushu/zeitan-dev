---
name: feedback_git_rules
description: Git ブランチ運用ルール（main/develop/feature）
type: feedback
---

- **main へのマージはリリース時のみ**。開発中は絶対にしない。
- feature/* → develop へマージ。直接 develop にコミットしない。
- **新機能は必ず develop から新 feature/* ブランチを切って作業。**

**Why:** main は本番デプロイに直結するため、未完成の機能が混入するのを防ぐ。
**How to apply:** 作業開始時は必ず `git checkout develop && git checkout -b feature/xxx` から。
