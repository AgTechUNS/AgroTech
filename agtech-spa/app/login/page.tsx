"use client";

import { useState, useEffect } from "react";
import { useAuth } from "@/hooks/useAuth";
import { clearTokens } from "@/lib/auth";

export default function LoginPage() {
  const { isLoading, error, login } = useAuth();
  const [emailUsuario, setEmailUsuario] = useState("");

  useEffect(() => { clearTokens(); }, []);
  const [password, setPassword] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login(emailUsuario, password);
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        background: "var(--bg-gradient)",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: "var(--bg-glass)",
          backdropFilter: "var(--blur-lg)",
          WebkitBackdropFilter: "var(--blur-lg)",
          padding: "2.5rem",
          borderRadius: "var(--radius-lg)",
          border: "1px solid var(--border)",
          boxShadow: "var(--shadow-lg)",
          width: "100%",
          maxWidth: 380,
        }}
      >
        <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>🌾</div>
          <h1 style={{ margin: 0, fontSize: "1.4rem", fontWeight: 700, letterSpacing: "-0.02em" }}>
            AgTech UNS
          </h1>
          <p style={{ color: "var(--text-muted)", margin: "0.3rem 0 0", fontSize: "0.85rem" }}>
            Ingresá tus credenciales
          </p>
        </div>

        {error && (
          <div
            style={{
              color: "var(--danger)",
              background: "var(--danger-bg)",
              padding: "0.6rem 0.75rem",
              borderRadius: "var(--radius)",
              fontSize: "0.85rem",
              marginBottom: "1rem",
              border: "1px solid var(--danger)",
            }}
          >
            {error}
          </div>
        )}

        <div style={{ marginBottom: "1rem" }}>
          <label
            style={{
              display: "block",
              marginBottom: "0.3rem",
              fontSize: "0.85rem",
              fontWeight: 500,
              color: "var(--text-secondary)",
            }}
          >
            Email
          </label>
          <input
            type="email"
            value={emailUsuario}
            onChange={(e) => setEmailUsuario(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "0.6rem 0.75rem",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              fontSize: "0.95rem",
              fontFamily: "inherit",
              boxSizing: "border-box",
              background: "var(--bg-input)",
              color: "var(--text-primary)",
              outline: "none",
              transition: "border-color var(--transition)",
            }}
            onFocus={(e) => { e.currentTarget.style.borderColor = "var(--accent)"; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = "var(--border)"; }}
          />
        </div>

        <div style={{ marginBottom: "1.5rem" }}>
          <label
            style={{
              display: "block",
              marginBottom: "0.3rem",
              fontSize: "0.85rem",
              fontWeight: 500,
              color: "var(--text-secondary)",
            }}
          >
            Contraseña
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "0.6rem 0.75rem",
              border: "1px solid var(--border)",
              borderRadius: "var(--radius)",
              fontSize: "0.95rem",
              fontFamily: "inherit",
              boxSizing: "border-box",
              background: "var(--bg-input)",
              color: "var(--text-primary)",
              outline: "none",
              transition: "border-color var(--transition)",
            }}
            onFocus={(e) => { e.currentTarget.style.borderColor = "var(--accent)"; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = "var(--border)"; }}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "0.65rem",
            background: isLoading ? "var(--text-muted)" : "var(--accent)",
            color: "#fff",
            border: "none",
            borderRadius: "var(--radius)",
            fontSize: "0.95rem",
            fontWeight: 600,
            fontFamily: "inherit",
            cursor: isLoading ? "not-allowed" : "pointer",
            opacity: isLoading ? 0.6 : 1,
            transition: "all var(--transition)",
            boxShadow: "var(--shadow-sm)",
          }}
          onMouseEnter={(e) => {
            if (!isLoading) {
              e.currentTarget.style.background = "var(--accent-hover)";
              e.currentTarget.style.boxShadow = "var(--shadow)";
            }
          }}
          onMouseLeave={(e) => {
            if (!isLoading) {
              e.currentTarget.style.background = "var(--accent)";
              e.currentTarget.style.boxShadow = "var(--shadow-sm)";
            }
          }}
        >
          {isLoading ? "Ingresando…" : "Ingresar"}
        </button>

        <div style={{ marginTop: "1.25rem", textAlign: "center" }}>
          <a
            href="/reset-password"
            style={{ color: "var(--text-muted)", fontSize: "0.85rem", transition: "color var(--transition)" }}
            onMouseEnter={(e) => { e.currentTarget.style.color = "var(--accent)"; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = "var(--text-muted)"; }}
          >
            ¿Olvidaste tu contraseña?
          </a>
        </div>
      </form>
    </div>
  );
}
