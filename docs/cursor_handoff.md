# Zeitan - Cursor引き継ぎプロンプト

## 🎯 このファイルについて
このファイルは、claude.aiでの長期にわたる議論・計画をCursorに引き継ぐためのものです。
開発に関する質問・実装はすべてCursor上で行います。

---

## 📋 プロジェクト概要

### プロジェクト名
**Zeitan（ゼイタン）**
- 由来：「税」+「簡単」
- ビジョン：日本の暗号通貨投資家の確定申告を簡単にする

### 開発者
- Python上級者
- 副業として週5-10時間
- MacBook Air使用
- Cursor（無料版）で開発

---

## 🏗️ 現在の開発環境（完了済み）

```
✅ Cursor インストール済み
✅ Python 3.12.10 インストール済み
✅ /Users/yutookiguchi/Work/zeitan-dev にプロジェクト作成済み
✅ 仮想環境（venv）作成・有効化済み
✅ Streamlitのローカルホスト表示確認済み
```

### 環境情報
```
OS: macOS (MacBook Air)
Python: 3.12.10
仮想環境: venv
プロジェクトフォルダ: /Users/yutookiguchi/Work/zeitan-dev
エディタ: Cursor（Auto-Run Mode: Run Everything Unsandboxed）
```

---

## 🗺️ 開発ロードマップ

### Phase 1（2026年3月〜6月）: MVP開発 ← 今ここ
```
目標: ローカルで動くStreamlitアプリ
対象: 旧税制（移動平均法・総平均法）のみ
```

### Phase 2（2026年7月〜9月）: 拡張
```
目標: 海外取引所対応、FastAPI化
```

### Phase 3（2026年10月〜12月）: 本格化
```
目標: DeFi/NFT対応、新税制エンジン開発開始
```

### Phase 4（2027年1月〜3月）: 正式リリース
```
目標: 確定申告シーズンに旧税制で正式運用
予想収益: 月$20,000〜$40,000
```

### Phase 5（2027年4月〜12月）: 新税制準備
```
目標: 2028年新税制の完全対応
```

### Phase 6（2028年1月〜）: 新税制元年
```
目標: 申告分離課税20.315%対応でリリース
予想収益: 月$50,000〜$100,000
```

---

## 💼 税制の理解（重要）

### 旧税制（〜2027年）← Phase 1で実装
```
課税方式: 雑所得（総合課税）
税率: 最大55%
計算方法: 移動平均法 or 総平均法
損失繰越: 不可
```

### 新税制（2028年〜）← Phase 3以降で実装
```
施行: 2028年1月
課税方式: 申告分離課税
税率: 一律20.315%
損失繰越: 3年間可能
損益通算: 暗号資産内で可能
```

---

## 🔧 技術スタック

### Phase 1（現在）
```
言語: Python 3.12.10
UI: Streamlit
DB: SQLite
ORM: SQLAlchemy
データ処理: pandas + numpy
レポート: python-docx
テスト: pytest
```

### Phase 2以降（予定）
```
バックエンド: FastAPI
フロントエンド: Next.js
DB: PostgreSQL（Supabase）
認証: Supabase Auth
決済: Stripe
ホスティング: Vercel + Railway
```

---

## 📁 プロジェクト構造

```
zeitan-dev/
├── src/
│   ├── __init__.py
│   ├── main.py              # Streamlitメインアプリ
│   ├── parsers/             # 取引所CSVパーサー
│   │   ├── __init__.py
│   │   ├── base.py          # 抽象基底クラス
│   │   ├── bitflyer.py      # bitFlyer
│   │   ├── coincheck.py     # Coincheck
│   │   ├── gmo.py           # GMOコイン
│   │   ├── bitbank.py       # bitbank
│   │   ├── sbivc.py         # SBI VCトレード
│   │   ├── rakuten.py       # 楽天ウォレット
│   │   └── linebitmax.py    # LINE BITMAX
│   ├── calculators/         # 税金計算エンジン
│   │   ├── __init__.py
│   │   ├── moving_average.py  # 移動平均法
│   │   └── total_average.py   # 総平均法
│   ├── models/              # データモデル
│   │   ├── __init__.py
│   │   └── transaction.py
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       └── formatter.py
├── tests/
│   ├── test_parsers.py
│   ├── test_calculators.py
│   └── fixtures/            # テスト用サンプルCSV
│       ├── sample_bitflyer.csv
│       └── sample_coincheck.csv
├── data/
│   ├── uploads/
│   └── reports/
├── docs/
│   └── cursor_handoff.md    # このファイル
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 💾 データモデル

### Transaction（標準フォーマット）
```python
{
    'timestamp': datetime,    # 取引日時
    'exchange': str,          # 'bitflyer', 'coincheck', 'gmo', 'bitbank', 'sbivc', 'rakuten', 'linebitmax'
    'symbol': str,            # 'BTC/JPY', 'ETH/JPY'
    'type': str,              # 'buy' or 'sell'
    'amount': float,          # 取引数量
    'price': float,           # 取引価格（円）
    'fee': float,             # 手数料（円）
}
```

---

## 🧮 計算ロジック

### 移動平均法
```
購入時:
新しい平均取得原価 = (既存保有額 + 購入額) / (既存数量 + 購入数量)

