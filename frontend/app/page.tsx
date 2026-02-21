"use client";

import { useState } from "react";
import { calculate } from "@/lib/api";
import type {
  CalcMethod,
  CalculateRequest,
  CalculateResponseWithSession,
  TransactionResponse,
} from "@/lib/types";
import { CalcMethodSelector } from "@/components/CalcMethodSelector";
import { DownloadButtons } from "@/components/DownloadButtons";
import { FileUploader } from "@/components/FileUploader";
import { ResultMetrics } from "@/components/ResultMetrics";
import { TransactionTable } from "@/components/TransactionTable";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

type Step = "upload" | "calculate" | "result";

export default function Home() {
  const [step, setStep] = useState<Step>("upload");
  const [transactions, setTransactions] = useState<TransactionResponse[]>([]);
  const [method, setMethod] = useState<CalcMethod>("moving_average");
  const [result, setResult] = useState<CalculateResponseWithSession | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [calcError, setCalcError] = useState<string | null>(null);

  function handleTransactions(txs: TransactionResponse[]) {
    setTransactions(txs);
    if (txs.length > 0) setStep("calculate");
    else setStep("upload");
  }

  async function handleCalculate() {
    if (transactions.length === 0) return;
    setIsCalculating(true);
    setCalcError(null);
    try {
      const req: CalculateRequest = { transactions, method };
      const res = await calculate(req);
      setResult(res);
      setStep("result");
    } catch (err) {
      setCalcError(
        err instanceof Error ? err.message : "計算中にエラーが発生しました"
      );
    } finally {
      setIsCalculating(false);
    }
  }

  function handleReset() {
    setStep("upload");
    setTransactions([]);
    setResult(null);
    setCalcError(null);
  }

  const calcRequest: CalculateRequest | null =
    result ? { transactions, method } : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">暗号資産 損益計算</h1>
        <p className="text-sm text-muted-foreground">
          CSVをアップロードして税金計算を行います
        </p>
      </div>

      {/* Step indicator */}
      <div className="flex items-center gap-2 text-sm">
        {(["upload", "calculate", "result"] as Step[]).map((s, i) => {
          const labels: Record<Step, string> = {
            upload: "1. アップロード",
            calculate: "2. 計算設定",
            result: "3. 結果",
          };
          const isActive = step === s;
          const isPast =
            (s === "upload" && (step === "calculate" || step === "result")) ||
            (s === "calculate" && step === "result");
          return (
            <span
              key={s}
              className={`flex items-center gap-2 ${
                isActive
                  ? "font-semibold text-foreground"
                  : isPast
                  ? "text-muted-foreground"
                  : "text-muted-foreground/40"
              }`}
            >
              {i > 0 && <span className="text-muted-foreground/30">›</span>}
              {labels[s]}
            </span>
          );
        })}
      </div>

      <Separator />

      {/* Step A: Upload */}
      <Card>
        <CardHeader>
          <CardTitle>CSVファイルのアップロード</CardTitle>
        </CardHeader>
        <CardContent>
          <FileUploader onTransactions={handleTransactions} />
          {transactions.length > 0 && (
            <p className="mt-3 text-sm text-muted-foreground">
              合計 <strong>{transactions.length.toLocaleString()} 件</strong>{" "}
              の取引を読み込みました
            </p>
          )}
        </CardContent>
      </Card>

      {/* Step B: Calculate */}
      {(step === "calculate" || step === "result") && (
        <Card>
          <CardHeader>
            <CardTitle>計算設定</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <CalcMethodSelector value={method} onChange={setMethod} />
            {calcError && (
              <p className="text-sm text-destructive">{calcError}</p>
            )}
            <div className="flex gap-3">
              <Button
                onClick={handleCalculate}
                disabled={isCalculating || transactions.length === 0}
              >
                {isCalculating ? "計算中..." : "計算する"}
              </Button>
              {step === "result" && (
                <Button variant="outline" onClick={handleReset}>
                  最初からやり直す
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step C: Results */}
      {step === "result" && result && (
        <>
          <Card>
            <CardHeader>
              <CardTitle>計算結果</CardTitle>
            </CardHeader>
            <CardContent>
              <ResultMetrics result={result} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>取引一覧</CardTitle>
                {calcRequest && <DownloadButtons request={calcRequest} />}
              </div>
            </CardHeader>
            <CardContent>
              <TransactionTable results={result.results} />
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
