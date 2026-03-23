"use client";

import { useEffect, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import Link from "next/link";
import { getDashboard } from "@/lib/api";
import type { DashboardData, SessionSummary } from "@/lib/types";
import { formatJPY, methodLabel } from "@/lib/format";

// ── ユーティリティ ───────────────────────────────────────
function sessionLabel(s: SessionSummary) {
  const year = s.tax_year ?? new Date(s.created_at).getFullYear();
  return `${year}年度（${new Date(s.created_at).toLocaleDateString("ja-JP")} 計算）`;
}

// ── KPI カード ───────────────────────────────────────────
function KpiCard({ label, value, sub, accent }: {
  label: string; value: string; sub?: string; accent?: "green" | "red" | "blue";
}) {
  const colors = {
    green: "text-emerald-600",
    red: "text-red-500",
    blue: "text-blue-600",
  };
  return (
    <div className="rounded-xl border bg-white p-3 sm:p-5 shadow-sm">
      <p className="text-xs text-slate-500 mb-1">{label}</p>
      <p className={`text-lg sm:text-2xl font-bold tracking-tight ${accent ? colors[accent] : "text-slate-800"}`}>
        {value}
      </p>
      {sub && <p className="text-xs text-slate-400 mt-1">{sub}</p>}
    </div>
  );
}

// ── 申告ステータスバナー ──────────────────────────────────
function TaxNotice({ profit }: { profit: number }) {
  if (profit <= 0) {
    return (
      <div className="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3">
        <span className="mt-0.5 text-slate-400">ℹ</span>
        <div>
          <p className="text-sm font-medium text-slate-600">損失または損益なし</p>
          <p className="text-xs text-slate-400 mt-0.5">
            今年度の売買損益がゼロ以下のため、暗号資産による課税所得はありません。
          </p>
        </div>
      </div>
    );
  }
  if (profit <= 200000) {
    return (
      <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3">
        <span className="mt-0.5 text-amber-500">⚠</span>
        <div>
          <p className="text-sm font-medium text-amber-700">確定申告が不要な場合があります</p>
          <p className="text-xs text-amber-600 mt-0.5">
            年間利益が20万円以下のため、給与所得者は確定申告が不要な場合があります。
            ただし住民税の申告は別途必要です。詳しくは税理士にご確認ください。
          </p>
        </div>
      </div>
    );
  }
  return (
    <div className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 px-4 py-3">
      <span className="mt-0.5 text-red-500">!</span>
      <div>
        <p className="text-sm font-medium text-red-700">確定申告が必要です</p>
        <p className="text-xs text-red-600 mt-0.5">
          年間利益が20万円を超えているため確定申告が必要です。
          申告期限は翌年3月15日です。詳しくは税理士にご確認ください。
        </p>
      </div>
    </div>
  );
}

// ── セクションヘッダー ────────────────────────────────────
function SectionHeading({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <div className="w-1 h-5 rounded-full bg-blue-600" />
      <h2 className="text-sm font-semibold text-slate-700">{children}</h2>
    </div>
  );
}

// ── 月別グラフ ────────────────────────────────────────────
function MonthlyChart({ data }: { data: DashboardData["by_month"] }) {
  // 12ヶ月全てある場合は "1月" 〜 "12月"、それ以外は "YYYY/MM" で表示
  const allSameYear = data.length === 12 && new Set(data.map((d) => d.year_month.slice(0, 4))).size === 1;
  const chartData = data.map((d) => ({
    month: allSameYear
      ? `${parseInt(d.year_month.slice(5), 10)}月`
      : d.year_month.replace(/^(\d{4})-(\d{2})$/, "$1/$2"),
    損益: d.profit_loss,
  }));

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={chartData} margin={{ top: 4, right: 4, left: -10, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#94a3b8" }} />
        <YAxis
          tickFormatter={(v) => `¥${(v / 10000).toFixed(0)}万`}
          tick={{ fontSize: 10, fill: "#94a3b8" }}
          width={50}
        />
        <Tooltip
          formatter={(value: number | undefined) => [value != null ? formatJPY(value) : "－", "損益"]}
          labelStyle={{ fontSize: 12 }}
          contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid #e2e8f0" }}
        />
        <Bar dataKey="損益" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, i) => (
            <Cell
              key={i}
              fill={entry.損益 > 0 ? "#10b981" : entry.損益 < 0 ? "#ef4444" : "#cbd5e1"}
            />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

// 通貨シンボルから基軸通貨を抽出（"BTC/JPY" → "BTC"）
function baseCurrency(symbol: string) {
  return symbol.includes("/") ? symbol.split("/")[0] : symbol;
}

// ── 通貨別テーブル ────────────────────────────────────────
function CurrencyTable({ data }: { data: DashboardData["by_currency"] }) {
  const totalPL = data.reduce((s, r) => s + r.profit_loss, 0);
  const totalTx = data.reduce((s, r) => s + r.transaction_count, 0);
  const totalBuy = data.reduce((s, r) => s + r.buy_count, 0);
  const totalSell = data.reduce((s, r) => s + r.sell_count, 0);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-xs text-slate-500">
            <th className="text-left py-2 font-medium">通貨</th>
            <th className="text-right py-2 font-medium">損益（円）</th>
            <th className="text-right py-2 font-medium">取引件数</th>
            <th className="text-right py-2 font-medium">購入</th>
            <th className="text-right py-2 font-medium">売却</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={row.symbol} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
              <td className="py-2.5 font-medium text-slate-800">{baseCurrency(row.symbol)}</td>
              <td className={`py-2.5 text-right font-semibold tabular-nums ${row.profit_loss > 0 ? "text-emerald-600" : row.profit_loss < 0 ? "text-red-500" : "text-slate-400"}`}>
                {row.profit_loss !== 0 ? (row.profit_loss > 0 ? "+" : "") + formatJPY(row.profit_loss) : "－"}
              </td>
              <td className="py-2.5 text-right text-slate-600 tabular-nums">{row.transaction_count}</td>
              <td className="py-2.5 text-right text-slate-600 tabular-nums">{row.buy_count}</td>
              <td className="py-2.5 text-right text-slate-600 tabular-nums">{row.sell_count}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-slate-300 bg-slate-50 font-semibold">
            <td className="py-2.5 text-xs text-slate-500">合計</td>
            <td className={`py-2.5 text-right tabular-nums ${totalPL > 0 ? "text-emerald-600" : totalPL < 0 ? "text-red-500" : "text-slate-400"}`}>
              {totalPL !== 0 ? (totalPL > 0 ? "+" : "") + formatJPY(totalPL) : "－"}
            </td>
            <td className="py-2.5 text-right text-slate-700 tabular-nums">{totalTx}</td>
            <td className="py-2.5 text-right text-slate-700 tabular-nums">{totalBuy}</td>
            <td className="py-2.5 text-right text-slate-700 tabular-nums">{totalSell}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

// ── 取引所別テーブル ──────────────────────────────────────
function ExchangeTable({ data }: { data: DashboardData["by_exchange"] }) {
  const absTotal = data.reduce((s, r) => s + Math.abs(r.profit_loss), 0);
  const totalPL = data.reduce((s, r) => s + r.profit_loss, 0);
  const totalTx = data.reduce((s, r) => s + r.transaction_count, 0);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-xs text-slate-500">
            <th className="text-left py-2 font-medium">取引所</th>
            <th className="text-right py-2 font-medium">損益（円）</th>
            <th className="text-right py-2 font-medium">取引件数</th>
            <th className="text-left py-2 pl-4 font-medium">割合</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => {
            const pct = absTotal > 0 ? Math.round((Math.abs(row.profit_loss) / absTotal) * 100) : 0;
            return (
              <tr key={row.exchange} className={i % 2 === 0 ? "bg-white" : "bg-slate-50"}>
                <td className="py-2.5 font-medium text-slate-800 capitalize">{row.exchange}</td>
                <td className={`py-2.5 text-right font-semibold tabular-nums ${row.profit_loss > 0 ? "text-emerald-600" : row.profit_loss < 0 ? "text-red-500" : "text-slate-400"}`}>
                  {row.profit_loss !== 0 ? (row.profit_loss > 0 ? "+" : "") + formatJPY(row.profit_loss) : "－"}
                </td>
                <td className="py-2.5 text-right text-slate-600 tabular-nums">{row.transaction_count}</td>
                <td className="py-2.5 pl-4">
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-slate-200 rounded-full h-1.5 w-20">
                      <div className="bg-blue-500 h-1.5 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                    <span className="text-xs text-slate-500 w-8 text-right">{pct}%</span>
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-slate-300 bg-slate-50 font-semibold">
            <td className="py-2.5 text-xs text-slate-500">合計</td>
            <td className={`py-2.5 text-right tabular-nums ${totalPL > 0 ? "text-emerald-600" : totalPL < 0 ? "text-red-500" : "text-slate-400"}`}>
              {totalPL !== 0 ? (totalPL > 0 ? "+" : "") + formatJPY(totalPL) : "－"}
            </td>
            <td className="py-2.5 text-right text-slate-700 tabular-nums">{totalTx}</td>
            <td className="py-2.5 pl-4 text-xs text-slate-400">100%</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

// ── メインコンポーネント ──────────────────────────────────
export function DashboardClient() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<number | undefined>(undefined);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setData(null);
    getDashboard(selectedId)
      .then(setData)
      .catch((e) => setError(e instanceof Error ? e.message : "データの取得に失敗しました"))
      .finally(() => setLoading(false));
  }, [selectedId]);

  if (loading) return <p className="text-slate-500 py-12 text-center">読み込み中...</p>;
  if (error) return (
    <div className="text-center py-12">
      <p className="text-red-500">{error}</p>
      <p className="text-sm text-slate-400 mt-2 mb-4">まずCSVをアップロードして計算を実行してください</p>
      <Link
        href="/calculate"
        className="inline-block text-sm font-medium text-blue-600 hover:text-blue-800 border border-blue-300 rounded-lg px-4 py-2 hover:bg-blue-50 transition-colors"
      >
        計算ページへ →
      </Link>
    </div>
  );
  if (!data) return null;

  const isProfit = data.total_profit_loss >= 0;

  return (
    <div className="space-y-6">
      {/* ── ページヘッダー + セレクター ── */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold text-slate-800">ダッシュボード</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {data.tax_year ? `${data.tax_year}年度` : "最新"} の損益サマリー
          </p>
        </div>
        {data.available_sessions.length > 1 && (
          <select
            value={selectedId ?? data.session_id}
            onChange={(e) => setSelectedId(Number(e.target.value))}
            className="text-sm border border-slate-200 rounded-lg px-3 py-2 bg-white text-slate-700 shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            {data.available_sessions.map((s) => (
              <option key={s.id} value={s.id}>{sessionLabel(s)}</option>
            ))}
          </select>
        )}
      </div>

      {/* ── KPI カード ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <KpiCard
          label="売買損益（確定）"
          value={(isProfit ? "+" : "") + formatJPY(data.total_profit_loss)}
          sub={isProfit ? "▲ 利益" : "▼ 損失"}
          accent={isProfit ? "green" : "red"}
        />
        <KpiCard
          label="概算税額（目安）"
          value={data.total_profit_loss > 0 ? formatJPY(Math.round(data.total_profit_loss * 0.2)) : "－"}
          sub="税率20%で試算 ※実際は所得により異なる"
          accent={data.total_profit_loss > 0 ? "red" : undefined}
        />
        <KpiCard
          label="総取引件数"
          value={data.transaction_count.toLocaleString()}
          sub={`購入 ${data.buy_count} / 売却 ${data.sell_count}`}
        />
        <KpiCard
          label="計算方法"
          value={methodLabel(data.calc_method)}
          accent="blue"
        />
      </div>

      {/* ── 申告ステータスバナー ── */}
      <TaxNotice profit={data.total_profit_loss} />

      {/* ── 月別損益グラフ ── */}
      {data.by_month.length > 0 && (
        <div className="rounded-xl border bg-white p-3 sm:p-5 shadow-sm">
          <SectionHeading>月別 損益推移</SectionHeading>
          <MonthlyChart data={data.by_month} />
        </div>
      )}

      {/* ── 通貨別 + 取引所別（2カラム） ── */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {data.by_currency.length > 0 && (
          <div className="rounded-xl border bg-white p-3 sm:p-5 shadow-sm">
            <SectionHeading>通貨別 損益内訳</SectionHeading>
            <CurrencyTable data={data.by_currency} />
          </div>
        )}
        {data.by_exchange.length > 0 && (
          <div className="rounded-xl border bg-white p-3 sm:p-5 shadow-sm">
            <SectionHeading>取引所別 損益内訳</SectionHeading>
            <ExchangeTable data={data.by_exchange} />
          </div>
        )}
      </div>
    </div>
  );
}
