"use client";

import { useState } from "react";

// ---------------------------------------------------------------------------
// Rendered by web/app/first-call/admin/page.tsx (a Server Component) when
// no valid session cookie is present. On success, the login route sets an
// httpOnly cookie the browser will send on the next request -- a plain
// reload is enough to re-run the Server Component's cookie check and hand
// back the submissions list, no client-side routing needed.
// ---------------------------------------------------------------------------

export default function AdminLoginForm() {
  const [password, setPassword] = useState("");
  const [error, setError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit() {
    if (password.length === 0) return;
    setIsLoading(true);
    setError(false);
    try {
      const res = await fetch("/api/first-call/admin-login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      if (!res.ok) {
        setError(true);
        setIsLoading(false);
        return;
      }
      window.location.reload();
    } catch {
      setError(true);
      setIsLoading(false);
    }
  }

  return (
    <main className="max-w-sm mx-auto px-6 py-16">
      <p className="font-ui text-xs tracking-widest uppercase text-slate mb-2">First Call</p>
      <h1 className="font-display text-2xl text-charcoal mb-6">Admin</h1>

      <div className="mb-4">
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="Password"
          autoFocus
          className="w-full font-ui text-sm border border-gray-200 rounded-lg px-3 py-2.5 bg-white text-charcoal focus:outline-none focus:border-charcoal"
        />
      </div>

      {error && <p className="font-ui text-sm text-charcoal mb-4">Incorrect password.</p>}

      <button
        onClick={handleSubmit}
        disabled={password.length === 0 || isLoading}
        className="w-full bg-charcoal text-white font-ui text-sm font-medium px-5 py-3 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {isLoading ? "Checking…" : "Enter"}
      </button>
    </main>
  );
}
