"use client";

import { useState, useCallback } from "react";

type Status = "idle" | "loading" | "success" | "error";

export default function SubscribeForm() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<Status>("idle");
  const [message, setMessage] = useState("");

  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      if (!email.trim()) return;

      setStatus("loading");
      try {
        const res = await fetch("/api/subscribe", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: email.trim() }),
        });

        const data = await res.json();

        if (!res.ok) {
          setStatus("error");
          setMessage(data.error || "Something went wrong.");
          return;
        }

        setStatus("success");
        setMessage("Check your inbox for a confirmation link!");
        setEmail("");
      } catch {
        setStatus("error");
        setMessage("Network error. Please try again.");
      }
    },
    [email]
  );

  return (
    <div className="bg-brand-card border border-white/10 rounded-2xl p-6 max-w-md mx-auto">
      <h3 className="text-lg font-semibold text-white mb-1">
        Get it in your inbox
      </h3>
      <p className="text-sm text-brand-muted mb-4">
        Weekly digest + podcast delivered every Sunday.
      </p>

      {status === "success" ? (
        <div className="flex items-center gap-2 text-sm text-green-400 bg-green-400/10 border border-green-400/20 rounded-lg px-4 py-3">
          <svg viewBox="0 0 24 24" fill="currentColor" className="w-5 h-5 shrink-0">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
          </svg>
          {message}
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="email"
            value={email}
            onChange={(e) => {
              setEmail(e.target.value);
              if (status === "error") setStatus("idle");
            }}
            placeholder="you@company.com"
            required
            className="flex-1 bg-brand-surface border border-white/10 rounded-lg px-4 py-2.5 text-sm text-white placeholder:text-brand-muted/60 outline-none focus:border-brand-orange/50 focus:ring-1 focus:ring-brand-orange/20 transition-all"
          />
          <button
            type="submit"
            disabled={status === "loading"}
            className="px-5 py-2.5 bg-gradient-to-r from-brand-orange to-brand-red text-white text-sm font-semibold rounded-lg hover:shadow-lg hover:shadow-brand-orange/20 active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed whitespace-nowrap"
          >
            {status === "loading" ? (
              <span className="inline-flex items-center gap-2">
                <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" />
                  <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="3" strokeLinecap="round" className="opacity-75" />
                </svg>
                Sending
              </span>
            ) : (
              "Subscribe"
            )}
          </button>
        </form>
      )}

      {status === "error" && (
        <p className="mt-2 text-sm text-red-400">{message}</p>
      )}
    </div>
  );
}
