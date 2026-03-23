export interface ExchangeConfig {
  id: string;
  name: string;
  nameJa: string;
  category: "domestic" | "international";
  color: string;
  instructions: string[];
}

export const EXCHANGES: ExchangeConfig[] = [
  {
    id: "bitflyer",
    name: "bitFlyer",
    nameJa: "ビットフライヤー",
    category: "domestic",
    color: "#1DA2DC",
    instructions: [
      "bitFlyerにログイン",
      "「お取引レポート」→「取引履歴」を選択",
      "期間を指定してCSVをダウンロード",
    ],
  },
  {
    id: "coincheck",
    name: "Coincheck",
    nameJa: "コインチェック",
    category: "domestic",
    color: "#2BAD4A",
    instructions: [
      "Coincheckにログイン",
      "「取引履歴」ページへ移動",
      "CSVダウンロードボタンをクリック",
    ],
  },
  {
    id: "gmo",
    name: "GMOコイン",
    nameJa: "GMOコイン",
    category: "domestic",
    color: "#0070C0",
    instructions: [
      "GMOコインにログイン",
      "「明細」→「取引履歴」を選択",
      "期間を指定してCSVをダウンロード",
    ],
  },
  {
    id: "bitbank",
    name: "bitbank",
    nameJa: "ビットバンク",
    category: "domestic",
    color: "#00A968",
    instructions: [
      "bitbankにログイン",
      "「資産」→「取引履歴」を選択",
      "CSVをダウンロード",
    ],
  },
  {
    id: "sbivc",
    name: "SBI VCトレード",
    nameJa: "SBI VCトレード",
    category: "domestic",
    color: "#003399",
    instructions: [
      "SBI VCトレードにログイン",
      "「取引履歴」を選択",
      "CSVをダウンロード",
    ],
  },
  {
    id: "rakuten",
    name: "楽天ウォレット",
    nameJa: "楽天ウォレット",
    category: "domestic",
    color: "#BF0000",
    instructions: [
      "楽天ウォレットにログイン",
      "「取引履歴」を選択",
      "CSVをダウンロード",
    ],
  },
  {
    id: "linebitmax",
    name: "LINE BITMAX",
    nameJa: "LINE BITMAX",
    category: "domestic",
    color: "#06C755",
    instructions: [
      "LINE BITMAXアプリを開く",
      "「取引履歴」を選択",
      "CSVをダウンロード",
    ],
  },
  {
    id: "binance",
    name: "Binance",
    nameJa: "バイナンス",
    category: "international",
    color: "#F0B90B",
    instructions: [
      "Binanceにログイン",
      "「Orders」→「Trade History」を選択",
      "「Export Trade History」からCSVをダウンロード",
    ],
  },
  {
    id: "bybit",
    name: "Bybit",
    nameJa: "バイビット",
    category: "international",
    color: "#F7A600",
    instructions: [
      "Bybitにログイン",
      "「Assets」→「Transaction History」を選択",
      "CSVをダウンロード",
    ],
  },
  {
    id: "kraken",
    name: "Kraken",
    nameJa: "クラーケン",
    category: "international",
    color: "#5741D9",
    instructions: [
      "Krakenにログイン",
      "「History」→「Export」を選択",
      "Trades/Ledgerを選択してCSVをダウンロード",
    ],
  },
  {
    id: "coinbase",
    name: "Coinbase",
    nameJa: "コインベース",
    category: "international",
    color: "#0052FF",
    instructions: [
      "Coinbaseにログイン",
      "「Reports」→「Transaction History」を選択",
      "「Generate Report」でCSVをダウンロード",
    ],
  },
];

export function getExchangeById(id: string): ExchangeConfig | undefined {
  return EXCHANGES.find((e) => e.id === id);
}
