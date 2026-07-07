"use client";
import { createContext, useContext, useEffect, useState } from "react";
import { api, Period } from "@/lib/api";

type PeriodContextValue = {
  periods: Period[];
  selected: string;
  setSelected: (key: string) => void;
  loading: boolean;
};

const PeriodContext = createContext<PeriodContextValue>({
  periods: [],
  selected: "",
  setSelected: () => {},
  loading: true,
});

export function PeriodProvider({ children }: { children: React.ReactNode }) {
  const [periods, setPeriods] = useState<Period[]>([]);
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api
      .periods()
      .then((data: Period[]) => {
        setPeriods(data);
        const latest = data[data.length - 1];
        if (latest) setSelected(latest.period_key);
      })
      .finally(() => setLoading(false));
  }, []);

  return (
    <PeriodContext.Provider value={{ periods, selected, setSelected, loading }}>
      {children}
    </PeriodContext.Provider>
  );
}

export function usePeriod() {
  return useContext(PeriodContext);
}