売却時:
売却損益 = (売却価格 - 平均取得原価) × 売却数量
```

### 総平均法
```
年間平均取得原価 = 年間総購入額 / 年間総購入数量
年間売却損益 = Σ[(売却価格 - 年間平均取得原価) × 売却数量]
```

---

## 📌 Cursorで実施済みの作業（別AIへの引き継ぎ用）

以下の作業は Cursor 上で完了済みです。続きの開発時に参照してください。

### 環境構築（完了済み）
- 既存の仮想環境（.venv）を削除し、**Python 3.12.10** で **venv** を新規作成
- プロジェクト構造を以下のように作成:
  - `src/parsers`, `src/calculators`, `src/models`, `src/utils`
  - `tests/fixtures`, `data/uploads`, `data/reports`, `docs`
  - `src/__init__.py`, `src/main.py`, `requirements.txt`, `README.md`, `.gitignore`
- **requirements.txt** に streamlit, pandas, numpy, sqlalchemy, pytest, python-docx, openpyxl を記載し、`pip install -r requirements.txt` を実行済み
- **Streamlit 起動確認**: `streamlit run src/main.py` で http://localhost:8501 に「💰 Zeitan」「暗号通貨の税金、簡単に。」を表示することを確認済み

### パーサー基盤（完了済み）
- **src/parsers/base.py** を実装済み
  - **TransactionFormat**: TypedDict で標準取引フォーマット（timestamp, exchange, symbol, type, amount, price, fee）を定義
  - **BaseParser**: ABC の抽象基底クラス
    - 抽象プロパティ `exchange_name` → 取引所識別子を返す
    - 抽象メソッド `parse(file_path: str | Path) -> list[TransactionFormat]` → CSV をパースして標準フォーマットのリストを返す
    - 抽象メソッド `validate(file_path: str | Path) -> bool` → CSV が当該取引所形式か検証する
  - Google style docstring、Python 3.12 の型ヒント（str | Path, list[TransactionFormat]）を使用
- **src/parsers/__init__.py**: `BaseParser` と `TransactionFormat` をエクスポート（相対インポート使用）

### パーサー開発（完了済み - 2026年2月15日）
- **7取引所のパーサー実装完了**:
  - bitFlyer, Coincheck, GMOコイン, bitbank（従来の4取引所）
  - SBI VCトレード, 楽天ウォレット, LINE BITMAX（新規追加）
- **全38テスト通過**（tests/test_parsers.py）
- 各取引所のサンプルCSVファイル作成済み（tests/fixtures/）

### 未着手・変更なし
- **src/main.py** は変更していない。画面上はタイトルとキャプションのみで、CSV アップロードや計算機能は未実装
- 計算エンジン（moving_average.py, total_average.py）は未実装

### 次の担当者がやること（推奨）
1. **src/calculators/moving_average.py** の実装（移動平均法の計算ロジック）
2. **src/calculators/total_average.py** の実装（総平均法の計算ロジック）
3. **tests/test_calculators.py** でユニットテスト作成

### Git の状態（別AIでのプッシュ用）
- **リポジトリ**: 初期化済み、ブランチ `main`
- **初回コミット済み**: 「Initial commit: Zeitan Phase 1 base」（parsers/base.py、Streamlit shell、handoff 等を含む）
- **リモート**: 未設定（プッシュするには以下を実行する必要あり）

**リモートにプッシュする手順（GitHub の例）**
1. GitHub で新規リポジトリ作成（例: `zeitan-dev`）。README や .gitignore は追加しない。
2. ローカルでリモートを追加してプッシュ:
   ```bash
   cd /Users/yutookiguchi/Work/zeitan-dev
   git remote add origin https://github.com/<ユーザー名>/zeitan-dev.git
   git push -u origin main
   ```
   SSH の場合は `git@github.com:<ユーザー名>/zeitan-dev.git` を指定。

---

## 🎯 Phase 1 タスクリスト

### Week 1-2: CSVパーサー開発
```
✅ src/parsers/base.py: 抽象基底クラス作成（完了）
✅ src/parsers/bitflyer.py: bitFlyerパーサー（完了）
✅ src/parsers/coincheck.py: Coincheckパーサー（完了）
✅ src/parsers/gmo.py: GMOコインパーサー（完了）
✅ src/parsers/bitbank.py: bitbankパーサー（完了）
✅ src/parsers/sbivc.py: SBI VCトレードパーサー（完了）
✅ src/parsers/rakuten.py: 楽天ウォレットパーサー（完了）
✅ src/parsers/linebitmax.py: LINE BITMAXパーサー（完了）
✅ tests/test_parsers.py: 全パーサーのユニットテスト（完了・38テスト通過）
```

### Week 3-4: 計算エンジン
```
□ src/calculators/moving_average.py: 移動平均法
□ src/calculators/total_average.py: 総平均法
□ tests/test_calculators.py: 計算テスト
□ エッジケース対応（ハードフォーク、エアドロップ等）
```

### Week 5-6: UI + レポート
```
□ src/main.py: Streamlitアプリ完成
  - CSVアップロード画面
  - 計算方法選択（移動平均法/総平均法）
  - 計算結果表示
  - レポートダウンロード
