"use client";
import { useEffect, useState } from "react";
import { usePeriod } from "@/lib/PeriodContext";
import { api } from "@/lib/api";
import CommentaryBlock from "@/components/CommentaryBlock";

const SECTION_TITLES: Record<string, string> = {
  overview: "Overview",
  growth: "Growth & Revenue",
  profitability: "Profitability",
  cash: "Cash & Liquidity",
  solvency: "Solvency & Leverage",
  returns: "Returns",
};

export default function InsightsPage() {
  const { selected } = usePeriod();
  const [rows, setRows] = useState<any[]>([]);

  useEffect(() => {
    if (!selected) return;
    api.insights(selected).then(setRows);
  }, [selected]);

  return (
    <div className="space-y-6">
      <div className="card p-4 text-sm text-emerald-200/70">
        AI-generated board commentary for the selected period. Each paragraph is produced from the computed
        metrics only (see backend/app/ai_commentary.py) — in demo mode this is a deterministic, auditable
        rule-based generator with no external API calls; setting <code className="text-brand2">AI_PROVIDER=openai</code> and an
        API key switches this to LLM-generated prose over the same metrics, with automatic fallback if the call fails.
      </div>
      {rows.map((row) => (
        <div key={row.section}>
          <h2 className="mb-2 text-sm font-semibold text-white">{SECTION_TITLES[row.section] || row.section}</h2>
          <CommentaryBlock text={row.text} generatedBy={row.generated_by} />
        </div>
      ))}
    </div>
  );
}
