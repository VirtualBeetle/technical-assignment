"use client";
import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend } from "recharts";
import { usePeriod } from "@/lib/PeriodContext";
import { useMetrics, fmtEur, fmtPct, shortLabel } from "@/lib/useMetrics";
import { api } from "@/lib/api";
import KpiCard from "@/components/KpiCard";
import CommentaryBlock from "@/components/CommentaryBlock";

export default function GrowthPage() {
  const { selected } = usePeriod();
  const { rows } = useMetrics("growth");
  const [commentary, setCommentary] = useState({ text: "", generatedBy: "" });

  useEffect(() => {
    if (!selected) return;
    api.insights(selected).then((r) => {
      const row = r.find((x: any) => x.section === "growth");
      if (row) setCommentary({ text: row.text, generatedBy: row.generated_by });
    });
  }, [selected]);

  const current = rows.find((r) => r.period.period_key === selected)?.metrics;
  const trend = rows.map((row) => ({
    name: shortLabel(row.period.period_key),
    Revenue: row.metrics.revenue,
    "Gross Profit": row.metrics.gross_profit,
  }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard label="Revenue" value={fmtEur(current?.revenue)} accent="revenue" />
        <KpiCard label="Revenue Growth" value={fmtPct(current?.revenue_growth_pct)} tone={current?.revenue_growth_pct > 0 ? "positive" : "negative"} accent="revenue" />
        <KpiCard label="Gross Profit Growth" value={fmtPct(current?.gross_profit_growth_pct)} tone={current?.gross_profit_growth_pct > 0 ? "positive" : "negative"} accent="margin" />
        <KpiCard label="Customer Accounts" value={current?.customer_accounts ? String(current.customer_accounts) : "—"} sub="Most recent annual filing" accent="brand" />
      </div>

      <div className="card p-5">
        <h2 className="mb-4 text-sm font-medium text-slate-300">Revenue &amp; gross profit trend</h2>
        <ResponsiveContainer width="100%" height={260}>
          <LineChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
            <XAxis dataKey="name" stroke="#7c8aad" fontSize={12} />
            <YAxis stroke="#7c8aad" fontSize={12} tickFormatter={(v) => fmtEur(v)} />
            <Tooltip contentStyle={{ background: "#111a2e", border: "1px solid #1e2a45", color: "#fff" }} formatter={(v: number) => fmtEur(v)} />
            <Legend />
            <Line type="monotone" dataKey="Revenue" stroke="#38bdf8" strokeWidth={2.5} dot={{ r: 3 }} />
            <Line type="monotone" dataKey="Gross Profit" stroke="#a78bfa" strokeWidth={2.5} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {current?.pipeline_deals_closed_in_period_eur !== undefined && (
        <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
          <KpiCard label="Deals Closed (Period)" value={fmtEur(current.pipeline_deals_closed_in_period_eur)} sub={`${current.pipeline_deals_closed_in_period_customers} enterprise customers`} accent="revenue" />
          <KpiCard label="Open Pipeline" value={fmtEur(current.open_pipeline_eur)} accent="brand" />
          <KpiCard label="Deals Closed (final 2mo 2025)" value={fmtEur(current.deals_closed_final_2_months_2025_eur)} sub={`${current.deals_closed_final_2_months_2025_count} deals`} accent="revenue" />
        </div>
      )}

      {commentary.text && <CommentaryBlock text={commentary.text} generatedBy={commentary.generatedBy} />}
    </div>
  );
}
