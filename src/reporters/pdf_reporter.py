"""PDF形式のレポート生成モジュール."""

from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class PDFReporter:
    """PDF形式のレポート生成クラス.

    暗号資産税金計算の結果をPDF形式で出力します。
    """

    def __init__(self) -> None:
        """PDFレポーター を初期化."""
        self._setup_japanese_fonts()

    def _setup_japanese_fonts(self) -> None:
        """日本語フォントを設定（システムフォントを使用）."""
        # macOSの場合はヒラギノ、Linuxの場合はIPAフォントなどを使用
        # フォントが見つからない場合はデフォルトフォントにフォールバック
        try:
            # Try to register Hiragino (macOS)
            pdfmetrics.registerFont(
                TTFont("Japanese", "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc")
            )
            self.japanese_font = "Japanese"
        except Exception:
            try:
                # Try HeiseiKakuGo (common on many systems)
                pdfmetrics.registerFont(TTFont("Japanese", "HeiseiKakuGo-W5"))
                self.japanese_font = "Japanese"
            except Exception:
                # Fallback to Helvetica (no Japanese support)
                self.japanese_font = "Helvetica"

    def generate(
        self,
        results: list[dict],
        total_profit_loss: float,
        calc_method: str,
        output_path: str | Path | None = None,
    ) -> bytes:
        """PDF レポートを生成する.

        Args:
            results: 計算結果のリスト（TradeResult の辞書形式）。
            total_profit_loss: 総損益（円）。
            calc_method: 計算方法（"移動平均法" または "総平均法"）。
            output_path: 出力先パス（省略時はバイトデータのみ返す）。

        Returns:
            生成されたPDFのバイトデータ。
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=20 * mm,
            bottomMargin=20 * mm,
        )

        # ストーリー（PDF要素のリスト）
        story = []

        # スタイル設定
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "JapaneseTitle",
            parent=styles["Title"],
            fontName=self.japanese_font,
            fontSize=24,
            textColor=colors.HexColor("#1a1a1a"),
        )
        heading_style = ParagraphStyle(
            "JapaneseHeading",
            parent=styles["Heading1"],
            fontName=self.japanese_font,
            fontSize=16,
            textColor=colors.HexColor("#333333"),
            spaceAfter=12,
        )
        normal_style = ParagraphStyle(
            "JapaneseNormal",
            parent=styles["Normal"],
            fontName=self.japanese_font,
            fontSize=10,
        )

        # タイトル
        title = Paragraph("Zeitan 暗号資産税金計算レポート", title_style)
        story.append(title)
        story.append(Spacer(1, 12))

        # 生成日時
        generated_at = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        date_para = Paragraph(f"生成日時: {generated_at}", normal_style)
        story.append(date_para)
        story.append(Spacer(1, 12))

        # サマリーセクション
        summary_heading = Paragraph("📊 サマリー", heading_style)
        story.append(summary_heading)

        # サマリーテーブル
        summary_data = [
            ["項目", "値"],
            ["計算方法", calc_method],
            ["総取引件数", f"{len(results)} 件"],
            [
                "総損益",
                f"¥{total_profit_loss:,.0f} {'(利益)' if total_profit_loss > 0 else '(損失)' if total_profit_loss < 0 else ''}",
            ],
        ]

        # 売却件数
        sell_count = sum(1 for r in results if r.get("type") == "sell")
        summary_data.append(["売却取引件数", f"{sell_count} 件"])

        # 雑所得（エアドロップ等）
        income_types = ("airdrop", "fork", "reward")
        income_total = sum(
            r.get("profit_loss", 0) for r in results if r.get("type") in income_types
        )
        income_count = sum(1 for r in results if r.get("type") in income_types)
        if income_count > 0:
            summary_data.append(
                ["雑所得（報酬等）", f"¥{income_total:,.0f} ({income_count}件)"]
            )

        summary_table = Table(summary_data, colWidths=[80 * mm, 80 * mm])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4CAF50")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                    ("FONTNAME", (0, 0), (-1, -1), self.japanese_font),
                    ("FONTSIZE", (0, 0), (-1, 0), 12),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                    ("GRID", (0, 0), (-1, -1), 1, colors.black),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 20))

        # 取引履歴セクション
        if len(results) > 0:
            history_heading = Paragraph("📋 取引履歴（抜粋）", heading_style)
            story.append(history_heading)

            # 取引履歴テーブル（最初の50件）
            history_data = [["日時", "取引所", "通貨", "種別", "数量", "価格", "損益"]]

            type_mapping = {
                "buy": "購入",
                "sell": "売却",
                "airdrop": "エアドロップ",
                "fork": "フォーク",
                "reward": "報酬",
                "transfer_in": "受取",
                "transfer_out": "送金",
            }

            for r in results[:50]:  # 最初の50件のみ
                timestamp = r.get("timestamp", datetime.now())
                if isinstance(timestamp, datetime):
                    date_str = timestamp.strftime("%Y/%m/%d")
                else:
                    date_str = str(timestamp)

                tx_type = type_mapping.get(r.get("type", ""), r.get("type", ""))
                profit_loss = r.get("profit_loss", 0)
                pl_str = f"¥{profit_loss:,.0f}" if profit_loss != 0 else "-"

                history_data.append(
                    [
                        date_str,
                        r.get("exchange", ""),
                        r.get("symbol", ""),
                        tx_type,
                        f"{r.get('amount', 0):.4f}",
                        f"¥{r.get('price', 0):,.0f}",
                        pl_str,
                    ]
                )

            col_widths = [25 * mm, 20 * mm, 20 * mm, 20 * mm, 20 * mm, 25 * mm, 30 * mm]
            history_table = Table(history_data, colWidths=col_widths)
            history_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2196F3")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, -1), self.japanese_font),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                    ]
                )
            )
            story.append(history_table)

            if len(results) > 50:
                note = Paragraph(
                    f"※ 全{len(results)}件中、最初の50件を表示しています",
                    normal_style,
                )
                story.append(Spacer(1, 6))
                story.append(note)

        # フッター
        story.append(Spacer(1, 20))
        footer = Paragraph(
            "Generated by Zeitan v1.0 - https://github.com/soushu/zeitan-dev",
            normal_style,
        )
        story.append(footer)

        # PDF生成
        doc.build(story)

        # ファイル出力
        pdf_bytes = buffer.getvalue()
        if output_path:
            Path(output_path).write_bytes(pdf_bytes)

        buffer.close()
        return pdf_bytes
