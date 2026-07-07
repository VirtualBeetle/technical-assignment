"use client";
import { useEffect, useState } from "react";
import { api, Period } from "@/lib/api";

export type MetricsRow = { period: Period; metrics: Record<string, any> };

export function useMetrics(category: string) {
  const [rows, setRows] = useState<MetricsRow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    api
      .metrics(category)
      .then((data: MetricsRow[]) => {
        if (!cancelled) setRows(data);
      })
      .catch((e) => !cancelled && setError(String(e)))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [category]);

  return { rows, loading, error };
}

export function fmtEur(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  const sign = value < 0 ? "-" : "";
  const abs = Math.abs(value);
  if (abs >= 1_000_000) return `${sign}€${(abs / 1_000_000).toFixed(2)}m`;
  if (abs >= 1_000) return `${sign}€${(abs / 1_000).toFixed(1)}k`;
  return `${sign}€${abs.toFixed(0)}`;
}

export function fmtPct(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${value.toFixed(digits)}%`;
}

export function shortLabel(periodKey: string): string {
  const map: Record<string, string> = {
    FY2024: "FY24",
    FY2025: "FY25",
    HY_DEC_2024: "H1 FY25",
    HY_DEC_2025: "H1 FY26",
  };
  return map[periodKey] || periodKey;
}
