"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("ceo@senus.com");
  const [password, setPassword] = useState("Senus2030!");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      router.push("/dashboard");
    } catch (err) {
      setError("Invalid email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-app-gradient px-4">
      <div className="w-full max-w-sm card p-8">
        <div className="mb-6 text-center">
          <div className="mx-auto mb-3 h-11 w-11 rounded-xl bg-gradient-to-br from-brand to-brand2 shadow-lg shadow-brand/30" />
          <h1 className="text-xl font-semibold text-white">Senus Board Report</h1>
          <p className="mt-1 text-sm text-slate-400">
            AI-native financial reporting, built for Assiduous
          </p>
        </div>
        <form onSubmit={onSubmit} className="space-y-4">
          <div>
            <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">
              Email
            </label>
            <input
              className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-white outline-none focus:border-brand"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              required
            />
          </div>
          <div>
            <label className="mb-1 block text-xs uppercase tracking-wide text-slate-400">
              Password
            </label>
            <input
              className="w-full rounded-md border border-border bg-surface px-3 py-2 text-sm text-white outline-none focus:border-brand"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
            />
          </div>
          {error && <p className="text-sm text-bad">{error}</p>}
          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-md bg-gradient-to-r from-brand to-brand2 py-2 text-sm font-medium text-white shadow-lg shadow-brand/20 transition hover:opacity-90 disabled:opacity-50"
          >
            {loading ? "Signing in..." : "Sign in"}
          </button>
          <p className="text-center text-xs text-slate-500">
            Demo credentials are pre-filled — this is a demonstration login for
            the technical assignment, not a production auth system.
          </p>
        </form>
      </div>
    </main>
  );
}
