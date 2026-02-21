"""Zeitan - 暗号通貨税金計算アプリ（Streamlit版）."""

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from src.calculators import MovingAverageCalculator, TotalAverageCalculator
from src.parsers import (
    AaveParser,
    BinanceParser,
    BitbankParser,
    BitflyerParser,
    BlurParser,
    BybitParser,
    CoinbaseParser,
    CoincheckParser,
    GMOParser,
    KrakenParser,
    LiquidityPoolParser,
    LineBitmaxParser,
    OpenSeaParser,
    RakutenParser,
    SBIVCParser,
    UniswapParser,
)
from src.parsers.base import BaseParser, TransactionFormat
from src.reporters import PDFReporter

# ページ設定
st.set_page_config(
    page_title="Zeitan - 暗号通貨税金計算",
    page_icon="💰",
    layout="wide",
)

# タイトル
st.title("💰 Zeitan")
st.caption("暗号通貨の税金、簡単に。")
st.divider()

# サイドバー
with st.sidebar:
    st.header("📊 対応取引所")
    st.markdown("**🇯🇵 国内取引所**")
    st.markdown(
        """
        - bitFlyer
        - Coincheck
        - GMOコイン
        - bitbank
        - SBI VCトレード
        - 楽天ウォレット
        - LINE BITMAX
        """
    )
    st.markdown("**🌏 海外取引所**")
    st.markdown(
        """
        - Binance
        - Bybit
        - Coinbase
        - Kraken
        """
    )
    st.markdown("**🔗 DeFi**")
    st.markdown(
        """
        - Uniswap
        - Aave
        - Liquidity Pool
        """
    )
    st.markdown("**🖼️ NFT**")
    st.markdown(
        """
        - OpenSea
        - Blur
        """
    )
    st.divider()
    st.header("⚙️ 計算方法")
    calc_method = st.radio(
        "計算方法を選択",
        options=["移動平均法", "総平均法"],
        help="移動平均法: 購入ごとに平均取得原価を更新\n総平均法: 年間の購入平均を使用",
    )

# パーサーのマッピング
PARSERS: dict[str, BaseParser] = {
    # 国内取引所
    "bitFlyer": BitflyerParser(),
    "Coincheck": CoincheckParser(),
    "GMOコイン": GMOParser(),
    "bitbank": BitbankParser(),
    "SBI VCトレード": SBIVCParser(),
    "楽天ウォレット": RakutenParser(),
    "LINE BITMAX": LineBitmaxParser(),
    # 海外取引所
    "Binance": BinanceParser(),
    "Bybit": BybitParser(),
    "Coinbase (US)": CoinbaseParser(),
    "Kraken": KrakenParser(),
    # DeFi
    "Uniswap": UniswapParser(),
    "Aave": AaveParser(),
    "Liquidity Pool": LiquidityPoolParser(),
    # NFT
    "OpenSea": OpenSeaParser(),
    "Blur": BlurParser(),
}


def detect_exchange(file_bytes: bytes, filename: str) -> str | None:
    """CSVファイルから取引所を自動検出する.

    Args:
        file_bytes: CSVファイルのバイト列。
        filename: ファイル名。

    Returns:
        取引所名（検出できない場合は None）。
    """
    # 一時ファイルとして保存
    temp_path = Path(f"/tmp/{filename}")
    temp_path.write_bytes(file_bytes)

    for exchange_name, parser in PARSERS.items():
        try:
            if parser.validate(temp_path):
                return exchange_name
        except Exception:
            continue

    return None


# メインコンテンツ
st.header("1️⃣ CSVファイルをアップロード")

uploaded_files = st.file_uploader(
    "取引所からダウンロードしたCSVファイルを選択してください",
    type=["csv", "xlsx"],
    accept_multiple_files=True,
    help="複数の取引所のファイルを同時にアップロードできます",
)

