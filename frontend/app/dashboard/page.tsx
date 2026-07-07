"use client";
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { usePeriod } from "@/lib/PeriodContext";
import { useMetrics, fmtEur, fmtPct, shortLabel } from "@/lib/useMetrics";
import { api } from "@/lib/api";
import KpiCard from "@/components/KpiCard";
import CommentaryBlock from "@/components/CommentaryBlock";

export default function OverviewPage() {
  const { selected } = usePeriod();
  const growth = useMetrics("growth");
  const profitability = useMetrics("profitability");
  const cash = useMetrics("cash");
  const solvency = useMetrics("solvency");
  const returns = useMetrics("returns");

  const [overview, setOverview] = useState<string>("");
  const [generatedBy, setGeneratedBy] = useState<string>("");

  useEffect(() => {
    if (!selected) return;
    api.insights(selected).then((rows) => {
      const row = rows.find((r: any) => r.section === "overview");
      if (row) {
        setOverview(row.text);
        setGeneratedBy(row.generated_by);
      }
    });
  }, [selected]);

  const g = growth.rows.find((r) => r.period.period_key === selected)?.metrics;
  const p = profitability.rows.find((r) => r.period.period_key === selected)?.metrics;
  const c = cash.rows.find((r) => r.period.period_key === selected)?.metrics;
  const s = solvency.rows.find((r) => r.period.period_key === selected)?.metrics;
  const r = returns.rows.find((r) => r.period.period_key === selected)?.metrics;

  const revenueTrend = growth.rows.map((row) => ({
    name: shortLabel(row.period.period_key),
    revenue: row.metrics.revenue,
  }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3 lg:grid-cols-6">
        <KpiCard
          label="Revenue"
          value={fmtEur(g?.revenue)}
          sub={g?.revenue_growth_pct !== undefined ? `${g.revenue_growth_pct > 0 ? "+" : ""}${g.revenue_growth_pct}% vs prior` : undefined}
          tone={g?.revenue_growth_pct > 0 ? "positive" : "neutral"}
          accent="revenue"
        />
        <KpiCard label="Gross Margin" value={fmtPct(p?.gross_margin_pct)} accent="margin" />
        <KpiCard
          label="EBITDA"
          value={fmtEur(p?.ebitda)}
          sub={fmtPct(p?.ebitda_margin_pct) + " margin"}
          tone={p?.ebitda < 0 ? "negative" : "positive"}
          accent="warn"
        />
        <KpiCard
          label="Cash"
          value={fmtEur(c?.cash)}
          sub={c?.cash_runway_months ? `${c.cash_runway_months} mo runway` : undefined}
          accent="cash"
        />
        <KpiCard
          label="Net Cash Position"
          value={fmtEur(s?.net_cash_position)}
          tone={s?.net_cash_position > 0 ? "positive" : "negative"}
          accent="solvency"
        />
        <KpiCard label="ROCE (annualised)" value={fmtPct(r?.roce_pct)} tone={r?.roce_pct < 0 ? "negative" : "positive"} accent="returns" />
      </div>

      <div className="card p-5">
        <h2 className="mb-4 text-sm font-medium text-slate-300">Revenue by period</h2>
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={revenueTrend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
            <XAxis dataKey="name" stroke="#7c8aad" fontSize={12} />
            <YAxis stroke="#7c8aad" fontSize={12} tickFormatter={(v) => fmtEur(v)} />
            <Tooltip
              contentStyle={{ background: "#111a2e", border: "1px solid #1e2a45", color: "#fff" }}
              formatter={(v: number) => fmtEur(v)}
            />
            <Bar dataKey="revenue" fill="#38bdf8" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {overview && <CommentaryBlock text={overview} generatedBy={generatedBy} />}
    </div>
  );
}
