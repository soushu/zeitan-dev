# Zeitan 開発ガイド

## 🌿 ブランチ戦略

このプロジェクトでは **Git Flow** ベースのブランチ戦略を採用しています。

### ブランチ構成

```
main        ← 本番リリース用（安定版）
  ↑
develop     ← 開発の軸（統合ブランチ）
  ↑
feature/*   ← 機能開発ブランチ
```

### ブランチの役割

| ブランチ | 用途 | マージ先 |
|---------|------|---------|
| `main` | 本番リリース済みコード | - |
| `develop` | 開発中の統合ブランチ | `main` |
| `feature/*` | 新機能・改善の開発 | `develop` |
| `hotfix/*` | 本番の緊急修正 | `main` と `develop` |

---

## 🚀 開発フロー

### 1. 新機能開発の開始

```bash
# developブランチを最新化
git checkout develop
git pull origin develop

# 機能ブランチを作成
git checkout -b feature/機能名

# 例:
git checkout -b feature/add-pdf-report
git checkout -b feature/support-defi-transactions
```

### 2. 開発・コミット

```bash
# コードを変更
# ...

# 変更をステージング
git add .

# コミット（コミットメッセージ規約に従う）
git commit -m "feat: 機能の説明"

# リモートにプッシュ
git push -u origin feature/機能名
```

### 3. developへのマージ

#### 方法1: プルリクエスト（推奨）

1. GitHubでプルリクエストを作成
   - Base: `develop`
   - Compare: `feature/機能名`

2. レビュー・承認後、マージ

3. ローカルのdevelopを更新
   ```bash
   git checkout develop
   git pull origin develop
   ```

#### 方法2: ローカルマージ

```bash
# developに切り替え
git checkout develop

# 機能ブランチをマージ
git merge --no-ff feature/機能名

# リモートにプッシュ
git push origin develop

# 使用済みブランチを削除
git branch -d feature/機能名
git push origin --delete feature/機能名
```

### 4. 本番リリース（developからmainへ）

```bash
# mainに切り替え
git checkout main

# developをマージ
git merge --no-ff develop

# タグを付ける
git tag -a v1.1.0 -m "Release v1.1.0"

# リモートにプッシュ
git push origin main --tags
```

---

## 📋 コミットメッセージ規約

### フォーマット

```
<type>: <subject>

[optional body]

[optional footer]
```

### Type（種別）

| Type | 用途 | 例 |
|------|------|-----|
| `feat` | 新機能追加 | `feat: PDF レポート生成機能を追加` |
| `fix` | バグ修正 | `fix: 総平均法の計算エラーを修正` |
| `docs` | ドキュメント変更 | `docs: READMEに使用例を追加` |
| `style` | コードスタイル修正 | `style: インデントを修正` |
| `refactor` | リファクタリング | `refactor: パーサーのコードを整理` |
| `test` | テスト追加・修正 | `test: 移動平均法のテストを追加` |
| `chore` | ビルド・設定変更 | `chore: requirements.txt を更新` |

### 例

```bash
# 良い例
git commit -m "feat: 楽天ウォレットのパーサーを追加"
git commit -m "fix: CSV読み込み時の文字コードエラーを修正"
git commit -m "docs: 開発ガイドを作成"

# 悪い例
git commit -m "update"
git commit -m "fix bug"
git commit -m "色々修正"
```

---

## 🧪 テストの実行

### すべてのテストを実行

```bash
# 仮想環境を有効化
source venv/bin/activate

# PYTHONPATHを設定
export PYTHONPATH=$(pwd)

# pytestを実行
pytest -v
```

### 特定のテストのみ実行

```bash
# パーサーテストのみ
pytest tests/test_parsers.py -v

# 計算エンジンテストのみ
pytest tests/test_calculators.py -v

# 特定のテストクラスのみ
pytest tests/test_parsers.py::TestBitflyerParser -v
```

### コミット前のチェック

```bash
# テストがすべて通過することを確認
pytest

# コードスタイルチェック（将来追加予定）
# black --check src/ tests/
# ruff check src/ tests/
```

---

## 📦 プルリクエストの作成

### タイトル

コミットメッセージと同じ形式：

```
feat: 新機能の説明
fix: バグ修正の説明
```

### 説明テンプレート

```markdown
## 概要
この変更の目的を簡潔に説明

## 変更内容
- 追加した機能や修正した内容をリスト形式で記載
- 主要な変更ファイルを列挙

## テスト
- [ ] すべてのユニットテストが通過
- [ ] 新しいテストを追加（該当する場合）
- [ ] 手動テストを実施

## チェックリスト
- [ ] コードレビュー準備完了
- [ ] ドキュメント更新済み（該当する場合）
- [ ] CHANGELOG.md 更新済み（該当する場合）
```

---

## 🔧 開発環境のセットアップ

### 初回セットアップ

```bash
# リポジトリをクローン
git clone https://github.com/soushu/zeitan-dev.git
cd zeitan-dev

# 仮想環境を作成
python3.12 -m venv venv
source venv/bin/activate

# 依存関係をインストール
pip install -r requirements.txt

# 環境変数を設定
export PYTHONPATH=$(pwd)

# Streamlitを起動して動作確認
streamlit run src/main.py
```

