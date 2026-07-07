"use client";
import { usePeriod } from "@/lib/PeriodContext";

export default function PeriodSelector() {
  const { periods, selected, setSelected } = usePeriod();
  return (
    <select
      value={selected}
      onChange={(e) => setSelected(e.target.value)}
      className="rounded-lg border border-border bg-surface px-3 py-1.5 text-sm text-white outline-none ring-brand/40 focus:ring-2"
    >
      {periods.map((p) => (
        <option key={p.period_key} value={p.period_key}>
          {p.label}
        </option>
      ))}
    </select>
  );
}
