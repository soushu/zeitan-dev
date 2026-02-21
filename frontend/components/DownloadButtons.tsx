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

  async function handleCSV() {
    setLoadingCsv(true);
    try {
      const blob = await downloadCSV(request);
      triggerDownload(blob, "zeitan_report.csv");
    } catch (err) {
      alert(err instanceof Error ? err.message : "CSVダウンロードに失敗しました");
    } finally {
      setLoadingCsv(false);
    }
  }

  async function handlePDF() {
    setLoadingPdf(true);
    try {
      const blob = await downloadPDF(request);
      triggerDownload(blob, "zeitan_report.pdf");
    } catch (err) {
      alert(err instanceof Error ? err.message : "PDFダウンロードに失敗しました");
    } finally {
      setLoadingPdf(false);
    }
  }

  return (
    <div className="flex gap-3">
      <Button variant="outline" onClick={handleCSV} disabled={loadingCsv}>
        {loadingCsv ? "ダウンロード中..." : "CSV ダウンロード"}
      </Button>
      <Button variant="outline" onClick={handlePDF} disabled={loadingPdf}>
        {loadingPdf ? "ダウンロード中..." : "PDF ダウンロード"}
      </Button>
    </div>
  );
}
