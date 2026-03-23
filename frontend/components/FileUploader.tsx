"use client";

import { useRef, useState } from "react";
import { parseCSV } from "@/lib/api";
import type { TransactionResponse } from "@/lib/types";
import type { ExchangeConfig } from "@/lib/exchange-config";
import { ExchangeGrid } from "@/components/ExchangeGrid";
import { ExchangeUploadDialog } from "@/components/ExchangeUploadDialog";
import { UploadSummaryCards } from "@/components/UploadSummaryCards";

interface ParsedFile {
  fileName: string;
  transactions: TransactionResponse[];
  exchange: string;
  error?: string;
}

interface FileUploaderProps {
  onTransactions: (transactions: TransactionResponse[]) => void;
}

type UploaderState = "grid" | "upload" | "done";

export function FileUploader({ onTransactions }: FileUploaderProps) {
  const [state, setState] = useState<UploaderState>("grid");
  const [selectedExchange, setSelectedExchange] = useState<ExchangeConfig | null>(null);
  const [parsedFiles, setParsedFiles] = useState<ParsedFile[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const plainInputRef = useRef<HTMLInputElement>(null);

  async function processFiles(files: File[]) {
    setIsLoading(true);
    const results: ParsedFile[] = [];

    for (const file of files) {
      try {
        const transactions = await parseCSV(file);
        const exchange =
          transactions.length > 0 ? transactions[0].exchange : "不明";
        results.push({ fileName: file.name, transactions, exchange });
      } catch (err) {
        results.push({
          fileName: file.name,
          transactions: [],
          exchange: selectedExchange?.id ?? "エラー",
          error: err instanceof Error ? err.message : "パースエラー",
        });
      }
    }

    const updated = [...parsedFiles, ...results];
    setParsedFiles(updated);
    setState("done");

    const allTransactions = updated
      .filter((pf) => !pf.error)
      .flatMap((pf) => pf.transactions);
    onTransactions(allTransactions);
    setIsLoading(false);
  }

  function handleSelectExchange(exchange: ExchangeConfig) {
    setSelectedExchange(exchange);
    setState("upload");
  }

  function handleSkip() {
    setSelectedExchange(null);
    setState("upload");
  }

  function handleBack() {
    if (parsedFiles.length > 0) {
      setState("done");
    } else {
      setState("grid");
      setSelectedExchange(null);
    }
  }

  function handleRemove(index: number) {
    const updated = parsedFiles.filter((_, i) => i !== index);
    setParsedFiles(updated);
    if (updated.length === 0) {
      setState("grid");
      setSelectedExchange(null);
      onTransactions([]);
    } else {
      onTransactions(updated.flatMap((pf) => pf.transactions));
    }
  }

  function handleAddMore() {
    setState("grid");
    setSelectedExchange(null);
  }

  function handlePlainDrop(e: React.DragEvent) {
    e.preventDefault();
    const files = Array.from(e.dataTransfer.files).filter((f) =>
      f.name.endsWith(".csv")
    );
    if (files.length > 0) processFiles(files);
  }

  function handlePlainChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    if (files.length > 0) processFiles(files);
    e.target.value = "";
  }

  return (
    <div className="space-y-4">
      {state === "grid" && (
        <ExchangeGrid onSelect={handleSelectExchange} onSkip={handleSkip} />
      )}

      {state === "upload" && selectedExchange && (
        <ExchangeUploadDialog
          exchange={selectedExchange}
          onBack={handleBack}
          onFiles={processFiles}
          isLoading={isLoading}
        />
      )}

      {state === "upload" && !selectedExchange && (
        <div className="space-y-3">
          <button
            onClick={handleBack}
            className="text-sm text-slate-400 hover:text-slate-600"
          >
            &larr; 取引所選択に戻る
          </button>
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handlePlainDrop}
            onClick={() => plainInputRef.current?.click()}
            className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 cursor-pointer border-slate-300 hover:border-blue-300 hover:bg-slate-50 transition-colors"
          >
            <input
              ref={plainInputRef}
              type="file"
              accept=".csv"
              multiple
              className="hidden"
              onChange={handlePlainChange}
            />
            <p className="text-sm text-slate-600">
              CSVファイルをドラッグ&ドロップ、またはクリック
            </p>
            <p className="mt-1 text-xs text-slate-400">
              取引所は自動検出されます
            </p>
            {isLoading && (
              <p className="mt-2 text-sm text-blue-600">解析中...</p>
            )}
          </div>
        </div>
      )}

      {state === "done" && (
        <>
          <UploadSummaryCards
            files={parsedFiles.map((pf) => ({
              fileName: pf.fileName,
              exchange: pf.exchange,
              transactionCount: pf.transactions.length,
              error: pf.error,
            }))}
            onRemove={handleRemove}
          />
          <button
            onClick={handleAddMore}
            className="text-sm text-blue-600 hover:text-blue-800 font-medium"
          >
            + 別の取引所のCSVを追加
          </button>
        </>
      )}
    </div>
  );
}
