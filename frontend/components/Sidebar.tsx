"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { clearToken } from "@/lib/api";

const NAV = [
  { href: "/dashboard", label: "Overview", dot: "bg-brand" },
  { href: "/dashboard/growth", label: "Growth & Revenue", dot: "bg-revenue" },
  { href: "/dashboard/profitability", label: "Profitability", dot: "bg-margin" },
  { href: "/dashboard/cash", label: "Cash & Liquidity", dot: "bg-cash" },
  { href: "/dashboard/solvency", label: "Solvency & Leverage", dot: "bg-solvency" },
  { href: "/dashboard/returns", label: "Returns", dot: "bg-returns" },
  { href: "/dashboard/insights", label: "AI Insights", dot: "bg-warn" },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <aside className="flex w-64 shrink-0 flex-col border-r border-border bg-panel px-4 py-6">
      <div className="mb-8 flex items-center gap-3 px-2">
        <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-brand to-brand2 shadow-lg shadow-brand/20" />
        <div>
          <p className="text-sm font-semibold text-white">Senus PLC</p>
          <p className="text-[11px] text-slate-400">Board Report</p>
        </div>
      </div>
      <nav className="flex-1 space-y-1">
        {NAV.map((item) => {
          const active = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition ${
                active
                  ? "bg-white/[0.06] text-white ring-1 ring-inset ring-white/10"
                  : "text-slate-400 hover:bg-white/[0.03] hover:text-white"
              }`}
            >
              <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${item.dot} ${active ? "" : "opacity-50"}`} />
              {item.label}
            </Link>
          );
        })}
      </nav>
      <button
        onClick={() => {
          clearToken();
          router.push("/login");
        }}
        className="mt-4 rounded-lg border border-border px-3 py-2 text-left text-xs text-slate-400 transition hover:border-slate-600 hover:text-white"
      >
        Sign out
      </button>
    </aside>
  );
}
