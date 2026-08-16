"use client";

import { useState } from "react";
import { loginApi } from "@/lib/api";

type LoginFormProps = {
  onLoginSuccess: () => void;
};

export const LoginForm = ({ onLoginSuccess }: LoginFormProps) => {
  const [username, setUsername] = useState("user");
  const [password, setPassword] = useState("password");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const success = await loginApi(username, password);
      if (success) {
        onLoginSuccess();
      } else {
        setError("Invalid username or password.");
      }
    } catch {
      setError("Unable to connect to authentication server.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[var(--surface)] px-4">
      <div className="w-full max-w-md rounded-3xl border border-[var(--stroke)] bg-white p-8 shadow-xl">
        <div className="mb-6 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
            Single Board Kanban
          </p>
          <h1 className="mt-2 text-3xl font-bold text-[var(--navy-dark)]">
            Kanban Studio Sign In
          </h1>
          <p className="mt-2 text-sm text-[var(--gray-text)]">
            Please sign in to access your project management board.
          </p>
        </div>

        {error && (
          <div className="mb-4 rounded-xl border border-red-200 bg-red-50 p-3 text-xs font-medium text-red-600">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--navy-dark)]">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="mt-1 w-full rounded-xl border border-[var(--stroke)] px-4 py-3 text-sm text-[var(--navy-dark)] focus:border-[var(--primary-blue)] focus:outline-none"
              placeholder="user"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-[var(--navy-dark)]">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="mt-1 w-full rounded-xl border border-[var(--stroke)] px-4 py-3 text-sm text-[var(--navy-dark)] focus:border-[var(--primary-blue)] focus:outline-none"
              placeholder="password"
            />
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-[var(--secondary-purple)] py-3.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
            >
              {loading ? "Signing in..." : "Sign In"}
            </button>
          </div>
        </form>

        <div className="mt-6 rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] p-4 text-center">
          <p className="text-xs text-[var(--gray-text)]">
            Demo Credentials: Username <span className="font-semibold text-[var(--navy-dark)]">user</span> | Password <span className="font-semibold text-[var(--navy-dark)]">password</span>
          </p>
        </div>
      </div>
    </div>
  );
};
