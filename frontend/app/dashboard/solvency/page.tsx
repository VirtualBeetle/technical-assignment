"use client";
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { usePeriod } from "@/lib/PeriodContext";
import { useMetrics, fmtEur, shortLabel } from "@/lib/useMetrics";
import { api } from "@/lib/api";
import KpiCard from "@/components/KpiCard";
import CommentaryBlock from "@/components/CommentaryBlock";

export default function SolvencyPage() {
  const { selected } = usePeriod();
  const { rows } = useMetrics("solvency");
  const [commentary, setCommentary] = useState({ text: "", generatedBy: "" });

  useEffect(() => {
    if (!selected) return;
    api.insights(selected).then((r) => {
      const row = r.find((x: any) => x.section === "solvency");
      if (row) setCommentary({ text: row.text, generatedBy: row.generated_by });
    });
  }, [selected]);

  const current = rows.find((r) => r.period.period_key === selected)?.metrics;
  const trend = rows.map((row) => ({
    name: shortLabel(row.period.period_key),
    Cash: row.metrics.cash,
    "Bank Debt": row.metrics.bank_debt,
    "Net Cash Position": row.metrics.net_cash_position,
  }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard label="Net Cash Position" value={fmtEur(current?.net_cash_position)} tone={current?.net_cash_position > 0 ? "positive" : "negative"} accent="solvency" />
        <KpiCard label="Bank Debt" value={fmtEur(current?.bank_debt)} accent="warn" />
        <KpiCard label="Current Ratio" value={current?.current_ratio ? `${current.current_ratio}x` : "—"} accent="solvency" />
        <KpiCard label="Interest Cover" value={current?.interest_cover_x ? `${current.interest_cover_x}x` : "—"} accent="solvency" />
      </div>

      {current && current.contingent_consideration > 0 && (
        <div className="card border-l-4 border-l-warn border-t-0 p-4 text-sm text-amber-100/90">
          <strong className="text-warn">Watch item:</strong> {fmtEur(current.contingent_consideration)} of
          contingent consideration relates to the performance-linked Loamin acquisition earn-out — non-cash unless
          targets are achieved, but it depresses reported net current assets in the statutory balance sheet.
        </div>
      )}

      <div className="card p-5">
        <h2 className="mb-4 text-sm font-medium text-slate-300">Cash, debt &amp; net position by period</h2>
        <ResponsiveContainer width="100%" height={280}>
          <BarChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
            <XAxis dataKey="name" stroke="#7c8aad" fontSize={12} />
            <YAxis stroke="#7c8aad" fontSize={12} tickFormatter={(v) => fmtEur(v)} />
            <Tooltip contentStyle={{ background: "#111a2e", border: "1px solid #1e2a45", color: "#fff" }} formatter={(v: number) => fmtEur(v)} />
            <Legend />
            <Bar dataKey="Cash" fill="#22d3ee" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Bank Debt" fill="#fbbf24" radius={[4, 4, 0, 0]} />
            <Bar dataKey="Net Cash Position" fill="#2dd4bf" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {!current?.dscr_meaningful && (
        <p className="text-xs text-slate-500">
          Debt Service Coverage Ratio and Net Debt/EBITDA are not shown numerically while EBITDA is negative — see AI
          commentary below for why, and what would make them meaningful (Senus 2030 targets EBITDA breakeven in FY2028).
        </p>
      )}

      {commentary.text && <CommentaryBlock text={commentary.text} generatedBy={commentary.generatedBy} />}
    </div>
  );
}
