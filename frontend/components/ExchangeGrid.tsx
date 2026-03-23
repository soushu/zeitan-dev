"use client";

import { useState } from "react";
import { EXCHANGES, type ExchangeConfig } from "@/lib/exchange-config";

interface ExchangeGridProps {
  onSelect: (exchange: ExchangeConfig) => void;
  onSkip: () => void;
}

export function ExchangeGrid({ onSelect, onSkip }: ExchangeGridProps) {
  const [filter, setFilter] = useState<"all" | "domestic" | "international">("all");

  const filtered = filter === "all"
    ? EXCHANGES
    : EXCHANGES.filter((e) => e.category === filter);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center rounded-full bg-blue-50 border border-blue-200 px-2.5 py-0.5 text-xs font-medium text-blue-700">
            {EXCHANGES.length}取引所対応
          </span>
        </div>
        <div className="flex gap-1 text-xs">
          {(["all", "domestic", "international"] as const).map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`rounded-md px-2.5 py-1 transition-colors ${
                filter === cat
                  ? "bg-slate-900 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {cat === "all" ? "すべて" : cat === "domestic" ? "国内" : "海外"}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
        {filtered.map((exchange) => (
          <button
            key={exchange.id}
            onClick={() => onSelect(exchange)}
            className="flex flex-col items-center gap-2 rounded-xl border bg-white p-4 shadow-sm hover:shadow-md hover:border-blue-300 transition-all text-center"
          >
            <div
              className="flex h-10 w-10 items-center justify-center rounded-lg text-white text-sm font-bold"
              style={{ backgroundColor: exchange.color }}
            >
              {exchange.name.slice(0, 2).toUpperCase()}
            </div>
            <div>
              <p className="text-sm font-medium text-slate-900">{exchange.name}</p>
              <p className="text-xs text-slate-400">
                {exchange.category === "domestic" ? "国内" : "海外"}
              </p>
            </div>
          </button>
        ))}
      </div>

      <div className="text-center pt-2">
        <button
          onClick={onSkip}
          className="text-xs text-slate-400 hover:text-slate-600 underline"
        >
          取引所を選択せずにアップロード
        </button>
      </div>
    </div>
  );
}
