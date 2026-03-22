/** FastAPI Pydantic モデルに対応した TypeScript 型定義 */

export interface TransactionResponse {
  timestamp: string;
  exchange: string;
  symbol: string;
  type: string;
  amount: number;
  price: number;
  fee: number;
}

export type CalcMethod = "moving_average" | "total_average";

export interface CalculateRequest {
  transactions: TransactionResponse[];
  method: CalcMethod;
}

export interface TradeResultResponse {
  timestamp: string;
  exchange: string;
  symbol: string;
  type: string;
  amount: number;
  price: number;
  fee: number;
  profit_loss: number;
  average_cost_after: number | null;
  average_cost_used: number | null;
}

export interface CalculateResponse {
  results: TradeResultResponse[];
  total_profit_loss: number;
  method: string;
}

export interface CalculateResponseWithSession extends CalculateResponse {
  session_id: number;
}

export interface ExchangeInfo {
  id: string;
  name: string;
  category: "domestic" | "international";
}

export interface SessionSummary {
  id: number;
  created_at: string;
  calc_method: string;
  total_profit_loss: number;
  transaction_count: number;
  note: string | null;
  tax_year: number | null;
}

export interface SessionDetail extends SessionSummary {
  transactions: TransactionResponse[];
  results: TradeResultResponse[];
}

export interface CurrencyBreakdown {
  symbol: string;
  profit_loss: number;
  transaction_count: number;
  sell_count: number;
  buy_count: number;
}

export interface ExchangeBreakdown {
  exchange: string;
  profit_loss: number;
  transaction_count: number;
}

export interface MonthlyBreakdown {
  year_month: string;
  profit_loss: number;
  sell_count: number;
}

export interface AlertItem {
  type: "oversell" | "no_buy_before_sell" | "duplicate";
  severity: "error" | "warning";
  symbol: string;
  message: string;
  transaction_index: number | null;
}

export interface AlertsResponse {
  alerts: AlertItem[];
  has_errors: boolean;
  has_warnings: boolean;
}

export interface DashboardData {
  session_id: number;
  tax_year: number | null;
  calc_method: string;
  total_profit_loss: number;
  transaction_count: number;
  sell_count: number;
  buy_count: number;
  by_currency: CurrencyBreakdown[];
  by_exchange: ExchangeBreakdown[];
  by_month: MonthlyBreakdown[];
  available_sessions: SessionSummary[];
}