if uploaded_files:
    st.success(f"{len(uploaded_files)} 件のファイルがアップロードされました")

    # ファイルごとに取引所を検出
    all_transactions: list[TransactionFormat] = []
    file_info = []

    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        detected_exchange = detect_exchange(file_bytes, uploaded_file.name)

        if detected_exchange:
            file_info.append(
                {
                    "ファイル名": uploaded_file.name,
                    "取引所": detected_exchange,
                    "サイズ": f"{len(file_bytes) / 1024:.1f} KB",
                }
            )

            # パース
            temp_path = Path(f"/tmp/{uploaded_file.name}")
            temp_path.write_bytes(file_bytes)
            parser = PARSERS[detected_exchange]
            transactions = parser.parse(temp_path)
            all_transactions.extend(transactions)
        else:
            file_info.append(
                {
                    "ファイル名": uploaded_file.name,
                    "取引所": "⚠️ 検出失敗",
                    "サイズ": f"{len(file_bytes) / 1024:.1f} KB",
                }
            )

    # ファイル情報を表示
    st.subheader("📁 アップロードされたファイル")
    df_files = pd.DataFrame(file_info)
    st.dataframe(df_files, use_container_width=True, hide_index=True)

    if all_transactions:
        st.divider()
        st.header("2️⃣ 計算結果")

        # 計算実行
        if calc_method == "移動平均法":
            calculator = MovingAverageCalculator()
        else:
            calculator = TotalAverageCalculator()

        results = calculator.calculate(all_transactions)
        total_pl = calculator.get_total_profit_loss(results)

        # 結果をデータフレームに変換
        df_results = pd.DataFrame(results)
        df_results["取引日時"] = pd.to_datetime(df_results["timestamp"])
        df_results["損益（円）"] = df_results["profit_loss"].apply(
            lambda x: f"¥{x:,.0f}"
        )

        # 表示用カラムを選択
        display_cols = [
            "取引日時",
            "exchange",
            "symbol",
            "type",
            "amount",
            "price",
            "fee",
            "損益（円）",
        ]
        df_display = df_results[display_cols].copy()
        df_display.columns = [
            "取引日時",
            "取引所",
            "通貨ペア",
            "種別",
            "数量",
            "価格",
            "手数料",
            "損益",
        ]

        # 種別を日本語に変換
        type_mapping = {
            "buy": "購入",
            "sell": "売却",
            "airdrop": "エアドロップ",
            "fork": "フォーク",
            "reward": "報酬",
            "transfer_in": "受取",
            "transfer_out": "送金",
            "swap": "スワップ",
            "liquidity_add": "流動性追加",
            "liquidity_remove": "流動性削除",
            "lending": "レンディング",
            "nft_buy": "NFT購入",
            "nft_sell": "NFT売却",
        }
        df_display["種別"] = df_display["種別"].map(type_mapping)

        # 総損益を表示
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(
                label="総取引件数",
                value=f"{len(results)} 件",
            )
        with col2:
            st.metric(
                label=f"総損益（{calc_method}）",
                value=f"¥{total_pl:,.0f}",
                delta=None if total_pl == 0 else ("利益" if total_pl > 0 else "損失"),
            )
        with col3:
            sell_count = sum(1 for r in results if r["type"] == "sell")
            st.metric(
                label="売却取引件数",
                value=f"{sell_count} 件",
            )
        with col4:
            # エアドロップ・報酬・フォークの合計所得
            income_types = ("airdrop", "fork", "reward")
            income_total = sum(
                r["profit_loss"] for r in results if r["type"] in income_types
            )
            income_count = sum(1 for r in results if r["type"] in income_types)
            st.metric(
                label="雑所得（報酬等）",
                value=f"¥{income_total:,.0f}" if income_count > 0 else "¥0",
                help=f"エアドロップ・フォーク・報酬による所得 ({income_count}件)",
            )

        # 取引履歴を表示
        st.subheader("📋 取引履歴")
        st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            height=400,
        )

        # CSV出力
        st.divider()
        st.header("3️⃣ レポートダウンロード")

        # CSVダウンロード
        csv_buffer = io.StringIO()
        df_results.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
        csv_bytes = csv_buffer.getvalue().encode("utf-8-sig")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                label="📥 CSV形式でダウンロード",
                data=csv_bytes,
                file_name=f"zeitan_report_{calc_method}.csv",
                mime="text/csv",
                help="計算結果をCSV形式でダウンロードします",
            )

        with col2:
            # PDFダウンロード
            pdf_reporter = PDFReporter()
            pdf_bytes = pdf_reporter.generate(
                results=results,
                total_profit_loss=total_pl,
                calc_method=calc_method,
            )
            st.download_button(
                label="📄 PDF形式でダウンロード",
                data=pdf_bytes,
                file_name=f"zeitan_report_{calc_method}.pdf",
                mime="application/pdf",
                help="計算結果をPDF形式でダウンロードします（サマリー付き）",
            )

        # サマリー情報
        st.subheader("📊 サマリー")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**取引所別の取引件数**")
            exchange_counts = df_results["exchange"].value_counts()
            st.bar_chart(exchange_counts)

        with col2:
            st.markdown("**通貨ペア別の取引件数**")
            symbol_counts = df_results["symbol"].value_counts()
            st.bar_chart(symbol_counts)

    else:
        st.warning("⚠️ パース可能なファイルがありません。対応形式のCSVファイルをアップロードしてください。")
else:
    st.info("👆 まずは取引所からダウンロードしたCSVファイルをアップロードしてください")

# フッター
st.divider()
st.caption("Zeitan v1.0 | 対応: 移動平均法・総平均法 | 取引所: 11社 + DeFi 3 + NFT 2")
