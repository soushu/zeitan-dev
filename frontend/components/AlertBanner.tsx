"use client";

import { useEffect, useState } from "react";
import { getAlerts } from "@/lib/api";
import type { AlertsResponse } from "@/lib/types";

interface AlertBannerProps {
  sessionId: number;
}

export function AlertBanner({ sessionId }: AlertBannerProps) {
  const [data, setData] = useState<AlertsResponse | null>(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    getAlerts(sessionId).then(setData).catch(() => {});
  }, [sessionId]);

  if (!data || data.alerts.length === 0) return null;

  const errorCount = data.alerts.filter((a) => a.severity === "error").length;
  const warningCount = data.alerts.filter((a) => a.severity === "warning").length;

  const borderColor = data.has_errors ? "border-red-300" : "border-amber-300";
  const bgColor = data.has_errors ? "bg-red-50" : "bg-amber-50";
  const iconColor = data.has_errors ? "text-red-500" : "text-amber-500";
  const titleColor = data.has_errors ? "text-red-700" : "text-amber-700";

  return (
    <div className={`rounded-xl border ${borderColor} ${bgColor} px-4 py-3`}>
      <div className="flex items-start gap-3">
        <span className={`mt-0.5 ${iconColor} text-lg`}>
          {data.has_errors ? "!" : "?"}
        </span>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between">
            <p className={`text-sm font-medium ${titleColor}`}>
              要処理アラート
              {errorCount > 0 && (
                <span className="ml-2 inline-flex items-center rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-700">
                  {errorCount}件のエラー
                </span>
              )}
              {warningCount > 0 && (
                <span className="ml-2 inline-flex items-center rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700">
                  {warningCount}件の警告
                </span>
              )}
            </p>
            <button
              onClick={() => setExpanded(!expanded)}
              className={`text-xs ${titleColor} hover:underline ml-2 whitespace-nowrap`}
            >
              {expanded ? "閉じる" : "詳細を見る"}
            </button>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            取引データに確認が必要な項目があります
          </p>

          {expanded && (
            <ul className="mt-3 space-y-2">
              {data.alerts.map((alert, i) => (
                <li
                  key={i}
                  className={`flex items-start gap-2 text-xs rounded-lg px-3 py-2 ${
                    alert.severity === "error"
                      ? "bg-red-100/60 text-red-700"
                      : "bg-amber-100/60 text-amber-700"
                  }`}
                >
                  <span className="font-bold mt-px">
                    {alert.severity === "error" ? "E" : "W"}
                  </span>
                  <span>{alert.message}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
