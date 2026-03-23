"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";
import { getPortfolio } from "@/lib/api";
import type { PortfolioData } from "@/lib/types";
import { formatJPY } from "@/lib/format";

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#06b6d4", "#84cc16"];

function baseCurrency(symbol: string) {
  return symbol.includes("/") ? symbol.split("/")[0] : symbol;
}

export function PortfolioClient() {
  const [data, setData] = useState<PortfolioData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getPortfolio()
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "取得エラー"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="text-slate-500 py-12 text-center">読み込み中...</p>;

  if (error || !data || data.holdings.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-slate-500 mb-2">ポートフォリオデータがありません</p>
        <p className="text-sm text-slate-400 mb-4">CSVをアップロードして計算を実行してください</p>
        <Link
          href="/calculate"
          className="inline-block text-sm font-medium text-blue-600 hover:text-blue-800 border border-blue-300 rounded-lg px-4 py-2 hover:bg-blue-50 transition-colors"
        >
          計算ページへ →
        </Link>
      </div>
    );
  }

  const isProfit = data.unrealized_pnl >= 0;
  const pieData = data.holdings.map((h) => ({
    name: baseCurrency(h.symbol),
    value: h.current_value,
  }));

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl sm:text-2xl font-bold text-slate-800">ポートフォリオ</h1>
        <p className="text-sm text-slate-500 mt-0.5">保有資産の概要</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="rounded-xl border bg-white p-4 sm:p-5 shadow-sm">
          <p className="text-xs text-slate-500 mb-1">評価額合計</p>
          <p className="text-xl sm:text-2xl font-bold text-slate-800">
            {formatJPY(data.total_value)}
          </p>
        </div>
        <div className="rounded-xl border bg-white p-4 sm:p-5 shadow-sm">
          <p className="text-xs text-slate-500 mb-1">取得原価合計</p>
          <p className="text-xl sm:text-2xl font-bold text-slate-800">
            {formatJPY(data.total_cost)}
          </p>
        </div>
        <div className="rounded-xl border bg-white p-4 sm:p-5 shadow-sm">
          <p className="text-xs text-slate-500 mb-1">含み損益</p>
          <p className={`text-xl sm:text-2xl font-bold ${isProfit ? "text-emerald-600" : "text-red-500"}`}>
            {isProfit ? "+" : ""}{formatJPY(data.unrealized_pnl)}
          </p>
          <p className="text-xs text-slate-400 mt-0.5">
            {isProfit ? "含み益" : "含み損"}
          </p>
        </div>
      </div>

      {/* Pie Chart + Holdings Table */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart */}
        <div className="rounded-xl border bg-white p-4 sm:p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">通貨別構成比</h2>
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                dataKey="value"
                paddingAngle={2}
              >
                {pieData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value: number) => [formatJPY(value), "評価額"]}
                contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
              />
              <Legend
                formatter={(value: string) => (
                  <span className="text-xs text-slate-600">{value}</span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Holdings Table */}
        <div className="rounded-xl border bg-white p-4 sm:p-5 shadow-sm">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">保有通貨一覧</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-xs text-slate-500">
                  <th className="text-left py-2 font-medium">通貨</th>
                  <th className="text-right py-2 font-medium">数量</th>
                  <th className="text-right py-2 font-medium">評価額</th>
                  <th className="text-right py-2 font-medium">損益</th>
                  <th className="text-right py-2 font-medium">割合</th>
                </tr>
              </thead>
              <tbody>
                {data.holdings.map((h, i) => (
                  <tr key={h.symbol} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                    <td className="py-2.5 font-medium text-slate-800">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full flex-shrink-0"
                          style={{ backgroundColor: COLORS[i % COLORS.length] }}
                        />
                        {baseCurrency(h.symbol)}
                      </div>
                    </td>
                    <td className="py-2.5 text-right text-slate-600 tabular-nums">
                      {h.amount.toLocaleString("ja-JP", { maximumFractionDigits: 6 })}
                    </td>
                    <td className="py-2.5 text-right font-medium text-slate-800 tabular-nums">
                      {formatJPY(h.current_value)}
                    </td>
                    <td className={`py-2.5 text-right font-medium tabular-nums ${
                      h.unrealized_pnl >= 0 ? "text-emerald-600" : "text-red-500"
                    }`}>
                      {h.unrealized_pnl >= 0 ? "+" : ""}{formatJPY(h.unrealized_pnl)}
                    </td>
                    <td className="py-2.5 text-right text-slate-500 tabular-nums">
                      {h.allocation_pct}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Note */}
      <div className="rounded-lg bg-slate-50 border px-4 py-3 text-xs text-slate-500">
        ※ 評価額は最終取引時の価格で算出しています。リアルタイム市場価格とは異なる場合があります。
      </div>
    </div>
  );
}
