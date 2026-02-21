"use client";

import type { CalcMethod } from "@/lib/types";

interface CalcMethodSelectorProps {
  value: CalcMethod;
  onChange: (method: CalcMethod) => void;
}

const METHODS: { value: CalcMethod; label: string; description: string }[] = [
  {
    value: "moving_average",
    label: "移動平均法",
    description: "取得のたびに平均単価を更新する方法",
  },
  {
    value: "total_average",
    label: "総平均法",
    description: "期間全体の平均単価を用いる方法",
  },
];

export function CalcMethodSelector({ value, onChange }: CalcMethodSelectorProps) {
  return (
    <div className="space-y-2">
      <p className="text-sm font-medium">計算方法</p>
      <div className="flex gap-4">
        {METHODS.map((m) => (
          <label
            key={m.value}
            className={`flex flex-1 cursor-pointer flex-col gap-1 rounded-lg border p-4 transition-colors
              ${value === m.value ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"}`}
          >
            <input
              type="radio"
              name="calc-method"
              value={m.value}
              checked={value === m.value}
              onChange={() => onChange(m.value)}
              className="sr-only"
            />
            <span className="font-medium">{m.label}</span>
            <span className="text-xs text-muted-foreground">{m.description}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
