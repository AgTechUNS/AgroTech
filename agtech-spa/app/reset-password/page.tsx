"use client";

import { useState, FormEvent } from "react";
import Link from "next/link";
import { api } from "@/lib/api";

export default function ResetPasswordPage() {
  const [emailUsuario, setEmailUsuario] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setIsLoading(true);
    try {
      await api.post("/auth/reset-request", { emailUsuario });
    } catch {
      // Anti-enumeración: siempre mostramos éxito
    } finally {
      setIsLoading(false);
      setSubmitted(true);
    }
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
          Recuperar contraseña
        </h1>

        {submitted ? (
          <p
            role="status"
            style={{
              color: "#27ae60",
              background: "#eafaf1",
              border: "1px solid #a9dfbf",
              borderRadius: "4px",
              padding: "0.6rem 0.8rem",
              margin: 0,
              fontSize: "0.9rem",
              textAlign: "center",
            }}
          >
            Si el email está registrado, recibirás las instrucciones.
          </p>
        ) : (
          <>
            <p
              style={{
                margin: 0,
                fontSize: "0.9rem",
                color: "#555",
                textAlign: "center",
              }}
            >
              Ingresá tu email y te enviaremos las instrucciones para
              restablecer tu contraseña.
            </p>

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
              {isLoading ? "Enviando…" : "Enviar instrucciones"}
            </button>
          </>
        )}

        <Link
          href="/login"
          style={{
            textAlign: "center",
            fontSize: "0.85rem",
            color: "#2c7be5",
            textDecoration: "none",
          }}
        >
          ← Volver al inicio de sesión
        </Link>
      </form>
    </main>
  );
}
