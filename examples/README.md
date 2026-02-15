# Zeitan サンプルデータ

## 📁 sample_csv/

Streamlit UIでテスト用に使用できる、7取引所のサンプルCSVファイルです。

### 含まれるファイル

| ファイル | 取引所 | 取引件数 | 通貨ペア |
|---------|--------|---------|---------|
| test_bitflyer.csv | bitFlyer | 10件 | BTC/JPY, ETH/JPY |
| test_coincheck.csv | Coincheck | 10件 | BTC/JPY |
| test_gmo.csv | GMOコイン | 10件 | BTC/JPY, ETH/JPY |
| test_bitbank.csv | bitbank | 10件 | BTC/JPY, ETH/JPY |
| test_sbivc.csv | SBI VCトレード | 10件 | BTC/JPY, ETH/JPY |
| test_rakuten.csv | 楽天ウォレット | 10件 | BTC/JPY, ETH/JPY |
| test_linebitmax.csv | LINE BITMAX | 10件 | BTC/JPY, ETH/JPY |

### データ期間

- **期間**: 2024年1月〜4月
- **取引種別**: 買い（購入）と売り（売却）の両方
- **特徴**: 実際の取引を想定した現実的なデータ

### 使い方

1. Streamlitアプリを起動
   ```bash
   cd /Users/yutookiguchi/Work/zeitan-dev
   source venv/bin/activate
   export PYTHONPATH=$(pwd)
   streamlit run src/main.py
   ```

2. ブラウザで http://localhost:8501 にアクセス

3. サンプルCSVファイルをアップロード
   - 1つのファイルのみ、または
   - 複数のファイルを同時にアップロード可能

4. 計算方法を選択（移動平均法 or 総平均法）

5. 結果を確認してCSVレポートをダウンロード

### 期待される動作

- ✅ 各ファイルの取引所が自動検出される
- ✅ 買いと売りから損益が計算される
- ✅ 取引所別・通貨ペア別のサマリーが表示される
- ✅ CSV形式でレポートがダウンロードできる
