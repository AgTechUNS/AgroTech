"use client";

import { useState, FormEvent } from "react";
import { useAuth } from "@/hooks/useAuth";

const ERROR_LABELS: Record<string, string> = {
  CREDENTIALS_INVALID: "Email o contraseña incorrectos.",
  VALIDATION_ERROR: "Los datos ingresados no son válidos.",
  ACCOUNT_DISABLED: "La cuenta está deshabilitada.",
  ACCOUNT_NOT_FOUND: "No existe una cuenta con ese email.",
  TOO_MANY_ATTEMPTS: "Demasiados intentos. Intentá más tarde.",
};

function errorLabel(code: string): string {
  return ERROR_LABELS[code] ?? `Error: ${code}`;
}

export default function LoginPage() {
  const { login, isLoading, error } = useAuth();
  const [emailUsuario, setEmailUsuario] = useState("");
  const [password, setPassword] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    await login(emailUsuario, password);
  }

  return (
    <main
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "#f5f5f5",
      }}
    >
      <form
        onSubmit={handleSubmit}
        style={{
          background: "#fff",
          padding: "2rem",
          borderRadius: "8px",
          boxShadow: "0 2px 8px rgba(0,0,0,0.1)",
          width: "100%",
          maxWidth: "360px",
          display: "flex",
          flexDirection: "column",
          gap: "1rem",
        }}
      >
        <h1 style={{ margin: 0, fontSize: "1.4rem", textAlign: "center" }}>
          AgTech UNS
        </h1>

        {error && (
          <p
            role="alert"
            style={{
              color: "#c0392b",
              background: "#fdecea",
              border: "1px solid #f5c6cb",
              borderRadius: "4px",
              padding: "0.6rem 0.8rem",
              margin: 0,
              fontSize: "0.9rem",
            }}
          >
            {errorLabel(error)}
          </p>
        )}

        <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>Email</span>
          <input
            type="email"
            value={emailUsuario}
            onChange={(e) => setEmailUsuario(e.target.value)}
            required
            autoComplete="email"
            placeholder="usuario@agtech.uns.edu.ar"
            style={{
              padding: "0.5rem 0.75rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
              fontSize: "1rem",
            }}
          />
        </label>

        <label style={{ display: "flex", flexDirection: "column", gap: "4px" }}>
          <span style={{ fontSize: "0.85rem", fontWeight: 600 }}>
            Contraseña
          </span>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            autoComplete="current-password"
            placeholder="••••••••"
            style={{
              padding: "0.5rem 0.75rem",
              borderRadius: "4px",
              border: "1px solid #ccc",
              fontSize: "1rem",
            }}
          />
        </label>

        <button
          type="submit"
          disabled={isLoading}
          style={{
            padding: "0.6rem",
            borderRadius: "4px",
            border: "none",
            background: isLoading ? "#aaa" : "#2c7be5",
            color: "#fff",
            fontSize: "1rem",
            cursor: isLoading ? "not-allowed" : "pointer",
            fontWeight: 600,
          }}
        >
          {isLoading ? "Ingresando…" : "Ingresar"}
        </button>
      </form>
    </main>
  );
}
