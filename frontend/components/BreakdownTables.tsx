"use client";

import type { CurrencyBreakdown, ExchangeBreakdown, TradeResultResponse } from "@/lib/types";
import { formatJPY } from "@/lib/format";

// 通貨シンボルから基軸通貨を抽出（"BTC/JPY" → "BTC"）
function baseCurrency(symbol: string) {
  return symbol.includes("/") ? symbol.split("/")[0] : symbol;
}

// TradeResultResponse[] から通貨別・取引所別に集計
function computeBreakdowns(results: TradeResultResponse[]) {
  const currencyMap = new Map<string, CurrencyBreakdown>();
  const exchangeMap = new Map<string, ExchangeBreakdown>();

  for (const r of results) {
    if (!currencyMap.has(r.symbol)) {
      currencyMap.set(r.symbol, {
        symbol: r.symbol,
        profit_loss: 0,
        transaction_count: 0,
        sell_count: 0,
        buy_count: 0,
      });
    }
    const c = currencyMap.get(r.symbol)!;
    c.profit_loss += r.profit_loss;
    c.transaction_count++;
    if (r.type === "sell") c.sell_count++;
    if (r.type === "buy") c.buy_count++;

    if (!exchangeMap.has(r.exchange)) {
      exchangeMap.set(r.exchange, { exchange: r.exchange, profit_loss: 0, transaction_count: 0 });
    }
    const e = exchangeMap.get(r.exchange)!;
    e.profit_loss += r.profit_loss;
    e.transaction_count++;
  }

  const byCurrency = [...currencyMap.values()].sort(
    (a, b) => Math.abs(b.profit_loss) - Math.abs(a.profit_loss)
  );
  const byExchange = [...exchangeMap.values()].sort(
    (a, b) => Math.abs(b.profit_loss) - Math.abs(a.profit_loss)
  );

  return { byCurrency, byExchange };
}

function plClass(v: number) {
  return v > 0 ? "text-emerald-600" : v < 0 ? "text-red-500" : "text-slate-400";
}
function plText(v: number) {
  if (v === 0) return "－";
  return (v > 0 ? "+" : "") + formatJPY(Math.round(v));
}

// ── 通貨別テーブル ────────────────────────────────────────
function CurrencyTable({ data }: { data: CurrencyBreakdown[] }) {
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
              <td className="py-2 font-medium text-slate-800">{baseCurrency(row.symbol)}</td>
              <td className={`py-2 text-right font-semibold tabular-nums ${plClass(row.profit_loss)}`}>
                {plText(row.profit_loss)}
              </td>
              <td className="py-2 text-right text-slate-600 tabular-nums">{row.transaction_count}</td>
              <td className="py-2 text-right text-slate-600 tabular-nums">{row.buy_count}</td>
              <td className="py-2 text-right text-slate-600 tabular-nums">{row.sell_count}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr className="border-t-2 border-slate-300 bg-slate-50 font-semibold">
            <td className="py-2 text-xs text-slate-500">合計</td>
            <td className={`py-2 text-right tabular-nums ${plClass(totalPL)}`}>{plText(totalPL)}</td>
            <td className="py-2 text-right text-slate-700 tabular-nums">{totalTx}</td>
            <td className="py-2 text-right text-slate-700 tabular-nums">{totalBuy}</td>
            <td className="py-2 text-right text-slate-700 tabular-nums">{totalSell}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

// ── 取引所別テーブル ──────────────────────────────────────
function ExchangeTable({ data }: { data: ExchangeBreakdown[] }) {
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
                <td className="py-2 font-medium text-slate-800 capitalize">{row.exchange}</td>
                <td className={`py-2 text-right font-semibold tabular-nums ${plClass(row.profit_loss)}`}>
                  {plText(row.profit_loss)}
                </td>
                <td className="py-2 text-right text-slate-600 tabular-nums">{row.transaction_count}</td>
                <td className="py-2 pl-4">
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
            <td className="py-2 text-xs text-slate-500">合計</td>
            <td className={`py-2 text-right tabular-nums ${plClass(totalPL)}`}>{plText(totalPL)}</td>
            <td className="py-2 text-right text-slate-700 tabular-nums">{totalTx}</td>
            <td className="py-2 pl-4 text-xs text-slate-400">100%</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

// ── メインコンポーネント ──────────────────────────────────
interface BreakdownTablesProps {
  results: TradeResultResponse[];
}

export function BreakdownTables({ results }: BreakdownTablesProps) {
  const { byCurrency, byExchange } = computeBreakdowns(results);

  if (byCurrency.length === 0) return null;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div className="rounded-xl border bg-white p-4 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
          <span className="w-1 h-4 rounded-full bg-blue-600 inline-block" />
          通貨別 損益内訳
        </h3>
        <CurrencyTable data={byCurrency} />
      </div>
      {byExchange.length > 1 && (
        <div className="rounded-xl border bg-white p-4 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-700 mb-3 flex items-center gap-2">
            <span className="w-1 h-4 rounded-full bg-blue-600 inline-block" />
            取引所別 損益内訳
          </h3>
          <ExchangeTable data={byExchange} />
        </div>
      )}
    </div>
  );
}
