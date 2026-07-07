"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Sidebar from "@/components/Sidebar";
import PeriodSelector from "@/components/PeriodSelector";
import { PeriodProvider } from "@/lib/PeriodContext";
import { api, getToken } from "@/lib/api";

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [checked, setChecked] = useState(false);
  const [companyName, setCompanyName] = useState("Senus PLC");

  useEffect(() => {
    if (!getToken()) {
      router.replace("/login");
      return;
    }
    api
      .company()
      .then((c) => setCompanyName(c.name))
      .catch(() => router.replace("/login"))
      .finally(() => setChecked(true));
  }, [router]);

  if (!checked) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-app-gradient text-slate-500">
        Loading…
      </div>
    );
  }

  return (
    <PeriodProvider>
      <div className="flex min-h-screen bg-app-gradient">
        <Sidebar />
        <div className="flex-1">
          <header className="flex items-center justify-between border-b border-border bg-panel/60 px-8 py-4 backdrop-blur">
            <div>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-500">Board Report</p>
              <h1 className="text-lg font-semibold text-white">{companyName}</h1>
            </div>
            <PeriodSelector />
          </header>
          <main className="px-8 py-6">{children}</main>
        </div>
      </div>
    </PeriodProvider>
  );
}
