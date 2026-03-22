"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { downloadCSV, downloadPDF, getAvailableYears, getHistory, getSessionDetail, recalculate, triggerDownload } from "@/lib/api";
import type { CalcMethod, SessionDetail, SessionSummary } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { TransactionTable } from "@/components/TransactionTable";
import { BreakdownTables } from "@/components/BreakdownTables";
import { formatJPY, formatDate, methodLabel } from "@/lib/format";

function reportTitle(s: SessionSummary): string {
  if (s.tax_year) return `${s.tax_year}年度 損益計算レポート`;
  return `損益計算レポート（${formatDate(s.created_at)}）`;
}

export function HistoryList() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadingCsv, setDownloadingCsv] = useState<number | null>(null);
  const [downloadingPdf, setDownloadingPdf] = useState<number | null>(null);
  const [recalculating, setRecalculating] = useState<number | null>(null);
  const [downloadError, setDownloadError] = useState<string | null>(null);
  const [availableYears, setAvailableYears] = useState<number[]>([]);
  const [selectedYear, setSelectedYear] = useState<number | undefined>(undefined);

  useEffect(() => {
    getAvailableYears().then(setAvailableYears).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    setExpandedId(null);
    setDetail(null);
    getHistory(selectedYear)
      .then(setSessions)
      .catch((e) =>
        setError(e instanceof Error ? e.message : "履歴の取得に失敗しました")
      )
      .finally(() => setLoading(false));
  }, [selectedYear]);

  async function handleDownloadCSV(s: SessionSummary) {
    setDownloadingCsv(s.id);
    setDownloadError(null);
    try {
      const d = detail?.id === s.id ? detail : await getSessionDetail(s.id);
      const blob = await downloadCSV({ transactions: d.transactions, method: d.calc_method as CalcMethod });
      const year = s.tax_year ?? new Date(s.created_at).getFullYear();
      triggerDownload(blob, `zeitan_${year}年度_損益計算.csv`);
    } catch (e) {
      setDownloadError(e instanceof Error ? e.message : "CSVダウンロードに失敗しました");
    } finally {
      setDownloadingCsv(null);
    }
  }

  async function handleDownloadPDF(s: SessionSummary) {
    setDownloadingPdf(s.id);
    setDownloadError(null);
    try {
      const d = detail?.id === s.id ? detail : await getSessionDetail(s.id);
      const blob = await downloadPDF({ transactions: d.transactions, method: d.calc_method as CalcMethod });
      const year = s.tax_year ?? new Date(s.created_at).getFullYear();
      triggerDownload(blob, `zeitan_${year}年度_損益計算.pdf`);
    } catch (e) {
      setDownloadError(e instanceof Error ? e.message : "PDFダウンロードに失敗しました");
    } finally {
      setDownloadingPdf(null);
    }
  }

  async function handleRecalculate(s: SessionSummary) {
    const alternateMethod: CalcMethod =
      s.calc_method === "moving_average" ? "total_average" : "moving_average";
    setRecalculating(s.id);
    setDownloadError(null);
    try {
      const result = await recalculate(s.id, { method: alternateMethod });
      // 新しいセッションを一覧の先頭に追加
      const newSession: SessionSummary = {
        id: result.session_id,
        created_at: new Date().toISOString(),
        calc_method: result.method,
        total_profit_loss: result.total_profit_loss,
        transaction_count: s.transaction_count,
        note: null,
        tax_year: s.tax_year,
      };
      setSessions((prev) => [newSession, ...prev]);
    } catch (e) {
      setDownloadError(
        e instanceof Error ? e.message : "再計算に失敗しました"
      );
    } finally {
      setRecalculating(null);
    }
  }

  async function toggleDetail(id: number) {
    if (expandedId === id) {
      setExpandedId(null);
      setDetail(null);
      return;
    }
    setExpandedId(id);
    setDetailLoading(true);
    setDownloadError(null);
    try {
      const d = await getSessionDetail(id);
      setDetail(d);
    } catch (e) {
      setDownloadError(e instanceof Error ? e.message : "詳細の取得に失敗しました");
    } finally {
      setDetailLoading(false);
    }
  }

  if (loading) return <p className="text-muted-foreground py-8 text-center">読み込み中...</p>;
  if (error) return <p className="text-destructive py-8 text-center">{error}</p>;
  if (sessions.length === 0)
    return (
      <div className="text-center py-16 text-muted-foreground">
        <p className="text-4xl mb-3">📂</p>
        <p className="font-medium">計算履歴がまだありません</p>
        <p className="text-sm mt-1 mb-4">CSVをアップロードして損益計算を実行してください</p>
        <Link
          href="/"
          className="inline-block text-sm font-medium text-blue-600 hover:text-blue-800 border border-blue-300 rounded-lg px-4 py-2 hover:bg-blue-50 transition-colors"
        >
          計算ページへ →
        </Link>
      </div>
    );

  return (
    <div className="space-y-4">
      {/* 年度フィルター */}
      {availableYears.length > 0 && (
        <div className="flex items-center gap-3">
          <label htmlFor="year-filter" className="text-sm font-medium text-slate-700">
            年度で絞り込み
          </label>
          <select
            id="year-filter"
            value={selectedYear ?? ""}
            onChange={(e) =>
              setSelectedYear(e.target.value ? Number(e.target.value) : undefined)
            }
            className="rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm text-slate-700 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">すべての年度</option>
            {availableYears.map((y) => (
              <option key={y} value={y}>
                {y}年度
              </option>
            ))}
          </select>
        </div>
      )}

      {downloadError && (
        <div className="flex items-center justify-between rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
          <span>{downloadError}</span>
          <button onClick={() => setDownloadError(null)} aria-label="エラーメッセージを閉じる" className="ml-4 text-red-400 hover:text-red-600 font-medium">✕</button>
        </div>
      )}
      {sessions.map((s) => {
        const isExpanded = expandedId === s.id;
        const isProfit = s.total_profit_loss >= 0;

        return (
          <div
            key={s.id}
            className="border rounded-xl overflow-hidden bg-white shadow-sm hover:shadow-md transition-shadow"
          >
            {/* ── カードヘッダー（年度バー） ── */}
            <div className="bg-slate-800 px-5 py-3 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-white font-semibold text-sm">
                  {reportTitle(s)}
                </span>
                <Badge
                  variant="secondary"
                  className="bg-slate-600 text-slate-200 text-xs"
                >
                  {methodLabel(s.calc_method)}
                </Badge>
              </div>
              <span className="text-slate-400 text-xs">
                計算日: {formatDate(s.created_at)}
              </span>
            </div>

            {/* ── メトリクス行 ── */}
            <div className="px-5 py-4 grid grid-cols-3 gap-4 border-b">
              {/* 総損益 */}
              <div>
                <p className="text-xs text-muted-foreground mb-1">総損益</p>
                <p
                  className={`text-2xl font-bold tracking-tight ${
                    isProfit ? "text-emerald-600" : "text-red-500"
                  }`}
                >
                  {isProfit ? "+" : ""}
                  {formatJPY(s.total_profit_loss)}
                </p>
                <p className="text-xs mt-0.5 text-muted-foreground">
                  {isProfit ? "▲ 利益" : "▼ 損失"}
                </p>
              </div>

              {/* 取引件数 */}
              <div>
                <p className="text-xs text-muted-foreground mb-1">取引件数</p>
                <p className="text-2xl font-bold text-slate-800">
                  {s.transaction_count.toLocaleString()}
                  <span className="text-sm font-normal text-muted-foreground ml-1">件</span>
                </p>
              </div>

              {/* アクションボタン */}
              <div className="flex flex-col gap-2 justify-center">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-xs border-blue-300 text-blue-700 hover:bg-blue-50"
                  onClick={() => handleRecalculate(s)}
                  disabled={recalculating === s.id}
                >
                  {recalculating === s.id
                    ? "再計算中..."
                    : `${s.calc_method === "moving_average" ? "総平均法" : "移動平均法"}で再計算`}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-xs border-slate-300 hover:bg-slate-50"
                  onClick={() => handleDownloadCSV(s)}
                  disabled={downloadingCsv === s.id}
                >
                  {downloadingCsv === s.id ? "作成中..." : "CSV ダウンロード"}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-xs border-slate-300 hover:bg-slate-50"
                  onClick={() => handleDownloadPDF(s)}
                  disabled={downloadingPdf === s.id}
                >
                  {downloadingPdf === s.id ? "作成中..." : "PDF ダウンロード"}
                </Button>
              </div>
            </div>

            {/* ── フッター（詳細トグル） ── */}
            <div className="px-5 py-2.5 bg-slate-50 flex items-center justify-end">
              <button
                onClick={() => toggleDetail(s.id)}
                className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1 transition-colors"
              >
                {isExpanded ? "▲ 詳細を閉じる" : "▼ 取引詳細を見る"}
              </button>
            </div>

            {/* ── 詳細展開エリア ── */}
            {isExpanded && (
              <div className="px-5 py-4 border-t bg-white">
                {detailLoading ? (
                  <p className="text-sm text-muted-foreground text-center py-4">読み込み中...</p>
                ) : detail ? (
                  <div className="space-y-4">
                    <BreakdownTables results={detail.results} />
                    <TransactionTable results={detail.results} />
                  </div>
                ) : null}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
