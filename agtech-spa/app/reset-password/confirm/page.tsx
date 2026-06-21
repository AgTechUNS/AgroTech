"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui";

export default function ConfirmResetPage() {
  const router = useRouter();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setError("Las contraseñas no coinciden");
      return;
    }
    // TODO: call confirm-reset API with token from query
    router.push("/login");
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
      }}
    >
      <Card style={{ width: "100%", maxWidth: 360 }}>
        <form onSubmit={handleSubmit}>
          <h1 style={{ margin: "0 0 0.3rem", fontSize: "1.3rem" }}>
            Nueva contraseña
          </h1>
          <p style={{ color: "var(--text-secondary)", margin: "0 0 1.5rem", fontSize: "0.9rem" }}>
            Ingresá tu nueva contraseña.
          </p>

          {error && (
            <p
              style={{
                color: "var(--danger)",
                background: "var(--danger-bg)",
                padding: "0.5rem",
                borderRadius: "4px",
                fontSize: "0.85rem",
                marginBottom: "1rem",
              }}
            >
              {error}
            </p>
          )}

          <div style={{ marginBottom: "1rem" }}>
            <label
              style={{
                display: "block",
                marginBottom: "0.3rem",
                fontSize: "0.85rem",
                fontWeight: 500,
              }}
            >
              Nueva contraseña
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={6}
              style={{
                width: "100%",
                padding: "0.5rem",
                border: "1px solid var(--border)",
                borderRadius: "4px",
                fontSize: "0.9rem",
                boxSizing: "border-box",
                background: "var(--bg-input)",
                color: "var(--text-primary)",
              }}
            />
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label
              style={{
                display: "block",
                marginBottom: "0.3rem",
                fontSize: "0.85rem",
                fontWeight: 500,
              }}
            >
              Confirmar contraseña
            </label>
            <input
              type="password"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              required
              minLength={6}
              style={{
                width: "100%",
                padding: "0.5rem",
                border: "1px solid var(--border)",
                borderRadius: "4px",
                fontSize: "0.9rem",
                boxSizing: "border-box",
                background: "var(--bg-input)",
                color: "var(--text-primary)",
              }}
            />
          </div>

          <button
            type="submit"
            style={{
              width: "100%",
              padding: "0.6rem",
              background: "var(--accent)",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              fontSize: "0.9rem",
              fontWeight: 500,
              cursor: "pointer",
            }}
          >
            Restablecer
          </button>
        </form>
      </Card>
    </div>
  );
}
