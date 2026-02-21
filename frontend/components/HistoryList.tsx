"use client";

import { useEffect, useState } from "react";
import { downloadCSV, downloadPDF, getHistory, getSessionDetail, triggerDownload } from "@/lib/api";
import type { CalcMethod, SessionDetail, SessionSummary } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TransactionTable } from "@/components/TransactionTable";

function formatJPY(n: number): string {
  return n.toLocaleString("ja-JP", {
    style: "currency",
    currency: "JPY",
    maximumFractionDigits: 0,
  });
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("ja-JP");
}

function methodLabel(method: string): string {
  return method === "moving_average" ? "移動平均法" : "総平均法";
}

export function HistoryList() {
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [detail, setDetail] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [downloadingCsv, setDownloadingCsv] = useState(false);
  const [downloadingPdf, setDownloadingPdf] = useState(false);

  useEffect(() => {
    getHistory()
      .then(setSessions)
      .catch((e) =>
        setError(e instanceof Error ? e.message : "履歴の取得に失敗しました")
      )
      .finally(() => setLoading(false));
  }, []);

  async function handleDownloadCSV(d: SessionDetail) {
    setDownloadingCsv(true);
    try {
      const blob = await downloadCSV({ transactions: d.transactions, method: d.calc_method as CalcMethod });
      triggerDownload(blob, `zeitan_session_${d.id}.csv`);
    } catch (e) {
      alert(e instanceof Error ? e.message : "CSVダウンロードに失敗しました");
    } finally {
      setDownloadingCsv(false);
    }
  }

  async function handleDownloadPDF(d: SessionDetail) {
    setDownloadingPdf(true);
    try {
      const blob = await downloadPDF({ transactions: d.transactions, method: d.calc_method as CalcMethod });
      triggerDownload(blob, `zeitan_session_${d.id}.pdf`);
    } catch (e) {
      alert(e instanceof Error ? e.message : "PDFダウンロードに失敗しました");
    } finally {
      setDownloadingPdf(false);
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
    try {
      const d = await getSessionDetail(id);
      setDetail(d);
    } catch (e) {
      alert(e instanceof Error ? e.message : "詳細の取得に失敗しました");
    } finally {
      setDetailLoading(false);
    }
  }

  if (loading) return <p className="text-muted-foreground">読み込み中...</p>;
  if (error) return <p className="text-destructive">{error}</p>;
  if (sessions.length === 0)
    return (
      <p className="text-muted-foreground">計算履歴がありません。</p>
    );

  return (
    <div className="space-y-4">
      {sessions.map((s) => (
        <Card key={s.id}>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <CardTitle className="text-base">
                  セッション #{s.id}
                </CardTitle>
                <div className="flex gap-2 text-sm text-muted-foreground">
                  <span>{formatDate(s.created_at)}</span>
                  <Badge variant="secondary">{methodLabel(s.calc_method)}</Badge>
                </div>
              </div>
              <div className="text-right">
                <p
                  className={`text-lg font-bold ${
                    s.total_profit_loss >= 0
                      ? "text-green-600"
                      : "text-red-600"
                  }`}
                >
                  {formatJPY(s.total_profit_loss)}
                </p>
                <p className="text-xs text-muted-foreground">
                  {s.transaction_count} 件
                </p>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <Button
              variant="outline"
              size="sm"
              onClick={() => toggleDetail(s.id)}
            >
              {expandedId === s.id ? "閉じる" : "詳細を見る"}
            </Button>

            {expandedId === s.id && (
              <div className="mt-4 space-y-4">
                {detailLoading ? (
                  <p className="text-sm text-muted-foreground">読み込み中...</p>
                ) : detail ? (
                  <>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownloadCSV(detail)}
                        disabled={downloadingCsv}
                      >
                        {downloadingCsv ? "ダウンロード中..." : "CSV ダウンロード"}
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownloadPDF(detail)}
                        disabled={downloadingPdf}
                      >
                        {downloadingPdf ? "ダウンロード中..." : "PDF ダウンロード"}
                      </Button>
                    </div>
                    <TransactionTable results={detail.results} />
                  </>
                ) : null}
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