□ 確定申告用CSV出力
□ PDFレポート生成
```

---

## 📝 取引所CSVフォーマット（参考）

### bitFlyer
```csv
日時,種別,通貨,数量,価格,手数料,注文ID,決済区分,受渡区分
2024/01/15 10:30:00,買,BTC,0.01,5000000,50,xxx,,,
2024/01/20 15:45:00,売,BTC,0.01,5100000,51,xxx,,,
```

### Coincheck
```csv
日時,操作,レート(円),BTC(量),残高(BTC),円(量),残高(円),手数料(BTC),手数料(円)
2024-01-15 10:30:00,buy,5000000,0.01,0.01,50000,950000,0,0
```

### GMOコイン
```csv
取引日時,銘柄,取引区分,取引数量,取引レート,手数料,決済損益
2024/01/15 10:30:00,BTC,現物買い,0.01,5000000,50,
```

---

## 🚨 重要な開発原則

```
1. 計算精度が最優先
   → UIより先に計算エンジンをテスト徹底

2. MVPファースト
   → 最初は「CSV取込→計算→CSV出力」のみ

3. テストデータを先に作る
   → 各取引所のサンプルCSVと期待結果をセット

4. Phase 1ではやらないこと:
   ❌ ユーザー認証
   ❌ 本番デプロイ
   ❌ 決済機能
   ❌ DeFi/NFT対応
   ❌ 新税制対応（Phase 3）
   ❌ API連携（Phase 2）
```

---

## 🎯 競合情報（参考）

```
Cryptact: ¥8,800〜/年、新税制未対応
Gtax: ¥8,250〜/年、機能不足
Koinly: $99〜/年、日本税制非対応

Zeitanの強み:
✅ 2028年新税制完全対応（唯一）
✅ 低価格（¥4,980〜）
✅ 完全日本語
✅ DeFi/NFT対応
✅ 損失繰越管理
```

---

## 💰 収益予測

```
2027年（旧税制リリース）: 月$20,000〜$40,000
2028年（新税制元年）: 月$50,000〜$100,000
```

---

## 🚀 今すぐ始めること

### 最初の依頼（これをCursorに入力）

```
Zeitanの開発を始めます。
このファイル（docs/cursor_handoff.md）を読んで、
Phase 1の最初のタスクを実行してください。

まず src/parsers/base.py を実装してください。

要件:
- ABCモジュールを使った抽象基底クラス
- parse()メソッド（抽象メソッド）
- 戻り値: List[dict]（Transactionフォーマット）
- validate()メソッド（CSVの形式チェック）
- Google style docstring
- Python 3.12の型ヒント使用
```

---

## 📚 参考資料

```
国税庁: 暗号資産に関する税務上の取扱い
Streamlit公式: https://docs.streamlit.io/
pandas公式: https://pandas.pydata.org/docs/
```

---

最終更新: 2026年2月15日  
作成: claude.ai との対話から引き継ぎ  
追記: Cursor で実施した作業を別AIへの引き継ぎ用に記録（parsers/base.py 完了、環境構築・Streamlit 起動確認済み）
