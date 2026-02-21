"use client";

import { useState } from "react";
import type { TradeResultResponse } from "@/lib/types";
import { Button } from "@/components/ui/button";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

interface TransactionTableProps {
  results: TradeResultResponse[];
}

const PAGE_SIZE = 20;

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString("ja-JP");
}

function formatNumber(n: number): string {
  return n.toLocaleString("ja-JP", { maximumFractionDigits: 8 });
}

function formatJPY(n: number): string {
  return n.toLocaleString("ja-JP", { maximumFractionDigits: 0 });
}

export function TransactionTable({ results }: TransactionTableProps) {
  const [page, setPage] = useState(0);
  const totalPages = Math.ceil(results.length / PAGE_SIZE);
  const slice = results.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE);

  return (
    <div className="space-y-2">
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>日時</TableHead>
              <TableHead>取引所</TableHead>
              <TableHead>通貨</TableHead>
              <TableHead>種別</TableHead>
              <TableHead className="text-right">数量</TableHead>
              <TableHead className="text-right">単価 (JPY)</TableHead>
              <TableHead className="text-right">損益 (JPY)</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {slice.map((r, i) => (
              <TableRow key={i}>
                <TableCell className="whitespace-nowrap text-xs">
                  {formatDate(r.timestamp)}
                </TableCell>
                <TableCell className="text-xs">{r.exchange}</TableCell>
                <TableCell className="font-medium">{r.symbol}</TableCell>
                <TableCell>
                  <Badge
                    variant={
                      r.type.toLowerCase() === "sell"
                        ? "default"
                        : "secondary"
                    }
                  >
                    {r.type}
                  </Badge>
                </TableCell>
                <TableCell className="text-right text-xs">
                  {formatNumber(r.amount)}
                </TableCell>
                <TableCell className="text-right text-xs">
                  {formatJPY(r.price)}
                </TableCell>
                <TableCell
                  className={`text-right font-medium ${
                    r.profit_loss >= 0 ? "text-green-600" : "text-red-600"
                  }`}
                >
                  {r.profit_loss !== 0
                    ? (r.profit_loss >= 0 ? "+" : "") + formatJPY(r.profit_loss)
                    : "-"}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {totalPages > 1 && (
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            {page * PAGE_SIZE + 1}〜
            {Math.min((page + 1) * PAGE_SIZE, results.length)} /{" "}
            {results.length} 件
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={page === 0}
              onClick={() => setPage((p) => p - 1)}
            >
              前へ
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={page >= totalPages - 1}
              onClick={() => setPage((p) => p + 1)}
            >
              次へ
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
