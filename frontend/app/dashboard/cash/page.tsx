"use client";
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend, Cell } from "recharts";
import { usePeriod } from "@/lib/PeriodContext";
import { useMetrics, fmtEur, shortLabel } from "@/lib/useMetrics";
import { api } from "@/lib/api";
import KpiCard from "@/components/KpiCard";
import CommentaryBlock from "@/components/CommentaryBlock";

export default function CashPage() {
  const { selected } = usePeriod();
  const { rows } = useMetrics("cash");
  const [commentary, setCommentary] = useState({ text: "", generatedBy: "" });

  useEffect(() => {
    if (!selected) return;
    api.insights(selected).then((r) => {
      const row = r.find((x: any) => x.section === "cash");
      if (row) setCommentary({ text: row.text, generatedBy: row.generated_by });
    });
  }, [selected]);

  const current = rows.find((r) => r.period.period_key === selected)?.metrics;
  const cashTrend = rows.map((row) => ({ name: shortLabel(row.period.period_key), Cash: row.metrics.cash }));

  const bridge = current?.ebitda_to_fcf_bridge;
  const bridgeData = bridge
    ? [
        { name: "EBITDA", value: bridge.ebitda },
        { name: "Working Capital", value: bridge.working_capital_movement },
        { name: "Interest", value: bridge.interest },
        { name: "Capex", value: bridge.capex },
        { name: "Free Cash Flow", value: bridge.free_cash_flow, isTotal: true },
      ]
    : [];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        <KpiCard label="Cash Balance" value={fmtEur(current?.cash)} accent="cash" />
        <KpiCard label="Monthly Cash Burn" value={fmtEur(current?.monthly_cash_burn)} accent="warn" />
        <KpiCard label="Cash Runway" value={current?.cash_runway_months ? `${current.cash_runway_months} months` : "—"} accent="cash" />
        <KpiCard label="Working Capital" value={fmtEur(current?.working_capital)} accent="solvency" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-5">
          <h2 className="mb-4 text-sm font-medium text-slate-300">Cash balance by period</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={cashTrend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
              <XAxis dataKey="name" stroke="#7c8aad" fontSize={12} />
              <YAxis stroke="#7c8aad" fontSize={12} tickFormatter={(v) => fmtEur(v)} />
              <Tooltip contentStyle={{ background: "#111a2e", border: "1px solid #1e2a45", color: "#fff" }} formatter={(v: number) => fmtEur(v)} />
              <Bar dataKey="Cash" fill="#22d3ee" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="card p-5">
          <h2 className="mb-4 text-sm font-medium text-slate-300">EBITDA → Free Cash Flow bridge — {shortLabel(selected)}</h2>
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={bridgeData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
              <XAxis dataKey="name" stroke="#7c8aad" fontSize={11} />
              <YAxis stroke="#7c8aad" fontSize={12} tickFormatter={(v) => fmtEur(v)} />
              <Tooltip contentStyle={{ background: "#111a2e", border: "1px solid #1e2a45", color: "#fff" }} formatter={(v: number) => fmtEur(v)} />
              <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                {bridgeData.map((d, i) => (
                  <Cell key={i} fill={d.isTotal ? "#fbbf24" : d.value >= 0 ? "#34d399" : "#fb7185"} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {commentary.text && <CommentaryBlock text={commentary.text} generatedBy={commentary.generatedBy} />}
    </div>
  );
}
