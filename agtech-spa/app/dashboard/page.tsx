"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { jwtDecode } from "jwt-decode";
import { getAccessToken } from "@/lib/auth";
import { useAuth } from "@/hooks/useAuth";

interface JwtPayload {
  sub?: string;
  exp?: number;
  rol?: string;
  [key: string]: unknown;
}

const EXCLUDED_KEYS = new Set(["iat", "exp", "nbf", "jti", "iss", "aud", "sub"]);

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}m ${String(s).padStart(2, "0")}s`;
}

function timerColor(seconds: number): string {
  if (seconds > 300) return "#27ae60";
  if (seconds > 60) return "#f39c12";
  return "#c0392b";
}

export default function DashboardPage() {
  const router = useRouter();
  const { logout } = useAuth();
  const [payload, setPayload] = useState<JwtPayload | null>(null);
  const [secondsLeft, setSecondsLeft] = useState<number>(0);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace("/login");
      return;
    }
    try {
      setPayload(jwtDecode<JwtPayload>(token));
    } catch {
      router.replace("/login");
    }
  }, [router]);

  useEffect(() => {
    if (!payload?.exp) return;

    const exp = payload.exp;

    const tick = () => {
      const remaining = exp - Math.floor(Date.now() / 1000);
      const clamped = Math.max(0, remaining);
      setSecondsLeft(clamped);
      if (remaining <= 0) logout();
    };

    tick();
    const id = setInterval(tick, 1000);
    return () => clearInterval(id);
  }, [payload?.exp, logout]);

  if (!payload) {
    return (
      <main style={{ padding: "2rem", textAlign: "center" }}>
        Cargando…
      </main>
    );
  }

  const displayEntries = Object.entries(payload).filter(
    ([key]) => !EXCLUDED_KEYS.has(key)
  );

  return (
    <main
      style={{
        minHeight: "100vh",
        background: "#f5f5f5",
        padding: "2rem",
      }}
    >
      <div
        style={{
          maxWidth: "640px",
          margin: "0 auto",
          background: "#fff",
          borderRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          padding: "2rem",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            marginBottom: "1.5rem",
          }}
        >
          <div>
            <h1 style={{ margin: 0, fontSize: "1.4rem" }}>Dashboard</h1>
            {payload.sub && (
              <p style={{ margin: "0.25rem 0 0", fontSize: "0.85rem", color: "#666" }}>
                {payload.sub}
              </p>
            )}
          </div>
          <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: "0.4rem" }}>
            <span
              style={{
                fontSize: "0.9rem",
                fontWeight: 700,
                color: timerColor(secondsLeft),
              }}
            >
              {formatTime(secondsLeft)}
            </span>
            <button
              onClick={logout}
              style={{
                padding: "0.4rem 1rem",
                borderRadius: "4px",
                border: "1px solid #c0392b",
                background: "transparent",
                color: "#c0392b",
                cursor: "pointer",
                fontWeight: 600,
              }}
            >
              Cerrar sesión
            </button>
          </div>
        </div>

        <h2 style={{ fontSize: "1rem", marginBottom: "0.75rem", color: "#555" }}>
          Payload del token
        </h2>

        <table style={{ width: "100%", borderCollapse: "collapse" }}>
          <thead>
            <tr>
              <th
                style={{
                  textAlign: "left",
                  padding: "0.5rem",
                  borderBottom: "2px solid #eee",
                  fontSize: "0.85rem",
                  color: "#888",
                  fontWeight: 600,
                }}
              >
                Campo
              </th>
              <th
                style={{
                  textAlign: "left",
                  padding: "0.5rem",
                  borderBottom: "2px solid #eee",
                  fontSize: "0.85rem",
                  color: "#888",
                  fontWeight: 600,
                }}
              >
                Valor
              </th>
            </tr>
          </thead>
          <tbody>
            {displayEntries.map(([key, value]) => (
              <tr key={key}>
                <td
                  style={{
                    padding: "0.5rem",
                    borderBottom: "1px solid #f0f0f0",
                    fontWeight: 600,
                    fontSize: "0.9rem",
                    color: "#333",
                  }}
                >
                  {key}
                </td>
                <td
                  style={{
                    padding: "0.5rem",
                    borderBottom: "1px solid #f0f0f0",
                    fontSize: "0.9rem",
                    color: "#555",
                    wordBreak: "break-all",
                  }}
                >
                  {typeof value === "object"
                    ? JSON.stringify(value)
                    : String(value)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </main>
  );
}
