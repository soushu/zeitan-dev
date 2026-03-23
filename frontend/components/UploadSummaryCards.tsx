"use client";

import { getExchangeById } from "@/lib/exchange-config";

interface UploadedFile {
  fileName: string;
  exchange: string;
  transactionCount: number;
  error?: string;
}

interface UploadSummaryCardsProps {
  files: UploadedFile[];
  onRemove: (index: number) => void;
}

export function UploadSummaryCards({ files, onRemove }: UploadSummaryCardsProps) {
  if (files.length === 0) return null;

  const totalCount = files
    .filter((f) => !f.error)
    .reduce((sum, f) => sum + f.transactionCount, 0);

  return (
    <div className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {files.map((file, i) => {
          const config = getExchangeById(file.exchange);
          const color = config?.color ?? "#64748b";

          return (
            <div
              key={i}
              className="flex items-center gap-3 rounded-xl border bg-white p-3 shadow-sm"
              style={{ borderLeftWidth: 4, borderLeftColor: color }}
            >
              <div
                className="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-lg text-white text-xs font-bold"
                style={{ backgroundColor: color }}
              >
                {(config?.name ?? file.exchange).slice(0, 2).toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-900 truncate">
                  {file.fileName}
                </p>
                {file.error ? (
                  <p className="text-xs text-red-500">{file.error}</p>
                ) : (
                  <p className="text-xs text-slate-500">
                    {config?.name ?? file.exchange} - {file.transactionCount}件
                  </p>
                )}
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onRemove(i);
                }}
                className="text-xs text-slate-400 hover:text-red-500 flex-shrink-0"
              >
                削除
              </button>
            </div>
          );
        })}
      </div>

      <p className="text-sm text-slate-600">
        合計 <strong>{totalCount.toLocaleString()} 件</strong>の取引を読み込みました
      </p>
    </div>
  );
}
