import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Base surfaces - dark navy rather than flat dark-green, so the
        // category accent colors below actually stand out against it.
        ink: "#070b14",
        panel: "#0d1220",
        surface: "#111a2e",
        border: "#1e2a45",

        // Brand / chrome accent (sidebar, primary buttons, active states).
        brand: "#6366f1",
        brand2: "#a78bfa",

        // Category accents used across KPI cards and charts - each metric
        // family gets its own color so the dashboard isn't monochrome, while
        // red/green stay reserved purely for good/bad signal (see KpiCard).
        revenue: "#38bdf8",
        margin: "#a78bfa",
        cash: "#22d3ee",
        solvency: "#2dd4bf",
        returns: "#f472b6",
        warn: "#fbbf24",
        good: "#34d399",
        bad: "#fb7185",
      },
      backgroundImage: {
        "app-gradient":
          "radial-gradient(circle at 15% 0%, #131c33 0%, #070b14 45%), radial-gradient(circle at 85% 100%, #14203a 0%, #070b14 55%)",
      },
    },
  },
  plugins: [],
};
export default config;
