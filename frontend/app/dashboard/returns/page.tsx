"use client";
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from "recharts";
import { usePeriod } from "@/lib/PeriodContext";
import { useMetrics, fmtEur, fmtPct, shortLabel } from "@/lib/useMetrics";
import { api } from "@/lib/api";
import KpiCard from "@/components/KpiCard";
import CommentaryBlock from "@/components/CommentaryBlock";

export default function ReturnsPage() {
  const { selected } = usePeriod();
  const { rows } = useMetrics("returns");
  const [commentary, setCommentary] = useState({ text: "", generatedBy: "" });

  useEffect(() => {
    if (!selected) return;
    api.insights(selected).then((r) => {
      const row = r.find((x: any) => x.section === "returns");
      if (row) setCommentary({ text: row.text, generatedBy: row.generated_by });
    });
  }, [selected]);

  const current = rows.find((r) => r.period.period_key === selected)?.metrics;
  const trend = rows.map((row) => ({ name: shortLabel(row.period.period_key), "ROCE %": row.metrics.roce_pct }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
        <KpiCard label="Capital Employed" value={fmtEur(current?.capital_employed)} accent="returns" />
        <KpiCard label="ROCE (annualised)" value={fmtPct(current?.roce_pct)} tone={current?.roce_pct < 0 ? "negative" : "positive"} accent="returns" />
        <KpiCard label="Net Assets" value={fmtEur(current?.net_assets)} tone={current?.net_assets < 0 ? "negative" : "positive"} accent="returns" />
      </div>

      <div className="card p-5">
        <h2 className="mb-4 text-sm font-medium text-slate-300">Return on Capital Employed by period</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={trend}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e2a45" />
            <XAxis dataKey="name" stroke="#7c8aad" fontSize={12} />
            <YAxis stroke="#7c8aad" fontSize={12} tickFormatter={(v) => `${v}%`} />
            <Tooltip contentStyle={{ background: "#111a2e", border: "1px solid #1e2a45", color: "#fff" }} />
            <Bar dataKey="ROCE %" radius={[4, 4, 0, 0]}>
              {trend.map((d, i) => (
                <Cell key={i} fill={d["ROCE %"] < 0 ? "#fb7185" : "#f472b6"} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      {commentary.text && <CommentaryBlock text={commentary.text} generatedBy={commentary.generatedBy} />}
    </div>
  );
}