### 開発時の起動

```bash
cd zeitan-dev
source venv/bin/activate
export PYTHONPATH=$(pwd)
streamlit run src/main.py
```

---

## 📁 プロジェクト構造

```
zeitan-dev/
├── src/                    # ソースコード
│   ├── calculators/        # 税金計算エンジン
│   ├── parsers/            # 取引所CSVパーサー
│   ├── models/             # データモデル
│   ├── utils/              # ユーティリティ
│   └── main.py             # Streamlitアプリ
├── tests/                  # テストコード
│   ├── test_parsers.py
│   └── test_calculators.py
├── examples/               # サンプルデータ
│   └── sample_csv/         # テスト用CSV
├── data/                   # データディレクトリ
│   ├── uploads/            # アップロードファイル（Git管理外）
│   └── reports/            # 生成レポート（Git管理外）
├── docs/                   # ドキュメント
├── requirements.txt        # 依存パッケージ
├── README.md               # プロジェクト概要
└── DEVELOPMENT.md          # 開発ガイド（このファイル）
```

---

## 🎯 Phase別の開発フォロー

### Phase 1（完了）
- ✅ 7取引所対応のCSVパーサー
- ✅ 移動平均法・総平均法の計算エンジン
- ✅ Streamlit UI

### Phase 2（予定）
- エッジケース対応（ハードフォーク、エアドロップ等）
- PDFレポート生成
- 海外取引所対応

### Phase 3（予定）
- FastAPI化
- DeFi/NFT対応

---

## 🚨 重要なルール

### ❌ やってはいけないこと

1. **mainブランチへの直接コミット禁止**
   - 必ずdevelopまたはfeatureブランチで作業

2. **強制プッシュ禁止**（特に共有ブランチ）
   ```bash
   # ❌ 禁止
   git push --force origin develop
   git push --force origin main
   ```

3. **大きなファイルのコミット禁止**
   - CSVファイル、データベースファイル等は `.gitignore` で除外

4. **テストが通らない状態でマージ禁止**
   - 必ず `pytest` を実行してすべて通過を確認

5. **AI（Claude等）は原則Git操作を行わない**
   - ブランチのマージ、プッシュ、PR作成等のGit操作は開発者が手動で行う
   - **例外**: 開発者が明示的に指示した場合のみ、AIがGit操作を実行してよい
   - AIにはコード生成、テスト実行、ファイル編集を依頼する

### ✅ 推奨すること

1. **小さく頻繁にコミット**
   - 機能単位でコミットを分割

2. **わかりやすいコミットメッセージ**
   - 規約に従った明確なメッセージ

3. **定期的なdevelopへの同期**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout feature/your-feature
   git merge develop  # コンフリクトを早期に解決
   ```

4. **コードレビューの実施**
   - プルリクエストを活用

---

## 🤖 AI（Claude）との協業ルール

### AIに任せて良いこと ✅

- **コード作成・編集**
  - 新機能の実装
  - バグ修正
  - リファクタリング
  - テストコード作成

- **ファイル操作**
  - ファイルの読み書き
  - ディレクトリ構造の確認

- **テスト実行**
  - pytestの実行
  - テスト結果の確認

- **調査・検索**
  - コードベースの検索
  - ドキュメント作成
  - Web検索による技術調査

### AIは原則やらない（明示的な指示があれば実行可） ⚠️

- **Git操作**
  - `git merge`
  - `git push`
  - `git pull`
  - `git checkout`
  - GitHub PR作成
  - ブランチの削除
  - **重要**: 開発者が「〇〇をプッシュして」「PRを作成して」等と明示的に指示した場合は実行してよい

- **重要な意思決定**
  - アーキテクチャの大幅な変更
  - 依存パッケージのメジャーアップデート
  - 本番環境への反映

### 理由

Git操作は開発フローの重要な部分であり、**開発者が意図を持って指示・実行する**ことで：
- マージのタイミングを適切に管理できる
- コンフリクト解決を自分で制御できる
- コミット履歴を意識的に構築できる
- 誤った操作のリスクを最小化できる

AIは開発者の明示的な指示がある場合にのみGit操作を実行し、自発的には行わない。

---

## 📞 困ったときは

1. **テストが通らない**
   ```bash
   # 依存関係を再インストール
   pip install -r requirements.txt --upgrade

   # キャッシュをクリア
   pytest --cache-clear
   ```

2. **マージコンフリクト**
   ```bash
   # developの最新を取得
   git checkout develop
   git pull origin develop

   # フィーチャーブランチでdevelopをマージ
   git checkout feature/your-feature
   git merge develop

   # コンフリクトを解決してコミット
   git add .
   git commit -m "merge: developをマージしてコンフリクト解決"
   ```

3. **間違えてコミットした**
   ```bash
   # 直前のコミットを取り消し（変更は保持）
   git reset --soft HEAD~1

   # 直前のコミットメッセージを修正
   git commit --amend -m "新しいメッセージ"
   ```

---

**最終更新**: 2026年2月15日
**メンテナー**: Zeitan開発チーム
