"use client";

import { useRef, useState } from "react";
import { parseCSV } from "@/lib/api";
import type { TransactionResponse } from "@/lib/types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface ParsedFile {
  file: File;
  transactions: TransactionResponse[];
  exchange: string;
  error?: string;
}

interface FileUploaderProps {
  onTransactions: (transactions: TransactionResponse[]) => void;
}

export function FileUploader({ onTransactions }: FileUploaderProps) {
  const [parsedFiles, setParsedFiles] = useState<ParsedFile[]>([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function processFiles(files: File[]) {
    setIsLoading(true);
    const results: ParsedFile[] = [];

    for (const file of files) {
      try {
        const transactions = await parseCSV(file);
        const exchange =
          transactions.length > 0 ? transactions[0].exchange : "不明";
        results.push({ file, transactions, exchange });
      } catch (err) {
        results.push({
          file,
          transactions: [],
          exchange: "エラー",
          error: err instanceof Error ? err.message : "パースエラー",
        });
      }
    }

    const updated = [...parsedFiles, ...results];
    setParsedFiles(updated);

    const allTransactions = updated.flatMap((pf) => pf.transactions);
    onTransactions(allTransactions);
    setIsLoading(false);
  }

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files).filter((f) =>
      f.name.endsWith(".csv")
    );
    if (files.length > 0) processFiles(files);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    if (files.length > 0) processFiles(files);
    e.target.value = "";
  }

  function removeFile(index: number) {
    const updated = parsedFiles.filter((_, i) => i !== index);
    setParsedFiles(updated);
    onTransactions(updated.flatMap((pf) => pf.transactions));
  }

  return (
    <div className="space-y-4">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-10 cursor-pointer transition-colors
          ${isDragging ? "border-primary bg-primary/5" : "border-muted-foreground/30 hover:border-primary/50 hover:bg-muted/30"}`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          multiple
          className="hidden"
          onChange={handleChange}
        />
        <p className="text-sm text-muted-foreground">
          CSVファイルをドラッグ&ドロップ、またはクリックして選択
        </p>
        <p className="mt-1 text-xs text-muted-foreground/60">
          複数ファイル対応（BitFlyer, Coincheck, Binance 等）
        </p>
        {isLoading && (
          <p className="mt-2 text-sm text-primary">解析中...</p>
        )}
      </div>

      {parsedFiles.length > 0 && (
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ファイル名</TableHead>
              <TableHead>取引所</TableHead>
              <TableHead className="text-right">件数</TableHead>
              <TableHead />
            </TableRow>
          </TableHeader>
          <TableBody>
            {parsedFiles.map((pf, i) => (
              <TableRow key={i}>
                <TableCell className="font-medium">{pf.file.name}</TableCell>
                <TableCell>
                  {pf.error ? (
                    <Badge variant="destructive">エラー</Badge>
                  ) : (
                    <Badge>{pf.exchange}</Badge>
                  )}
                  {pf.error && (
                    <span className="ml-2 text-xs text-destructive">
                      {pf.error}
                    </span>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  {pf.transactions.length.toLocaleString()}
                </TableCell>
                <TableCell>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(i);
                    }}
                  >
                    削除
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      )}
    </div>
  );
}
