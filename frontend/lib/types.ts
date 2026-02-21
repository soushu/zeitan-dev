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
}

export interface SessionDetail extends SessionSummary {
  transactions: TransactionResponse[];
  results: TradeResultResponse[];
}
