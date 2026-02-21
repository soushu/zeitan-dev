import type { CalculateResponseWithSession } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ResultMetricsProps {
  result: CalculateResponseWithSession;
}

function formatJPY(value: number): string {
  return value.toLocaleString("ja-JP", {
    style: "currency",
    currency: "JPY",
    maximumFractionDigits: 0,
  });
}

export function ResultMetrics({ result }: ResultMetricsProps) {
  const sellCount = result.results.filter(
    (r) => r.type.toLowerCase() === "sell"
  ).length;

  const miscIncome = result.results
    .filter((r) => r.type.toLowerCase() !== "sell")
    .reduce((sum, r) => sum + r.profit_loss, 0);

  const metrics = [
    {
      title: "総取引件数",
      value: `${result.results.length.toLocaleString()} 件`,
    },
    {
      title: "総損益",
      value: formatJPY(result.total_profit_loss),
      highlight: true,
      positive: result.total_profit_loss >= 0,
    },
    {
      title: "売却件数",
      value: `${sellCount.toLocaleString()} 件`,
    },
    {
      title: "雑所得",
      value: formatJPY(miscIncome),
      positive: miscIncome >= 0,
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
      {metrics.map((m) => (
        <Card key={m.title}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              {m.title}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p
              className={`text-xl font-bold ${
                m.highlight
                  ? m.positive
                    ? "text-green-600"
                    : "text-red-600"
                  : ""
              }`}
            >
              {m.value}
            </p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
