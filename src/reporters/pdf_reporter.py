"""PDF形式のレポート生成モジュール."""

from datetime import datetime
from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── カラーパレット ──────────────────────────────────────────
C_NAVY = colors.HexColor("#1A3A5C")       # ヘッダー背景
C_BLUE = colors.HexColor("#2D7DD2")       # サブヘッダー・アクセント
C_BLUE_LIGHT = colors.HexColor("#EBF4FF") # 薄い青（交互行）
C_GREEN = colors.HexColor("#27AE60")      # 利益
C_RED = colors.HexColor("#E74C3C")        # 損失
C_GRAY_BG = colors.HexColor("#F7F9FC")    # カード背景
C_GRAY_LINE = colors.HexColor("#CBD5E0")  # 罫線
C_TEXT = colors.HexColor("#1A202C")       # 本文テキスト
C_MUTED = colors.HexColor("#718096")      # サブテキスト
C_WHITE = colors.white


class PDFReporter:
    """PDF形式のレポート生成クラス."""

    def __init__(self) -> None:
        """PDFレポーターを初期化."""
        self._setup_fonts()

    def _setup_fonts(self) -> None:
        """日本語フォントを設定."""
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))
            self.font = "HeiseiKakuGo-W5"
            return
        except Exception:
            pass
        for path in [
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
        ]:
            try:
                pdfmetrics.registerFont(TTFont("Japanese", path))
                self.font = "Japanese"
                return
            except Exception:
                continue
        self.font = "Helvetica"

    # ── スタイル定義 ────────────────────────────────────────

    def _styles(self) -> dict:
        f = self.font
        return {
            "normal": ParagraphStyle("N", fontName=f, fontSize=9, textColor=C_TEXT, leading=14),
            "small": ParagraphStyle("S", fontName=f, fontSize=8, textColor=C_MUTED, leading=12),
            "section": ParagraphStyle(
                "SEC", fontName=f, fontSize=12, textColor=C_NAVY,
                spaceBefore=6, spaceAfter=6, leading=18,
            ),
            "kpi_label": ParagraphStyle("KL", fontName=f, fontSize=9, textColor=C_MUTED, alignment=1),
            "kpi_value": ParagraphStyle("KV", fontName=f, fontSize=15, textColor=C_TEXT, alignment=1, leading=20),
            "kpi_value_green": ParagraphStyle("KVG", fontName=f, fontSize=15, textColor=C_GREEN, alignment=1, leading=20),
            "kpi_value_red": ParagraphStyle("KVR", fontName=f, fontSize=15, textColor=C_RED, alignment=1, leading=20),
            "footer": ParagraphStyle("F", fontName=f, fontSize=7, textColor=C_MUTED, alignment=1),
            "note": ParagraphStyle("NOTE", fontName=f, fontSize=8, textColor=C_MUTED, leading=12),
        }

    # ── ヘッダーバナー ──────────────────────────────────────

    def _build_header(self, generated_at: str, calc_method: str) -> Table:
        f = self.font
        # タイトル行（ネイビー背景）
        title_data = [[
            Paragraph(
                '<font size="22" color="white"><b>Zeitan</b></font>'
                '<font size="14" color="#A0C4FF">　暗号資産税金計算レポート</font>',
                ParagraphStyle("H", fontName=f, leading=28),
            ),
            Paragraph(
                f'<font size="9" color="#A0C4FF">生成日時　</font>'
                f'<font size="9" color="white">{generated_at}</font>',
                ParagraphStyle("HR", fontName=f, alignment=2, leading=14),
            ),
        ]]
        title_table = Table(title_data, colWidths=[120 * mm, 60 * mm])
        title_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_NAVY),
            ("TOPPADDING", (0, 0), (-1, -1), 14),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ("LEFTPADDING", (0, 0), (0, -1), 14),
            ("RIGHTPADDING", (-1, 0), (-1, -1), 14),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        # メタ情報バー（薄い青）
        meta_data = [[
            Paragraph(f'<font color="#2D7DD2">計算方法　</font><b>{calc_method}</b>',
                      ParagraphStyle("M", fontName=f, fontSize=9, textColor=C_TEXT)),
            Paragraph(
                '<font color="#2D7DD2">免責　</font>'
                'このレポートは参考情報です。申告には税理士にご確認ください。',
                ParagraphStyle("MD", fontName=f, fontSize=8, textColor=C_MUTED, alignment=2),
            ),
        ]]
        meta_table = Table(meta_data, colWidths=[60 * mm, 120 * mm])
        meta_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_BLUE_LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (0, -1), 14),
            ("RIGHTPADDING", (-1, 0), (-1, -1), 14),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))

        return [title_table, meta_table]

    # ── KPI カード ──────────────────────────────────────────

    def _build_kpi_cards(self, results: list[dict], total_profit_loss: float) -> Table:
        st = self._styles()
        sell_count = sum(1 for r in results if r.get("type") == "sell")
        income_types = ("airdrop", "fork", "reward")
        income_total = sum(r.get("profit_loss", 0) for r in results if r.get("type") in income_types)

        pl_style = st["kpi_value_green"] if total_profit_loss >= 0 else st["kpi_value_red"]
        pl_sign = "+" if total_profit_loss > 0 else ""
        pl_label = "利益" if total_profit_loss > 0 else "損失" if total_profit_loss < 0 else ""

        def card(label: str, value_para: Paragraph, sub: str = "") -> list:
            return [
                Paragraph(label, st["kpi_label"]),
                value_para,
                Paragraph(sub, st["kpi_label"]),
            ]

        cards = [
            card(
                "総損益（円）",
                Paragraph(f"{pl_sign}¥{total_profit_loss:,.0f}", pl_style),
                pl_label,
            ),
            card(
                "総取引件数",
                Paragraph(f"{len(results)}", st["kpi_value"]),
                "件",
            ),
            card(
                "売却取引件数",
                Paragraph(f"{sell_count}", st["kpi_value"]),
                "件",
            ),
            card(
                "雑所得（報酬等）",
                Paragraph(f"¥{income_total:,.0f}" if income_total else "－", st["kpi_value"]),
                "エアドロップ・フォーク等",
            ),
        ]

        data = [cards]  # 1行4列
        t = Table(data, colWidths=[42.5 * mm] * 4, rowHeights=[22 * mm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), C_GRAY_BG),
            ("BOX", (0, 0), (0, -1), 0.5, C_GRAY_LINE),
            ("BOX", (1, 0), (1, -1), 0.5, C_GRAY_LINE),
            ("BOX", (2, 0), (2, -1), 0.5, C_GRAY_LINE),
            ("BOX", (3, 0), (3, -1), 0.5, C_GRAY_LINE),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LINEABOVE", (0, 0), (-1, 0), 3, C_BLUE),
        ]))
        return t

    # ── サマリーテーブル ────────────────────────────────────

    def _build_summary_table(self, results: list[dict], total_profit_loss: float, calc_method: str) -> Table:
        f = self.font
        sell_count = sum(1 for r in results if r.get("type") == "sell")
        buy_count = sum(1 for r in results if r.get("type") == "buy")
        income_types = ("airdrop", "fork", "reward")
        income_total = sum(r.get("profit_loss", 0) for r in results if r.get("type") in income_types)
        income_count = sum(1 for r in results if r.get("type") in income_types)

        pl_color = "#27AE60" if total_profit_loss >= 0 else "#E74C3C"

        rows = [
            ["項目", "内容"],
            ["計算方法", calc_method],
            ["総取引件数", f"{len(results)} 件（購入 {buy_count} 件 / 売却 {sell_count} 件）"],
            ["総損益（売買）",
             f'<font color="{pl_color}"><b>¥{total_profit_loss:,.0f}</b></font>'
             f'　{"（利益）" if total_profit_loss > 0 else "（損失）" if total_profit_loss < 0 else ""}'],
            ["雑所得（報酬等）",
             f"¥{income_total:,.0f}（{income_count} 件）" if income_count > 0 else "なし"],
        ]

        cell_style = ParagraphStyle("SC", fontName=f, fontSize=9, textColor=C_TEXT, leading=13)
        hdr_style = ParagraphStyle("SH", fontName=f, fontSize=9, textColor=C_WHITE, leading=13)

        table_data = []
        for i, row in enumerate(rows):
            if i == 0:
                table_data.append([Paragraph(c, hdr_style) for c in row])
            else:
                table_data.append([
                    Paragraph(row[0], cell_style),
                    Paragraph(row[1], cell_style),
                ])

        t = Table(table_data, colWidths=[55 * mm, 115 * mm])
        t.setStyle(TableStyle([
            # ヘッダー行
            ("BACKGROUND", (0, 0), (-1, 0), C_NAVY),
            ("TOPPADDING", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 9),
            # データ行
            ("BACKGROUND", (0, 1), (-1, -1), C_WHITE),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_GRAY_BG]),
            ("TOPPADDING", (0, 1), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, C_GRAY_LINE),
            # 左列（項目名）を薄く
            ("TEXTCOLOR", (0, 1), (0, -1), C_MUTED),
        ]))
        return t

    # ── 取引履歴テーブル ────────────────────────────────────

    def _build_history_table(self, results: list[dict]) -> Table:
        f = self.font
        type_map = {
            "buy": "購入", "sell": "売却",
            "airdrop": "エアドロップ", "fork": "フォーク",
            "reward": "報酬", "transfer_in": "受取", "transfer_out": "送金",
        }
        hdr_style = ParagraphStyle("TH", fontName=f, fontSize=8, textColor=C_WHITE, alignment=1, leading=11)
        cell_center = ParagraphStyle("TC", fontName=f, fontSize=8, textColor=C_TEXT, alignment=1, leading=11)
        cell_right = ParagraphStyle("TR", fontName=f, fontSize=8, textColor=C_TEXT, alignment=2, leading=11)
        cell_muted = ParagraphStyle("TM", fontName=f, fontSize=8, textColor=C_MUTED, alignment=1, leading=11)

        headers = ["日時", "取引所", "通貨ペア", "種別", "数量", "価格（円）", "損益（円）"]
        table_data = [[Paragraph(h, hdr_style) for h in headers]]

        for r in results[:100]:
            ts = r.get("timestamp", datetime.now())
            date_str = ts.strftime("%Y/%m/%d") if isinstance(ts, datetime) else str(ts)[:10]
            tx_type = type_map.get(r.get("type", ""), r.get("type", ""))
            pl = r.get("profit_loss", 0)

            if pl > 0:
                pl_str = f'<font color="#27AE60">+¥{pl:,.0f}</font>'
                pl_sty = ParagraphStyle("PG", fontName=f, fontSize=8, textColor=C_GREEN, alignment=2, leading=11)
            elif pl < 0:
                pl_str = f'<font color="#E74C3C">¥{pl:,.0f}</font>'
                pl_sty = ParagraphStyle("PR", fontName=f, fontSize=8, textColor=C_RED, alignment=2, leading=11)
            else:
                pl_str = "－"
                pl_sty = cell_muted

            table_data.append([
                Paragraph(date_str, cell_center),
                Paragraph(r.get("exchange", ""), cell_center),
                Paragraph(r.get("symbol", ""), cell_center),
                Paragraph(tx_type, cell_center),
                Paragraph(f"{r.get('amount', 0):.4f}", cell_right),
                Paragraph(f"¥{r.get('price', 0):,.0f}", cell_right),
                Paragraph(pl_str, pl_sty),
            ])

        col_widths = [22 * mm, 20 * mm, 20 * mm, 22 * mm, 18 * mm, 26 * mm, 26 * mm]
        t = Table(table_data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            # ヘッダー
            ("BACKGROUND", (0, 0), (-1, 0), C_BLUE),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            # データ行
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_WHITE, C_BLUE_LIGHT]),
            ("TOPPADDING", (0, 1), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            # 罫線（外枠のみ強め、内側は薄く）
            ("BOX", (0, 0), (-1, -1), 0.5, C_GRAY_LINE),
            ("INNERGRID", (0, 0), (-1, -1), 0.3, C_GRAY_LINE),
            ("LINEBELOW", (0, 0), (-1, 0), 0, C_BLUE),
        ]))
        return t

    # ── フッター描画コールバック ────────────────────────────

    def _make_footer_canvas(self, total_pages_ref: list):
        """ページフッター（ページ番号）を描画するキャンバスファクトリ."""
        from reportlab.pdfgen.canvas import Canvas

        font = self.font

        class FooterCanvas(Canvas):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._saved_page_states = []

            def showPage(self):
                self._saved_page_states.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                num_pages = len(self._saved_page_states)
                for state in self._saved_page_states:
                    self.__dict__.update(state)
                    self._draw_footer(num_pages)
                    super().showPage()
                super().save()

            def _draw_footer(self, total):
                page = self._pageNumber
                w, h = A4
                self.setFont(font, 7)
                self.setFillColor(C_MUTED)
                # 区切り線
                self.setStrokeColor(C_GRAY_LINE)
                self.setLineWidth(0.5)
                self.line(20 * mm, 14 * mm, w - 20 * mm, 14 * mm)
                # フッターテキスト
                self.drawString(20 * mm, 10 * mm, "Generated by Zeitan  |  参考情報のため、確定申告には税理士へご確認ください。")
                self.drawRightString(w - 20 * mm, 10 * mm, f"{page} / {total}")

        return FooterCanvas

    # ── メイン generate ─────────────────────────────────────

    def generate(
        self,
        results: list[dict],
        total_profit_loss: float,
        calc_method: str,
        output_path: str | Path | None = None,
    ) -> bytes:
        """PDF レポートを生成する."""
        buffer = BytesIO()
        generated_at = datetime.now().strftime("%Y年%m月%d日  %H:%M:%S")
        st = self._styles()

        story = []

        # ── ヘッダーバナー
        for elem in self._build_header(generated_at, calc_method):
            story.append(elem)
        story.append(Spacer(1, 6 * mm))

        # ── KPI カード
        story.append(self._build_kpi_cards(results, total_profit_loss))
        story.append(Spacer(1, 6 * mm))

        # ── サマリーセクション
        story.append(Paragraph("■ サマリー", st["section"]))
        story.append(self._build_summary_table(results, total_profit_loss, calc_method))
        story.append(Spacer(1, 8 * mm))

        # ── 取引履歴セクション
        if results:
            display_count = min(len(results), 100)
            story.append(Paragraph(f"■ 取引履歴（全 {len(results)} 件中 {display_count} 件を表示）", st["section"]))
            story.append(self._build_history_table(results))
            if len(results) > 100:
                story.append(Spacer(1, 3 * mm))
                story.append(Paragraph(
                    f"※ 件数が多いため最初の 100 件のみ表示しています。全データは CSV でご確認ください。",
                    st["note"],
                ))

        story.append(Spacer(1, 10 * mm))

        # ── PDF 構築
        total_ref: list = []
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=20 * mm,
            leftMargin=20 * mm,
            topMargin=18 * mm,
            bottomMargin=22 * mm,
        )
        doc.build(story, canvasmaker=self._make_footer_canvas(total_ref))

        pdf_bytes = buffer.getvalue()
        if output_path:
            Path(output_path).write_bytes(pdf_bytes)

        buffer.close()
        return pdf_bytes
