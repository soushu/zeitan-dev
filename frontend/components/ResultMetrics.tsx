import type { CalculateResponseWithSession } from "@/lib/types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { formatJPY } from "@/lib/format";

interface ResultMetricsProps {
  result: CalculateResponseWithSession;
}

export function ResultMetrics({ result }: ResultMetricsProps) {
  const sellCount = result.results.filter(
    (r) => r.type.toLowerCase() === "sell"
  ).length;

  const estimatedTax = result.total_profit_loss > 0
    ? Math.round(result.total_profit_loss * 0.2)
    : null;

  const metrics = [
    {
      title: "総損益",
      value: formatJPY(result.total_profit_loss),
      highlight: true,
      positive: result.total_profit_loss >= 0,
    },
    {
      title: "概算税額（目安）",
      value: estimatedTax != null ? formatJPY(estimatedTax) : "－",
      sub: "税率20%で試算",
      highlight: estimatedTax != null,
      positive: false,
    },
    {
      title: "総取引件数",
      value: `${result.results.length.toLocaleString()} 件`,
    },
    {
      title: "売却件数",
      value: `${sellCount.toLocaleString()} 件`,
    },
  ];

  return (
    <div className="grid grid-cols-2 gap-2 sm:gap-4 md:grid-cols-4">
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
            {"sub" in m && m.sub && (
              <p className="text-xs text-muted-foreground mt-1">{m.sub}</p>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
