/** 共通フォーマットユーティリティ */

export function formatJPY(n: number): string {
  return n.toLocaleString("ja-JP", {
    style: "currency",
    currency: "JPY",
    maximumFractionDigits: 0,
  });
}

export function formatDate(iso: string): string {
  const date = new Date(iso);
  if (isNaN(date.getTime())) return "－";
  return date.toLocaleDateString("ja-JP", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

export function methodLabel(method: string): string {
  return method === "moving_average" ? "移動平均法" : "総平均法";
}
