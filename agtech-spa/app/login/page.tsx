"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";

export default function LoginPage() {
  const { isLoading, error, login } = useAuth();
  const [emailUsuario, setEmailUsuario] = useState("");
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
        background: "#f1f5f9",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: "#fff",
          padding: "2rem",
          borderRadius: "8px",
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          width: "100%",
          maxWidth: 360,
        }}
      >
        <h1 style={{ margin: "0 0 0.3rem", fontSize: "1.3rem" }}>AgTech UNS</h1>
        <p style={{ color: "#64748b", margin: "0 0 1.5rem", fontSize: "0.9rem" }}>
          Ingresá tus credenciales
        </p>

        {error && (
          <p
            style={{
              color: "#dc2626",
              background: "#fef2f2",
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
            Email
          </label>
          <input
            type="email"
            value={emailUsuario}
            onChange={(e) => setEmailUsuario(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #e2e8f0",
              borderRadius: "4px",
              fontSize: "0.9rem",
              boxSizing: "border-box",
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
            Contraseña
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              width: "100%",
              padding: "0.5rem",
              border: "1px solid #e2e8f0",
              borderRadius: "4px",
              fontSize: "0.9rem",
              boxSizing: "border-box",
            }}
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            width: "100%",
            padding: "0.6rem",
            background: isLoading ? "#94a3b8" : "#2c7be5",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            fontSize: "0.9rem",
            fontWeight: 500,
            cursor: isLoading ? "not-allowed" : "pointer",
          }}
        >
          {isLoading ? "Ingresando…" : "Ingresar"}
        </button>

        <div style={{ marginTop: "1rem", textAlign: "center" }}>
          <a
            href="/reset-password"
            style={{ color: "#2c7be5", fontSize: "0.85rem", textDecoration: "none" }}
          >
            ¿Olvidaste tu contraseña?
          </a>
        </div>
      </form>
    </div>
  );
}
