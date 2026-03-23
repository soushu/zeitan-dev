"use client";

import { useRef, useState } from "react";
import type { ExchangeConfig } from "@/lib/exchange-config";
import { Button } from "@/components/ui/button";

interface ExchangeUploadDialogProps {
  exchange: ExchangeConfig;
  onBack: () => void;
  onFiles: (files: File[]) => void;
  isLoading: boolean;
}

export function ExchangeUploadDialog({
  exchange,
  onBack,
  onFiles,
  isLoading,
}: ExchangeUploadDialogProps) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  function handleDrop(e: React.DragEvent) {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files).filter((f) =>
      f.name.endsWith(".csv")
    );
    if (files.length > 0) onFiles(files);
  }

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(e.target.files ?? []);
    if (files.length > 0) onFiles(files);
    e.target.value = "";
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button
          onClick={onBack}
          className="text-sm text-slate-400 hover:text-slate-600"
        >
          &larr; 戻る
        </button>
        <div className="flex items-center gap-2">
          <div
            className="flex h-8 w-8 items-center justify-center rounded-lg text-white text-xs font-bold"
            style={{ backgroundColor: exchange.color }}
          >
            {exchange.name.slice(0, 2).toUpperCase()}
          </div>
          <span className="font-semibold text-slate-900">{exchange.name}</span>
        </div>
      </div>

      {/* Instructions */}
      <div className="rounded-lg bg-slate-50 border p-4">
        <p className="text-xs font-medium text-slate-500 mb-2">CSVダウンロード手順</p>
        <ol className="space-y-1.5">
          {exchange.instructions.map((step, i) => (
            <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
              <span className="flex-shrink-0 flex h-5 w-5 items-center justify-center rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
                {i + 1}
              </span>
              {step}
            </li>
          ))}
        </ol>
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`flex flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 cursor-pointer transition-colors ${
          isDragging
            ? "border-blue-400 bg-blue-50"
            : "border-slate-300 hover:border-blue-300 hover:bg-slate-50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".csv"
          multiple
          className="hidden"
          onChange={handleChange}
        />
        <p className="text-sm text-slate-600">
          CSVファイルをドラッグ&ドロップ、またはクリック
        </p>
        {isLoading && (
          <p className="mt-2 text-sm text-blue-600">解析中...</p>
        )}
      </div>
    </div>
  );
}
