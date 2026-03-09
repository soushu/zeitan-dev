"use client";

import { useState } from "react";
import { downloadCSV, downloadPDF, triggerDownload } from "@/lib/api";
import type { CalculateRequest } from "@/lib/types";
import { Button } from "@/components/ui/button";

interface DownloadButtonsProps {
  request: CalculateRequest;
}

export function DownloadButtons({ request }: DownloadButtonsProps) {
  const [loadingCsv, setLoadingCsv] = useState(false);
  const [loadingPdf, setLoadingPdf] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function todayStr() {
    return new Date().toISOString().slice(0, 10);
  }

  async function handleCSV() {
    setLoadingCsv(true);
    setError(null);
    try {
      const blob = await downloadCSV(request);
      triggerDownload(blob, `zeitan_${todayStr()}_損益計算.csv`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "CSVダウンロードに失敗しました");
    } finally {
      setLoadingCsv(false);
    }
  }

  async function handlePDF() {
    setLoadingPdf(true);
    setError(null);
    try {
      const blob = await downloadPDF(request);
      triggerDownload(blob, `zeitan_${todayStr()}_損益計算.pdf`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "PDFダウンロードに失敗しました");
    } finally {
      setLoadingPdf(false);
    }
  }

  return (
    <div className="space-y-2">
      <div className="flex gap-3">
        <Button variant="outline" onClick={handleCSV} disabled={loadingCsv}>
          {loadingCsv ? "ダウンロード中..." : "CSV ダウンロード"}
        </Button>
        <Button variant="outline" onClick={handlePDF} disabled={loadingPdf}>
          {loadingPdf ? "ダウンロード中..." : "PDF ダウンロード"}
        </Button>
      </div>
      {error && (
        <p className="text-sm text-destructive">{error}</p>
      )}
    </div>
  );
}
