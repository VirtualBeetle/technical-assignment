type Accent = "revenue" | "margin" | "cash" | "solvency" | "returns" | "brand" | "warn";

const ACCENT_STYLES: Record<Accent, { border: string; dot: string }> = {
  revenue: { border: "border-t-revenue", dot: "bg-revenue" },
  margin: { border: "border-t-margin", dot: "bg-margin" },
  cash: { border: "border-t-cash", dot: "bg-cash" },
  solvency: { border: "border-t-solvency", dot: "bg-solvency" },
  returns: { border: "border-t-returns", dot: "bg-returns" },
  brand: { border: "border-t-brand", dot: "bg-brand" },
  warn: { border: "border-t-warn", dot: "bg-warn" },
};

export default function KpiCard({
  label,
  value,
  sub,
  tone = "neutral",
  accent = "brand",
}: {
  label: string;
  value: string;
  sub?: string;
  tone?: "neutral" | "positive" | "negative";
  accent?: Accent;
}) {
  const valueClass =
    tone === "positive" ? "text-good" : tone === "negative" ? "text-bad" : "text-white";
  const styles = ACCENT_STYLES[accent];

  return (
    <div className={`card p-4 border-t-[3px] ${styles.border}`}>
      <div className="mb-2 flex items-center justify-between">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">{label}</p>
        <span className={`h-2 w-2 rounded-full ${styles.dot}`} />
      </div>
      <p className={`text-2xl font-semibold ${valueClass}`}>{value}</p>
      {sub && <p className="mt-1 text-xs text-slate-500">{sub}</p>}
    </div>
  );
}
