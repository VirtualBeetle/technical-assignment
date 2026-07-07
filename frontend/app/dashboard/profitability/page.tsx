"use client";
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { usePeriod } from "@/lib/PeriodContext";
import { useMetrics, fmtEur, fmtPct, shortLabel } from "@/lib/useMetrics";
import { api } from "@/lib/api";
import KpiCard from "@/components/KpiCard";
import CommentaryBlock from "@/components/CommentaryBlock";

export default function ProfitabilityPage() {
  const { selected } = usePeriod();
  const { rows } = useMetrics("profitability");
  const [commentary, setCommentary] = useState({ text: "", generatedBy: "" });

  useEffect(() => {
    if (!selected) return;
    api.insights(selected).then((r) => {
      const row = r.find((x: any) => x.section === "profitability");
      if (row) setCommentary({ text: row.text, generatedBy: row.generated_by });
    });
  }, [selected]);

  const current = rows.find((r) => r.period.period_key === selected)?.metrics;
  const marginTrend = rows.map((row) => ({
    name: shortLabel(row.period.period_key),
    "Gross Margin %": row.metrics.gross_margin_pct,
    "EBITDA Margin %": row.metrics.ebitda_margin_pct,
    "Operating Margin %": row.metrics.operating_margin_pct,
  }));
  const costBreakdown = current
    ? [
        { name: shortLabel(selected), "Cost of Sales": current.cost_of_sales, "Admin Expenses": current.administrative_expenses },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard label="Gross Margin" value={fmtPct(current?.gross_margin_pct)} accent="margin" />
        <KpiCard label="Operating Margin" value={fmtPct(current?.operating_margin_pct)} tone="negative" accent="warn" />
        <KpiCard label="EBITDA" value={fmtEur(current?.ebitda)} tone={current?.ebitda < 0 ? "negative" : "positive"} accent="warn" />
        <KpiCard label="EBITDA Margin" value={fmtPct(current?.ebitda_margin_pct)} tone={current?.ebitda_margin_pct < 0 ? "negative" : "positive"} accent="warn" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-5">
          <h2 className="mb-4 text-sm font-medium text-slate-300">Margin trend</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={marginTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
              <XAxis dataKey="name" stroke="#7c8aad" fontSize={12} />
              <YAxis stroke="#7c8aad" fontSize={12} tickFormatter={(v) => `${v}%`} />
              <Tooltip contentStyle={{ background: "#111a2e", border: "1px solid #1e2a45", color: "#fff" }} />
              <Legend />
              <Bar dataKey="Gross Margin %" fill="#a78bfa" radius={[4, 4, 0, 0]} />
              <Bar dataKey="EBITDA Margin %" fill="#fbbf24" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Operating Margin %" fill="#fb7185" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card p-5">
          <h2 className="mb-4 text-sm font-medium text-slate-300">Cost breakdown — {shortLabel(selected)}</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={costBreakdown} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
              <XAxis type="number" stroke="#7c8aad" fontSize={12} tickFormatter={(v) => fmtEur(v)} />
              <YAxis type="category" dataKey="name" stroke="#7c8aad" fontSize={12} />
              <Tooltip contentStyle={{ background: "#111a2e", border: "1px solid #1e2a45", color: "#fff" }} formatter={(v: number) => fmtEur(v)} />
              <Legend />
              <Bar dataKey="Cost of Sales" fill="#38bdf8" radius={[0, 4, 4, 0]} />
              <Bar dataKey="Admin Expenses" fill="#fbbf24" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {commentary.text && <CommentaryBlock text={commentary.text} generatedBy={commentary.generatedBy} />}
    </div>
  );
}
